# MenuTitle: Anchor Remover
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Remove anchors from glyphs: by anchor name, from suffixed glyphs, or strip non-standard anchors. Consolidates 'Remove Anchors', 'Remove Anchors in Suffixed Glyphs', and 'Remove Non-Standard Anchors from Selected Glyphs'.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton, match

allAnchors = "All Anchors"


class AnchorRemover(mekkaObject):
	prefDict = {
		"anchorName": "",
		"suffixList": ".sups, .sinf, superior, inferior",
		"exceptAnchors": "*alt*, cap*, connect",
		"keepExtensions": 0,
		"keepExitAndEntry": 0,
		"keepCarets": 1,
		"keepNoDefaults": 0,
		"allGlyphs": 0,
		"allMasters": 1,
	}

	def __init__(self):
		windowWidth = 450
		windowHeight = 300
		windowWidthResize = 1000
		windowHeightResize = 0
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Anchor Remover",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),
			autosaveName=self.domain("mainwindow"),
		)

		linePos, inset, lineHeight, lineHeightS = 12, 15, 26, 22
		tab1 = 150  # controls start here; labels are right-aligned from inset up to tab1-5

		# --- Row 1: Remove anchor by name ---
		self.w.anchorText = vanilla.TextBox(
			(inset, linePos + 3, tab1 - 5, 17), "Remove anchor:", selectable=True, alignment="right"
		)
		self.w.anchorName = vanilla.ComboBox(
			(inset + tab1, linePos + 2, -(inset + 20 + 5 + 80 + 5), 22),
			[],
			callback=self.SavePreferences,
		)
		self.w.anchorName.setToolTip(
			"Anchor name, wildcard pattern (e.g. top*, *viet), or 'All Anchors'. Click the refresh button to populate the dropdown from the current font."
		)
		self.w.updateButton = UpdateButton(
			(-(inset + 80 + 5 + 20), linePos, 20, 20),
			callback=self.updateAnchorList,
		)
		self.w.updateButton.setToolTip(
			"Scan the frontmost font for all anchor names and update the popup list."
		)
		self.w.removeAnchorButton = vanilla.Button(
			(-(inset + 80), linePos, -inset, 21), "Remove", callback=self.removeByName
		)
		self.w.removeAnchorButton.setToolTip(
			"Remove the selected anchor from glyphs. Scope is determined by the ⚠️ checkboxes below."
		)
		linePos += lineHeight + 8

		# --- Row 2: Remove from suffixed glyphs ---
		self.w.suffixText = vanilla.TextBox(
			(inset, linePos + 3, tab1 - 5, 17), "By glyph suffix:", selectable=True, alignment="right"
		)
		self.w.suffixList = vanilla.EditText(
			(inset + tab1, linePos, -(inset + 80 + 5), 22),
			".sups, .sinf, superior, inferior",
			callback=self.SavePreferences,
		)
		self.w.suffixList.setToolTip(
			"Comma-separated suffixes. All anchors are removed from every glyph whose name ends in one of these suffixes. Applies font-wide across all layers, ignoring scope settings."
		)
		self.w.removeSuffixButton = vanilla.Button(
			(-(inset + 80), linePos, -inset, 21), "Remove", callback=self.removeBySuffix
		)
		self.w.removeSuffixButton.setToolTip(
			"Remove all anchors from every glyph whose name ends in one of the listed suffixes. Always operates font-wide on all layers."
		)
		linePos += lineHeight + 8

		# --- Row 3: Remove non-standard anchors ---
		self.w.nonStandardText = vanilla.TextBox(
			(inset, linePos + 3, tab1 - 5, 17), "Non-standard, keep:", selectable=True, alignment="right"
		)
		self.w.exceptAnchors = vanilla.EditText(
			(inset + tab1, linePos, -(inset + 80 + 5), 22),
			"",
			callback=self.SavePreferences,
		)
		self.w.exceptAnchors.setToolTip(
			"Comma-separated anchor names or wildcard patterns to keep even if non-standard (e.g. top_*, caret*). Wildcards: * matches any string, ? matches one character."
		)
		self.w.removeNonStandardButton = vanilla.Button(
			(-(inset + 80), linePos, -inset, 21), "Remove", callback=self.removeNonStandard
		)
		self.w.removeNonStandardButton.setToolTip(
			"Remove anchors not listed as defaults for each glyph by GlyphsApp (e.g. ogonek from J). Respects the ⚠️ checkboxes below."
		)
		linePos += lineHeight

		# Sub-checkboxes for non-standard section (small, indented)
		indent = inset + tab1
		self.w.keepExtensions = vanilla.CheckBox(
			(indent, linePos, -inset, 18),
			"Keep underscore variants of standard anchors (e.g. top_low)",
			value=False,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.keepExtensions.setToolTip(
			"Keep anchors whose name starts with a standard anchor name followed by an underscore, e.g. keep top_low if top is standard for this glyph."
		)
		linePos += lineHeightS

		self.w.keepExitAndEntry = vanilla.CheckBox(
			(indent, linePos, -inset, 18),
			"Keep exit and entry anchors",
			value=False,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.keepExitAndEntry.setToolTip(
			"Do not remove exit, entry, #exit and #entry anchors (used for cursive attachment features)."
		)
		linePos += lineHeightS

		self.w.keepCarets = vanilla.CheckBox(
			(indent, linePos, -inset, 18),
			"Keep caret anchors (only in ligatures)",
			value=True,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.keepCarets.setToolTip(
			"Keep caret_* anchors in glyphs that are ligatures (subCategory = Ligature or underscore in name)."
		)
		linePos += lineHeightS

		self.w.keepNoDefaults = vanilla.CheckBox(
			(indent, linePos, -inset, 18),
			"Skip glyphs with no default anchors defined",
			value=False,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.keepNoDefaults.setToolTip(
			"If GlyphsApp has no default anchors defined for a glyph, leave all its anchors untouched."
		)
		linePos += lineHeightS + 8

		# Separator
		self.w.separator = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 10

		# Scope checkboxes (regular size, with warning)
		self.w.allGlyphs = vanilla.CheckBox(
			(inset, linePos, -inset, 22),
			"⚠️ Remove in ALL glyphs (otherwise selected glyphs only)",
			value=False,
			callback=self.SavePreferences,
		)
		self.w.allGlyphs.setToolTip(
			"When checked, 'Remove anchor' and 'Remove non-standard' operate on every glyph in the font. When unchecked (default), they operate on the current selection only."
		)
		linePos += lineHeight

		self.w.allMasters = vanilla.CheckBox(
			(inset, linePos, -inset, 22),
			"⚠️ Remove on ALL masters (otherwise current master only)",
			value=True,
			callback=self.SavePreferences,
		)
		self.w.allMasters.setToolTip(
			"When checked (default), 'Remove anchor' operates on all master layers. When unchecked, only the layers of the currently selected master are affected."
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
		"""Returns glyphs to process: all glyphs or current selection."""
		font = Glyphs.font
		if not font:
			return []
		if self.prefBool("allGlyphs"):
			return list(font.glyphs)
		return [layer.parent for layer in font.selectedLayers if layer.parent]

	def layersForGlyph(self, glyph):
		"""Returns layers to process: all masters or current master only."""
		if self.prefBool("allMasters"):
			return list(glyph.layers)
		masterId = Glyphs.font.selectedFontMaster.id
		return [l for l in glyph.layers if l.associatedMasterId == masterId]

	# -------------------------------------------------------------------------

	def updateAnchorList(self, sender):
		"""Scan the font for anchor names and populate the combo box dropdown."""
		font = Glyphs.font
		if not font:
			return
		names = set()
		glyphs = list(font.glyphs) if self.prefBool("allGlyphs") else [l.parent for l in font.selectedLayers if l.parent]
		for glyph in glyphs:
			for layer in glyph.layers:
				for anchor in layer.anchors:
					names.add(anchor.name)
		self.w.anchorName.setItems(sorted(names) + [allAnchors])

	# -------------------------------------------------------------------------

	def removeByName(self, sender=None):
		"""Remove anchors matching the combo box entry (exact name, wildcard, or All Anchors)."""
		font = Glyphs.font
		if not font:
			Message("No font open", "Please open a font first.", OKButton=None)
			return

		anchorName = self.pref("anchorName").strip()
		if not anchorName:
			Message("No anchor specified", "Enter an anchor name or wildcard pattern, or choose from the dropdown.", OKButton=None)
			return

		removeAll = anchorName == allAnchors
		hasWildcard = not removeAll and ("*" in anchorName or "?" in anchorName)
		glyphs = self.getGlyphs()
		if not glyphs:
			self.w.status.set("No glyphs to process.")
			return

		Glyphs.clearLog()
		print("Anchor Remover — Remove by name\n")
		print("Font: %s" % font.familyName)
		if font.filepath:
			print(font.filepath)
		print("\nDeleting %s …\n" % ("all anchors" if removeAll else "anchors matching '%s'" % anchorName if hasWildcard else "anchor '%s'" % anchorName))

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
					elif hasWildcard:
						toDelete = [a.name for a in layer.anchors if match(a.name, anchorName)]
						for name in toDelete:
							del layer.anchors[name]
						deleted += len(toDelete)
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
				if not any(glyph.name.endswith(s) or ("%s." % s) in glyph.name for s in suffixes):
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
		"""Remove anchors not listed as defaults for each glyph, with optional exceptions."""
		font = Glyphs.font
		if not font:
			Message("No font open", "Please open a font first.", OKButton=None)
			return

		keepExtensions = self.prefBool("keepExtensions")
		keepExitAndEntry = self.prefBool("keepExitAndEntry")
		keepCarets = self.prefBool("keepCarets")
		keepNoDefaults = self.prefBool("keepNoDefaults")

		rawExcept = self.pref("exceptAnchors")
		exceptPatterns = [p.strip() for p in rawExcept.split(",") if p.strip()]

		glyphs = self.getGlyphs()
		if not glyphs:
			self.w.status.set("No glyphs to process.")
			return

		Glyphs.clearLog()
		print("Anchor Remover — Remove non-standard anchors\n")
		print("Font: %s" % font.familyName)
		if font.filepath:
			print(font.filepath)
		if exceptPatterns:
			print("Keeping: %s\n" % ", ".join(exceptPatterns))
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
						# User-specified except patterns (wildcards)
						if any(match(anchorName, p) for p in exceptPatterns):
							keep = True
						# Underscore variants (e.g. top_low when top is standard)
						if keepExtensions and "_" in anchorName:
							base = anchorName[:anchorName.find("_")]
							if base in defaultAnchors:
								keep = True
						# Exit / entry anchors (with or without leading #)
						if keepExitAndEntry:
							if anchorName.lstrip("#") in ("exit", "entry"):
								keep = True
						# Caret anchors in ligatures
						if keepCarets and anchorName.startswith("caret"):
							if glyph.subCategory == "Ligature" or "_" in glyph.name[1:]:
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
