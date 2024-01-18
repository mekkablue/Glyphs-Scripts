# MenuTitle: Production Namer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Override default production names. Default are the usual subjects which create problems in legacy PDF workflows: mu, onesuperior, twosuperior, threesuperior.
"""

import vanilla
from AppKit import NSFont
from GlyphsApp import Glyphs, Message
from mekkaCore import mekkaObject


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
		"recipe": 0,
		"applyPopup": 0,
		"applyContaining": "",
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 260
		windowWidthResize = 1000  # user can resize width by this value
		windowHeightResize = 1000  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Production Namer",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Will reset the production names of these glyphs:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.recipe = vanilla.TextEditor((1, linePos, -1, -70), text=defaultString.strip(), callback=self.SavePreferences, checksSpelling=False)
		self.w.recipe.getNSTextView().setToolTip_("- Syntax: glyphname -> productionname\n- Whitespace does not matter\n- Only lines containing a dash (-) followed by a greater sign (>) count\n- Freely write comments and empty lines\n- Anything after a hashtag (#) is ignored")
		self.w.recipe.getNSScrollView().setHasVerticalScroller_(1)
		self.w.recipe.getNSScrollView().setHasHorizontalScroller_(1)
		self.w.recipe.getNSScrollView().setRulersVisible_(0)

		legibleFont = NSFont.legibileFontOfSize_(NSFont.systemFontSize())
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
		linePos = -inset - 50
		self.w.finger = vanilla.TextBox((inset - 5, linePos, 22, 22), "👉 ", sizeStyle='regular', selectable=True)
		self.w.applyText = vanilla.TextBox((inset + 17, linePos + 2, 70, 14), "Apply to", sizeStyle='small', selectable=True)
		self.w.applyPopup = vanilla.PopUpButton((inset + 70, linePos, 150, 17), ("ALL open fonts", "open fonts containing", "frontmost font only"), sizeStyle='small', callback=self.SavePreferences)
		self.w.applyContaining = vanilla.EditText((inset + 70 + 150 + 10, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small', placeholder="enter part of family name here")
		self.w.applyContaining.getNSTextField().setToolTip_("Only applies the settings to fonts that contain this in Font Info > Font > Family Name.")
		linePos += lineHeight

		self.w.resetButton = vanilla.Button((inset, -20 - inset, 80, -inset), "Reset", sizeStyle='regular', callback=self.updateUI)

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Set Names", sizeStyle='regular', callback=self.ProductionNamerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		# show or hide text field
		self.w.applyContaining.show(self.w.applyPopup.get() == 1)  # 0=all fonts, 1=fonts containing..., 2=frontmost font only

		# enable or disable run button
		applySettingsEnable = self.w.applyPopup.get() == 0 or len(self.w.applyContaining.get().strip()) > 0
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
							fileName = "%s (unsaved file)" % thisFont.familyName
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
