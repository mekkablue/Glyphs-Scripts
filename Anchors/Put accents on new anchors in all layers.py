#MenuTitle: Move acute, grave and hook to top_viet position in all layers
"""Puts acute, grave, hookabove on top_viet in all layers.
Assumes that you have a top_viet anchor in circumflex."""

accents_to_be_moved = [ "acute", "grave", "hookabovecomb" ]
new_anchor = "top_viet"

import GlyphsApp

Doc  = Glyphs.currentDocument
Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

def process( thisGlyph ):
	for thisMaster in Font.masters:
		
		print "__Master", thisMaster
		
		thisLayerID = thisMaster.id
		thisLayer = thisGlyph.layers[ thisLayerID ]
		
		for thisComponentIndex in range( len( thisLayer.components )):
			for accent_name in accents_to_be_moved:
				if thisLayer.components[ thisComponentIndex ].componentName == accent_name:
					# UNCOMMENT FOR DEBUGGING:
					# print "position:", thisLayer.components[ thisComponentIndex ].position
					# print "componentName:", thisLayer.components[ thisComponentIndex ].componentName
					# print "component:", thisLayer.components[ thisComponentIndex ].component
					# print "transform:", thisLayer.components[ thisComponentIndex ].transform
					# print "bounds:", thisLayer.components[ thisComponentIndex ].bounds
					# print "targetAnchor:", targetAnchor
					
					# CHECKING FOR AVAILABILITY OF TOP_VIET:
					# targetAnchor = thisLayer.components[ thisComponentIndex-1 ].component.layers[ thisLayerID ].anchors[ new_anchor ]

					try:
						thisLayer.components[ thisComponentIndex ].setAnchor_( new_anchor )
					except Exception, e:
						print e

Font.disableUpdateInterface()

for thisGlyph in selectedGlyphs:
	print "Processing", thisGlyph.name
	process( thisGlyph )

Font.enableUpdateInterface()
