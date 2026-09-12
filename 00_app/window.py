# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – Window factory.
Creates the application window with a toggle button for the TEST overlay.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from test_overlay import TestOverlayWindow


# Module-level reference so the click handler can access the overlay
# without walking the widget tree.
_overlay: TestOverlayWindow | None = None


def create_window(app: Gtk.Application) -> Gtk.ApplicationWindow:
    """
    Return a Gtk.ApplicationWindow with a "Toggle TEST Overlay" button.
    Clicking the button creates (or hides) a transparent, always-on-top
    overlay that shows only the text "TEST".
    """
    win = Gtk.ApplicationWindow(application=app)
    win.set_title("DASHBOARD")
    win.set_default_size(400, 300)
    win.set_icon_name("org.ficus.Dashboard")

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.set_halign(Gtk.Align.CENTER)
    box.set_valign(Gtk.Align.CENTER)
    box.set_spacing(12)
    win.set_child(box)

    global _overlay

    overlay_btn = Gtk.Button(label="Toggle TEST Overlay")
    overlay_btn.set_tooltip_text(
        "Show or hide a transparent, always-on-top overlay window displaying 'TEST'.\n"
        "The overlay can be dragged anywhere on the screen."
    )
    overlay_btn.connect("clicked", _on_toggle_clicked)
    box.append(overlay_btn)

    return win


def _on_toggle_clicked(btn: Gtk.Button) -> None:
    """
    Show or hide the TEST overlay window.
    """
    global _overlay

    if _overlay is None:
        overlay = TestOverlayWindow()
        # Position near top-right of the primary screen
        monitor = _get_primary_monitor()
        if monitor:
            rect = monitor.get_geometry()
            overlay.move(rect.x + rect.width - 200, rect.y + 80)
        else:
            overlay.move(800, 100)
        overlay.show()
        _overlay = overlay
    else:
        _overlay.hide()
        _overlay = None

    _refresh_button_label(btn)


def _get_primary_monitor() -> Gtk.Monitor | None:
    """Return the primary GdkMonitor if available."""
    display = Gtk.Display.get_default()
    if display is None:
        return None
    n_monitors = display.get_n_monitors()
    if n_monitors > 0:
        return display.get_monitor(0)
    return None


def _refresh_button_label(btn: Gtk.Button) -> None:
    """Update the button label to reflect current overlay state."""
    if _overlay is not None and _overlay.get_visible():
        btn.set_label("Hide TEST Overlay")
    else:
        btn.set_label("Toggle TEST Overlay")
