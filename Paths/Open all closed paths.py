#MenuTitle: Open closed paths
# -*- coding: utf-8 -*-
__doc__="""
Opens all paths in the visible layers of selected glyphs.
"""



Font = Glyphs.font
selectedLayers = Font.selectedLayers

def process( thisLayer ):
	pathCount = 0
	
	for thisPath in thisLayer.paths:
		if thisPath.closed:
			thisPath.closed = False
			pathCount += 1
	
	return pathCount

Font.disableUpdateInterface()

print "Opening paths in %i glyphs:" % len( selectedLayers )

for thisLayer in selectedLayers:
	print "-- %s: opened %i path(s)." % ( thisLayer.parent.name, process( thisLayer ) )

Font.enableUpdateInterface()

