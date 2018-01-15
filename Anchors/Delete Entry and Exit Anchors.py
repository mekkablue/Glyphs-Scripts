#MenuTitle: Delete Entry and Exit Anchors
# -*- coding: utf-8 -*-
__doc__="""
Deletes all entry and exit anchors (for the curs feature) in the selected glyphs.
"""



thisFont = Glyphs.font # frontmost font
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def process( thisLayer ):
	anchorsToBeDeleted = [ a for a in thisLayer.anchors if a.name.startswith("exit_") or a.name.startswith("entry_") or a.name in ("exit", "entry") ]
	if anchorsToBeDeleted:
		print "  Deleting: %s" % ( ", ".join([a.name for a in anchorsToBeDeleted]) )
		for thisAnchor in anchorsToBeDeleted:
			thisLayer.removeAnchor_(thisAnchor)

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	process( thisLayer )
