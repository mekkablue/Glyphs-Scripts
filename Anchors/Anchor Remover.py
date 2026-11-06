# MenuTitle: Anchor Remover
__doc__ = """
Remove anchors from glyphs: by anchor name, from suffixed glyphs, or strip non-standard anchors. Consolidates 'Remove Anchors', 'Remove Anchors in Suffixed Glyphs', and 'Remove Non-Standard Anchors from Selected Glyphs'.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSTextAlignmentRight, NSWindowStyleMaskResizable
from Foundation import NSSize
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
		"allFonts": 0,
	}

	def __init__(self):
		windowWidth = 520
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Anchor Remover",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		inset = 15

		# --- Row 1: Remove anchor by name ---
		anchorTooltip = "Anchor name, wildcard pattern (e.g. top*, *viet), or 'All Anchors'. Click the refresh button to populate the dropdown from the current font."
		self.w.anchorText = vanilla.TextBox("auto", "Remove anchor:", selectable=True)
		self.w.anchorText.setToolTip(anchorTooltip)
		self.w.anchorName = vanilla.ComboBox("auto", [], callback=self.SavePreferences)
		self.w.anchorName.setToolTip(anchorTooltip)
		self.w.updateButton = UpdateButton("auto", callback=self.updateAnchorList)
		self.w.updateButton.setToolTip("Scan the frontmost font for all anchor names and update the popup list.")
		self.w.removeAnchorButton = vanilla.Button("auto", "Remove", callback=self.removeByName)
		self.w.removeAnchorButton.setToolTip("Remove the selected anchor from glyphs. Scope is determined by the ⚠️ checkboxes below.")

		# --- Row 2: Remove from suffixed glyphs ---
		suffixTooltip = "Comma-separated suffixes. All anchors are removed from every glyph whose name ends in one of these suffixes. Applies font-wide across all layers, ignoring the glyph and master scope settings."
		self.w.suffixText = vanilla.TextBox("auto", "By glyph suffix:", selectable=True)
		self.w.suffixText.setToolTip(suffixTooltip)
		self.w.suffixList = vanilla.EditText("auto", ".sups, .sinf, superior, inferior", callback=self.SavePreferences)
		self.w.suffixList.setToolTip(suffixTooltip)
		self.w.removeSuffixButton = vanilla.Button("auto", "Remove", callback=self.removeBySuffix)
		self.w.removeSuffixButton.setToolTip("Remove all anchors from every glyph whose name ends in one of the listed suffixes. Always operates font-wide on all layers.")

		# --- Row 3: Remove non-standard anchors ---
		exceptTooltip = "Comma-separated anchor names or wildcard patterns to keep even if non-standard (e.g. top_*, caret*). Wildcards: * matches any string, ? matches one character."
		self.w.nonStandardText = vanilla.TextBox("auto", "Non-standard, keep:", selectable=True)
		self.w.nonStandardText.setToolTip(exceptTooltip)
		self.w.exceptAnchors = vanilla.EditText("auto", "", callback=self.SavePreferences)
		self.w.exceptAnchors.setToolTip(exceptTooltip)
		self.w.removeNonStandardButton = vanilla.Button("auto", "Remove", callback=self.removeNonStandard)
		self.w.removeNonStandardButton.setToolTip("Remove anchors not listed as defaults for each glyph by GlyphsApp (e.g. ogonek from J). Respects the ⚠️ checkboxes below.")

		# Sub-checkboxes for non-standard section
		self.w.keepExtensions = vanilla.CheckBox("auto", "Keep underscore variants of standard anchors (e.g. top_low)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.keepExtensions.setToolTip("Keep anchors whose name starts with a standard anchor name followed by an underscore, e.g. keep top_low if top is standard for this glyph.")
		self.w.keepExitAndEntry = vanilla.CheckBox("auto", "Keep exit and entry anchors", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.keepExitAndEntry.setToolTip("Do not remove exit, entry, #exit and #entry anchors (used for cursive attachment features).")
		self.w.keepCarets = vanilla.CheckBox("auto", "Keep caret anchors (only in ligatures)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.keepCarets.setToolTip("Keep caret_* anchors in glyphs that are ligatures (subCategory = Ligature or underscore in name).")
		self.w.keepNoDefaults = vanilla.CheckBox("auto", "Skip glyphs with no default anchors defined", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.keepNoDefaults.setToolTip("If GlyphsApp has no default anchors defined for a glyph, leave all its anchors untouched.")

		# --- Row 4: Remove explicit traversing anchors in composites ---
		traversingTooltip = "In composite glyphs, remove explicit anchors that are already provided by traversal from a component. Lets the component's anchors propagate naturally."
		self.w.traversingText = vanilla.TextBox("auto", "Remove explicit traversing anchors in composites:", selectable=True)
		self.w.traversingText.setToolTip(traversingTooltip)
		self.w.removeTraversingButton = vanilla.Button("auto", "Remove", callback=self.removeExplicitTraversing)
		self.w.removeTraversingButton.setToolTip(traversingTooltip)

		self.w.separator = vanilla.HorizontalLine("auto")

		# Scope checkboxes (with warning)
		self.w.allGlyphs = vanilla.CheckBox("auto", "⚠️ Remove in ALL glyphs (otherwise selected glyphs only)", value=False, callback=self.SavePreferences)
		self.w.allGlyphs.setToolTip("When checked, 'Remove anchor' and 'Remove non-standard' operate on every glyph in the font. When unchecked (default), they operate on the current selection only.")
		self.w.allMasters = vanilla.CheckBox("auto", "⚠️ Remove on ALL masters (otherwise current master only)", value=True, callback=self.SavePreferences)
		self.w.allMasters.setToolTip("When checked (default), 'Remove anchor' operates on all master layers. When unchecked, only the layers of the currently selected master are affected.")
		self.w.allFonts = vanilla.CheckBox("auto", "⚠️ Remove in ALL open fonts (otherwise frontmost font only)", value=False, callback=self.SavePreferences)
		self.w.allFonts.setToolTip("When checked, all Remove buttons process every open font, each with the glyph and master scope set above. When unchecked (default), only the frontmost font is processed.")

		# checkboxes stretch vertically by default; hug so the window is as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels in front of fields: right-aligned, all as wide as the widest one
		labelNames = ("anchorText", "suffixText", "nonStandardText")
		widestLabel = "nonStandardText"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]
		# all Remove buttons share one width
		widthRules += [
			{"view1": getattr(self.w, buttonName), "attribute1": "width", "view2": self.w.removeAnchorButton, "attribute2": "width"}
			for buttonName in ("removeSuffixButton", "removeNonStandardButton", "removeTraversingButton")
		]
		# the checkboxes of the non-standard section line up with its field
		alignRules = [
			{"view1": getattr(self.w, checkName), "attribute1": "left", "view2": self.w.exceptAnchors, "attribute2": "left"}
			for checkName in ("keepExtensions", "keepExitAndEntry", "keepCarets", "keepNoDefaults")
		]
		# each row has one view in the vertical chain; the others follow its centerY
		centerRules = [
			{"view1": getattr(self.w, followerName), "attribute1": "centerY", "view2": getattr(self.w, leaderName), "attribute2": "centerY"}
			for followerName, leaderName in (
				("anchorText", "anchorName"),
				("updateButton", "anchorName"),
				("removeAnchorButton", "anchorName"),
				("suffixText", "suffixList"),
				("removeSuffixButton", "suffixList"),
				("nonStandardText", "exceptAnchors"),
				("removeNonStandardButton", "exceptAnchors"),
				("traversingText", "removeTraversingButton"),
			)
		]

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[anchorText]-gap-[anchorName(>=120)]-gap-[updateButton]-gap-[removeAnchorButton(>=70)]-inset-|",
				"H:|-inset-[suffixText]-gap-[suffixList]-gap-[removeSuffixButton]-inset-|",
				"H:|-inset-[nonStandardText]-gap-[exceptAnchors]-gap-[removeNonStandardButton]-inset-|",
				"H:[keepExtensions]-(>=inset)-|",
				"H:[keepExitAndEntry]-(>=inset)-|",
				"H:[keepCarets]-(>=inset)-|",
				"H:[keepNoDefaults]-(>=inset)-|",
				"H:|-inset-[traversingText]-(>=gap)-[removeTraversingButton]-inset-|",
				"H:|-inset-[separator]-inset-|",
				"H:|-inset-[allGlyphs]-(>=inset)-|",
				"H:|-inset-[allMasters]-(>=inset)-|",
				"H:|-inset-[allFonts]-(>=inset)-|",
				"V:|-gap-[anchorName]-section-[suffixList]-section-[exceptAnchors]-row-[keepExtensions]-checkRow-[keepExitAndEntry]-checkRow-[keepCarets]-checkRow-[keepNoDefaults]-section-[removeTraversingButton]-section-[separator(1)]-row-[allGlyphs]-checkRow-[allMasters]-checkRow-[allFonts]-inset-|",
			] + widthRules + alignRules + centerRules,
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5, "section": 12},
		)

		self.LoadPreferences()
		self.updateAnchorList(None)

		self.w.open()
		self.w.makeKey()

		# resizable horizontally only: lock the content height Auto Layout arrived at
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()
		contentHeight = nsWindow.contentView().frame().size.height
		nsWindow.setContentMinSize_(NSSize(windowWidth, contentHeight))
		nsWindow.setContentMaxSize_(NSSize(windowWidth + 1000, contentHeight))

	# -------------------------------------------------------------------------

	def targetFonts(self):
		"""Returns the fonts to process: all open fonts or the frontmost font."""
		if self.prefBool("allFonts"):
			return list(Glyphs.fonts)
		return [Glyphs.font]

	def getGlyphs(self, font):
		"""Returns glyphs of the font to process: all glyphs or current selection."""
		if self.prefBool("allGlyphs"):
			return list(font.glyphs)
		return [layer.parent for layer in font.selectedLayers if layer.parent]

	def layersForGlyph(self, font, glyph):
		"""Returns layers to process: all masters or current master only."""
		if self.prefBool("allMasters"):
			return list(glyph.layers)
		masterId = font.selectedFontMaster.id
		return [layer for layer in glyph.layers if layer.associatedMasterId == masterId]

	def printFontHeader(self, font):
		print("Font: %s" % font.familyName)
		if font.filepath:
			print(font.filepath)

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

	def runOnFonts(self, title, processFont, summary):
		"""Runs processFont(font) on all target fonts, which returns (anchorCount, glyphCount); logs and reports the totals."""
		Glyphs.clearLog()
		print("Anchor Remover — %s\n" % title)
		anchorCount = 0
		glyphCount = 0
		fonts = self.targetFonts()
		for font in fonts:
			self.printFontHeader(font)
			font.disableUpdateInterface()
			try:
				fontAnchors, fontGlyphs = processFont(font)
			finally:
				font.enableUpdateInterface()
			anchorCount += fontAnchors
			glyphCount += fontGlyphs
			print()

		msg = summary % (
			anchorCount,
			"" if anchorCount == 1 else "s",
			glyphCount,
			"" if glyphCount == 1 else "s",
		)
		if len(fonts) > 1:
			msg += " (%i fonts)" % len(fonts)
		print("🔠 %s Done." % msg)
		Glyphs.showNotification("Anchor Remover", msg)

	# -------------------------------------------------------------------------

	def removeByName(self, sender=None):
		"""Remove anchors matching the combo box entry (exact name, wildcard, or All Anchors)."""
		if not Glyphs.font:
			Message("No font open", "Please open a font first.", OKButton=None)
			return

		anchorName = self.pref("anchorName").strip()
		if not anchorName:
			Message("No anchor specified", "Enter an anchor name or wildcard pattern, or choose from the dropdown.", OKButton=None)
			return

		removeAll = anchorName == allAnchors
		hasWildcard = not removeAll and ("*" in anchorName or "?" in anchorName)
		what = "all anchors" if removeAll else "anchors matching '%s'" % anchorName if hasWildcard else "anchor '%s'" % anchorName

		def processFont(font):
			glyphs = self.getGlyphs(font)
			anchorCount = 0
			glyphCount = 0
			print("\nDeleting %s …\n" % what)
			for glyph in glyphs:
				deleted = 0
				for layer in self.layersForGlyph(font, glyph):
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
			return anchorCount, glyphCount

		self.runOnFonts("Remove by name", processFont, "Deleted %i anchor%s in %i glyph%s.")

	# -------------------------------------------------------------------------

	def removeBySuffix(self, sender=None):
		"""Remove all anchors from glyphs whose name ends in any of the listed suffixes."""
		if not Glyphs.font:
			Message("No font open", "Please open a font first.", OKButton=None)
			return

		raw = self.pref("suffixList")
		suffixes = [s.strip() for s in raw.split(",") if s.strip()]
		if not suffixes:
			Message("No suffixes", "Enter at least one suffix in the field.", OKButton=None)
			return

		def processFont(font):
			print("\nSuffixes: %s\n" % ", ".join(suffixes))
			anchorCount = 0
			glyphCount = 0
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
			return anchorCount, glyphCount

		self.runOnFonts("Remove from suffixed glyphs", processFont, "Removed %i anchor%s from %i glyph%s.")

	# -------------------------------------------------------------------------

	def removeNonStandard(self, sender=None):
		"""Remove anchors not listed as defaults for each glyph, with optional exceptions."""
		if not Glyphs.font:
			Message("No font open", "Please open a font first.", OKButton=None)
			return

		keepExtensions = self.prefBool("keepExtensions")
		keepExitAndEntry = self.prefBool("keepExitAndEntry")
		keepCarets = self.prefBool("keepCarets")
		keepNoDefaults = self.prefBool("keepNoDefaults")

		rawExcept = self.pref("exceptAnchors")
		exceptPatterns = [p.strip() for p in rawExcept.split(",") if p.strip()]

		def processFont(font):
			if exceptPatterns:
				print("Keeping: %s\n" % ", ".join(exceptPatterns))
			anchorCount = 0
			glyphCount = 0
			for glyph in self.getGlyphs(font):
				glyphInfo = glyph.glyphInfo
				defaultAnchors = []
				if glyphInfo and glyphInfo.anchors:
					for name in glyphInfo.anchors:
						if "@" in name:
							name = name[:name.find("@")]
						defaultAnchors.append(name)

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
						if any(match(anchorName, pattern) for pattern in exceptPatterns):
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
			return anchorCount, glyphCount

		self.runOnFonts("Remove non-standard anchors", processFont, "Removed %i non-standard anchor%s from %i glyph%s.")

	# -------------------------------------------------------------------------

	def removeExplicitTraversing(self, sender=None):
		"""In composite layers, remove explicit anchors already provided by traversal from a component."""
		if not Glyphs.font:
			Message("No font open", "Please open a font first.", OKButton=None)
			return

		def processFont(font):
			anchorCount = 0
			glyphCount = 0
			for glyph in self.getGlyphs(font):
				deleted = 0
				for layer in self.layersForGlyph(font, glyph):
					if not layer.components:
						continue
					# Collect anchor names provided by traversal from all components.
					# Non-underscore anchors on a component's referenced layer traverse upward.
					traversedNames = set()
					for component in layer.components:
						compLayer = component.layer
						if compLayer:
							for anchor in compLayer.anchors:
								if not anchor.name.startswith("_"):
									traversedNames.add(anchor.name)
					if not traversedNames:
						continue
					toDelete = [a.name for a in layer.anchors if a.name in traversedNames]
					for name in toDelete:
						print("\t✅ %s / %s: removed explicit '%s' (covered by component traversal)" % (glyph.name, layer.name, name))
						del layer.anchors[name]
						deleted += 1
				if deleted:
					anchorCount += deleted
					glyphCount += 1
			return anchorCount, glyphCount

		self.runOnFonts("Remove explicit traversing anchors in composites", processFont, "Removed %i explicit traversing anchor%s from %i glyph%s.")


AnchorRemover()
