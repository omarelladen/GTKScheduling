#!/bin/sh

# Include config variables
. "$PWD"/config

PYTHON_SITE=$(python3 -c "import site; print(site.getsitepackages()[0])")
PYTHON_PKG_DIR="$PYTHON_SITE/$APP_NAME_LOWER"


rm -rfv "$DATA_DIR" "$DESKTOP_FILE" "$PYTHON_PKG_DIR" "$BIN_FILE"
