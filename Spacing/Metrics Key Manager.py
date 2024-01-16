# MenuTitle: Metrics Key Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Batch apply metrics keys to the current font.
"""

import vanilla
from AppKit import NSFont, NSAlert, NSAlertStyleWarning, NSAlertFirstButtonReturn
from GlyphsApp import Glyphs, Message

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


class MetricsKeyManager(object):
	prefID = "com.mekkablue.MetricsKeyManager"
	prefDict = {
		"LeftMetricsKeys": LeftKeys,
		"RightMetricsKeys": RightKeys,
		"WidthMetricsKeys": WidthKeys,
		"symmetricThreshold": "2",
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 550
		windowHeight = 300
		windowWidthResize = 1000  # user can resize width by this value
		windowHeightResize = 1000  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Metrics Key Manager",  # window title
			minSize=(windowWidth, windowHeight - 100),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight, boxHeight = self.getMeasurements()

		self.w.LeftMetricsKeysText = vanilla.TextBox((inset, linePos + 2, 70, 14), "Left Keys:", sizeStyle='small', selectable=True)
		self.w.LeftMetricsKeys = vanilla.TextEditor((inset + 70, linePos, -inset, boxHeight), "", callback=self.SavePreferences)  # , sizeStyle='small' )

		linePos += boxHeight + 10
		self.w.RightMetricsKeysText = vanilla.TextBox((inset, linePos + 2, 70, 14), "Right Keys:", sizeStyle='small', selectable=True)
		self.w.RightMetricsKeys = vanilla.TextEditor((inset + 70, linePos, -inset, boxHeight), "", callback=self.SavePreferences)  # , sizeStyle='small' )

		linePos += boxHeight + 10
		self.w.WidthMetricsKeysText = vanilla.TextBox((inset, linePos + 2, 70, 14), "Width Keys:", sizeStyle='small', selectable=True)
		self.w.WidthMetricsKeys = vanilla.TextEditor((inset + 70, linePos, -inset, boxHeight), "", callback=self.SavePreferences)  # , sizeStyle='small' )

		size = NSFont.smallSystemFontSize()
		editFont = NSFont.userFixedPitchFontOfSize_(size)
		for legibleFont in ("legibleFontOfSize_", "legibileFontOfSize_"):
			if hasattr(NSFont, legibleFont):
				editFont = getattr(NSFont, legibleFont)(size)
				break

		for editField in (self.w.LeftMetricsKeys, self.w.RightMetricsKeys, self.w.WidthMetricsKeys):
			editField.getNSTextView().setToolTip_("Enter a metrics key like '=H', followed by a colon (:), followed by glyph names, spearated by space, comma, or any other separator that cannot be part of a glyph name. (Glyph names can contain A-Z, a-z, 0-9, period, underscore and hyphen.)\nExample: ‘=H: B D E F’.")
			editField.getNSTextView().setFont_(editFont)
			editField.getNSScrollView().setHasVerticalScroller_(1)
			editField.getNSScrollView().setRulersVisible_(1)

		# Buttons:
		self.w.symmetricButton = vanilla.Button((inset, -20 - inset, 60, -inset), "Add =|", sizeStyle='regular', callback=self.AddMissingSymmetricKeys)
		self.w.symmetricThreshold = vanilla.EditText((inset + 65, -19 - inset, 20, -inset), "2", callback=self.SavePreferences, sizeStyle="small")
		self.w.symmetricThresholdText = vanilla.TextBox((inset + 65 + 20, -16 - inset, 60, -inset), "Threshold", sizeStyle="small", selectable=True)
		linePos += lineHeight
		tooltip = "Adds glyphs with symmetrical SBs to =| in the right metrics keys. Add a threshold in units for catching SBs off by a unit or two."
		self.w.symmetricButton.getNSButton().setToolTip_(tooltip)
		self.w.symmetricThreshold.getNSTextField().setToolTip_(tooltip)
		self.w.symmetricThresholdText.getNSTextField().setToolTip_(tooltip)

		self.w.deleteAllButton = vanilla.Button((inset + 150, -20 - inset, 80, -inset), "Delete All", sizeStyle='regular', callback=self.deleteAllMetricsKeys)

		self.w.resetButton = vanilla.Button((-240 - inset, -20 - inset, -inset - 170, -inset), "⟲ Reset", sizeStyle='regular', callback=self.SetDefaults)
		self.w.resetButton.getNSButton().setToolTip_("Resets the contents of the L+R Keys to their (currently only Latin) defaults.")

		self.w.scanButton = vanilla.Button((-160 - inset, -20 - inset, -inset - 80, -inset), "↑ Extract", sizeStyle='regular', callback=self.ScanFontForKeys)
		self.w.scanButton.getNSButton().setToolTip_("Scans the current font for all metrics keys and lists them here. Normalizes the preceding equals sign (=). No matter whether you typed them with or without an equals sign, they will show up here with one.")

		self.w.runButton = vanilla.Button((-70 - inset, -20 - inset, -inset, -inset), "↓ Apply", sizeStyle='regular', callback=self.MetricsKeyManagerMain)
		self.w.runButton.getNSButton().setToolTip_("Parses the current content of the window and will attempt to set the metrics keys of the respective glyphs in the frontmost font.")
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Metrics Key Manager' could not load preferences. Will resort to defaults")

		# Bind resizing method:
		self.w.bind("resize", self.windowResize)

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def getMeasurements(self, sender=None):
		lineHeight = 22
		currentWindowHeight = self.w.getPosSize()[3]
		boxHeight = currentWindowHeight // 3 - int(lineHeight * 1.1)
		return 12, 15, lineHeight, boxHeight

	def windowResize(self, sender=None):
		linePos, inset, lineHeight, boxHeight = self.getMeasurements()
		self.w.LeftMetricsKeysText.setPosSize((inset, linePos + 2, 70, 14))
		self.w.LeftMetricsKeys.setPosSize((inset + 70, linePos, -inset, boxHeight))
		linePos += boxHeight + 10
		self.w.RightMetricsKeysText.setPosSize((inset, linePos + 2, 70, 14))
		self.w.RightMetricsKeys.setPosSize((inset + 70, linePos, -inset, boxHeight))
		linePos += boxHeight + 10
		self.w.WidthMetricsKeysText.setPosSize((inset, linePos + 2, 70, 14))
		self.w.WidthMetricsKeys.setPosSize((inset + 70, linePos, -inset, boxHeight))

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()

	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				getattr(self.w, prefName).set(self.pref(prefName).strip())
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def SetDefaults(self, sender=None):
		self.w.RightMetricsKeys.set(RightKeys.strip())
		self.w.LeftMetricsKeys.set(LeftKeys.strip())
		self.w.WidthMetricsKeys.set(WidthKeys.strip())

		# update settings to the latest user input:
		if not self.SavePreferences(self):
			print("⚠️ Metrics Key Manager could not write preferences.")

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
		threshold = int(self.pref("symmetricThreshold"))
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

			# update settings to the latest user input:
			if not self.SavePreferences(self):
				print("Note: 'Metrics Key Manager' could not write preferences.")

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
									print("	⚠️ Glyph '%s' not in font. Skipped." % glyphName)
							if reportGlyphs:
								print("	✅ %s" % ", ".join(reportGlyphs))
							else:
								print("	🤷🏻‍♀️ No glyphs changed.")

				if affectedGlyphs and shouldOpenTabWithAffectedGlyphs:
					affectedGlyphs = set(affectedGlyphs)
					thisFont.newTab("/" + "/".join(affectedGlyphs))

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Metrics Key Manager Error: %s" % e)
			import traceback
			print(traceback.format_exc())


MetricsKeyManager()
