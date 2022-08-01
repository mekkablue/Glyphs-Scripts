#MenuTitle: KernCrash Current Glyph
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Opens a new tab containing kerning combos with the current glyph that collide in the current fontmaster.
"""

from AppKit import NSNotFound, NSAffineTransform
from kernanalysis import effectiveKerning

exceptions="""
.notdef
Ldot ldot ldot.sc
Jacute jacute jacute.sc
periodcentered.loclCAT periodcentered.loclCAT.case periodcentered.loclCAT.sc
currency
emptyset
infinity
integral
product
summation
radical
partialdiff
lozenge
paragraph
asciicircum
"""

# def effectiveKerning( leftGlyphName, rightGlyphName, thisFont, thisFontMasterID):
	
# 	leftLayer = thisFont.glyphs[leftGlyphName].layers[thisFontMasterID]
# 	rightLayer = thisFont.glyphs[rightGlyphName].layers[thisFontMasterID]
# 	if Glyphs.versionNumber < 3:
# 		effectiveKerning = leftLayer.rightKerningForLayer_( rightLayer )
# 	else:
		
# 		effectiveKerning = leftLayer.nextKerningForLayer_direction_(rightLayer, leftLayer.parent.direction)
# 	if effectiveKerning < NSNotFound:
# 		return effectiveKerning
# 	else:
# 		return 0.0

def pathCountOnLayer( thisLayer ):
	thisLayer.removeOverlap()
	return len( thisLayer.paths )

def pathCount( thisGlyph, thisFontMasterID ):
	thisLayer = thisGlyph.layers[thisFontMasterID].copyDecomposedLayer()
	return pathCountOnLayer(thisLayer)

def pathCountForGlyphName( glyphName, thisFont, thisFontMasterID ):
	thisGlyph = thisFont.glyphs[glyphName]
	return pathCount( thisGlyph, thisFontMasterID )

def pathCountInKernPair( firstGlyphName, secondGlyphName, thisFont, thisFontMasterID, minDistance ):
	#ligatureName = "%s_%s" % ( nameUntilFirstPeriod(firstGlyphName), nameUntilFirstPeriod(secondGlyphName) )
	#newGlyph = thisFont.newGlyphWithName_changeName_( "_deleteMe", False )

	ligatureLayer = thisFont.glyphs[secondGlyphName].layers[thisFontMasterID].copyDecomposedLayer()
	addedLayer = thisFont.glyphs[firstGlyphName].layers[thisFontMasterID].copyDecomposedLayer()
	
	# position of right component:
	kerning = effectiveKerning( firstGlyphName, secondGlyphName, thisFont, thisFontMasterID )
	rightShift = NSAffineTransform.transform()
	rightShift.translateXBy_yBy_( addedLayer.width + kerning - minDistance, 0.0 )
	ligatureLayer.transform_checkForSelection_( rightShift, False )
	
	for addedPath in addedLayer.paths:
		if Glyphs.versionNumber < 3:
			ligatureLayer.addPath_( addedPath.copy() )
		else:
			ligatureLayer.addShape_( addedPath.copy() )
	
	return pathCountOnLayer( ligatureLayer )

try:
	# query frontmost fontmaster:
	thisFont = Glyphs.font
	thisFontMaster = thisFont.selectedFontMaster
	thisFontMasterID = thisFontMaster.id
	if not thisFont.selectedLayers:
		Message(title="No glyph selected", message="The script could not determine the current glyph. Please select a glyph and try again.", OKButton=None)
	else:
		thisGlyph = thisFont.selectedLayers[0].parent
	
		# brings macro window to front and clears its log:
		Glyphs.clearLog()
		Glyphs.showMacroWindow()
	
		print("KernCrash Current Glyph Report for %s, master %s:\n" % (thisFont.familyName, thisFontMaster.name))
	
		# get list of glyph names:
		currentGlyphName = thisGlyph.name
		exceptionList = exceptions.split()
		completeSet = [g.name for g in thisFont.glyphs
						if g.export
						and g.name not in exceptionList # excluded glyphs, list at beginning of this .py
						and g.subCategory != "Nonspacing" # no combining accents
					]
	
		# get pathcounts for every glyph:
		pathCountDict = {}
		for thisGlyphName in completeSet:
			pathCountDict[thisGlyphName] = pathCountForGlyphName( thisGlyphName, thisFont, thisFontMasterID )
	
		# all possible kern pairs:
		tabStringLeftGlyphs = []
		tabStringRightGlyphs = []
	
		for otherGlyphName in completeSet:
			firstCount = pathCountDict[currentGlyphName]
			secondCount = pathCountDict[otherGlyphName]
		
			# current glyph on left side:
			kernCount = pathCountInKernPair( currentGlyphName, otherGlyphName, thisFont, thisFontMasterID, 0.0 )
			if firstCount + secondCount > kernCount:
				tabStringLeftGlyphs.append(otherGlyphName)
				# += "/%s/%s/space" % ( firstGlyphName, secondGlyphName )
				
			# current glyph on left side:
			kernCount = pathCountInKernPair( otherGlyphName, currentGlyphName, thisFont, thisFontMasterID, 0.0 )
			if firstCount + secondCount > kernCount:
				tabStringRightGlyphs.append(otherGlyphName)
				#tabStringLeft += "/%s/%s/space" % ( firstGlyphName, secondGlyphName )

		# open new Edit tab:
		if tabStringLeftGlyphs or tabStringRightGlyphs:
			Glyphs.showNotification('KernCrash Current Glyph', 'Some kerning crashes have been found.')
			# opens new Edit tab:
			tabStrings = []
			if tabStringLeftGlyphs:
				inBetween = "  /%s/" % currentGlyphName
				tabStrings.append( "/%s/"%currentGlyphName + inBetween.join(tabStringLeftGlyphs) )
				print("Colliding glyphs when %s is on the LEFT:\n%s\n" % ( currentGlyphName, " ".join(tabStringLeftGlyphs) ))
			if tabStringRightGlyphs:
				inBetween = "/%s  /" % currentGlyphName
				tabStrings.append( "/" + inBetween.join(tabStringRightGlyphs) + "/%s"%currentGlyphName )
				print("Colliding glyphs when %s is on the RIGHT:\n%s\n" % ( currentGlyphName, " ".join(tabStringRightGlyphs) ))
			
			thisFont.newTab( "\n\n".join(tabStrings) )
			# Floating notification:
			Glyphs.showNotification( 
				"KernCrashed %s, master ‘%s’" % (thisFont.familyName, thisFontMaster.name),
				"Found %i kerning collisions with %s. Details in Macro Window" % ( len(tabStringRightGlyphs)+len(tabStringLeftGlyphs), currentGlyphName ),
				)
			
		# or report that nothing was found:
		else:
			# Floating notification:
			Glyphs.showNotification( 
				"KernCrashed %s, master ‘%s’:" % (thisFont.familyName, thisFontMaster.name),
				"No collisions found for %s." % currentGlyphName,
				)
except Exception as e:
	Message("KernCrash Error", "KernCrash Current Glyph Error: %s\nTraceback in Macro Window." % e, OKButton=None)
	import traceback
	print(traceback.format_exc())
	print(pathCountDict)
