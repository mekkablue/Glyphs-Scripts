from __future__ import print_function
#MenuTitle: Transfer Hints to First Master
# -*- coding: utf-8 -*-
__doc__="""
Moves PostScript (stem and ghost) hints from the current layer to the first master layer, provided the paths are compatible.
"""

from GlyphsApp import TOPGHOST, BOTTOMGHOST, STEM, TTANCHOR, TTSTEM, TTALIGN, TTINTERPOLATE, TTDIAGONAL, TTDELTA

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
firstMaster = thisFont.masters[0]
firstMasterId = firstMaster.id
supportedHintTypes = (TOPGHOST, BOTTOMGHOST, STEM, TTANCHOR, TTSTEM, TTALIGN, TTINTERPOLATE, TTDIAGONAL, TTDELTA, )

def deleteHintsOnLayer(thisLayer):
	for i in range(len(thisLayer.hints))[::-1]:
		if thisLayer.hints[i].type in supportedHintTypes:
			del thisLayer.hints[i]

def transferHintsFromTo( sourceLayer, targetLayer ):
	# clean slate in targetLayer:
	deleteHintsOnLayer(targetLayer)
	
	# go through all hints in source layer:
	for thisHint in sourceLayer.hints:
		
		# if it is a recognized hint type...
		if thisHint.type in supportedHintTypes and thisHint.originNode:
			
			# ... create hint for target layer:
			pathIndex = sourceLayer.paths.index(thisHint.originNode.parent)
			originNodeIndex = thisHint.originNode.index
			newHint = GSHint()
			newHint.type = thisHint.type
			newHint.originNode = targetLayer.paths[pathIndex].nodes[originNodeIndex]
			newHint.horizontal = thisHint.horizontal
			
			# ... look for optional nodes:
			if thisHint.targetNode:
				targetNodeIndex = thisHint.targetNode.index
				targetPathIndex = sourceLayer.paths.index(thisHint.targetNode.parent)
				newHint.targetNode = targetLayer.paths[targetPathIndex].nodes[targetNodeIndex]
				
			if thisHint.otherNode1:
				targetNodeIndex = thisHint.otherNode1.index
				targetPathIndex = sourceLayer.paths.index(thisHint.otherNode1.parent)
				newHint.otherNode1 = targetLayer.paths[targetPathIndex].nodes[targetNodeIndex]
				
			if thisHint.otherNode2:
				targetNodeIndex = thisHint.otherNode2.index
				targetPathIndex = sourceLayer.paths.index(thisHint.otherNode2.parent)
				newHint.otherNode2 = targetLayer.paths[targetPathIndex].nodes[targetNodeIndex]
			
			# ... and add to target layer:
			targetLayer.hints.append(newHint)
		
	# ... delete hints in source layer:
	deleteHintsOnLayer(sourceLayer)

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

# brings macro window to front and clears its log:
Glyphs.clearLog()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	if thisLayer.layerId != firstMasterId:
		firstLayer = thisGlyph.layers[firstMasterId]
		if thisGlyph.mastersCompatibleForLayers_([thisLayer,firstLayer]):
			print("Transfering hints in: %s" % thisGlyph.name)
			thisGlyph.beginUndo() # begin undo grouping
			transferHintsFromTo( thisLayer, firstLayer )
			thisGlyph.endUndo()   # end undo grouping
		else:
			Glyphs.showMacroWindow()
			print("%s: layers incompatible." % thisGlyph.name)
	else:
		Glyphs.showMacroWindow()
		print("%s: layer '%s' is already the first master layer." % (thisGlyph.name,thisLayer.name))

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
