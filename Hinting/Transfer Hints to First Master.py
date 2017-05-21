#MenuTitle: Transfer Hints to First Master
# -*- coding: utf-8 -*-
__doc__="""
Moves PostScript (stem and ghost) hints from the current layer to the first master layer, provided the paths are compatible.
"""

from GlyphsApp import TOPGHOST, BOTTOMGHOST, STEM

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
firstMaster = thisFont.masters[0]
firstMasterId = firstMaster.id
supportedHintTypes = (TOPGHOST, BOTTOMGHOST, STEM)

def deleteHintsOnLayer(thisLayer):
	for i in range(len(thisLayer.hints))[::-1]:
		if thisLayer.hints[i].type in supportedHintTypes:
			del thisLayer.hints[i]

def transferHintsFromTo( sourceLayer, targetLayer ):
	# empty put targetLayer's hints:
	deleteHintsOnLayer(targetLayer)
	for thisHint in sourceLayer.hints:
		if thisHint.type in supportedHintTypes and thisHint.originNode:
			pathIndex = sourceLayer.paths.index(thisHint.originNode.parent)
			originNodeIndex = thisHint.originNode.index
			newHint = GSHint()
			newHint.type = thisHint.type
			newHint.originNode = targetLayer.paths[pathIndex].nodes[originNodeIndex]
			if thisHint.targetNode:
				# stem hint has target node:
				targetNodeIndex = thisHint.targetNode.index
				targetPathIndex = sourceLayer.paths.index(thisHint.targetNode.parent)
				newHint.targetNode = targetLayer.paths[targetPathIndex].nodes[targetNodeIndex]
				newHint.horizontal = thisHint.horizontal
			targetLayer.hints.append(newHint)
	deleteHintsOnLayer(sourceLayer)

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

# brings macro window to front and clears its log:
Glyphs.clearLog()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	if thisLayer.layerId != firstMasterId:
		firstLayer = thisGlyph.layers[firstMasterId]
		if thisGlyph.mastersCompatibleForLayers_([thisLayer,firstLayer]):
			print "Transfering hints in: %s" % thisGlyph.name
			thisGlyph.beginUndo() # begin undo grouping
			transferHintsFromTo( thisLayer, firstLayer )
			thisGlyph.endUndo()   # end undo grouping
		else:
			Glyphs.showMacroWindow()
			print "%s: layers incompatible." % thisGlyph.name
	else:
		Glyphs.showMacroWindow()
		print "%s: layer '%s' is already the first master layer." % (thisGlyph.name,thisLayer.name)

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
