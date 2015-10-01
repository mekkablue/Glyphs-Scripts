#MenuTitle: Bump right
# -*- coding: utf-8 -*-
__doc__="""
Align selected paths (and parts of paths) to the next sidebearing or glyph center to the right.
"""

import GlyphsApp

Font = Glyphs.font
Doc = Glyphs.currentDocument
Master = Font.selectedFontMaster
allMetrics = [ 0.0, selectedLayer.width, selectedLayer.width//2 ]
selectedLayer = Font.selectedLayers[0]

try:
	try:
		# until v2.1:
		selection = selectedLayer.selection()
	except:
		# since v2.2:
		selection = selectedLayer.selection
	
	rightMostX = max( ( n.x for n in selection ) )
	try:
		nextMetricLineToTheRight = min( ( m for m in allMetrics if m > rightMostX ) )
	except:
		nextMetricLineToTheRight = max( allMetrics )

	Font.disableUpdateInterface()

	for thisNode in selection:
		thisNode.x += ( nextMetricLineToTheRight - rightMostX )

	Font.enableUpdateInterface()
	
except Exception, e:
	if selection == ():
		print "Cannot bump right: nothing selected in frontmost layer."
	else:
		print "Error. Cannot bump selection:", selection
		print e
