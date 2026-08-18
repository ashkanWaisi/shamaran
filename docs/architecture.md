# Architecture

Shamaran separates policy, execution, and presentation:

- `cli.py` owns the interactive session and confirmations.
- `agent/` validates a small JSON action protocol and enforces a step limit.
- `providers/` isolates vendor APIs behind `BaseProvider`.
- `tools/` validates inputs, applies security policy, and returns structured results.
- `memory/` stores deliberate, non-secret context in SQLite.
- `ui/` renders state without controlling behavior.

The model never calls subprocesses or files directly. It requests a registered tool;
the registry validates its schema, the tool applies policy, and only the structured
observation returns to the next agent step.
