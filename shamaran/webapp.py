"""Local FastAPI application for Shamaran's graphical interface."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from shamaran.agent import ShamaranAgent
from shamaran.agent.context import relevant_memory
from shamaran.cli import build_registry
from shamaran.config import Settings
from shamaran.exceptions import ShamaranError
from shamaran.memory import SQLiteMemory
from shamaran.providers.registry import default_provider_registry
from shamaran.providers.ollama import OllamaProvider
from shamaran.providers.openai_compatible import OpenAICompatibleProvider
from shamaran.version import __version__


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)
    provider: Literal["ollama", "openai-compatible"] = "ollama"
    endpoint: str | None = Field(default=None, max_length=500)
    model: str | None = None
    max_steps: int | None = Field(default=None, ge=1, le=32)
    allow_mutations: bool = False


class ModelDiscoveryRequest(BaseModel):
    provider: Literal["ollama", "openai-compatible"]
    endpoint: str = Field(min_length=8, max_length=500)


def _endpoint(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Endpoint must be a valid HTTP(S) URL")
    return value.rstrip("/")


def _record(record: Any) -> dict[str, Any]:
    return record.model_dump(mode="json")


def create_app() -> FastAPI:
    settings = Settings()
    settings.ensure_directories()
    memory = SQLiteMemory(settings.memory_db)
    static_dir = Path(__file__).resolve().parent / "web" / "static"
    app = FastAPI(title="Shamaran Web", version=__version__)

    @app.get("/api/status")
    def status() -> dict[str, Any]:
        models: list[str] = []
        ollama_ok = False
        ollama_detail = "Ollama is not reachable"
        try:
            response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=2.5)
            response.raise_for_status()
            models = [item["name"] for item in response.json().get("models", []) if item.get("name")]
            ollama_ok = True
            ollama_detail = "Connected"
        except (httpx.HTTPError, ValueError, TypeError):
            pass
        tools = build_registry(settings, confirmation=lambda _message: False)
        return {
            "version": __version__,
            "provider": settings.provider,
            "model": settings.ollama_model if settings.provider == "ollama" else settings.compatible_model,
            "models": models,
            "endpoint": settings.ollama_base_url,
            "workspace": str(settings.workspace.expanduser().resolve()),
            "max_steps": settings.max_steps,
            "memory_ok": memory.healthy(),
            "ollama_ok": ollama_ok,
            "ollama_detail": ollama_detail,
            "tools": tools.descriptions(),
            "providers": [
                {"id": "ollama", "name": "Ollama", "protocol": "ollama", "default_endpoint": settings.ollama_base_url},
                {"id": "lm-studio", "name": "LM Studio", "protocol": "openai-compatible", "default_endpoint": "http://localhost:1234/v1"},
                {"id": "localai", "name": "LocalAI", "protocol": "openai-compatible", "default_endpoint": "http://localhost:8080/v1"},
                {"id": "llama-cpp", "name": "llama.cpp", "protocol": "openai-compatible", "default_endpoint": "http://localhost:8080/v1"},
                {"id": "vllm", "name": "vLLM", "protocol": "openai-compatible", "default_endpoint": "http://localhost:8000/v1"},
                {"id": "custom", "name": "Custom server", "protocol": "openai-compatible", "default_endpoint": settings.compatible_base_url},
            ],
        }

    @app.post("/api/models/discover")
    def discover_models(payload: ModelDiscoveryRequest) -> dict[str, Any]:
        endpoint = _endpoint(payload.endpoint)
        try:
            if payload.provider == "ollama":
                provider = OllamaProvider(endpoint, settings.ollama_model, timeout=5)
            else:
                provider = OpenAICompatibleProvider(
                    endpoint,
                    settings.compatible_model,
                    settings.compatible_api_key,
                    timeout=5,
                )
            models = provider.models()
        except ShamaranError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {
            "connected": True,
            "provider": payload.provider,
            "endpoint": endpoint,
            "models": models,
            "auth_configured": bool(settings.compatible_api_key) if payload.provider != "ollama" else True,
        }

    @app.get("/api/memory")
    def memories(query: str = Query(default="", max_length=200)) -> dict[str, Any]:
        records = memory.search(query, limit=20) if query.strip() else memory.list_recent(20)
        return {"items": [_record(record) for record in records]}

    @app.post("/api/chat")
    def chat(payload: ChatRequest) -> dict[str, Any]:
        updates: dict[str, Any] = {
            "provider": payload.provider,
            "max_steps": payload.max_steps or settings.max_steps,
        }
        if payload.provider == "ollama":
            updates["ollama_base_url"] = _endpoint(payload.endpoint or settings.ollama_base_url)
            updates["ollama_model"] = payload.model or settings.ollama_model
        else:
            updates["compatible_base_url"] = _endpoint(payload.endpoint or settings.compatible_base_url)
            updates["compatible_model"] = payload.model or settings.compatible_model
        runtime = settings.model_copy(update=updates)
        plan: list[str] = []
        events: list[dict[str, Any]] = []
        tools = build_registry(
            runtime,
            confirmation=lambda _message: payload.allow_mutations,
        )
        agent = ShamaranAgent(
            default_provider_registry().create(runtime),
            tools,
            runtime.max_steps,
            on_plan=lambda steps: plan.extend(steps),
            on_tool=lambda name, ok, summary: events.append(
                {"name": name, "ok": ok, "summary": summary}
            ),
        )
        try:
            result = agent.run(payload.message.strip(), relevant_memory(memory, payload.message))
        except ShamaranError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {
            "answer": result.answer,
            "plan": plan,
            "tools": events,
            "steps_used": result.steps_used,
            "exhausted": result.exhausted,
            "model": runtime.ollama_model if runtime.provider == "ollama" else runtime.compatible_model,
            "provider": runtime.provider,
        }

    if static_dir.exists():
        assets_dir = static_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def frontend(path: str) -> FileResponse:
            candidate = (static_dir / path).resolve()
            if path and candidate.is_file() and static_dir in candidate.parents:
                return FileResponse(candidate)
            return FileResponse(static_dir / "index.html")
    else:
        @app.get("/", include_in_schema=False)
        def missing_frontend() -> dict[str, str]:
            return {"error": "Web assets are missing. Build the web workspace first."}

    return app


app = create_app()
