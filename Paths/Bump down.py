#MenuTitle: Bump down
"""Align selected paths (and parts of paths) to the next metric line below."""

import GlyphsApp

selectedLayer = Glyphs.font.selectedLayers[0]

try:
	selectedLayer.setDisableUpdates()
	allMetrics = sorted(selectedLayer.glyphMetrics()[1:-2]) # glyphMetrics returnes a tupel (width, ascender, capHeight, descender, xHeight, italicAngle, vertWidth)
	selection = selectedLayer.selection()
	lowestY = min( ( n.y for n in selection ) )
	try:
		nextMetricLineBelow = max( ( m for m in allMetrics if m < lowestY ) )
	except:
		nextMetricLineBelow = min( allMetrics )
	
	for thisNode in selection:
		thisNode.y -= ( lowestY - nextMetricLineBelow )
	
	selectedLayer.setEnableUpdates()
	
except Exception, e:
	if selection == ():
		print "Cannot bump down: nothing selected in frontmost layer."
	else:
		print "Error. Cannot bump selection:", selection
		print e
