#!/usr/bin/env bash
# Initialise local Git repository for DASHBOARD.
set -euo pipefail

cd /home/ficus-pro/Documents/DASHBOARD

git init

cat > .gitignore << 'EOF'
# Build artefacts
dist/
build/
*.spec
__pycache__/
*.py[cod]
*.egg-info/

# Virtual environments
venv/
.venv/

# IDE
.vscode/
.idea/

# Fedora / GNOME
*.desktop.bak
*.png
!05_icons/

# Runtime data
04_data/ram_data.db
04_data/plugins/
EOF

git add .
git commit -m "Initial commit: minimal GTK4 window application"

git status
