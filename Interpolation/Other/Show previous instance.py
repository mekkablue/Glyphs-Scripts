#MenuTitle: Show Previous Instance
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Jumps to previous instance shown in the preview field or window.
"""

from Foundation import NSApplication

numberOfInstances = len( Glyphs.font.instances )
Doc = Glyphs.currentDocument

# Preview Area at the bottom of Edit view:
PreviewField = Doc.windowController().activeEditViewController()

# Window > Preview Panel:
PreviewPanel = None

for p in NSApplication.sharedApplication().delegate().valueForKey_("pluginInstances"):
	if p.__class__.__name__ == "NSKVONotifying_GlyphsPreviewPanel":
		PreviewPanel = p

try:
	currentInstanceNumber = PreviewField.selectedInstance()

	if currentInstanceNumber > -2:
		PreviewField.setSelectedInstance_( currentInstanceNumber - 1 )
		if PreviewPanel:
			PreviewPanel.setSelectedInstance_( currentInstanceNumber - 1 )
	else:
		PreviewField.setSelectedInstance_( numberOfInstances - 1 )
		if PreviewPanel:
			PreviewPanel.setSelectedInstance_( numberOfInstances - 1 )
			
	# trigger update interface notification (so palettes and views can redraw):
	NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", Doc)

except Exception, e:
	print "Error:", e
