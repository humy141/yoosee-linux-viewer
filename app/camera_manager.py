import sqlite3
import os
from app.link_discovery import CameraLinkDiscovery


class CameraStore:
    """Lưu trữ thông tin camera trong SQLite."""

    DB_FILE = "cameras.db"

    def __init__(self):
        self.conn = sqlite3.connect(self.DB_FILE)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cameras (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                ip TEXT NOT NULL UNIQUE,
                port INTEGER DEFAULT 554,
                username TEXT DEFAULT 'admin',
                password TEXT DEFAULT 'admin',
                rtsp_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def add_camera(self, name, ip, port=554, username="admin", password="admin"):
        """Thêm camera mới. Nếu IP đã tồn tại, update."""
        try:
            # Kiểm tra RTSP URL
            discovery = CameraLinkDiscovery(ip, username, password)
            discovery.discover_all()
            rtsp_url = discovery.get_best_rtsp_url()

            # Cố gắng insert, nếu lỗi unique constraint thì update
            self.cursor.execute(
                """
                INSERT INTO cameras (name, ip, port, username, password, rtsp_url)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, ip, port, username, password, rtsp_url),
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            # IP đã tồn tại, cập nhật
            self.cursor.execute(
                """
                UPDATE cameras
                SET name=?, port=?, username=?, password=?, rtsp_url=?
                WHERE ip=?
                """,
                (name, port, username, password, discovery.get_best_rtsp_url(), ip),
            )
            self.conn.commit()

        return self.get_camera_by_ip(ip)

    def get_camera_by_ip(self, ip):
        self.cursor.execute("SELECT * FROM cameras WHERE ip=?", (ip,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def list_cameras(self):
        self.cursor.execute("SELECT * FROM cameras ORDER BY created_at DESC")
        return [dict(row) for row in self.cursor.fetchall()]

    def delete_camera(self, ip):
        self.cursor.execute("DELETE FROM cameras WHERE ip=?", (ip,))
        self.conn.commit()

    def build_rtsp_url(self, camera):
        """Build RTSP URL từ thông tin camera."""
        if camera.get("rtsp_url"):
            return camera["rtsp_url"]
        # Fallback nếu không có RTSP URL
        return f"rtsp://{camera['username']}:{camera['password']}@{camera['ip']}:{camera['port']}/onvif2"

    def close(self):
        self.conn.close()


__all__ = ["CameraStore"]
