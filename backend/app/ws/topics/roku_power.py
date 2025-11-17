# app/ws/topics/roku_power.py
from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
from typing import Any

from ..hub import register_topic, broadcast
from ...services.roku.client import get_power_mode

TOPIC_NAME = "roku_power"

_power_state: str | None = None
_poller_started = False
_poller_lock = threading.Lock()


def _power_poller_loop(poll_interval: float = 2.0) -> None:
    global _power_state

    while True:
        try:
            mode = get_power_mode()
        except Exception:
            mode = "offline"

        if mode != _power_state:
            _power_state = mode
            broadcast(
                TOPIC_NAME,
                {
                    "type": "power_state",
                    "powerMode": mode,
                    "ts": datetime.now(timezone.utc).isoformat(),
                },
            )

        time.sleep(poll_interval)


def _start_poller() -> None:
    global _poller_started
    with _poller_lock:
        if _poller_started:
            return
        _poller_started = True

        t = threading.Thread(target=_power_poller_loop, daemon=True)
        t.start()


def _on_subscribe(ws: Any) -> None:
    """
    When a client subscribes to roku_power, if we already know the latest
    state, send it immediately to that socket.
    """
    if _power_state is None:
        return

    payload = {
        "type": "power_state",
        "powerMode": _power_state,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    try:
        ws.send(json.dumps(payload))
    except Exception as exc:
        print("[roku_power] initial send error:", exc)


# Register the topic with the hub at import time
register_topic(
    name=TOPIC_NAME,
    on_first_subscribe=_start_poller,
    on_subscribe=_on_subscribe,
    # on_unsubscribe can be added if you want shutdown logic later
)