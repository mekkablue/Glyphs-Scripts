#MenuTitle: Close All Tabs of All Open Fonts
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Closes all Edit tabs of all fonts currently open in the app.
"""

closedTabCount = 0
for thisFont in Glyphs.fonts:
	while thisFont.tabs:
		thisFont.tabs[0].close()
		closedTabCount += 1

# Floating notification:
Glyphs.showNotification(
	"No more tabs open",
	"%i tab%s closed in %i font%s." % (
		closedTabCount,
		"" if closedTabCount == 1 else "s",
		len(Glyphs.fonts),
		"" if len(Glyphs.fonts) == 1 else "s",
		),
	)
