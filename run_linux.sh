#!/usr/bin/env bash
# ============================================================
# run_linux.sh — GroceryApp setup & launcher for Linux
#
# First run:  installs python3-tk if needed, creates a venv,
#             installs dependencies, then starts the app.
# Later runs: skips setup, just launches.
#
# Usage:
#   chmod +x run_linux.sh      (only needed once)
#   ./run_linux.sh
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_MIN_MAJOR=3
PYTHON_MIN_MINOR=10

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[setup]${NC} $*"; }
warn()  { echo -e "${YELLOW}[warn] ${NC} $*"; }
error() { echo -e "${RED}[error]${NC} $*"; exit 1; }

# ============================================================
# 1. Find a suitable Python 3
# ============================================================
find_python() {
    for cmd in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$cmd" &>/dev/null; then
            local maj min
            maj=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
            min=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null)
            if [ "$maj" -ge "$PYTHON_MIN_MAJOR" ] && [ "$min" -ge "$PYTHON_MIN_MINOR" ]; then
                echo "$cmd"
                return
            fi
        fi
    done
    echo ""
}

PYTHON=$(find_python)

if [ -z "$PYTHON" ]; then
    error "Python $PYTHON_MIN_MAJOR.$PYTHON_MIN_MINOR+ not found.\n\
Install it with your package manager, e.g.:\n\
  sudo apt install python3"
fi

info "Using Python: $PYTHON ($($PYTHON --version))"

# ============================================================
# 2. Check for tkinter — offer to install it if missing
# ============================================================
if ! "$PYTHON" -c "import tkinter" &>/dev/null; then
    warn "tkinter is not installed."

    # Detect package manager and offer to install
    if command -v apt &>/dev/null; then
        echo ""
        read -rp "  Install python3-tk now? This requires sudo. [Y/n]: " answer
        answer="${answer:-Y}"
        if [[ "$answer" =~ ^[Yy] ]]; then
            sudo apt install -y python3-tk
        else
            error "tkinter is required. Install it with: sudo apt install python3-tk"
        fi
    elif command -v dnf &>/dev/null; then
        error "tkinter not found. Install it with: sudo dnf install python3-tkinter"
    elif command -v pacman &>/dev/null; then
        error "tkinter not found. Install it with: sudo pacman -S tk"
    else
        error "tkinter not found. Install the python3-tk package for your distribution."
    fi

    # Verify it worked
    if ! "$PYTHON" -c "import tkinter" &>/dev/null; then
        error "tkinter still not available after install attempt. Please install it manually."
    fi
    info "tkinter installed successfully."
fi

# ============================================================
# 3. Create virtualenv (only on first run)
# ============================================================
if [ ! -d "$VENV_DIR" ]; then
    info "Creating virtual environment at $VENV_DIR ..."

    # python3-venv is sometimes a separate package on Debian/Ubuntu
    if ! "$PYTHON" -m venv "$VENV_DIR" &>/dev/null; then
        warn "venv creation failed. Trying to install python3-venv ..."
        if command -v apt &>/dev/null; then
            sudo apt install -y python3-venv
            "$PYTHON" -m venv "$VENV_DIR"
        else
            error "Could not create venv. Install python3-venv for your distribution."
        fi
    fi

    info "Virtual environment created."
else
    info "Virtual environment already exists — skipping creation."
fi

VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

# ============================================================
# 4. Install / upgrade dependencies
# ============================================================
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

if [ ! -f "$REQUIREMENTS" ]; then
    error "requirements.txt not found at $REQUIREMENTS"
fi

info "Installing dependencies from requirements.txt ..."
"$VENV_PIP" install --upgrade pip --quiet
"$VENV_PIP" install -r "$REQUIREMENTS" --quiet
info "Dependencies installed."

# ============================================================
# 5. Warn if todoist_settings.py is missing
# ============================================================
SETTINGS="$SCRIPT_DIR/src/todoist_settings.py"
EXAMPLE="$SCRIPT_DIR/src/todoist_settings.example.py"

if [ ! -f "$SETTINGS" ]; then
    warn "todoist_settings.py not found."
    if [ -f "$EXAMPLE" ]; then
        warn "Copy the example and fill in your API token:"
        warn "  cp src/todoist_settings.example.py src/todoist_settings.py"
    fi
    warn "The app will still run — Todoist posting will be skipped."
    echo ""
fi

# ============================================================
# 6. Launch the app
# ============================================================
info "Starting GroceryApp ..."
echo ""
cd "$SCRIPT_DIR/src"
exec "$VENV_PYTHON" main.py
