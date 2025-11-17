# app/ws/hub.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Set, Any

# Type aliases
WsType = Any  # flask_sock's ws object
JsonDict = Dict[str, Any]

OnFirstSubscribe = Callable[[], None]
OnSubscribe = Callable[[WsType], None]
OnUnsubscribe = Callable[[WsType], None]


@dataclass
class Topic:
    name: str
    on_first_subscribe: Optional[OnFirstSubscribe] = None
    on_subscribe: Optional[OnSubscribe] = None
    on_unsubscribe: Optional[OnUnsubscribe] = None
    started: bool = False  # internal flag


# Global state
_connections_lock = __import__("threading").Lock()
_connections: Set[WsType] = set()
_subscriptions: Dict[WsType, Set[str]] = {}
_topics: Dict[str, Topic] = {}
_topic_subscriber_counts: Dict[str, int] = {}


def register_topic(
    name: str,
    on_first_subscribe: Optional[OnFirstSubscribe] = None,
    on_subscribe: Optional[OnSubscribe] = None,
    on_unsubscribe: Optional[OnUnsubscribe] = None,
) -> None:
    """
    Register a topic once at import time.

    New topics can be added by calling this in e.g. app/ws/topics/foo.py
    """
    if name in _topics:
        # allow re-registration with same name if needed, but typically not
        return

    _topics[name] = Topic(
        name=name,
        on_first_subscribe=on_first_subscribe,
        on_subscribe=on_subscribe,
        on_unsubscribe=on_unsubscribe,
    )
    _topic_subscriber_counts[name] = 0


def add_connection(ws: WsType) -> None:
    with _connections_lock:
        _connections.add(ws)
        _subscriptions[ws] = set()


def remove_connection(ws: WsType) -> None:
    with _connections_lock:
        topics = _subscriptions.pop(ws, set())
        _connections.discard(ws)

    # Adjust topic subscriber counts and call on_unsubscribe
    for topic_name in topics:
        topic = _topics.get(topic_name)
        if not topic:
            continue
        _topic_subscriber_counts[topic_name] = max(
            0, _topic_subscriber_counts.get(topic_name, 0) - 1
        )
        if topic.on_unsubscribe:
            try:
                topic.on_unsubscribe(ws)
            except Exception as exc:
                print(f"[ws hub] on_unsubscribe error for {topic_name}: {exc}")


def subscribe(ws: WsType, topic_name: str) -> None:
    topic = _topics.get(topic_name)
    if not topic:
        # Auto-register unknown topics if you want, or ignore
        print(f"[ws hub] subscribe to unknown topic: {topic_name}")
        with _connections_lock:
            _subscriptions.setdefault(ws, set()).add(topic_name)
        return

    first_for_topic = False
    with _connections_lock:
        _subscriptions.setdefault(ws, set()).add(topic_name)
        prev_count = _topic_subscriber_counts.get(topic_name, 0)
        _topic_subscriber_counts[topic_name] = prev_count + 1
        if prev_count == 0:
            first_for_topic = True

    if first_for_topic and topic.on_first_subscribe and not topic.started:
        topic.started = True
        try:
            topic.on_first_subscribe()
        except Exception as exc:
            print(f"[ws hub] on_first_subscribe error for {topic_name}: {exc}")

    if topic.on_subscribe:
        try:
            topic.on_subscribe(ws)
        except Exception as exc:
            print(f"[ws hub] on_subscribe error for {topic_name}: {exc}")


def unsubscribe(ws: WsType, topic_name: str) -> None:
    topic = _topics.get(topic_name)

    with _connections_lock:
        topics = _subscriptions.get(ws)
        if not topics or topic_name not in topics:
            return
        topics.discard(topic_name)
        if topic:
            _topic_subscriber_counts[topic_name] = max(
                0, _topic_subscriber_counts.get(topic_name, 0) - 1
            )

    if topic and topic.on_unsubscribe:
        try:
            topic.on_unsubscribe(ws)
        except Exception as exc:
            print(f"[ws hub] on_unsubscribe error for {topic_name}: {exc}")


def broadcast(topic_name: str, payload: JsonDict) -> None:
    """
    Send payload to all connections subscribed to `topic_name`.
    """
    msg = json.dumps(payload)
    dead: list[WsType] = []

    with _connections_lock:
        for ws in list(_connections):
            topics = _subscriptions.get(ws, set())
            if topic_name not in topics:
                continue
            try:
                ws.send(msg)
            except Exception:
                dead.append(ws)

        for ws in dead:
            _connections.discard(ws)
            _subscriptions.pop(ws, None)


def handle_client_message(ws: WsType, raw: str) -> None:
    """
    Dispatch client JSON messages (subscribe/unsubscribe/echo).
    """
    try:
        msg = json.loads(raw)
    except Exception:
        print("[ws hub] invalid JSON from client")
        return

    mtype = msg.get("type")

    if mtype == "subscribe":
        topic = msg.get("topic")
        if not topic:
            return
        subscribe(ws, topic)

    elif mtype == "unsubscribe":
        topic = msg.get("topic")
        if not topic:
            return
        unsubscribe(ws, topic)

    elif mtype == "echo":
        # optional debug behavior
        payload = {
            "type": "echo",
            "data": msg.get("data"),
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        try:
            ws.send(json.dumps(payload))
        except Exception as exc:
            print("[ws hub] echo send error", exc)

    # You can add more generic message types here later if needed.