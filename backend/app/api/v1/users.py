from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from flask import jsonify, request

from . import v1_bp


@dataclass
class User:
    id: int
    email: str


# Very fake in-memory "store"
_USERS: dict[int, User] = {
    1: User(id=1, email="alice@example.com"),
    2: User(id=2, email="bob@example.com"),
}


@v1_bp.get("/users")
def list_users():
    return jsonify([asdict(u) for u in _USERS.values()])


@v1_bp.get("/users/<int:user_id>")
def get_user(user_id: int):
    user = _USERS.get(user_id)
    if not user:
        return jsonify({"error": "not_found"}), 404
    return jsonify(asdict(user))


@v1_bp.post("/users")
def create_user():
    data: dict[str, Any] = request.get_json(silent=True) or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "email_required"}), 400

    new_id = max(_USERS.keys() or [0]) + 1
    user = User(id=new_id, email=email)
    _USERS[new_id] = user
    return jsonify(asdict(user)), 201
