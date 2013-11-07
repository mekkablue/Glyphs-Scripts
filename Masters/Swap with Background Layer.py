#MenuTitle: Swap with Background Layer
# -*- coding: utf-8 -*-
"""Swaps the current layer(s) with their respective backgrounds."""

import GlyphsApp


Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	thisBackgroundBackup = thisLayer.background.copy() #.copy()
	
	# set the background:
	thisLayer.setBackground_( thisLayer )

	# clear the foreground:
	while len( thisLayer.paths ) > 0:
		del thisLayer.paths[0]

	while len( thisLayer.anchors ) > 0:
		del thisLayer.anchors[0]

	while len( thisLayer.components ) > 0:
		del thisLayer.components[0]
	
	# set the foreground:
	for thisBackgroundPath in thisBackgroundBackup.paths:
		thisLayer.addPath_( thisBackgroundPath.copy() )
	
	for thisBackgroundAnchor in thisBackgroundBackup.anchors:
		thisLayer.addAnchor_( thisBackgroundAnchor.copy() )
	
	for thisBackgroundComponent in thisBackgroundBackup.components:
		thisLayer.addComponent_( thisBackgroundComponent.copy() )
		
	


Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	try:
		# foreground is the active layer:
		thisGlyph = thisLayer.parent
		print "Processing", thisGlyph.name
		thisGlyph.beginUndo()	
		process( thisLayer )
		thisGlyph.endUndo()
	except:
		# background is the active layer:
		# doesn't work yet, sorry :-(
		thisGlyph = thisLayer.parent.parent
		print "Processing", thisGlyph.name
		thisGlyph.beginUndo()	
		process( thisLayer.parent )
		thisGlyph.endUndo()

Font.enableUpdateInterface()
