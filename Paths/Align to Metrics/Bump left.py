#MenuTitle: Bump left
"""Align selected paths (and parts of paths) to the next sidebearing or glyph center to the left."""

import GlyphsApp

Font = Glyphs.font
Doc = Glyphs.currentDocument
Master = Font.selectedFontMaster
selectedLayer = Font.selectedLayers[0]

allMetrics = [ 0.0, selectedLayer.width, selectedLayer.width//2 ]

try:
	selection = selectedLayer.selection()
	leftMostX = min( ( n.x for n in selection ) )
	try:
		nextMetricLineToTheLeft = max( ( m for m in allMetrics if m < leftMostX ) )
	except:
		nextMetricLineToTheLeft = min( allMetrics )

	Font.disableUpdateInterface()

	for thisNode in selection:
		thisNode.x -= ( leftMostX - nextMetricLineToTheLeft )

	Font.enableUpdateInterface()
	
except Exception, e:
	if selection == ():
		print "Cannot bump left: nothing selected in frontmost layer."
	else:
		print "Error. Cannot bump selection:", selection
		print e
