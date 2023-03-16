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
previewPanel = None

for p in NSApplication.sharedApplication().delegate().valueForKey_("pluginInstances"):
	if "GlyphsPreviewPanel" in p.__class__.__name__:
		previewPanel = p
		break

try:
	currentInstanceNumber = previewingTab.selectedInstance()
	if currentInstanceNumber < numberOfInstances - 1:
		previewingTab.setSelectedInstance_( currentInstanceNumber + 1 )
		if previewPanel:
			previewPanel.setSelectedInstance_( currentInstanceNumber + 1 )
	else:
		previewingTab.setSelectedInstance_( -2 )
		if previewPanel:
			previewPanel.setSelectedInstance_( -2 )
	previewingTab.updatePreview()
	previewingTab.forceRedraw()

except Exception as e:
	print("Error:", e)
	import traceback
	print(traceback.format_exc())