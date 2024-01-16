# MenuTitle: Toggle Script Windows
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Toggles visibility of all windows and panels created by Python scripts.
"""

from GlyphsApp import Glyphs

scriptWindow = Glyphs.delegate().macroPanelController().window()

if scriptWindow:
	scriptWindow.setIsVisible_(not scriptWindow.isVisible())
