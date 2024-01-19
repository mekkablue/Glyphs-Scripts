# MenuTitle: Cap and Corner Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Batch-edit settings for cap, corner, brush or segment components throughout all glyphs in the frontmost font.
"""

import vanilla
from GlyphsApp import Glyphs, Message, CORNER, CAP
from mekkablue import mekkaObject

# alignment constants:
LEFT = 0  # bit 0
RIGHT = 1  # bit 1
CENTER = 2  # bit 2
NOALIGN = 4  # bit 3
FIT = 8  # bit 4

alignmentOptions = (
	"Left",
	"Center",
	"Right",
	"None",
)

alignmentDict = {
	"Left": LEFT,
	"Center": RIGHT,
	"Right": CENTER,
	"None": NOALIGN,
}

alignmentLookupDict = {
	LEFT: "Left",
	RIGHT: "Center",
	CENTER: "Right",
	NOALIGN: "None",
}


def disableBit(number, bit):
	return number ^ 2**bit


def enableBit(number, bit):
	return number | 2**bit


class CapAndCornerManager(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"componentName": "",
		"shouldAlign": 0,
		"alignment": 0,
		"shouldFit": 1,
		"fit": 1,
		"shouldScale": 0,
		"scaleH": 100,
		"scaleV": 100,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 200
		windowHeight = 190
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Cap and Corner Manager",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight, tab = 12, 15, 22, 60

		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Batch-edit in frontmost font:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.componentName = vanilla.ComboBox((inset, linePos - 2, -inset - 25, 19), self.cornersOfFrontmostFont(), sizeStyle="small", callback=self.SavePreferences)
		self.w.componentName.getNSComboBox().setToolTip_("Batch-edit all instances of this special component. Can be a Brush, Segment, Cap and Corner component.")
		self.w.updateComponentNames = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle="small", callback=self.updateGUI)
		self.w.updateComponentNames.getNSButton().setToolTip_("Update the list of available components for the frontmost font.")
		linePos += lineHeight + 5

		self.w.shouldAlign = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Align", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.alignment = vanilla.PopUpButton((inset + tab, linePos, -inset, 17), alignmentOptions, sizeStyle="small", callback=self.SavePreferences)
		tooltip = "Alignment options for Cap and Corner components."
		self.w.shouldAlign.getNSButton().setToolTip_(tooltip)
		self.w.alignment.getNSPopUpButton().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.shouldFit = vanilla.CheckBox((inset, linePos - 1, tab, 20), "Fit Cap", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.fit = vanilla.PopUpButton((inset + tab, linePos, -inset, 17), ("Off (don’t fit)", "On (do fit)"), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "Fit option for Cap components."
		self.w.shouldFit.getNSButton().setToolTip_(tooltip)
		self.w.fit.getNSPopUpButton().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.shouldScale = vanilla.CheckBox((inset, linePos - 1, tab, 20), "Scale", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.scaleH = vanilla.EditText((inset + tab, linePos - 1, 40, 19), "100", callback=self.SavePreferences, sizeStyle="small")
		self.w.scaleH.getNSTextField().setToolTip_("Horizontal scale for components in percent. 100 means unscaled.")
		self.w.scaleV = vanilla.EditText((inset + tab + 45, linePos - 1, 40, 19), "100", callback=self.SavePreferences, sizeStyle="small")
		self.w.scaleV.getNSTextField().setToolTip_("Vertical scale for components in percent. 100 means unscaled.")
		self.w.resetScale = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle="small", callback=self.updateGUI)
		self.w.resetScale.getNSButton().setToolTip_("Resets the scale to 100% horizontal, 100% vertical.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Apply", sizeStyle="regular", callback=self.CapAndCornerManagerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def cornersOfFrontmostFont(self, sender=None):
		frontmostFont = Glyphs.font
		if not frontmostFont:
			return []
		return [g.name for g in frontmostFont.glyphs if g.category == "Corner"]

	def updateGUI(self, sender=None):
		if sender == self.w.resetScale:
			for orientation in "HV":
				prefName = f"scale{orientation}"
				Glyphs.defaults[self.domain(prefName)] = "100"
				self.LoadPreferences()
			return

		currentComponentName = self.pref("componentName")

		if sender == self.w.updateComponentNames:
			componentNames = self.cornersOfFrontmostFont()
			self.w.componentName.setItems(componentNames)
			if currentComponentName in componentNames:
				self.w.componentName.set(currentComponentName)

		enableFit = currentComponentName.startswith("_cap.")
		self.w.shouldFit.enable(enableFit)
		self.w.fit.enable(enableFit and self.pref("shouldFit"))

		enableAlign = enableFit or currentComponentName.startswith("_corner.")
		self.w.shouldAlign.enable(enableAlign)
		self.w.alignment.enable(enableAlign and self.pref("shouldAlign"))

		enableScale = bool(currentComponentName)
		self.w.shouldScale.enable(enableScale)
		self.w.scaleH.enable(enableScale and self.pref("shouldScale") and not (self.pref("shouldFit") and self.pref("fit")))
		self.w.scaleV.enable(enableScale and self.pref("shouldScale"))

		enableApply = any([self.pref(x) for x in ("shouldAlign", "shouldScale", "shouldFit")]) and enableScale
		self.w.runButton.enable(enableApply)

	def CapAndCornerManagerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			# read prefs:
			componentName = self.pref("componentName").strip()

			shouldAlign = self.pref("shouldAlign")
			alignment = alignmentDict[alignmentOptions[self.pref("alignment")]]

			shouldFit = self.pref("shouldFit")
			fit = self.prefInt("fit") * int(shouldFit) * FIT  # so you can add alignment+fit for caps

			shouldScale = self.pref("shouldScale")
			scaleH = self.prefFloat("scaleH") / 100.0
			scaleV = self.prefFloat("scaleV") / 100.0

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and try again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				fontName = thisFont.familyName
				if filePath:
					fontName = filePath.lastPathComponent()
					reportName = f"{fontName}\n📄 {filePath}"
				else:
					reportName = f"{fontName}\n⚠️ The font file has not been saved yet."
				print(f"Cap and Corner Manager Report for {reportName}")
				print()

				tabText = ""
				for thisGlyph in thisFont.glyphs:
					if thisGlyph.category == "Corner":
						continue
						# skip special components themselves

					glyphIsAffected = False
					for thisLayer in thisGlyph.layers:
						if not thisLayer.hints:
							continue
						for thisHint in thisLayer.hints:
							if thisHint.name != componentName:
								continue

							if shouldAlign:
								if thisHint.type == CORNER and thisHint.options != alignment:
									thisHint.options = alignment
									glyphIsAffected = True
								elif thisHint.type == CAP:
									currentAlign = thisHint.options & (LEFT + RIGHT + CENTER + NOALIGN)
									if currentAlign != alignment:
										currentFit = thisHint.options & FIT
										thisHint.options = currentFit + alignment
										glyphIsAffected = True

							if shouldFit and thisHint.type == CAP:
								currentFit = thisHint.options & FIT
								if currentFit != fit:
									currentAlign = thisHint.options & (LEFT + RIGHT + CENTER + NOALIGN)
									thisHint.options = currentAlign + fit
									glyphIsAffected = True

							isFitted = (thisHint.type == CAP) and (thisHint.options & FIT == FIT)  # it is a cap and fit option is on
							canScale = (thisHint.scale.x != scaleH and not isFitted) or thisHint.scale.y != scaleV
							if shouldScale and canScale:
								if not isFitted:
									thisHint.scale.x = scaleH
									# do not scale horizontally if the cap is fitted (because H scale is determined by fit)
								thisHint.scale.y = scaleV
								glyphIsAffected = True

					if glyphIsAffected:
						print(f"🔠 made changes in {thisGlyph.name}")
						tabText += f"/{thisGlyph.name}"

				if not tabText:
					print("No changes necessary.")
					Message(
						title=f"No changes in {fontName}",
						message=f"Could not find any instances of {componentName} that still needed the required changes.",
						OKButton=None,
					)
				else:
					thisFont.newTab("Affected glyphs:\n" + tabText)

			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Cap and Corner Manager Error: {e}")
			import traceback
			print(traceback.format_exc())


CapAndCornerManager()
