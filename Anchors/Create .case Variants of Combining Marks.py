#MenuTitle: Create .case Variants of Combining Marks
# -*- coding: utf-8 -*-
__doc__="""
Creates missing .case duplicates of combining marks and shifts them above the cap height.
"""

from math import tan, radians

suffix = "case"
thisFont = Glyphs.font # frontmost font
listOfCombiningMarks = [ g for g in thisFont.glyphs if g.category=="Mark" and g.subCategory=="Nonspacing" ]
listOfMarkNames = [ g.name for g in listOfCombiningMarks ]

def italicize( thisPoint, italicAngle=0.0, pivotalY=0.0 ):
	x = thisPoint.x
	yOffset = thisPoint.y - pivotalY # calculate vertical offset
	italicAngle = radians( italicAngle ) # convert to radians
	tangens = tan( italicAngle ) # math.tan needs radians
	horizontalDeviance = tangens * yOffset # vertical distance from pivotal point
	return horizontalDeviance # x of point that is yOffset from pivotal point

def process( thisLayer ):
	anchorNames = [a.name for a in thisLayer.anchors]
	topAnchorName = "_top"
	if topAnchorName in anchorNames:
		
		master = thisLayer.associatedFontMaster()

		# determine y shift:
		capHeight = master.capHeight
		diffToCap = capHeight - thisLayer.anchors[topAnchorName].y
		
		# determine x shift:
		italicOffset = 0.0
		italicAngle = master.italicAngle
		if italicAngle != 0.0:
			italicOffset = italicize( NSPoint(0,diffToCap), italicAngle )
		
		# execute shift:
		shifting = NSAffineTransform.transform()
		shifting.translateXBy_yBy_( italicOffset, diffToCap )
		thisLayer.transform_checkForSelection_( shifting, False )
		print "   %s shifted %.1f %.1f" % (thisLayer.name, italicOffset, diffToCap)
		

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

for thisMark in listOfCombiningMarks:
	thisMarkName = thisMark.name
	if not "." in thisMarkName:
		caseName = "%s.%s" % (thisMarkName, suffix)
		if not caseName in listOfMarkNames:
			caseMark = thisMark.copy()
			caseMark.name = caseName
			caseMark.unicode = None
			thisFont.glyphs.append(caseMark)
			
			print "Created %s:" % caseName
			for markLayer in thisFont.glyphs[caseName].layers:
				process(markLayer)
			
		
thisFont.enableUpdateInterface() # re-enables UI updates in Font View
