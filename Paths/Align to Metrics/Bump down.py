#MenuTitle: Bump down
"""Align selected paths (and parts of paths) to the next metric line below."""

import GlyphsApp

Font = Glyphs.font
Doc = Glyphs.currentDocument
Master = Font.selectedFontMaster
allMetrics = [ Master.ascender, Master.capHeight, Master.xHeight, 0.0, Master.descender ]

selectedLayer = Font.selectedLayers[0]

try:
	selection = selectedLayer.selection()
	lowestY = min( ( n.y for n in selection ) )
	try:
		nextMetricLineBelow = max( ( m for m in allMetrics if m < lowestY ) )
	except:
		nextMetricLineBelow = min( allMetrics )

	Font.disableUpdateInterface()

	for thisNode in selection:
		thisNode.y -= ( lowestY - nextMetricLineBelow )

	Font.enableUpdateInterface()
	
except Exception, e:
	if selection == ():
		print "Cannot bump down: nothing selected in frontmost layer."
	else:
		print "Error. Cannot bump selection:", selection
		print e
