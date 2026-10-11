from pathlib import Path
import json

APP_NAME = "Yoosee Linux"
CONFIG_DIR = Path.home() / ".yoosee_linux"
CONFIG_FILE = CONFIG_DIR / "config.json"
CAMERA_FILE = CONFIG_DIR / "cameras.json"
LOG_DIR = CONFIG_DIR / "logs"
RECORD_DIR = CONFIG_DIR / "recordings"


def ensure_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    RECORD_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps({"username": "admin", "password": "admin"}, indent=2), encoding="utf-8")
    if not CAMERA_FILE.exists():
        CAMERA_FILE.write_text("[]", encoding="utf-8")


def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default if default is not None else {}


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
