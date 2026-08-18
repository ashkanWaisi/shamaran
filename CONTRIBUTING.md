# Contributing to Shamaran

Thank you for helping make Shamaran safer and more useful.

Shamaran is created and maintained by **Ashkan Allahveisi**. Contributions are
welcome through focused issues and pull requests.

## Development setup

Use Python 3.11 or newer. Create a virtual environment, activate it, then run:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python scripts/check_secrets.py
```

Copy `.env.example` to `.env` only for local manual testing. Never commit `.env`,
database files, logs, model data, or credentials.

## Style and tests

Prefer typed, readable Python and small functions. Keep dependencies minimal.
Run the full suite before opening a pull request. Bug fixes need a regression test;
public behavior changes need documentation updates.

## Adding a tool

1. Derive from `BaseTool` and declare a Pydantic input model.
2. Choose an honest `SAFE`, `CONFIRM`, or `BLOCKED` policy.
3. Return `ToolResult`; never invent observations.
4. Register the tool centrally and add validation, success, failure, and abuse tests.
5. Preserve workspace boundaries and avoid `shell=True`.

## Adding a provider

Implement `BaseProvider`, translate vendor errors into concise `ProviderError`
messages, and register a factory in `ProviderRegistry`. Tests must use mocks and
must not need network access or credentials.

## Pull requests

Keep changes focused. Explain the behavior and security impact, list tests run,
and flag any new dependency. Never weaken safety checks to make a test pass.
Do not include generated runtime state. Maintainers should inspect staged changes
and run the secret checker before merging.
