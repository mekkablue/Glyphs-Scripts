# MenuTitle: Baseline Wiggle
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Add OpenType feature with pseudorandom GPOS baseline shift for all glyphs in a class.
"""

import vanilla
from random import randint
from GlyphsApp import Glyphs, GSFeature, GSClass, Message
from mekkablue import mekkaObject


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
		windowWidth = 240
		windowHeight = 210
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Baseline Wiggle",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight, tab = 12, 15, 22, 100

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Create pseudorandom glyph wiggles:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.otClassText = vanilla.TextBox((inset, linePos + 2, tab, 14), "with class:", sizeStyle='small', selectable=True)
		self.w.otClass = vanilla.ComboBox((inset + tab, linePos - 1, -inset - 24, 19), ["All"] + sorted([c.name for c in Glyphs.font.classes if not c.name == "All"]), sizeStyle='small', callback=self.SavePreferences)
		self.w.otClassUpdate = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.update)
		linePos += lineHeight

		self.w.otFeatureText = vanilla.TextBox((inset, linePos + 2, tab, 14), "in feature:", sizeStyle='small', selectable=True)
		self.w.otFeature = vanilla.ComboBox((inset + tab, linePos - 1, -inset, 19), allPossibleFeatures, sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.wiggleMinText = vanilla.TextBox((inset, linePos + 2, tab, 14), "lowest wiggle:", sizeStyle='small', selectable=True)
		self.w.wiggleMin = vanilla.EditText((inset + tab, linePos, -inset, 19), "-50", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.wiggleMaxText = vanilla.TextBox((inset, linePos + 2, tab, 14), "highest wiggle:", sizeStyle='small', selectable=True)
		self.w.wiggleMax = vanilla.EditText((inset + tab, linePos, -inset, 19), "50", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.lineLengthText = vanilla.TextBox((inset, linePos + 2, tab, 14), "for line length:", sizeStyle='small', selectable=True)
		self.w.lineLength = vanilla.EditText((inset + tab, linePos, -inset, 19), "70", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Wiggle", sizeStyle='regular', callback=self.BaselineWiggleMain)
		self.w.setDefaultButton(self.w.runButton)

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
				filePath = thisFont.filepath
				if filePath:
					report = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					report = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
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
