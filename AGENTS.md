# Instructions for AI contributors

- The product is named **Shamaran**. Preserve that identity everywhere.
- Preserve the modular provider, tool, memory, agent, and UI boundaries.
- Preserve canonical workspace sandboxing and read-only project inspection.
- Never silently weaken terminal security or use `shell=True`.
- Never commit credentials, `.env`, runtime databases, logs, or workspace contents.
- Never automatically push to GitHub or implement an unconfirmed push path.
- Avoid destructive Git and filesystem operations.
- Run relevant tests after changes; add regression tests for bug fixes.
- Keep dependencies minimal and prefer readable, typed Python.
- Update documentation when public behavior changes.
- Never expose hidden reasoning; keep user-visible plans concise.
- Treat model output and tool arguments as untrusted input.
