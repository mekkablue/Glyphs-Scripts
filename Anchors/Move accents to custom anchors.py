#MenuTitle: Move marks to custom anchors in all masters
"""Moves acute(.case) from 'top' to 'top_acute' anchors where available. And other accents likewise."""

import GlyphsApp

Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Font.selectedLayers ]

def customAnchorName( currentAnchorName, componentName ):
	pureAnchorName = currentAnchorName.split("_")[0]
	pureComponentName = componentName.split(".")[0]
	return "%s_%s" % ( pureAnchorName, pureComponentName )

def process( thisGlyph ):
	for thisMasterID in [ m.id for m in Font.masters ]:
		thisLayer = thisGlyph.layers[ thisMasterID ]
		
		for thisComponentIndex in range( len( thisLayer.components ))[1:]:
			thisComponent = thisLayer.components[ thisComponentIndex ]
			componentGlyph = thisComponent.component
			componentLayer = componentGlyph.layers[ thisMasterID ]
			componentAnchorName = [ a.name for a in componentLayer.anchors if a.name[0] == "_" ][0][1:]
			
			try:
				newAnchorName = customAnchorName( componentAnchorName, thisComponent.componentName )
				thisComponent.setAnchor_( newAnchorName )
			except Exception, e:
				print e

for thisGlyph in selectedGlyphs:
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisGlyph )
	thisGlyph.endUndo()

