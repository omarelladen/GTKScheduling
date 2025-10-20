#!/bin/sh

./scripts/uninstall.sh


APP_NAME="gtkscheduling"
PREFIX=/usr/local
BIN_DIR=$PREFIX/bin
BIN_FILE=$BIN_DIR/$APP_NAME
DATA_DIR=$PREFIX/share/$APP_NAME
ICONS_DIR=$DATA_DIR/icons
TASKS_DIR=$DATA_DIR/tasks
DESKTOP_DIR=/usr/local/share/applications
PYTHON_SITE=$(python3 -c "import site; print(site.getsitepackages()[0])")
PYTHON_PKG_DIR=$PYTHON_SITE/$APP_NAME


mkdir -pv "$BIN_DIR" "$ICONS_DIR" "$TASKS_DIR" "$DESKTOP_DIR" "$PYTHON_PKG_DIR"

cp -v src/*.py "$PYTHON_PKG_DIR"
cp -v data/icons/* "$ICONS_DIR/"
cp -v data/tasks/* "$TASKS_DIR"
cp -v data/$APP_NAME.desktop "$DESKTOP_DIR/"
cp -v config "$DATA_DIR/"


touch $BIN_FILE

cat << 'EOF' > "$BIN_FILE"
#!/usr/bin/env python3
from gtkscheduling.main import main

if __name__ == "__main__":
    main()
EOF

chmod -v +x "$BIN_FILE"
