#MenuTitle: Delete components out of bounds
"""Looks for components out of bounds."""

outOfBounds = 3000.0

import GlyphsApp
import math

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def scanOutOfBounds( thisLayer ):
	
	listOfComponents = [c for c in thisLayer.components]
	indexesOutOfBounds = []

	for i in range( len( listOfComponents )):
		c = thisLayer.components[i]
		if math.fabs(c.y) > outOfBounds or math.fabs(c.x) > outOfBounds:
			indexesOutOfBounds.append(i)
	
	return sorted( set( indexesOutOfBounds ) )

def process( thisLayer ):
	glyphName = thisLayer.parent.name
	
	if len( thisLayer.components ) != 0:
		thisLayer.setDisableUpdates()
		thisLayer.parent.beginUndo()
	
		indexesOutOfBounds = scanOutOfBounds( thisLayer )
		numberOfOffComponents = len(indexesOutOfBounds)

		if numberOfOffComponents > 0:
			print "Deleting %i components in %s." % (numberOfOffComponents, glyphName)
		
			for indexOutOfBounds in indexesOutOfBounds[::-1]:
				del thisLayer.components[indexOutOfBounds]
		else:
			print "No components out of bounds in %s." % glyphName
		
		thisLayer.parent.endUndo()
		thisLayer.setEnableUpdates()
	else:
		print "No components in %s." % glyphName

for thisLayer in selectedLayers:
	process( thisLayer )
