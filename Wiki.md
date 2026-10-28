# BudgetApp Wiki

## Overview

BudgetApp is a desktop application for creating and managing commercial budgets. It is built with Python and PySide6, supports a local SQLite database and a remote MySQL database, and provides a bilingual Spanish/English interface.

The application is designed around a budgeting workspace with searchable history, a focused editor, and a persistent financial summary.

## Main capabilities

- Create, edit, duplicate, delete, and track the status of budgets.
- Save company tax details and customer information.
- Calculate totals with decimal arithmetic and consistent rounding.
- Export commercial budgets to PDF and print the active budget.
- Work with local SQLite persistence or a remote MySQL installation.
- Store remote database passwords in the operating-system keychain.
- Create validated SQLite backups and restore them safely.
- Switch the user interface and generated commercial PDFs between Spanish and English.

## Requirements

- Python 3.11 or newer.
- The dependencies listed in `requirements.txt`.
- Optional: MySQL for remote mode.
- Optional: PyInstaller and the relevant platform tools when building installers.

## Installation and startup

Create a virtual environment, install dependencies, and start the application:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

On its first launch, BudgetApp asks where to work:

- **Local installation** uses a SQLite database stored in the user's application-data directory.
- **Remote installation** requests MySQL connection details and stores the password in the system keychain rather than application settings.

## Budget workflow

The primary workspace is split into three resizable areas:

| Area | Purpose |
| --- | --- |
| History panel | Create, search, and open saved budgets. |
| Budget editor | Enter client details, date, and budget line items. |
| Summary panel | Review subtotal, discounts, VAT, total, and save or export actions. |

### Creating a budget

1. Select **New budget** from the history panel or use `Ctrl+N`.
2. Enter the customer name and tax identifier.
3. Add one or more budget lines, including description, product, quantity, unit price, discount, and VAT.
4. Review the persistent financial summary.
5. Select **Save** or use `Ctrl+S`.

### Managing budgets

Saved budgets can be opened from the history panel. The application supports draft, sent, and accepted statuses. Additional actions, including duplicate, delete, print, and save as, remain available through the application menus and keyboard shortcuts.

### Exporting and printing

- Use **Export PDF** in the summary panel or `Ctrl+P` to create a PDF of the active budget.
- Use the print action from the File menu to send the active budget to a printer.
- PDF content follows the language selected in the interface.

## Data and security

### Local data

Local mode uses SQLite. Backups are validated before restoration, and restoring a backup replaces the local database only after confirmation.

### Remote data

Remote mode uses MySQL. Remote budget operations support transactional updates and deletion. Passwords are stored through the operating system's keychain integration and are not written to application settings.

## Interface languages

Spanish and English are available from the start screen and application settings. The chosen language applies to the interface and commercial PDF exports.

## Quality checks

Run the test suite with:

```bash
python3 -m unittest discover -v
```

The repository includes Ruff configuration and a GitHub Actions workflow. On every push and pull request, the Quality workflow runs the unit tests and `ruff check .`.

## Building installers

### macOS

```bash
python3 -m pip install -r requirements.txt
bash build_mac_installer.sh
```

The generated application is located at `dist/BudgetApp.app`, and the disk image is created at `dist/BudgetApp.dmg`.

### Windows

```bat
python -m pip install -r requirements.txt
build_windows_installer.bat
```

The Windows bundle is created in `dist/windows/BudgetApp/` and the installer in `dist/installer/BudgetApp-Setup.exe`. Inno Setup 6, or `ISCC.exe` on `PATH`, is required.

### Linux

```bash
python3 -m pip install -r requirements.txt
bash build_linux_installer.sh
```

The build creates `dist/linux/BudgetApp/` and prepares an `AppDir` in `dist/AppDir/`. If `appimagetool` is installed, it also creates `dist/installer/BudgetApp-x86_64.AppImage`.

## Project structure

```text
application/       Presentation and use-case logic
core/              Domain models, records, and repository contracts
infrastructure/    Database, services, runtime, and PySide6 UI implementations
installer/         Platform-specific installer resources
tests/             Automated tests
```

The codebase is inspired by Clean Architecture. It separates domain models, application logic, infrastructure adapters, and user-interface code, while keeping the composition and some UI behavior intentionally lightweight for a desktop application of this size.

## Design resources

The redesign rationale is documented in [docs/REDESIGN.md](docs/REDESIGN.md). A visual concept is available at [docs/design/budgetapp-workspace-concept.png](docs/design/budgetapp-workspace-concept.png).

## License

BudgetApp is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for the full text.
