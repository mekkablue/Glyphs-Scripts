#MenuTitle: New Tab with Dangerous Glyphs for Interpolation
# -*- coding: utf-8 -*-
__doc__="""
Finds and outputs glyphs like the equals sign, or a symmetrical period, with paths that could interpolate wrongly within themselves.
"""

import GlyphsApp

Font = Glyphs.font
outputString = ""

def nodeCounts( thisLayer ):
	countList = [ len(p.nodes) for p in thisLayer.paths ]
	return countList

def shiftString( myString ):
	return myString[1:] + myString[0]

def nodeString( path ):
	nodestring = ""
	for thisNode in path.nodes:
		if thisNode.type == 65:
			nodestring += "h"
		else:
			nodestring += "n"
	return nodestring

def compatibleWhenReversed( path1, path2 ):
	pathstring1 = nodeString(path1)
	pathstring2 = "".join(reversed(nodeString(path2)))
	if pathstring1 == pathstring2:
		return True
	return False

def compatibleWithDifferentStartPoints( path1, path2 ):
	pathstring1 = nodeString(path1)
	pathstring2 = nodeString(path2)
	for x in pathstring1:
		pathstring2 = shiftString(pathstring2)
		if pathstring1 == pathstring2:
			return True
	return False

def check( thisLayer ):
	thesePaths = thisLayer.paths
	theseComponents = thisLayer.components
	
	if len( theseComponents ) > 1:
		componentNameList = [ c.componentName for c in theseComponents ]
		compareValue_1 = len( componentNameList )
		compareValue_2 = len( set( componentNameList ) )
		if compareValue_1 != compareValue_2:
			return True
	
	if len( thisLayer.paths ) > 1:
		pathStructureList = [ nodeString(p) for p in thesePaths ]
		compareValue_1 = len( pathStructureList )
		compareValue_2 = len( set( pathStructureList ) )
		if compareValue_1 != compareValue_2:
			return True

		nodecounts = nodeCounts(thisLayer)
		if len(nodecounts) != len( set(nodecounts) ):
			numberOfPaths = len(thesePaths)
			for i in range( numberOfPaths ):
				firstPath = thesePaths[i]
				firstPathCount = len(firstPath.nodes)
				for j in range( i+1, numberOfPaths):
					secondPath = thesePaths[j]
					secondPathCount = len(secondPath.nodes)
					if firstPathCount == secondPathCount:
						if firstPath.closed and secondPath.closed and compatibleWithDifferentStartPoints( firstPath, secondPath ):
							return True
						elif compatibleWhenReversed( firstPath, secondPath ):
							return True
							
	if len(thisLayer.paths) == 1:
		thisPath = thisLayer.paths[0]
		if thisPath.closed and compatibleWithDifferentStartPoints( thisPath, thisPath ):
			return True
		elif compatibleWhenReversed( thisPath, thisPath ):
			return True

	return False

for thisGlyph in Font.glyphs:
	if check( thisGlyph.layers[0] ):
		outputString += "/%s" % thisGlyph.name

if outputString:
	Font.newTab( outputString )
else:
	Message(
		"No interpolation problems",
		"Cannot find any dangerous glyphs in this font.",
		OKButton="Hurrah!"
	)
