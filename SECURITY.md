
# Security Policy

## Project Status

BackInTime is under development. It should not be considered production-ready until its implementation, testing, and release status support that claim.

Do not rely on experimental functionality as the sole protection for important data.

## Supported Versions

A formal release and supported-version policy has not yet been established.

Once releases are available, this section should list the versions receiving security fixes.

Until then, include the relevant commit or version when reporting a vulnerability.

## Reporting a Vulnerability

**Please do not report security vulnerabilities in public issues, discussions, or pull requests.**

Use GitHub's private vulnerability reporting or Security Advisories feature if it is enabled for this repository.

If private reporting is unavailable, contact the repository maintainers through a verified private contact method.

Before publishing this file, the repository owner should confirm that a private reporting method is available and monitored.

## What to Include

Where possible, include:

- A clear description of the vulnerability.
- Potential impact and affected functionality.
- The affected commit or version.
- Operating system and relevant configuration.
- Minimal reproduction steps.
- A proof of concept using disposable test data, if appropriate.
- Suggested mitigation, if known.

Remove passwords, tokens, private keys, personal data, and sensitive file paths from logs before sharing them.

## Examples of Security Issues

Examples include:

- Path traversal in backup or restore operations.
- Restore operations deleting files outside their intended scope.
- Unsafe handling of symbolic links or destination paths.
- Permission handling that exposes protected data.
- Sensitive information written to logs or metadata.
- Race conditions that corrupt snapshots.
- Unsafe recovery of stale locks or incomplete operations.
- Vulnerable dependencies affecting the application.

## Response Process

Maintainers will review reports as promptly as practical, investigate reproducibility and severity, and coordinate remediation and disclosure with the reporter.

Response times cannot be guaranteed while the project is in early development.

Please allow time for investigation and remediation before publicly disclosing a vulnerability.

## Security Development Principles

- Validate paths and destructive operations.
- Constrain operations to their intended scope.
- Do not silently mark failed or partial backups as successful.
- Use disposable data in security tests.
- Keep logs useful without exposing secrets.
- Add regression tests for confirmed security defects.
- Review dependency maintenance and licence compatibility.
