<img height="64" src="data/icons/icon.png" align="left"/>

# GTKScheduling (in development)

GTKScheduling is GTK 3 based app to simulate CPU scheduling.

<p align="center" width="100%">
<img src="data/imgs/diagram.png">
<img src="data/imgs/info.png">
</p>

## Requirements
This GTK 3 based app uses [PyGObject](https://pygobject.gnome.org/), which is a Python package that provides bindings for GObject based libraries such as GTK, GStreamer, WebKitGTK, GLib, GIO and many more.

The dependencies usually come pre-installed on popular Linux distributions, however some do not come with the package 'python3-gi-cairo' installed by default.

To install it on Debian-based distributions:
```sh
sudo apt install python3-gi-cairo
```

If you wish to configure on other operating systems, including Windows, follow the instructions on the [PyGObject website](https://pygobject.gnome.org/getting_started.html), making sure to replace 'GTK4' with 'GTK3' when instaling packages.

## Configure scheduling parameters
The scheduling parameters can be changed by editing the data/tasks/tasks file.

## Install app
```sh
cd GTKScheduling
sudo scripts/install.sh
```
After the installation you can open the app with the apps menu of your desktop environment or run:
```sh
gtkscheduling
```

## Uninstall app
```sh
cd GTKScheduling
sudo scripts/uninstall.sh
```
