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
	dotIndex = thisName.find(".")
	if dotIndex > 0:
		return thisName[:dotIndex]
	else:
		return thisName

def process( thisGlyph ):
	statusString = "Processing %s" % thisGlyph.name
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
							statusString += "\n   %s: Moved %s on %s." % ( thisLayer.name, accentName, newAnchor )
						except Exception, e:
							return "\nERROR in %s %s:\nCould not move %s onto %s.\n%s" % ( thisGlyph.name, thisLayer.name, accentName, newAnchor, e )
	return statusString

for thisGlyph in selectedGlyphs:
	thisGlyph.beginUndo()
	print process( thisGlyph )
	thisGlyph.endUndo()

