# AI Agent Plan — DASHBOARD Refine (Phase 2)

**Branch:** `feature/refine`
**Base:** `DASHBOARD-0.1v-linux-native`
**Repo:** `/home/ficus-pro/Documents/DASHBOARD`
**Date:** 2026-09-13
**Status:** Ready for execution

---

## Executive Summary

This plan fixes **16 remaining issues** that were not covered in the previous `feature/codebase-verification` pass. These are critical bugs (silent data loss via `.gitignore`, import-time crashes, missing license, broken desktop launch) and structural gaps (no test fixtures, no packaging metadata, Flatpak sandbox misconfiguration).

**Verification baseline (all commands run from `/home/ficus-pro/Documents/DASHBOARD`):**
- `python3 -m py_compile 00_app/*.py` — passes
- `DISPLAY=:99 QT_QPA_PLATFORM=offscreen GDK_BACKEND=x11 PYTHONPATH=00_app pytest 09_tests/ -v` — 5 passed, 0 failed
- `git check-ignore -v 01_build/00_dashboard.spec` — **PASS** (ignored, needs fix)
- `git ls-files 05_icons/` — **FAIL** (0 files tracked, needs fix)
- `ls 08_legal/00_LICENSE` — **FAIL** (missing, needs fix)
- `python3 -c "import importlib,sys; sys.path.insert(0,'00_app'); importlib.import_module('00_main')"` — **hangs** (QApplication created at import time, needs fix)

---

## Phase 0 — Pre-flight

- [ ] `git status` — confirm on branch `feature/refine`, working tree has only uncommitted `qt_overlay.py` edit from previous branch
- [ ] `git log --oneline -3` — confirm last commit is `244ff8c fix: codebase verification pass`
- [ ] Record baseline test count: `DISPLAY=:99 QT_QPA_PLATFORM=offscreen GDK_BACKEND=x11 PYTHONPATH=00_app pytest 09_tests/ -v --tb=no -q`

---

## Phase 1 — Fix Critical VCS Data Loss (A.1, A.2, A.3)

### A.1 — Stop `.gitignore` from hiding `*.spec` build configs
`*.spec` glob matches `01_build/00_dashboard.spec`. Clone victims lose their build spec.

**File:** `.gitignore`

Change:
```gitignore
*.spec
```
To:
```gitignore
# Build artefacts
dist/
build/
!01_build/*.spec
__pycache__/
```

### A.2 — Fix `!05_icons/` to un-ignore PNGs inside
Git does NOT re-include files inside a directory just because the directory entry is un-ignored.

**File:** `.gitignore`

Change:
```gitignore
*.png
!05_icons/
```
To:
```gitignore
*.png
!05_icons/
!05_icons/**/*
```

### A.3 — Track the 6 icon PNGs
After A.2 fix, add and verify:
```bash
git add 05_icons/
git ls-files 05_icons/   # must show 6 files
```

- [ ] Apply A.1 and A.2 edits to `.gitignore`
- [ ] Run `git add .gitignore && git status --short .gitignore` — confirm staged
- [ ] Run `git add 05_icons/ && git ls-files 05_icons/` — confirm 6 tracked
- [ ] Run `git check-ignore -v 01_build/00_dashboard.spec` — must return nothing

---

## Phase 2 — Add Missing `08_legal/00_LICENSE` (A.4)

GPL-3.0-or-later requires full license text distributed with source.

- [ ] Copy system GPL-3.0 text:
  ```bash
  cp /usr/share/licenses/cockpit-bridge/GPL-3.0.txt 08_legal/00_LICENSE
  ```
- [ ] Add SPDX header as first line:
  ```
  # SPDX-License-Identifier: GPL-3.0-or-later
  # Copyright (C) 2026 ficus-pro
  ```
  (insert after the existing first line)
- [ ] Verify: `head -3 08_legal/00_LICENSE` shows SPDX header
- [ ] Verify: `git add 08_legal/00_LICENSE && git ls-files 08_legal/` shows both files

---

## Phase 3 — Fix Import-Time Side Effects in `00_main.py` (C.1, C.2)

**Problem:** `QApplication([])` and `GLib.timeout_add(50, _pump_qt_events)` run at **module import time**. This causes:
- `test_main.py`'s `importlib.import_module("00_main")` to start a forever-firing timeout
- Any tool that imports `00_main` (linters, docs generators) to block on Qt initialization
- The app to crash if PyQt6 is not installed, even before `main()` is called

**File:** `00_app/00_main.py`

**Current (broken):**
```python
from PyQt6.QtWidgets import QApplication    # line 18
from PyQt6.QtCore import Qt                 # line 19
...
_qt_app = QApplication.instance()           # line 27
if _qt_app is None:
    QApplication([])                        # line 29 — SIDE EFFECT at import
...
GLib.timeout_add(50, _pump_qt_events)       # line 43 — SIDE EFFECT at import
```

**Target (fixed):**
```python
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – Entry point.
Launches the GTK application and shows the main window.

Qt (PyQt6) is initialized lazily inside main() so that importing this module
does not create a QApplication or start background timers.
"""

import os
import sys
from pathlib import Path

# Environment variables must be set before any GUI toolkit initializes.
os.environ.setdefault("QT_QPA_PLATFORM", "wayland")

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib


def _pump_qt_events() -> bool:
    """Process pending Qt events from the GLib main loop."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is not None:
        app.processEvents()
    return True  # Keep firing.


def on_activate(app):
    """Callback invoked when the application is activated."""
    from PyQt6.QtWidgets import QApplication
    qt_app = QApplication.instance()
    if qt_app is None:
        QApplication([])
    GLib.timeout_add(50, _pump_qt_events)
    from window import create_window
    win = create_window(app)
    win.present()


def on_shutdown(app):
    """Clean up the Qt application when GTK shuts down."""
    from PyQt6.QtWidgets import QApplication
    qt_app = QApplication.instance()
    if qt_app is not None:
        qt_app.quit()


def main():
    """Create the GTK application and run it."""
    from PyQt6.QtWidgets import QApplication
    qt_app = QApplication.instance()
    if qt_app is None:
        QApplication([])
    app = Gtk.Application(application_id="org.ficus.Dashboard")
    app.connect("activate", on_activate)
    app.connect("shutdown", on_shutdown)
    return app.run(None)


if __name__ == "__main__":
    raise SystemExit(main())
```

Key changes:
1. Removed top-level `from PyQt6.QtWidgets import QApplication` and `from PyQt6.QtCore import Qt`
2. Removed `_qt_app = QApplication.instance(); if _qt_app is None: QApplication([])` from module level
3. Removed `GLib.timeout_add(50, _pump_qt_events)` from module level
4. Moved all PyQt6 imports and side effects inside `main()` and `on_activate()`
5. Moved `from window import create_window` inside `on_activate()` to avoid top-level GTK import chain

- [ ] Replace `00_app/00_main.py` with the target above
- [ ] Verify: `python3 -c "import importlib,sys; sys.path.insert(0,'00_app'); importlib.import_module('00_main'); print('OK — no side effects')" 2>&1` prints `OK` and exits within 2 seconds
- [ ] Verify: `python3 -m py_compile 00_app/00_main.py` passes
- [ ] Verify: tests still pass (the import-time side effect is gone, so `test_main.py` should be cleaner)

---

## Phase 4 — Fix Lazy Import in `window.py` (C.3)

**Problem:** `import test_overlay` at module top means the GTK app cannot start at all if PyQt6 is missing — even if the user never clicks the overlay button.

**File:** `00_app/window.py`

Move `import test_overlay` from module top into the two functions that use it.

**Current:**
```python
import test_overlay


def create_window(app: Gtk.Application) -> Gtk.ApplicationWindow:
    ...


def _on_toggle_clicked(btn: Gtk.Button) -> None:
    if test_overlay.is_overlay_visible():
        test_overlay.hide_overlay()
    else:
        test_overlay.show_overlay()
    _refresh_button_label(btn)


def _refresh_button_label(btn: Gtk.Button) -> None:
    if test_overlay.is_overlay_visible():
        btn.set_label("Hide TEST Overlay")
    else:
        btn.set_label("Toggle TEST Overlay")
```

**Target:**
```python
def create_window(app: Gtk.Application) -> Gtk.ApplicationWindow:
    ...  # unchanged body


def _on_toggle_clicked(btn: Gtk.Button) -> None:
    import test_overlay
    if test_overlay.is_overlay_visible():
        test_overlay.hide_overlay()
    else:
        test_overlay.show_overlay()
    _refresh_button_label(btn)


def _refresh_button_label(btn: Gtk.Button) -> None:
    import test_overlay
    if test_overlay.is_overlay_visible():
        btn.set_label("Hide TEST Overlay")
    else:
        btn.set_label("Toggle TEST Overlay")
```

- [ ] Remove `import test_overlay` from top of `window.py`
- [ ] Add `import test_overlay` inside `_on_toggle_clicked` and `_refresh_button_label`
- [ ] Verify: `python3 -c "import sys; sys.path.insert(0,'00_app'); from window import create_window; print('OK')"` exits without error (no PyQt6 import triggered)
- [ ] Verify: `python3 -m py_compile 00_app/window.py` passes

---

## Phase 5 — Clean Dead Code (B.2, B.4, B.5, B.6)

### B.2 — Use `ICON_DIR` in PyInstaller spec datas
`ICON_DIR` is defined on line 9 of `00_dashboard.spec` but never referenced in the `datas` list. Icons are not bundled into the frozen executable.

**File:** `01_build/00_dashboard.spec`

Add icons to the `datas` list:
```python
    datas=[
        (str(DATA_DIR / "00_org.ficus.Dashboard.metainfo.xml"), "data"),
        (str(DATA_DIR / "01_org.ficus.Dashboard.desktop"), "data"),
        (str(ICON_DIR), "icons"),
    ],
```

### B.4 — Remove unused `QPushButton` from `qt_overlay.py`
`QPushButton` is imported but never instantiated or used.

**File:** `00_app/qt_overlay.py`

Remove `QPushButton` from the import tuple:
```python
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QWidget,
)
```

### B.5 — Remove unused `import pytest` from `test_main.py`
**File:** `09_tests/test_main.py`

Remove line 7: `import pytest`

### B.6 — Remove unused `import pytest` from `test_overlay_qt.py`
**File:** `09_tests/test_overlay_qt.py`

Remove line 10: `import pytest`

- [ ] Apply all four fixes
- [ ] Verify: `python3 -m py_compile 00_app/*.py` passes
- [ ] Verify: `DISPLAY=:99 QT_QPA_PLATFORM=offscreen GDK_BACKEND=x11 PYTHONPATH=00_app pytest 09_tests/ -v --tb=short` — all pass

---

## Phase 6 — Add `09_tests/conftest.py` (D.1)

Every test file currently duplicates `sys.path.insert(...)` and has no shared headless environment setup.

**Create new file:** `09_tests/conftest.py`

```python
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""Shared pytest fixtures and configuration for DASHBOARD tests."""

import os
import sys
from pathlib import Path

import pytest

# Add 00_app to path so numbered modules (00_main, window, test_overlay, qt_overlay)
# are importable regardless of how pytest is invoked.
sys.path.insert(0, str(Path(__file__).parent.parent / "00_app"))

# Headless environment for both GTK4 and PyQt6.
# GTK needs GDK_BACKEND=x11 with Xvfb; Qt needs QT_QPA_PLATFORM=offscreen.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("GDK_BACKEND", "x11")


@pytest.fixture(autouse=True)
def _cleanup_qt_app():
    """Ensure no stray QApplication survives between tests."""
    yield
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is not None:
        app.quit()
        # Force garbage collection so the next test starts fresh
        import gc
        gc.collect()
```

Then remove duplicated `sys.path.insert(...)` from all test files:
- `09_tests/test_window.py` — remove lines 5–6 (`import sys`, `sys.path.insert(...)`)
- `09_tests/test_main.py` — remove lines 4–5 (`import sys`, `sys.path.insert(...)`)
- `09_tests/test_overlay_qt.py` — remove lines 6–7 (`import sys`, `sys.path.insert(...)`)

- [ ] Create `09_tests/conftest.py`
- [ ] Remove duplicated `sys.path.insert` from all 3 test files
- [ ] Verify: `DISPLAY=:99 QT_QPA_PLATFORM=offscreen GDK_BACKEND=x11 PYTHONPATH=00_app pytest 09_tests/ -v --tb=short` — all pass
- [ ] Verify: no `sys.path.insert` remains in any test file

---

## Phase 7 — Fix `test_window.py` (D.2, D.3)

**Problems:**
1. `Gtk.Application` is never registered — GTK4 emits `Gtk-CRITICAL` warnings
2. No `app.release()` cleanup — resource leak
3. No `GDK_BACKEND=x11` documented in the test itself (now handled by conftest.py)

**File:** `09_tests/test_window.py`

**Target:**
```python
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""Basic tests for the DASHBOARD window factory."""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from window import create_window


def test_window_creation():
    app = Gtk.Application(application_id="org.ficus.Dashboard.Test")
    app.register(None)
    try:
        win = create_window(app)
        assert win.get_title() == "DASHBOARD"
        assert win.get_default_size() == (400, 300)
    finally:
        app.release()
```

- [ ] Replace `09_tests/test_window.py` with target
- [ ] Verify test passes in headless mode

---

## Phase 8 — Fix Desktop Launch File (User Report)

The user reports `/home/ficus-pro/Desktop/00_dashboard.desktop` does not launch anything. It has absolute paths and a broken icon reference.

**File:** `/home/ficus-pro/Desktop/00_dashboard.desktop`

**Current (broken):**
```desktop
Exec=python3 /home/ficus-pro/Documents/DASHBOARD/00_app/00_main.py
Icon=/home/ficus-pro/Documents/DASHBOARD/05_icons/dashboard-icon.png
```

**Target:**
```desktop
[Desktop Entry]
Type=Application
Name=DASHBOARD
Comment=Minimal dashboard application
Exec=dashboard
Icon=org.ficus.Dashboard
Terminal=false
Categories=Utility;
Keywords=dashboard;gtk;python;
StartupNotify=true
StartupWMClass=Dashboard
X-GNOME-UsesNotifications=true
```

Changes:
- `Exec` → `dashboard` (canonical command installed by `pip install .` or Flatpak)
- `Icon` → `org.ficus.Dashboard` (Freedesktop icon theme name, resolves to installed hicolor icons)
- Added `StartupWMClass=Dashboard` for proper window matching in GNOME/KDE

- [ ] Write fixed desktop file to `/home/ficus-pro/Desktop/00_dashboard.desktop`
- [ ] Test: double-click the desktop file or run `desktop-file-validate /home/ficus-pro/Desktop/00_dashboard.desktop`

---

## Phase 9 — Fix AppStream Metainfo (F.1, F.2)

### F.1 — Remove broken screenshot reference
`04_data/screenshot.png` does not exist. `appstreamcli validate` will flag this.

### F.2 — Add `<provides>` section
Software centers need `<provides><binary>dashboard</binary></provides>` to map the app to its executable.

**File:** `04_data/00_org.ficus.Dashboard.metainfo.xml`

**Target:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>org.ficus.Dashboard</id>
  <name>DASHBOARD</name>
  <summary>Minimal dashboard application for Fedora Linux</summary>
  <metadata_license>CC-BY-4.0</metadata_license>
  <project_license>GPL-3.0-or-later</project_license>
  <description>
    <p>
      DASHBOARD is a lightweight GTK4 application built with Python and PyGObject.
      It provides a clean, minimal window for future dashboard functionality.
    </p>
  </description>
  <launchable type="desktop-id">org.ficus.Dashboard.desktop</launchable>
  <provides>
    <binary>dashboard</binary>
  </provides>
  <url type="homepage">https://github.com/ficusai/DASHBOARD</url>
  <url type="bugtracker">https://github.com/ficusai/DASHBOARD/issues</url>
  <url type="vcs-browser">https://github.com/ficusai/DASHBOARD</url>
  <releases>
    <release version="0.2.0" date="2026-09-13">
      <description>
        <p>Initial release: minimal GTK4 window with TEST overlay toggle.</p>
      </description>
    </release>
  </releases>
  <content_rating type="oars-1.1"/>
</component>
```

Changes from current:
- Removed entire `<screenshots>` block (no screenshot exists)
- Added `<provides><binary>dashboard</binary></provides>`
- Updated release description to mention TEST overlay
- Kept version `0.2.0` and date `2026-09-13`

- [ ] Replace `04_data/00_org.ficus.Dashboard.metainfo.xml` with target
- [ ] Verify: `appstreamcli validate 04_data/00_org.ficus.Dashboard.metainfo.xml 2>&1` — no errors (warnings about missing screenshot are acceptable since we removed the reference)

---

## Phase 10 — Fix Flatpak Manifest (E.1, E.2, E.3, E.4)

**File:** `06_flatpak/00_org.ficus.Dashboard.yml`

**Problems:**
- E.1: Missing `--session-bus` for GApplication D-Bus activation
- E.2: Overbroad `--filesystem=xdg-documents/DASHBOARD` exposes entire project tree
- E.3: No PyQt6 runtime (pip installs it but Flatpak sandboxes filesystem)
- E.4: `cp -r 05_icons/hicolor/*` will fail if icons aren't in the build context

**Target:**
```yaml
app-id: org.ficus.Dashboard
runtime: org.gnome.Platform
runtime-version: '50'
sdk: org.gnome.Sdk
command: dashboard

finish-args:
  - --share=ipc
  - --socket=fallback-x11
  - --socket=wayland
  - --device=dri
  - --socket=session-bus

modules:
  - name: dashboard
    buildsystem: simple
    build-commands:
      - pip3 install --prefix=/app .
      - install -Dm644 04_data/00_org.ficus.Dashboard.metainfo.xml
        /app/share/metainfo/org.ficus.Dashboard.metainfo.xml
      - install -Dm644 04_data/01_org.ficus.Dashboard.desktop
        /app/share/applications/org.ficus.Dashboard.desktop
      - cp -r 05_icons/hicolor/* /app/share/icons/hicolor/
    sources:
      - type: dir
        path: ..
```

Changes:
- Removed `--filesystem=xdg-documents/DASHBOARD` (app doesn't need its source tree at runtime)
- Added `--socket=session-bus` (required for GApplication D-Bus activation)
- Kept icons copy (will work once Phase 1 tracks the icons)

**Note on PyQt6 in Flatpak:** `pip3 install --prefix=/app .` from `pyproject.toml` will pull PyQt6 as a dependency. Since Flatpak's Python runtime includes pip, this works. No extra extension needed.

- [ ] Apply fixes to `06_flatpak/00_org.ficus.Dashboard.yml`
- [ ] Verify: no `xdg-documents` in finish-args
- [ ] Verify: `--session-bus` present

---

## Phase 11 — Fix PyInstaller Spec (G.1)

**File:** `01_build/00_dashboard.spec`

Add PyQt6 hiddenimports so PyInstaller bundles the Qt libraries:

**Current hiddenimports:**
```python
    hiddenimports=[
        "gi",
        "gi.repository.Gtk",
        "gi.repository.Gdk",
    ],
```

**Target:**
```python
    hiddenimports=[
        "gi",
        "gi.repository.Gtk",
        "gi.repository.Gdk",
        "PyQt6.QtCore",
        "PyQt6.QtWidgets",
        "PyQt6.QtGui",
    ],
```

- [ ] Add the three PyQt6 entries
- [ ] Verify: spec is valid Python syntax

---

## Phase 12 — Update `pyproject.toml` (J.4, J.6)

**File:** `pyproject.toml`

Add `[project.optional-dependencies]` and `[project.urls]`, and switch to PEP 639 license format.

**Target:**
```toml
# SPDX-License-Identifier: GPL-3.0-or-later
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "dashboard"
version = "0.2.0"
description = "Minimal GTK4 dashboard application for Fedora Linux"
readme = "README.md"
license = "GPL-3.0-or-later"
requires-python = ">=3.10"
dependencies = [
    "PyGObject>=3.44",
    "PyQt6>=6.5",
]

[project.scripts]
dashboard = "00_app.00_main:main"

[project.optional-dependencies]
test = ["pytest", "pytest-cov"]
build = ["pyinstaller"]

[project.urls]
Homepage = "https://github.com/ficusai/DASHBOARD"
Repository = "https://github.com/ficusai/DASHBOARD.git"
Issues = "https://github.com/ficusai/DASHBOARD/issues"

[tool.setuptools]
py-modules = ["00_app.00_main", "00_app.window", "00_app.test_overlay", "00_app.qt_overlay", "00_app.quit"]

[tool.pytest.ini_options]
testpaths = ["09_tests"]
addopts = "-v"
```

Changes from current:
- `license` changed from `{ text = "GPL-3.0-or-later" }` to `"GPL-3.0-or-later"` (PEP 639)
- Added `[project.optional-dependencies]` with `test` and `build` groups
- Added `[project.urls]` with Homepage, Repository, Issues
- Kept everything else the same

- [ ] Apply changes
- [ ] Verify: `python3 -m py_compile` still passes (TOML syntax is valid)
- [ ] Verify: `pip install -e . --dry-run` works (if pip is available)

---

## Phase 13 — Update `AGENTS.md` Python Version (H.1)

**File:** `AGENTS.md`

Change the stack table from `Python 3.11+` to `Python 3.10+` to match `pyproject.toml`'s `requires-python = ">=3.10"`.

**Current:**
```
| **Stack** | Python 3.11+, PyGObject, GTK4, PyQt6, PyInstaller, Flatpak |
```

**Target:**
```
| **Stack** | Python 3.10+, PyGObject, GTK4, PyQt6, PyInstaller, Flatpak |
```

- [ ] Apply fix
- [ ] Verify: grep confirms `3.10` in both files

---

## Phase 14 — Update `CONTRIBUTING.md` (H.10)

**File:** `CONTRIBUTING.md`

Add a Testing section and update Setup to include PyQt6.

**Current:**
```markdown
## Development Setup

1. Install system dependencies:
   ```bash
   sudo dnf install python3-gobject gtk4 python3-gobject-devel
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/ficusai/DASHBOARD.git
   cd dashboard
   ```

3. Run the application:
   ```bash
   python3 00_app/00_main.py
   ```
```

**Target:**
```markdown
## Development Setup

1. Install system dependencies:
   ```bash
   sudo dnf install python3-gobject gtk4 python3-gobject-devel
   ```

2. Install Python dependencies:
   ```bash
   pip install --user pyinstaller PyQt6 pytest pytest-cov
   ```

3. Clone the repository:
   ```bash
   git clone https://github.com/ficusai/DASHBOARD.git
   cd dashboard
   ```

4. Run the application:
   ```bash
   python3 00_app/00_main.py
   ```

## Testing

Run the test suite with a virtual display (required for GTK4 headless testing):

```bash
Xvfb :99 -screen 0 1024x768x24 &
DISPLAY=:99 QT_QPA_PLATFORM=offscreen GDK_BACKEND=x11 PYTHONPATH=00_app pytest 09_tests/ -v
kill %1 2>/dev/null
```

Or run just the Qt overlay tests (no display needed):
```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=00_app pytest 09_tests/test_overlay_qt.py -v
```
```

- [ ] Apply changes to `CONTRIBUTING.md`

---

## Phase 15 — Fix PLAN.md Scope Bugs (I.2, I.3, I.9, I.10)

**File:** `feature-dashboard-ram-monitor/PLAN.md`

### I.2 — `panels` variable scope
`create_window()` returns `Gtk.ApplicationWindow`, not panels. The Phase 4 snippet references `panels` but it's never returned.

**Fix:** Change `create_window()` signature in the plan to return a tuple, or create panels in `00_main.py` before calling `create_window()`.

Update Phase 4 in PLAN.md:
```python
# In window.py — change signature:
def create_window(app: Gtk.Application) -> tuple[Gtk.ApplicationWindow, tuple]:
    ...
    panels = create_ram_panels()
    for p in panels:
        box.append(p)
    return win, panels
```

```python
# In 00_main.py:
win, panels = create_window(app)
win.present()
```

### I.3 — Loader/plugin contract contradiction
Phase 5 says loader calls `ctx["register_panel"](...)`. Phase 6 says plugin calls `register_panel` itself.

**Fix:** Pick ONE contract. Recommended: plugin's `init()` returns info dict, loader registers:
```python
# In load_plugins():
info = plugin_mod.init(ctx)
ctx["register_panel"](info["name"], info["panel"])
```
Update Phase 6 to match — `plugin.init()` should NOT call `register_panel` itself.

### I.9 — `start_ram_sampler` thread start semantics
Current plan: function returns thread object, then caller calls `.start()` again. This double-starts.

**Fix:** Clarify that `start_ram_sampler()` RETURNS an ALREADY-STARTED daemon thread. Remove `t.start()` from Phase 4.

```python
t = start_ram_sampler(DB_PATH, lambda s: GLib.idle_add(_on_ram_sample, s, panels))
# t is already running; do NOT call t.start()
```

### I.10 — SQL schema PK bug
`ts INTEGER PRIMARY KEY` fails if two samples arrive in the same second.

**Fix:** Change schema to:
```sql
CREATE TABLE ram_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    used_mb REAL NOT NULL,
    total_mb REAL NOT NULL
);
CREATE INDEX idx_ram_ts ON ram_samples(ts);
```

- [ ] Apply all four PLAN.md fixes
- [ ] Verify: no syntax errors in the markdown (just visual inspection)

---

## Phase 16 — Update README.md (H.5, H.6, H.7)

### H.5 — Move branch-related file changes to per-branch section
The `## Branch-Related File Changes` section documents only historical branches. It should be replaced with a concise branch map and a pointer to commit history.

### H.6 — Check off completed Future Work
- [x] Add unit tests under `09_tests/` — already done (5 tests)

### H.7 — Add PyQt6 to Setup Steps
Current setup misses PyQt6 installation.

**Update Setup Steps:**
```markdown
## Setup Steps
1. `sudo dnf install python3-gobject gtk4 python3-gobject-devel`
2. `pip install --user pyinstaller PyQt6 pytest`
3. `bash 01_build/01_build_executable.sh`
4. `cp 02_desktop/00_dashboard.desktop ~/.local/share/applications/`
5. `bash 03_git/00_git_commands.sh`
```

- [ ] Apply README updates
- [ ] Verify: setup steps include PyQt6

---

## Phase 17 — Final Verification

Run all checks and confirm zero failures:

```bash
# 1. Syntax check
python3 -m py_compile 00_app/*.py && echo "py_compile: OK"

# 2. No import-side-effect hang
timeout 3 python3 -c "import importlib,sys; sys.path.insert(0,'00_app'); importlib.import_module('00_main'); print('import: OK')" && echo "import: OK"

# 3. All tests pass
Xvfb :99 -screen 0 1024x768x24 &
XPID=$!; sleep 1
DISPLAY=:99 QT_QPA_PLATFORM=offscreen GDK_BACKEND=x11 PYTHONPATH=00_app pytest 09_tests/ -v --tb=short
kill $XPID 2>/dev/null; wait $XPID 2>/dev/null

# 4. No tracked files hidden by .gitignore
git check-ignore -v 01_build/00_dashboard.spec || echo "A.1: spec NOT ignored — OK"
git ls-files 05_icons/ | wc -l   # expect 6

# 5. LICENSE exists
test -f 08_legal/00_LICENSE && echo "A.4: LICENSE exists — OK"

# 6. AppStream validation
appstreamcli validate 04_data/00_org.ficus.Dashboard.metainfo.xml 2>&1 | grep -i error || echo "metainfo: OK"

# 7. Desktop file validation
desktop-file-validate /home/ficus-pro/Desktop/00_dashboard.desktop 2>&1 || echo "desktop: warnings OK"
```

- [ ] All 7 checks pass
- [ ] Record pass/fail counts

---

## Phase 18 — Commit & Push

```bash
git add -A
git status --short
git commit -m "fix: codebase refine — VCS, side effects, tests, packaging, docs"
git push -u origin feature/refine
```

- [ ] Commit message follows Conventional Commits (`fix:`)
- [ ] Branch pushed to `origin/feature/refine`
- [ ] **DO NOT merge** — await human review

---

## Blocking Decisions (cannot proceed without human input)

1. **`qt_overlay.py` architecture** — It IS wired up via `test_overlay.py` subprocess calls, but the comment in `00_main.py` says "The real screen-backed app is created lazily inside test_overlay.py" which is misleading. Should the comment be fixed (recommended), or should `qt_overlay.py` be replaced by an in-process implementation?

2. **`PROGRESS archive/` fate** — It's a complete separate project bundled inside DASHBOARD. It causes pytest collection risk, grep noise, and repo bloat. Options:
   - (a) Extract to its own repo (recommended but requires user action)
   - (b) Move to `vendor/PROGRESS-archive/` and add to `.gitignore`
   - (c) Leave as-is with a clear exclusion note in README

3. **Screenshot for AppStream** — The metainfo previously referenced a non-existent screenshot. We removed it. Should we:
   - (a) Keep it removed (clean, no false promises)
   - (b) Add a placeholder/generate a screenshot later

4. **Python version** — `pyproject.toml` says `>=3.10` but GTK4 + PyQt6 may have issues on 3.10. Should we bump to `>=3.11` to match AGENTS.md intent, or keep `>=3.10` for broader compatibility?

---

## Definition of Done

- [ ] All Phase 1–17 items verified and either fixed or explicitly deferred with reason
- [ ] `python3 -m py_compile 00_app/*.py` passes
- [ ] `timeout 3 python3 -c "..."` exits cleanly (no import-side-effect hang)
- [ ] `pytest 09_tests/ -v` — all tests pass
- [ ] `git ls-files 05_icons/` — 6 PNGs tracked
- [ ] `git ls-files 08_legal/` — `00_LICENSE` + `01_VERSION`
- [ ] `git check-ignore -v 01_build/00_dashboard.spec` — returns nothing
- [ ] `appstreamcli validate` — no errors
- [ ] `/home/ficus-pro/Desktop/00_dashboard.desktop` — valid, launches `dashboard`
- [ ] Branch pushed to `origin/feature/refine`
- [ ] Human review requested on 4 blocking decisions
