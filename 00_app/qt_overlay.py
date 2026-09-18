#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – Standalone PyQt6 TEST overlay process.

Launched by the main GTK app via subprocess when the overlay is toggled.
Runs as a singleton: subsequent invocations send commands to the running
instance instead of starting a new process.

Usage:
    python3 qt_overlay.py --show     # Show the overlay
    python3 qt_overlay.py --hide     # Hide the overlay
    python3 qt_overlay.py --toggle   # Toggle visibility
    python3 qt_overlay.py --visible  # Print "true" or "false" to stdout
"""

import argparse
import os
import socket
import sys
from pathlib import Path

from PyQt6.QtCore import QSocketNotifier, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QWidget,
)

# GNOME/Mutter on Wayland ignores WindowStaysOnTopHint and client-side
# window moves for native Wayland surfaces.  Running the overlay through
# XWayland (xcb) makes the compositor honour _NET_WM_STATE_ABOVE and system
# moves instead, so the overlay stays on top like a notification and can be
# repositioned by the user.  Honoured as a default only: an explicitly set
# QT_QPA_PLATFORM is respected.
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

SOCKET_PATH = Path.home() / ".local" / "share" / "dashboard-overlay.sock"


def _send_command(cmd: str) -> str | None:
    """Send a command to the running overlay instance via Unix socket."""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        try:
            sock.connect(str(SOCKET_PATH))
        except ConnectionRefusedError:
            return None
        sock.sendall((cmd + "\n").encode())
        try:
            data = sock.recv(4096)
            return data.decode().strip()
        except socket.timeout:
            return None
        finally:
            sock.close()
    except (FileNotFoundError, OSError):
        return None


class DraggableOverlay(QWidget):
    """Frameless, always-on-top, translucent overlay showing "TEST".

    Subclassing QWidget is required: PyQt6 virtual method overrides are
    only picked up from subclass methods, not from instance attributes
    assigned after construction.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setFixedSize(140, 60)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 23, 42, 180);
            }
            QLabel {
                color: #60a5fa;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Segoe UI', Ubuntu, sans-serif;
            }
        """)

        label = QLabel("TEST", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label)

        self._drag_offset: "QPoint | None" = None
        self._is_dragging = False

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(24, 24 + self.height())

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if not self._is_dragging or self._drag_offset is None:
            return
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            self._is_dragging = False
            self._drag_offset = None
            event.accept()
            return
        # Prefer the window-system move (compositor-driven): works on both
        # X11/XWayland (_NET_WM_MOVERESIZE) and Wayland (xdg move), and is the
        # only way to reposition a window on Wayland.  Falls back to a manual
        # move otherwise.
        handle = self.windowHandle()
        if handle is not None:
            try:
                if handle.startSystemMove():
                    self._is_dragging = False
                    self._drag_offset = None
                    event.accept()
                    return
            except Exception:
                pass
        self.move(event.globalPosition().toPoint() - self._drag_offset)
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            self._drag_offset = None
            event.accept()


class OverlayApp:
    """Singleton overlay daemon managed by a local Unix socket."""

    def __init__(self) -> None:
        self._app = QApplication([])
        self._overlay = DraggableOverlay()

        self._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Remove stale socket from a previous run.
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()

        self._server.bind(str(SOCKET_PATH))
        self._server.listen(16)
        self._server.setblocking(False)

        self._notifier = QSocketNotifier(
            self._server.fileno(), QSocketNotifier.Type.Read
        )
        self._notifier.activated.connect(self._on_socket_activated)

    def _on_socket_activated(self) -> None:
        """Accept all pending connections and process their commands."""
        while True:
            try:
                conn, _ = self._server.accept()
            except (BlockingIOError, OSError):
                break
            with conn:
                try:
                    data = conn.recv(4096)
                except (BlockingIOError, OSError):
                    data = b""
                if data:
                    cmd = data.decode().strip()
                    resp = self.handle_command(cmd)
                    try:
                        conn.sendall((resp + "\n").encode())
                    except OSError:
                        pass

    def handle_command(self, cmd: str) -> str:
        """Process a command and return the response."""
        if cmd == "show":
            self._overlay.show()
            self._overlay.raise_()
            self._overlay.activateWindow()
            return "shown"
        elif cmd == "hide":
            self._overlay.hide()
            return "hidden"
        elif cmd == "toggle":
            if self._overlay.isVisible():
                self._overlay.hide()
                return "hidden"
            self._overlay.show()
            self._overlay.raise_()
            self._overlay.activateWindow()
            return "shown"
        elif cmd == "visible":
            return "true" if self._overlay.isVisible() else "false"
        return "unknown command"

    def run(self) -> int:
        """Run the Qt event loop, processing socket commands as they arrive."""
        return self._app.exec()


def main() -> int:
    parser = argparse.ArgumentParser(description="DASHBOARD TEST overlay (standalone)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--show", action="store_true", help="Show the overlay")
    group.add_argument("--hide", action="store_true", help="Hide the overlay")
    group.add_argument("--toggle", action="store_true", help="Toggle overlay visibility")
    group.add_argument("--visible", action="store_true", help="Print true/false to stdout")
    args = parser.parse_args()

    # Query-only: never start a daemon, just report current state.
    if args.visible:
        resp = _send_command("visible")
        print(resp if resp is not None else "false")
        return 0

    # Action commands: try the existing instance first, fall back to starting one.
    cmd = "show" if args.show else "hide" if args.hide else "toggle"
    resp = _send_command(cmd)
    if resp is not None:
        print(resp)
        return 0

    # No running instance — start the daemon and apply the command.
    overlay = OverlayApp()
    response = overlay.handle_command(cmd)
    print(response)
    return overlay.run()


if __name__ == "__main__":
    sys.exit(main())