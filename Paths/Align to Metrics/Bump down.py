#MenuTitle: Bump down
# -*- coding: utf-8 -*-
__doc__="""
Align selected components, paths (and parts of paths) to the next metric line or guideline below.
"""

import GlyphsApp

Font = Glyphs.font
Doc = Glyphs.currentDocument
Master = Font.selectedFontMaster
allMetrics = [ Master.ascender, Master.capHeight, Master.xHeight, 0.0, Master.descender ] + [ g.y for g in Master.guideLines if g.angle == 0.0 ]

selectedLayer = Font.selectedLayers[0]

try:
	try:
		# until v2.1:
		selection = selectedLayer.selection()
	except:
		# since v2.2:
		selection = selectedLayer.selection
	
	if selection:
		try:
			lowestPathY = min( n.y for n in selection if type(n) == GSNode )
		except:
			# No path selected
			lowestPathY = None
		
		try:
			lowestCompY = min( c.bounds.origin.y for c in selection if type(c) == GSComponent )
		except:
			# No component selected
			lowestCompY = None
			
		lowestY = min( y for y in [lowestCompY, lowestPathY] if y != None )

		try:
			nextMetricLineBelow = max( ( m for m in allMetrics if m < lowestY ) )
		except:
			nextMetricLineBelow = min( allMetrics )

		Font.disableUpdateInterface()

		for thisThing in selection:
			thisType = type(thisThing)
			if thisType == GSNode or thisType == GSComponent:
				thisThing.y -= ( lowestY - nextMetricLineBelow )

		Font.enableUpdateInterface()
	
except Exception, e:
	if selection == ():
		print "Cannot bump down: nothing selected in frontmost layer."
	else:
		print "Error. Cannot bump selection:", selection
		print e
