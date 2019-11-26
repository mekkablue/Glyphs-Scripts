from __future__ import print_function
#MenuTitle: Remove all Open Paths
# -*- coding: utf-8 -*-
__doc__="""
Deletes all paths in visible layers of selected glyphs.
"""

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	count = 0

	thisLayer.parent.beginUndo()
	for i in range( len( thisLayer.paths ))[::-1]:
		if thisLayer.paths[i].closed == False:
			del thisLayer.paths[i]
			count += 1
	thisLayer.parent.endUndo()
	
	return count

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	print("Removing %i open paths in %s." % ( process( thisLayer ), thisLayer.parent.name ))

Font.enableUpdateInterface()

