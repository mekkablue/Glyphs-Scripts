#MenuTitle: Align all Arabic Double Marks in Current Master
# -*- coding: utf-8 -*-
__doc__="""
Re-aligns components in double marks (like shadda_damma-ar) to each other according to their anchors. Only for the current master.
"""



# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
thisFontMasterName = thisFontMaster.name # active master name
thisFontMasterID = thisFontMaster.id # active master ID
listOfDoubleMarkGlyphs = [ g for g in Font.glyphs if "_" in g.name and g.name.endswith("-ar") and g.category == "Mark" ]

topBottomMarkLigatureNames = [ "shadda_kasra-ar", "shadda_kasratan-ar" ]

# sorry for the mess, this code needs some cleanup:

def errMsg( msg ):
	print "   Error: %s" % msg

def anchorDiffOrBaseOrMark( thisMarkLayer, whichOfTheThree ):
	"""
	whichOfTheThree = 0 ... anchorDiff (top <-> _top)
	whichOfTheThree = 1 ... base (top)
	whichOfTheThree = 2 ... mark (_top)
	"""
	defaultPosition = NSPoint( 0.0, 0.0 )
	theseAnchors = thisMarkLayer.anchors
	if len(theseAnchors) > 0:
		listOfUnderscoreAnchors = [ a for a in theseAnchors if a.name.startswith("_") ]
		listOfNormalAnchorNames = [ a.name for a in theseAnchors if not a.name.startswith("_") ]
		if listOfUnderscoreAnchors == []:
			errMsg( "no mark anchor (with underscore at beginning) in %s." % thisMarkLayer.parent.name )
			return defaultPosition
		else:
			for i in range(len(listOfUnderscoreAnchors)):
				markAnchor = listOfUnderscoreAnchors[i]
				markPosition = markAnchor.position
				baseAnchorName = markAnchor.name[1:]
				if baseAnchorName in listOfNormalAnchorNames:
					baseAnchor = [ a for a in thisMarkLayer.anchors if a.name == baseAnchorName ][0]
					basePosition = baseAnchor.position
					if whichOfTheThree == 0:
						anchorDiff = substractPoints( basePosition, markPosition )
						return anchorDiff
					if whichOfTheThree == 1:
						return basePosition
					elif whichOfTheThree == 2:
						return markPosition
			errMsg( "In %s, there are no corresponding base anchors for any of these mark anchors: %s." % ( thisMarkLayer.parent.name, ", ".join([a.name for a in listOfUnderscoreAnchors]) ) )
			return defaultPosition
	else:
		errMsg( "no anchors in %s." % thisMarkLayer.parent.name )
		return defaultPosition

def anchorDiff( thisMarkLayer ):
	return anchorDiffOrBaseOrMark( thisMarkLayer, 0 )

def basePosition( thisMarkLayer ):
	return anchorDiffOrBaseOrMark( thisMarkLayer, 1 )

def markPosition( thisMarkLayer ):
	return anchorDiffOrBaseOrMark( thisMarkLayer, 2 )

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

for thisGlyph in listOfDoubleMarkGlyphs:
	thisGlyphName = thisGlyph.name
	currentLayer = thisGlyph.layers[thisFontMasterID]
	specialCase = thisGlyphName in topBottomMarkLigatureNames
	print "Aligning components in %s (Master %s)." % ( thisGlyphName, thisFontMasterName )
	if len(currentLayer.paths) == 0:
		markdiffs = []
		lastBaseAnchorPosition = NSPoint( 0.0, 0.0 )
		for i in range(len(currentLayer.components)):
			thisComponent = currentLayer.components[i]
			if i == 0: # first component
				thisComponent.setPosition_( lastBaseAnchorPosition )
				if specialCase:
					# kasra and kasratan need to connect to shadda's _top (not top)
					lastBaseAnchorPosition = markPosition( thisComponent.component.layers[thisFontMasterID] )
				else:
					lastBaseAnchorPosition = basePosition( thisComponent.component.layers[thisFontMasterID] )
			else: # following components
				# move thisComponent:
				currentMarkAnchorPosition = markPosition( thisComponent.component.layers[thisFontMasterID] )
				componentPosition = substractPoints( lastBaseAnchorPosition, currentMarkAnchorPosition )
				thisComponent.setPosition_( componentPosition )
				# update lastBasePosition:
				thisAnchorDiff = anchorDiff( thisComponent.component.layers[thisFontMasterID] )
				lastBaseAnchorPosition = addPoints( lastBaseAnchorPosition, thisAnchorDiff )

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
