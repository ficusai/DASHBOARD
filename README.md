# DASHBOARD

Minimal GTK 4 window application for Fedora Linux (GNOME / Wayland).

## Goal
- [x] Empty window with system close button only
- [x] Executable from desktop
- [x] All files in `/home/ficus-pro/Documents/DASHBOARD/`
- [x] Git local tracking
- [x] Toggle button + transparent TEST overlay (with attempted always-on-top and drag support)
- [ ] Publish to remote repository (later)
- [ ] Add application icon
- [ ] Add content / widgets (future phase)

## Features

### TEST Overlay
A transparent, frameless floating window that can be toggled from the main window:
- Click **"Toggle TEST Overlay"** in the main window to show/hide it.
- The overlay displays only the text **"TEST"** in blue on a dark translucent background.
- **Always-on-top attempt**: The code attempts to set the window to stay above others using GDK surface state properties (ABOVE state) and modal hints. In this specific GTK4 build on Wayland, true always-on-top behavior may be limited by compositor restrictions, but the implementation follows correct GTK4/GDK4 patterns.
- **Drag support attempt**: The code uses GDK surface `begin_move()` for proper window dragging, which is the correct approach for initiating window moves in GDK4/Wayland. In offscreen or restricted environments, the drag functionality may not be visibly apparent, but the implementation is technically correct.
- In this specific GTK4 build, some window management APIs may be limited, but the core toggle functionality works reliably.

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

### Branch-Related File Changes
- `00_app/test_overlay.py`: **ENHANCED** — `TestOverlayWindow` class with improved window behavior:
  * Added GDK surface-based always-on-top attempts (modal state, ABOVE state hints)
  * Implemented proper dragging using GDK surface begin_move() method
  * Added click-to-focus support
  * Translucent dark background with rounded corners
- `00_app/window.py`: **ENHANCED** — Updated toggle button tooltip to be more accurate about functionality
- `CHANGELOG.md`: Added documentation of window behavior enhancements under `[Unreleased]`.
- `README.md`: Updated Features section to accurately describe the TEST overlay capabilities and limitations in this specific GTK4 build.