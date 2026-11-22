# MenuTitle: Add PUA Unicode Values to Selected Glyphs
__doc__ = """
Adds custom Unicode values to selected glyphs.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton, makeWindowResizable


class CustomUnicode(mekkaObject):
	prefDict = {
		"unicode": "E700",
		"keepExistingUnicodes": 1,
		"includeNonExportingGlyphs": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 340
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Add Unicode Values to Selected Glyphs",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		tooltipText = "The first selected glyph will receive this Unicode value. Subsequent glyphs will get the next respective Unicode value, until all selected glyphs have received one."
		self.w.descriptionText = vanilla.TextBox("auto", "Assign Unicode values starting at", selectable=True)
		self.w.descriptionText.setToolTip(tooltipText)
		self.w.unicode = vanilla.EditText("auto", "E700", callback=self.sanitizeEntry)
		self.w.unicode.setToolTip(tooltipText)
		self.w.updateButton = UpdateButton("auto", callback=self.update)
		self.w.updateButton.setToolTip("Resets the starting Unicode to the first BMP PUA available in the font. Useful if you do not wish to overwrite existing PUA codes.")

		self.w.keepExistingUnicodes = vanilla.CheckBox("auto", "Keep existing Unicode values", value=False, callback=self.SavePreferences)
		self.w.keepExistingUnicodes.setToolTip("Two things: it keeps (does not overwrite) the Unicode value of a selected glyph, and it skips Unicode values that are already in use elsewhere in the font. Allows you to select all glyphs and run the script, and thus, assign PUA codes to all unencoded glyphs.")

		self.w.includeNonExportingGlyphs = vanilla.CheckBox("auto", "Include non-exporting glyphs", value=False, callback=self.SavePreferences)
		self.w.includeNonExportingGlyphs.setToolTip("If disabled, will skip all glyphs that are set to not export. If enabled, will treat all selected glyphs, including non-exporting glyphs.")

		# Status Message:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", selectable=True, sizeStyle="small")
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Assign", callback=self.CustomUnicodeMain)
		self.w.runButton.setToolTip("Assigns Unicode values to the selected glyphs, starting at the given value.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, so the field takes the leftover width:
		nsLabel = self.w.descriptionText.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-gap-[unicode(>=60)]-gap-[updateButton]-inset-|",
				"H:|-inset-[keepExistingUnicodes]-(>=inset)-|",
				"H:|-inset-[includeNonExportingGlyphs]-(>=inset)-|",
				"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[unicode]-row-[keepExistingUnicodes]-checkRow-[includeNonExportingGlyphs]-inset-[runButton]-inset-|",
				{"view1": self.w.descriptionText, "attribute1": "centerY", "view2": self.w.unicode, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.unicode, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 10, "checkRow": 5},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def sanitizeEntry(self, sender):
		enteredUnicode = sender.get().upper().strip()
		for digit in enteredUnicode:
			if digit not in "0123456789ABCDEF":
				enteredUnicode = enteredUnicode.replace(digit, "")
		sender.set(enteredUnicode)
		self.SavePreferences(sender)

	def updateUI(self, sender=None):
		self.w.status.set("🤖 Ready.")

	def update(self, sender=None):
		self.setPref("unicode", self.lastPUAofCurrentFont())
		self.LoadPreferences()

	def lastPUAofCurrentFont(self):
		thisFont = Glyphs.font
		if not thisFont:
			return self.pref("unicode")
		lastPUA = sorted(["DFFF"] + [g.unicode for g in thisFont.glyphs if g.unicode and g.unicode >= "E000" and g.unicode <= "E8FF"])[-1]
		return "%04X" % (int(lastPUA, 16) + 1)

	def checkUnicodeEntry(self, unicodeValue):
		length = len(unicodeValue)
		if length < 4 or length > 5:
			print("ERROR: Entry has %i digits and therefore an invalid length. UTF-16 values must contain 4 or 5 hexadecimal digits." % length)
			return False

		# after sanitization, this will probably never be accessed anymore:
		allDigitsValid = True
		for digit in unicodeValue:
			if digit not in "0123456789ABCDEF":
				print("ERROR: Found '%s' in entry. Not a valid hex digit." % digit)
				allDigitsValid = False

		return allDigitsValid

	def statusMsg(self, msg, statusText=None):
		print("  %s" % msg)
		self.w.status.set(statusText or msg)
		self.w.status.getNSTextField().display()  # redraw right away, so it shows while the script is busy

	def CustomUnicodeMain(self, sender):
		try:
			# Try to save prefs:
			self.SavePreferences()

			# just to be safe:
			self.sanitizeEntry(self.w.unicode)
			enteredUnicode = self.pref("unicode")
			keepExistingUnicodes = self.prefBool("keepExistingUnicodes")

			if self.checkUnicodeEntry(enteredUnicode):
				thisFont = Glyphs.font  # frontmost font
				listOfSelectedGlyphs = [layer.parent for layer in thisFont.selectedLayers]  # currently selected glyphs
				PUAcode = int(enteredUnicode, 16)  # calculate the integer number from the Unicode string

				# Report in Macro window:
				Glyphs.clearLog()
				print("Setting Unicode values for '%s':" % thisFont.familyName)

				includeNonExportingGlyphs = self.prefBool("includeNonExportingGlyphs")
				# Apply Unicodes to selected glyphs:
				for thisGlyph in listOfSelectedGlyphs:
					if thisGlyph.export or includeNonExportingGlyphs:
						unicodeValue = "%04X" % PUAcode
						if keepExistingUnicodes:
							if thisGlyph.unicode or thisGlyph.name[0] in "._-":  # exclude .notdef, .null, etc.
								continue
							while thisFont.glyphForUnicode_(unicodeValue):
								self.statusMsg("%s: skipping (already in %s)" % (
									unicodeValue,
									thisFont.glyphForUnicode_(unicodeValue).name,
								), statusText=f"🔠 {thisGlyph.name}")
								PUAcode += 1
								unicodeValue = "%04X" % PUAcode
						thisGlyph.setUnicode_(unicodeValue)
						self.statusMsg("%s: %s" % (unicodeValue, thisGlyph.name), statusText=f"🔠 {thisGlyph.name}")
						PUAcode += 1
					else:
						self.statusMsg("Skipping %s (not exporting)" % thisGlyph.name, statusText=f"🔠 {thisGlyph.name}")

				self.statusMsg("Done.", statusText="✅ Done.")
				# self.w.close()  # closes window
			else:
				Message(
					message="The entered code is not a valid Unicode value. It must be either a four- or five-digit hexadecimal number. Find more details in the Macro Window.",
					title="Unicode Error",
					OKButton=None
				)
				Glyphs.showMacroWindow()

		except Exception as e:
			# brings macro window to front and reports error:
			Message(message="The following error occurred (more details in the Macro Window): %s" % e, title="Script Error", OKButton=None)
			import traceback
			print(traceback.format_exc())
			Glyphs.showMacroWindow()


CustomUnicode()
