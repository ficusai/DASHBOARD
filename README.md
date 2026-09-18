# DASHBOARD

A small Linux desktop dashboard written in Python. The current application provides a GTK 4 main window and a separate PyQt6-based `TEST` overlay that can be shown, hidden, toggled, and dragged while remaining above normal windows. The repository also includes Linux desktop integration, a user/system installer, Flatpak metadata, release automation, tests, and an experimental PostgreSQL-backed job/task schema for planned dashboard functionality.

> **Current status:** The shipped UI is intentionally minimal. The project dashboard, queue, progress, Git branch, MCP-server, and related concepts are currently represented as design/project-tracking data rather than implemented screens in the GTK application.

## Features

- GTK 4 application window titled **DASHBOARD**.
- One-button overlay control: `Toggle TEST Overlay` / `Hide TEST Overlay`.
- Frameless, translucent PyQt6 overlay displaying `TEST`.
- Overlay singleton controlled through a Unix domain socket at:
  `~/.local/share/dashboard-overlay.sock`.
- Always-on-top overlay behavior using Qt's `WindowStaysOnTopHint` and XWayland (`QT_QPA_PLATFORM=xcb` by default).
- Mouse-draggable overlay with `startSystemMove()` where supported.
- Portable launcher wrapper that resolves the project directory from its own location.
- User or system-wide `.desktop` launcher installation with icon and AppStream metadata registration.
- Flatpak manifest targeting the GNOME 50 runtime.
- Pytest coverage for entry-point availability, window construction, overlay APIs, and Qt window flags.
- Experimental PostgreSQL schema for queued tasks, task events, statuses, verification methods, retries, tags, and vector embeddings.

## Requirements

### Runtime

- Linux desktop environment with GTK 4 support.
- Python **3.10 or newer**.
- GTK 4 and PyGObject (`gi`, PyGObject 3.44 or newer).
- PyQt6 6.5 or newer.
- X11/XWayland is required for the default reliable always-on-top behavior on Wayland. The overlay respects an explicitly supplied `QT_QPA_PLATFORM`, but native Wayland compositors generally do not allow applications to request an always-on-top surface.

### Development and packaging

- `pip` and a Python build environment for editable installation.
- `pytest` to run the test suite.
- Optional: PyInstaller for the release executable workflow.
- Optional: Flatpak and `flatpak-builder` to build the Flatpak package.

## Install system dependencies

Install GTK/PyGObject from your distribution and PyQt6 with pip. The exact package names vary by distribution.

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0
python3 -m pip install --user 'PyQt6>=6.5'
```

### Fedora

```bash
sudo dnf install python3-gobject PyGObject gtk4
python3 -m pip install --user 'PyQt6>=6.5'
```

### Arch Linux

```bash
sudo pacman -S python-gobject gtk4
python3 -m pip install --user 'PyQt6>=6.5'
```

The repository's installer checks whether Python, `gi`, and `PyQt6` can be imported, but it does not install these dependencies automatically.

## Quick start

```bash
git clone https://github.com/ficusai/DASHBOARD.git
cd DASHBOARD
./run-dashboard.sh
```

`run-dashboard.sh` finds `00_app/00_main.py` relative to the wrapper, so the checkout may live anywhere. If `python3` is not on `PATH`, select the interpreter explicitly:

```bash
PYTHON=/absolute/path/to/python3 ./run-dashboard.sh
```

The application creates a 400×300 GTK window. Click **Toggle TEST Overlay** to start or show the overlay. Click the button again to hide it. The overlay itself is a 140×60 frameless window labeled `TEST`; drag it with the mouse to reposition it.

## Install the desktop launcher

The repository contains a portable `.desktop` template, but desktop entries require absolute paths. `install.sh` substitutes the checkout directory and installs the generated launcher.

### Per-user installation

```bash
./install.sh
```

This installs into `~/.local`, registers the application and icons, installs AppStream metadata when available, refreshes desktop/icon caches, and adds a desktop shortcut when a Desktop directory is detected.

To avoid a desktop shortcut:

```bash
./install.sh --user --no-desktop
```

To explicitly request one:

```bash
./install.sh --desktop
```

### System-wide installation

```bash
sudo ./install.sh --system
```

The default system prefix is `/usr/local`. A custom prefix can be supplied with `--prefix`:

```bash
./install.sh --prefix /some/prefix --no-desktop
```

### Installer options

```text
-u, --user          Install for the current user (~/.local), the default
-s, --system        Install system-wide (/usr/local; normally use sudo)
    --prefix DIR    Install into a custom prefix
-d, --desktop       Force a desktop shortcut
-n, --no-desktop    Do not create a desktop shortcut
    --uninstall     Remove the launcher, metadata, icons, and shortcut
-q, --quiet         Suppress non-error output
-h, --help          Show help
```

### Uninstall

```bash
./install.sh --uninstall
sudo ./install.sh --system --uninstall
```

## Run the Python entry point directly

The main entry point is `00_app/00_main.py`:

```bash
PYTHONPATH=00_app python3 00_app/00_main.py
```

The `pyproject.toml` also declares a `dashboard` console script. Because the source directory uses numeric names and the modules import one another as top-level modules, the wrapper script is the most reliable source-tree launch path.

## Development setup

Create an isolated environment when your distribution allows the GTK bindings to be used from it:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
```

On distributions where PyGObject is supplied by the system package manager, install it system-wide as described above rather than relying on a pip build.

## Testing

Run the repository tests with the application directory on `PYTHONPATH`:

```bash
PYTHONPATH=00_app pytest 09_tests -v
```

For headless environments and CI, use the same settings as the release workflow:

```bash
DISPLAY=:99 \
QT_QPA_PLATFORM=offscreen \
GDK_BACKEND=x11 \
PYTHONPATH=00_app \
pytest 09_tests/ -v
```

The tests currently verify:

- `00_app/00_main.py` exposes a callable `main()` function.
- `window.create_window()` creates a window titled `DASHBOARD` with a default size of 400×300.
- The subprocess overlay module exposes `show_overlay()`, `hide_overlay()`, and `is_overlay_visible()`.
- `qt_overlay.py` exists and uses frameless, tool, always-on-top Qt window flags.

## Architecture

```text
00_app/
  00_main.py       GTK application entry point and activate callback
  window.py        GTK window factory and overlay toggle button
  test_overlay.py  subprocess bridge to the PyQt6 overlay daemon
  qt_overlay.py    singleton PyQt6 overlay and Unix-socket command server

02_desktop/
  00_dashboard.desktop
                   portable desktop-entry template

04_data/
  *.desktop        installed-app desktop metadata
  *.metainfo.xml   AppStream application metadata

05_icons/
  dashboard-icon.png
  hicolor/         application icons at multiple sizes

06_flatpak/
  *.yml            Flatpak build manifest

07_ci/
  00_release.yml   tag-triggered Linux build and GitHub Release workflow

08_legal/
  01_VERSION       project version (`0.2.0`)

09_tests/
  test_main.py     entry-point test
  test_window.py   GTK window test
  test_overlay_qt.py
                   overlay API and Qt flag tests

feature-JOBS/
  schema.sql       PostgreSQL task/job schema
  snapshots/       timestamped schema/full-database snapshots

install.sh         user/system launcher and icon installer
run-dashboard.sh   location-independent source-tree launcher
pyproject.toml     package metadata, dependencies, console script, pytest config
```

### Runtime flow

`run-dashboard.sh` resolves its own directory and executes `00_app/00_main.py`. The entry point creates a `Gtk.Application` with application ID `org.ficus.Dashboard`; when activated, `window.create_window()` builds the main window and presents it.

The GTK button delegates overlay state to `test_overlay.py`. That module starts `qt_overlay.py` as a subprocess for action commands and queries the daemon with `--visible`. The Qt process owns the overlay and listens on the Unix socket for `show`, `hide`, `toggle`, and `visible` commands. This process separation avoids GTK/Qt GType conflicts while allowing the GTK UI and Qt overlay to coexist.

## Overlay command-line interface

The overlay script can also be invoked directly:

```bash
python3 00_app/qt_overlay.py --show
python3 00_app/qt_overlay.py --hide
python3 00_app/qt_overlay.py --toggle
python3 00_app/qt_overlay.py --visible
```

`--visible` prints `true` or `false`. Action commands communicate with an existing daemon when possible; otherwise they start one and apply the requested command.

## Flatpak

The manifest is `06_flatpak/00_org.ficus.Dashboard.yml`. It uses:

- Application ID: `org.ficus.Dashboard`
- Runtime: `org.gnome.Platform` 50
- Command: `dashboard`
- X11 fallback and Wayland sockets
- DRI access
- Access to `~/Documents/DASHBOARD`

A typical local build from the repository root is:

```bash
flatpak-builder --user --install --force-clean build-dir \
  06_flatpak/00_org.ficus.Dashboard.yml
flatpak run org.ficus.Dashboard
```

The manifest's source path is the repository parent (`..` relative to `06_flatpak`), so invoke `flatpak-builder` from the repository root as shown.

## Release build

The workflow in `07_ci/00_release.yml` runs when a tag beginning with `v` is pushed. It installs GTK build dependencies, installs PyQt6 and PyInstaller, runs the tests headlessly, builds a Linux executable with:

```bash
pyinstaller --clean --noconfirm 01_build/00_dashboard.spec
```

The resulting executable is renamed `dashboard-linux-x86_64`, uploaded as an artifact, and attached to a generated GitHub Release.

> **Maintainer note:** the current repository tree does not include the `01_build/00_dashboard.spec` path referenced by the release workflow. Add that PyInstaller specification, or update the workflow, before relying on tagged release builds.

## Experimental JOBS schema

`feature-JOBS/schema.sql` and its snapshots describe a PostgreSQL 18.6 task queue/data model. This schema is not currently connected to the GTK application.

It includes:

- `tasks`: UUID task records, priority, task type, instructions, target paths, verification configuration, retry limits, status, result/error data, dependencies, tags, and a 768-dimensional `vector` embedding.
- `task_events`: append-style task lifecycle events linked to `tasks` with cascading deletion.
- `models_allowed`, `tags_allowed`, and `system_state` support configuration and controlled values.
- Enums for task status, task type, event kind, and verification method.
- HNSW vector search, status, ready/running, and tag indexes.
- Lifecycle states including `pending`, `running`, `completed`, `error`, `failed`, and `skipped`.

The dump requires PostgreSQL with the `pgvector` extension. It should be treated as a schema artifact rather than an application migration until database integration is implemented.

## Project-tracking design

`NEW-BRANCH-FEAT-PROJECTS-TRACKING.json` documents a planned single-window Project Dashboard with:

- static project details such as name, intention, and mission;
- editable ideas, dependencies, and connected servers;
- dynamically updated MCP servers and Git branches;
- a queue of work items from sources such as Opencode and an Ollama embedding model;
- a progress estimate based on queue position and seconds per queue item.

These fields describe the intended product direction; the current GTK code only implements the minimal window and `TEST` overlay.

## Packaging files

| File | Purpose |
| --- | --- |
| `pyproject.toml` | Setuptools metadata, Python requirement, PyGObject/PyQt6 dependencies, console script, and pytest configuration |
| `install.sh` | Generates and installs absolute-path desktop launchers, icons, and metadata |
| `run-dashboard.sh` | Runs the source checkout without installation |
| `00_dashboard.desktop` | Portable desktop-entry template used by the installer |
| `04_data/00_org.ficus.Dashboard.metainfo.xml` | AppStream metadata |
| `04_data/01_org.ficus.Dashboard.desktop` | Installed launcher entry for packaged builds |
| `06_flatpak/00_org.ficus.Dashboard.yml` | Flatpak manifest |
| `07_ci/00_release.yml` | Tagged Linux release workflow |
| `08_legal/01_VERSION` | Human-readable project version |

## Version

The project version is **0.2.0**, declared in both `pyproject.toml` and `08_legal/01_VERSION`.

## License

DASHBOARD is licensed under the **GNU General Public License, version 3 or later** (`GPL-3.0-or-later`). AppStream metadata is marked `CC-BY-4.0`.
