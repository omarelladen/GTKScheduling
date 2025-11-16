#!/bin/sh

# Include config variables
. "$PWD"/config


expand_home()
{
	_PATH="$1"

	case "$_PATH" in
		"~"|"~"/*)
			_PATH="/home/${SUDO_USER:-$USER}${_PATH#\~}" ;;
	esac

	echo "$_PATH"
}

TASKS_DIR=$(expand_home "$TASKS_DIR")
TASKS_FILE=$(expand_home "$TASKS_FILE")


mkdir -pv "$BIN_DIR" "$DATA_DIR" "$ICONS_DIR" "$PYTHON_PKG_DIR" "$DESKTOP_DIR" "$TASKS_DIR"

cp -v "$ORIG_SRC_DIR"/* "$PYTHON_PKG_DIR"
cp -v "$ORIG_ICONS_DIR"/* "$ICONS_DIR"
cp -v config "$DATA_DIR"
cp -v "$ORIG_TASKS_FILE" "$TASKS_FILE"

chown -R "$SUDO_USER":"$SUDO_USER" "$TASKS_DIR"

echo "# This directory is a Python package." > "$PYTHON_PKG_DIR"/__init__.py


echo "[Desktop Entry]
Name=$APP_NAME
Comment=$APP_DESCRIPTION
Exec=$BIN_FILE
Type=Application
Categories=Education
Icon=$APP_ICON_FILE" > "$DESKTOP_FILE"


echo "#!/usr/bin/python3

import sys
sys.path.insert(0, \"$DATA_DIR\")

from $APP_NAME_LOWER.main import main

if __name__ == \"__main__\":
    main()
" > "$BIN_FILE"

chmod -v +x "$BIN_FILE"
