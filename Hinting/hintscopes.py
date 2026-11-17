"""
Helper module (not a script) for Remove TT Hints and Remove PS Hints:
the scope popup, sorted by escalation, and the glyphs and layers a scope covers.
"""

from GlyphsApp import Glyphs

# sorted by escalation, from the least to the most layers that are affected:
scopes = (
	"current layer of selected glyphs",
	"all layers of selected glyphs",
	"this master",
	"all masters but this one",
	"all masters but the first one",
	"⚠️ the complete font",
	"⚠️ all open fonts",
)
completeFontScope = 5
allFontsScope = 6

scopeTooltip = (
	"Where the hints are removed:\n"
	"• current layer of selected glyphs: only the layer you see in each selected glyph\n"
	"• all layers of selected glyphs: every layer of each selected glyph, including other masters and special layers\n"
	"• this master: the layers of the selected master in all glyphs of the font\n"
	"• all masters but this one: the layers of all other masters in all glyphs of the font\n"
	"• all masters but the first one: the layers of all masters except the first in all glyphs of the font, e.g. before transferring the hints of the first master\n"
	"• the complete font: all layers of all glyphs of the frontmost font\n"
	"• all open fonts: all layers of all glyphs of all open fonts\n\n"
	"⚠️ Mind the bigger scopes: they remove hints in many glyphs with one click. Consider saving first."
)


def fontsForScope(scope):
	"""The fonts a scope covers: all open fonts, or the frontmost font."""
	if scope == allFontsScope:
		return tuple(Glyphs.fonts)
	return (Glyphs.font, ) if Glyphs.font else ()


def glyphsAndLayers(thisFont, scope):
	"""Returns pairs of (glyph, layers) in this font for the scope. The scope ‘all open fonts’ takes all layers."""
	pairs = []
	if scope == 0:
		# current layer of selected glyphs
		for layer in thisFont.selectedLayers:
			pairs.append((layer.parent, [layer]))
	elif scope == 1:
		# all layers of selected glyphs
		seenNames = set()
		for layer in thisFont.selectedLayers:
			glyph = layer.parent
			if glyph.name not in seenNames:
				seenNames.add(glyph.name)
				pairs.append((glyph, list(glyph.layers)))
	else:
		currentMasterID = thisFont.selectedFontMaster.id
		firstMasterID = thisFont.masters[0].id
		layerFilters = {
			2: lambda layer: layer.associatedMasterId == currentMasterID,  # this master
			3: lambda layer: layer.associatedMasterId != currentMasterID,  # all masters but this one
			4: lambda layer: layer.associatedMasterId != firstMasterID,  # all masters but the first one
		}
		layerFilter = layerFilters.get(scope, lambda layer: True)  # complete font and all open fonts
		for glyph in thisFont.glyphs:
			layers = [layer for layer in glyph.layers if layerFilter(layer)]
			if layers:
				pairs.append((glyph, layers))
	return pairs
