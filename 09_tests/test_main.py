# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for the DASHBOARD application entry point."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "00_app"))


def test_main_module_exists():
    import importlib
    mod = importlib.import_module("00_main")
    assert hasattr(mod, "main")
    assert callable(mod.main)
