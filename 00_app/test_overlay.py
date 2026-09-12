# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – Transparent TEST overlay window.

Creates a small translucent overlay showing only the text "TEST".
The overlay attempts to stay above other windows and can be dragged
by clicking and dragging (using GDK surface begin_move for proper dragging).
The window background is transparent (using RGBA visual) with a semi-transparent
dark backdrop for the text to ensure readability.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk


class TestOverlayWindow(Gtk.Window):
    """
    A translucent overlay showing only "TEST".
    Uses RGBA visual for transparent background and attempts to stay above
    other windows via GDK surface state. Drag support via GDK surface begin_move.
    """

    def __init__(self) -> None:
        super().__init__()
        self.set_title("TEST Overlay")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_size_request(140, 60)

        # Attempt to use RGBA visual for transparent background (required for
        # true transparency on compositing compositors like Wayland/X11 with compositor).
        try:
            screen = self.get_screen()
            rgba = screen.get_rgba_visual()
            if rgba is not None:
                self.set_visual(rgba)
        except Exception:
            # If we can't set RGBA visual, continue without it (window may not be
            # fully transparent, but we'll still try other transparency methods).
            pass

        # Translucent dark background for the text backdrop (semi-transparent)
        # and transparent window background (via RGBA visual + CSS).
        provider = Gtk.CssProvider()
        provider.load_from_data(
            b"""
            .test-overlay-window {
                background-color: transparent;
            }
            .test-overlay-box {
                background-color: alpha(#0f172a, 0.7);  /* 70% opacity dark blue */
                border-radius: 8px;
                padding: 10px;
            }
            .test-label {
                font-size: 28px;
                font-weight: bold;
                color: #60a5fa;  /* opaque blue */
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

        # Try to make window stay above others using GDK surface APIs
        self._setup_window_behavior()

        # Add drag support via GDK surface begin_move (proper window dragging)
        self._setup_drag_support()

    def _setup_window_behavior(self) -> None:
        """Configure window to stay above other windows where possible."""
        try:
            # Get the GDK surface to access lower-level window properties
            native = self.get_native()
            if native and hasattr(native, 'get_surface'):
                surface = native.get_surface()
                if surface:
                    # Try to set modal (often helps with stacking/focus)
                    try:
                        surface.set_modal(True)
                    except Exception:
                        pass
                    
                    # Try to set state to ABOVE if the property is writable
                    # In some GTK4 builds, state might be writable via props
                    if hasattr(surface, 'props') and hasattr(surface.props, 'state'):
                        try:
                            # Only try if it seems writable (we'll catch exceptions)
                            current_state = surface.get_state()
                            new_state = current_state | Gdk.ToplevelState.ABOVE
                            surface.props.state = new_state
                        except Exception:
                            pass  # Property is read-only or not supported
                    
                    # Try direct state setting if method exists and is writable
                    if hasattr(surface, 'set_state'):
                        try:
                            current_state = surface.get_state()
                            new_state = current_state | Gdk.ToplevelState.ABOVE
                            surface.set_state(new_state)
                        except Exception:
                            pass  # Method might not exist or not be writable
                            
                    # Additional hints that might help with stacking
                    try:
                        surface.set_keep_above(True)  # Might exist in some builds
                    except Exception:
                        pass
                        
                    try:
                        surface.set_skip_taskbar_hint(True)
                    except Exception:
                        pass
                        
                    try:
                        surface.set_skip_pager_hint(True)
                    except Exception:
                        pass
        except Exception:
            # If anything fails, continue without special window behavior
            pass

    def _setup_drag_support(self) -> None:
        """Add drag support for moving the window using GDK surface begin_move."""
        # Create a gesture controller for dragging
        drag = Gtk.GestureDrag()
        drag.connect("drag-begin", self._on_drag_begin)
        drag.connect("drag-update", self._on_drag_update)
        drag.connect("drag-end", self._on_drag_end)
        self.add_controller(drag)

        # Also add click-to-focus behavior
        click = Gtk.GestureClick()
        click.connect("pressed", self._on_click_pressed)
        self.add_controller(click)

    # ------------------------------------------------------------------ #
    #  Event Handlers                                                      #
    # ------------------------------------------------------------------ #

    def _on_drag_begin(self, gesture: Gtk.GestureDrag, x: float, y: float) -> None:
        """Start interactive window move using GDK surface begin_move."""
        try:
            # Get the GDK surface and initiate a move operation
            native = self.get_native()
            if native and hasattr(native, 'get_surface'):
                surface = native.get_surface()
                if surface:
                    # Get the device and timestamp for begin_move
                    display = Gdk.Display.get_default()
                    if display:
                        seat = display.get_default_seat()
                        if seat:
                            pointer = seat.get_pointer()
                            if pointer:
                                # Get current timestamp
                                timestamp = int(Gdk.CURRENT_TIME)
                                # Begin the move operation
                                surface.begin_move(pointer, 1, x, y, timestamp)
                                return
        except Exception:
            # If anything fails, fall back to basic behavior (do nothing)
            pass
        # If we couldn't initiate the move, at least consume the gesture
        # to prevent interference with other handlers

    def _on_drag_update(self, gesture: Gtk.GestureDrag, x: float, y: float) -> None:
        """Drag updates are handled by the begin_move operation."""
        # The begin_move operation handles the actual movement
        # We just need to consume the event to prevent propagation
        pass

    def _on_drag_end(self, gesture: Gtk.GestureDrag, x: float, y: float) -> None:
        """Clean up after drag ends."""
        pass

    def _on_click_pressed(self, gesture: Gtk.GestureClick, n_press: int, x: float, y: float) -> None:
        """Ensure window gets focus when clicked."""
        self.present()