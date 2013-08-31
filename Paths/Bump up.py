#MenuTitle: Bump up
"""Align selected paths (and parts of paths) to the next metric line above."""

import GlyphsApp

Font = Glyphs.font
Master = Font.selectedFontMaster
allMetrics = [ Master.ascender, Master.capHeight, Master.xHeight, 0.0, Master.descender ]

selectedLayer = Font.selectedLayers[0]

try:
	selectedLayer.setDisableUpdates()
	
	selection = selectedLayer.selection()
	highestY = max( ( n.y for n in selection ) )
	try:
		nextMetricLineAbove = min( ( m for m in allMetrics if m > highestY ) )
	except:
		nextMetricLineAbove = max( allMetrics )
	
	for thisNode in selection:
		thisNode.y += ( nextMetricLineAbove - highestY )
	
	selectedLayer.setEnableUpdates()
	
except Exception, e:
	if selection == ():
		print "Cannot bump up: nothing selected in frontmost layer."
	else:
		print "Error. Cannot bump selection:", selection
		print e
