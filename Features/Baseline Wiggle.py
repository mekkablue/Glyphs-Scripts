# MenuTitle: Baseline Wiggle
__doc__ = """
Add OpenType feature with pseudorandom GPOS baseline shift for all glyphs in a class.
"""

import objc
import vanilla
from random import randint
from mekkablue import mekkaObject, UpdateButton, reportFontName
from GlyphsApp import Glyphs, GSFeature, GSClass, Message
from AppKit import (
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


allPossibleFeatures = [
	'aalt', 'abvf', 'abvm', 'abvs', 'afrc', 'akhn', 'blwf', 'blwm', 'blws', 'calt', 'case', 'ccmp', 'cfar', 'chws', 'cjct', 'clig', 'cpct', 'cpsp', 'cswh', 'curs', 'c2pc', 'c2sc',
	'dist', 'dlig', 'dnom', 'dtls', 'expt', 'falt', 'fin2', 'fin3', 'fina', 'flac', 'frac', 'fwid', 'half', 'haln', 'halt', 'hist', 'hkna', 'hlig', 'hngl', 'hojo', 'hwid', 'init',
	'isol', 'ital', 'jalt', 'jp78', 'jp83', 'jp90', 'jp04', 'kern', 'lfbd', 'liga', 'ljmo', 'lnum', 'locl', 'ltra', 'ltrm', 'mark', 'med2', 'medi', 'mgrk', 'mkmk', 'mset', 'nalt',
	'nlck', 'nukt', 'numr', 'onum', 'opbd', 'ordn', 'ornm', 'palt', 'pcap', 'pkna', 'pnum', 'pref', 'pres', 'pstf', 'psts', 'pwid', 'qwid', 'rand', 'rclt', 'rkrf', 'rlig', 'rphf',
	'rtbd', 'rtla', 'rtlm', 'ruby', 'rvrn', 'salt', 'sinf', 'size', 'smcp', 'smpl', 'ss01', 'ss02', 'ss03', 'ss04', 'ss05', 'ss06', 'ss07', 'ss08', 'ss09', 'ss10', 'ss11', 'ss12',
	'ss13', 'ss14', 'ss15', 'ss16', 'ss17', 'ss18', 'ss19', 'ss20', 'ssty', 'stch', 'subs', 'sups', 'swsh', 'titl', 'tjmo', 'tnam', 'tnum', 'trad', 'twid', 'unic', 'valt', 'vatu',
	'vchw', 'vert', 'vhal', 'vjmo', 'vkna', 'vkrn', 'vpal', 'vrt2', 'vrtr', 'zero'
]

for i in range(1, 100):
	cvName = f"cv{i:02}"
	allPossibleFeatures.append(cvName)


def updatedCode(oldCode, beginSig, endSig, newCode):
	"""Replaces text in oldCode with newCode, but only between beginSig and endSig."""
	beginOffset = oldCode.find(beginSig)
	endOffset = oldCode.find(endSig) + len(endSig)
	newCode = oldCode[:beginOffset] + beginSig + newCode + "\n" + endSig + oldCode[endOffset:]
	return newCode


def createOTFeature(featureName="calt", featureCode="# empty feature code", targetFont=Glyphs.font, codeSig="CUSTOM-CONTEXTUAL-ALTERNATES"):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	featureName: name of the feature (str),
	featureCode: the AFDKO feature code (str),
	targetFont: the GSFont object receiving the feature,
	codeSig: the code signature (str) used as delimiters.
	"""

	beginSig = "# BEGIN " + codeSig + "\n"
	endSig = "# END " + codeSig + "\n"

	if featureName in [f.name for f in targetFont.features]:
		# feature already exists:
		targetFeature = targetFont.features[featureName]

		if beginSig in targetFeature.code:
			# replace old code with new code:
			targetFeature.code = updatedCode(targetFeature.code, beginSig, endSig, featureCode)
		else:
			# append new code:
			targetFeature.code += "\n" + beginSig + featureCode + "\n" + endSig

		return f"Updated existing OT feature ‘{featureName}’."
	else:
		# create feature with new code:
		newFeature = GSFeature()
		newFeature.name = featureName
		newFeature.code = beginSig + featureCode + "\n" + endSig
		targetFont.features.append(newFeature)
		return f"Created new OT feature ‘{featureName}’"


def createOTClass(className="@default", classGlyphs=None, targetFont=Glyphs.font):
	"""
	Creates an OpenType class called className in targetFont
	containg classGlyphs, or updates it if it already exists.
	className: name of the OT class, with or without leading at sign,
	classGlyphs: list of glyph names,
	targetFont: the GSFont that receives the OT class.
	"""
	if classGlyphs is None:
		classGlyphs = [layer.parent.name for layer in Glyphs.font.selectedLayers]
	# strip '@' from beginning:
	if className[0] == "@":
		className = className[1:]

	classCode = " ".join(classGlyphs)

	if className in [c.name for c in targetFont.classes]:
		targetFont.classes[className].code = classCode
		return f"Updated existing OT class ‘{className}’."
	else:
		newClass = GSClass()
		newClass.name = className
		newClass.code = classCode
		targetFont.classes.append(newClass)
		return f"Created new OT class: ‘{className}’"


class BaselineWiggle(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"otClass": "All",
		"otFeature": "kern",
		"lineLength": 70,
		"wiggleMax": -50,
		"wiggleMin": 50,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 270
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Baseline Wiggle",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Create pseudorandom glyph wiggles:", sizeStyle="small", selectable=True)

		tooltipText = "Name of the OpenType class containing the glyphs that receive the wiggle. ‘All’ will be created from all exporting glyphs if it does not exist yet."
		self.w.otClassText = vanilla.TextBox("auto", "with class:", sizeStyle="small", selectable=True)
		self.w.otClass = vanilla.ComboBox("auto", ["All"] + sorted([c.name for c in Glyphs.font.classes if not c.name == "All"]), sizeStyle="small", callback=self.SavePreferences)
		self.w.otClassUpdate = UpdateButton("auto", callback=self.update)
		self.w.otClassText.setToolTip(tooltipText)
		self.w.otClass.setToolTip(tooltipText)
		self.w.otClassUpdate.setToolTip("Reload the classes of the frontmost font.")

		tooltipText = "Name of the OpenType feature that receives the wiggle code. Will be created if it does not exist yet."
		self.w.otFeatureText = vanilla.TextBox("auto", "in feature:", sizeStyle="small", selectable=True)
		self.w.otFeature = vanilla.ComboBox("auto", allPossibleFeatures, sizeStyle="small", callback=self.SavePreferences)
		self.w.otFeatureText.setToolTip(tooltipText)
		self.w.otFeature.setToolTip(tooltipText)

		# whole numbers, negative values allowed
		wiggleFormatter = NSNumberFormatter.alloc().init()
		wiggleFormatter.setAllowsFloats_(False)

		tooltipText = "Lowest vertical shift (in units) the random wiggle can have. Negative values shift down."
		self.w.wiggleMinText = vanilla.TextBox("auto", "lowest wiggle:", sizeStyle="small", selectable=True)
		self.w.wiggleMin = SteppingEditText("auto", "-50", callback=self.SavePreferences, sizeStyle="small", formatter=wiggleFormatter)
		self.w.wiggleMinText.setToolTip(tooltipText)
		self.w.wiggleMin.setToolTip(tooltipText)

		tooltipText = "Highest vertical shift (in units) the random wiggle can have."
		self.w.wiggleMaxText = vanilla.TextBox("auto", "highest wiggle:", sizeStyle="small", selectable=True)
		self.w.wiggleMax = SteppingEditText("auto", "50", callback=self.SavePreferences, sizeStyle="small", formatter=wiggleFormatter)
		self.w.wiggleMaxText.setToolTip(tooltipText)
		self.w.wiggleMax.setToolTip(tooltipText)

		lineLengthFormatter = NSNumberFormatter.alloc().init()
		lineLengthFormatter.setAllowsFloats_(False)
		lineLengthFormatter.setMinimum_(1)
		tooltipText = "Number of glyphs in a line, i.e., how many glyphs long the wiggle context rules reach."
		self.w.lineLengthText = vanilla.TextBox("auto", "for line length:", sizeStyle="small", selectable=True)
		self.w.lineLength = SteppingEditText("auto", "70", callback=self.SavePreferences, sizeStyle="small", formatter=lineLengthFormatter)
		self.w.lineLengthText.setToolTip(tooltipText)
		self.w.lineLength.setToolTip(tooltipText)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Wiggle", callback=self.BaselineWiggleMain)
		self.w.runButton.setToolTip("Create the class and feature code in the frontmost font.")
		self.w.setDefaultButton(self.w.runButton)

		# labels: right-aligned, same width
		labelNames = ("otClassText", "otFeatureText", "wiggleMinText", "wiggleMaxText", "lineLengthText")
		widestLabel = "lineLengthText"  # the label with the longest text
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
			{"view1": getattr(self.w, labelName), "attribute1": "centerY", "view2": getattr(self.w, labelName[:-4]), "attribute2": "centerY"}
			for labelName in labelNames
		]

		# hug vertically so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[otClassText]-gap-[otClass]-gap-[otClassUpdate(20)]-inset-|",
				"H:|-inset-[otFeatureText]-gap-[otFeature]-inset-|",
				"H:|-inset-[wiggleMinText]-gap-[wiggleMin(60)]-(>=inset)-|",
				"H:|-inset-[wiggleMaxText]-gap-[wiggleMax(60)]-(>=inset)-|",
				"H:|-inset-[lineLengthText]-gap-[lineLength(60)]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[otClass]-row-[otFeature]-row-[wiggleMin]-row-[wiggleMax]-row-[lineLength]-inset-[runButton]-inset-|",
				{"view1": self.w.otClassUpdate, "attribute1": "centerY", "view2": self.w.otClass, "attribute2": "centerY"},
			] + widthRules + centerRules,
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def update(self, sender=None):
		if sender == self.w.otClassUpdate:
			otClasses = ["All"] + sorted([c.name for c in Glyphs.font.classes if not c.name == "All"])
			self.w.otClass.setItems(otClasses)

	def BaselineWiggleMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			# read prefs:

			otClass = self.pref("otClass")
			otFeature = self.pref("otFeature")
			lineLength = self.prefInt("lineLength")
			wiggleMax = self.prefInt("wiggleMax")
			wiggleMin = self.prefInt("wiggleMin")
			wiggleMin, wiggleMax = sorted((wiggleMin, wiggleMax))  # reorder if necessary

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				report = reportFontName(thisFont)
				print(f"Baseline Wiggle Report for {report}")
				print()

				if otClass and otFeature:
					# remove leading at signs:
					while otClass[0] == "@":
						otClass = otClass[1:]

					featuretext = ""
					for j in range(lineLength, 0, -1):
						newline = f"pos @{otClass}' " + f"@{otClass} " * j + f"<0 {randint(wiggleMin, wiggleMax)} 0 0>;\n"
						featuretext += newline

					if otClass not in [c.name for c in thisFont.classes]:
						report = createOTClass(
							className=otClass,
							classGlyphs=[g.name for g in thisFont.glyphs if g.export],
						)
						print(report)

					report = createOTFeature(
						featureName=otFeature,
						featureCode=featuretext,
						codeSig="BASELINE-WIGGLE",
					)
					print(report)

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Baseline Wiggle Error: {e}")
			import traceback
			print(traceback.format_exc())


BaselineWiggle()
