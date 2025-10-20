#!/bin/sh

APP_NAME="gtkscheduling"

PREFIX=/usr/local

BIN_DIR=$PREFIX/bin
BIN_FILE=$BIN_DIR/$APP_NAME

DATA_DIR=$PREFIX/share/$APP_NAME

DESKTOP_DIR=/usr/local/share/applications
DESKTOP_FILE=$DESKTOP_DIR/$APP_NAME.desktop

PYTHON_SITE=$(python3 -c "import site; print(site.getsitepackages()[0])")  # site-packages
PYTHON_PKG_DIR=$PYTHON_SITE/$APP_NAME


rm -rfv "$DATA_DIR" "$DESKTOP_FILE" "$PYTHON_PKG_DIR" "$BIN_FILE"
