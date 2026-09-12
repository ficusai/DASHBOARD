# Contributing to DASHBOARD

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

## Code Style

- Follow PEP 8
- Add SPDX license headers to every file
- Write tests for new functionality
- Update CHANGELOG.md for user-facing changes

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `chore:` for maintenance
