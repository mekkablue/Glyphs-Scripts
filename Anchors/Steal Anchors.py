# MenuTitle: Steal Anchors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Batch-copy the anchors from one font master to another.
"""

import vanilla
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSAnchor, Message
from mekkaCore import mekkaObject, italicize


class StealAnchors(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
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
	orderedFonts = Glyphs.fonts

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 265
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Steal Anchors",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 8, 15, 22
		tab = 110
		self.w.textFont = vanilla.TextBox((inset + tab, linePos + 2, tab, 14), "Font:", sizeStyle="small", selectable=True)
		self.w.textMaster = vanilla.TextBox((inset + tab * 2, linePos + 2, tab, 14), "Master:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.originText = vanilla.TextBox((inset, linePos + 2, tab, 14), "Copy anchors from:", sizeStyle="small", selectable=True)
		self.w.originFont = vanilla.PopUpButton((inset + tab, linePos, tab, 17), self.availableFonts(), sizeStyle="small", callback=self.SavePreferences)
		self.w.originMaster = vanilla.PopUpButton((inset + tab * 2, linePos, -inset, 17), self.availableOriginMasters(), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "The font/master combination that serves as source for anchors to be copied. Choose the All Masters option to copy from all masters at once."
		self.w.originText.getNSTextField().setToolTip_(tooltip)
		self.w.originFont.getNSPopUpButton().setToolTip_(tooltip)
		self.w.originMaster.getNSPopUpButton().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.targetText = vanilla.TextBox((inset, linePos + 2, tab, 14), "Paste them into:", sizeStyle="small", selectable=True)
		self.w.targetFont = vanilla.PopUpButton((inset + tab, linePos, tab, 17), self.availableFonts(), sizeStyle="small", callback=self.SavePreferences)
		self.w.targetMaster = vanilla.PopUpButton((inset + tab * 2, linePos, -inset, 17), self.availableTargetMasters(), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "The font/master combination that serves as target for anchors to be pasted."
		self.w.targetText.getNSTextField().setToolTip_(tooltip)
		self.w.targetFont.getNSPopUpButton().setToolTip_(tooltip)
		self.w.targetMaster.getNSPopUpButton().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.allMasters = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Copy from (and paste into) all masters of the fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allMasters.getNSButton().setToolTip_("Copy from all masters of the source font to all masters of the target font.")
		linePos += lineHeight

		self.w.overwriteExistingAnchors = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Delete existing anchors in target before copying", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.overwriteExistingAnchors.getNSButton().setToolTip_("If enabled, will reset the anchors in the target font to whatever is in the source font. If disabled, will skip anchors that are already in the target font, and only add the ones that are missing.")
		linePos += lineHeight

		self.w.respectItalicAngle = vanilla.CheckBox((inset, linePos - 1, 160, 20), "Adjust for italic angles", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.respectItalicAngle.getNSButton().setToolTip_("If enabled, will slant the anchor positions accordiing to the italic angles in both fonts. Useful for transfering from Roman to Italic.")
		self.w.respectWidths = vanilla.CheckBox((inset + 160, linePos - 1, -inset, 20), "Adjust for widths", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.respectWidths.getNSButton().setToolTip_("If enabled, will scale the x coordinates of the anchors so they fit into the width of the target glyph.")
		linePos += lineHeight

		self.w.targetSelectedGlyphsOnly = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Limit to selected glyphs in target font", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.targetSelectedGlyphsOnly.getNSButton().setToolTip_("If enabled, will only copy into the glyphs that are selected in the target font. If disabled, will copy into all glyphs.")
		linePos += lineHeight

		self.w.includeNonExportingGlyphs = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Include non-exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeNonExportingGlyphs.getNSButton().setToolTip_("If enabled, will ignore all glyphs that are sentto not export. Useful for not messing up helper glyphs.")
		linePos += lineHeight

		self.w.excludeCapAndCorner = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Exclude _cap, _corner, _segment, _brush (recommended)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.excludeCapAndCorner.getNSButton().setToolTip_("If enabled, will ignore special components, no matter what the other settings say. Strongly recommended.")
		linePos += lineHeight

		# Run Button:
		self.w.updateButton = vanilla.Button((-180 - inset, -20 - inset, -90 - inset, -inset), "Update", sizeStyle="regular", callback=self.updateUI)
		self.w.updateButton.getNSButton().setToolTip_("Will update the popup menus above. Use this if you opened a new font after opening this dialog.")
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Steal", sizeStyle="regular", callback=self.StealAnchorsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Steal Anchors’ could not load preferences. Will resort to defaults.")

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
		popups = (
			self.w.originFont,
			self.w.targetFont,
		)
		for popupButton in popups:
			availableFonts = self.availableFonts()
			if popupButton.getItems() != availableFonts:
				self.orderedFonts = Glyphs.fonts
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
			if not self.SavePreferences():
				print("⚠️ ‘Steal Anchors’ could not write preferences.")

			if Glyphs.font is None:
				Message(title="No Font Open", message="The script requires at least one font. Open a font and run the script again.", OKButton=None)
			else:
				originFont = self.orderedFonts[self.pref("originFont")]
				targetFont = self.orderedFonts[self.pref("targetFont")]

				originMaster = originFont.masters[self.pref("originMaster")]
				targetMaster = targetFont.masters[self.pref("targetMaster")]

				print(f"Steal Anchors\nOrigin: {originFont.familyName}, {originMaster.name}\nTarget: {targetFont.familyName}, {targetMaster.name}\n")

				if self.pref("targetSelectedGlyphsOnly"):
					targetGlyphs = [layer.parent for layer in targetFont.selectedLayers]
				else:
					targetGlyphs = [g for g in targetFont.glyphs if g.export or self.pref("includeNonExportingGlyphs")]

				for targetGlyph in targetGlyphs:
					originGlyph = originFont.glyphs[targetGlyph.name]
					if not originGlyph:
						print(f"⚠️ Missing in origin font: {targetGlyph.name}. Skipping.")
						continue
					if targetGlyph.name.startswith("_") and self.pref("excludeCapAndCorner"):
						if any([targetGlyph.name.startswith(x) for x in excludedPrefixes]):
							continue

					anchorCount = 0
					for i, stepMaster in enumerate(targetFont.masters):
						originLayer = None
						if self.pref("allMasters"):
							originIndex = min(len(originFont.masters) - 1, i)
							originStepMaster = originFont.masters[originIndex]
							originLayer = originGlyph.layers[originStepMaster.id]
						elif stepMaster == targetMaster:
							originLayer = originGlyph.layers[originMaster.id]

						if originLayer:
							targetLayers = [targetGlyph.layers[stepMaster.id]]
							for specialLayer in targetGlyph.layers:
								if specialLayer.isSpecialLayer and not specialLayer.isMasterLayer:
									targetLayers.append(specialLayer)
							for targetLayer in targetLayers:
								# TODO: find better origin layer if exists (for brace/bracket layers)
								if self.pref("overwriteExistingAnchors"):
									targetLayer.anchors = None
								for originAnchor in originLayer.anchors:
									if not targetLayer.anchors[originAnchor.name]:
										targetAnchor = GSAnchor(originAnchor.name, originAnchor.position)
										if self.pref("respectItalicAngle") and targetLayer.italicAngle != originLayer.italicAngle:
											pivot = targetLayer.master.slantHeightForLayer_(targetLayer)
											if not pivot:
												pivot = targetLayer.master.xHeight * 0.5
											targetAnchor.position = italicize(
												targetAnchor.position,
												italicAngle=targetLayer.italicAngle - originLayer.italicAngle,
												pivotalY=pivot,
											)
										if self.pref("respectWidths") and targetLayer.width != originLayer.width:
											horizontalScaleFactor = targetLayer.width / originLayer.width
											targetAnchor.position = NSPoint(
												round(targetAnchor.position.x * horizontalScaleFactor),
												round(targetAnchor.position.y),
											)
										targetLayer.anchors.append(targetAnchor)
										anchorCount += 1

					print(f"🔤 {targetGlyph.name}: copied {anchorCount} anchor{'' if anchorCount == 1 else 's'}.")

					("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Steal Anchors Error: {e}")
			import traceback
			print(traceback.format_exc())


StealAnchors()
