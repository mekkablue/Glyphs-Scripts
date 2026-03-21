# MenuTitle: Remove Metrics Keys
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Remove glyph-wide (=) and/or layer-specific (==) metrics keys. Optionally filter by referenced glyph name, and choose the scope from selected glyphs to all open fonts.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, match

scopeOptions = (
	"selected glyphs",
	"all masters of selected glyphs",
	"⚠️ complete current master",
	"⚠️ complete font",
	"⚠️ all open fonts",
)


class RemoveMetricsKeys(mekkaObject):
	prefDict = {
		"glyphWideKeys": 1,
		"layerSpecificKeys": 1,
		"glyphNameFilter": "",
		"scope": 3,
	}

	def __init__(self):
		windowWidth = 380
		windowHeight = 142
		windowWidthResize = 600
		windowHeightResize = 0
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Remove Metrics Keys",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight),
			autosaveName=self.domain("mainwindow"),
		)

		linePos, inset, lineHeight = 12, 15, 22

		# Row 1: label + two checkboxes on one line
		col1 = inset + 72  # checkboxes start here
		self.w.removeAllLabel = vanilla.TextBox(
			(inset, linePos + 3, 62, 14),
			"Remove all",
			sizeStyle="small",
		)
		self.w.glyphWideKeys = vanilla.CheckBox(
			(col1, linePos, 135, 20),
			"glyph-wide keys (=)",
			value=True,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.glyphWideKeys.setToolTip(
			"Remove metrics keys set on the glyph level (e.g. =H, =|H, =H+20). "
			"These apply across all masters by default."
		)
		self.w.layerSpecificKeys = vanilla.CheckBox(
			(col1 + 135, linePos, -inset, 20),
			"layer-specific keys (==)",
			value=True,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.layerSpecificKeys.setToolTip(
			"Remove metrics keys set on individual layers (e.g. ==H, ==|H). "
			"These override the glyph-wide key for a specific master."
		)
		linePos += lineHeight

		# Row 2: label + text field on one line
		filterLabelWidth = 122
		self.w.glyphNameFilterLabel = vanilla.TextBox(
			(inset, linePos + 3, filterLabelWidth, 14),
			"Only keys referencing:",
			sizeStyle="small",
		)
		self.w.glyphNameFilter = vanilla.EditText(
			(inset + filterLabelWidth, linePos, -inset, 19),
			"",
			callback=self.SavePreferences,
			sizeStyle="small",
			placeholder="any glyph (see tooltip)",
		)
		self.w.glyphNameFilter.setToolTip(
			"Comma-separated glyph names or wildcard patterns (e.g. H, n, a*). "
			"Only metrics keys that reference one of these glyph names will be removed. "
			"Wildcards: * matches any string, ? matches one character. "
			"Leave empty to remove all keys regardless of what they reference."
		)
		linePos += lineHeight

		# Row 3: scope label + fixed-width popup (does not grow with window)
		scopeLabelWidth = 64
		popupWidth = int((windowWidth - inset - (inset + scopeLabelWidth)) * 0.8)
		self.w.scopeLabel = vanilla.TextBox(
			(inset, linePos + 3, scopeLabelWidth, 14),
			"Remove in:",
			sizeStyle="small",
		)
		self.w.scope = vanilla.PopUpButton(
			(inset + scopeLabelWidth, linePos, popupWidth, 18),
			scopeOptions,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.scope.setToolTip(
			"Determines which glyphs and layers are affected:\n"
			"• Selected glyphs – current master layer of each selected glyph.\n"
			"• All masters of selected glyphs – all layers of each selected glyph.\n"
			"• ⚠️ Complete current master – all glyphs in the font, current master only.\n"
			"• ⚠️ Complete font – all glyphs in the font, all masters.\n"
			"• ⚠️ All open fonts – all glyphs in every open font, all masters."
		)

		# Status + regular-size button, side by side at the bottom
		self.w.status = vanilla.TextBox(
			(inset, -inset - 18, -inset - 90, 14),
			"",
			sizeStyle="small",
		)
		self.w.runButton = vanilla.Button(
			(-80 - inset, -22 - inset, -inset, -inset),
			"Remove",
			callback=self.run,
		)
		self.w.setDefaultButton(self.w.runButton)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		glyphWideOn = self.prefBool("glyphWideKeys")
		layerSpecificOn = self.prefBool("layerSpecificKeys")
		self.w.runButton.enable(glyphWideOn or layerSpecificOn)

	def glyphFilterPatterns(self):
		"""Return list of glyph-name wildcard patterns from the filter field, or [] if blank."""
		raw = self.pref("glyphNameFilter").strip()
		if not raw:
			return []
		return [p.strip() for p in raw.split(",") if p.strip()]

	def keyMatchesFilter(self, key, patterns):
		"""
		Return True if key references a glyph matching any pattern, or if patterns is empty.
		Extracts the referenced glyph name by stripping leading = signs, | pipe, and arithmetic.
		"""
		if not patterns:
			return True
		if not key:
			return False
		k = key
		while k.startswith("="):
			k = k[1:]
		if k.startswith("|"):
			k = k[1:]
		for sep in ("+", "-", "*", "/", " ", "%", "("):
			idx = k.find(sep)
			if idx != -1:
				k = k[:idx]
		k = k.strip()
		if not k:
			return False
		return any(match(k, p) for p in patterns)

	def glyphsAndLayerScope(self, font):
		"""Return (glyphs, layerScope) where layerScope is a masterId string or 'all'."""
		scope = self.prefInt("scope")
		masterId = font.selectedFontMaster.id
		if scope == 0:  # selected glyphs, current master only
			glyphs = list(dict.fromkeys(layer.parent for layer in font.selectedLayers if layer.parent))
			return glyphs, masterId
		elif scope == 1:  # all masters of selected glyphs
			glyphs = list(dict.fromkeys(layer.parent for layer in font.selectedLayers if layer.parent))
			return glyphs, "all"
		elif scope == 2:  # complete current master
			return list(font.glyphs), masterId
		elif scope == 3:  # complete font
			return list(font.glyphs), "all"
		else:  # scope == 4: all open fonts (handled at caller level)
			return list(font.glyphs), "all"

	def layersForGlyph(self, glyph, layerScope):
		"""Return the layers to process for a glyph given the layer scope."""
		if layerScope == "all":
			return list(glyph.layers)
		return [l for l in glyph.layers if l.associatedMasterId == layerScope]

	def processFont(self, font, patterns, removeGlyphWide, removeLayerSpecific):
		"""Process a single font; return (totalKeysRemoved, affectedGlyphCount)."""
		glyphs, layerScope = self.glyphsAndLayerScope(font)
		removedKeys = 0
		affectedGlyphs = 0

		for glyph in glyphs:
			glyphKeys = 0

			if removeGlyphWide:
				for attr in ("leftMetricsKey", "rightMetricsKey", "widthMetricsKey"):
					currentKey = getattr(glyph, attr)
					if currentKey and self.keyMatchesFilter(currentKey, patterns):
						setattr(glyph, attr, None)
						glyphKeys += 1

			if removeLayerSpecific:
				for layer in self.layersForGlyph(glyph, layerScope):
					for attr in ("leftMetricsKey", "rightMetricsKey", "widthMetricsKey"):
						currentKey = getattr(layer, attr)
						if currentKey and self.keyMatchesFilter(currentKey, patterns):
							setattr(layer, attr, None)
							glyphKeys += 1

			if glyphKeys:
				print("\t✅ %s: removed %i metrics key%s" % (glyph.name, glyphKeys, "" if glyphKeys == 1 else "s"))
				removedKeys += glyphKeys
				affectedGlyphs += 1

		return removedKeys, affectedGlyphs

	def run(self, sender):
		self.SavePreferences()
		removeGlyphWide = self.prefBool("glyphWideKeys")
		removeLayerSpecific = self.prefBool("layerSpecificKeys")
		scope = self.prefInt("scope")
		patterns = self.glyphFilterPatterns()

		fonts = Glyphs.fonts if scope == 4 else ([Glyphs.font] if Glyphs.font else [])
		if not fonts:
			Message("No font open", "Please open a font first.", OKButton=None)
			return

		Glyphs.clearLog()
		print("Remove Metrics Keys\n")

		totalKeys = 0
		totalGlyphs = 0

		for font in fonts:
			print("Font: %s" % font.familyName)
			if font.filepath:
				print(font.filepath)
			else:
				print("⚠️ Font has not been saved yet.")
			print()

			font.disableUpdateInterface()
			try:
				removedKeys, affectedGlyphs = self.processFont(font, patterns, removeGlyphWide, removeLayerSpecific)
				totalKeys += removedKeys
				totalGlyphs += affectedGlyphs
			except Exception as e:
				Glyphs.showMacroWindow()
				print("\n⚠️ Script Error:\n")
				import traceback
				print(traceback.format_exc())
				raise e
			finally:
				font.enableUpdateInterface()

		msg = "Removed %i key%s in %i glyph%s." % (
			totalKeys,
			"" if totalKeys == 1 else "s",
			totalGlyphs,
			"" if totalGlyphs == 1 else "s",
		)
		print("\n🔠 %s Done." % msg)
		self.w.status.set(msg)
		Glyphs.showNotification("Remove Metrics Keys", msg)


Glyphs.clearLog()
RemoveMetricsKeys()
