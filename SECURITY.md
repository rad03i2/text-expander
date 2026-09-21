# Security Policy

## Scope
Text Expander is a local CLI. It does not transmit snippets, use telemetry, or require network access at runtime. Snippets are stored as plain UTF-8 JSON on the local machine.

## Sensitive data
Do **not** use the snippet store as a password manager or secret vault. Anyone/process able to read the store file can read its contents. Protect the host account and filesystem permissions, and avoid committing exported stores.

Template variables perform literal text substitution only; the project does not execute snippet text as shell commands or code.

## Reporting
Please report a suspected vulnerability privately through GitHub's available security-reporting mechanism rather than publishing exploit details in a public issue. Include affected version, reproduction steps, and impact where possible.

Maintainer: Radwan Abdulhadi Ahmed (@rad03i2).
