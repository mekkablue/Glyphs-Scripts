#MenuTitle: Toggle Script Windows
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Toggles visibility of all windows and panels created by Python scripts.
"""

scriptWindows = [
	w for w in Glyphs.windows()
	if w.isMovable() 
	and w.isMiniaturizable() 
	and not w.document() 
	and w.isFloatingPanel() 
	and w.title() != "Compare Fonts"
	]

if scriptWindows:
	visible = not scriptWindows[0].isVisible()
	for w in scriptWindows:
		w.setIsVisible_(visible)
