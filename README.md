# Budget App

🧾 Budget App is a desktop application for managing commercial budgets with local SQLite and remote MySQL support. It is built with Python and PySide6, and it already includes bilingual UI text in Spanish and English.

## ✨ Highlights

- 🗂️ Create and edit budgets
- 🏢 Store company fiscal data
- 💾 Persist data locally or remotely
- 📋 List saved budgets
- 🧾 Export budgets to PDF
- 🌍 Switch the interface between Spanish and English

## 🏗️ Architecture snapshot

The codebase is **inspired by Clean Architecture**, but it is **not a strict Clean Architecture implementation** yet.

### ✅ What is already well structured

- `core/model`: domain entities such as `Budget`, `BudgetLine`, and `Company`
- `core/records`: DTO-style records used across the repository boundary
- `application`: presentation and use-case logic, including the main `BudgetViewModel`
- `infrastructure/database`: data access implementations for SQLite and MySQL
- `infrastructure/services`: external services such as PDF generation
- `infrastructure/ui`: Qt views, dialogs, styles, and presentation wiring
- `main.py`: composition root that assembles the application

### ⚠️ Where it still deviates from Clean Architecture

- `main.py` has been reduced to a minimal entry point, but the bootstrap layer still wires concrete implementations.
- Database classes now exchange DTO-style records instead of domain entities directly, which is cleaner than before, but still simple.
- Some modules still contain UI text and behavior mixed together, which is acceptable in a small app but less ideal for long-term maintainability.

### 🧠 Clean Code assessment

The code is reasonably modular and readable, but there are still a few issues to improve:

- duplicated responsibilities in some UI classes
- some methods are too long or do more than one thing
- some classes depend directly on concrete implementations instead of abstractions
- some naming and message text are still tied to the current business language instead of being fully normalized

Overall, this is a **partial clean architecture / clean code implementation**, not a strict one. The project is structured enough to evolve, but there is still room to introduce clearer boundaries and dependency inversion.

## 📁 Project structure

```text
core/
  model/
infrastructure/
  database/
  services/
  ui/
    dialogs
    views
    view_model
main.py
```

## 🚀 Running the app

Install the dependencies used by the project and run:

```bash
python main.py
```

If you use a packaged build, the generated app can be launched from the `dist/` output produced by the build process.

## 📦 Generar instalable en macOS

El proyecto incluye una spec de PyInstaller y un script para generar la app y un `.dmg`.

```bash
python3 -m pip install -r requirements.txt
bash build_mac_installer.sh
```

El resultado queda en `dist/BudgetApp.app` y `dist/BudgetApp.dmg`.

La base de datos local se guarda en la carpeta de datos de usuario, no dentro del bundle.

## 📦 Generar instalable en Windows

El proyecto también incluye una spec específica para Windows y un script de build que genera el bundle con PyInstaller y después lo empaqueta con Inno Setup.

```bat
python -m pip install -r requirements.txt
build_windows_installer.bat
```

El resultado queda en `dist/windows/BudgetApp/` para el bundle y en `dist/installer/BudgetApp-Setup.exe` para el instalador.

Nota: necesitas tener Inno Setup 6 instalado en Windows o `ISCC.exe` disponible en `PATH`.

## 📦 Generar instalable en Linux

En Linux el proyecto usa un flujo tipo AppImage. El script genera el bundle con PyInstaller, prepara un `AppDir` y, si tienes `appimagetool` instalado, construye el `.AppImage` final.

```bash
python3 -m pip install -r requirements.txt
bash build_linux_installer.sh
```

El bundle queda en `dist/linux/BudgetApp/` y el AppDir preparado en `dist/AppDir/`. Si `appimagetool` está disponible, el instalador final se genera en `dist/installer/BudgetApp-x86_64.AppImage`.

Nota: este flujo asume una distribución x86_64 y requiere `appimagetool` para producir el archivo final `.AppImage`.

## 📝 Notes

- Local persistence uses SQLite.
- Remote persistence uses MySQL.
- UI text is managed through a small internal bilingual dictionary.

## 📜 License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
