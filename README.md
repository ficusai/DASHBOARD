# DASHBOARD

Minimal GTK4 dashboard application for Linux, written in Python.
Shows a small main window with a button that toggles a translucent,
always-on-top "TEST" overlay.

## Requirements

- Linux with a desktop environment (GNOME, KDE, etc.)
- Python >= 3.10
- GTK4 + PyGObject (`gi` / `PyGObject >= 3.44`)
- PyQt6 (used by the always-on-top overlay)

Install the Python dependencies on common distributions:

```bash
# Debian / Ubuntu
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0
pip install --user PyQt6

# Fedora
sudo dnf install python3-gobject PyGObject gtk4
pip install --user PyQt6

# Arch
sudo pacman -S python-gobject gtk4
pip install --user PyQt6

# Generic
pip install --user PyGObject PyQt6
```

## Install the launcher

A `.desktop` file must contain absolute paths, so run the installer to
generate one for your own system:

```bash
git clone https://github.com/ficusai/DASHBOARD.git
cd DASHBOARD
./install.sh            # installs for your user (no root needed)
```

For all users on the machine:

```bash
sudo ./install.sh --system
```

After installing, launch DASHBOARD from your application menu. A desktop
shortcut is also added automatically when the installer finds a Desktop
directory (disable with `--no-desktop`).

## Run without installing

```bash
./run-dashboard.sh
```

The wrapper locates the project from its own path, so the project can live
anywhere and `/usr/bin/python3` is not assumed. If `python3` is not on your
PATH, set `PYTHON=/path/to/python3 ./run-dashboard.sh`.

## Uninstall

```bash
./install.sh --uninstall          # remove your user launcher and icons
sudo ./install.sh --system --uninstall   # remove the system-wide ones
```

## Develop / test

```bash
pip install --user -e .
PYTHONPATH=00_app pytest 09_tests -v
```

## License

GPL-3.0-or-later