#MenuTitle: Bump right
"""Align selected paths (and parts of paths) to the next sidebearing or glyph center to the right."""

import GlyphsApp

Font = Glyphs.font
Doc = Glyphs.currentDocument
Master = Doc.selectedFontMaster()
selectedLayer = Doc.selectedLayers()[0]

allMetrics = [ 0.0, selectedLayer.width, selectedLayer.width//2 ]

try:
	selection = selectedLayer.selection()
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
