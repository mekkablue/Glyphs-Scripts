#MenuTitle: New Tab with Dangerous Glyphs for Interpolation
# -*- coding: utf-8 -*-
__doc__="""
Finds and outputs glyphs like the equals sign, with paths that could interpolate within themselves.
"""

import GlyphsApp
from PyObjCTools.AppHelper import callAfter

Font = Glyphs.font
outputString = ""

def pathStructure( thisPath ):
	typeList = [ str(n.type) for n in thisPath.nodes ]
	thisPathStructureString = "-".join( typeList )
	return thisPathStructureString

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

def compatibleWithDifferentStartPoints( path1, path2 ):
	pathstring1 = nodeString(path1)
	pathstring2 = nodeString(path2)
	print pathstring1, pathstring2
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
		pathStructureList = [ pathStructure(p) for p in thesePaths ]
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
						if compatibleWithDifferentStartPoints( firstPath, secondPath ):
							return True
							
	if len(thisLayer.paths) == 1:
		thisPath = thisLayer.paths[0]
		if compatibleWithDifferentStartPoints( thisPath, thisPath ):
			return True

	return False

for thisGlyph in Font.glyphs:
	if check( thisGlyph.layers[0] ):
		outputString += "/%s" % thisGlyph.name

callAfter( Glyphs.currentDocument.windowController().addTabWithString_, outputString )

# Comment out or delete the previous line
# and uncomment the following three lines
# if the tab opening does not work for you:

# Glyphs.clearLog()
# Glyphs.showMacroWindow()
# print "Please check these glyphs again:\n%s" % outputString

