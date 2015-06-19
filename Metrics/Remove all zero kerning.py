#MenuTitle: Remove All Zero Kernings in Font
# -*- coding: utf-8 -*-
__doc__="""
Removes all kern pairs from the font that have value zero. Be careful, not every zero kerning is useless.
"""

import GlyphsApp
thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master

def nameForID( Font, ID ):
	try:
		if ID[0] == "@": # is a group
			return ID
		else: # is a glyph
			return Font.glyphForId_( ID ).name
	except Exception as e:
		raise e

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

print "Removing Zero Kern Pairs in: %s" % thisFont.familyName

for thisFontMaster in thisFont.masters:
	print "  Processing Master %s:" % thisFontMaster.name
	kernpairsToBeRemoved = []
	
	thisFontMasterID = thisFontMaster.id
	MasterKernDict = thisFont.kerning[thisFontMasterID]
	for leftGlyphID in MasterKernDict.keys():
		for rightGlyphID in MasterKernDict[ leftGlyphID ].keys():
			originalKerningValue = MasterKernDict[ leftGlyphID ][ rightGlyphID ]
			if originalKerningValue == 0.0:
				leftName  = nameForID( thisFont, leftGlyphID )
				rightName = nameForID( thisFont, rightGlyphID )
				kernpairsToBeRemoved.append( (leftName, rightName) )
	
	for thisKernPair in kernpairsToBeRemoved:
		leftSide = thisKernPair[0]
		rightSide = thisKernPair[1]
		thisFont.removeKerningForPair( thisFontMasterID, leftSide, rightSide )
		
	print "    Removed %i zero pairs." % len(kernpairsToBeRemoved)
