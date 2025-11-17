#!/bin/bash
set -e

REPO_DIR="$HOME/gym-controller"
NOVNC_DIR="$REPO_DIR/tools/noVNC"

cd "$NOVNC_DIR"
./utils/novnc_proxy --vnc localhost:5900 --listen 6080