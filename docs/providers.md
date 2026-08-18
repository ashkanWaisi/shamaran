# Providers

Version 0.1.0 implements Ollama through `BaseProvider`. Configure `OLLAMA_BASE_URL`,
`OLLAMA_MODEL`, and `OLLAMA_TIMEOUT`. The registry is the extension point for future
providers; the agent and tool layers do not import Ollama.

Provider implementations must translate connection, timeout, HTTP, and response-shape
errors into readable domain errors. Automated tests must mock remote calls.
