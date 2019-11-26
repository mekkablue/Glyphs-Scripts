#MenuTitle: New Tab with Offcurves as Start Points
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
Opens a new tab with all glyphs that contain paths where the first point is an offcurve.
"""

def isLayerAffected( Layer ):
	isAffected = False
	for p in Layer.paths:
		scenario1 = p.nodes[0].type == OFFCURVE and p.nodes[1].type != OFFCURVE
		scenario2 = p.nodes[0].type == CURVE and p.nodes[-1].type == OFFCURVE
		if scenario1 or scenario2:
			p.selected = True
			isAffected = True
	return isAffected

thisFont = Glyphs.font # frontmost font
Glyphs.clearLog()
print("Looking for Offcurve Start Points in: %s" % thisFont.familyName)

affectedGlyphNames = []
for thisGlyph in thisFont.glyphs:
	print("Analysing %s:" % thisGlyph.name, end=' ')
	isAffected = False
	for thisLayer in thisGlyph.layers:
		if isLayerAffected( thisLayer ):
			isAffected = True
			print(u"\n  ⚠️ Offcurve start point on layer '%s'." % thisLayer.name)
	if isAffected:
		affectedGlyphNames.append(thisGlyph.name)
	else:
		print("OK.")

if affectedGlyphNames:
	tabString = "/" + "/".join(affectedGlyphNames)
	thisFont.newTab( tabString )
else:
	Message(
		title="No Starting Offcurves Found", 
		message="There are no layers that have an offcurve as start point. Congratulations!", 
		OKButton="Good"
	)



