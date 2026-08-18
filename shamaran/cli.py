"""Typer entry point and interactive Rich shell."""

import logging
import os
import webbrowser
from collections.abc import Callable
from pathlib import Path

import typer
from pydantic import ValidationError
from rich.prompt import Confirm, Prompt
from rich.table import Table

from shamaran.agent import ShamaranAgent
from shamaran.agent.context import relevant_memory
from shamaran.config import DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILE, Settings
from shamaran.doctor import run_checks
from shamaran.exceptions import ShamaranError
from shamaran.logging_config import configure_logging
from shamaran.memory import SQLiteMemory
from shamaran.providers.registry import default_provider_registry
from shamaran.tools.filesystem import FilesystemSandbox, filesystem_tools
from shamaran.tools.git_tools import git_tools
from shamaran.tools.desktop import DesktopOpenTool
from shamaran.tools.registry import ToolRegistry
from shamaran.tools.terminal import TerminalTool
from shamaran.ui import console, print_assistant_answer, show_banner, status_table
from shamaran.version import __version__


app = typer.Typer(
    name="shamaran",
    help="Shamaran — secure, local-first AI agent.",
    add_completion=False,
    invoke_without_command=True,
    no_args_is_help=False,
)
logger = logging.getLogger("shamaran.cli")


def _confirm(message: str, enabled: bool) -> bool:
    if not enabled:
        console.print("[shamaran.warning]Mutation confirmations are disabled; action rejected.[/]")
        return False
    return Confirm.ask(message, default=False)


def build_registry(
    settings: Settings,
    confirmation: Callable[[str], bool] | None = None,
) -> ToolRegistry:
    registry = ToolRegistry()
    confirmation = confirmation or (
        lambda message: _confirm(message, settings.confirm_mutations)
    )
    sandbox = FilesystemSandbox(settings.workspace, Path.cwd())
    for tool in filesystem_tools(sandbox, confirmation):
        registry.register(tool)
    registry.register(TerminalTool(Path.cwd(), confirmation))
    registry.register(DesktopOpenTool(confirmation))
    for tool in git_tools(Path.cwd(), confirmation):
        registry.register(tool)
    return registry


def _show_status(settings: Settings, memory: SQLiteMemory, tools: ToolRegistry) -> None:
    console.print(
        status_table(
            [
                ("Version", __version__),
                ("Provider", settings.provider),
                ("Model", settings.ollama_model or "Not configured"),
                ("Workspace", str(settings.workspace.resolve())),
                ("Memory", "Ready" if memory.healthy() else "Unavailable"),
                ("Tools", f"{len(tools)} registered"),
                ("Max steps", str(settings.max_steps)),
            ]
        )
    )


def _show_help() -> None:
    table = Table(title="Built-in commands", header_style="shamaran.title")
    table.add_column("Command")
    table.add_column("Purpose")
    for command, purpose in [
        ("/help", "Show this help"), ("/status", "Show runtime status"),
        ("/tools", "List registered tools"), ("/config", "Show safe configuration"),
        ("/memory", "Show recent memory"), ("/memory clear", "Clear memory after confirmation"),
        ("/clear", "Clear the terminal"), ("/version", "Show version"),
        ("/doctor", "Run diagnostics"), ("/exit", "Exit Shamaran"),
    ]:
        table.add_row(command, purpose)
    console.print(table)


def _show_doctor(settings: Settings) -> None:
    console.print("\n[shamaran.title]Shamaran Doctor[/]\n")
    checks = run_checks(settings)
    for check in checks:
        icon = "[shamaran.success]✓[/]" if check.ok else "[shamaran.error]✗[/]"
        console.print(f"{icon} {check.name}: {check.detail}")
    console.print(
        "\n[shamaran.success]System ready.[/]" if all(c.ok for c in checks)
        else "\n[shamaran.warning]Some checks need attention.[/]"
    )


def _builtin(
    command: str, settings: Settings, memory: SQLiteMemory, tools: ToolRegistry
) -> bool:
    if command == "/help":
        _show_help()
    elif command == "/status":
        _show_status(settings, memory, tools)
    elif command == "/tools":
        for item in tools.descriptions():
            console.print(f"[shamaran.accent]{item['name']}[/] — {item['description']}")
    elif command == "/config":
        console.print(status_table([
            ("Provider", settings.provider), ("Endpoint", settings.ollama_base_url),
            ("Model", settings.ollama_model or "Not configured"),
            ("Workspace", str(settings.workspace.resolve())),
            ("Confirm", str(settings.confirm_mutations)),
        ]))
    elif command == "/memory":
        records = memory.list_recent()
        if not records:
            console.print("[shamaran.muted]Memory is empty.[/]")
        for record in records:
            console.print(f"[shamaran.accent]#{record.id}[/] [{record.category}] {record.content}")
    elif command == "/memory clear":
        if Confirm.ask("Clear all Shamaran memory?", default=False):
            console.print(f"Cleared {memory.clear()} memory record(s).")
    elif command == "/clear":
        console.clear()
        show_banner()
    elif command == "/version":
        console.print(f"Shamaran {__version__}")
    elif command == "/doctor":
        _show_doctor(settings)
    elif command in {"/exit", "/quit"}:
        return False
    else:
        console.print("[shamaran.warning]Unknown command. Use /help.[/]")
    return True


def _interactive(settings: Settings) -> None:
    settings.ensure_directories()
    configure_logging(settings.log_level)
    logger.info("startup version=%s provider=%s", __version__, settings.provider)
    memory = SQLiteMemory(settings.memory_db)
    tools = build_registry(settings)
    provider = default_provider_registry().create(settings)
    agent = ShamaranAgent(
        provider,
        tools,
        settings.max_steps,
        on_plan=lambda plan: console.print(
            "\n[shamaran.title]Plan[/]\n" + "\n".join(f"{i}. {step}" for i, step in enumerate(plan, 1))
        ),
        on_tool=lambda name, ok, summary: console.print(
            f"[{'shamaran.success' if ok else 'shamaran.error'}]{'✓' if ok else '✗'}[/] → {name} — {summary}"
        ),
    )
    show_banner()
    _show_status(settings, memory, tools)
    console.print("\n[shamaran.success]Shamaran is ready.[/] Type /help for commands.\n")
    try:
        while True:
            request = Prompt.ask("[bold]You[/]").strip()
            if not request:
                continue
            if request.startswith("/"):
                if not _builtin(request.lower(), settings, memory, tools):
                    break
                continue
            try:
                result = agent.run(request, relevant_memory(memory, request))
                console.print("\n[shamaran.title]Shamaran[/]\n")
                print_assistant_answer(result.answer)
            except ShamaranError as exc:
                logger.warning("request failed error=%s", exc)
                console.print(f"[shamaran.error]{exc}[/]")
    except (KeyboardInterrupt, EOFError):
        console.print("\n[shamaran.muted]Goodbye.[/]")
    finally:
        logger.info("shutdown")


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Show version and exit."),
) -> None:
    if version:
        console.print(f"Shamaran {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is not None:
        return
    if not Path(".env").exists() and not DEFAULT_CONFIG_FILE.exists():
        show_banner()
        console.print(
            "\n[shamaran.title]Welcome to Shamaran.[/]\n\n"
            "No .env configuration was found.\n\n"
            "1. Run shamaran setup --model YOUR_MODEL_NAME\n"
            "2. Run Shamaran again\n\n"
            "Run [shamaran.accent]python scripts/doctor.py[/] for diagnostics."
        )
        return
    try:
        _interactive(Settings())
    except ValidationError as exc:
        console.print(f"[shamaran.error]Invalid configuration:[/] {exc}")


@app.command()
def setup(
    model: str = typer.Option(..., "--model", "-m", help="Installed Ollama model name."),
    force: bool = typer.Option(False, "--force", help="Replace existing global configuration."),
) -> None:
    """Create a global user configuration so `shamaran` works from any directory."""
    if DEFAULT_CONFIG_FILE.exists() and not force:
        console.print(
            f"[shamaran.warning]Configuration already exists:[/] {DEFAULT_CONFIG_FILE}\n"
            "Use --force only if you want to replace it."
        )
        return
    model = model.strip()
    if not model:
        raise typer.BadParameter("model cannot be empty")
    workspace = (DEFAULT_CONFIG_DIR / "workspace").as_posix()
    memory_db = (DEFAULT_CONFIG_DIR / "data" / "shamaran_memory.db").as_posix()
    DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_CONFIG_FILE.write_text(
        "SHAMARAN_PROVIDER=ollama\n"
        f'SHAMARAN_WORKSPACE="{workspace}"\n'
        "SHAMARAN_MAX_STEPS=8\n"
        "SHAMARAN_LOG_LEVEL=INFO\n"
        "SHAMARAN_CONFIRM_MUTATIONS=true\n"
        f'SHAMARAN_MEMORY_DB="{memory_db}"\n\n'
        "OLLAMA_BASE_URL=http://localhost:11434\n"
        f"OLLAMA_MODEL={model}\n"
        "OLLAMA_TIMEOUT=120\n",
        encoding="utf-8",
    )
    console.print(f"[shamaran.success]Configuration saved:[/] {DEFAULT_CONFIG_FILE}")
    console.print("Run [shamaran.accent]shamaran doctor[/], then [shamaran.accent]shamaran[/].")


@app.command()
def doctor(no_ollama: bool = typer.Option(False, help="Skip Ollama connectivity.")) -> None:
    """Run installation diagnostics."""
    settings = Settings()
    checks = run_checks(settings, check_ollama=not no_ollama)
    for check in checks:
        typer.echo(f"{'OK' if check.ok else 'FAIL'} {check.name}: {check.detail}")
    if not all(check.ok for check in checks):
        raise typer.Exit(code=1)


@app.command()
def web(
    host: str = typer.Option("127.0.0.1", help="Address to bind the Web UI to."),
    port: int = typer.Option(8000, min=1, max=65535, help="Port for the Web UI."),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open the UI in your browser."),
) -> None:
    """Launch Shamaran's local graphical interface."""
    import uvicorn

    from shamaran.webapp import create_app

    url_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    url = f"http://{url_host}:{port}"
    console.print(f"[shamaran.success]Shamaran Web is ready:[/] {url}")
    if host in {"0.0.0.0", "::"}:
        console.print("[shamaran.warning]LAN access is enabled. Only use this on a trusted network.[/]")
    if open_browser:
        webbrowser.open(url)
    uvicorn.run(create_app(), host=host, port=port, log_level="info")
