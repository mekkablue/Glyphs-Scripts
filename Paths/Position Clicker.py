# MenuTitle: Position Clicker
__doc__ = """
Finds all combinations of positional shapes that do not click well. Clicking means sharing two point coordinates when overlapping.
"""

import objc
import vanilla
from mekkablue import mekkaObject, newLineControlLayer, UpdateButton
from GlyphsApp import Glyphs, GSOFFCURVE, Message
from AppKit import (
	NSColor,
	NSFont,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)
from Foundation import NSNumberFormatter


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def layerMissesPointsAtCoordinates(thisLayer, coordinates):
	tickOff = list(coordinates)
	for thisPath in thisLayer.paths:
		if tickOff:
			for thisNode in thisPath.nodes:
				while thisNode.position in tickOff:
					tickOff.remove(thisNode.position)
	return tickOff


def isPositional(glyphName):
	for suffix in ("medi", "init", "fina"):
		if suffix in glyphName.split("."):
			return True
	if glyphName.startswith("kashida"):
		return True
	return False


def correctForCursiveAttachment(layer, anchorName):
	anchor = layer.anchors[anchorName]
	if anchor:
		layer.applyTransform((1, 0, 0, 1, -anchor.x, -anchor.y))
		layer.width = 0
	return layer


def roundedCoord(coord):
	coord.x = int(coord.x)
	coord.y = int(coord.y)
	return coord


def doTheyClick(leftLayer, rightLayer, requiredClicks=2, verbose=False):
	leftCompareLayer = correctForCursiveAttachment(leftLayer.copyDecomposedLayer(), "entry")
	rightCompareLayer = correctForCursiveAttachment(rightLayer.copyDecomposedLayer(), "exit")
	leftWidth = leftCompareLayer.width
	rightCoordinates = []
	for p in rightCompareLayer.paths:
		for n in p.nodes:
			if n.type != GSOFFCURVE:
				coord = n.position
				coord.x += leftWidth
				coord = roundedCoord(coord)  # catch floating point errors
				rightCoordinates.append(coord)
	clickCount = 0
	for p in leftCompareLayer.paths:
		for n in p.nodes:
			coord = n.position
			coord = roundedCoord(coord)  # catch floating point errors
			if coord in rightCoordinates:
				clickCount += 1
	if clickCount < requiredClicks:
		print("❌ %s does not click with a following %s (%s)." % (rightLayer.parent.name, leftLayer.parent.name, leftLayer.name))
		# print(rightCoordinates)
		return False
	else:
		if verbose:
			print("✅ OK: %s ⟺ %s  Ⓜ️ %s" % (
				leftLayer.parent.name,
				rightLayer.parent.name,
				leftLayer.master.name,
			))
		return True


class PositionClicker(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"referenceGlyphName": "behDotless-ar.medi",
		"ignoreGlyphs": ".alt, .calt, .pre, .post",
		"clickCount": 2,
		"includeNonExporting": False,
		"reuseTab": False,
		"verbose": False,
		"includeComposites": False,
		"limitToSelection": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Position Clicker",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Report positional combos that do not click", sizeStyle="small", selectable=True)
		self.w.descriptionText.setToolTip("Clicking means that when two matching positional shapes follow each other (e.g. initial and final), they 'click', i.e., they share at least 2 node coordinates. Or whatever number is set in the minimal node count setting below.")

		tooltip = "Reference glyph. Pick a medial glyph with paths for clicking. We recommend behDotless-ar.medi."
		self.w.referenceText = vanilla.TextBox("auto", "Click with glyph", sizeStyle="small", selectable=True)
		self.w.referenceText.setToolTip(tooltip)
		self.w.referenceGlyphName = vanilla.ComboBox("auto", self.getAllMediGlyphNames(), sizeStyle="small", callback=self.SavePreferences)
		self.w.referenceGlyphName.getNSComboBox().setFont_(NSFont.userFixedPitchFontOfSize_(10))
		self.w.referenceGlyphName.setToolTip(tooltip)
		self.w.updateButton = UpdateButton("auto", callback=self.updateReferenceGlyphs)
		self.w.updateButton.setToolTip("Update the list in the combo box with all .medi glyphs in the frontmost font.")

		tooltip = "The amount of point coordinates that must be shared between two consecutive positional forms. E.g., if set to 2, an initial and a final shape must have two or more nodes exactly on top of each other when they follow each other. Will respect exit and entry anchors."
		self.w.clickCountText = vanilla.TextBox("auto", "Min count of node clicks", sizeStyle="small", selectable=True)
		clickCountFormatter = NSNumberFormatter.alloc().init()
		clickCountFormatter.setAllowsFloats_(False)
		clickCountFormatter.setMinimum_(1)
		self.w.clickCount = SteppingEditText("auto", "2", callback=self.SavePreferences, sizeStyle="small", formatter=clickCountFormatter)
		self.w.clickCountText.setToolTip(tooltip)
		self.w.clickCount.setToolTip(tooltip)

		tooltip = "Ignore glyphs that contain any of these name particles. Useful if you have alternates that are intentionally not clicking with the reference glyph, e.g. because they are contextual alternates for specific situations. Use comma's to separate multiple particles."
		self.w.ignoreGlyphsText = vanilla.TextBox("auto", "Ignore glyphs containing", sizeStyle="small", selectable=True)
		self.w.ignoreGlyphs = vanilla.EditText("auto", ".alt, .calt, .pre, .post", callback=self.SavePreferences, sizeStyle="small")
		self.w.ignoreGlyphsText.setToolTip(tooltip)
		self.w.ignoreGlyphs.setToolTip(tooltip)

		self.w.includeNonExporting = vanilla.CheckBox("auto", "Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeNonExporting.setToolTip("Will also measure glyphs that are set to not export.")

		self.w.includeComposites = vanilla.CheckBox("auto", "Include composites", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeComposites.setToolTip("Will also check glyphs that consist entirely of components (no paths of their own).")

		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.reuseTab.setToolTip("Will use the current tab for output. Will open a new tab only if there is no Edit tab open already.")

		self.w.verbose = vanilla.CheckBox("auto", "Verbose reporting", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose.setToolTip("Also reports successful clicks in Macro Window (slow).")

		self.w.limitToSelection = vanilla.CheckBox("auto", "Limit to selected glyphs only", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.limitToSelection.setToolTip("Only check glyphs that are currently selected in the font window or edit tab, instead of all glyphs in the font.")

		# Status line and Run Button:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.runButton = vanilla.Button("auto", "Open Tab", callback=self.PositionClickerMain)
		self.w.runButton.setToolTip("Run the check and open a tab with all non-clicking combinations.")
		self.w.setDefaultButton(self.w.runButton)

		# labels: right-aligned, same width
		labelNames = ("referenceText", "clickCountText", "ignoreGlyphsText")
		widestLabel = "ignoreGlyphsText"  # the label with the longest text
		fieldNames = {"referenceText": "referenceGlyphName", "clickCountText": "clickCount", "ignoreGlyphsText": "ignoreGlyphs"}
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]
		centerRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "centerY", "view2": getattr(self.w, fieldNames[labelName]), "attribute2": "centerY"}
			for labelName in labelNames
		]

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[referenceText]-gap-[referenceGlyphName]-gap-[updateButton(20)]-inset-|",
				"H:|-inset-[clickCountText]-gap-[clickCount(50)]-(>=inset)-|",
				"H:|-inset-[ignoreGlyphsText]-gap-[ignoreGlyphs]-inset-|",
				"H:|-inset-[includeNonExporting]-gap-[includeComposites]-(>=inset)-|",
				"H:|-inset-[reuseTab]-gap-[verbose]-(>=inset)-|",
				"H:|-inset-[limitToSelection]-(>=inset)-|",
				"H:|-inset-[status]-gap-[runButton(>=100)]-inset-|",
				"V:|-gap-[descriptionText]-row-[referenceGlyphName]-row-[clickCount]-row-[ignoreGlyphs]-row-[includeNonExporting]-checkRow-[reuseTab]-checkRow-[limitToSelection]-inset-[runButton]-inset-|",
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.referenceGlyphName, "attribute2": "centerY"},
				{"view1": self.w.includeComposites, "attribute1": "centerY", "view2": self.w.includeNonExporting, "attribute2": "centerY"},
				{"view1": self.w.verbose, "attribute1": "centerY", "view2": self.w.reuseTab, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.reuseTab, "attribute1": "width", "view2": self.w.includeNonExporting, "attribute2": "width"},
			] + widthRules + centerRules,
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateReferenceGlyphs(self, sender=None):
		self.w.referenceGlyphName.setItems(self.getAllMediGlyphNames())

	def updateUI(self, sender=None):
		glyphSelected = self.w.referenceGlyphName.get()
		atLeastOneClick = self.prefInt("clickCount") > 0
		self.w.runButton.enable(bool(glyphSelected) and atLeastOneClick)

	def getAllMediGlyphNames(self, sender=None):
		font = Glyphs.font
		fallback = "behDotless-ar.medi"
		if not font:
			return [fallback]
		else:
			glyphNames = []
			for g in font.glyphs:
				if ".medi" in g.name or g.name.startswith("kashida") or g.unicode == "0640":
					glyphNames.append(g.name)
			if fallback in glyphNames:
				glyphNames.remove(fallback)
				glyphNames.insert(0, fallback)
			return glyphNames

	def PositionClickerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			self.w.status.set("⏳ Checking…")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Position Clicker Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				referenceGlyphName = self.pref("referenceGlyphName")
				includeNonExporting = self.pref("includeNonExporting")
				reuseTab = self.pref("reuseTab")
				clickCount = self.prefInt("clickCount")
				includeComposites = self.pref("includeComposites")
				verbose = self.pref("verbose")
				limitToSelection = self.pref("limitToSelection")
				ignoreParticles = [name.strip() for name in self.pref("ignoreGlyphs").split(",")]

				if limitToSelection:
					selectedGlyphNames = set(l.parent.name for l in (thisFont.selectedLayers or []) if l.parent)

				try:
					spaceLayer = thisFont.glyphs["space"].layers[0]
				except:
					spaceLayer = newLineControlLayer()

				referenceGlyph = thisFont.glyphs[referenceGlyphName]
				try:
					# GLYPHS 3
					isRTL = referenceGlyph.direction == 2  # 0=LTR, 1=BiDi, 2=RTL
				except:
					# GLYPHS 2
					isRTL = True

				tabLayers = []
				count = 0
				comboCount = 0
				for thisGlyph in thisFont.glyphs:
					glyphName = thisGlyph.name
					if glyphName == referenceGlyphName:
						continue
					if limitToSelection and glyphName not in selectedGlyphNames:
						continue
					if any([part in glyphName for part in ignoreParticles]):
						continue

					if isPositional(glyphName):
						nameParticles = glyphName.split(".")
						comesFirst = "medi" in nameParticles or "init" in nameParticles or glyphName.startswith("kashida")
						comesLater = "medi" in nameParticles or "fina" in nameParticles or glyphName.startswith("kashida")
						if thisGlyph.export or includeNonExporting:
							for thisLayer in thisGlyph.layers:
								if (thisLayer.isMasterLayer or thisLayer.isSpecialLayer) and (thisLayer.paths or includeComposites):
									comboCount += 1
									referenceLayer = referenceGlyph.layers[thisLayer.master.id]
									if referenceLayer is None:
										continue
									if (comesFirst and isRTL) or (comesLater and not isRTL):
										if not doTheyClick(referenceLayer, thisLayer, clickCount, verbose):
											tabLayers.append(referenceLayer)
											tabLayers.append(thisLayer)
											tabLayers.append(spaceLayer)
											count += 1
									if (comesLater and isRTL) or (comesFirst and not isRTL):
										if not doTheyClick(thisLayer, referenceLayer, clickCount, verbose):
											tabLayers.append(thisLayer)
											tabLayers.append(referenceLayer)
											tabLayers.append(spaceLayer)
											count += 1

				if comboCount == 0:
					if limitToSelection:
						Message(
							title="No Positional Glyphs in Selection",
							message="⚠️ None of the selected glyphs are positional (no .init, .medi, or .fina suffix). Select some positional glyphs and try again.",
							OKButton=None,
						)
					else:
						Message(
							title="No Positional Glyphs in Font",
							message="⚠️ No positional glyphs (.init, .medi, .fina) were found in the font.",
							OKButton=None,
						)
				elif len(tabLayers) > 0:
					Glyphs.showNotification(
						"%s: Position Clicker" % (thisFont.familyName),
						"Found %i imprecise connections. Details in Macro Window." % count,
					)
					if not reuseTab or not thisFont.currentTab:
						# opens new Edit tab:
						tab = thisFont.newTab()
					else:
						tab = thisFont.currentTab
					tab.layers = tabLayers
					tab.direction = 0  # LTR!
				else:
					Message(
						title="Position Clicker found no problems 😃",
						message="✅ Checked %i combinations on %i master%s in %s: all positional glyphs click on %i points or more. Good job!\nDetailed report in Macro Window." % (
							comboCount,
							len(thisFont.masters),
							"" if len(thisFont.masters) == 1 else "s",
							thisFont.filepath.lastPathComponent() if thisFont.filepath else thisFont.familyName,
							clickCount,
						),
						OKButton="🥂Cool",
					)

			self.w.status.set("✅ Done.")
			print("\nDone.")

		except Exception as e:
			self.w.status.set("❌ Error.")
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Position Clicker Error: %s" % e)
			import traceback
			print(traceback.format_exc())


PositionClicker()
