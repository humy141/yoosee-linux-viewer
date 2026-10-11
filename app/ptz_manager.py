import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET


class ONVIFPTZManager:
    """Basic ONVIF PTZ controller for cameras exposing the PTZ service."""

    DEVICE_SERVICE_CANDIDATES = [
        "/onvif/device_service",
        "/onvif/DeviceService",
        "/onvif/device_service?wsdl",
        "/onvif/device",
    ]

    MEDIA_SERVICE_CANDIDATES = [
        "/onvif/media_service",
        "/onvif/MediaService",
        "/onvif/media",
    ]

    PTZ_SERVICE_CANDIDATES = [
        "/onvif/ptz_service",
        "/onvif/PTZService",
        "/onvif/ptz",
    ]

    def __init__(self, camera_ip, username="admin", password="admin", port=80):
        self.camera_ip = camera_ip
        self.username = username
        self.password = password
        self.port = int(port or 80)
        self.base_url = f"http://{camera_ip}:{self.port}"
        self.device_url = None
        self.ptz_url = None
        self.profile_token = None

    def _get(self, url, timeout=8):
        try:
            return requests.get(
                url,
                auth=HTTPBasicAuth(self.username, self.password),
                timeout=timeout,
                verify=False,
            )
        except Exception:
            return None

    def _post_soap(self, url, body, action):
        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "SOAPAction": action,
        }
        resp = requests.post(
            url,
            data=body,
            headers=headers,
            auth=HTTPBasicAuth(self.username, self.password),
            timeout=8,
            verify=False,
        )
        return resp

    def _find_service_by_candidates(self, candidates):
        for cand in candidates:
            url = f"{self.base_url}{cand}"
            r = self._get(url)
            if r and r.status_code in (200, 401, 403, 405):
                return url
        return None

    def discover_device_service(self):
        self.device_url = self._find_service_by_candidates(self.DEVICE_SERVICE_CANDIDATES)
        return self.device_url

    def discover_ptz_service(self):
        if self.ptz_url:
            return self.ptz_url

        candidates = [
            *self.PTZ_SERVICE_CANDIDATES,
            *[f"{self.base_url}/onvif/{x}" for x in ["ptz_service", "PTZService", "ptz"]],
        ]
        for cand in candidates:
            url = cand if cand.startswith("http") else f"{self.base_url}{cand}"
            r = self._get(url)
            if r and r.status_code in (200, 401, 403, 405):
                self.ptz_url = url
                return url

        # fallback: try device service GetCapabilities
        self.device_url = self.device_url or self.discover_device_service()
        if self.device_url:
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
            resp = self._post_soap(self.device_url, body, "http://www.onvif.org/ver10/device/wsdl/GetCapabilities")
            if resp.status_code in (200, 401, 403, 405):
                text = resp.text
                if "PTZ" in text or "xaddr" in text.lower():
                    # best effort: parse XAddr if present
                    try:
                        root = ET.fromstring(text)
                        for elem in root.iter():
                            if "PTZ" in elem.tag or "XAddr" in elem.tag:
                                if elem.text and "http" in elem.text:
                                    self.ptz_url = elem.text
                                    return elem.text
                    except Exception:
                        pass

        return self.ptz_url

    def discover_profile_token(self):
        if self.profile_token:
            return self.profile_token

        for media_path in self.MEDIA_SERVICE_CANDIDATES:
            url = f"{self.base_url}{media_path}"
            body = '''
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
                           xmlns:trt="http://www.onvif.org/ver10/media/wsdl">
              <soap:Body>
                <trt:GetProfiles/>
              </soap:Body>
            </soap:Envelope>
            '''
            resp = self._post_soap(url, body, "http://www.onvif.org/ver10/media/wsdl/GetProfiles")
            if resp.status_code in (200, 401, 403, 405):
                text = resp.text
                # Try to parse ProfileToken from XML
                try:
                    root = ET.fromstring(text)
                    for elem in root.iter():
                        if elem.tag.endswith("ProfileToken") and elem.text:
                            self.profile_token = elem.text
                            return self.profile_token
                except Exception:
                    pass
                if "ProfileToken" in text:
                    try:
                        value = text.split("ProfileToken>")[-1].split("</")[0]
                        if value:
                            self.profile_token = value
                            return value
                    except Exception:
                        pass

        self.profile_token = "main_profile"
        return self.profile_token

    def move_relative(self, pan=0.0, tilt=0.0, zoom=0.0):
        service_url = self.discover_ptz_service()
        if not service_url:
            raise RuntimeError("Không tìm thấy service PTZ qua ONVIF.")
        token = self.discover_profile_token()
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
                <tt:PanTilt x="1.0" y="1.0" space="http://www.onvif.org/onvif/ptz/space/position"/>
                <tt:Zoom x="1.0"/>
              </tptz:Speed>
            </tptz:RelativeMove>
          </soap:Body>
        </soap:Envelope>
        '''
        resp = self._post_soap(service_url, body, "http://www.onvif.org/ver20/ptz/wsdl/RelativeMove")
        return resp

    def stop(self):
        service_url = self.discover_ptz_service()
        if not service_url:
            raise RuntimeError("Không tìm thấy service PTZ qua ONVIF.")
        token = self.discover_profile_token()
        body = f'''
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
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
        return self._post_soap(service_url, body, "http://www.onvif.org/ver20/ptz/wsdl/Stop")

    def center(self):
        service_url = self.discover_ptz_service()
        if not service_url:
            raise RuntimeError("Không tìm thấy service PTZ qua ONVIF.")
        token = self.discover_profile_token()
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
        return self._post_soap(service_url, body, "http://www.onvif.org/ver20/ptz/wsdl/AbsoluteMove")

    def zoom(self, delta):
        self.move_relative(zoom=delta)


__all__ = ["ONVIFPTZManager"]
