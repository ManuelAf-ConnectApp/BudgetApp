#!/usr/bin/env bash
set -euo pipefail

python3 -m PyInstaller BudgetApp.spec

APP_PATH="dist/BudgetApp.app"
DMG_PATH="dist/BudgetApp.dmg"

if [ -d "$APP_PATH" ]; then
  rm -f "$DMG_PATH"
  hdiutil create -volname "BudgetApp" -srcfolder "$APP_PATH" -ov -format UDZO "$DMG_PATH"
  echo "DMG creado en: $DMG_PATH"
else
  echo "No se encontró $APP_PATH"
  exit 1
fi
