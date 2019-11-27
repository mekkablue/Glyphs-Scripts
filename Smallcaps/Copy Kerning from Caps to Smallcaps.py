#MenuTitle: Copy Kerning from Caps to Smallcaps
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Looks for cap kerning pairs and reduplicates their kerning for corresponding .sc glyphs, if they are available in the font. Please be careful: Will overwrite existing SC kerning pairs.
"""

smallcapSuffix = ".sc"
# or ".c2sc"
# or ".smcp"

areSmallcapsNamedLowercase = True
# True if you use "a.sc"
# False if you use "A.sc"

def thisGlyphIsUppercase( glyphName, thisFont=Glyphs.font ):
	"""Tests if the glyph referenced by the supplied glyphname is an uppercase glyph."""
	try:
		if glyphName and thisFont.glyphs[glyphName].subCategory == "Uppercase":
			return True
		return False
	except Exception as e:
		print("Cannot determine case for: %s" % glyphName)
		print("Error: %s" % e)
		return False

def smallcapName( glyphName="scGlyph", suffix=".sc", lowercase=True ):
	"""Returns the appropriate smallcap name, e.g. A-->a.sc or a-->a.sc"""
	try:
		returnName = glyphName
		
		# make lowercase if requested:
		if lowercase:
			suffixOffset = returnName.find(".")
			if suffixOffset > 0:
				returnName = returnName[:suffixOffset].lower() + returnName[suffixOffset:]
			else:
				returnName = returnName.lower()
			
		# add suffix:
		returnName = returnName + suffix
		return returnName
	except Exception as e:
		print("Cannot compute smallcap name for: %s" % glyphName)
		print("Error: %s" % e)
		return None

thisFont = Glyphs.font
selectedFontMaster = thisFont.selectedFontMaster
fontMasterID = selectedFontMaster.id
fontMasterName = selectedFontMaster.name
masterKernDict = thisFont.kerning[ fontMasterID ]
scKerningList = []

# Report in the Macro Window:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print("Copying Kerning from UC to SC...")
print("Font: %s" % ( thisFont.familyName ))
print("Master: %s\n" % ( fontMasterName ))

# Sync left and right Kerning Groups between UC and SC:
print("Kerning Groups:")
UppercaseGroups = set()
for g in thisFont.glyphs:
	if g.subCategory == "Uppercase":
		ucGlyphName = g.name
		scGlyphName = smallcapName( ucGlyphName )
		scGlyph = thisFont.glyphs[scGlyphName]
		if scGlyph == None:
			print("  SC %s not found in font (Uc %s exists)" % ( scGlyphName, ucGlyphName ))
			continue
			
		LeftKey = g.leftKerningGroupId()
		if LeftKey:
			UppercaseGroups.add( LeftKey )
			scLeftKey = LeftKey[:7] + smallcapName( LeftKey[7:] )
			if scGlyph.leftKerningGroupId() == None:
				scGlyph.setLeftKerningGroupId_(scLeftKey)
				print("  %s: set LEFT group to @%s (was empty)." % ( scGlyphName, scLeftKey[7:] ))
			elif scGlyph.leftKerningGroupId() != scLeftKey:
				print("  %s: unexpected LEFT group: @%s (should be @%s), not changed." % ( scGlyphName, scGlyph.leftKerningGroupId()[7:], scLeftKey[7:] ))
		
		RightKey = g.rightKerningGroupId()
		if RightKey:
			UppercaseGroups.add( RightKey )
			scRightKey = RightKey[:7] + smallcapName( RightKey[7:] )
			if scGlyph.rightKerningGroupId() == None:
				scGlyph.setRightKerningGroupId_(scRightKey)
				print("  %s: set RIGHT group to @%s (was empty)." % ( scGlyphName, scRightKey[7:] ))
			elif scGlyph.rightKerningGroupId() != scRightKey:
				print("  %s: unexpected RIGHT group: @%s (should be @%s), not changed." % ( scGlyphName, scGlyph.rightKerningGroupId()[7:], scRightKey[7:] ))

print("  Done.\n")


# Sync Kerning Values between UC and SC:
print("Kerning Values:")
kerningToBeAdded = []
LeftKeys = masterKernDict.keys()
for LeftKey in LeftKeys:
	# is left key a class?
	leftKeyIsGroup = ( LeftKey[0] == "@" )
	# prepare SC left key:
	scLeftKey = None
	# determine the SC leftKey:
	if leftKeyIsGroup: # a kerning group
		leftKeyName = "@%s" % LeftKey[7:]
		if LeftKey in UppercaseGroups:
			scLeftKey = LeftKey[:7] + smallcapName( LeftKey[7:] )
	else: # a single glyph (exception)
		leftGlyphName = thisFont.glyphForId_( LeftKey ).name
		leftKeyName = leftGlyphName
		if thisGlyphIsUppercase( leftGlyphName ):
			scLeftGlyphName = smallcapName( leftGlyphName )
			scLeftGlyph = thisFont.glyphs[ scLeftGlyphName ]
			if scLeftGlyph:
				scLeftKey = scLeftGlyph.name
	
	RightKeys = masterKernDict[LeftKey].keys()
	for RightKey in RightKeys:
		# is right key a class?
		rightKeyIsGroup = ( RightKey[0] == "@" )
		# prepare SC right key:
		scRightKey = None
		# determine the SC rightKey:
		if rightKeyIsGroup: # a kerning group
			rightKeyName = "@%s" % RightKey[7:]
			if RightKey in UppercaseGroups:
				scRightKey = RightKey[:7] + smallcapName( RightKey[7:] )
		else: # a single glyph (exception)
			rightGlyphName = thisFont.glyphForId_( RightKey ).name
			rightKeyName = rightGlyphName
			if thisGlyphIsUppercase( rightGlyphName ):
				scRightGlyphName = smallcapName( rightGlyphName )
				scRightGlyph = thisFont.glyphs[ scRightGlyphName ]
				if scRightGlyph:
					scRightKey = scRightGlyph.name
		
		# If we have one of the left+right keys, create a pair:
		if scRightKey != None or scLeftKey != None:
			
			# fallback:
			if scLeftKey == None:
				scLeftKey = leftKeyName.replace("@","@MMK_L_")
			if scRightKey == None:
				scRightKey = rightKeyName.replace("@","@MMK_R_")
				
			scKernValue = masterKernDict[LeftKey][RightKey]
			print("  Set kerning: %s %s %.1f (derived from %s %s)" % ( 
				scLeftKey.replace("MMK_L_",""),	scRightKey.replace("MMK_R_",""),
				scKernValue,
				leftKeyName, rightKeyName
			))
			kerningToBeAdded.append( (fontMasterID, scLeftKey, scRightKey, scKernValue) )
				

# go through the list of SC kern pairs, and add them to the font:
thisFont.disableUpdateInterface()
for thisKernInfo in kerningToBeAdded:
	fontMasterID = thisKernInfo[0]
	scLeftKey = thisKernInfo[1]
	scRightKey = thisKernInfo[2]
	scKernValue = thisKernInfo[3]
	thisFont.setKerningForPair( fontMasterID, scLeftKey, scRightKey, scKernValue )
thisFont.enableUpdateInterface()
print("  Done.")