#MenuTitle: Copy Kerning from Caps to Small Caps
# -*- coding: utf-8 -*-
__doc__="""
Looks for cap kerning pairs and reduplicates their kerning for corresponding .sc glyphs, if they are available in the font. Please be careful: Will overwrite existing SC kerning pairs.
"""

smallcapSuffix = ".sc"
# or ".c2sc"
# or ".smcp"

areSmallcapsNamedLowercase = True
# True if you use "a.sc"
# False if you use "A.sc"

import GlyphsApp

thisFont = Glyphs.font
selectedFontMaster = thisFont.selectedFontMaster
fontMasterID = selectedFontMaster.id
fontMasterName = selectedFontMaster.name
masterKernDict = thisFont.kerning[ fontMasterID ]
scKerningList = []

def thisGlyphIsUppercase( glyphName, thisFont=Glyphs.font ):
	"""Tests if the glyph referenced by the supplied glyphname is an uppercase glyph."""
	try:
		if glyphName:
			if thisFont.glyphs[glyphName].subCategory == "Uppercase":
				return True
			else:
				return False
		else:
			return False
	except Exception, e:
		print "Cannot determine case for: %s" % glyphName
		print "Error: %s" % e
		return False

def smallcapName( glyphName="scGlyph", suffix=".sc", lowercase=True ):
	"""Returns the appropriate smallcap name, e.g. A-->a.sc or a-->a.sc"""
	try:
		returnName = glyphName
		# make lowercase if requested:
		if lowercase:
			returnName = returnName.lower()
		# add suffix:
		returnName = returnName + suffix
		return returnName
	except Exception as e:
		print "Cannot compute smallcap name for: %s" % glyphName
		print "Error: %s" % e
		return None
		
Glyphs.clearLog()
Glyphs.showMacroWindow()
print "Copying Kerning from UC to SC...\nFont: %s\nMaster: %s\n" % ( thisFont.familyName, fontMasterName )

for LeftKey in masterKernDict.keys():
	# is left key a class?
	leftKeyIsGroup = ( LeftKey[0] == "@" )
	isANewKerningPair = False
	
	if leftKeyIsGroup:
		leftGlyphName = None
	else:
		leftGlyphName = thisFont.glyphForId_( LeftKey ).name
	
	# determine the SC leftKey:
	if ( leftKeyIsGroup and thisGlyphIsUppercase( LeftKey[7:] ) ):
		scLeftKey = LeftKey[:7] + smallcapName( LeftKey[7:] )
		isANewKerningPair = True
	elif ( thisGlyphIsUppercase( leftGlyphName ) and not leftKeyIsGroup ):
		scLeftGlyph = thisFont.glyphs[ smallcapName( leftGlyphName ) ]
		if scLeftGlyph == None:
			scLeftKey = LeftKey
		else:
			scLeftKey = scLeftGlyph.name
			isANewKerningPair = True
	else:
		scLeftKey = LeftKey
	
	for RightKey in masterKernDict[LeftKey].keys():
		# is right key a class?
		rightKeyIsGroup = ( RightKey[0] == "@" )
		
		if rightKeyIsGroup:
			rightGlyphName = None
		else:
			rightGlyphName = thisFont.glyphForId_( RightKey ).name
		
		# determine the SC leftKey:
		if ( rightKeyIsGroup and thisGlyphIsUppercase( RightKey[7:] ) ):
			scRightKey = RightKey[:7] + smallcapName( RightKey[7:] )
			isANewKerningPair = True
		elif ( thisGlyphIsUppercase( rightGlyphName ) and not rightKeyIsGroup ):
			scRightGlyph = thisFont.glyphs[ smallcapName( rightGlyphName ) ]
			if scRightGlyph == None:
				scRightKey = RightKey
			else:
				scRightKey = scRightGlyph.name
				isANewKerningPair = True
		else:
			scRightKey = RightKey
		
		if isANewKerningPair:
			kernValue = masterKernDict[LeftKey][RightKey]
			print "  Added %s %s %.1f" % ( 
				scLeftKey.replace("MMK_L_",""),
				scRightKey.replace("MMK_R_",""),
				kernValue
			)
			scKerningList.append( ( scLeftKey, scRightKey, kernValue ) )

for thisKernPair in scKerningList:
	scLeftKey = thisKernPair[0]
	scRightKey = thisKernPair[1]
	scKernValue = thisKernPair[2]
	thisFont.setKerningForPair( fontMasterID, scLeftKey, scRightKey, scKernValue )
