#MenuTitle: Decompose Corners and Caps
# -*- coding: utf-8 -*-
__doc__="""
Decomposes all corner and cap components in selected glyphs. Reports to Macro Window.
"""

def process( layer ):
	count = 0
	for thisHint in layer.hints:
		if thisHint.type == CORNER or thisHint.type == CAP:
			count += 1
	if count:
		layer.decomposeCorners()
		print u"   👊 Decomposed %i caps and/or corners" % count

Glyphs.clearLog() # clear macro window log

thisFont = Glyphs.font
for thisLayer in thisFont.selectedLayers:
	thisGlyph = thisLayer.parent
	print "Processing", thisGlyph.name
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()
