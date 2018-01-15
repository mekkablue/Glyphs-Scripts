#MenuTitle: Sync Components Across Masters
# -*- coding: utf-8 -*-
__doc__="""
Takes the current layer’s components, and resets all other masters to the same component structure. Ignores paths and anchors.
"""



thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def baseHasAnchor( thisComponent, masterID, anchorToLookFor ):
	baseGlyph = thisComponent.component
	baseLayer = baseGlyph.layers[masterID]
	baseAnchors = [a for a in baseLayer.anchors]
	anchorIsInLayer = False
	for i in range(len(baseAnchors)):
		if baseAnchors[i].name == anchorToLookFor:
			anchorIsInLayer = True
	return anchorIsInLayer

def process( thisLayer ):
	thisGlyph = thisLayer.parent
	compSet = thisLayer.componentNames()
	
	# only act if components are present:
	if compSet: 
		
		# see if there are special anchors (e.g., top_1, top_2, etc.) the components are attached to:
		componentAnchors = [ None ]
		numberOfComponents = len(compSet)
		for i in range( 1, numberOfComponents ):
			thisAnchor =  thisLayer.components[i].anchor
			componentAnchors.append( thisAnchor )
	
		# go through all other layers:
		for thatLayer in thisGlyph.layers:
			if thatLayer != thisLayer: # don't sync the layer with itself
				thatLayerID = thatLayer.layerId
				if thatLayerID == thatLayer.associatedMasterId: # only sync master layers
					thatLayer.setComponentNames_( compSet ) # sync components
					
					# try to attach the newly synced components to the right anchors:
					if len(thatLayer.components) == numberOfComponents:
						baseComponent = thatLayer.components[0]
						for i in range( 1, numberOfComponents ):
							thisAnchor = componentAnchors[i]
							if thisAnchor:
								if baseHasAnchor( baseComponent, thatLayerID, thisAnchor ):
									thatComponent = thatLayer.components[i]
									thatComponent.setAnchor_( thisAnchor )

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
