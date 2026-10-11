import os
import re
import json
import time
import socket
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin


class PTZDebugTool:
    """Tool tìm endpoint PTZ và thử lệnh điều khiển cho camera FNKVision SEA-U2."""

    DEFAULT_ENDPOINTS = [
        "/onvif/device_service",
        "/onvif/media_service",
        "/onvif/ptz_service",
        "/onvif/PTZService",
        "/onvif/DeviceService",
        "/onvif/MediaService",
        "/cgi-bin/ptz.cgi",
        "/cgi-bin/ptz",
        "/cgi-bin/ptz.cgi?action=move",
        "/cgi-bin/ptz.cgi?action=zoom",
        "/cgi-bin/api/ptz",
        "/api/ptz",
        "/ptz",
        "/PTZ",
        "/ptz/control",
        "/cgi-bin/ptzControl.cgi",
        "/cgi-bin/ptzControl",
        "/cgi-bin/camera_control.cgi",
        "/cgi-bin/camera.cgi?action=ptz",
        "/cgi-bin/ptz.cgi?command=move",
        "/cgi-bin/ptz.cgi?command=zoom",
    ]

    PTZ_PATHS = [
        "stream1",
        "stream",
        "live",
        "live/ch0",
        "live/ch1",
        "h264/ch1",
        "mjpeg/ch1",
        "video",
        "cgi-bin/api/stream",
        "api/stream",
    ]

    def __init__(self, ip, username="admin", password="admin", port=80):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = int(port or 80)
        self.base = f"http://{self.ip}:{self.port}"

    def test_url(self, url):
        try:
            r = requests.get(url, auth=HTTPBasicAuth(self.username, self.password), timeout=5)
            return {
                "status": r.status_code,
                "content_type": r.headers.get("Content-Type"),
                "snippet": r.text[:250],
                "url": url,
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "url": url}

    def discover_endpoints(self):
        result = []
        for endpoint in self.DEFAULT_ENDPOINTS:
            url = urljoin(self.base, endpoint)
            result.append(self.test_url(url))
        return result

    def try_common_onvif_checks(self):
        candidates = [
            "http://{ip}:{port}/onvif/device_service",
            "http://{ip}:{port}/onvif/device_service?wsdl",
            "http://{ip}:{port}/onvif/DeviceService",
            "http://{ip}:{port}/onvif/MediaService",
            "http://{ip}:{port}/onvif/PTZService",
        ]
        results = []
        for cand in candidates:
            url = cand.format(ip=self.ip, port=self.port)
            results.append(self.test_url(url))
        return results

    def try_ptz_commands(self):
        """Thử các lệnh điều khiển PTZ thông dụng"""
        commands = []
        payloads = [
            {"action": "ptz_move", "direction": "left"},
            {"action": "ptz_move", "direction": "right"},
            {"action": "ptz_move", "direction": "up"},
            {"action": "ptz_move", "direction": "down"},
            {"action": "zoom", "direction": "in"},
            {"action": "zoom", "direction": "out"},
            {"action": "ptz", "cmd": "left"},
            {"action": "ptz", "cmd": "right"},
            {"action": "ptz", "cmd": "up"},
            {"action": "ptz", "cmd": "down"},
        ]
        for payload in payloads:
            for endpoint in self.DEFAULT_ENDPOINTS:
                url = urljoin(self.base, endpoint)
                try:
                    resp = requests.get(url, params=payload, auth=HTTPBasicAuth(self.username, self.password), timeout=5)
                    commands.append({
                        "url": url,
                        "payload": payload,
                        "status": resp.status_code,
                        "snippet": resp.text[:200],
                    })
                except Exception as e:
                    commands.append({"url": url, "payload": payload, "status": "error", "error": str(e)})
        return commands

    def dump_report(self):
        report = {
            "camera_ip": self.ip,
            "username": self.username,
            "password": self.password,
            "port": self.port,
            "endpoint_scan": self.discover_endpoints(),
            "onvif_scan": self.try_common_onvif_checks(),
            "ptz_command_tests": self.try_ptz_commands(),
        }
        return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PTZ debug tool for FNKVision camera")
    parser.add_argument("--ip", required=True, help="IP camera")
    parser.add_argument("--user", default="admin")
    parser.add_argument("--pass", default="admin")
    parser.add_argument("--port", default=80, type=int)
    parser.add_argument("--out", default="ptz_debug_report.json")
    args = parser.parse_args()

    tool = PTZDebugTool(args.ip, args.user, args.pass, args.port)
    report = tool.dump_report()
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(json.dumps({"saved_to": args.out, "results": len(report["endpoint_scan"])}, ensure_ascii=False))
