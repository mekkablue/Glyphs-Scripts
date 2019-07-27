#MenuTitle: Show next instance
# -*- coding: utf-8 -*-
__doc__="""
Jumps to next instance shown in the preview field or window.
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

	if currentInstanceNumber < numberOfInstances - 1:
		PreviewField.setSelectedInstance_( currentInstanceNumber + 1 )
		if PreviewPanel:
			PreviewPanel.setSelectedInstance_( currentInstanceNumber + 1 )
	else:
		PreviewField.setSelectedInstance_( -2 )
		if PreviewPanel:
			PreviewPanel.setSelectedInstance_( -2 )
	
	# trigger update interface notification (so palettes and views can redraw):
	NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", Doc)

except Exception, e:
	print "Error:", e
