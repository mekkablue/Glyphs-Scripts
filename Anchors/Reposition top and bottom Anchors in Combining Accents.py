#MenuTitle: Reposition top & bottom Anchors in Combining Accents
# -*- coding: utf-8 -*-
__doc__="""
On all layers in selected glyphs, repositions top/bottom anchors for stacking in all top/bottom combining marks in line with the italic angle of the respective master. Keeps the anchor's y height, only moves horizontally.
"""

import math

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def italicize( thisPoint, italicAngle=0.0, pivotalY=0.0 ):
	"""
	Returns the italicized position of an NSPoint 'thisPoint'
	for a given angle 'italicAngle' and the pivotal height 'pivotalY',
	around which the italic slanting is executed, usually half x-height.
	Usage: myPoint = italicize(myPoint,10,xHeight*0.5)
	"""
	x = thisPoint.x
	yOffset = thisPoint.y - pivotalY # calculate vertical offset
	italicAngle = math.radians( italicAngle ) # convert to radians
	tangens = math.tan( italicAngle ) # math.tan needs radians
	horizontalDeviance = tangens * yOffset # vertical distance from pivotal point
	x += horizontalDeviance # x of point that is yOffset from pivotal point
	return NSPoint( x, thisPoint.y )

def process( thisLayer ):
	for anchorName in ("_top", "_bottom"):
		underscoreAnchor = thisLayer.anchors[anchorName]
		if underscoreAnchor:
			
			# look for anchor without underscore (_top -> top): defaultAnchor
			defaultAnchorName = anchorName[1:]
			defaultAnchor = thisLayer.anchors[defaultAnchorName]
			
			# if found, try to move it:
			if defaultAnchor:
				
				# record original position:
				oldPosition = defaultAnchor.position
				
				# determine italic angle and move the anchor accordingly:
				italicAngle = thisLayer.associatedFontMaster().italicAngle
				straightPosition = NSPoint( underscoreAnchor.position.x, defaultAnchor.position.y )
				if italicAngle:
					defaultAnchor.position = italicize( straightPosition, italicAngle, underscoreAnchor.position.y )
				else:
					defaultAnchor.position = straightPosition
				
				# compare new position to original position, and report if moved:
				if defaultAnchor.position != oldPosition:
					print "   Moved %s on layer '%s'" % ( anchorName[1:], thisLayer.name )
		else:
			# create defaultAnchor and append it
			# perhaps a bad idea
			pass

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

selectedCombiningMarks = [ g for g in [l.parent for l in thisFont.selectedLayers] if g.category=="Mark" and g.subCategory=="Nonspacing" ]

if selectedCombiningMarks:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()

	for thisMark in selectedCombiningMarks:
		thisMark.beginUndo() # begin undo grouping
		print "Processing %s" % thisMark.name
		for thisLayer in thisMark.layers:
			process( thisLayer )
		thisMark.endUndo()   # end undo grouping
else:
	Message("No Comb Marks in Selection", "No combining marks selected. Select the combining marks you want to process and try again.", OKButton="OK, got it!")

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
