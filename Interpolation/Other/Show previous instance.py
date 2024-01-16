# MenuTitle: Show Previous Instance
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Jumps to previous instance shown in the preview field or window.
"""

from GlyphsApp import Glyphs

font = Glyphs.font
numberOfInstances = len(font.instances)

# Preview Area at the bottom of Edit view:
previewingTab = font.currentTab

# Window > Preview Panel:

previewPanel = Glyphs.delegate().pluginForClassName_("GlyphsPreviewPanel")

try:
	currentInstanceNumber = previewingTab.selectedInstance()
	if currentInstanceNumber > -2:
		newInstanceNumber = currentInstanceNumber - 1
	else:
		newInstanceNumber = numberOfInstances - 1

	previewingTab.setSelectedInstance_(newInstanceNumber)
	if previewPanel:
		previewPanel.setSelectedInstance_(newInstanceNumber)

except Exception as e:
	print("Error:", e)
	import traceback
	print(traceback.format_exc())
