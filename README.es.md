# Budget App

🧾 Budget App es una aplicación de escritorio para gestionar presupuestos comerciales, con soporte para SQLite local y MySQL remoto. Está creada con Python y PySide6 e incluye textos de interfaz bilingües en español e inglés.

## ✨ Características destacadas

- 🗂️ Crear y editar presupuestos
- 🏢 Guardar los datos fiscales de la empresa
- 💾 Persistir datos de forma local o remota
- 📋 Consultar presupuestos guardados
- 🧾 Exportar presupuestos a PDF
- 🌍 Cambiar la interfaz entre español e inglés
- 🖼️ Pantalla de inicio e icono de aplicación personalizados
- 🔄 Actualizar, duplicar, eliminar y hacer seguimiento del estado de los presupuestos (borrador, enviado, aceptado)
- 🔐 Guardar las credenciales de la base de datos remota en el llavero del sistema operativo
- 💶 Calcular importes monetarios con aritmética decimal y redondeo consistente
- 🛡️ Crear copias de seguridad SQLite validadas y restaurarlas de forma segura
- ✨ Trabajar en un espacio rediseñado de tres paneles: historial con búsqueda, editor centrado y resumen financiero persistente

## 🎨 Espacio de trabajo rediseñado

El flujo de trabajo de presupuestos se organiza alrededor de la tarea principal:

- **Historial con búsqueda**: crea, encuentra y abre presupuestos guardados rápidamente desde el panel izquierdo.
- **Editor centrado**: reúne los datos del cliente, la fecha y las líneas del presupuesto en el espacio de trabajo central.
- **Resumen persistente**: consulta subtotal, descuentos, IVA, total y las acciones principales de guardar o exportar sin abandonar el presupuesto.
- **Jerarquía visual más clara**: las tarjetas, tablas, campos, botones, estados de foco y controles de estado renovados mejoran la legibilidad sin perder los atajos de teclado ni la interfaz bilingüe.

La dirección de diseño está documentada en [docs/REDESIGN.md](docs/REDESIGN.md), junto con un concepto visual en [docs/design/budgetapp-workspace-concept.png](docs/design/budgetapp-workspace-concept.png).

## Mejoras de la versión

Esta versión refuerza la integridad de los datos, la seguridad y la mantenibilidad:

- Los datos de empresa de SQLite ahora permiten actualizaciones posteriores, en lugar de fallar después del primer guardado.
- Los repositorios local y remoto permiten actualizaciones transaccionales y eliminación de presupuestos.
- El historial remoto conserva el ID del presupuesto en la base de datos, evitando agrupar registros distintos de forma accidental.
- Los PDFs comerciales generados siguen el idioma español o inglés seleccionado en la interfaz.
- El proyecto incluye comprobaciones de calidad automatizadas mediante Ruff y GitHub Actions.

## 🏗️ Resumen de arquitectura

El código está **inspirado en Clean Architecture**, pero todavía **no es una implementación estricta** de Clean Architecture.

### ✅ Lo que ya está bien estructurado

- `core/model`: entidades de dominio como `Budget`, `BudgetLine` y `Company`
- `core/records`: registros tipo DTO utilizados en el límite de los repositorios
- `application`: lógica de presentación y casos de uso, incluido el `BudgetViewModel` principal
- `infrastructure/database`: implementaciones de acceso a datos para SQLite y MySQL
- `infrastructure/services`: servicios externos como la generación de PDF
- `infrastructure/ui`: vistas Qt, diálogos, estilos y cableado de presentación
- `main.py`: raíz de composición que ensambla la aplicación

### ⚠️ Dónde sigue desviándose de Clean Architecture

- `main.py` se ha reducido a un punto de entrada mínimo, pero la capa de bootstrap sigue conectando implementaciones concretas.
- Las clases de base de datos intercambian ahora registros tipo DTO en vez de entidades de dominio directamente, lo cual es más limpio que antes, pero continúa siendo una solución sencilla.
- Algunos módulos todavía mezclan textos y comportamiento de interfaz, algo aceptable en una aplicación pequeña pero menos adecuado a largo plazo.

### 🧠 Evaluación de Clean Code

El código es razonablemente modular y legible, aunque todavía hay aspectos mejorables:

- responsabilidades duplicadas en algunas clases de interfaz
- métodos demasiado largos o con más de una responsabilidad
- clases que dependen directamente de implementaciones concretas en lugar de abstracciones
- algunos nombres y mensajes siguen ligados al lenguaje de negocio actual en lugar de estar totalmente normalizados

En conjunto, se trata de una implementación **parcial de clean architecture / clean code**, no de una implementación estricta. El proyecto tiene estructura suficiente para evolucionar, pero aún hay margen para introducir límites más claros e inversión de dependencias.

## 📁 Estructura del proyecto

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

## 🚀 Ejecutar la aplicación

Crea un entorno virtual, instala las dependencias del proyecto y ejecuta:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

La conexión remota guarda su contraseña en el llavero seguro del sistema mediante `keyring`; no se persiste en los ajustes de la aplicación.

## Calidad

La suite se ejecuta con:

```bash
python3 -m unittest discover -v
```

El repositorio incluye configuración de Ruff y un flujo de GitHub Actions que ejecuta pruebas y análisis estático en cada `push` y `pull request`.

Si utilizas una compilación empaquetada, la aplicación generada puede ejecutarse desde la salida `dist/` creada por el proceso de build.

## 📦 Generar instalable en macOS

El proyecto incluye una especificación de PyInstaller y un script para generar la aplicación y un `.dmg`.

```bash
python3 -m pip install -r requirements.txt
bash build_mac_installer.sh
```

El resultado queda en `dist/BudgetApp.app` y `dist/BudgetApp.dmg`.

La base de datos local se guarda en la carpeta de datos de usuario, no dentro del bundle.

## 📦 Generar instalable en Windows

El proyecto también incluye una especificación específica para Windows y un script de build que genera el bundle con PyInstaller y después lo empaqueta con Inno Setup.

```bat
python -m pip install -r requirements.txt
build_windows_installer.bat
```

El resultado queda en `dist/windows/BudgetApp/` para el bundle y en `dist/installer/BudgetApp-Setup.exe` para el instalador.

Nota: necesitas tener Inno Setup 6 instalado en Windows o `ISCC.exe` disponible en `PATH`.

## 📦 Generar instalable en Linux

En Linux el proyecto usa un flujo de tipo AppImage. El script genera el bundle con PyInstaller, prepara un `AppDir` y, si tienes `appimagetool` instalado, construye el `.AppImage` final.

```bash
python3 -m pip install -r requirements.txt
bash build_linux_installer.sh
```

El bundle queda en `dist/linux/BudgetApp/` y el AppDir preparado en `dist/AppDir/`. Si `appimagetool` está disponible, el instalador final se genera en `dist/installer/BudgetApp-x86_64.AppImage`.

Nota: este flujo asume una distribución x86_64 y requiere `appimagetool` para producir el archivo final `.AppImage`.

## 📝 Notas

- La persistencia local usa SQLite.
- La persistencia remota usa MySQL.
- Los textos de interfaz se gestionan mediante un pequeño diccionario interno bilingüe.

## 📜 Licencia

Este proyecto se distribuye bajo la licencia Apache License 2.0. Consulta [LICENSE](LICENSE).
