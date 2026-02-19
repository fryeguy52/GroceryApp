#!/usr/bin/env bash
# ============================================================
# run_tests_linux.sh — Run the GroceryApp test suite on Linux
#
# Uses the same .venv as run_linux.sh. If the venv doesn't
# exist yet, run run_linux.sh first to set it up.
#
# Usage:
#   chmod +x run_tests_linux.sh                          (once)
#   ./run_tests_linux.sh                                 (all tests)
#   ./run_tests_linux.sh -v                              (verbose)
#   ./run_tests_linux.sh TestIngredient                  (one class)
#   ./run_tests_linux.sh TestIngredient.test_valid_input (one test)
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
TEST_DIR="$SCRIPT_DIR/test"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'
info()  { echo -e "${GREEN}[tests]${NC} $*"; }
warn()  { echo -e "${YELLOW}[warn] ${NC} $*"; }
error() { echo -e "${RED}[error]${NC} $*"; exit 1; }

# ============================================================
# 1. Make sure the venv exists
# ============================================================
if [ ! -f "$VENV_PYTHON" ]; then
    error "Virtual environment not found at $SCRIPT_DIR/.venv\nRun ./run_linux.sh first to create it and install dependencies."
fi

# ============================================================
# 2. Parse optional arguments
# ============================================================
FILTER=""

for arg in "$@"; do
    case "$arg" in
        -v|--verbose) true ;;  # verbose is always on below
        -*)           warn "Unknown flag '$arg' — ignoring." ;;
        *)            FILTER="$arg" ;;
    esac
done

# ============================================================
# 3. Run the tests
# ============================================================
echo ""
echo -e "${BOLD}GroceryApp Test Suite${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$TEST_DIR"

if [ -n "$FILTER" ]; then
    info "Running: $FILTER"
    echo ""
    "$VENV_PYTHON" -m unittest "$FILTER" -v
else
    info "Running all tests"
    echo ""
    "$VENV_PYTHON" -m unittest discover \
        --start-directory "$TEST_DIR" \
        --pattern "test_*.py" \
        --verbose
fi

EXIT_CODE=$?
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}${BOLD}All tests passed.${NC}"
else
    echo -e "${RED}${BOLD}Some tests failed — see above for details.${NC}"
fi
echo ""
exit $EXIT_CODE
