# MenuTitle: Remove Orphaned Group Kerning
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Deletes all group kernings referring to groups that are not (anymore) in the font.
"""

from GlyphsApp import Glyphs

thisFont = Glyphs.font  # frontmost font

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print("REMOVING ORPHANED GROUP KERNING")

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


def nameForKerningKey(kerningKey):
	"""Turns a glyph ID used in font.kerning into a glyph name; group keys are returned unchanged."""
	if kerningKey.startswith("@"):
		return kerningKey
	glyph = thisFont.glyphForId_(kerningKey)
	if glyph:
		return glyph.name
	return kerningKey


deletionCount = 0

if thisFont is None:
	print("⚠️ No font open.")
else:
	# collect group names:
	leftGroups = tuple(set(g.leftKerningGroup for g in thisFont.glyphs))
	rightGroups = tuple(set(g.rightKerningGroup for g in thisFont.glyphs))
	print("Found: %s left groups, %s right groups." % (len(leftGroups), len(rightGroups)))

for thisMaster in (thisFont.masters if thisFont else ()):
	toBeDeleted = []
	thisMasterID = thisMaster.id
	print("\nMaster ‘%s’" % thisMaster.name)

	for leftKey in thisFont.kerning[thisMasterID].keys():
		if leftKey.startswith("@") and not leftKey[7:] in rightGroups:
			for rightKey in thisFont.kerning[thisMasterID][leftKey].keys():
				toBeDeleted.append((leftKey, rightKey))
				print("\tMarked for deletion: *%s - %s (%i)" % (
					convertIntoName(leftKey),
					convertIntoName(rightKey),
					thisFont.kerning[thisMasterID][leftKey][rightKey],
				))
		else:
			for rightKey in thisFont.kerning[thisMasterID][leftKey].keys():
				if rightKey.startswith("@") and not rightKey[7:] in leftGroups:
					toBeDeleted.append((leftKey, rightKey))
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
		# removeKerningForPair expects glyph names (or group keys), not the glyph IDs used in font.kerning
		thisFont.removeKerningForPair(thisMasterID, nameForKerningKey(leftSide), nameForKerningKey(rightSide))

	print("\tSuccessfully deleted orphaned group kern pairs in master ‘%s’." % thisMaster.name)
