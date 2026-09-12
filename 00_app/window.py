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


def create_window(app: Gtk.Application) -> Gtk.ApplicationWindow:
    """
    Return a Gtk.ApplicationWindow with a "Toggle TEST Overlay" button.
    The button controls a transparent, always-on-top overlay that shows
    only the text "TEST" and can be dragged around the screen.
    """
    win = Gtk.ApplicationWindow(application=app)
    win.set_title("DASHBOARD")
    win.set_default_size(400, 300)
    win.set_icon_name("org.ficus.Dashboard")

    # Vertical box to centre the button
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.set_halign(Gtk.Align.CENTER)
    box.set_valign(Gtk.Align.CENTER)
    box.set_spacing(12)
    win.set_child(box)

    # Toggle button for the TEST overlay
    overlay_btn = Gtk.Button(label="Toggle TEST Overlay")
    overlay_btn.set_tooltip_text(
        "Show or hide a transparent, always-on-top overlay window displaying 'TEST'.\n"
        "The overlay can be dragged anywhere on the screen."
    )
    overlay_btn.connect("clicked", _on_toggle_clicked)

    box.append(overlay_btn)

    # Store a reference on the window so the overlay can be toggled later
    win._overlay: TestOverlayWindow | None = None  # type: ignore[attr-defined]

    return win


def _on_toggle_clicked(_btn: Gtk.Button) -> None:
    """
    Show or hide the TEST overlay window.
    Called when the toggle button is clicked.
    """
    app = Gtk.Application.get_default()
    if not isinstance(app, Gtk.ApplicationWindow.__mro__[0]):
        return

    # Find the window that owns this button (walk up the parent chain)
    win = _find_parent_window(_btn)
    if win is None:
        return

    if getattr(win, "_overlay", None) is None:
        # Create and position the overlay
        overlay = TestOverlayWindow()
        # Position near the top-right of the main window
        geo = win.get_geometry()
        if geo:
            x, y, _w, _h = geo
            display = win.get_display()
            n_screens = display.get_n_screens() if hasattr(display, 'get_n_screens') else 1
            if n_screens > 0:
                screen = display.get_screen()  # deprecated in newer GTK but still works
                mon = screen.get_monitor_at_window(win.get_window())
                rect = mon.get_geometry()
                overlay.move(rect.x + rect.width - 200, rect.y + 80)
            else:
                overlay.move(x + 420, y + 40)
        else:
            overlay.move(800, 100)
        overlay.show()
        win._overlay = overlay  # type: ignore[attr-defined]
    else:
        overlay = win._overlay  # type: ignore[attr-defined]
        if overlay.get_visible():
            overlay.hide()
        else:
            overlay.show()

    # Refresh the button label to reflect current state
    _update_button_label(_btn, win)


def _find_parent_window(widget: Gtk.Widget) -> Gtk.Window | None:
    """Walk up the widget parent chain to find the nearest Gtk.Window."""
    parent = widget.get_parent()
    while parent is not None:
        if isinstance(parent, Gtk.Window):
            return parent
        parent = parent.get_parent()
    return None


def _update_button_label(btn: Gtk.Button, win: Gtk.Window) -> None:
    """Update the toggle button label to reflect overlay visibility."""
    overlay: TestOverlayWindow | None = getattr(win, "_overlay", None)  # type: ignore[attr-defined]
    if overlay is not None and overlay.get_visible():
        btn.set_label("Hide TEST Overlay")
    else:
        btn.set_label("Toggle TEST Overlay")
