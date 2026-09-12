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

### Changed
- Improved window.py tooltip to be more accurate
- Enhanced test_overlay.py with xprop-based always-on-top:
  * Added `_set_window_above()` function using xprop to set _NET_WM_STATE_ABOVE
  * This is needed because GNOME Shell 50.4 does not honor Gdk.ToplevelState.ABOVE
  * Run with GDK_BACKEND=x11 for best results (similar to PROGRESS's QT_QPA_PLATFORM=xcb)
  * Implemented proper dragging using GDK surface begin_move() method
  * Added click-to-focus behavior
- Updated documentation

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