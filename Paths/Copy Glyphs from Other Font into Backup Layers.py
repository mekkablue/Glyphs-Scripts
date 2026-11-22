# MenuTitle: Copy Glyphs from Other Font into Backup Layers
__doc__ = """
Creates backup layers for selected glyphs in target font, and fills them with the respective glyphs in source font.
"""

import vanilla
from AppKit import NSColor, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSTextAlignmentRight
from GlyphsApp import Glyphs
from mekkablue import mekkaObject, makeWindowResizable


class CopyGlyphsIntoBackupLayers(mekkaObject):
	prefDict = {
		"from_font": 0,
		"to_font": 0,
		"suffix": "Backup",
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Copy glyphs into backup layers",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		self.w.from_text = vanilla.TextBox("auto", "Backup layers from:", sizeStyle='small')
		tooltipText = "The font whose glyphs (on its current master) are copied into backup layers."
		self.w.from_text.setToolTip(tooltipText)
		self.w.from_font = vanilla.PopUpButton("auto", self.GetFonts(isSourceFont=True), sizeStyle='small', callback=self.buttonCheck)
		self.w.from_font.setToolTip(tooltipText)

		self.w.to_text = vanilla.TextBox("auto", "Into selected glyphs in:", sizeStyle='small')
		tooltipText = "The font whose selected glyphs receive the backup layers."
		self.w.to_text.setToolTip(tooltipText)
		self.w.to_font = vanilla.PopUpButton("auto", self.GetFonts(isSourceFont=False), sizeStyle='small', callback=self.buttonCheck)
		self.w.to_font.setToolTip(tooltipText)

		self.w.suffix_text = vanilla.TextBox("auto", "Layer name suffix:", sizeStyle='small')
		tooltipText = "Text appended to the master name to name the new backup layers."
		self.w.suffix_text.setToolTip(tooltipText)
		self.w.suffix = vanilla.EditText("auto", "Backup", sizeStyle='small')
		self.w.suffix.setToolTip(tooltipText)

		self.w.status = vanilla.TextBox("auto", "🤖 Ready. 💬 See tooltips for help.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")
		self.w.status.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.copybutton = vanilla.Button("auto", "Copy", callback=self.CopyGlyphsIntoBackupLayersMain)
		self.w.copybutton.setToolTip("Copies the glyphs from the source font into backup layers of the selected glyphs in the target font.")
		self.w.setDefaultButton(self.w.copybutton)
		self.w.copybutton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.copybutton.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned and share the width of the widest one, so the fields line up:
		labelNames = ("from_text", "to_text", "suffix_text")
		widestLabel = "to_text"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[from_text]-gap-[from_font]-inset-|",
				"H:|-inset-[to_text]-gap-[to_font]-inset-|",
				"H:|-inset-[suffix_text]-gap-[suffix]-inset-|",
				"H:|-inset-[status]-gap-[copybutton(>=70)]-inset-|",
				"V:|-inset-[from_font]-row-[to_font]-row-[suffix]-inset-[copybutton]-inset-|",
				{"view1": self.w.from_text, "attribute1": "centerY", "view2": self.w.from_font, "attribute2": "centerY"},
				{"view1": self.w.to_text, "attribute1": "centerY", "view2": self.w.to_font, "attribute2": "centerY"},
				{"view1": self.w.suffix_text, "attribute1": "centerY", "view2": self.w.suffix, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.copybutton, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.buttonCheck()

	def fontTitle(self, document):
		return "%s - %s" % (document.font.familyName, document.selectedFontMaster().name)

	def GetFonts(self, isSourceFont):
		myFontList = [self.fontTitle(x) for x in Glyphs.orderedDocuments()]

		if isSourceFont:
			myFontList.reverse()

		return myFontList

	def buttonCheck(self, sender=None):
		fromFonts = self.w.from_font.getItems()
		toFonts = self.w.to_font.getItems()
		fromIndex = self.w.from_font.get()
		toIndex = self.w.to_font.get()
		if not 0 <= fromIndex < len(fromFonts) or not 0 <= toIndex < len(toFonts):
			# no font open, or nothing selected in the popups
			self.w.copybutton.enable(onOff=False)
			return

		if fromFonts[fromIndex] == toFonts[toIndex]:
			self.w.copybutton.enable(onOff=False)
		else:
			self.w.copybutton.enable(onOff=True)

	def CopyGlyphsIntoBackupLayersMain(self, sender):
		lastItem = "start"
		try:
			self.setStatus("🛠️ Processing …")
			fromFont = self.w.from_font.getItems()[self.w.from_font.get()]
			toFont = self.w.to_font.getItems()[self.w.to_font.get()]
			layerSuffix = self.w.suffix.get()

			Doc_source = [x for x in Glyphs.orderedDocuments() if self.fontTitle(x) == fromFont][0]
			Font_source = Doc_source.font
			Font_target = [x.font for x in Glyphs.orderedDocuments() if self.fontTitle(x) == toFont][0]

			MasterID_source = Font_source.selectedFontMaster.id
			MasterID_target = Font_target.selectedFontMaster.id

			Glyphs_selected = [layer.parent for layer in Font_target.selectedLayers]

			self.setStatus(f"🛠️ Processing {len(Glyphs_selected)} glyphs …")
			missingCount = 0
			print("Backing up", len(Glyphs_selected), "glyphs from", Font_source.familyName, "into", Font_target.familyName, ":")

			for targetGlyph in Glyphs_selected:
				glyphName = targetGlyph.name
				lastItem = glyphName
				self.setStatus(f"🔠 {glyphName}")
				sourceGlyph = Font_source.glyphs[glyphName]
				if not sourceGlyph:
					# font.glyphs[name] returns None for a missing glyph, it does not raise
					print("  Error: glyph %s not found in source font %s." % (glyphName, Font_source.familyName))
					missingCount += 1
				else:
					sourceLayer = sourceGlyph.layers[MasterID_source].copy()
					targetMasterName = targetGlyph.layers[MasterID_target].name

					targetGlyph.layers[MasterID_source] = sourceLayer
					targetGlyph.layers[MasterID_source].setAssociatedMasterId_(MasterID_target)
					targetGlyph.layers[MasterID_source].setName_("%s %s" % (targetMasterName, layerSuffix))

			self.SavePreferences()

			if not Glyphs_selected:
				self.setStatus("⚠️ No glyphs selected.")
			elif missingCount:
				self.setStatus(f"⚠️ Backed up {len(Glyphs_selected) - missingCount} glyphs, {missingCount} not found in source font.")
			else:
				self.setStatus(f"✅ Backed up {len(Glyphs_selected)} glyphs.")
			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			self.setStatus(f"❌ Error at {lastItem}. Details in Macro Window.")
			print("Script Error: %s" % e)


CopyGlyphsIntoBackupLayers()
