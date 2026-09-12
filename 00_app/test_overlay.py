# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – Transparent always-on-top TEST overlay window.

Creates a small draggable overlay that displays only the text "TEST".
The window has a translucent background, stays above all other windows,
and can be repositioned by clicking and dragging anywhere on it.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk

OVERLAY_CSS = """
.test-overlay {
    background-color: alpha(#0f172a, 0.85);
    color: #f8fafc;
}
.test-overlay label {
    font-size: 28px;
    font-weight: bold;
    color: #60a5fa;
}
"""


class TestOverlayWindow(Gtk.Window):
    """
    A transparent, always-on-top, draggable overlay showing only "TEST".
    """

    def __init__(self) -> None:
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("TEST Overlay")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_size_request(140, 60)

        # Keep above all other windows
        self.set_keep_above(True)

        # Stay out of the taskbar / alt-tab switcher
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

        # Utility-type hint helps keep it above normal windows on some WMs
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)

        # Translucent background
        self.set_opacity(0.92)

        # Apply CSS style
        provider = Gtk.CssProvider()
        provider.load_from_data(OVERLAY_CSS.encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        box.add_css_class("test-overlay")

        self.label = Gtk.Label(label="TEST")
        self.label.set_halign(Gtk.Align.CENTER)
        self.label.set_valign(Gtk.Align.CENTER)
        box.append(self.label)

        self.set_child(box)

        # Drag state
        self._dragging = False
        self._drag_offset_x = 0
        self._drag_offset_y = 0

        self.connect("button-press-event", self._on_button_press)
        self.connect("button-release-event", self._on_button_release)
        self.connect("motion-notify-event", self._on_motion_notify)

    # ------------------------------------------------------------------ #
    #  Drag handling                                                       #
    # ------------------------------------------------------------------ #

    def _on_button_press(self, _widget: Gtk.Widget, event: Gdk.Event) -> bool:
        """Start dragging when the left mouse button is pressed."""
        if event.get_button() == 1:
            self._dragging = True
            root_x, root_y = event.get_root()
            win_x, win_y = self.get_position()
            self._drag_offset_x = int(root_x) - win_x
            self._drag_offset_y = int(root_y) - win_y
        return True

    def _on_button_release(self, _widget: Gtk.Widget, _event: Gdk.Event) -> bool:
        """Stop dragging on mouse release."""
        self._dragging = False
        return True

    def _on_motion_notify(self, _widget: Gtk.Widget, event: Gdk.Event) -> bool:
        """Move the window while the mouse is held down."""
        if self._dragging:
            root_x, root_y = event.get_root()
            self.move(int(root_x) - self._drag_offset_x,
                      int(root_y) - self._drag_offset_y)
        return True
