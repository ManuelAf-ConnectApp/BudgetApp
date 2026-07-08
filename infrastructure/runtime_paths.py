from __future__ import annotations

import os
import sys
from pathlib import Path


APP_NAME = "Budget App"


def project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parents[1]


def resource_path(*parts: str) -> Path:
    return project_root().joinpath(*parts)


def user_data_root(app_name: str = APP_NAME) -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    path = base / app_name
    path.mkdir(parents=True, exist_ok=True)
    return path


def local_database_path(database_name: str = "my_budgets.db") -> Path:
    return user_data_root() / database_name
