#!/usr/bin/env bash
# ============================================================
# create_app.sh — Creates a double-clickable GroceryApp.app
#                 on macOS using AppleScript + osacompile.
#
# Run this ONCE from the root of the GroceryApp folder:
#   chmod +x create_app_macos.sh
#   ./create_app_macos.sh
#
# It will create GroceryApp.app in the same folder.
# You can then drag it to the Dock or Applications if you like.
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="GroceryApp"
APP_PATH="$SCRIPT_DIR/$APP_NAME.app"
RUN_SCRIPT="$SCRIPT_DIR/run_macos.sh"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[create_app_macos]${NC} $*"; }
warn()  { echo -e "${YELLOW}[warn]      ${NC} $*"; }
error() { echo -e "${RED}[error]     ${NC} $*"; exit 1; }

# -- Sanity checks ----------------------------------------------
if [ ! -f "$RUN_SCRIPT" ]; then
    error "run_macos.sh not found at $SCRIPT_DIR. Make sure create_app_macos.sh is in the GroceryApp root folder."
fi

if ! command -v osacompile &>/dev/null; then
    error "osacompile not found — this script requires macOS."
fi

# -- Remove old app if it exists --------------------------------
if [ -d "$APP_PATH" ]; then
    warn "Removing existing $APP_NAME.app …"
    rm -rf "$APP_PATH"
fi

# ============================================================
# Build the AppleScript that will run run_macos.sh in a Terminal window
# ============================================================
#
# Why Terminal?  run_macos.sh prints status messages and error output.
# Opening a Terminal window means your wife can see what's
# happening (and any errors) rather than them disappearing silently.
#
APPLESCRIPT=$(cat << ASEOF
tell application "Terminal"
    activate
    do script "cd '$SCRIPT_DIR' && bash run_macos.sh; exit"
end tell
ASEOF
)

info "Compiling $APP_NAME.app …"
echo "$APPLESCRIPT" | osacompile -o "$APP_PATH"

# ============================================================
# Optionally replace the default Automator icon with something
# friendlier — we use the built-in Grocery/Food emoji rendered
# via Python into an ICNS-compatible PNG, then sips converts it.
# Falls back silently if anything goes wrong.
# ============================================================
set_icon() {
    local icon_src
    icon_src="$SCRIPT_DIR/.groceryapp_icon.png"

    # Use Python to draw a simple emoji icon (no ImageMagick needed)
    python3 - << PYEOF 2>/dev/null || return
try:
    import tkinter as tk
    import math

    root = tk.Tk()
    root.withdraw()

    size = 512
    c = tk.Canvas(root, width=size, height=size, bg="#4CAF50", highlightthickness=0)
    c.pack()

    # Green rounded background + shopping cart emoji text
    c.create_oval(20, 20, size-20, size-20, fill="#4CAF50", outline="")
    c.create_text(size//2, size//2, text="🛒", font=("Apple Color Emoji", 260))

    c.update()
    c.postscript(file="$icon_src.eps", colormode="color")
    root.destroy()
except Exception:
    pass
PYEOF

    # Convert EPS → PNG → ICNS using only built-in macOS tools
    if [ -f "${icon_src}.eps" ]; then
        local iconset="$SCRIPT_DIR/.groceryapp.iconset"
        mkdir -p "$iconset"
        sips -s format png "${icon_src}.eps" --out "$icon_src" &>/dev/null || return
        for size in 16 32 64 128 256 512; do
            sips -z $size $size "$icon_src" --out "$iconset/icon_${size}x${size}.png" &>/dev/null || true
        done
        iconutil -c icns "$iconset" -o "$SCRIPT_DIR/.groceryapp.icns" &>/dev/null || return

        # Inject icon into the .app bundle
        cp "$SCRIPT_DIR/.groceryapp.icns" "$APP_PATH/Contents/Resources/droplet.icns" 2>/dev/null || true

        # Clean up temp files
        rm -rf "$iconset" "$icon_src" "${icon_src}.eps" "$SCRIPT_DIR/.groceryapp.icns"
    fi
}

info "Setting app icon …"
set_icon || warn "Could not set custom icon — the app will use the default script icon."

# -- Tell macOS to refresh the icon cache -----------------------
touch "$APP_PATH"

# ============================================================
# Done
# ============================================================
echo ""
info "✅  Created: $APP_PATH"
echo ""
echo "  Next steps:"
echo "  1. Double-click GroceryApp.app in Finder to launch."
echo "  2. If macOS blocks it the first time, go to:"
echo "       System Settings → Privacy & Security → 'Open Anyway'"
echo "  3. To add it to the Dock: drag GroceryApp.app onto the Dock."
echo "  4. To add it to Applications: drag it to /Applications in Finder."
echo ""
