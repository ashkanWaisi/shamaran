# Security guide

See [SECURITY.md](../SECURITY.md) for the threat model. Keep `SHAMARAN_WORKSPACE`
dedicated to generated work, review every confirmation prompt, and treat code in any
repository as potentially executable. Set `SHAMARAN_CONFIRM_MUTATIONS=false` for a
read-focused session; this rejects confirmation-level actions.

Before a commit, inspect `git status`, inspect staged content with `git diff --cached`,
and run `python scripts/check_secrets.py`.
