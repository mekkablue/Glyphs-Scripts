# MenuTitle: Anchor Remover
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Remove anchors from glyphs: by anchor name, from suffixed glyphs, or strip non-standard anchors. Consolidates 'Remove Anchors', 'Remove Anchors in Suffixed Glyphs', and 'Remove Non-Standard Anchors from Selected Glyphs'.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject

allAnchors = "All Anchors"


class AnchorRemover(mekkaObject):
	prefDict = {
		"anchorPopup": 0,
		"suffixList": ".sups, .sinf, superior, inferior",
		"keepExtensions": 0,
		"keepExitAndEntry": 0,
		"keepCarets": 1,
		"keepNoDefaults": 0,
		"selectedGlyphsOnly": 0,
		"currentMasterOnly": 0,
	}

	def __init__(self):
		windowWidth = 370
		windowHeight = 280
		windowWidthResize = 150
		windowHeightResize = 0
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Anchor Remover",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),
			autosaveName=self.domain("mainwindow"),
		)

		linePos, inset, lineHeight = 12, 15, 22
		tab1 = 150  # controls start here; labels are right-aligned up to tab1-5

		# --- Row 1: Remove by anchor name ---
		self.w.anchorText = vanilla.TextBox(
			(inset, linePos + 2, tab1 - 5, 14), "Remove anchor:", sizeStyle="small", selectable=True, alignment="right"
		)
		self.w.anchorPopup = vanilla.PopUpButton(
			(inset + tab1, linePos, -(inset + 20 + 5 + 75 + 5), 17),
			[],
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.anchorPopup.setToolTip(
			"Choose an anchor to delete, or 'All Anchors'. Click ⟲ to refresh the list from the current font."
		)
		self.w.updateButton = vanilla.SquareButton(
			(-(inset + 75 + 5 + 20), linePos, -(inset + 75 + 5), 19),
			"⟲",
			sizeStyle="small",
			callback=self.updateAnchorList,
		)
		self.w.updateButton.setToolTip("Scan the font for all anchor names and update the popup list.")
		self.w.removeAnchorButton = vanilla.Button(
			(-(inset + 75), linePos, -inset, 20), "Remove", callback=self.removeByName, sizeStyle="small"
		)
		self.w.removeAnchorButton.setToolTip(
			"Remove the selected anchor from glyphs. Scope is determined by the checkboxes below."
		)
		linePos += lineHeight + 8

		# --- Row 2: Remove from suffixed glyphs ---
		self.w.suffixText = vanilla.TextBox(
			(inset, linePos + 2, tab1 - 5, 14),
			"Remove from suffix:",
			sizeStyle="small",
			selectable=True,
			alignment="right",
		)
		self.w.suffixList = vanilla.EditText(
			(inset + tab1, linePos, -(inset + 75 + 5), 19),
			".sups, .sinf, superior, inferior",
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.suffixList.setToolTip(
			"Comma-separated suffixes. All anchors are removed from every glyph whose name ends in one of these suffixes. Applies font-wide across all layers."
		)
		self.w.removeSuffixButton = vanilla.Button(
			(-(inset + 75), linePos, -inset, 20), "Remove", callback=self.removeBySuffix, sizeStyle="small"
		)
		self.w.removeSuffixButton.setToolTip("Remove all anchors from every glyph that ends in one of the listed suffixes.")
		linePos += lineHeight + 8

		# --- Row 3: Non-standard anchors ---
		self.w.nonStandardText = vanilla.TextBox(
			(inset, linePos + 2, tab1 - 5, 14),
			"Non-standard anchors:",
			sizeStyle="small",
			selectable=True,
			alignment="right",
		)
		self.w.removeNonStandardButton = vanilla.Button(
			(-(inset + 75), linePos, -inset, 20), "Remove", callback=self.removeNonStandard, sizeStyle="small"
		)
		self.w.removeNonStandardButton.setToolTip(
			"Remove anchors not listed as defaults for each glyph by GlyphsApp (e.g. ogonek from J). Respects 'Selected glyphs only'."
		)
		linePos += lineHeight

		indent = inset + tab1
		self.w.keepExtensions = vanilla.CheckBox(
			(indent, linePos, -inset, 20),
			"Keep underscore variants of standard anchors (e.g. top_low)",
			value=False,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.keepExtensions.setToolTip(
			"Keep anchors like top_low if top is a standard anchor for this glyph."
		)
		linePos += lineHeight

		self.w.keepExitAndEntry = vanilla.CheckBox(
			(indent, linePos, -inset, 20),
			"Keep exit and entry anchors",
			value=False,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.keepExitAndEntry.setToolTip("Do not remove exit and entry anchors (used for cursive attachment).")
		linePos += lineHeight

		self.w.keepCarets = vanilla.CheckBox(
			(indent, linePos, -inset, 20),
			"Keep caret anchors (only in ligatures)",
			value=True,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.keepCarets.setToolTip("Keep caret_* anchors in ligature glyphs.")
		linePos += lineHeight

		self.w.keepNoDefaults = vanilla.CheckBox(
			(indent, linePos, -inset, 20),
			"Skip glyphs with no default anchors defined",
			value=False,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.keepNoDefaults.setToolTip(
			"If a glyph has no anchors listed as defaults in Glyphs, leave it untouched entirely."
		)
		linePos += lineHeight + 8

		# Separator
		self.w.separator = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 10

		# Scope options (shared by rows 1 and 3)
		self.w.selectedGlyphsOnly = vanilla.CheckBox(
			(inset, linePos, -inset, 20),
			"Selected glyphs only (otherwise all glyphs in font)",
			value=False,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.selectedGlyphsOnly.setToolTip(
			"Apply 'Remove anchor' and 'Remove non-standard' to the current glyph selection only. The suffix operation always runs font-wide."
		)
		linePos += lineHeight

		self.w.currentMasterOnly = vanilla.CheckBox(
			(inset, linePos, -inset, 20),
			"Current master only (otherwise all masters)",
			value=False,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.currentMasterOnly.setToolTip(
			"Apply 'Remove anchor' only to layers of the currently selected master."
		)
		linePos += lineHeight + 5

		# Status line
		self.w.status = vanilla.TextBox((inset, linePos, -inset, 14), "", sizeStyle="small")

		self.LoadPreferences()
		self.updateAnchorList(None)

		self.w.open()
		self.w.makeKey()

	# -------------------------------------------------------------------------

	def getGlyphs(self):
		"""Returns the glyphs to process based on the 'selectedGlyphsOnly' pref."""
		font = Glyphs.font
		if not font:
			return []
		if self.prefBool("selectedGlyphsOnly"):
			return [layer.parent for layer in font.selectedLayers if layer.parent]
		return list(font.glyphs)

	def layersForGlyph(self, glyph):
		"""Returns the layers of glyph to process based on the 'currentMasterOnly' pref."""
		if self.prefBool("currentMasterOnly"):
			masterId = Glyphs.font.selectedFontMaster.id
			return [l for l in glyph.layers if l.associatedMasterId == masterId]
		return list(glyph.layers)

	# -------------------------------------------------------------------------

	def updateAnchorList(self, sender):
		"""Scan the font for anchor names and populate the popup."""
		font = Glyphs.font
		if not font:
			return
		names = set()
		glyphs = self.getGlyphs() if self.prefBool("selectedGlyphsOnly") else list(font.glyphs)
		for glyph in glyphs:
			for layer in glyph.layers:
				for anchor in layer.anchors:
					names.add(anchor.name)
		items = sorted(names) + [allAnchors]
		self.w.anchorPopup.setItems(items)
		# Clamp saved index
		saved = self.prefInt("anchorPopup")
		if saved >= len(items):
			self.setPref("anchorPopup", 0)
			self.w.anchorPopup.set(0)
		else:
			self.w.anchorPopup.set(saved)

	# -------------------------------------------------------------------------

	def removeByName(self, sender=None):
		"""Remove the selected anchor (or all anchors) from glyphs."""
		font = Glyphs.font
		if not font:
			Message("No font open", "Please open a font first.", OKButton=None)
			return

		items = self.w.anchorPopup.getItems()
		if not items:
			Message("No anchors found", "No anchors found in the font. Click ⟲ to refresh.", OKButton=None)
			return

		anchorName = items[self.prefInt("anchorPopup")]
		removeAll = anchorName == allAnchors
		glyphs = self.getGlyphs()
		if not glyphs:
			self.w.status.set("No glyphs to process.")
			return

		Glyphs.clearLog()
		print("Anchor Remover — Remove by name\n")
		print("Font: %s" % font.familyName)
		if font.filepath:
			print(font.filepath)
		print("\nDeleting %s …\n" % ("all anchors" if removeAll else "anchor '%s'" % anchorName))

		anchorCount = 0
		glyphCount = 0
		font.disableUpdateInterface()
		try:
			for glyph in glyphs:
				deleted = 0
				for layer in self.layersForGlyph(glyph):
					if removeAll:
						deleted += len(layer.anchors)
						layer.anchors = None
					elif layer.anchors[anchorName]:
						del layer.anchors[anchorName]
						deleted += 1
				if deleted:
					print("\t✅ %s: deleted %i anchor%s" % (glyph.name, deleted, "" if deleted == 1 else "s"))
					anchorCount += deleted
					glyphCount += 1
		finally:
			font.enableUpdateInterface()

		msg = "Deleted %i anchor%s in %i glyph%s." % (
			anchorCount,
			"" if anchorCount == 1 else "s",
			glyphCount,
			"" if glyphCount == 1 else "s",
		)
		print("\n🔠 %s Done." % msg)
		self.w.status.set(msg)
		Glyphs.showNotification("Anchor Remover", msg)

	# -------------------------------------------------------------------------

	def removeBySuffix(self, sender=None):
		"""Remove all anchors from glyphs whose name ends in any of the listed suffixes."""
		font = Glyphs.font
		if not font:
			Message("No font open", "Please open a font first.", OKButton=None)
			return

		raw = self.pref("suffixList")
		suffixes = [s.strip() for s in raw.split(",") if s.strip()]
		if not suffixes:
			Message("No suffixes", "Enter at least one suffix in the field.", OKButton=None)
			return

		Glyphs.clearLog()
		print("Anchor Remover — Remove from suffixed glyphs\n")
		print("Font: %s" % font.familyName)
		if font.filepath:
			print(font.filepath)
		print("\nSuffixes: %s\n" % ", ".join(suffixes))

		anchorCount = 0
		glyphCount = 0
		font.disableUpdateInterface()
		try:
			for glyph in font.glyphs:
				matched = any(glyph.name.endswith(s) or ("%s." % s) in glyph.name for s in suffixes)
				if not matched:
					continue
				deleted = 0
				for layer in glyph.layers:
					deleted += len(layer.anchors)
					layer.anchors = []
				if deleted:
					print("\t✅ %s: removed %i anchor%s" % (glyph.name, deleted, "" if deleted == 1 else "s"))
					anchorCount += deleted
					glyphCount += 1
		finally:
			font.enableUpdateInterface()

		msg = "Removed %i anchor%s from %i glyph%s." % (
			anchorCount,
			"" if anchorCount == 1 else "s",
			glyphCount,
			"" if glyphCount == 1 else "s",
		)
		print("\n🔠 %s Done." % msg)
		self.w.status.set(msg)
		Glyphs.showNotification("Anchor Remover", msg)

	# -------------------------------------------------------------------------

	def removeNonStandard(self, sender=None):
		"""Remove anchors that are not listed as defaults for each glyph."""
		font = Glyphs.font
		if not font:
			Message("No font open", "Please open a font first.", OKButton=None)
			return

		keepExtensions = self.prefBool("keepExtensions")
		keepExitAndEntry = self.prefBool("keepExitAndEntry")
		keepCarets = self.prefBool("keepCarets")
		keepNoDefaults = self.prefBool("keepNoDefaults")

		glyphs = self.getGlyphs()
		if not glyphs:
			self.w.status.set("No glyphs to process.")
			return

		Glyphs.clearLog()
		print("Anchor Remover — Remove non-standard anchors\n")
		print("Font: %s" % font.familyName)
		if font.filepath:
			print(font.filepath)
		print()

		anchorCount = 0
		glyphCount = 0
		font.disableUpdateInterface()
		try:
			for glyph in glyphs:
				glyphInfo = glyph.glyphInfo
				if glyphInfo and glyphInfo.anchors:
					defaultAnchors = []
					for a in glyphInfo.anchors:
						name = a if isinstance(a, str) else a
						if "@" in name:
							name = name[:name.find("@")]
						defaultAnchors.append(name)
				else:
					defaultAnchors = []

				if not defaultAnchors and keepNoDefaults:
					continue

				deleted = 0
				for layer in glyph.layers:
					currentNames = [a.name for a in layer.anchors]
					for anchorName in currentNames:
						if anchorName in defaultAnchors:
							continue
						keep = False
						if keepExtensions and "_" in anchorName:
							base = anchorName[:anchorName.find("_")]
							if base in defaultAnchors:
								keep = True
						if keepExitAndEntry:
							bare = anchorName.lstrip("#")
							if bare in ("exit", "entry"):
								keep = True
						if keepCarets and anchorName.startswith("caret"):
							isLigature = glyph.subCategory == "Ligature" or "_" in glyph.name[1:]
							if isLigature:
								keep = True
						if not keep:
							print("\t❌ %s / %s: deleting '%s'" % (glyph.name, layer.name, anchorName))
							del layer.anchors[anchorName]
							deleted += 1

				if deleted:
					anchorCount += deleted
					glyphCount += 1
		finally:
			font.enableUpdateInterface()

		msg = "Removed %i non-standard anchor%s from %i glyph%s." % (
			anchorCount,
			"" if anchorCount == 1 else "s",
			glyphCount,
			"" if glyphCount == 1 else "s",
		)
		print("\n🔠 %s Done." % msg)
		self.w.status.set(msg)
		Glyphs.showNotification("Anchor Remover", msg)


AnchorRemover()
