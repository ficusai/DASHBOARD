# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Transparent always-on-top TEST overlay window (`test_overlay.py`)
- Toggle button in main window to show/hide the TEST overlay
- Overlay is draggable by clicking and holding anywhere on it
- Overlay stays above all other windows and skips taskbar/alt-tab

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
