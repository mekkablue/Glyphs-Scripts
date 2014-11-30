#MenuTitle: Diacritic Ligature Maker
# -*- coding: utf-8 -*-
__doc__="""
For selected ligatures with appropriate anchors (top_1, top_2, etc.), all possible diacritic variations are created. E.g., A_h -> Adieresis_h, Aacute_h, A_hcircumflex, Adieresis_hcircumflex, etc.
"""

import GlyphsApp
import itertools

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
thisFontMasterID = thisFontMaster.id
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs
selectTool = NSClassFromString("GSToolSelect").alloc().init()

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

def ligatures( l1, l2 ):
	returnList = []
	for i in itertools.product( l1, l2 ):
		returnList.append("_".join( list(i) ))
	return returnList

def allLigaturesFromNameLists( l ):
	if len( l ) > 1:
		return ligatures( l[0], allLigaturesFromNameLists( l[1:] )  )
	else:
		return l[0]

def namesOfGlyphsContainingThisComponent( componentName ):
	listOfGlyphs = selectTool._glyphsContainingComponentWithName_font_masterID_( componentName, thisFont, thisMaster.id )
	nameList = [ g.name for g in listOfGlyphs ]
	return nameList

def createLigatureWithBaseLigature( newLigatureName, baseGlyphName ):
	individualGlyphNames = newLigatureName.split("_")
	diacriticComponents = [ thisFont.glyphs[n].layers[thisFontMasterID].components[1] for n in individualGlyphNames ]
	baseGlyphAnchorNames = [a.name for a in thisFont.glyphs[baseGlyphName].layers[thisFontMasterID].anchors]
	baseGlyphAnchorNameLists = [ [ "_%s" % a[:-2] for a in baseGlyphAnchorNames if a.endswith("_%i" % (i+1)) ] for i in range(len(individualGlyphNames)) ]
	
	newGlyph = GSGlyph()
	newGlyph.name = newLigatureName
	thisFont.glyphs.append( newGlyph )
	
	for thisLayerID in [m.id for m in thisFont.masters]:
		
		# add base ligature:
		thisLayer = newGlyph.layers[thisLayerID]
		thisLayer.addComponent_( GSComponent(baseGlyphName) )
		
		# add marks:
		for i in range(len(diacriticComponents)):
			thisComponent = diacriticComponents[i]
			if thisComponent:
				newComponent = GSComponent( thisComponent.componentName )
				thisLayer.addComponent_( newComponent )
				oldAnchor = thisComponent.anchor()
				if oldAnchor:
					newAnchor = "%s_%i" % ( oldAnchor, i+1 )
				else:
					anchorBaseName = [ a.name[1:] for a in thisComponent.component.layers[thisMaster.id].anchors if a.name in baseGlyphAnchorNameLists[i] ][0]
					newAnchor = "%s_%i" % ( anchorBaseName, i+1 )
				
				print "       %s -> %s" % ( thisComponent.componentName, newAnchor )
				newComponent.setAnchor_( newAnchor )
	
def process( thisLigatureName ):
	thisLigatureNameWithoutExtension = thisLigatureName.split(".")[0]
	namesOfLigatureLetters = thisLigatureNameWithoutExtension.split("_")
	diacriticLetterLists = [ [n]+namesOfGlyphsContainingThisComponent(n) for n in namesOfLigatureLetters ]
	listOfLigatures = [ n for n in allLigaturesFromNameLists( diacriticLetterLists ) if n != thisLigatureNameWithoutExtension ]
	for diacriticLigatureName in listOfLigatures:
		if not thisFont.glyphs[diacriticLigatureName]:
			print "    Creating %s" % diacriticLigatureName
			createLigatureWithBaseLigature( diacriticLigatureName, thisLigatureName )
		else:
			print "    Skipping %s: already exists in font" % diacriticLigatureName
	return listOfLigatures

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

allNewLigatures = []

for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyphName = thisGlyph.name

	print "Creating variations for %s:" % thisGlyphName
	thisGlyph.beginUndo() # begin undo grouping
	allNewLigatures += process( thisGlyphName )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View

print "\nCopy and paste this paragraph in an Edit Tab to see all ligatures mentioned above:\n\n/%s\n" % ( "/".join(allNewLigatures) )