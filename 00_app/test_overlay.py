# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – Transparent TEST overlay window.

Creates a small translucent overlay showing only the text "TEST".
The overlay stays above other windows using Gdk.ToplevelState.ABOVE
and can be dragged by clicking and dragging.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk


class TestOverlayWindow(Gtk.Window):
    """
    A translucent overlay showing only "TEST".
    Uses Gdk.ToplevelState.ABOVE to stay above other windows
    and Gtk.GestureDrag for proper dragging.
    """

    def __init__(self) -> None:
        super().__init__()
        self.set_title("TEST Overlay")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_size_request(140, 60)

        # Translucent dark background via CSS
        provider = Gtk.CssProvider()
        provider.load_from_data(
            b"""
            .test-overlay-box {
                background-color: alpha(#0f172a, 0.7);
                border-radius: 8px;
            }
            .test-label {
                font-size: 28px;
                font-weight: bold;
                color: #60a5fa;
            }
            """
        )
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.add_css_class("test-overlay-box")
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        label = Gtk.Label(label="TEST")
        label.add_css_class("test-label")
        label.set_halign(Gtk.Align.CENTER)
        label.set_valign(Gtk.Align.CENTER)
        box.append(label)

        self.set_child(box)

        # Make window stay above others using GDK toplevel state
        self._setup_always_on_top()

        # Add drag support via Gtk.GestureDrag
        self._setup_drag_support()

    def _setup_always_on_top(self) -> None:
        """Configure window to stay above other windows."""
        # Set the ABOVE state flag on the window
        # This requests the compositor to keep the window above others
        self.set_state_flags(Gdk.ToplevelState.ABOVE)

        # Also set as modal to help with stacking
        try:
            native = self.get_native()
            if native and hasattr(native, 'get_surface'):
                surface = native.get_surface()
                if surface:
                    surface.set_modal(True)
        except Exception:
            pass

    def _setup_drag_support(self) -> None:
        """Add drag support for moving the window."""
        drag = Gtk.GestureDrag()
        drag.connect("drag-begin", self._on_drag_begin)
        drag.connect("drag-update", self._on_drag_update)
        drag.connect("drag-end", self._on_drag_end)
        self.add_controller(drag)

        click = Gtk.GestureClick()
        click.connect("pressed", self._on_click_pressed)
        self.add_controller(click)

    # ------------------------------------------------------------------ #
    #  Event Handlers                                                      #
    # ------------------------------------------------------------------ #

    def _on_drag_begin(self, gesture: Gtk.GestureDrag, x: float, y: float) -> None:
        """Start interactive window move using GDK surface begin_move."""
        try:
            native = self.get_native()
            if native and hasattr(native, 'get_surface'):
                surface = native.get_surface()
                if surface:
                    display = Gdk.Display.get_default()
                    if display:
                        seat = display.get_default_seat()
                        if seat:
                            pointer = seat.get_pointer()
                            if pointer:
                                timestamp = int(Gdk.CURRENT_TIME)
                                surface.begin_move(pointer, 1, x, y, timestamp)
        except Exception:
            pass

    def _on_drag_update(self, gesture: Gtk.GestureDrag, x: float, y: float) -> None:
        """Drag updates are handled by begin_move."""
        pass

    def _on_drag_end(self, gesture: Gtk.GestureDrag, x: float, y: float) -> None:
        """Clean up after drag ends."""
        pass

    def _on_click_pressed(self, gesture: Gtk.GestureClick, n_press: int, x: float, y: float) -> None:
        """Ensure window gets focus when clicked."""
        self.present()