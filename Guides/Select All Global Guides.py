# MenuTitle: Select All Global Guides
__doc__ = """
Selects all global guides.
"""
from mekkablue import guidesOf
from GlyphsApp import Glyphs

thisFont = Glyphs.font  # frontmost font
selectedLayers = thisFont.selectedLayers if thisFont else []  # active layers of selected glyphs


def selectGuidesOnLayer(thisLayer):
	thisMaster = thisLayer.master
	thisLayer.clearSelection()
	for thisGuide in guidesOf(thisMaster):
		thisLayer.selection.append(thisGuide)
	return len(thisLayer.selection)


if thisFont is None:
	print("⚠️ No font open.")
else:
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		numberOfGuides = selectGuidesOnLayer(thisLayer)
		print("Selected %i guides in %s" % (numberOfGuides, thisGlyph.name))
