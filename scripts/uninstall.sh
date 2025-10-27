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

TASKS_DIR=$(expand_home "$TASKS_FILE")


rm -rfv "$BIN_FILE" "$PYTHON_PKG_DIR" "ICONS_DIR" "$DATA_DIR" "$DESKTOP_FILE" "$TASKS_DIR"
