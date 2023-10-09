#MenuTitle: Show Next Instance
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Jumps to next instance shown in the preview field or window.
"""

from Foundation import NSApplication

font = Glyphs.font
numberOfInstances = len(font.instances)

# Preview Area at the bottom of Edit view:
previewingTab = font.currentTab

# Window > Preview Panel:
previewPanel = Glyphs.delegate().pluginForClassName_("GlyphsPreviewPanel")

try:
	currentInstanceNumber = previewingTab.selectedInstance()
	if currentInstanceNumber < numberOfInstances - 1:
		newInstanceNumber = currentInstanceNumber + 1
	else:
		newInstanceNumber = -2

	previewingTab.setSelectedInstance_(newInstanceNumber)
	if previewPanel:
		previewPanel.setSelectedInstance_(newInstanceNumber)

except Exception as e:
	print("Error:", e)
	import traceback
	print(traceback.format_exc())
