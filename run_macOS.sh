#!/usr/bin/env bash
# ============================================================
# run_macos.sh — GroceryApp setup & launcher for macOS
#
# First run:  creates a venv, installs dependencies, then starts the app.
# Later runs: skips setup if the venv already exists, just runs.
#
# Usage:
#   chmod +x run_macOS.sh      (only needed once)
#   ./run_macOS.sh
# ============================================================

set -euo pipefail

# -- Resolve the directory this script lives in -----------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_MIN_MAJOR=3
PYTHON_MIN_MINOR=10

# -- Colours ----------------------------------------------------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${GREEN}[setup]${NC} $*"; }
warn()    { echo -e "${YELLOW}[warn] ${NC} $*"; }
error()   { echo -e "${RED}[error]${NC} $*"; exit 1; }

# ============================================================
# 1. Find a suitable Python 3
# ============================================================
find_python() {
    for cmd in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null)
            local maj
            maj=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
            if [ "$maj" -ge "$PYTHON_MIN_MAJOR" ] && [ "$ver" -ge "$PYTHON_MIN_MINOR" ]; then
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
Install it from https://www.python.org/downloads/ or via Homebrew:\n\
  brew install python@3.13"
fi

info "Using Python: $PYTHON ($($PYTHON --version))"

# ============================================================
# 2. Check tkinter is available (macOS python.org builds include it;
#    Homebrew sometimes needs a separate package)
# ============================================================
if ! "$PYTHON" -c "import tkinter" &>/dev/null; then
    error "tkinter is not available in $($PYTHON --version).\n\
If you installed Python via Homebrew, run:\n\
  brew install python-tk\n\
Or download the official installer from https://www.python.org/downloads/ \n\
which bundles tkinter automatically."
fi

# ============================================================
# 3. Create virtualenv (only on first run)
# ============================================================
if [ ! -d "$VENV_DIR" ]; then
    info "Creating virtual environment at $VENV_DIR …"
    "$PYTHON" -m venv "$VENV_DIR"
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

info "Installing dependencies from requirements.txt …"
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
info "Starting GroceryApp …"
echo ""
cd "$SCRIPT_DIR/src"
exec "$VENV_PYTHON" main.py
