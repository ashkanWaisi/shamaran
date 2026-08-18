# Changelog

All notable changes to Shamaran are recorded here.

## Unreleased

- Adopted the official Shamaran symbol, logotype, and combined PNG artwork.
- Refined project metadata and documentation under Ashkan Allahveisi's authorship.
- Added cross-platform CI for Windows, macOS, and Linux on Python 3.11–3.13.
- Documented the project's Kurdish cultural inspiration with academic and cultural
  references.
- Added issue forms, a pull request template, code ownership, Dependabot, support
  guidance, a code of conduct, and citation metadata.
- Expanded both READMEs with compatibility, configuration, troubleshooting, and
  extension guidance.
- Improved Ollama structured-output reliability with an explicit agent schema,
  deterministic generation, and one bounded format-repair attempt.
- Reframed the project's cultural note around Şahmaran's Kurdish identity and
  strengthened it with Kurdish-studies and Harvard Divinity School references.
- Added Persian/Arabic shaping and bidirectional terminal rendering while preserving
  embedded Latin text such as branch names and commands.
- Added `shamaran setup` and global user configuration loading for a short,
  directory-independent installation and launch flow.

## 0.1.0 — Initial MVP

- Bounded, JSON-protocol agent loop with concise visible plans.
- Ollama provider behind a provider-neutral interface and registry.
- Workspace-confined filesystem tools with traversal and symlink protection.
- Restricted shell-free terminal execution and confirmation policy.
- Read-only and confirmation-gated Git tools; no push implementation.
- Local SQLite memory with credential-like content rejection.
- Rich interactive CLI, built-in commands, diagnostics, and safe logging.
- English and Persian documentation, tests, CI, and initial brand assets.
