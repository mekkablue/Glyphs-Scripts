#MenuTitle: Move acute, grave and hook to top_viet position in all layers
# -*- coding: utf-8 -*-
__doc__="""
Where possible, puts acute, grave, hookabove on 'top_viet' in all selected glyphs. Assumes that you have a 'top_viet' anchor in circumflex. Useful for Vietnamese glyphs.
"""

accentsToBeMoved = [ "acute", "grave", "hookabovecomb", "acutecomb", "gravecomb" ]
newAnchor = "top_viet"

import GlyphsApp

Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Font.selectedLayers ]

def baseHasAnchor( thisComponent, masterID, anchorToLookFor = "top_viet" ):
	baseGlyph = thisComponent.component
	baseLayer = baseGlyph.layers[masterID]
	baseAnchors = [a for a in baseLayer.anchors]
	anchorIsInLayer = False
	for i in range(len(baseAnchors)):
		if baseAnchors[i].name == anchorToLookFor:
			anchorIsInLayer = True
	return anchorIsInLayer

def nameUntilFirstDot( thisName ):
	return thisName[:thisName.find(".")]

def process( thisGlyph ):
	for thisMaster in Font.masters:
		thisLayerID = thisMaster.id
		thisLayer = thisGlyph.layers[ thisLayerID ]
		
		for thisComponentIndex in range( len( thisLayer.components ))[1:]:
			accentComponent = thisLayer.components[ thisComponentIndex ]
			accentName = nameUntilFirstDot( accentComponent.componentName )
			if accentName in accentsToBeMoved:
				baseComponent = thisLayer.components[ thisComponentIndex - 1 ]
				if baseComponent:
					if baseHasAnchor( baseComponent, thisLayerID, anchorToLookFor=newAnchor ):
						try:
							thisLayer.components[ thisComponentIndex ].setAnchor_( newAnchor )
						except Exception, e:
							print e

for thisGlyph in selectedGlyphs:
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisGlyph )
	thisGlyph.endUndo()

