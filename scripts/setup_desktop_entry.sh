#!/bin/sh

mkdir -p "$HOME"/.local/share/applications

root_dir=$PWD


echo "[Desktop Entry]
Name=GTK Scheduling
Comment=CPU scheduling simulator
Exec=sh $root_dir/scripts/launcher.sh
Type=Application
Icon=$root_dir/imgs/icon.png" > "$HOME"/.local/share/applications/gtk-scheduling.desktop


echo "#!/bin/sh

cd "$root_dir" && /usr/bin/python3 src/main.py" > "$root_dir"/scripts/launcher.sh
