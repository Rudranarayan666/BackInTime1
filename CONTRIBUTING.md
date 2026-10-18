
# Contributing to BackInTime

Thank you for your interest in contributing to BackInTime.

BackInTime is an early-stage project focused on backup correctness, snapshot integrity, safe restoration, and reliable failure handling. Contributions should prioritize correctness, reproducibility, and data safety.

## Before You Start

1. Read the project [README.md](README.md).
2. Check existing issues and pull requests before starting work.
3. For significant changes, open an issue to discuss the proposed approach.
4. For security vulnerabilities, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.
5. Ensure that contributed code and other materials may legally be distributed under the project's licence.

## Useful Contributions

We welcome contributions involving:

- Bug reports with reproducible steps.
- Automated regression tests.
- Snapshot creation and deletion.
- Backup change detection.
- Restore correctness and data safety.
- Include/exclude rule handling.
- File metadata preservation.
- Operation locking and interruption recovery.
- Destination validation and mount handling.
- Error reporting and logging.
- Documentation, testing, and development tooling.

## Development Principles

- Keep changes focused and reviewable.
- Prefer small fixes over unrelated rewrites.
- Keep core backup logic separate from GUI code where practical.
- Explain the purpose of new dependencies.
- Do not claim a feature is complete without implementation and appropriate tests.
- Do not expose credentials or private user data in commits, logs, or test fixtures.
- Never use real personal files or production backups for destructive tests.
- Make destructive operations predictable and explicitly validated.
- Document intentional behaviour changes.

## Development Setup

Follow the installation and development instructions provided in the repository.

The project intends to use Python, pytest, and Ruff. Exact commands should be added here once the dependency configuration and test setup are available.

Before submitting changes:

1. Run the relevant focused tests.
2. Run the full test suite if available.
3. Run configured linting and formatting checks.
4. Review your changes with `git diff`.
5. Check for unrelated files, secrets, generated artifacts, and machine-specific settings.
6. Update documentation if behaviour or configuration changes.

If a test cannot be run, state that clearly in your pull request.

## Backup and Restore Testing

Changes affecting backup correctness or data safety should include regression tests where practical.

Important scenarios include:

- A backup where the only change is file deletion.
- Removing one snapshot without changing other snapshots.
- Including a directory inside an excluded directory.
- Restoring without deleting unrelated or excluded live files.
- Two operations targeting the same profile simultaneously.
- Preservation of supported file metadata.
- An unavailable destination or insufficient permissions.
- A failed or interrupted copy operation.
- Detection of incomplete snapshots.
- Safe snapshot retention and removal.
- Accurate interpretation of external command exit codes.

Use temporary directories and disposable test data. Never run destructive tests against real user files.

## Pull Request Guidelines

Each pull request should include:

- **Summary:** What changed?
- **Reason:** Which problem does it address?
- **Expected behaviour:** What should happen after the change?
- **Tests:** Which commands were run, and what were the results?
- **Risks:** Could the change affect data, metadata, compatibility, or performance?
- **Documentation:** Were relevant instructions updated?

Keep pull requests focused on one main change whenever possible.

Do not state that tests passed unless they were actually run.

## Commit Messages

Use concise, descriptive commit messages.

Examples:

- `test: cover deletion-only backups`
- `fix: improve snapshot removal safety`
- `fix: preserve unrelated files during restore`
- `docs: clarify backup reliability requirements`

## Code of Conduct

By participating in this project, you agree to follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

Thank you for helping make backup software safer and more reliable.
