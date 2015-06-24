#MenuTitle: Delete Kerning Pairs for Selected Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Deletes all kerning pairs with the selected glyphs, for the current master only. Includes group kerning and exceptions, ie. when selecting /m which has left group: n, right group: n, the @MM_K_L_n, @MM_K_R_n kerning pairs will be deleted along with kerning pair execptions containing /m.
"""
import GlyphsApp

Glyphs.clearLog()
Font = Glyphs.font
Doc = Glyphs.currentDocument
selectedLayers = Font.selectedLayers
selectedMaster = Font.selectedFontMaster
masterID = selectedMaster.id

namesOfSelectedGlyphs = [ l.parent.name for l in selectedLayers if hasattr(l.parent, 'name')]
pairsToBeDeleted = []

# function to return @MMK_ name or glyph name
def nameMaker(kernGlyph):
	if kernGlyph[0] == "@":
	# 	if option == 1:
	# 		return kernGlyph[7:]
	# 	else:
		return kernGlyph
	else:
		return Font.glyphForId_(kernGlyph).name	

def uniquify(seq):
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]

totalNumberOfDeletions = 0

for selectedGlyph in namesOfSelectedGlyphs:

	leftGlyphNames = []
	rightKerningGroup = Font.glyphs[ selectedGlyph ].rightKerningGroup
	if rightKerningGroup is not None:
		leftGlyphNames += ["@MMK_L_{0}".format(rightKerningGroup)]
	leftGlyphNames += [selectedGlyph]

	rightGlyphNames = []
	leftKerningGroup = Font.glyphs[ selectedGlyph ].leftKerningGroup
	if leftKerningGroup is not None:
		rightGlyphNames += ["@MMK_R_{0}".format(leftKerningGroup)]
	else:
		rightGlyphNames += [selectedGlyph]

	for L in Font.kerning[ masterID ]:
		# if there exist kerning pairs "L, *" where L is either class kerning, an exception or normal kerning
		if str(nameMaker(L)) in leftGlyphNames:
			for R in Font.kerning[masterID][L]:
				pairsToBeDeleted += [ (nameMaker(L), nameMaker(R)) ]

		# if there exist kerning pairs "*, R" where R is either class kerning, an exception or normal kerning
		for R in Font.kerning[masterID][L]:
			if str(nameMaker(R)) in rightGlyphNames:
				pairsToBeDeleted += [ (nameMaker(L), nameMaker(R)) ]

Font.disableUpdateInterface()

# uniquify so that it doesn't try to delete the same kerning pair again
for thisDeletionGroup in uniquify(pairsToBeDeleted):
	leftGlyphName = thisDeletionGroup[0]
	rightGlyphName = thisDeletionGroup[1]

	try:
		Font.removeKerningForPair( masterID, leftGlyphName, rightGlyphName )
		totalNumberOfDeletions += 1
		print "Deleting pair: %s %s ..." % ( leftGlyphName, rightGlyphName )
	except Exception, e:
		print "-- Error: could not delete pair %s %s (%s)" % ( leftGlyphName, rightGlyphName, e )

print "Done: %i pairs deleted in %s." % ( totalNumberOfDeletions, selectedMaster.name )

Font.enableUpdateInterface()
