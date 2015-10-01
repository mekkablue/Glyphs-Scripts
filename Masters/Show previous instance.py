#MenuTitle: Show previous instance
# -*- coding: utf-8 -*-
__doc__="""
Jumps to previous instance shown in the preview field or window.
"""

import GlyphsApp
from Foundation import NSApplication

numberOfInstances = len( Glyphs.font.instances )
Doc = Glyphs.currentDocument
PreviewField = Doc.windowController().activeEditViewController()
PreviewPanel = None

for p in NSApplication.sharedApplication().delegate().valueForKey_("pluginInstances"):
	if p.__class__.__name__ == "NSKVONotifying_GlyphsPreviewPanel":
		PreviewPanel = p

try:
	currentInstanceNumber = PreviewField.selectedInstance()

	if currentInstanceNumber > 1:
		PreviewField.setSelectedInstance_( currentInstanceNumber - 1 )
		if PreviewPanel:
			PreviewPanel.setSelectedInstance_( currentInstanceNumber - 1 )
	else:
		PreviewField.setSelectedInstance_( numberOfInstances )
		if PreviewPanel:
			PreviewPanel.setSelectedInstance_( numberOfInstances )

except Exception, e:
	print "Error:", e
