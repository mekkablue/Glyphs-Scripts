# MenuTitle: Update Text Preview
# -*- coding: utf-8 -*-

__doc__ = """
Force-updates the font shown in Window > Text Preview.
"""

from GlyphsApp import PreviewTextWindow

PreviewTextWindow.defaultInstance().reloadFont()
