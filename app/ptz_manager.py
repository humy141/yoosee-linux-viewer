import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET


class ONVIFPTZManager:
    """Generic ONVIF PTZ controller for cameras that expose PTZ service via ONVIF."""

    DEVICE_SERVICE_CANDIDATES = [
        "/onvif/device_service",
        "/onvif/device_service?wsdl",
        "/onvif/device_service",
        "/onvif/DeviceService",
    ]

    def __init__(self, camera_ip, username="admin", password="admin", port=80):
        self.camera_ip = camera_ip
        self.username = username
        self.password = password
        self.port = int(port or 80)
        self.base_url = f"http://{camera_ip}:{self.port}"
        self.device_url = None
        self.ptz_url = None

    def _request(self, url, body, action, content_type="application/soap+xml; charset=utf-8"):
        headers = {
            "Content-Type": content_type,
            "SOAPAction": action,
        }
        resp = requests.post(
            url,
            data=body,
            headers=headers,
            auth=HTTPBasicAuth(self.username, self.password),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.text

    def discover_device_service(self):
        body = '''
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
                       xmlns:tds="http://www.onvif.org/ver10/device/wsdl">
          <soap:Body>
            <tds:GetCapabilities>
              <tds:Category>All</tds:Category>
            </tds:GetCapabilities>
          </soap:Body>
        </soap:Envelope>
        '''
        for path in self.DEVICE_SERVICE_CANDIDATES:
            url = self.base_url + path
            try:
                output = self._request(url, body, "http://www.onvif.org/ver10/device/wsdl/GetCapabilities")
                self.device_url = url
                if "XAddr" in output or "PTZ" in output:
                    return url
            except Exception:
                continue
        return None

    def discover_ptz_service(self):
        device_url = self.device_url or self.discover_device_service()
        if not device_url:
            raise RuntimeError("Không tìm thấy ONVIF Device Service trên camera.")

        body = '''
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
                       xmlns:tds="http://www.onvif.org/ver10/device/wsdl">
          <soap:Body>
            <tds:GetCapabilities>
              <tds:Category>PTZ</tds:Category>
            </tds:GetCapabilities>
          </soap:Body>
        </soap:Envelope>
        '''
        try:
            output = self._request(device_url, body, "http://www.onvif.org/ver10/device/wsdl/GetCapabilities")
            root = ET.fromstring(output)
            ns = {"soap": "http://www.w3.org/2003/05/soap-envelope", "tds": "http://www.onvif.org/ver10/device/wsdl", "tt": "http://www.onvif.org/ver10/schema"}
            for elem in root.iter():
                if elem.tag.endswith("PTZ") and elem.text and "http" in elem.text:
                    self.ptz_url = elem.text
                    return elem.text
            for elem in root.iter():
                if 'XAddr' in elem.tag:
                    self.ptz_url = elem.text
                    return elem.text
        except Exception:
            pass

        # Fallback to common ONVIF PTZ URL patterns
        fallback_urls = [
            f"{self.base_url}/onvif/ptz_service",
            f"{self.base_url}/onvif/PTZService",
            f"{self.base_url}/onvif/ptz",
        ]
        for url in fallback_urls:
            try:
                self._request(url, body, "http://www.onvif.org/ver10/device/wsdl/GetCapabilities")
                self.ptz_url = url
                return url
            except Exception:
                continue
        raise RuntimeError("Không tìm thấy ONVIF PTZ service trên camera.")

    def get_profile_token(self):
        ptz_url = self.ptz_url or self.discover_ptz_service()
        # Query profiles on media service is required to find PTZ profile token
        media_candidates = [
            f"{self.base_url}/onvif/media_service",
            f"{self.base_url}/onvif/MediaService",
            f"{self.base_url}/onvif/media",
        ]

        body = '''
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
                       xmlns:trt="http://www.onvif.org/ver10/media/wsdl">
          <soap:Body>
            <trt:GetProfiles/>
          </soap:Body>
        </soap:Envelope>
        '''
        for url in media_candidates:
            try:
                output = self._request(url, body, "http://www.onvif.org/ver10/media/wsdl/GetProfiles")
                if "ProfileToken" in output:
                    token = output.split("ProfileToken>")[-1].split("</")[0]
                    if token:
                        return token
            except Exception:
                continue
        return "main_profile"

    def move_relative(self, pan=0.0, tilt=0.0, zoom=0.0):
        service_url = self.ptz_url or self.discover_ptz_service()
        token = self.get_profile_token()
        body = f'''
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
                       xmlns:tt="http://www.onvif.org/ver10/schema"
                       xmlns:tptz="http://www.onvif.org/ver20/ptz/wsdl">
          <soap:Body>
            <tptz:RelativeMove>
              <tptz:ProfileToken>{token}</tptz:ProfileToken>
              <tptz:Translation>
                <tt:PanTilt x="{pan}" y="{tilt}" space="http://www.onvif.org/onvif/ptz/space/position"/>
                <tt:Zoom x="{zoom}" y="0" space="http://www.onvif.org/onvif/ptz/space/position"/>
              </tptz:Translation>
              <tptz:Speed>
                <tt:PanTilt x="1" y="1" space="http://www.onvif.org/onvif/ptz/space/position"/>
                <tt:Zoom x="1"/>
              </tptz:Speed>
            </tptz:RelativeMove>
          </soap:Body>
        </soap:Envelope>
        '''
        return self._request(service_url, body, "http://www.onvif.org/ver20/ptz/wsdl/RelativeMove")

    def stop(self):
        service_url = self.ptz_url or self.discover_ptz_service()
        token = self.get_profile_token()
        body = f'''
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
                       xmlns:tt="http://www.onvif.org/ver10/schema"
                       xmlns:tptz="http://www.onvif.org/ver20/ptz/wsdl">
          <soap:Body>
            <tptz:Stop>
              <tptz:ProfileToken>{token}</tptz:ProfileToken>
              <tptz:PanTilt>true</tptz:PanTilt>
              <tptz:Zoom>true</tptz:Zoom>
            </tptz:Stop>
          </soap:Body>
        </soap:Envelope>
        '''
        return self._request(service_url, body, "http://www.onvif.org/ver20/ptz/wsdl/Stop")

    def center(self):
        service_url = self.ptz_url or self.discover_ptz_service()
        token = self.get_profile_token()
        body = f'''
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
                       xmlns:tt="http://www.onvif.org/ver10/schema"
                       xmlns:tptz="http://www.onvif.org/ver20/ptz/wsdl">
          <soap:Body>
            <tptz:AbsoluteMove>
              <tptz:ProfileToken>{token}</tptz:ProfileToken>
              <tptz:Position>
                <tt:PanTilt x="0.5" y="0.5" space="http://www.onvif.org/onvif/ptz/space/position"/>
                <tt:Zoom x="0.5"/>
              </tptz:Position>
            </tptz:AbsoluteMove>
          </soap:Body>
        </soap:Envelope>
        '''
        return self._request(service_url, body, "http://www.onvif.org/ver20/ptz/wsdl/AbsoluteMove")

    def zoom(self, delta):
        self.move_relative(zoom=delta)


__all__ = ["ONVIFPTZManager"]
