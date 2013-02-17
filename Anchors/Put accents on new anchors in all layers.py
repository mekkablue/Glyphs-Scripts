#MenuTitle: Put accent on new anchor in all layers
"""Puts e.g. the 'acute' on 'top_viet' in all layers."""

accent_name = "acute"
new_anchor = "top_viet"

import GlyphsApp

#Font = Glyphs.orderedDocuments()[0].font
Doc  = Glyphs.currentDocument
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

def Fontmasters( font=Glyphs.orderedDocuments()[0].font ):
	"""Return a list of fontmasters"""
	returnList = []
	masterIndex = 0
	controlValue = True
	
	while controlValue == True:
		fontmaster = font.masters[ masterIndex ]
		if fontmaster == None:
			returnList.append( fontmaster )
		else:
			controlValue = False
			
	return returnList

def process( thisGlyph ):
	for thisMaster in Fontmasters(): # error: cannot call Font.masters[:] :-(
		thisLayerIndex = thisMaster.id
		thisLayer = thisGlyph.layers[ thisLayerIndex ]
		for thisComponentIndex in range( len( thisLayer.components )):
			if thisLayer.components[ thisComponentIndex ].componentName == accent_name:
				# something along the line of:
				# E.g. if it's the acute, then hang it on the top_viet anchor of the previous component.
				thisLayer.components[ thisComponentIndex ].setAnchor_( thisLayer.components[ thisComponentIndex-1 ].component.layers[ thisLayerIndex ].anchors[ new_anchor ] )
				# but this doesn't work yet :-(

Font.willChangeValueForKey_("glyphs")

for thisGlyph in selectedGlyphs:
	print "Processing", thisGlyph.name
	process( thisGlyph )

Font.didChangeValueForKey_("glyphs")

