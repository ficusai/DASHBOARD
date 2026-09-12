# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Transparent TEST overlay window (`test_overlay.py`)
- Toggle button in main window to show/hide the TEST overlay
- Overlay is translucent and frameless
- Overlay can be shown/hidden via toggle button
- PyQt6-based overlay with native Wayland always-on-top support
- Drag support via Qt mouse events
- `show_overlay()` / `hide_overlay()` / `is_overlay_visible()` module API
- Qt event pump (`GLib.timeout_add`) for GTK+PyQt6 coexistence
- `09_tests/test_overlay_qt.py` — flag verification test

### Changed
- Replaced GTK4 `Gdk.ToplevelState.ABOVE` + xprop approach with PyQt6 `Qt.WindowStaysOnTopHint` (works natively on Wayland, no `GDK_BACKEND=x11` needed)
- GTK and PyQt6 now coexist in the same process; Qt is initialized before GTK
- Simplified `window.py` toggle logic to use module-level overlay API
- Updated tooltip and documentation to reflect Wayland-native behavior

## [0.1.0] - 2026-09-12

### Added
- Minimal GTK4 window with system close button only
- PyInstaller build configuration with GTK4 hook optimization
- AppStream metadata for software center listing
- Flatpak manifest for sandboxed distribution
- GitHub Actions CI/CD workflow for automated releases
- Application icons following Freedesktop Icon Theme Specification
- SPDX license headers (GPL-3.0-or-later)
- pytest test suite for window factory