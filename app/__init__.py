from pathlib import Path

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
        CONFIG_FILE.write_text('{"username": "admin", "password": "admin"}', encoding="utf-8")
    if not CAMERA_FILE.exists():
        CAMERA_FILE.write_text('[]', encoding="utf-8")


def read_json(path: Path):
    try:
        return __import__("json").loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [] if path.name.endswith(".json") and "cameras" in path.name else {}


def write_json(path: Path, data):
    path.write_text(__import__("json").dumps(data, indent=2), encoding="utf-8")
