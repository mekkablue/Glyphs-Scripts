#MenuTitle: New Tab with Kerning Missing in Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
Opens New Tabs for each master showing kerning missing in this master but present in other masters.
"""

thisFont = Glyphs.font # frontmost font

Glyphs.clearLog()
print("Missing kerning, report for %s" % thisFont.familyName)
print(thisFont.filepath)
print()

if not len(thisFont.masters) > 1:
	Message("Not enough masters", "If you want to compare kerning between masters, you need at least two masters in your font.", OKButton="Oh Shoot")
else:
	#prepare tabStrings:
	tabStrings = {}
	for thisMaster in thisFont.masters:
		tabStrings[thisMaster.id] = "Kerning missing in %s:\n" % thisMaster.name
	
	#prepare defaultGlyphs:
	leftGroupDefaults = {}
	rightGroupDefaults = {}
	for thisGlyph in thisFont.glyphs[::-1]:
		if thisGlyph.leftKerningGroup:
			leftGroupDefaults[thisGlyph.leftKerningGroup] = thisGlyph.name
		if thisGlyph.rightKerningGroup:
			rightGroupDefaults[thisGlyph.rightKerningGroup] = thisGlyph.name
	
	for thisMaster in thisFont.masters:
		masterID = thisMaster.id
		otherMasterIDs = [m.id for m in thisFont.masters if m != thisMaster]
		masterKerning = thisFont.kerning[masterID]
		for leftSide in masterKerning:
			for rightSide in masterKerning[leftSide]:
				for otherID in otherMasterIDs:
					
					try:
						probeValue = thisFont.kerning[otherID][leftSide][rightSide]
					except:
						# kerning does not exist:
					
						leftSideGlyphName,rightSideGlyphName = None, None
						if not leftSide[0] == "@":
							leftSideGlyph = thisFont.glyphForId_(leftSide)
							if leftSideGlyph:
								leftSideGlyphName = leftSideGlyph.name
							else:
								print(u"❌ Glyph %s: Orphaned LEFT glyph ID in kerning. No corresponding glyph in font." % leftSide)
						elif not leftSide[7:] in rightGroupDefaults:
							print(u"❌ @%s: Orphaned LEFT SIDE of kern pair. No corresponding RIGHT GROUP in glyphs." % leftSide[7:])
							Glyphs.showMacroWindow()
						elif rightGroupDefaults[leftSide[7:]]:
							leftSideGlyphName = rightGroupDefaults[leftSide[7:]]
						else:
							print(u"🤷🏻‍♀️ Cannot convert left side name:", leftSide)
						
						if not rightSide[0] == "@":
							rightSideGlyph = thisFont.glyphForId_(rightSide)
							if rightSideGlyph:
								rightSideGlyphName = rightSideGlyph.name
							else:
								print(u"❌ Glyph %s: Orphaned RIGHT glyph ID in kerning. No corresponding glyph in font." % rightSide)
						elif not rightSide[7:] in leftGroupDefaults:
							print(u"❌ @%s: Orphaned RIGHT SIDE of kern pair. No corresponding LEFT GROUP in glyphs." % rightSide[7:])
							Glyphs.showMacroWindow()
						elif leftGroupDefaults[rightSide[7:]]:
							rightSideGlyphName = leftGroupDefaults[rightSide[7:]]
						else:
							print(u"🤷🏻‍♀️ Cannot convert right side name:", rightSide)
							
						if leftSideGlyphName and rightSideGlyphName:
							tabStrings[otherID] += "/%s/%s  " % (leftSideGlyphName,rightSideGlyphName)
	if tabStrings:
		print("\nOrphaned groups and glyph IDs: consider cleaning up kerning on Window > Kerning.")
	for masterID in tabStrings:
		thisFont.newTab(tabStrings[masterID])
