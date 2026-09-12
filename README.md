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
- **Always-on-top**: Uses PyQt6's `Qt.WindowStaysOnTopHint`, which works natively on Wayland. This replaces the previous xprop-based workaround that only functioned under X11. No environment variables are required.
- **Drag support**: The overlay uses Qt mouse events (`mousePressEvent` / `mouseMoveEvent` / `mouseReleaseEvent`) for click-and-drag repositioning.
- **Transparency**: The overlay uses Qt stylesheet `rgba()` for a translucent dark background.

> **Note**: GTK4 and PyQt6 coexist in the same process. Qt is initialized before GTK so `WindowStaysOnTopHint` is respected on Wayland.

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
| `feature/qt-always-on-top-overlay` | PyQt6 overlay with native Wayland always-on-top | Active |
| `feature/codebase-verification` | Fix runtime bugs, build/packaging, dependency contradictions, test failures, AGENTS.md rule compliance | Active |

### Branch-Related File Changes
- `00_app/test_overlay.py`: **REWRITTEN** — Replaced GTK4 window with PyQt6 `QWidget` using `Qt.WindowStaysOnTopHint` for native Wayland always-on-top; extracted pattern from PROGRESS /floating_overlay_card.py; added drag support via Qt mouse events; added `show_overlay()` / `hide_overlay()` / `is_overlay_visible()` module-level API.
- `00_app/00_main.py`: **ENHANCED** — Initializes PyQt6 `QApplication` before GTK; adds `GLib.timeout_add(50, _pump_qt_events)` to keep Qt event loop running alongside GTK; connects GTK "shutdown" signal to `qt_app.quit()`.
- `00_app/window.py`: **SIMPLIFIED** — Removed GTK-specific `TestOverlayWindow` import; now calls `test_overlay.show_overlay()` / `test_overlay.hide_overlay()` / `test_overlay.is_overlay_visible()`; updated tooltip to reflect Wayland-native behavior.
- `09_tests/test_overlay_qt.py`: **NEW** — Verifies module API (`show_overlay`, `hide_overlay`, `is_overlay_visible`), `TestOverlayWindow` class existence, and correct Qt window flags (`WindowStaysOnTopHint`, `FramelessWindowHint`, `Tool`, `Window`).
- `README.md`: Updated Features section to document PyQt6-based always-on-top; removed `GDK_BACKEND=x11` requirement note.
- `00_app/qt_overlay.py`: **FIXED** — Added `WA_StyledBackground`; removed broken `super(QWidget, widget).mouseMoveEvent()`; removed `required=True` from argparse; fixed command handling when no daemon running.
- `01_build/00_dashboard.spec`: **FIXED** — Corrected `PROJECT_ROOT` from `parent.parent` to `parent`.
- `pyproject.toml`: **FIXED** — Added `PyQt6>=6.5`; fixed entry point to `00_app.00_main:main`; replaced broken package discovery with explicit `py-modules`.
- `01_build/00_requirements.txt`: **FIXED** — Added `PyQt6>=6.5`.
- `01_build/01_build_executable.sh`: **FIXED** — Added `PyQt6` to pip install.
- `07_ci/00_release.yml`: **FIXED** — Added PyQt6; added Xvfb; added pytest step.
- `06_flatpak/00_org.ficus.Dashboard.yml`: **FIXED** — Added HTML5 client extension.
- `02_desktop/00_dashboard.desktop`: **FIXED** — Replaced absolute path with `Exec=dashboard`.
- `04_data/01_org.ficus.Dashboard.desktop`: **FIXED** — Aligned `Exec=dashboard`.
- `04_data/00_org.ficus.Dashboard.metainfo.xml`: **FIXED** — Bumped version to `0.2.0`.
- `CHANGELOG.md`: **FIXED** — Moved entries to `[0.2.0]`.
- `AGENTS.md`: **FIXED** — Permit PyQt6; updated Current State; fixed py_compile command.
- `03_git/00_git_commands.sh`: **FIXED** — Updated `.gitignore` heredoc.
- `09_tests/test_window.py`: **FIXED** — Works with Xvfb headless GTK4 testing.
- `feature-dashboard-ram-monitor/PLAN.md`: **FIXED** — Corrected invalid imports, `glib_idle_add`, double-start thread, plugin naming.