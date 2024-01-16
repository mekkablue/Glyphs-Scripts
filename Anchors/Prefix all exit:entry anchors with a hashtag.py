# MenuTitle: Prefix all exit & entry anchors with a hashtag
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Looks for all exit and entry anchors anywhere in the font, and disables curs feature generation.
"""

from GlyphsApp import Glyphs, Message


def processLayer(thisLayer):
	foundExitOrEntry = False
	for thisAnchor in thisLayer.anchors:
		if thisAnchor.name in ("exit", "entry"):
			thisAnchor.name = "#%s" % thisAnchor.name
			foundExitOrEntry = True
	return foundExitOrEntry


def processGlyph(thisGlyph):
	layerCount = 0
	for thisLayer in thisGlyph.layers:
		if processLayer(thisLayer):
			layerCount += 1
	if layerCount:
		print("%s: changed anchor names on %i layer%s" % (
			thisGlyph.name,
			layerCount,
			"" if layerCount == 1 else "s",
		))
		return 1

	return 0


# brings macro window to front and clears its log:
Glyphs.clearLog()
thisFont = Glyphs.font  # frontmost font

print("Looking for exit/entry in %s:" % thisFont.familyName)
print(thisFont.filepath)
print("Scanning %i glyphs..." % len(thisFont.glyphs))
print()
glyphCount = 0
for thisGlyph in thisFont.glyphs:
	# thisGlyph.beginUndo()  # undo grouping causes crashes
	glyphCount += processGlyph(thisGlyph)
	# thisGlyph.beginUndo()  # undo grouping causes crashes

reportMessage = "Hashtagged exit/entry anchors in %i glyph%s." % (
	glyphCount,
	"" if glyphCount == 1 else "s",
)

print("\n%s\nDone." % reportMessage)
Message(title="Exit/Entry Prefix Report", message="Font ‘%s’: %s Detailed report in Macro Window." % (thisFont.familyName, reportMessage), OKButton=None)
