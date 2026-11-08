# MenuTitle: Cap and Corner Manager
__doc__ = """
Batch-edit settings for cap, corner, brush or segment components throughout all glyphs in the frontmost font.
"""

import vanilla
from mekkablue import mekkaObject, UpdateButton
from GlyphsApp import Glyphs, Message, CORNER, CAP
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut

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
		windowWidth = 300
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Cap and Corner Manager",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Batch-edit in frontmost font", sizeStyle="small", selectable=True)

		self.w.componentName = vanilla.ComboBox("auto", self.cornersOfFrontmostFont(), sizeStyle="small", callback=self.SavePreferences)
		self.w.componentName.setToolTip("Batch-edit all instances of this special component. Can be a Brush, Segment, Cap and Corner component.")
		self.w.updateComponentNames = UpdateButton("auto", callback=self.updateUI)
		self.w.updateComponentNames.setToolTip("Update the list of available components for the frontmost font.")

		self.w.shouldAlign = vanilla.CheckBox("auto", "Align", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.alignment = vanilla.PopUpButton("auto", alignmentOptions, sizeStyle="small", callback=self.SavePreferences)
		tooltip = "Alignment options for Cap and Corner components."
		self.w.shouldAlign.setToolTip(tooltip)
		self.w.alignment.setToolTip(tooltip)

		self.w.shouldFit = vanilla.CheckBox("auto", "Fit Cap", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.fit = vanilla.PopUpButton("auto", ("Off (don’t fit)", "On (do fit)"), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "Fit option for Cap components."
		self.w.shouldFit.setToolTip(tooltip)
		self.w.fit.setToolTip(tooltip)

		self.w.shouldScale = vanilla.CheckBox("auto", "Scale", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.scaleH = vanilla.EditText("auto", "100", callback=self.SavePreferences, sizeStyle="small")
		self.w.scaleH.setToolTip("Horizontal scale for components in percent. 100 means unscaled.")
		self.w.scaleV = vanilla.EditText("auto", "100", callback=self.SavePreferences, sizeStyle="small")
		self.w.scaleV.setToolTip("Vertical scale for components in percent. 100 means unscaled.")
		self.w.resetScale = UpdateButton("auto", callback=self.updateUI)
		self.w.resetScale.setToolTip("Resets the scale to 100% horizontal, 100% vertical.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Apply", callback=self.CapAndCornerManagerMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[componentName]-gap-[updateComponentNames(20)]-inset-|",
				"H:|-inset-[shouldAlign]-gap-[alignment]-inset-|",
				"H:|-inset-[shouldFit]-gap-[fit]-inset-|",
				"H:|-inset-[shouldScale]-gap-[scaleH(50)]-gap-[scaleV(50)]-gap-[resetScale(20)]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[componentName]-row-[alignment]-row-[fit]-row-[scaleH]-inset-[runButton]-inset-|",
				{"view1": self.w.updateComponentNames, "attribute1": "centerY", "view2": self.w.componentName, "attribute2": "centerY"},
				{"view1": self.w.shouldAlign, "attribute1": "centerY", "view2": self.w.alignment, "attribute2": "centerY"},
				{"view1": self.w.shouldFit, "attribute1": "centerY", "view2": self.w.fit, "attribute2": "centerY"},
				{"view1": self.w.shouldScale, "attribute1": "centerY", "view2": self.w.scaleH, "attribute2": "centerY"},
				{"view1": self.w.scaleV, "attribute1": "centerY", "view2": self.w.scaleH, "attribute2": "centerY"},
				{"view1": self.w.resetScale, "attribute1": "centerY", "view2": self.w.scaleH, "attribute2": "centerY"},
				{"view1": self.w.shouldAlign, "attribute1": "width", "view2": self.w.shouldFit, "attribute2": "width"},
				{"view1": self.w.shouldScale, "attribute1": "width", "view2": self.w.shouldFit, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

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

	def updateUI(self, sender=None):
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
