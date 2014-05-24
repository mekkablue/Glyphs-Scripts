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

def check( thisLayer ):
	thesePaths = thisLayer.paths
	theseComponents = thisLayer.components
	
	if len( thisLayer.paths ) > 1:
		pathStructureList = [ pathStructure(p) for p in thesePaths ]
		compareValue_1 = len( pathStructureList )
		compareValue_2 = len( set( pathStructureList ) )
		if compareValue_1 != compareValue_2:
			return True
			
	elif len( theseComponents ) > 1:
		componentNameList = [ c.componentName for c in theseComponents ]
		compareValue_1 = len( componentNameList )
		compareValue_2 = len( set( componentNameList ) )
		if compareValue_1 != compareValue_2:
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

