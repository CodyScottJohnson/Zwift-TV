# app/services/roku_client.py
from __future__ import annotations

import os
import requests
import xml.etree.ElementTree as ET
from typing import Optional


class RokuClientError(Exception):
    pass


def _get_roku_ip() -> str:
    ip = os.getenv("ROKU_IP")
    if not ip:
        raise RokuClientError("ROKU_IP environment variable not set")
    return ip


def _base_url() -> str:
    return f"http://{_get_roku_ip()}:8060"


def _get(path: str, timeout: float = 2.0) -> requests.Response:
    url = _base_url() + path
    return requests.get(url, timeout=timeout)


def _post(path: str, timeout: float = 2.0) -> requests.Response:
    url = _base_url() + path
    return requests.post(url, timeout=timeout)


def send_keypress(key: str) -> None:
    """
    Send a simple keypress like 'Home', 'PowerOn', 'VolumeUp', etc.
    Raises RokuClientError on failure (non-2xx).
    """
    resp = _post(f"/keypress/{key}")
    if not resp.ok:
        raise RokuClientError(f"Keypress {key} failed: {resp.status_code} {resp.text}")


# ---- power controls ----

def power_on() -> None:
    send_keypress("PowerOn")


def power_off() -> None:
    send_keypress("PowerOff")


def power_toggle() -> None:
    send_keypress("Power")


# ---- volume controls ----

def volume_up(steps: int = 1) -> None:
    for _ in range(max(0, steps)):
        send_keypress("VolumeUp")


def volume_down(steps: int = 1) -> None:
    for _ in range(max(0, steps)):
        send_keypress("VolumeDown")


def volume_mute() -> None:
    send_keypress("VolumeMute")


# ---- state queries ----

def get_power_mode() -> str:
    """
    Returns one of:
      - 'PowerOn'
      - 'DisplayOff'
      - 'PowerStandby'
      - 'offline'  (if unreachable / HTTP error)
      - 'unknown'  (if XML missing field)
    """
    try:
        resp = _get("/query/device-info")
    except requests.RequestException:
        return "offline"

    if not resp.ok:
        return "offline"

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError:
        return "unknown"

    val: Optional[str] = root.findtext("power-mode")
    return val or "unknown"