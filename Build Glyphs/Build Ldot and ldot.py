#MenuTitle: Build Ldot and ldot
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
Builds Ldot, ldot and ldot.sc from existing L and periodcentered.loclCAT(.case/.sc).
"""

from Foundation import NSPoint

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def buildLdot( targetGlyphName, baseName, accentName ):
	print("%s + %s = %s" % ( baseName, accentName, targetGlyphName ))
	for thisMaster in thisFont.masters:
		print("Processing", thisMaster)
		thisMasterID = thisMaster.id
		offsetAccent = thisFont.glyphs[baseName].layers[thisMasterID].width
		accentWidth = thisFont.glyphs[accentName].layers[thisMasterID].width
		baseWidth = thisFont.glyphs[baseName].layers[thisMasterID].width
		targetGlyph = thisFont.glyphs[targetGlyphName]
		if not targetGlyph:
			targetGlyph = GSGlyph(targetGlyphName)
			thisFont.glyphs.append(targetGlyph)
		targetLayer = targetGlyph.layers[thisMasterID]
		targetLayer.components = []
		targetLayer.components.append( GSComponent( baseName ) )
		targetLayer.components.append( GSComponent( accentName, NSPoint( offsetAccent, 0.0) ) )
		for thisComp in targetLayer.components:
			thisComp.disableAlignment = False
		targetLayer.width = baseWidth + accentWidth

buildGlyphs = [
	("ldot", "l", "periodcentered.loclCAT"),
	("Ldot", "L", "periodcentered.loclCAT.case"),
	("ldot.sc", "l.sc", "periodcentered.loclCAT.sc")
]

for glyphInfo in buildGlyphs:
	target = glyphInfo[0]
	base = glyphInfo[1]
	accent = glyphInfo[2]
	
	if thisFont.glyphs[base] and thisFont.glyphs[accent]:
		buildLdot( target, base, accent )
		