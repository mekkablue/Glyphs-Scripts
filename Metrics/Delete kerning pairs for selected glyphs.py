#MenuTitle: Delete kerning pairs for selected glyphs
# -*- coding: utf-8 -*-
__doc__="""
Deletes all kerning pairs with the selected glyphs, for the current master only.
"""

import GlyphsApp

Font = Glyphs.font
Master = Font.selectedFontMaster

selectedLayers = Font.selectedLayers
listOfIDs = [ x.parent.id for x in selectedLayers ]
masterID = Master.id
totalNumberOfDeletions = 0

print "Analyzing kerning pairs in %s ..." % Master.name
print "1. Pairs where selected glyphs are on the left side:"

pairsToBeDeleted = []

for leftGlyphID in listOfIDs:
	leftGlyphName = Font.glyphForId_( leftGlyphID ).name
	try:
		# print leftGlyphID, leftGlyphName, len( Font.kerning[ masterID ][ leftGlyphID ] ) #DEBUG
		if Font.kerning[ masterID ].has_key( leftGlyphID ):
			rightGlyphIDs = Font.kerning[ masterID ][ leftGlyphID ].keys()
			numberOfPairs = len( rightGlyphIDs )
			rightGlyphNames = [ Font.glyphForId_(x).name for x in rightGlyphIDs ]
			totalNumberOfDeletions += numberOfPairs

			print "   %s on the left: Found %i pairs ..." % ( leftGlyphName, numberOfPairs )
			#print " ".join( rightGlyphNames ) #DEBUG
			
			pairsToBeDeleted.append( [leftGlyphName, rightGlyphNames] )

	except Exception, e:
		print "-- Error while processing %s (%s)" % ( leftGlyphName, e )

print "2. Deleting these %i pairs ..." % ( totalNumberOfDeletions )

for thisDeletionGroup in pairsToBeDeleted:
	leftGlyphName = thisDeletionGroup[0]
	rightGlyphNames = thisDeletionGroup[1]
	
	for thisRightGlyphName in rightGlyphNames:
		try:
			Font.removeKerningForPair( masterID, leftGlyphName, thisRightGlyphName )
		except Exception, e:
			print "-- Error: could not delete pair %s %s (%s)" % ( leftGlyphName, thisRightGlyphName, e )


print "3. Pairs where selected glyphs are on the right side (may take a while):"

pairsToBeDeleted = []

for leftGlyphID in Font.kerning[ masterID ].keys():
	for rightGlyphID in Font.kerning[ masterID ][ leftGlyphID ].keys():
		if rightGlyphID in listOfIDs:
			pairsToBeDeleted.append( [ leftGlyphID, rightGlyphID ] )

print "4. Deleting these pairs ..."

for kernPair in pairsToBeDeleted:
	rightGlyphName = Font.glyphForId_( kernPair[1] ).name
	if kernPair[0][0] == "@":
		# left glyph is a class
		leftGlyphName = kernPair[0]
	else:
		# left glyph is a glyph
		leftGlyphName = Font.glyphForId_( kernPair[0] ).name
	
	# print "   Deleting pair: %s %s ..." % ( leftGlyphName, rightGlyphName )
	try:
		Font.removeKerningForPair( masterID, leftGlyphName, rightGlyphName )
	except Exception, e:
		print "-- Error: could not delete pair %s %s (%s)" % ( leftGlyphName, rightGlyphName, e )

totalNumberOfDeletions += ( len( pairsToBeDeleted ) )

print "Done: %i pairs deleted in %s." % ( totalNumberOfDeletions, Master.name )
