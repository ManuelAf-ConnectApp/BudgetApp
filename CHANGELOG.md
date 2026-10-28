# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added

- Search field and quick creation action in the budget history panel.
- Persistent financial summary with subtotal, discount, VAT, total, and primary save/export actions.
- Design specification and workspace concept mockup for the application redesign.

### Changed

- Redesigned the budget workspace into three resizable areas: history, editor, and summary.
- Added a budget header with visible date and status controls.
- Refined the shared visual system for cards, inputs, tables, buttons, menus, and focus states.
- Kept existing budget workflows, keyboard shortcuts, bilingual UI, and domain behavior intact while improving visual hierarchy.

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
