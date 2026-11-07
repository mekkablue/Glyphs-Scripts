# MenuTitle: Steal Anchors
__doc__ = """
Batch-copy the anchors from one font master to another.
"""

import vanilla
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)
from Foundation import NSPoint
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, newAnchorWithName, UpdateButton
from mekkablue.geometry import italicize


class StealAnchors(mekkaObject):
	prefDict = {
		"originFont": 0,
		"originMaster": 0,
		"targetFont": 0,
		"targetMaster": 0,
		"allMasters": 0,
		"respectItalicAngle": 1,
		"respectWidths": 1,
		"targetSelectedGlyphsOnly": 0,
		"overwriteExistingAnchors": 0,
		"includeNonExportingGlyphs": 1,
		"excludeCapAndCorner": 1,
	}

	def __init__(self):
		self.orderedFonts = list(Glyphs.fonts)

		# Window 'self.w':
		windowWidth = 470
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Steal Anchors",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.textFont = vanilla.TextBox("auto", "Font:", sizeStyle="small", selectable=True)
		self.w.textMaster = vanilla.TextBox("auto", "Master:", sizeStyle="small", selectable=True)
		self.w.updateButton = UpdateButton("auto", callback=self.updateUI)
		self.w.updateButton.setToolTip("Will update the popup menus below. Use this if you opened a new font after opening this dialog.")

		self.w.originText = vanilla.TextBox("auto", "Copy anchors from:", sizeStyle="small", selectable=True)
		self.w.originFont = vanilla.PopUpButton("auto", self.availableFonts(), sizeStyle="small", callback=self.SavePreferences)
		self.w.originMaster = vanilla.PopUpButton("auto", self.availableOriginMasters(), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "The font/master combination that serves as source for anchors to be copied. Choose the All Masters option to copy from all masters at once."
		self.w.originText.setToolTip(tooltip)
		self.w.originFont.setToolTip(tooltip)
		self.w.originMaster.setToolTip(tooltip)

		self.w.targetText = vanilla.TextBox("auto", "Paste them into:", sizeStyle="small", selectable=True)
		self.w.targetFont = vanilla.PopUpButton("auto", self.availableFonts(), sizeStyle="small", callback=self.SavePreferences)
		self.w.targetMaster = vanilla.PopUpButton("auto", self.availableTargetMasters(), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "The font/master combination that serves as target for anchors to be pasted."
		self.w.targetText.setToolTip(tooltip)
		self.w.targetFont.setToolTip(tooltip)
		self.w.targetMaster.setToolTip(tooltip)

		self.w.allMasters = vanilla.CheckBox("auto", "Copy from (and paste into) all masters of the fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allMasters.setToolTip("Copy from all masters of the source font to all masters of the target font.")

		self.w.overwriteExistingAnchors = vanilla.CheckBox("auto", "Delete existing anchors in target before copying", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.overwriteExistingAnchors.setToolTip("If enabled, will reset the anchors in the target font to whatever is in the source font. If disabled, will skip anchors that are already in the target font, and only add the ones that are missing.")

		self.w.respectItalicAngle = vanilla.CheckBox("auto", "Adjust for italic angles", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.respectItalicAngle.setToolTip("If enabled, will slant the anchor positions according to the italic angles in both fonts. Useful for transferring from Roman to Italic.")
		self.w.respectWidths = vanilla.CheckBox("auto", "Adjust for widths", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.respectWidths.setToolTip("If enabled, will scale the x coordinates of the anchors so they fit into the width of the target glyph.")

		self.w.targetSelectedGlyphsOnly = vanilla.CheckBox("auto", "Limit to selected glyphs in target font", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.targetSelectedGlyphsOnly.setToolTip("If enabled, will only copy into the glyphs that are selected in the target font. If disabled, will copy into all glyphs.")

		self.w.includeNonExportingGlyphs = vanilla.CheckBox("auto", "Include non-exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeNonExportingGlyphs.setToolTip("If enabled, will also copy anchors into glyphs that are set to not export. If disabled, will skip them, which is useful for not messing up helper glyphs.")

		self.w.excludeCapAndCorner = vanilla.CheckBox("auto", "Exclude _cap, _corner, _segment, _brush (recommended)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.excludeCapAndCorner.setToolTip("If enabled, will ignore special components, no matter what the other settings say. Strongly recommended.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Steal", callback=self.StealAnchorsMain)
		self.w.setDefaultButton(self.w.runButton)

		# right-align the row labels and let them hug their text:
		for labelName in ("originText", "targetText"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# the master popups list long IDs: let them truncate instead of widening the window
		for popupName in ("originFont", "originMaster", "targetFont", "targetMaster"):
			getattr(self.w, popupName).getNSPopUpButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[originText]-gap-[originFont]-gap-[originMaster]-inset-|",
				"H:|-inset-[targetText]-gap-[targetFont]-gap-[targetMaster]-inset-|",
				"H:[updateButton(>=20)]-inset-|",
				"H:|-inset-[allMasters]-(>=inset)-|",
				"H:|-inset-[overwriteExistingAnchors]-(>=inset)-|",
				"H:|-inset-[respectItalicAngle]-gap-[respectWidths]-(>=inset)-|",
				"H:|-inset-[targetSelectedGlyphsOnly]-(>=inset)-|",
				"H:|-inset-[includeNonExportingGlyphs]-(>=inset)-|",
				"H:|-inset-[excludeCapAndCorner]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[updateButton]-row-[originFont]-row-[targetFont]-inset-[allMasters]-checkRow-[overwriteExistingAnchors]-checkRow-[respectItalicAngle]-checkRow-[targetSelectedGlyphsOnly]-checkRow-[includeNonExportingGlyphs]-checkRow-[excludeCapAndCorner]-inset-[runButton]-inset-|",
				# column headers sit above their popups:
				{"view1": self.w.textFont, "attribute1": "left", "view2": self.w.originFont, "attribute2": "left"},
				{"view1": self.w.textMaster, "attribute1": "left", "view2": self.w.originMaster, "attribute2": "left"},
				{"view1": self.w.textFont, "attribute1": "centerY", "view2": self.w.updateButton, "attribute2": "centerY"},
				{"view1": self.w.textMaster, "attribute1": "centerY", "view2": self.w.updateButton, "attribute2": "centerY"},
				# labels share the baseline of their popups:
				{"view1": self.w.originText, "attribute1": "centerY", "view2": self.w.originFont, "attribute2": "centerY"},
				{"view1": self.w.originMaster, "attribute1": "centerY", "view2": self.w.originFont, "attribute2": "centerY"},
				{"view1": self.w.targetText, "attribute1": "centerY", "view2": self.w.targetFont, "attribute2": "centerY"},
				{"view1": self.w.targetMaster, "attribute1": "centerY", "view2": self.w.targetFont, "attribute2": "centerY"},
				{"view1": self.w.respectWidths, "attribute1": "centerY", "view2": self.w.respectItalicAngle, "attribute2": "centerY"},
				# columns of the two popup rows line up:
				{"view1": self.w.targetText, "attribute1": "width", "view2": self.w.originText, "attribute2": "width"},
				{"view1": self.w.targetFont, "attribute1": "width", "view2": self.w.originFont, "attribute2": "width"},
				{"view1": self.w.targetMaster, "attribute1": "width", "view2": self.w.originMaster, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def availableFonts(self, sender=None):
		return [f"{i}: {f.familyName}" for i, f in enumerate(Glyphs.fonts)]

	def availableMasters(self, sender=None, fontPref="originFont"):
		returnList = []
		fontIndex = self.pref(fontPref)
		if fontIndex is None:
			fontIndex = 0
		if fontIndex < len(Glyphs.fonts):
			font = Glyphs.fonts[fontIndex]
			for i, master in enumerate(font.masters):
				returnList.append(f"{i}: {master.name} (ID: {master.id})")
		return returnList

	def availableOriginMasters(self, sender=None):
		return self.availableMasters(fontPref="originFont")

	def availableTargetMasters(self, sender=None):
		return self.availableMasters(fontPref="targetFont")

	def updateFontPopups(self, sender=None):
		availableFonts = self.availableFonts()
		for popupButton in (self.w.originFont, self.w.targetFont):
			if popupButton.getItems() != availableFonts:
				self.orderedFonts = list(Glyphs.fonts)
				popupButton.setItems(availableFonts)

	def updateMasterPopups(self, sender=None):
		popups = (
			{
				"fontPref": "originFont",
				"button": self.w.originMaster,
			},
			{
				"fontPref": "targetFont",
				"button": self.w.targetMaster,
			},
		)
		for popup in popups:
			availableMasters = self.availableMasters(fontPref=popup["fontPref"])
			popupButton = popup["button"]
			if popupButton.getItems() != availableMasters:
				popupButton.setItems(availableMasters)

	def updateUI(self, sender=None):
		self.updateFontPopups()
		self.updateMasterPopups()
		for popUpButton in (self.w.originMaster, self.w.targetMaster):
			popUpButton.enable(not self.pref("allMasters"))
		sameFonts = self.pref("originFont") == self.pref("targetFont")
		sameMasters = (self.pref("originMaster") == self.pref("targetMaster")) or self.pref("allMasters")
		self.w.runButton.enable(not (sameFonts and sameMasters))

	def StealAnchorsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			excludedPrefixes = ("_cap", "_corner", "_brush", "_segment")

			# update settings to the latest user input:
			self.SavePreferences()

			if Glyphs.font is None:
				Message(title="No Font Open", message="The script requires at least one font. Open a font and run the script again.", OKButton=None)
				return

			originFont = self.orderedFonts[self.pref("originFont")]
			targetFont = self.orderedFonts[self.pref("targetFont")]

			originMaster = originFont.masters[self.pref("originMaster")]
			targetMaster = targetFont.masters[self.pref("targetMaster")]

			allMasters = self.prefBool("allMasters")
			overwriteExistingAnchors = self.prefBool("overwriteExistingAnchors")
			respectItalicAngle = self.prefBool("respectItalicAngle")
			respectWidths = self.prefBool("respectWidths")
			excludeCapAndCorner = self.prefBool("excludeCapAndCorner")
			includeNonExportingGlyphs = self.prefBool("includeNonExportingGlyphs")

			print(f"Steal Anchors\nOrigin: {originFont.familyName}, {originMaster.name}\nTarget: {targetFont.familyName}, {targetMaster.name}\n")

			if self.prefBool("targetSelectedGlyphsOnly"):
				targetGlyphs = []
				for layer in targetFont.selectedLayers:  # several layers of one glyph may be selected
					if layer.parent not in targetGlyphs:
						targetGlyphs.append(layer.parent)
			else:
				targetGlyphs = [g for g in targetFont.glyphs if g.export or includeNonExportingGlyphs]

			for targetGlyph in targetGlyphs:
				originGlyph = originFont.glyphs[targetGlyph.name]
				if not originGlyph:
					print(f"\t⚠️ Missing in origin font: {targetGlyph.name}. Skipping.")
					continue
				if excludeCapAndCorner and targetGlyph.name.startswith(excludedPrefixes):
					continue

				anchorCount = 0
				for i, stepMaster in enumerate(targetFont.masters):
					originLayer = None
					if allMasters:
						originIndex = min(len(originFont.masters) - 1, i)
						originStepMaster = originFont.masters[originIndex]
						originLayer = originGlyph.layers[originStepMaster.id]
					elif stepMaster == targetMaster:
						originLayer = originGlyph.layers[originMaster.id]

					if originLayer is None:
						continue

					targetLayers = [targetGlyph.layers[stepMaster.id]]
					for specialLayer in targetGlyph.layers:
						# special layers (brace, bracket) belong to the master they are associated with:
						if specialLayer.isSpecialLayer and not specialLayer.isMasterLayer and specialLayer.associatedMasterId == stepMaster.id:
							targetLayers.append(specialLayer)

					for targetLayer in targetLayers:
						# TODO: find better origin layer if exists (for brace/bracket layers)
						if overwriteExistingAnchors:
							targetLayer.anchors = None
						for originAnchor in originLayer.anchors:
							if targetLayer.anchors[originAnchor.name]:
								continue
							targetAnchor = newAnchorWithName(originAnchor.name, originAnchor.position)
							if respectItalicAngle and targetLayer.italicAngle != originLayer.italicAngle:
								pivot = targetLayer.master.slantHeightForLayer_(targetLayer)
								if not pivot:
									pivot = targetLayer.master.xHeight * 0.5
								targetAnchor.position = italicize(
									targetAnchor.position,
									italicAngle=targetLayer.italicAngle - originLayer.italicAngle,
									pivotalY=pivot,
								)
							if respectWidths and originLayer.width and targetLayer.width != originLayer.width:  # origin width may be zero
								horizontalScaleFactor = targetLayer.width / originLayer.width
								targetAnchor.position = NSPoint(
									round(targetAnchor.position.x * horizontalScaleFactor),
									round(targetAnchor.position.y),
								)
							targetLayer.anchors.append(targetAnchor)
							anchorCount += 1

				print(f"\t🔤 {targetGlyph.name}: copied {anchorCount} anchor{'' if anchorCount == 1 else 's'}.")

			print("\n✅ Done.")
			Glyphs.showNotification("Steal Anchors", "Done! Details in Macro Window.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Steal Anchors Error: {e}")
			import traceback
			print(traceback.format_exc())


StealAnchors()
