#MenuTitle: Remove Orphaned Group Kerning
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Deletes all group kernings referring to groups that are not (anymore) in the font.
"""

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

# collect group names:
leftGroups = []
rightGroups = []
for thisGlyph in thisFont.glyphs:
	leftGroups.append( thisGlyph.leftKerningGroup )
	rightGroups.append( thisGlyph.rightKerningGroup )

leftGroups = tuple(set(leftGroups))
rightGroups = tuple(set(rightGroups))

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print("REMOVING ORPHANED GROUP KERNING")
print("Found: %s left groups, %s right groups." % ( len(leftGroups), len(rightGroups) ))

# Glyphs.removeKerningForPair(FontMasterId, LeftKey, RightKey)
# Removes the kerning for the two specified glyphs (LeftKey or RightKey is the glyphname) or a kerning group key (@MMK_X_XX).
# Parameters:	
# FontMasterId (str) – The id of the FontMaster
# LeftKey (str) – either a glyph name or a class name
# RightKey (str) – either a glyph name or a class name

def convertIntoName(groupOrGlyphID):
	if groupOrGlyphID.startswith("@MMK"):
		return "@%s" % groupOrGlyphID[7:]
	elif groupOrGlyphID.startswith("@"):
		return "@%s" % groupOrGlyphID
	else:
		return thisFont.glyphForId_(groupOrGlyphID).name

deletionCount = 0

for thisMaster in thisFont.masters:
	toBeDeleted = []
	thisMasterID = thisMaster.id
	print("\nMaster ‘%s’" % thisMaster.name)
	
	for leftKey in thisFont.kerning[thisMasterID]:
		if leftKey.startswith("@") and not leftKey[7:] in rightGroups:
			for rightKey in thisFont.kerning[thisMasterID][leftKey]:
				toBeDeleted.append( (leftKey,rightKey) )
				print("\tMarked for deletion: *%s - %s (%i)" % ( 
					convertIntoName(leftKey),
					convertIntoName(rightKey),
					thisFont.kerning[thisMasterID][leftKey][rightKey],
					))
		else:
			for rightKey in thisFont.kerning[thisMasterID][leftKey]:
				if rightKey.startswith("@") and not rightKey[7:] in leftGroups:
					toBeDeleted.append( (leftKey,rightKey) )
					print("\tMarked for deletion: %s - *%s (%i)" % ( 
						convertIntoName(leftKey),
						convertIntoName(rightKey),
						thisFont.kerning[thisMasterID][leftKey][rightKey],
						))
	
	deletionCount += len(toBeDeleted)
	print("\tDeleting %i kern pairs in master ‘%s’..." % (
		len(toBeDeleted),
		thisMaster.name,
		))

	for thisPair in toBeDeleted:
		leftSide, rightSide = thisPair
		thisFont.removeKerningForPair(thisMasterID, leftSide, rightSide)
	
	print("\tSuccessfully deleted orphaned group kern pairs in master ‘%s’." % (
		thisMaster.name,
		))
	