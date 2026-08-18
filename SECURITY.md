# Shamaran security model

Shamaran is designed for controlled local assistance, not unattended autonomy.
Its safety boundaries reduce risk but do not make model-generated actions trusted.

## Boundaries

- Writes are confined to the configured workspace after canonical path resolution.
- `..`, absolute escapes, and symlink escapes are rejected.
- Project source is optionally readable through the explicit `@project/` scope and
  remains read-only to filesystem tools.
- Terminal commands use argument arrays and `shell=False`. Metacharacters, shell
  chaining, pipes, command substitution, destructive commands, and unsupported Git
  subcommands are blocked.
- Mutating filesystem and Git actions require interactive confirmation. If
  confirmations are disabled, Shamaran rejects them instead of silently approving.
- Git push, force-push, reset-hard, clean, filesystem deletion, and privilege
  escalation are not implemented.
- The agent loop has a hard step budget.
- Memory is local SQLite and rejects obvious credential-like values.
- Logs redact common credential assignments and should still be treated as local
  operational data.

## Trust assumptions and limitations

Running Python or pytest can execute repository code, so these commands require
appropriate policy or confirmation. Allowlisting cannot make untrusted source safe.
Symlink protection relies on operating-system path resolution and should be tested
on each supported platform. The included secret checker only catches obvious
patterns; use a dedicated scanner for high-assurance workflows.

Ollama traffic goes to the configured endpoint. A remote endpoint is not local-first;
review that endpoint's privacy and transport security before use.

## Reporting a vulnerability

Do not open a public issue containing exploit details or secrets. Contact the
repository maintainer privately through the security-reporting channel listed on
the eventual GitHub repository. Include affected version, reproduction steps,
impact, and a suggested mitigation if available.
