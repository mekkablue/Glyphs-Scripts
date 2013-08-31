#MenuTitle: Bump right
"""Align selected paths (and parts of paths) to the next sidebearing or glyph center to the right."""

import GlyphsApp

Font = Glyphs.font
Master = Font.selectedFontMaster
selectedLayer = Font.selectedLayers[0]

allMetrics = [ 0.0, selectedLayer.width, selectedLayer.width//2 ]

try:
	selectedLayer.setDisableUpdates()
	
	selection = selectedLayer.selection()
	rightMostX = max( ( n.x for n in selection ) )
	try:
		nextMetricLineToTheRight = min( ( m for m in allMetrics if m > rightMostX ) )
	except:
		nextMetricLineToTheRight = max( allMetrics )
	
	for thisNode in selection:
		thisNode.x += ( nextMetricLineToTheRight - rightMostX )
	
	selectedLayer.setEnableUpdates()

except Exception, e:
	if selection == ():
		print "Cannot bump right: nothing selected in frontmost layer."
	else:
		print "Error. Cannot bump selection:", selection
		print e
