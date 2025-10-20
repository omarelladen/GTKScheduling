#!/bin/sh

# Include config variables
. "$PWD"/config


./scripts/uninstall.sh

PYTHON_SITE=$(python3 -c "import site; print(site.getsitepackages()[0])")
PYTHON_PKG_DIR="$PYTHON_SITE/$APP_NAME_LOWER"


mkdir -pv "$BIN_DIR" "$DATA_DIR" "$ICONS_DIR" "$DESKTOP_DIR" "$PYTHON_PKG_DIR"

cp -v "$ORIG_SRC_DIR"/* "$PYTHON_PKG_DIR"
cp -v "$ORIG_ICONS_DIR"/* "$ICONS_DIR"
cp -v "$ORIG_TASKS_FILE" "$DATA_DIR"
cp -v config "$DATA_DIR"


echo "[Desktop Entry]
Name=$APP_NAME
Comment=$APP_DESCRIPTION
Exec=$BIN_FILE
Type=Application
Icon=$APP_ICON_FILE" > "$DESKTOP_FILE"


echo "#!/usr/bin/python3
from $APP_NAME_LOWER.main import main

if __name__ == '__main__':
    main()
" > "$BIN_FILE"

chmod -v +x "$BIN_FILE"
