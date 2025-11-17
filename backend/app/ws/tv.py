# app/ws/connections.py
from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
from typing import Set

from flask_sock import Sock

from ..roku_client import get_power_mode

# ---- shared state for power notifications ----

_power_connections_lock = threading.Lock()
_power_connections: Set[object] = set()
_power_state: str | None = None
_power_poller_started = False


def _broadcast_power_state(new_state: str) -> None:
    """
    Send the current power state to all connected /ws/roku-power clients.
    Drop any connections that error on send.
    """
    payload = {
        "type": "power_state",
        "powerMode": new_state,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    msg = json.dumps(payload)

    dead = []
    with _power_connections_lock:
        for ws in list(_power_connections):
            try:
                ws.send(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            _power_connections.discard(ws)


def _power_poller_loop(poll_interval: float = 2.0) -> None:
    """
    Background loop that long-polls the Roku's /query/device-info
    and pushes changes in power-mode to any websocket listeners.
    """
    global _power_state

    while True:
        try:
            mode = get_power_mode()
        except Exception:
            mode = "offline"

        if mode != _power_state:
            _power_state = mode
            _broadcast_power_state(mode)

        time.sleep(poll_interval)


def _ensure_power_poller_started() -> None:
    global _power_poller_started
    if _power_poller_started:
        return
    _power_poller_started = True

    t = threading.Thread(target=_power_poller_loop, daemon=True)
    t.start()


# ---- public registration hook used by create_app() ----

def register_ws_routes(sock: Sock) -> None:
    # existing echo + notifications routes
    @sock.route("/ws/echo")
    def echo(ws):
        """
        Basic echo socket for testing from Next.js.
        """
        while True:
            data = ws.receive()
            if data is None:
                break

            payload = {
                "type": "echo",
                "data": data,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            ws.send(json.dumps(payload))

    @sock.route("/ws/notifications")
    def notifications(ws):
        ws.send(json.dumps({"type": "welcome", "message": "connected"}))
        while True:
            data = ws.receive()
            if data is None:
                break
            # process or ignore `data`

    # NEW: Roku power-state WebSocket
    @sock.route("/ws/roku-power")
    def roku_power(ws):
        """
        Emits power state updates for the Roku TV.

        - On connect: sends the last known state (if any).
        - Whenever the background poller detects a change, all
          connected clients receive {"type": "power_state", "powerMode": "..."}.
        """
        _ensure_power_poller_started()

        # register connection
        with _power_connections_lock:
            _power_connections.add(ws)

        # send initial snapshot
        if _power_state is not None:
            ws.send(
                json.dumps(
                    {
                        "type": "power_state",
                        "powerMode": _power_state,
                        "ts": datetime.now(timezone.utc).isoformat(),
                    }
                )
            )

        # keep the connection open; we don't really care what client sends
        try:
            while True:
                data = ws.receive()
                if data is None:
                    break
        finally:
            with _power_connections_lock:
                _power_connections.discard(ws)