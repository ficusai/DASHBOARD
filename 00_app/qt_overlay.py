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
import select
import socket
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

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


class OverlayApp:
    """Singleton overlay window managed by a local Unix socket."""

    def __init__(self) -> None:
        self._app = QApplication([])
        self._widget: QWidget | None = None
        self._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Remove stale socket from previous run
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()

        self._server.bind(str(SOCKET_PATH))
        self._server.listen(1)
        self._server.setblocking(False)

    def _get_widget(self) -> QWidget:
        if self._widget is None:
            widget = QWidget()
            widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
            widget.setWindowFlags(
                Qt.WindowType.Window
                | Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.Tool
            )
            widget.setFixedSize(140, 60)
            widget.setCursor(Qt.CursorShape.SizeAllCursor)
            widget.setStyleSheet("""
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
            label = QLabel("TEST", widget)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay = QVBoxLayout(widget)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(label)

            # Drag support
            self._drag_offset = None
            self._is_dragging = False

            def mousePressEvent(event):
                if event.button() == Qt.MouseButton.LeftButton:
                    self._is_dragging = True
                    self._drag_offset = event.globalPosition().toPoint() - widget.pos()
                    event.accept()

            def mouseMoveEvent(event):
                if self._is_dragging and self._drag_offset is not None:
                    if event.buttons() & Qt.MouseButton.LeftButton:
                        widget.move(event.globalPosition().toPoint() - self._drag_offset)
                        event.accept()
                        return

            def mouseReleaseEvent(event):
                if event.button() == Qt.MouseButton.LeftButton:
                    self._is_dragging = False
                    self._drag_offset = None
                    event.accept()

            widget.mousePressEvent = mousePressEvent
            widget.mouseMoveEvent = mouseMoveEvent
            widget.mouseReleaseEvent = mouseReleaseEvent

            # Position at top-left
            screen = QApplication.primaryScreen().availableGeometry()
            widget.move(24, 24 + widget.height())

            self._widget = widget
        return self._widget

    def handle_command(self, cmd: str) -> str:
        """Process a command and return the response."""
        if cmd == "show":
            w = self._get_widget()
            w.show()
            w.raise_()
            w.activateWindow()
            return "shown"
        elif cmd == "hide":
            w = self._get_widget()
            if w is not None:
                w.hide()
            return "hidden"
        elif cmd == "toggle":
            w = self._get_widget()
            if w is not None and w.isVisible():
                w.hide()
                return "hidden"
            else:
                w = self._get_widget()
                w.show()
                w.raise_()
                w.activateWindow()
                return "shown"
        elif cmd == "visible":
            w = self._get_widget()
            return "true" if (w is not None and w.isVisible()) else "false"
        return "unknown command"

    def run(self) -> int:
        """Run the overlay event loop, processing socket commands."""
        while True:
            # Check for incoming connections / data
            readable, _, _ = select.select([self._server], [], [], 0.1)
            if readable:
                try:
                    conn, _ = self._server.accept()
                    with conn:
                        data = conn.recv(4096)
                        if data:
                            cmd = data.decode().strip()
                            resp = self.handle_command(cmd)
                            conn.sendall((resp + "\n").encode())
                except OSError:
                    pass

            # Process Qt events
            QApplication.processEvents()


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

    # Action commands: try existing instance first, fall back to starting one.
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
