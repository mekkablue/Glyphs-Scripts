#MenuTitle: Delete Components out of Bounds
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Looks for components out of bounds.
"""

from math import fabs

Font = Glyphs.font
selectedLayers = Font.selectedLayers
outOfBounds = 3000.0

def scanOutOfBounds( thisLayer ):
	
	listOfComponents = [c for c in thisLayer.components]
	indexesOutOfBounds = []

	for i in range( len( listOfComponents )):
		c = thisLayer.components[i]
		if fabs(c.y) > outOfBounds or fabs(c.x) > outOfBounds:
			indexesOutOfBounds.append(i)
	
	return sorted( set( indexesOutOfBounds ) )

def process( thisLayer ):
	glyphName = thisLayer.parent.name
	
	if len( thisLayer.components ) != 0:
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
	else:
		print "No components in %s." % glyphName

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	process( thisLayer )

Font.enableUpdateInterface()
