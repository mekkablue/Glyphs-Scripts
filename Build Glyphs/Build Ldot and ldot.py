#MenuTitle: Build Ldot and ldot
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Builds Ldot, ldot and ldot.sc from existing L and periodcentered.loclCAT(.case/.sc).
"""

from Foundation import NSPoint

def buildLdot( targetGlyphName, baseName, accentName ):
	try:
		print("\n%s + %s = %s" % ( baseName, accentName, targetGlyphName ))
		for thisMaster in thisFont.masters:
			print("\tProcessing master: %s" % thisMaster.name)
			thisMasterID = thisMaster.id
			offsetAccent = thisFont.glyphs[baseName].layers[thisMasterID].width
			accentWidth = thisFont.glyphs[accentName].layers[thisMasterID].width
			baseWidth = thisFont.glyphs[baseName].layers[thisMasterID].width
			targetGlyph = thisFont.glyphs[targetGlyphName]
			if not targetGlyph:
				targetGlyph = GSGlyph(targetGlyphName)
				thisFont.glyphs.append(targetGlyph)
			else:
				targetGlyph.leftMetricsKey = None
				targetGlyph.rightMetricsKey = None
			targetLayer = targetGlyph.layers[thisMasterID]
			try:
				targetLayer.shapes = None
				targetLayer.shapes.append( GSComponent( baseName ) )
				targetLayer.shapes.append( GSComponent( accentName, NSPoint( offsetAccent, 0.0) ) )
			except:
				targetLayer.components = []
				targetLayer.components.append( GSComponent( baseName ) )
				targetLayer.components.append( GSComponent( accentName, NSPoint( offsetAccent, 0.0) ) )
			for thisComp in targetLayer.components:
				thisComp.disableAlignment = False
			targetLayer.width = baseWidth + accentWidth
			targetLayer.leftMetricsKey = None
			targetLayer.rightMetricsKey = None
		return 1
	except:
		return 0

thisFont = Glyphs.font # frontmost font
Glyphs.clearLog() # clears macro window log
print("Report for %s:" % thisFont.familyName)
if thisFont.filepath:
	print(thisFont.filepath)

buildGlyphs = [
	("ldot", "l", "periodcentered.loclCAT"),
	("Ldot", "L", "periodcentered.loclCAT.case"),
	("ldot.sc", "l.sc", "periodcentered.loclCAT.sc")
]

createdGlyphs = []
for glyphInfo in buildGlyphs:
	target = glyphInfo[0]
	base = glyphInfo[1]
	accent = glyphInfo[2]
	
	if thisFont.glyphs[base] and thisFont.glyphs[accent]:
		if buildLdot( target, base, accent ):
			createdGlyphs.append(target)

reportMessage = "%i glyph%s created" % (
		len(createdGlyphs),
		"" if len(createdGlyphs)==1 else "s",
)

print("\nDone: %s." % reportMessage)

# Floating notification:
Glyphs.showNotification( 
	u"%s: %s" % (
		thisFont.familyName, 
		reportMessage,
	),
	u"Created %s. Detailed info in Macro Window." % (", ".join(createdGlyphs)),
	)

		