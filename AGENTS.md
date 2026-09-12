# DASHBOARD — Agent Instructions

## Project Identity

| Field | Value |
|-------|-------|
| **Path** | `/home/ficus-pro/Documents/DASHBOARD` |
| **Branch** | `DASHBOARD-0.1v-linux-native` |
| **Remote** | `https://github.com/ficusai/DASHBOARD.git` |
| **License** | GPL-3.0-or-later |
| **Stack** | Python 3.11+, PyGObject, GTK4, PyQt6, PyInstaller, Flatpak |
| **Entry Point** | `00_app/00_main.py` |

---

## File Numbering Convention

All files are numbered `_00`–`_99` reflecting **runtime and build sequence**:

| Prefix | Purpose | Sequence |
|--------|---------|----------|
| `00_` | Application source (runtime) | `_00` = entry, `_99` = quit/close |
| `01_` | Build & packaging | Last manual step |
| `02_` | Desktop integration | Post-build install |
| `03_` | Git helpers | Repo setup |
| `04_` | AppStream & metadata | Software center config |
| `05_` | Application icons | Visual assets |
| `06_` | Flatpak packaging | Distribution manifest |
| `07_` | CI/CD | Automated releases |
| `08_` | Legal & licensing | Version & license files |
| `09_` | Tests | Validation suite |

**Rule:** `_00` is always the first thing executed at runtime. `_99` (or equivalent) is always the last — application quit or shutdown handler.

---

## Directory Map

| Folder | Contents |
|--------|----------|
| `00_app/` | Source code — one file per function, atomic design |
| `01_build/` | PyInstaller spec, requirements, build script |
| `02_desktop/` | `.desktop` launcher file |
| `03_git/` | Git initialization script |
| `04_data/` | AppStream metainfo, desktop entry (installed copy) |
| `05_icons/` | Hicolor icon theme at 16/32/48/64/128/256 px |
| `06_flatpak/` | Flatpak manifest (`*.yml`) |
| `07_ci/` | GitHub Actions workflow |
| `08_legal/` | LICENSE text, VERSION file |
| `09_tests/` | pytest test suite |

---

## Atomic Source Files — Hard Rule

**Every new function MUST go in its own dedicated file inside its own folder.**

- No grouping functions into shared or utility files.
- No multi-function modules.
- Each function = one file, one purpose-built directory.
- Applies to `00_app/` and any new source directories created during development.

---

## Code Conventions

- **License header** on every file:
  ```python
  # SPDX-License-Identifier: GPL-3.0-or-later
  # Copyright (C) 2026 ficus-pro
  ```
- **Primary toolkit: GTK4 / PyGObject.** PyQt6 is permitted for overlay functionality where GTK cannot provide native Wayland always-on-top behavior.
- **Type hints** required on all function signatures.
- **PEP 8** — follow standard Python formatting.
- **Numeric module names** (`00_main.py`, `01_window.py`) — use `importlib.import_module()` in tests, never `from _00_main import ...`.
- **No external dependencies** beyond `PyGObject>=3.44` unless explicitly approved.

---

## Commands

```bash
# Run application (dev)
python3 00_app/00_main.py

# Run tests
# Use Xvfb for headless GTK testing:
#   Xvfb :99 -screen 0 1024x768x24 &
#   DISPLAY=:99 QT_QPA_PLATFORM=offscreen GDK_BACKEND=x11 PYTHONPATH=00_app pytest 09_tests/ -v

# Compile / syntax check
python3 -m py_compile $(find 00_app -name '*.py' -not -path '*__pycache__*')

# Build standalone executable
bash 01_build/01_build_executable.sh

# Clean build artefacts
rm -rf dist/ build/ __pycache__ .pytest_cache
```

---

## Git Workflow

```bash
# Feature branch (always create before editing)
git checkout -b feature/<feature-name>

# After each logical change
git add . && git commit -m "feat: <description>"

# Push feature branch
git push -u origin feature/<feature-name>

# Merge to release branch
git checkout DASHBOARD-0.1v-linux-native
git merge feature/<feature-name>
git push origin DASHBOARD-0.1v-linux-native
```

**Commit convention:** `feat:`, `fix:`, `docs:`, `chore:` (Conventional Commits).

**Branch documentation rule:** Before pushing any feature branch, update `README.md` with a `## Branch-Related File Changes` section listing every file added or modified.

---

## Restrictions

- **Never** commit `agents.json` or the master `AGENTS.md` — these belong to the parent workspace.
- **Never** modify `08_legal/01_VERSION` manually without a semantic version decision (MAJOR.MINOR.PATCH).
- **Never** install or reference packages from outside the Fedora repos or `pyproject.toml` dependencies.
- **Never** hard-code absolute paths in source code — use `pathlib.Path` relative to `__file__`.
- **Never** remove or rename numbered files in `00_app/` — the numbering encodes runtime order.
- **Always** run tests (`pytest`) before committing.
- **Always** update `CHANGELOG.md` for any user-facing change.

---

## Current State

- Version: `0.2.0`
- Status: GTK4 main window with PyQt6 TEST overlay (native Wayland always-on-top via Qt.WindowStaysOnTopHint)
- Remote: https://github.com/ficusai/DASHBOARD.git
- Tests: 5 passing (all `09_tests/` pass with `QT_QPA_PLATFORM=offscreen GDK_BACKEND=offscreen`)
