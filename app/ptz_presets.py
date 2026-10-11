import json
import os


class PTZPresetManager:
    """Quản lý preset PTZ theo từng camera. Lưu vào file JSON."""

    def __init__(self, base_path="ptz_presets.json"):
        self.base_path = base_path
        self.presets = self._load()

    def _load(self):
        if not os.path.exists(self.base_path):
            return {}
        try:
            with open(self.base_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save(self):
        with open(self.base_path, "w", encoding="utf-8") as f:
            json.dump(self.presets, f, indent=2, ensure_ascii=False)

    def get_presets_for_camera(self, camera_name):
        return self.presets.get(camera_name, {})

    def add_preset(self, camera_name, preset_name, position):
        if camera_name not in self.presets:
            self.presets[camera_name] = {}
        self.presets[camera_name][preset_name] = position
        self._save()

    def remove_preset(self, camera_name, preset_name):
        if camera_name in self.presets and preset_name in self.presets[camera_name]:
            del self.presets[camera_name][preset_name]
            if not self.presets[camera_name]:
                del self.presets[camera_name]
            self._save()

    def list_presets(self, camera_name):
        return list(self.get_presets_for_camera(camera_name).keys())

    def get_preset(self, camera_name, preset_name):
        return self.get_presets_for_camera(camera_name).get(preset_name)


__all__ = ["PTZPresetManager"]
