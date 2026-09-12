# SPDX-License-Identifier: GPL-3.0-or-later
"""Basic tests for the DASHBOARD window factory."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "00_app"))

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from _01_window import create_window


def test_window_creation():
    app = Gtk.Application(application_id="org.ficus.Dashboard.Test")
    win = create_window(app)
    assert win.get_title() == "DASHBOARD"
    assert win.get_default_size() == (400, 300)
