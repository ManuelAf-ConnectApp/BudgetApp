@echo off
setlocal enabledelayedexpansion

set "ROOT=%~dp0"
cd /d "%ROOT%"

if exist "build\windows" rmdir /s /q "build\windows"
if exist "dist\windows" rmdir /s /q "dist\windows"

echo Building Windows bundle with PyInstaller...
python -m PyInstaller --noconfirm --clean --distpath "dist\windows" --workpath "build\windows" "BudgetApp.windows.spec"
if errorlevel 1 exit /b 1

set "ISCC="
where iscc >nul 2>nul
if not errorlevel 1 set "ISCC=iscc"

if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if not defined ISCC (
  echo Inno Setup compiler not found. Install Inno Setup 6 or add ISCC to PATH.
  exit /b 1
)

echo Building Windows installer...
"%ISCC%" /O"dist\installer" "installer\windows\BudgetApp.iss"
if errorlevel 1 exit /b 1

echo Installer created in dist\installer
