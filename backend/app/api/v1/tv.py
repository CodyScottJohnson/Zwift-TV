# app/api/v1/roku.py
from __future__ import annotations

from flask import jsonify, request

from . import v1_bp
from ...services.roku.client import (
    power_on,
    power_off,
    power_toggle,
    volume_up,
    volume_down,
    volume_mute,
    get_power_mode,
    RokuClientError,
)


@v1_bp.get("/tv/power")
def tv_power():
    mode = get_power_mode()
    return jsonify(powerMode=mode)


@v1_bp.post("/tv/power/on")
def tv_power_on():
    try:
        power_on()
        return jsonify(ok=True), 200
    except RokuClientError as e:
        return jsonify(ok=False, error=str(e)), 502


@v1_bp.post("/tv/power/off")
def tv_power_off():
    try:
        power_off()
        return jsonify(ok=True), 200
    except RokuClientError as e:
        return jsonify(ok=False, error=str(e)), 502


@v1_bp.post("/tv/power/toggle")
def tv_power_toggle():
    try:
        power_toggle()
        return jsonify(ok=True), 200
    except RokuClientError as e:
        return jsonify(ok=False, error=str(e)), 502


@v1_bp.post("/tv/volume/up")
def tv_volume_up():
    steps = int(request.json.get("steps", 1)) if request.is_json else 1
    try:
        volume_up(steps)
        return jsonify(ok=True), 200
    except RokuClientError as e:
        return jsonify(ok=False, error=str(e)), 502


@v1_bp.post("/tv/volume/down")
def tv_volume_down():
    steps = int(request.json.get("steps", 1)) if request.is_json else 1
    try:
        volume_down(steps)
        return jsonify(ok=True), 200
    except RokuClientError as e:
        return jsonify(ok=False, error=str(e)), 502


@v1_bp.post("/tv/volume/mute")
def tv_volume_mute():
    try:
        volume_mute()
        return jsonify(ok=True), 200
    except RokuClientError as e:
        return jsonify(ok=False, error=str(e)), 502