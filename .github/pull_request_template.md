## Summary

Describe what changed and why.

## User impact

Describe visible behavior, compatibility, and any migration required.

## Validation

- [ ] `python -m pytest`
- [ ] `python scripts/check_secrets.py`
- [ ] `git diff --check`
- [ ] Documentation updated when public behavior changed

## Safety review

- [ ] No credentials, private data, or generated runtime files are included
- [ ] Filesystem, terminal, Git, and confirmation boundaries remain fail-closed
