#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
#
# DASHBOARD launcher installer.
#
# Generates the org.ficus.Dashboard.desktop launcher from the portable
# @PROJECT_DIR@ template, fills in the actual project location, installs
# the icons, and registers the app in the application menu — for the
# current user (default) or system-wide. Works on any Linux distribution.
#
# It does NOT install Python/GTK/Qt dependencies; those must be present
# (see README.md). The script only warns if it cannot find them.

set -euo pipefail

APP_ID="org.ficus.Dashboard"
DESKTOP_NAME="${APP_ID}.desktop"
METAINFO_NAME="${APP_ID}.metainfo.xml"
TEMPLATE_DESKTOP="00_dashboard.desktop"
WRAPPER="run-dashboard.sh"
ICON_SOURCE="05_icons/hicolor"
ROOT_PIXMAP_ICON="05_icons/dashboard-icon.png"

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename -- "$0")"

MODE="user"
PREFIX=""
DESKTOP_SHORTCUT="auto"
UNINSTALL=0
QUIET=0

msg() {
    [ "$QUIET" -eq 1 ] && return 0
    printf '%s\n' "$*"
}

warn() {
    printf '%s\n' "install.sh: warning: $*" >&2
}

die() {
    printf '%s\n' "install.sh: error: $*" >&2
    exit 1
}

usage() {
    cat <<USAGE
$SCRIPT_NAME - install the DASHBOARD launcher and icons

Usage: $SCRIPT_NAME [OPTIONS]

Registers the DASHBOARD application menu entry (org.ficus.Dashboard.desktop),
installs its icons and (optionally) drops a launcher on your desktop.
Does not require root unless you use --system.

Options:
  -u, --user          Install for the current user (~/.local) [default]
  -s, --system        Install system-wide (/usr/local; use with sudo)
      --prefix DIR    Install into DIR instead of the default prefix
  -d, --desktop       Force a launcher icon on the desktop
  -n, --no-desktop    Never create a desktop icon
      --uninstall     Remove the previously installed launcher and icons
  -q, --quiet         Suppress non-error output
  -h, --help          Show this help

Examples:
  ./$SCRIPT_NAME                 # install for the current user
  sudo ./$SCRIPT_NAME --system   # install for all users
  ./$SCRIPT_NAME --uninstall     # remove this user's launcher and icons
  ./$SCRIPT_NAME --user --no-desktop
USAGE
}

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            -u|--user)   MODE="user" ;;
            -s|--system) MODE="system" ;;
            --prefix)    [ $# -ge 2 ] || die "--prefix requires a directory"
                         PREFIX="$2"; shift ;;
            --prefix=*)  PREFIX="${1#--prefix=}" ;;
            -d|--desktop)    DESKTOP_SHORTCUT="yes" ;;
            -n|--no-desktop) DESKTOP_SHORTCUT="no" ;;
            --uninstall) UNINSTALL=1 ;;
            -q|--quiet)  QUIET=1 ;;
            -h|--help)   usage; exit 0 ;;
            *) die "unknown option: $1 (try --help)" ;;
        esac
        shift
    done

    [ -n "$PREFIX" ] && MODE="custom"

    case "$MODE" in
        user)   PREFIX="${HOME}/.local" ;;
        system) PREFIX="/usr/local" ;;
    esac

    APPS_DIR="${PREFIX%/}/share/applications"
    ICONS_DIR="${PREFIX%/}/share/icons/hicolor"
    METAINFO_DIR="${PREFIX%/}/share/metainfo"
}

find_desktop_dir() {
    local d
    if command -v xdg-user-dir >/dev/null 2>&1; then
        d="$(xdg-user-dir DESKTOP 2>/dev/null || true)"
        if [ -n "$d" ] && [ -d "$d" ]; then
            printf '%s' "$d"
            return 0
        fi
    fi
    if [ -d "${HOME}/Desktop" ]; then
        printf '%s' "${HOME}/Desktop"
        return 0
    fi
    return 1
}

ensure_requirements() {
    local py
    py="$(command -v python3 || true)"
    if [ -z "$py" ]; then
        warn "python3 not found on PATH. DASHBOARD needs Python >= 3.10 with GTK4 (PyGObject) and PyQt6."
        return 0
    fi
    "$py" -c 'import gi' >/dev/null 2>&1 \
        || warn "python3 found but PyGObject (GTK) is not importable; install python3-gi / gir1.2-gtk-4.0 first."
    "$py" -c 'import PyQt6' >/dev/null 2>&1 \
        || warn "python3 found but PyQt6 is not importable; the TEST overlay needs PyQt6."
}

generate_desktop() {
    local src="$PROJECT_DIR/$TEMPLATE_DESKTOP"
    local out="$1"
    local line

    [ -f "$src" ] || die "launcher template not found: $src (run this script from the project directory)"

    while IFS= read -r line; do
        printf '%s\n' "${line//@PROJECT_DIR@/$PROJECT_DIR}"
    done < "$src" > "$out"
    chmod 644 "$out"
    msg "Generated launcher: $out"
}

install_icons() {
    local src_icons="$PROJECT_DIR/$ICON_SOURCE"
    if [ -d "$src_icons" ]; then
        mkdir -p "$ICONS_DIR"
        # Copy the hicolor theme tree (16x16..256x256 apps icons).
        cp -r "$src_icons/." "$ICONS_DIR/"
        msg "Installed icons to $ICONS_DIR"
    else
        warn "icon theme directory not found: $src_icons (skipping icon install)"
    fi
}

install_metainfo() {
    local src="$PROJECT_DIR/04_data/$METAINFO_NAME"
    if [ -f "$src" ]; then
        mkdir -p "$METAINFO_DIR"
        cp "$src" "$METAINFO_DIR/$METAINFO_NAME"
        chmod 644 "$METAINFO_DIR/$METAINFO_NAME"
    fi
}

refresh_caches() {
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -f -t "$ICONS_DIR" >/dev/null 2>&1 || true
    fi
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
    fi
}

install_desktop_shortcut() {
    [ "$DESKTOP_SHORTCUT" = "no" ] && return 0
    local desktop_dir
    desktop_dir="$(find_desktop_dir || true)"
    if [ "$DESKTOP_SHORTCUT" = "yes" ] && [ -z "$desktop_dir" ]; then
        warn "--desktop requested but no desktop directory found; skipping"
        return 0
    fi
    [ -z "$desktop_dir" ] && return 0
    if [ -d "$desktop_dir" ]; then
        cp "$APPS_DIR/$DESKTOP_NAME" "$desktop_dir/$DESKTOP_NAME"
        chmod +x "$desktop_dir/$DESKTOP_NAME"
        msg "Desktop shortcut: $desktop_dir/$DESKTOP_NAME"
    fi
}

do_install() {
    ensure_requirements
    generate_desktop "$APPS_DIR/$DESKTOP_NAME"
    install_icons
    install_metainfo
    refresh_caches
    install_desktop_shortcut
    msg ""
    msg "DASHBOARD installed ($MODE mode, prefix: $PREFIX)."
    msg "Launch it from your application menu or run: $(basename -- "$PROJECT_DIR")/run-dashboard.sh"
}

do_uninstall() {
    local removed=0
    rm -f "$APPS_DIR/$DESKTOP_NAME" && [ ! -e "$APPS_DIR/$DESKTOP_NAME" ] && removed=1
    rm -f "$METAINFO_DIR/$METAINFO_NAME"
    rm -f "$ICONS_DIR"/*/apps/"$APP_ID".png 2>/dev/null || true
    local desktop_dir
    desktop_dir="$(find_desktop_dir || true)"
    [ -n "$desktop_dir" ] && rm -f "$desktop_dir/$DESKTOP_NAME"
    refresh_caches
    [ "$removed" -eq 1 ] && msg "Removed $APPS_DIR/$DESKTOP_NAME and DASHBOARD icons."
    msg "DASHBOARD launcher uninstalled." || true
}

main() {
    parse_args "$@"

    [ -e "$PROJECT_DIR/$WRAPPER" ] \
        || die "run-dashboard.sh not found next to this script; run it from the project directory"

    if [ "$UNINSTALL" -eq 1 ]; then
        do_uninstall
        exit 0
    fi

    if [ "$MODE" = "system" ] && [ "$(id -u)" -ne 0 ]; then
        warn "system install writes to /usr/local; re-run as root: sudo $SCRIPT_NAME --system"
    fi

    mkdir -p "$APPS_DIR" || die "cannot create $APPS_DIR (run as root for system install?)"
    mkdir -p "$METAINFO_DIR" || true

    do_install
}

main "$@"