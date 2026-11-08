# MenuTitle: Sample Strings with Master Kerning
__doc__ = """
Creates kern strings for the current kerning and adds them to the Sample Strings.
"""

import objc
import vanilla
import sampleText
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, GSUppercase, GSSmallcaps, Message
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSNumberFormatter


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def integerFormatter(minimum=None, maximum=None):
	"""Number formatter that only accepts integers, optionally within a range."""
	formatter = NSNumberFormatter.alloc().init()
	formatter.setAllowsFloats_(False)
	if minimum is not None:
		formatter.setMinimum_(minimum)
	if maximum is not None:
		formatter.setMaximum_(maximum)
	return formatter


class SampleStringsWithMasterKerning(mekkaObject):
	prefDict = {
		"groupToGroupOnly": 0,
		"positivePairs": 1,
		"negativePairs": 1,
		"zeroPairs": 1,
		"applyKernValueThreshold": 0,
		"minimumKerning": 100,
		"openTab": 1,
		"lockKerning": 1,
		"overrideContext": 0,
		"contextGlyphs": "HOOH,noon",
		"mirrorPair": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 340
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Sample Strings with Master Kerning",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Builds kern strings with current kerning in Sample Texts.", sizeStyle='small', selectable=True)

		self.w.positivePairs = vanilla.CheckBox("auto", "Positive", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.negativePairs = vanilla.CheckBox("auto", "Negative", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.zeroPairs = vanilla.CheckBox("auto", "Zero pairs", value=False, callback=self.SavePreferences, sizeStyle="small")

		self.w.groupToGroupOnly = vanilla.CheckBox("auto", "Group-to-group kerning only", value=False, callback=self.SavePreferences, sizeStyle="small")

		self.w.applyKernValueThreshold = vanilla.CheckBox("auto", "Only kernings of at least:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.minimumKerning = SteppingEditText("auto", "100", callback=self.SavePreferences, sizeStyle="small", formatter=integerFormatter(0))
		tooltipText = "Only kern pairs whose value is at least this many units away from zero (positive or negative) are used."
		self.w.applyKernValueThreshold.setToolTip(tooltipText)
		self.w.minimumKerning.setToolTip(tooltipText)

		tooltipText = "If checked, the surrounding glyphs will be replaced with those given in the text box. Use a comma to differentiate the left-side context from the right-side context: ‘HOOH,noon’ will put HOOH on the left side, ‘noon’ on the right side."
		self.w.overrideContext = vanilla.CheckBox("auto", "Override context glyphs:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.contextGlyphs = vanilla.EditText("auto", "HOOH,noon", callback=self.SavePreferences, sizeStyle='small')
		self.w.overrideContext.setToolTip(tooltipText)
		self.w.contextGlyphs.setToolTip(tooltipText)

		self.w.mirrorPair = vanilla.CheckBox("auto", "Mirror kerning pair (AV→AVA)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.mirrorPair.setToolTip("If checked, will create a mirrored version of the kerning string. E.g., instead of just AV, it will show AVA between the context glyphs.")

		self.w.openTab = vanilla.CheckBox("auto", "Open tab at first kern string", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.openTab.setToolTip("If checked, a new tab will be opened with the first found kern string, and the cursor positioned accordingly, ready for group kerning and switching to the next sample string.")
		self.w.lockKerning = vanilla.CheckBox("auto", "in kerning mode", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.lockKerning.setToolTip("Will set the kerning lock in the tab, prevents you from spacing accidentally.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Add", callback=self.SampleStringsWithCurrentKerning)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[positivePairs]-gap-[negativePairs]-gap-[zeroPairs]-(>=inset)-|",
				"H:|-inset-[groupToGroupOnly]-(>=inset)-|",
				"H:|-inset-[applyKernValueThreshold]-gap-[minimumKerning(60)]-(>=inset)-|",
				"H:|-inset-[overrideContext]-gap-[contextGlyphs]-inset-|",
				"H:|-inset-[mirrorPair]-(>=inset)-|",
				"H:|-inset-[openTab]-gap-[lockKerning]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[positivePairs]-checkRow-[groupToGroupOnly]-checkRow-[minimumKerning]-row-[contextGlyphs]-checkRow-[mirrorPair]-checkRow-[openTab]-inset-[runButton]-inset-|",
				{"view1": self.w.negativePairs, "attribute1": "centerY", "view2": self.w.positivePairs, "attribute2": "centerY"},
				{"view1": self.w.zeroPairs, "attribute1": "centerY", "view2": self.w.positivePairs, "attribute2": "centerY"},
				{"view1": self.w.applyKernValueThreshold, "attribute1": "centerY", "view2": self.w.minimumKerning, "attribute2": "centerY"},
				{"view1": self.w.overrideContext, "attribute1": "centerY", "view2": self.w.contextGlyphs, "attribute2": "centerY"},
				{"view1": self.w.lockKerning, "attribute1": "centerY", "view2": self.w.openTab, "attribute2": "centerY"},
				# same width, so both fields start at the same x-position:
				{"view1": self.w.overrideContext, "attribute1": "width", "view2": self.w.applyKernValueThreshold, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.runButton.enable(self.w.positivePairs.get() or self.w.negativePairs.get() or self.w.zeroPairs.get())

	def parseTheContextGlyphs(self):
		separator = ","
		txt = self.pref("contextGlyphs")
		if separator in txt:
			linePrefix, linePostfix = txt.split(separator)[:2]
		else:
			linePrefix, linePostfix = txt, txt
		return linePrefix, linePostfix

	def namesForGroupName(self, groupName, font, isLeft=True):
		names = []
		for g in font.glyphs:
			if isLeft:  # left side = right group
				if g.rightKerningGroup in (groupName, groupName[7:]):
					names.append(g.name)
			else:
				if g.leftKerningGroup in (groupName, groupName[7:]):
					names.append(g.name)
		return names

	def glyphNameForKerningName(self, name, font, isLeft=True):
		glyphName = None
		if name[0] == "@":
			names = self.namesForGroupName(name, font, isLeft=isLeft)
			if name.startswith("@MMK_"):
				glyphName = name.split("_")[2]
				if glyphName == "KO":  # KernOn convention
					glyphName = name.split("_")[3]
				if not font.glyphs[glyphName] or glyphName not in names:
					glyphName = None
			if not glyphName:
				for name in names:
					if font.glyphs[name]:
						glyphName = name
						break
		else:
			glyph = font.glyphForId_(name)
			if glyph:
				glyphName = glyph.name

		if glyphName:
			return glyphName
		else:
			print("⚠️ No glyph found for: {name}")
			return None

	def contextForGlyphs(self, leftName, rightName, font):
		linePrefix = "nonn"
		linePostfix = "noon"

		L = font.glyphs[leftName]
		R = font.glyphs[rightName]

		numberTriggers = ("Math", "Currency", "Decimal Digit")
		if L and L.subCategory in numberTriggers:
			linePrefix = "1200"
		if R and R.subCategory in numberTriggers:
			linePostfix = "0034567"
		if L and L.case == GSUppercase:
			linePrefix = "HOOH"
		elif L and L.case == GSSmallcaps:
			linePrefix = "/h.sc/o.sc/h.sc/h.sc"
		if R and R.case == GSSmallcaps:
			linePostfix = "/h.sc/o.sc/o.sc/h.sc"

		return linePrefix, linePostfix

	def SampleStringsWithCurrentKerning(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			thisMaster = thisFont.selectedFontMaster
			print(f"Sample Strings with Master Kerning Report for {thisFont.familyName}")
			if thisFont.filepath:
				print(thisFont.filepath)
			print(f"Ⓜ️ Master: ‘{thisMaster.name}’")
			print()

			leftContext, rightContext = "nonn", "noon"
			if self.pref("contextGlyphs"):
				leftContext, rightContext = self.parseTheContextGlyphs()

			cursorPos = len(leftContext) + 1
			minimumKerning = self.prefInt("minimumKerning")

			kernStrings = []
			for leftSide in thisFont.kerning[thisMaster.id].keys():
				leftGlyph = self.glyphNameForKerningName(leftSide, thisFont, isLeft=True)
				if not leftGlyph:
					continue
				for rightSide in thisFont.kerning[thisMaster.id][leftSide].keys():
					value = thisFont.kerning[thisMaster.id][leftSide][rightSide]
					if self.pref("applyKernValueThreshold") and minimumKerning > abs(value):
						continue
					if (self.pref("positivePairs") and value > 0) or (self.pref("negativePairs") and value < 0) or (self.pref("zeroPairs") and value == 0):
						rightGlyph = self.glyphNameForKerningName(rightSide, thisFont, isLeft=False)
						if not rightGlyph:
							continue
						if not self.pref("overrideContext"):
							leftContext, rightContext = self.contextForGlyphs(leftGlyph, rightGlyph, thisFont)
						line = f"{leftContext}/{leftGlyph}/{rightGlyph}"
						if self.pref("mirrorPair"):
							line += f"/{leftGlyph}"
						line += f" {rightContext}"
						kernStrings.append(line)

			if not kernStrings:
				Message(title="No Kern Strings Created", message="No kerning in the font that meets your selection.", OKButton=None)
				print("No kern strings built. Done.")
			else:
				marker = "Master Kerning"
				sampleText.executeAndReport(kernStrings, marker=marker)

				if self.pref("openTab"):
					newTab = thisFont.newTab()
					if Glyphs.versionNumber >= 3:
						sampleText.setSelectSampleTextIndex(thisFont, tab=newTab, marker=marker)
					else:
						sampleText.setSelectSampleTextIndex(thisFont, tab=newTab)
					if len(newTab.text) >= cursorPos:
						newTab.textCursor = cursorPos

					# set it to lock kerning:
					if self.pref("lockKerning"):
						newTab.graphicView().setDoSpacing_(0)
						newTab.graphicView().setDoKerning_(1)
						newTab.updateKerningButton()

				self.w.close()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Sample Strings with Master Kerning Error: %s" % e)
			import traceback
			print(traceback.format_exc())


Glyphs.clearLog()
SampleStringsWithMasterKerning()
