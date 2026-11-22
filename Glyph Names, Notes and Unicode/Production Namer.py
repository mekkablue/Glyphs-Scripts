# MenuTitle: Production Namer
__doc__ = """
Override default production names. Default are the usual subjects which create problems in legacy PDF workflows: mu, onesuperior, twosuperior, threesuperior.
"""

import vanilla
from mekkablue import mekkaObject, getLegibleFont, makeWindowResizable
from GlyphsApp import Glyphs, Message
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut


defaultString = """
Legacy PDF workflow fix:

onesuperior -> onesuperior
twosuperior -> twosuperior
threesuperior -> threesuperior
micro -> mu

# Syntax: glyphname -> productionname
Whitespace does not matter
Only lines containing a dash (-) followed by a greater sign (>) count
Freely write comments and empty lines
Anything after a hashtag (#) is ignored
"""


class ProductionNamer(mekkaObject):
	prefDict = {
		"recipe": defaultString.strip(),
		"applyPopup": 0,
		"applyContaining": "",
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 400
		windowHeight = 260
		# the window stays resizable, because the user needs to enlarge the text editor
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Production Namer",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Will reset the production names of these glyphs:", sizeStyle='small', selectable=True)

		self.w.recipe = vanilla.TextEditor("auto", text=defaultString.strip(), callback=self.SavePreferences, checksSpelling=False)
		self.w.recipe.setToolTip("- Syntax: glyphname -> productionname\n- Whitespace does not matter\n- Only lines containing a dash (-) followed by a greater sign (>) count\n- Freely write comments and empty lines\n- Anything after a hashtag (#) is ignored")
		self.w.recipe.getNSScrollView().setHasVerticalScroller_(1)
		self.w.recipe.getNSScrollView().setHasHorizontalScroller_(1)
		self.w.recipe.getNSScrollView().setRulersVisible_(0)

		legibleFont = getLegibleFont()

		textView = self.w.recipe.getNSTextView()
		textView.setFont_(legibleFont)
		textView.setHorizontallyResizable_(1)
		textView.setVerticallyResizable_(1)
		textView.setAutomaticDataDetectionEnabled_(1)
		textView.setAutomaticLinkDetectionEnabled_(1)
		textView.setDisplaysLinkToolTips_(1)
		textSize = textView.minSize()
		textSize.width = 1000
		textView.setMinSize_(textSize)

		# APPLY TO FONTS
		self.w.finger = vanilla.TextBox("auto", "👉", selectable=True)
		self.w.applyText = vanilla.TextBox("auto", "Apply to", sizeStyle='small', selectable=True)
		self.w.applyPopup = vanilla.PopUpButton("auto", ("ALL open fonts", "open fonts containing", "frontmost font only"), sizeStyle='small', callback=self.SavePreferences)
		tooltipText = "Choose whether to apply the production names to all open fonts, to open fonts whose family name contains a given text, or to the frontmost font only."
		self.w.applyText.setToolTip(tooltipText)
		self.w.applyPopup.setToolTip(tooltipText)
		self.w.applyContaining = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle='small', placeholder="enter part of family name here")
		self.w.applyContaining.setToolTip("Only applies the settings to fonts that contain this in Font Info > Font > Family Name.")

		self.w.resetButton = vanilla.Button("auto", "Reset", callback=self.updateUI)
		self.w.resetButton.setToolTip("Resets the text above to the default production names.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Set Names", callback=self.ProductionNamerMain)
		self.w.runButton.setToolTip("Sets the production names listed above in the chosen fonts.")
		self.w.setDefaultButton(self.w.runButton)

		# everything hugs vertically, except for the text editor, which takes the leftover height:
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)
		self.w.recipe.getNSScrollView().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationVertical)
		for label in (self.w.finger, self.w.applyText):
			label.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.applyPopup.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-0-[recipe]-0-|",
				"H:|-inset-[finger]-4-[applyText]-gap-[applyPopup]-gap-[applyContaining(>=100)]-inset-|",
				"H:|-inset-[resetButton(>=70)]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-gap-[recipe(>=100)]-gap-[applyPopup]-inset-[runButton]-inset-|",
				"V:[resetButton]-inset-|",
				{"view1": self.w.finger, "attribute1": "centerY", "view2": self.w.applyPopup, "attribute2": "centerY"},
				{"view1": self.w.applyText, "attribute1": "centerY", "view2": self.w.applyPopup, "attribute2": "centerY"},
				{"view1": self.w.applyContaining, "attribute1": "centerY", "view2": self.w.applyPopup, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8},
		)

		makeWindowResizable(self.w, vertical=True)  # resizable, limits in content sizes

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		# show or hide text field
		self.w.applyContaining.show(self.w.applyPopup.get() == 1)  # 0=all fonts, 1=fonts containing..., 2=frontmost font only

		# enable or disable run button
		applySettingsEnable = self.w.applyPopup.get() != 1 or len(self.w.applyContaining.get().strip()) > 0
		self.w.runButton.enable(applySettingsEnable)

		# reset recipe
		if sender is self.w.resetButton:
			self.w.recipe.set(defaultString.strip())

	def ProductionNamerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires at least one font. Open a font and run the script again.", OKButton=None)
			else:
				nameChangeString = self.pref("recipe")
				applyPopup = self.pref("applyPopup")

				if applyPopup == 0:
					# ALL OPEN FONTS
					theseFonts = Glyphs.fonts
				elif applyPopup == 1:
					# ALL FONTS CONTAINING
					theseFonts = [f for f in Glyphs.fonts if self.pref("applyContaining") in f.familyName]
				elif applyPopup == 2:
					# FRONTMOST FONT ONLY
					theseFonts = (thisFont, )

				print("Production Namer Report")
				print()

				# parse lines of nameChangeString:
				renameDict = {}
				for line in nameChangeString.splitlines():
					try:
						# cut off comments
						if "#" in line:
							line = line[:line.find("#")]

						if line.strip():  # skip empty lines

							# PRODUCTION LINE:
							if "->" in line:
								nameList = line.split("->")
								glyphName = nameList[0].strip()
								productionName = nameList[1].strip()
								if glyphName and productionName:
									renameDict[glyphName] = productionName
					except:
						pass

				count = 0
				for i, glyphName in enumerate(renameDict):
					productionName = renameDict[glyphName]
					print("🔠 %02i. %s -> %s" % (i + 1, glyphName, productionName))
					for thisFont in theseFonts:
						if thisFont.filepath:
							fileName = thisFont.filepath.lastPathComponent()
						else:
							fileName = "%s (unsaved)" % thisFont.familyName
						thisGlyph = thisFont.glyphs[glyphName]
						if not thisGlyph:
							print("  🚫 missing in %s" % fileName)
						else:
							count += 1
							thisGlyph.productionName = productionName
							thisGlyph.setStoreProduction_(1)
							print("  ✅ %s" % fileName)

				self.w.close()  # delete if you want window to stay open

				# Final report:
				Glyphs.showNotification(
					"Production Namer: Done",
					"Set production names for %i glyph%s in %i font%s.\nDetails in Macro Window." % (
						count,
						"" if count == 1 else "s",
						len(theseFonts),
						"" if len(theseFonts) == 1 else "s",
					),
				)

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Production Namer Error: %s" % e)
			import traceback
			print(traceback.format_exc())


ProductionNamer()
