#MenuTitle: Sync Selection between Masters
# -*- coding: utf-8 -*-
__doc__="""
Tries to recreate, as much as possible, the current node/anchor/component selection in all other layers.
"""

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def syncSelectionFromLayer( thisLayer ):
	thisGlyph = thisLayer.parent
	otherLayers = [l for l in thisGlyph.layers if l != thisLayer]
	
	for otherLayer in otherLayers:
		otherLayer.selection = None
	
	for i,thisPath in enumerate(thisLayer.paths):
		for j,thisNode in enumerate(thisPath.nodes):
			if thisNode.selected:
				for otherLayer in otherLayers:
					try:
						otherLayer.selection.append(otherLayer.paths[i].nodes[j])
					except:
						pass
						
	for i,thisComponent in enumerate(thisLayer.components):
		print i
		if thisComponent in Layer.selection:
			for otherLayer in otherLayers:
				try:
					otherLayer.selection.append(otherLayer.components[i])
				except:
					pass
					
	for thisAnchor in thisLayer.anchors:
		if thisAnchor.selected:
			for otherLayer in otherLayers:
				try:
					otherLayer.selection.append(otherLayer.anchors[thisAnchor.name])
				except:
					pass

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing %s" % thisGlyph.name
	thisGlyph.beginUndo() # begin undo grouping
	syncSelectionFromLayer( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
