# MenuTitle: Select All Local Guides in Selected Glyphs
__doc__ = """
Selects all guides in the selected glyph(s).
"""
from mekkablue import guidesOf
from GlyphsApp import Glyphs

thisFont = Glyphs.font  # frontmost font
selectedLayers = thisFont.selectedLayers if thisFont else []  # active layers of selected glyphs


def selectGuidesOnLayer(thisLayer):
	thisLayer.clearSelection()
	for thisGuide in guidesOf(thisLayer):
		thisLayer.selection.append(thisGuide)
	return len(thisLayer.selection)


if thisFont is None:
	print("⚠️ No font open.")
else:
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		numberOfGuides = selectGuidesOnLayer(thisLayer)
		print("Selected %i guides in %s" % (numberOfGuides, thisGlyph.name))
