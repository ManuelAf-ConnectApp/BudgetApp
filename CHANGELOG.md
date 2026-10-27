# Changelog

All notable changes to this project are documented in this file.

## [1.1.0] - 2026-10-27

### Added

- New Budget App logo on the welcome screen, application windows, and packaged builds.
- Budget lifecycle actions: update, duplicate, delete, and status tracking (`draft`, `sent`, `accepted`).
- Secure storage for remote database passwords through the operating-system keychain.
- SQLite backup validation and safe restore workflow.
- Decimal-based monetary calculations with half-up rounding.
- Spanish and English labels in commercial PDF exports.
- Ruff configuration and GitHub Actions quality workflow.

### Changed

- Local company profile save now updates the existing profile.
- Remote history retains budget IDs and no longer groups distinct budgets by their content.
- Local and remote budget saves are transactional and support updates.
- Package specifications now include the Budget App logo.
- Test discovery now works with the standard `unittest discover` command.

### Security

- Remote database names are validated before they are used to create a MySQL database.
- Remote passwords are no longer stored in application settings.
