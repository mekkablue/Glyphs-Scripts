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
		if glyphName and thisFont.glyphs[glyphName].subCategory == "Uppercase":
			return True
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

UppercaseClasses = set()
for g in thisFont.glyphs:
	if g.subCategory == "Uppercase":
		
		scGlyph = thisFont.glyphs[smallcapName( g.name )]
		if scGlyph == None:
			print "!!missing small cap glyph for: %s" % g.name
			continue
		LeftKey = g.leftKerningGroupId()
		if LeftKey:
			UppercaseClasses.add( LeftKey )
			scLeftKey = LeftKey[:7] + smallcapName( LeftKey[7:] )
			if scGlyph.leftKerningGroupId() != scLeftKey:
				print "Small cap glyph (%s) has wrong kerning class: %s != %s" % (scGlyph.name, scGlyph.leftKerningGroupId(), scLeftKey)
		
		RightKey = g.rightKerningGroupId()
		if RightKey:
			UppercaseClasses.add( RightKey )
			scRightKey = RightKey[:7] + smallcapName( RightKey[7:] )
			if scGlyph.rightKerningGroupId() != scRightKey:
				print "Small cap glyph (%s) has wrong kerning class: %s != %s" % (scGlyph.name, scGlyph.rightKerningGroupId(), scRightKey)

thisFont.disableUpdateInterface()

kerningToBeAdded = []

LeftKeys = masterKernDict.keys()
for LeftKey in LeftKeys:
	# is left key a class?
	leftKeyIsGroup = ( LeftKey[0] == "@" )
	isANewKerningPair = False
	
	scLeftKey = None
	scRightKey = None
	
	# determine the SC leftKey:
	if leftKeyIsGroup:
		if LeftKey in UppercaseClasses:
			scLeftKey = LeftKey[:7] + smallcapName( LeftKey[7:] )
	else:
		leftGlyphName = thisFont.glyphForId_( LeftKey ).name
		if thisGlyphIsUppercase( leftGlyphName ):
			scLeftGlyph = thisFont.glyphs[ smallcapName( leftGlyphName ) ]
			if scLeftGlyph:
				scLeftKey = scLeftGlyph.name
	
	if scLeftKey != None:
		RightKeys = masterKernDict[LeftKey].keys()
		for RightKey in RightKeys:
			# is right key a class?
			rightKeyIsGroup = ( RightKey[0] == "@" )
		
			# determine the SC leftKey:
			if rightKeyIsGroup:
				if RightKey in UppercaseClasses:
					scRightKey = RightKey[:7] + smallcapName( RightKey[7:] )
			else:
				rightGlyphName = thisFont.glyphForId_( RightKey ).name
				if thisGlyphIsUppercase( rightGlyphName ):
					scRightGlyph = thisFont.glyphs[ smallcapName( rightGlyphName ) ]
					if scRightGlyph:
						scRightKey = scRightGlyph.name

			if scRightKey != None:
				scKernValue = masterKernDict[LeftKey][RightKey]
				print "  Added %s %s %.1f" % ( 
					scLeftKey.replace("MMK_L_",""),
					scRightKey.replace("MMK_R_",""),
					scKernValue
				)
				kerningToBeAdded.append( (fontMasterID, scLeftKey, scRightKey, scKernValue) )

for thisKernInfo in kerningToBeAdded:
	fontMasterID = thisKernInfo[0]
	scLeftKey = thisKernInfo[1]
	scRightKey = thisKernInfo[2]
	scKernValue = thisKernInfo[3]
	thisFont.setKerningForPair( fontMasterID, scLeftKey, scRightKey, scKernValue )

thisFont.enableUpdateInterface()
