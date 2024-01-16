# MenuTitle: Add PUA Unicode Values to Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Adds custom Unicode values to selected glyphs.
"""

import vanilla
from GlyphsApp import Glyphs, Message


class CustomUnicode(object):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 130
		windowWidthResize = 200  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Add Unicode Values to Selected Glyphs",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName="com.mekkablue.CustomUnicode.mainwindow"  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 3, 190, 14), u"Assign Unicode values starting at:", sizeStyle='small', selectable=True)
		self.w.unicode = vanilla.EditText((inset + 190, linePos, -inset - 25, 19), "E700", callback=self.sanitizeEntry, sizeStyle='small')
		self.w.unicode.getNSTextField().setToolTip_(u"The first selected glyph will receive this Unicode value. Subsequent glyphs will get the next respective Unicode value, until all selected glyphs have received one.")
		self.w.updateButton = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), u"↺", sizeStyle='small', callback=self.update)
		self.w.updateButton.getNSButton().setToolTip_(u"Resets the starting Unicode to the first BMP PUA available in the font. Useful if you do not wish to overwrite existing PUA codes.")
		linePos += lineHeight

		self.w.keepExistingUnicodes = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Keep existing Unicode values", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.keepExistingUnicodes.getNSButton().setToolTip_(u"Two things: it keeps (does not overwrite) the Unicode value of a selected glyph, and it skips Unicode values that are already in use elsewhere in the font. Allows you to select all glyphs and run the script, and thus, assign PUA codes to all unencoded glyphs.")
		linePos += lineHeight

		self.w.includeNonExportingGlyphs = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExportingGlyphs.getNSButton().setToolTip_(u"If disabled, will skip all glyphs that are set to not export. If enabled, will treat all selected glyphs, including non-exporting glyphs.")
		linePos += lineHeight

		# Status Message:
		self.w.status = vanilla.TextBox((inset, -16 - inset, -inset, -inset), u"", sizeStyle='small', selectable=True)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Assign", sizeStyle='regular', callback=self.CustomUnicodeMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Add PUA Unicode Values to Selected Glyphs' could not load preferences. Will resort to defaults")

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

	def SavePreferences(self, sender):
		try:
			Glyphs.defaults["com.mekkablue.CustomUnicode.unicode"] = self.w.unicode.get()
			Glyphs.defaults["com.mekkablue.CustomUnicode.keepExistingUnicodes"] = self.w.keepExistingUnicodes.get()
			Glyphs.defaults["com.mekkablue.CustomUnicode.includeNonExportingGlyphs"] = self.w.includeNonExportingGlyphs.get()
			self.w.status.set("")
		except:
			return False
		return True

	def LoadPreferences(self):
		try:
			Glyphs.registerDefault("com.mekkablue.CustomUnicode.unicode", "E700")
			Glyphs.registerDefault("com.mekkablue.CustomUnicode.keepExistingUnicodes", 1)
			Glyphs.registerDefault("com.mekkablue.CustomUnicode.includeNonExportingGlyphs", 0)
			self.w.unicode.set(Glyphs.defaults["com.mekkablue.CustomUnicode.unicode"])
			self.w.keepExistingUnicodes.set(Glyphs.defaults["com.mekkablue.CustomUnicode.keepExistingUnicodes"])
			self.w.includeNonExportingGlyphs.set(Glyphs.defaults["com.mekkablue.CustomUnicode.includeNonExportingGlyphs"])
			self.w.status.set("")
		except:
			return False
		return True

	def update(self, sender=None):
		Glyphs.defaults["com.mekkablue.CustomUnicode.unicode"] = self.lastPUAofCurrentFont()
		self.LoadPreferences()

	def lastPUAofCurrentFont(self):
		thisFont = Glyphs.font
		lastPUA = sorted(["DFFF"] + [g.unicode for g in thisFont.glyphs if g.unicode and g.unicode >= "E000" and g.unicode <= "E8FF"])[-1]
		return "%04X" % (int(lastPUA, 16) + 1)

	def checkUnicodeEntry(self, unicodeValue):
		length = len(unicodeValue)
		if length < 4 or length > 5:
			print("ERROR: Entry has %i digits and therefore an invalid length. UTF-16 values must contain 4 or 5 hexadecimal digits." % length)
			return False

		# after sanitization, this will probably never be accessed anymore:
		for digit in unicodeValue:
			allDigitsValid = True
			if digit not in "0123456789ABCDEF":
				print("ERROR: Found '%s' in entry. Not a valid hex digit." % digit)
				allDigitsValid = False

		return allDigitsValid

	def statusMsg(self, msg):
		print("  %s" % msg)
		self.w.status.set(msg)

	def CustomUnicodeMain(self, sender):
		try:
			# Try to save prefs:
			if not self.SavePreferences(self):
				print("Note: 'Add PUA Unicode Values to Selected Glyphs' could not write preferences.")

			# just to be safe:
			self.sanitizeEntry(self.w.unicode)
			enteredUnicode = Glyphs.defaults["com.mekkablue.CustomUnicode.unicode"]
			keepExistingUnicodes = bool(Glyphs.defaults["com.mekkablue.CustomUnicode.keepExistingUnicodes"])

			if self.checkUnicodeEntry(enteredUnicode):
				thisFont = Glyphs.font  # frontmost font
				listOfSelectedGlyphs = [layer.parent for layer in thisFont.selectedLayers]  # currently selected glyphs
				PUAcode = int(enteredUnicode, 16)  # calculate the integer number from the Unicode string

				# Report in Macro window:
				Glyphs.clearLog()
				print("Setting Unicode values for '%s':" % thisFont.familyName)

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
								))
								PUAcode += 1
								unicodeValue = "%04X" % PUAcode
						thisGlyph.setUnicode_(unicodeValue)
						self.statusMsg("%s: %s" % (unicodeValue, thisGlyph.name))
						PUAcode += 1
					else:
						self.statusMsg("Skipping %s (not exporting)" % thisGlyph.name)

				self.statusMsg("Done.")
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
