# MenuTitle: Report Kerning Mistakes
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds unnecessary kernings and groupings.
"""

from GlyphsApp import Glyphs

thisFont = Glyphs.font  # frontmost font

# no groups, no kern pairs:
extensionsWithoutKerning = (".tf", ".tosf")
noKerningToTheLeft = ("jacute", "Jacute", "bullet", "copyright", "parenleft", "bracketleft", "braceleft", "section", "questiondown", "exclamdown")
noKerningToTheRight = ("ldot", "Ldot", "trademark", "registered", "parenright", "bracketright", "braceright", "degree", "percent", "perthousand", "ordfeminine", "ordmasculine")

# groups OK, but report kernings:
extensionsUnlikelyToBeKerned = ("comb")
glyphNamesWithExtensionsNotToBeKerned = []
for extension in extensionsWithoutKerning:
	extensionNames = [g.name for g in thisFont.glyphs if extension in g.name and not g.name.startswith(extension)]
	glyphNamesWithExtensionsNotToBeKerned += extensionNames

unlikelyToBeKerned = (
	'notequal', 'brokenbar', 'divide', 'yen', 'radical', 'dollar', 'currency', 'asciitilde', 'emptyset', 'increment', 'trademark', 'summation', 'dagger', 'estimated', 'florin',
	'copyright', 'partialdiff', 'section', 'less', 'percent', 'cent', 'ampersand', 'perthousand', 'Delta', 'lessequal', 'pi', 'Omega', 'sterling', 'product', 'infinity', 'greater',
	'degree', 'approxequal', 'integral', 'registered', 'numero', 'daggerdbl', 'plusminus', 'multiply', 'asciicircum', 'dbldagger', 'leftArrow', 'euro', 'Ohm', 'greaterequal',
	'bar', 'lozenge', 'literSign', 'equal', 'logicalnot', 'micro', 'paragraph', 'plus', '.notdef', 'published', 'at', 'minus', 'rightArrow'
)
dontKernThese = (unlikelyToBeKerned + tuple(glyphNamesWithExtensionsNotToBeKerned))
leftGroupsToBeChecked = [g.leftKerningGroup for g in thisFont.glyphs if g.leftKerningGroup and g.name in dontKernThese]
rightGroupsToBeChecked = [g.rightKerningGroup for g in thisFont.glyphs if g.rightKerningGroup and g.name in dontKernThese]


def reportLeftGroup(thisGlyph):
	if thisGlyph:
		if thisGlyph.leftKerningGroup:
			print("  Questionable LEFT kerning group: /%s" % thisGlyph.name)
			if not thisGlyph.export:
				print("     Attention: %s does not export." % thisGlyph.name)


def reportRightGroup(thisGlyph):
	if thisGlyph:
		if thisGlyph.rightKerningGroup:
			print("  Questionable RIGHT kerning group: /%s" % thisGlyph.name)
			if not thisGlyph.export:
				print("     Attention: %s does not export." % thisGlyph.name)


def humanReadableName(groupOrGlyphId):
	niceName = "???"
	if groupOrGlyphId[0] == "@":
		niceName = "@%s" % groupOrGlyphId[7:]
	else:
		thisGlyph = thisFont.glyphForId_(groupOrGlyphId)
		if thisGlyph:
			niceName = thisGlyph.name
		else:
			niceName = groupOrGlyphId
	return niceName


def reportBadKernPair(leftSide, rightSide, kernValue):
	leftName = humanReadableName(leftSide)
	rightName = humanReadableName(rightSide)
	print("  Questionable pair: %s -- %s (%i)" % (leftName, rightName, kernValue))


# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

# test for groups:
print("PROBLEMS WITH KERNING GROUPS:\n")
for extension in extensionsWithoutKerning:
	for thisGlyph in [g for g in thisFont.glyphs if extension in g.name]:
		reportLeftGroup(thisGlyph)
		reportRightGroup(thisGlyph)

print()

for glyphName in noKerningToTheLeft:
	thisGlyph = thisFont.glyphs[glyphName]
	reportLeftGroup(thisGlyph)

print()

for glyphName in noKerningToTheRight:
	thisGlyph = thisFont.glyphs[glyphName]
	reportRightGroup(thisGlyph)

# test for kern pairs:
print("\nPROBLEMS WITH KERN PAIRS:")
for thisMaster in thisFont.masters:
	print("\n  MASTER: %s" % thisMaster.name)

	masterKerning = thisFont.kerning[thisMaster.id]

	for leftGlyphName in (noKerningToTheRight + unlikelyToBeKerned + tuple(glyphNamesWithExtensionsNotToBeKerned)):
		if thisFont.glyphs[leftGlyphName]:
			leftGlyph = thisFont.glyphs[leftGlyphName]
			leftID = leftGlyph.id
			if leftID in masterKerning.keys():
				for rightSide in masterKerning[leftID].keys():
					reportBadKernPair(leftID, rightSide, masterKerning[leftID][rightSide])

	shouldntBeOnRightSide = (noKerningToTheLeft + unlikelyToBeKerned + tuple(glyphNamesWithExtensionsNotToBeKerned))
	for leftSide in masterKerning.keys():
		for rightSide in masterKerning[leftSide].keys():
			if rightSide[0] != "@":
				rightGlyph = thisFont.glyphForId_(rightSide)
				if rightGlyph:
					rightName = rightGlyph.name
					if rightName in shouldntBeOnRightSide:
						reportBadKernPair(leftSide, rightSide, masterKerning[leftSide][rightSide])
			elif rightSide.replace("@MMK_R_", "@") in leftGroupsToBeChecked:
				reportBadKernPair(leftSide, rightSide, masterKerning[leftSide][rightSide])

	for leftSideGroup in ["@MMK_L_%s" % groupname for groupname in rightGroupsToBeChecked]:
		if leftSideGroup in masterKerning.keys():
			for rightSide in masterKerning[leftSideGroup].keys():
				reportBadKernPair(leftSideGroup, rightSide, masterKerning[leftSideGroup][rightSide])

print("\nDON'T FORGET:\n")
print("  Please clean up kerning with:\n     Window > Kerning > gear menu > Clean up\n")
print("  Please test for overkerns with:\n     Script > mekkablue > Metrics > New Tab wth Overkerned Pairs\n")
print("  Please test for very small pairs with:\n     Script > mekkablue > Metrics > Delete Small Kern Pairs\n")
