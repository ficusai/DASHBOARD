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
- Improved window.py toggle button tooltip to be more accurate
- Enhanced test_overlay.py with better window behavior attempts:
  * Added GDK surface-based always-on-top attempts (modal state, ABOVE state hints)
  * Implemented proper dragging using GDK surface begin_move() method
  * Added click-to-focus support

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