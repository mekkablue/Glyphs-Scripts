#MenuTitle: Show previous instance
# -*- coding: utf-8 -*-
__doc__="""
Jumps to previous instance shown in the preview field or window.
"""

import GlyphsApp
from Foundation import NSApplication
PreviewPanel = None
Doc = Glyphs.currentDocument
numberOfInstances = len( Glyphs.font.instances )

for p in NSApplication.sharedApplication().delegate().valueForKey_("pluginInstances"):
	if p.__class__.__name__ == "NSKVONotifying_GlyphsPreviewPanel":
		PreviewPanel = p

try:
	if PreviewPanel:
		currentInstanceNumber = PreviewPanel.selectedInstance()

		if currentInstanceNumber > 1:
			PreviewPanel.setSelectedInstance_( currentInstanceNumber - 1 )
		else:
			PreviewPanel.setSelectedInstance_( numberOfInstances )
	else:
		currentInstanceNumber = Doc.windowController().activeEditViewController().selectedInstance()

		if currentInstanceNumber > 1:
			Doc.windowController().activeEditViewController().setSelectedInstance_( currentInstanceNumber - 1 )
		else:
			Doc.windowController().activeEditViewController().setSelectedInstance_( numberOfInstances )

except Exception, e:
	print "Error:", e
