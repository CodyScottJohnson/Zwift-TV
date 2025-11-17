# app/ws/app_socket.py
from __future__ import annotations

import json
from datetime import datetime, timezone

from flask_sock import Sock

from .hub import add_connection, remove_connection, handle_client_message

# Import topics so they register themselves with the hub
from .topics import roku_power  # noqa: F401  (just to trigger registration)


def register_app_ws(sock: Sock) -> None:
    @sock.route("/ws/app")
    def app_ws(ws):
        """
        Single WebSocket endpoint for the app.

        Client protocol (JSON):
          - { "type": "subscribe", "topic": "roku_power" }
          - { "type": "unsubscribe", "topic": "roku_power" }
          - { "type": "echo", "data": ... }  (optional debug)
        """
        add_connection(ws)

        # Optional welcome message
        ws.send(
            json.dumps(
                {
                    "type": "welcome",
                    "message": "connected",
                    "ts": datetime.now(timezone.utc).isoformat(),
                }
            )
        )

        try:
            while True:
                raw = ws.receive()
                if raw is None:
                    break
                handle_client_message(ws, raw)
        finally:
            remove_connection(ws)