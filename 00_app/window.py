# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – Window factory.
Creates the application window with a toggle button for the TEST overlay.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import test_overlay


def create_window(app: Gtk.Application) -> Gtk.ApplicationWindow:
    """
    Return a Gtk.ApplicationWindow with a "Toggle TEST Overlay" button.
    Clicking the button creates (or toggles) a translucent overlay window
    displaying only the text "TEST".
    The overlay uses PyQt6's Qt.WindowStaysOnTopHint, which works
    reliably on Wayland where GTK4's Gdk.ToplevelState.ABOVE is ignored.
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

    overlay_btn = Gtk.Button(label="Toggle TEST Overlay")
    overlay_btn.set_tooltip_text(
        "Show or hide a transparent overlay window displaying 'TEST'.\n"
        "The overlay stays on top of all other windows (Wayland-native)."
    )
    overlay_btn.connect("clicked", _on_toggle_clicked)
    box.append(overlay_btn)

    return win


def _on_toggle_clicked(btn: Gtk.Button) -> None:
    """Show or hide the TEST overlay window."""
    if test_overlay.is_overlay_visible():
        test_overlay.hide_overlay()
    else:
        test_overlay.show_overlay()
    _refresh_button_label(btn)


def _refresh_button_label(btn: Gtk.Button) -> None:
    """Update the button label to reflect overlay visibility."""
    if test_overlay.is_overlay_visible():
        btn.set_label("Hide TEST Overlay")
    else:
        btn.set_label("Toggle TEST Overlay")
