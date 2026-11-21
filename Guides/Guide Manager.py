# MenuTitle: Guide Manager
__doc__ = """
Selects or removes local (blue) and global (red) guides, with a scope for each. Optionally removes only the conditional global guides that match no glyph at all, because their rules are too strict.
"""

import vanilla
from mekkablue import mekkaObject, guidesOf, setGuides, fontFileName
from GlyphsApp import Glyphs, Message
from Foundation import NSSize
from AppKit import (
	NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut, NSWindowStyleMaskResizable,
)

localScopes = ("Selected glyphs", "All glyphs in current master", "All glyphs in all masters")
globalScopes = ("Current master", "All masters")


def plural(count, noun):
	return f"{count:,} {noun}{'' if count == 1 else 's'}"


class GuideManager(mekkaObject):
	prefDict = {
		"localGuides": True,
		"localScope": 0,
		"globalGuides": True,
		"globalScope": 0,
		"onlyConditional": False,
	}

	def __init__(self):
		windowWidth = 400
		windowWidthResize = 400  # user can resize the width by this much
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Guide Manager",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		inset = 15
		self.undoEntries = []  # (font, container, previous guides, description) of the most recent removal
		self.matchCache = {}  # (font, filter) -> does the filter match any glyph

		self.w.localGuides = vanilla.CheckBox("auto", "Local guides", callback=self.SavePreferences, sizeStyle="small")
		self.w.localGuides.setToolTip("The local (blue) guides in the glyphs of the chosen scope.")
		self.w.localScope = vanilla.PopUpButton("auto", localScopes, callback=self.SavePreferences, sizeStyle="small")
		self.w.localScope.setToolTip("Which glyphs to look at for local guides. Select always works on the selected glyphs only, because selecting needs the layer in the Edit view.")

		self.w.globalGuides = vanilla.CheckBox("auto", "Global guides", callback=self.SavePreferences, sizeStyle="small")
		self.w.globalGuides.setToolTip("The global (red) guides of the font masters.")
		self.w.globalScope = vanilla.PopUpButton("auto", globalScopes, callback=self.SavePreferences, sizeStyle="small")
		self.w.globalScope.setToolTip("Which masters to look at for global guides. Select always works on the master of each selected glyph.")

		self.w.onlyConditional = vanilla.CheckBox("auto", "Only conditional guides that match no glyph", callback=self.SavePreferences, sizeStyle="small")
		self.w.onlyConditional.setToolTip(
			"Only global guides with a filter (a condition for the glyphs they appear in) that matches no glyph in the font. "
			"Such guides never show anywhere, because their rules are too strict. Guides without a filter are never touched. Needs ‘Global guides’."
		)

		self.w.statusText = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small", selectable=True)
		self.w.statusText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.undoButton = vanilla.Button("auto", "Undo", callback=self.undoRemoval)
		self.w.undoButton.setToolTip("Puts back the guides removed by the most recent click on Remove.")
		self.w.undoButton.enable(False)
		self.w.selectButton = vanilla.Button("auto", "Select", callback=self.selectGuides)
		self.w.selectButton.setToolTip("Selects the guides in the selected glyphs, in the Edit view. Useful for batch-transforming them.")
		self.w.removeButton = vanilla.Button("auto", "Remove", callback=self.removeGuides)
		self.w.removeButton.setToolTip("Deletes the guides in the chosen scope. Undo takes the most recent removal back.")
		self.w.setDefaultButton(self.w.selectButton)

		# checkboxes with a popup hug their text, the popups take the extra width
		for checkBox in (self.w.localGuides, self.w.globalGuides):
			checkBox.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		for popup in (self.w.localScope, self.w.globalScope):
			popup.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# checkboxes stretch vertically by default; with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[localGuides]-gap-[localScope(>=100)]-inset-|",
				"H:|-inset-[globalGuides]-gap-[globalScope(>=100)]-inset-|",
				"H:|-indent-[onlyConditional]-(>=inset)-|",
				"H:|-inset-[statusText]-inset-|",
				"H:|-inset-[undoButton(>=70)]-(>=gap)-[selectButton(>=70)]-gap-[removeButton(>=70)]-inset-|",
				"V:|-inset-[localScope]-row-[globalScope]-row-[onlyConditional]-inset-[statusText]-row-[removeButton]-inset-|",
				"V:[undoButton]-inset-|",
				"V:[selectButton]-inset-|",
				{"view1": self.w.localGuides, "attribute1": "centerY", "view2": self.w.localScope, "attribute2": "centerY"},
				{"view1": self.w.globalGuides, "attribute1": "centerY", "view2": self.w.globalScope, "attribute2": "centerY"},
				{"view1": self.w.globalGuides, "attribute1": "width", "view2": self.w.localGuides, "attribute2": "width"},
			],
			metrics={"inset": inset, "indent": inset + 20, "gap": 8, "row": 8},
		)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

		# Resizable in width only. Vanilla's minSize/maxSize would count the title bar twice,
		# so set the limits on the NSWindow, in content sizes, with the size Auto Layout asks for:
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		fittingSize = nsWindow.contentView().fittingSize()
		nsWindow.setContentMinSize_(NSSize(min(fittingSize.width, windowWidth), fittingSize.height))
		nsWindow.setContentMaxSize_(NSSize(windowWidth + windowWidthResize, fittingSize.height))

	def setStatus(self, text):
		"""Sets the status line and redraws it right away, so it shows while the script is busy."""
		self.w.statusText.set(text)
		self.w.statusText.getNSTextField().display()

	# --- what is affected ---

	def localLayers(self, font):
		"""The layers whose local guides are in the scope."""
		scope = self.prefInt("localScope")
		if scope == 0:
			return [layer for layer in font.selectedLayers if layer.parent is not None]
		masterIDs = (font.selectedFontMaster.id, ) if scope == 1 else [master.id for master in font.masters]
		layers = []
		for glyph in font.glyphs:
			for masterID in masterIDs:
				layer = glyph.layers[masterID]
				if layer is not None:
					layers.append(layer)
		return layers

	def globalMasters(self, font):
		return (font.selectedFontMaster, ) if self.prefInt("globalScope") == 0 else tuple(font.masters)

	def matchesNoGlyph(self, font, guide):
		"""True if the guide has a filter and no glyph of the font passes it. The result is cached until the next run."""
		guideFilter = guide.filter
		if guideFilter is None:
			return False
		key = (font, guideFilter.predicateFormat())
		if key not in self.matchCache:
			self.matchCache[key] = not any(guideFilter.evaluateWithObject_(glyph) for glyph in font.glyphs)
		return self.matchCache[key]

	def affectedGlobalGuides(self, font, master):
		"""Returns all global guides of the master and a flag for each: is it affected by the settings?"""
		guides = list(guidesOf(master))
		if self.prefBool("onlyConditional"):
			flags = [self.matchesNoGlyph(font, guide) for guide in guides]
		else:
			flags = [True] * len(guides)
		return guides, flags

	def updateUI(self, sender=None):
		if self.w is None:
			return
		localOn = self.prefBool("localGuides")
		globalOn = self.prefBool("globalGuides")
		self.w.localScope.enable(localOn)
		self.w.globalScope.enable(globalOn)
		self.w.onlyConditional.enable(globalOn)
		font = Glyphs.font
		buttonsOn = bool(font) and (localOn or globalOn)
		self.w.selectButton.enable(buttonsOn)
		self.w.removeButton.enable(buttonsOn)
		if font is None:
			self.setStatus("❌ No font open.")
		elif not (localOn or globalOn):
			self.setStatus("🤖 Ready.")
		else:
			self.setStatus(self.predictionText(font, localOn, globalOn))

	def predictionText(self, font, localOn, globalOn):
		parts = []
		if localOn:
			guideCount = glyphCount = 0
			for layer in self.localLayers(font):
				count = len(guidesOf(layer))
				if count:
					guideCount += count
					glyphCount += 1
			parts.append(f"{plural(guideCount, 'local guide')} in {plural(glyphCount, 'glyph')}")
		if globalOn:
			guideCount = sum(sum(flags) for guides, flags in (self.affectedGlobalGuides(font, master) for master in self.globalMasters(font)))
			parts.append(plural(guideCount, "global guide"))
		return f"🔮 Will affect {' and '.join(parts)}."

	# --- actions ---

	def selectGuides(self, sender=None):
		try:
			Glyphs.clearLog()
			self.SavePreferences()
			font = Glyphs.font
			if font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			self.matchCache = {}
			print("Guide Manager: Select\n")
			print(f"📄 {fontFileName(font, fullPath=True)}")
			guideCount = glyphCount = 0
			for layer in font.selectedLayers:
				glyph = layer.parent
				if glyph is None:
					continue
				layer.clearSelection()
				guides = []
				if self.prefBool("localGuides"):
					guides.extend(guidesOf(layer))
				if self.prefBool("globalGuides"):
					masterGuides, flags = self.affectedGlobalGuides(font, layer.master)
					guides.extend(guide for guide, flag in zip(masterGuides, flags) if flag)
				for guide in guides:
					layer.selection.append(guide)
				print(f"\t☑️ {glyph.name}: {plural(len(guides), 'guide')}")
				if guides:
					guideCount += len(guides)
					glyphCount += 1
			self.setStatus(f"✅ Selected {plural(guideCount, 'guide')} in {plural(glyphCount, 'glyph')}. Details in Macro Window.")
			print("\n✅ Done")
		except Exception as e:
			self.reportError("Select", e)

	def removeGuides(self, sender=None):
		try:
			Glyphs.clearLog()
			self.SavePreferences()
			font = Glyphs.font
			if font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			self.matchCache = {}
			print("Guide Manager: Remove\n")
			print(f"📄 {fontFileName(font, fullPath=True)}")
			undoEntries = []
			guideCount = 0

			if self.prefBool("localGuides"):
				for layer in self.localLayers(font):
					guides = list(guidesOf(layer))
					if not guides:
						continue
					description = f"{layer.parent.name} ({layer.master.name})"
					undoEntries.append((font, layer, guides, description))
					setGuides(layer, [])
					guideCount += len(guides)
					print(f"\t🚫 {description}: {plural(len(guides), 'local guide')}")

			if self.prefBool("globalGuides"):
				for master in self.globalMasters(font):
					guides, flags = self.affectedGlobalGuides(font, master)
					removedCount = sum(flags)
					if not removedCount:
						continue
					undoEntries.append((font, master, guides, f"Master {master.name}"))
					setGuides(master, [guide for guide, flag in zip(guides, flags) if not flag])
					guideCount += removedCount
					print(f"\t🚫 Master {master.name}: {plural(removedCount, 'global guide')}")

			if undoEntries:
				self.undoEntries = undoEntries
			self.w.undoButton.enable(bool(self.undoEntries))
			self.setStatus(f"✅ Removed {plural(guideCount, 'guide')}. Details in Macro Window.")
			Glyphs.showNotification("Guide Manager", f"Removed {plural(guideCount, 'guide')}. Details in Macro Window.")
			print("\n✅ Done")
		except Exception as e:
			self.reportError("Remove", e)

	def undoRemoval(self, sender=None):
		try:
			Glyphs.clearLog()
			print("Guide Manager: Undo\n")
			guideCount = 0
			# reverse order of removal
			for font, container, guides, description in reversed(self.undoEntries):
				if font not in Glyphs.fonts:
					print(f"\t⚠️ Skipped {description}: font was closed")
					continue
				setGuides(container, guides)
				guideCount += len(guides)
				print(f"\t↩️ {description}: {plural(len(guides), 'guide')}")
			self.undoEntries = []
			self.w.undoButton.enable(False)
			self.setStatus(f"✅ Restored {plural(guideCount, 'guide')}. Details in Macro Window.")
			print("\n✅ Done")
		except Exception as e:
			self.reportError("Undo", e)

	def reportError(self, action, error):
		Glyphs.showMacroWindow()
		print(f"Guide Manager {action} Error: {error}")
		import traceback
		print(traceback.format_exc())
		self.setStatus("❌ Error. Details in Macro Window.")


GuideManager()
