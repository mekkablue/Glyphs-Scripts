#MenuTitle: Align anchors to pixelgrid
"""Looks for anchors not on the grid and rounds their coordinate to the closest grid node."""

import GlyphsApp

Font = Glyphs.orderedDocuments()[0].font
Doc  = Glyphs.currentDocument
FontMaster = Doc.selectedFontMaster()
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

pixelwidth = 50.0

def process( thisGlyph ):
	thisLayer = thisGlyph.layers[FontMaster.id]
	
	if len( thisLayer.components ) != 0:
		thisGlyph.undoManager().disableUndoRegistration()
		
		l = thisLayer.anchors
		anchorList = [ {"name": l[x].name, "x": l[x].x, "y": l[x].y, "index": x} for x in range( len(l) ) ]
		for a in anchorList:
			xrest, yrest = ( a["x"] % pixelwidth ), ( a["y"] % pixelwidth )
			
			if xrest or yrest:
				thisLayer.anchors[a["index"]].x = ( round( a["x"]/pixelwidth ) * pixelwidth )
				thisLayer.anchors[a["index"]].y = ( round( a["y"]/pixelwidth ) * pixelwidth )
				print "%s: %s %i|%i --> %i|%i" % ( thisGlyph.name, a["name"], int(a["x"]), int(a["y"]), int(thisLayer.anchors[a["index"]].x), int(thisLayer.anchors[a["index"]].y) )
		
		thisGlyph.undoManager().enableUndoRegistration()


Font.willChangeValueForKey_("glyphs")

for thisGlyph in selectedGlyphs:
	process( thisGlyph )

Font.didChangeValueForKey_("glyphs")

