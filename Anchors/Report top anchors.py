#MenuTitle: Report top positions
"""Reports the y positions of the top anchors in selected glyphs."""

import GlyphsApp
myAnchor = "top"

Font = Glyphs.orderedDocuments()[0].font
Doc  = Glyphs.currentDocument
FontMaster = Doc.selectedFontMaster()
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

def process( thisGlyph ):
	thisLayer = thisGlyph.layers[FontMaster.id]

	thisGlyph.undoManager().disableUndoRegistration()

	try:
		myY = thisLayer.anchors[myAnchor].y
		print thisGlyph.name, "--->", myY
	except Exception, e:
		print thisGlyph.name, "has no %s anchor." % myAnchor

	thisGlyph.undoManager().enableUndoRegistration()

Font.willChangeValueForKey_("glyphs")

for thisGlyph in selectedGlyphs:
	process( thisGlyph )

Font.didChangeValueForKey_("glyphs")

