#MenuTitle: Reset Rotated and Mirrored Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
Looks for mirrored and rotated components and resets them to their original orientation.
"""

Font = Glyphs.font
selectedLayers = Font.selectedLayers

for l in selectedLayers:
	thisGlyph = l.parent
	glyphName = thisGlyph.name
	toBeDeleted = []
	toBeAdded = []
	
	thisGlyph.beginUndo()
	
	for compIndex in range( len( l.components ) ):
		comp = l.components[ compIndex ]
		if comp.transform[0] != 1.0 or comp.transform[3] != 1.0:
			toBeDeleted.append( compIndex )
			toBeAdded.append( [ comp.componentName, comp.bounds.origin.x, comp.bounds.origin.y ] )
				
	numOfComponents = len( toBeAdded )
	print "Fixing %i components in %s ..." % ( numOfComponents, glyphName )

	for delIndex in sorted( toBeDeleted )[::-1]:
		del l.components[ delIndex ]

	for addMe in toBeAdded:
		newC = GSComponent( str( addMe[0] ) )
		newC.x = addMe[1]
		newC.y = addMe[2]
		l.components.append( newC )
	
	thisGlyph.endUndo()
	
