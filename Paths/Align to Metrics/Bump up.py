#MenuTitle: Bump up
# -*- coding: utf-8 -*-
__doc__="""
Align selected components, paths (and parts of paths) to the next metric line or guideline above.
"""



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
			highestPathY = max( n.y for n in selection if type(n) == GSNode )
		except:
			# No path selected
			highestPathY = None
		
		try:
			highestCompY = max( (c.bounds.origin.y + c.bounds.size.height) for c in selection if type(c) == GSComponent )
		except:
			# No component selected
			highestCompY = None
			
		highestY = max( y for y in [highestCompY, highestPathY] if y != None )
	
		try:
			nextMetricLineAbove = min( ( m for m in allMetrics if m > highestY ) )
		except:
			nextMetricLineAbove = max( allMetrics )

		Font.disableUpdateInterface()

		for thisThing in selection:
			thisType = type(thisThing)
			if thisType == GSNode or thisType == GSComponent:
				thisThing.y += ( nextMetricLineAbove - highestY )

		Font.enableUpdateInterface()
	
except Exception, e:
	print "Error. Cannot bump selection:"
	print selection
	print e
