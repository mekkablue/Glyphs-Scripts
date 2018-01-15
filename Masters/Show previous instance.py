#MenuTitle: Show previous instance
# -*- coding: utf-8 -*-
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

except Exception, e:
	print "Error:", e
