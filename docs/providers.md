# Providers

Shamaran implements two provider protocols through `BaseProvider`:

- `ollama` uses Ollama's native API and discovers models from `/api/tags`.
- `openai-compatible` discovers models from `/v1/models` and chats through
  `/v1/chat/completions`. This covers LM Studio, LocalAI, llama.cpp, vLLM, and
  other servers that implement those endpoints.

The Web UI's **Models** tab contains presets for common local servers, an editable
endpoint, connection testing, model discovery, and active-model selection. Configure
protected compatible servers with `SHAMARAN_COMPATIBLE_API_KEY` in a local `.env`;
the browser never receives or stores the key.

Configure Ollama with `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, and `OLLAMA_TIMEOUT`.
Configure compatible servers with `SHAMARAN_COMPATIBLE_BASE_URL`,
`SHAMARAN_COMPATIBLE_MODEL`, `SHAMARAN_COMPATIBLE_API_KEY`, and
`SHAMARAN_COMPATIBLE_TIMEOUT`. The agent and tool layers remain provider-neutral.

Provider implementations must translate connection, timeout, HTTP, and response-shape
errors into readable domain errors. Automated tests mock remote calls.
