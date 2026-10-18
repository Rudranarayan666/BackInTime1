
# BackInTime

**An independent backup and snapshot application focused on data integrity, safe restoration, and reliable recovery.**

> **Project status:** Early development. Features described as planned are not necessarily implemented or production-ready.

## Overview

BackInTime aims to provide reliable backups and snapshots while addressing common challenges in backup software, including deletion detection, snapshot integrity, restore safety, interrupted operations, and unclear error messages.

The project focuses on ensuring that backups accurately represent filesystem changes and that restore or snapshot-removal operations do not unexpectedly damage other data.

This repository is an independent implementation and is not affiliated with or endorsed by the original Back In Time project or its maintainers.

## Project Goals

- Create accurate snapshots of filesystem changes.
- Detect additions, modifications, and deletion-only changes.
- Prevent snapshot removal from corrupting other snapshots.
- Make restore operations predictable and safe.
- Handle concurrent backup and restore operations safely.
- Recover from interrupted operations where possible.
- Provide clear, actionable error messages.
- Test important edge cases using automated regression tests.

## Planned Features

- Local filesystem backups and timestamped snapshots.
- Efficient storage of unchanged files.
- Detection of file additions, modifications, and deletions.
- Selective file and directory restoration.
- Configurable include and exclude rules.
- Safe snapshot deletion and retention management.
- Backup and restore operation locking.
- Detection of incomplete or interrupted snapshots.
- Destination availability and permission checks.
- Clear logging and error reporting.
- Automated tests and continuous integration.
- A desktop interface and command-line workflow, subject to implementation.

## Reliability and Testing Priorities

The initial requirements are informed by backup reliability issues, including:

| Area | Expected Behaviour |
|---|---|
| Deletion-only backups | A backup must correctly record changes even when files were only deleted. |
| Snapshot integrity | Removing one snapshot must not unexpectedly change another snapshot's contents or metadata. |
| Include/exclude rules | Including a child path must not accidentally include unrelated contents of an excluded directory. |
| Restore safety | Restore operations must not delete unrelated or excluded live files unexpectedly. |
| Concurrent operations | Conflicting operations on the same backup profile must be coordinated safely. |
| Metadata preservation | Supported timestamps, permissions, and other metadata must be handled consistently. |
| Interrupted operations | Incomplete snapshots and interrupted removals must be detectable. |
| Error handling | External command failures must produce accurate and useful diagnostics. |
| Destination validation | Missing destinations and permission errors must be handled safely. |
| Regression testing | Every important bug fix should include a test that prevents the issue from returning. |

Issue numbers from other repositories may be mentioned in development notes as references, but they are not BackInTime issue identifiers unless created in this repository.

## Intended Technology

The initial technology direction is:

- **Language:** Python
- **Desktop interface:** PySide6, planned
- **File transfer:** rsync where appropriate
- **State management:** SQLite or another reviewed approach
- **Testing:** pytest
- **Code quality:** Ruff
- **Development focus:** Linux-first

The architecture may evolve as implementation requirements are validated. Backup logic should remain independently testable and separate from GUI code wherever practical.

## Getting Started

The project is under development, so installation and execution commands will be added after a runnable version and its dependency setup have been established.

For development:

1. Clone this repository.
2. Review the current project structure and setup instructions.
3. Create an isolated Python environment.
4. Install the dependencies documented by the project.
5. Run the available tests before trying backup operations.

Use temporary directories and disposable test data. Do not test experimental backup or restore functionality against your only copy of important files.

## Testing Strategy

Tests should cover:

- New, modified, renamed, and deleted files.
- Backups where deletion is the only change.
- Empty files and nested directories.
- Filenames containing spaces or unusual characters.
- Include/exclude rule combinations.
- Single-file, directory, and full-snapshot restoration.
- Preservation of supported metadata.
- Missing destinations and insufficient permissions.
- Failed or interrupted external commands.
- Concurrent operations on the same profile.
- Snapshot removal and retention safety.
- Detection and recovery of incomplete snapshots.
- Clear reporting of external command exit codes.

Destructive tests must use isolated test directories and must never target real user data.

## Data Safety and Security

- Validate paths used by backup and restore operations.
- Prevent operations from unintentionally affecting files outside their intended scope.
- Never silently treat a failed or partial backup as successful.
- Make destructive actions explicit and testable.
- Avoid logging passwords, tokens, private keys, or unnecessary personal information.
- Report vulnerabilities privately according to [SECURITY.md](SECURITY.md).

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

Do not publish security vulnerabilities in public issues. Follow the instructions in [SECURITY.md](SECURITY.md).

## Licence

This project uses the MIT License. See [LICENSE](LICENSE) for the complete licence text.

## Independence and Acknowledgements

This repository is intended to be an independent implementation. Existing backup applications and publicly documented issue reports may be used to understand common reliability problems.

The project does not claim affiliation with the original Back In Time project. Any third-party code, documentation, assets, or dependencies must be used in accordance with their applicable licences.

## Roadmap

1. Document architecture and data-safety requirements.
2. Implement a minimal local snapshot engine.
3. Add reliable detection of additions, modifications, and deletions.
4. Implement safe restoration.
5. Add snapshot integrity checks and safe removal.
6. Implement locking and interrupted-operation handling.
7. Add robust error reporting and regression tests.
8. Implement retention, scheduling, and a desktop interface.
9. Document verified installation steps and supported platforms.

---

**Warning:** This project is experimental. Do not rely on it as the sole protection for important data.
