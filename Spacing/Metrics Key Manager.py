# MenuTitle: Metrics Key Manager
__doc__ = """
Batch apply metrics keys to the current font.
"""

import objc
import vanilla
from mekkablue import mekkaObject, getLegibleFont
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSAlert,
	NSAlertStyleWarning,
	NSAlertFirstButtonReturn,
	NSEvent,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)
from Foundation import NSNumberFormatter

LeftKeys = """
=H: B D E F I K L N P R Thorn Germandbls M
=O: C G Q
=o: c d e q eth
=h: b k l thorn
=n: idotless m p r
=|n: u
"""

RightKeys = """
=|: A H I M N O T U V W X Y
=O: D
=U: J
=o: b p thorn
=n: h m
=|n: idotless u
"""

WidthKeys = """
=0: zerowidthspace
=1000: emquad emspace
=140: thinspace
=166: sixperemspace
=222: mediumspace-math
=250: fourperemspace
=333: threeperemspace
=500: enquad enspace
=70: hairspace
=space: nbspace
=space*0.2: narrownbspace
=zero.tf: figurespace
=period: punctuationspace
=plus: plus minus multiply divide equal notequal greater less greaterequal lessequal plusminus approxequal logicalnot asciitilde asciicircum
"""


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


class Alert(object):

	def __init__(self, messageText="Are you sure?", informativeText="This cannot be undone.", buttons=["OK", "Cancel"]):
		super(Alert, self).__init__()
		self.messageText = messageText
		self.informativeText = informativeText
		self.buttons = buttons

	def displayAlert(self):
		alert = NSAlert.alloc().init()
		alert.setMessageText_(self.messageText)
		alert.setInformativeText_(self.informativeText)
		alert.setAlertStyle_(NSAlertStyleWarning)
		for button in self.buttons:
			alert.addButtonWithTitle_(button)
		# NSApp.activateIgnoringOtherApps_(True)
		self.buttonPressed = alert.runModal()


class MetricsKeyManager(mekkaObject):
	prefDict = {
		"LeftMetricsKeys": LeftKeys,
		"RightMetricsKeys": RightKeys,
		"WidthMetricsKeys": WidthKeys,
		"symmetricThreshold": "2",
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 620
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Metrics Key Manager",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.LeftMetricsKeysText = vanilla.TextBox("auto", "Left Keys:", sizeStyle='small', selectable=True)
		self.w.LeftMetricsKeys = vanilla.TextEditor("auto", "", callback=self.SavePreferences)
		self.w.RightMetricsKeysText = vanilla.TextBox("auto", "Right Keys:", sizeStyle='small', selectable=True)
		self.w.RightMetricsKeys = vanilla.TextEditor("auto", "", callback=self.SavePreferences)
		self.w.WidthMetricsKeysText = vanilla.TextBox("auto", "Width Keys:", sizeStyle='small', selectable=True)
		self.w.WidthMetricsKeys = vanilla.TextEditor("auto", "", callback=self.SavePreferences)

		editFont = getLegibleFont()
		tooltipText = "Enter a metrics key like '=H', followed by a colon (:), followed by glyph names, separated by space, comma, or any other separator that cannot be part of a glyph name. (Glyph names can contain A-Z, a-z, 0-9, period, underscore and hyphen.)\nExample: ‘=H: B D E F’."
		for editField in (self.w.LeftMetricsKeys, self.w.RightMetricsKeys, self.w.WidthMetricsKeys):
			editField.setToolTip(tooltipText)
			editField.getNSTextView().setFont_(editFont)
			editField.getNSScrollView().setHasVerticalScroller_(1)
			editField.getNSScrollView().setRulersVisible_(1)
		for labelName in ("LeftMetricsKeysText", "RightMetricsKeysText", "WidthMetricsKeysText"):
			getattr(self.w, labelName).setToolTip(tooltipText)

		# Buttons:
		tooltipText = "Adds glyphs with symmetrical SBs to =| in the right metrics keys. Add a threshold in units for catching SBs off by a unit or two."
		self.w.symmetricButton = vanilla.Button("auto", "Add =|", callback=self.AddMissingSymmetricKeys)
		self.w.symmetricThreshold = SteppingEditText("auto", "2", callback=self.SavePreferences, sizeStyle="small", formatter=integerFormatter(0))
		self.w.symmetricThresholdText = vanilla.TextBox("auto", "Threshold", sizeStyle="small", selectable=True)
		self.w.symmetricButton.setToolTip(tooltipText)
		self.w.symmetricThreshold.setToolTip(tooltipText)
		self.w.symmetricThresholdText.setToolTip(tooltipText)

		self.w.deleteAllButton = vanilla.Button("auto", "Delete All", callback=self.deleteAllMetricsKeys)
		self.w.deleteAllButton.setToolTip("Deletes all metrics keys (left, right and width) in all glyphs and layers of the frontmost font. Cannot be undone.")

		self.w.resetButton = vanilla.Button("auto", "⟲ Reset", callback=self.SetDefaults)
		self.w.resetButton.setToolTip("Resets the contents of the L+R Keys to their (currently only Latin) defaults.")

		self.w.scanButton = vanilla.Button("auto", "↑ Extract", callback=self.ScanFontForKeys)
		self.w.scanButton.setToolTip("Scans the current font for all metrics keys and lists them here. Normalizes the preceding equals sign (=). No matter whether you typed them with or without an equals sign, they will show up here with one.")

		self.w.runButton = vanilla.Button("auto", "↓ Apply", callback=self.MetricsKeyManagerMain)
		self.w.runButton.setToolTip("Parses the current content of the window and will attempt to set the metrics keys of the respective glyphs in the frontmost font. Hold down your OPTION key to also update glyph metrics right away. Careful, that is hard to undo.")
		self.w.setDefaultButton(self.w.runButton)

		# labels: right-aligned, same width
		labelNames = ("LeftMetricsKeysText", "RightMetricsKeysText", "WidthMetricsKeysText")
		widestLabel = "WidthMetricsKeysText"  # the label with the longest text
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		# keep every control at its natural height, so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[LeftMetricsKeysText]-gap-[LeftMetricsKeys]-inset-|",
				"H:|-inset-[RightMetricsKeysText]-gap-[RightMetricsKeys]-inset-|",
				"H:|-inset-[WidthMetricsKeysText]-gap-[WidthMetricsKeys]-inset-|",
				"H:|-inset-[symmetricButton(>=70)]-gap-[symmetricThreshold(40)]-gap-[symmetricThresholdText]-gap-[deleteAllButton(>=70)]-(>=gap)-[resetButton(>=70)]-gap-[scanButton(>=70)]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[LeftMetricsKeys(boxHeight)]-boxGap-[RightMetricsKeys(boxHeight)]-boxGap-[WidthMetricsKeys(boxHeight)]-inset-[runButton]-inset-|",
				# labels sit at the top of their editors:
				{"view1": self.w.LeftMetricsKeysText, "attribute1": "top", "view2": self.w.LeftMetricsKeys, "attribute2": "top"},
				{"view1": self.w.RightMetricsKeysText, "attribute1": "top", "view2": self.w.RightMetricsKeys, "attribute2": "top"},
				{"view1": self.w.WidthMetricsKeysText, "attribute1": "top", "view2": self.w.WidthMetricsKeys, "attribute2": "top"},
				# all controls of the button row share the vertical center of the run button:
				{"view1": self.w.symmetricButton, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.symmetricThreshold, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.symmetricThresholdText, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.deleteAllButton, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.resetButton, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.scanButton, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": inset, "gap": 8, "boxGap": 10, "boxHeight": 80},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def SetDefaults(self, sender=None):
		self.w.RightMetricsKeys.set(RightKeys.strip())
		self.w.LeftMetricsKeys.set(LeftKeys.strip())
		self.w.WidthMetricsKeys.set(WidthKeys.strip())

		# update settings to the latest user input:
		self.SavePreferences()

	def parseGlyphNames(self, glyphNameText):
		possibleChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-_"
		glyphNames = []
		currName = ""
		for currChar in glyphNameText.strip() + " ":
			if currChar in possibleChars:
				currName += currChar
			else:
				if currName:
					glyphNames.append(currName)
					currName = ""
		return glyphNames

	def font2dicts(self, font):
		leftDict, rightDict, widthDict = {}, {}, {}
		for glyph in font.glyphs:
			leftKey = glyph.leftMetricsKey
			if leftKey:
				# normalize equals sign:
				if not leftKey[0] == "=":
					leftKey = "=%s" % leftKey

				# create list or append to list:
				if leftKey not in leftDict:
					leftDict[leftKey] = [
						glyph.name,
					]
				else:
					leftDict[leftKey].append(glyph.name)

			rightKey = glyph.rightMetricsKey
			if rightKey:
				# normalize equals sign:
				if not rightKey[0] == "=":
					rightKey = "=%s" % rightKey

				# create list or append to list:
				if rightKey not in rightDict:
					rightDict[rightKey] = [
						glyph.name,
					]
				else:
					rightDict[rightKey].append(glyph.name)

			widthKey = glyph.widthMetricsKey
			if widthKey:
				# normalize equals sign:
				if not widthKey[0] == "=":
					widthKey = "=%s" % widthKey

				# create list or append to list:
				if widthKey not in widthDict:
					widthDict[widthKey] = [
						glyph.name,
					]
				else:
					widthDict[widthKey].append(glyph.name)

		return leftDict, rightDict, widthDict

	def ScanFontForKeys(self, sender=None, font=None):
		if not font:
			font = Glyphs.font

		if font:
			leftDict, rightDict, widthDict = self.font2dicts(font)
			leftText = self.dict2text(leftDict)
			rightText = self.dict2text(rightDict)
			widthText = self.dict2text(widthDict)
			self.w.LeftMetricsKeys.set(leftText)
			self.w.RightMetricsKeys.set(rightText)
			self.w.WidthMetricsKeys.set(widthText)
			self.SavePreferences()

	def dict2text(self, keyDict):
		keyText = ""
		for key in sorted(keyDict.keys()):
			if key:
				glyphNames = " ".join(keyDict[key])
				keyText += "%s: %s\n" % (key, glyphNames)
		return keyText.strip()

	def text2dict(self, keyText):
		parseDict = {}
		keyText = keyText.strip()
		for line in keyText.splitlines():
			line = line.strip()
			if line and ":" in line:
				key, glyphNameText = line.split(":")[:2]
				parseDict[key] = self.parseGlyphNames(glyphNameText)
		return parseDict

	def deleteAllMetricsKeys(self, sender=None, font=None):
		# brings macro window to front and clears its log:
		Glyphs.clearLog()

		question = "Are you sure you want to delete all metrics keys in the font?"
		info = "This cannot be undone."

		def AskUser(message=question, informativeText=info, buttons=("Delete", "Cancel")):
			ap = Alert(message, informativeText, buttons)
			ap.displayAlert()
			return ap.buttonPressed == NSAlertFirstButtonReturn

		if not AskUser():
			return

		if not font:
			font = Glyphs.font

		print("Deleting Metrics Keys...")
		for g in font.glyphs:
			g.leftMetricsKey = None
			g.rightMetricsKey = None
			g.widthMetricsKey = None
			for layer in g.layers:
				layer.leftMetricsKey = None
				layer.rightMetricsKey = None
				layer.widthMetricsKey = None
			print(f"🔤 Deleted metrics keys in: {g.name}")
		print("✅ Done.")

	def symmetricGlyphsMissingMetricsKeys(self, sender=None, font=None):
		threshold = self.prefInt("symmetricThreshold")
		if not font:
			font = Glyphs.font

		glyphNames = []
		for g in font.glyphs:
			layerChecks = [
				not layer.widthMetricsKey and not layer.rightMetricsKey and layer.shapes and abs(layer.LSB - layer.RSB) <= abs(threshold) and not layer.isAligned for layer in g.layers
				if layer.isMasterLayer or layer.isSpecialLayer
			]
			if all(layerChecks):
				if not g.rightMetricsKey and not g.widthMetricsKey:
					glyphNames.append(g.name)

		return glyphNames

	def AddMissingSymmetricKeys(self, sender=None):
		self.SavePreferences()
		symmetricKey = "=|"
		metricsKeys = "RightMetricsKeys"
		RightKeysText = self.pref(metricsKeys)
		rightDict = self.text2dict(RightKeysText)
		missingGlyphs = self.symmetricGlyphsMissingMetricsKeys()
		print("🔠 Missing =|: %s" % ", ".join(missingGlyphs))
		if symmetricKey not in rightDict.keys():
			rightDict[symmetricKey] = []
		for glyphName in missingGlyphs:
			if glyphName not in rightDict[symmetricKey]:
				rightDict[symmetricKey].append(glyphName)
		Glyphs.defaults[self.domain(metricsKeys)] = self.dict2text(rightDict)
		self.LoadPreferences()

	def MetricsKeyManagerMain(self, sender):
		try:
			# clears macro window log:
			Glyphs.clearLog()

			keysPressed = NSEvent.modifierFlags()
			optionKey = 524288
			optionKeyPressed = keysPressed & optionKey == optionKey

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if not thisFont:
				Message(title="Metrics Key Manager Error", message="No font open. Metrics keys can only be applied to the frontmost font.", OKButton=None)
			else:
				print("Metrics Key Manager Report for %s" % thisFont.familyName)
				print(thisFont.filepath)

				# to be turned into selectable options:
				# delete all existing keys, respect existing keys, overwrite existing keys
				respectExistingKeys = False
				deleteExistingKeys = False
				includeNonexportingGlyphs = True
				shouldOpenTabWithAffectedGlyphs = False

				LeftKeysText = self.pref("LeftMetricsKeys")
				leftDict = self.text2dict(LeftKeysText)

				RightKeysText = self.pref("RightMetricsKeys")
				rightDict = self.text2dict(RightKeysText)

				WidthKeysText = self.pref("WidthMetricsKeys")
				widthDict = self.text2dict(WidthKeysText)

				dictDict = {
					"Left": leftDict,
					"Right": rightDict,
					"Width": widthDict,
				}
				emojis = {
					"Left": "⬅️",
					"Right": "➡️",
					"Width": "↔️",
				}

				affectedGlyphs = []

				for LorR in dictDict.keys():
					print()
					thisDict = dictDict[LorR]
					if LorR not in ("Left", "Right", "Width"):
						print("\n😬 Expected key ‘Left’, ‘Right’ or ‘Width’, but got ‘%s’ instead." % LorR)
						break
					else:
						for key in thisDict.keys():
							print("%s Setting %s key %s" % (emojis[LorR], LorR.lower(), key))
							glyphNames = thisDict[key]
							reportGlyphs = []
							for glyphName in glyphNames:
								glyph = thisFont.glyphs[glyphName]
								if glyph:
									if LorR == "Left":
										glyph.leftMetricsKey = key
									elif LorR == "Right":
										glyph.rightMetricsKey = key
									elif LorR == "Width":
										glyph.widthMetricsKey = key
									affectedGlyphs.append(glyphName)
									reportGlyphs.append(glyphName)
								else:
									print(f"	⚠️ Glyph ‘{glyphName}’ not in font. Skipped.")
							if reportGlyphs:
								print("	✅", ", ".join(reportGlyphs))
							else:
								print("	🤷🏻‍♀️ No glyphs changed.")

				if affectedGlyphs:
					affectedGlyphs = set(affectedGlyphs)

					if optionKeyPressed:
						for glyphName in affectedGlyphs:
							glyph = thisFont[glyphName]
							if not glyph:
								continue
							for layer in glyph.layers:
								if layer.isMasterLayer or layer.isSpecialLayer:
									layer.syncMetrics()

					if shouldOpenTabWithAffectedGlyphs:
						thisFont.newTab("/" + "/".join(affectedGlyphs))

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Metrics Key Manager Error: %s" % e)
			import traceback
			print(traceback.format_exc())


MetricsKeyManager()
