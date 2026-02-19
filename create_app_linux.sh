#!/usr/bin/env bash
# ============================================================
# create_app_linux.sh — Creates a double-clickable desktop
#                       shortcut for GroceryApp on Linux.
#
# Creates a .desktop file on the user's Desktop and registers
# it with the system so it appears in app menus too.
#
# Run this ONCE from the root of the GroceryApp folder:
#   chmod +x create_app_linux.sh
#   ./create_app_linux.sh
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_SCRIPT="$SCRIPT_DIR/run_linux.sh"
APP_NAME="GroceryApp"
DESKTOP_FILE="$HOME/Desktop/$APP_NAME.desktop"
APPS_DIR="$HOME/.local/share/applications"
APPS_FILE="$APPS_DIR/$APP_NAME.desktop"
ICON_DIR="$HOME/.local/share/icons"
ICON_FILE="$ICON_DIR/groceryapp.png"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[create_app]${NC} $*"; }
warn()  { echo -e "${YELLOW}[warn]      ${NC} $*"; }
error() { echo -e "${RED}[error]     ${NC} $*"; exit 1; }

# ============================================================
# Sanity checks
# ============================================================
if [ ! -f "$RUN_SCRIPT" ]; then
    error "run_linux.sh not found at $SCRIPT_DIR.\nMake sure create_app_linux.sh is in the GroceryApp root folder."
fi

# Make sure run_linux.sh is executable
chmod +x "$RUN_SCRIPT"

# ============================================================
# Create a simple icon using Python + tkinter
# (no ImageMagick or extra tools needed)
# ============================================================
mkdir -p "$ICON_DIR"

info "Generating app icon ..."
python3 - << PYEOF 2>/dev/null || warn "Could not generate icon — a default icon will be used."
import tkinter as tk
import os

try:
    root = tk.Tk()
    root.withdraw()

    size = 256
    canvas = tk.Canvas(root, width=size, height=size, bg="#4CAF50", highlightthickness=0)
    canvas.pack()
    canvas.create_oval(8, 8, size-8, size-8, fill="#388E3C", outline="")
    canvas.create_text(size//2, size//2, text="🛒", font=("DejaVu Sans", 120))
    canvas.update()

    # Save as EPS then convert with PIL if available
    eps_path = "/tmp/groceryapp_icon.eps"
    canvas.postscript(file=eps_path, colormode="color", width=size, height=size)
    root.destroy()

    try:
        from PIL import Image
        img = Image.open(eps_path)
        img = img.resize((256, 256))
        img.save("$ICON_FILE", "PNG")
        os.remove(eps_path)
    except ImportError:
        os.remove(eps_path)
except Exception as e:
    print(f"Icon generation skipped: {e}")
PYEOF

# Fall back to a standard system icon if we couldn't make one
if [ ! -f "$ICON_FILE" ]; then
    # Try to find a reasonable built-in icon
    for candidate in \
        /usr/share/icons/hicolor/256x256/apps/system-file-manager.png \
        /usr/share/pixmaps/python3.png \
        /usr/share/icons/hicolor/48x48/apps/utilities-terminal.png; do
        if [ -f "$candidate" ]; then
            cp "$candidate" "$ICON_FILE"
            break
        fi
    done
fi

ICON_PATH="${ICON_FILE:-utilities-terminal}"

# ============================================================
# Write the .desktop file
# ============================================================
DESKTOP_CONTENT="[Desktop Entry]
Version=1.0
Type=Application
Name=GroceryApp
Comment=Weekly meal planner and grocery list generator
Exec=bash -c 'cd \"$SCRIPT_DIR\" && bash run_linux.sh'
Icon=$ICON_PATH
Terminal=true
Categories=Utility;
StartupNotify=true"

# Desktop shortcut
mkdir -p "$HOME/Desktop"
echo "$DESKTOP_CONTENT" > "$DESKTOP_FILE"
chmod +x "$DESKTOP_FILE"

# App menu entry
mkdir -p "$APPS_DIR"
echo "$DESKTOP_CONTENT" > "$APPS_FILE"
chmod +x "$APPS_FILE"

# Tell the desktop environment to refresh
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi
if command -v xdg-desktop-menu &>/dev/null; then
    xdg-desktop-menu forceupdate 2>/dev/null || true
fi

# ============================================================
# On GNOME, .desktop files on the Desktop need to be marked
# trusted before they can be double-clicked
# ============================================================
if command -v gio &>/dev/null; then
    gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true
fi

# ============================================================
# Done
# ============================================================
echo ""
info "Done! Created:"
echo "   Desktop shortcut : $DESKTOP_FILE"
echo "   App menu entry   : $APPS_FILE"
echo ""
echo "  Next steps:"
echo "  1. Double-click GroceryApp on your Desktop to launch."
echo "  2. If it asks 'Trust and launch?' — click Trust."
echo "  3. The app will also appear in your applications menu."
echo ""
