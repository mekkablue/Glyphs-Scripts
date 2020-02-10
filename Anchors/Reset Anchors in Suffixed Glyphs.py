#MenuTitle: Reset Anchors in Suffixed Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Deletes existing anchors in selected glyphs that have a dot suffix, and copies anchors from their unsuffixed counterpart into them. E.g., puts anchors from A into A.swsh.
"""

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
Glyphs.clearLog() # clears log in Macro window

def process( thisLayer ):
	glyph = thisLayer.parent
	if not glyph:
		print("- No glyph found for layer '%s'"%thisLayer.name)
	else:
		originalGlyphName = glyph.name[:glyph.name.find(".")]
		originalGlyph = thisFont.glyphs[originalGlyphName]
		
		if not originalGlyph:
			print("- Glyph '%s' not found. Skipping." % originalGlyphName)
		else:
			masterID = thisLayer.master.id
			originalLayer = originalGlyph.layers[masterID]
			thisLayer.anchors = None
			for originalAnchor in originalLayer.anchors:
				thisAnchor = GSAnchor()
				thisAnchor.name = originalAnchor.name
				thisAnchor.position = originalAnchor.position
				thisLayer.anchors.append(thisAnchor)
				print("- %s: %.1f %.1f" % ( thisAnchor.name, thisAnchor.x, thisAnchor.y ))
	


for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	if "." in thisGlyph.name[1:]:
		print("\nResetting anchors in %s:" % thisGlyph.name)
		thisGlyph.beginUndo() # begin undo grouping
		process( thisLayer )
		thisGlyph.endUndo()   # end undo grouping
