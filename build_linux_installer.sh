#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

BUILD_DIR="build/linux"
DIST_DIR="dist/linux"
APPDIR="dist/AppDir"
APP_NAME="BudgetApp"

rm -rf "$BUILD_DIR" "$DIST_DIR" "$APPDIR"

python3 -m PyInstaller --noconfirm --clean --distpath "$DIST_DIR" --workpath "$BUILD_DIR" "BudgetApp.linux.spec"

mkdir -p "$APPDIR/usr/bin/$APP_NAME" "$APPDIR/usr/share/applications" "$APPDIR/usr/share/icons/hicolor/512x512/apps"

cp -R "$DIST_DIR/$APP_NAME/"* "$APPDIR/usr/bin/$APP_NAME/"
cp "installer/linux/AppRun" "$APPDIR/AppRun"
cp "installer/linux/BudgetApp.desktop" "$APPDIR/BudgetApp.desktop"
cp "installer/linux/BudgetApp.desktop" "$APPDIR/usr/share/applications/BudgetApp.desktop"
cp "assets/app_icon.png" "$APPDIR/usr/share/icons/hicolor/512x512/apps/BudgetApp.png"
cp "assets/app_icon.png" "$APPDIR/BudgetApp.png"

chmod +x "$APPDIR/AppRun"
chmod +x "$APPDIR/usr/bin/$APP_NAME/$APP_NAME"

if command -v appimagetool >/dev/null 2>&1; then
  OUTPUT_DIR="dist/installer"
  mkdir -p "$OUTPUT_DIR"
  appimagetool "$APPDIR" "$OUTPUT_DIR/BudgetApp-x86_64.AppImage"
  echo "AppImage created in $OUTPUT_DIR/BudgetApp-x86_64.AppImage"
else
  echo "PyInstaller bundle created in $DIST_DIR/$APP_NAME"
  echo "AppDir prepared in $APPDIR"
  echo "Install appimagetool to build the final .AppImage"
fi
