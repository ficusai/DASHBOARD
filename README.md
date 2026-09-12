# DASHBOARD

Minimal GTK 4 window application for Fedora Linux (GNOME / Wayland).

## Goal
- [x] Empty window with system close button only
- [x] Executable from desktop
- [x] All files in `/home/ficus-pro/Documents/DASHBOARD/`
- [x] Git local tracking
- [x] Toggle button + transparent TEST overlay (always-on-top on Wayland via PyQt6)
- [ ] Publish to remote repository (later)
- [ ] Add application icon
- [ ] Add content / widgets (future phase)

## Features

### TEST Overlay
A transparent, frameless floating window that can be toggled from the main window:
- Click **"Toggle TEST Overlay"** in the main window to show/hide it.
- The overlay displays only the text **"TEST"** in blue on a dark translucent background.
- **Always-on-top**: Uses PyQt6's `Qt.WindowStaysOnTopHint`, which works natively on Wayland. The overlay runs as a separate process (`qt_overlay.py`) to avoid GTK/Qt GType conflicts, communicating via a Unix domain socket. No environment variables are required.
- **Drag support**: The overlay uses Qt mouse events (`mousePressEvent` / `mouseMoveEvent` / `mouseReleaseEvent`) for click-and-drag repositioning.
- **Transparency**: The overlay uses Qt stylesheet `rgba()` for a translucent dark background.

> **Architecture note**: The overlay is a standalone PyQt6 process. The main GTK app launches it via `subprocess` and controls it through a Unix domain socket (`~/.local/share/dashboard-overlay.sock`). This avoids GTK/Qt coexistence issues on Wayland.

## File‑Numbering Convention
Folders and files are numbered `_00`–`_99` in **runtime / build order**:

| Prefix | Meaning |
|--------|---------|
| `00_`  | Application source (runtime) |
| `01_`  | Build & packaging |
| `02_`  | Desktop integration |
| `03_`  | Git helpers |
| `04_`  | AppStream & metadata |
| `05_`  | Application icons |
| `06_`  | Flatpak packaging |
| `07_`  | CI/CD |
| `08_`  | Legal & licensing |
| `09_`  | Tests |

## Setup Steps
1. `sudo dnf install python3-gobject gtk4 python3-gobject-devel`
2. `pip install --user pyinstaller`
3. `bash 01_build/01_build_executable.sh`
4. `cp 02_desktop/00_dashboard.desktop ~/.local/share/applications/`
5. `bash 03_git/00_git_commands.sh`

## Future Work
- [ ] Add a basic layout (header bar, content area)
- [ ] Implement data storage in the project folder
- [ ] Add unit tests under `09_tests/`
- [ ] Create RPM package with `fpm` or `fbs`
- [ ] Publish to GitHub / GitLab

---
## Git & Release Branching

Primary release branch: `DASHBOARD-0.1v-linux-native`
Remote repository: `https://github.com/ficusai/DASHBOARD.git`

### Branch Map
| Branch | Description | Status |
|--------|-------------|--------|
| `DASHBOARD-0.1v-linux-native` | Primary release branch for Linux native environment | Active |
| `feature/test-overlay-toggle` | Transparent TEST overlay with toggle button | Active |
| `feature/qt-always-on-top-overlay` | PyQt6 overlay with native Wayland always-on-top (separate process) | Active |

### Branch-Related File Changes
- `00_app/qt_overlay.py`: **NEW** — Standalone PyQt6 overlay daemon with Unix socket IPC; supports `--show`, `--hide`, `--toggle`, `--visible`; singleton pattern prevents multiple instances.
- `00_app/test_overlay.py`: **REWRITTEN** — Subprocess-based overlay management; launches `qt_overlay.py` and communicates via its CLI flags; exposes `show_overlay()`, `hide_overlay()`, `toggle_overlay()`, `is_overlay_visible()`.
- `00_app/00_main.py`: **SIMPLIFIED** — Pure GTK4 entry point; no Qt dependencies; clean shutdown.
- `00_app/window.py`: **UPDATED** — Toggle logic now calls `test_overlay.show_overlay()` / `hide_overlay()` / `is_overlay_visible()`.
- `09_tests/test_overlay_qt.py`: **UPDATED** — Tests module API, script existence, and Qt window flags.
- `README.md`: Updated Features and Architecture sections.
- `CHANGELOG.md`: Documented separate-process architecture.