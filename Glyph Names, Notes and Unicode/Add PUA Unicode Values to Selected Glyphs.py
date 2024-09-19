# MenuTitle: Add PUA Unicode Values to Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Adds custom Unicode values to selected glyphs.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject
from Cocoa import NSImage


class CustomUnicode(mekkaObject):
	prefDict = {
		"unicode": "E700",
		"keepExistingUnicodes": 1,
		"includeNonExportingGlyphs": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 312
		windowHeight = 125
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Add Unicode Values to Selected Glyphs",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 14, 15, 24

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 1, 210, 18), "Assign Unicode values starting at:", selectable=True)
		self.w.unicode = vanilla.EditText((inset + 212, linePos - 1, -inset - 20, 21), "E700", callback=self.sanitizeEntry)
		self.w.unicode.getNSTextField().setToolTip_(u"The first selected glyph will receive this Unicode value. Subsequent glyphs will get the next respective Unicode value, until all selected glyphs have received one.")
		self.w.updateButton = vanilla.SquareButton((-inset - 16, linePos, -inset, 18), "", callback=self.update)
		self.w.updateButton.getNSButton().setImage_(NSImage.imageNamed_("NSRefreshTemplate"))
		self.w.updateButton.getNSButton().setBordered_(False)
		self.w.updateButton.getNSButton().setToolTip_(u"Resets the starting Unicode to the first BMP PUA available in the font. Useful if you do not wish to overwrite existing PUA codes.")
		linePos += lineHeight

		self.w.keepExistingUnicodes = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Keep existing Unicode values", value=False, callback=self.SavePreferences)
		self.w.keepExistingUnicodes.getNSButton().setToolTip_(u"Two things: it keeps (does not overwrite) the Unicode value of a selected glyph, and it skips Unicode values that are already in use elsewhere in the font. Allows you to select all glyphs and run the script, and thus, assign PUA codes to all unencoded glyphs.")
		linePos += lineHeight

		self.w.includeNonExportingGlyphs = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Include non-exporting glyphs", value=False, callback=self.SavePreferences)
		self.w.includeNonExportingGlyphs.getNSButton().setToolTip_(u"If disabled, will skip all glyphs that are set to not export. If enabled, will treat all selected glyphs, including non-exporting glyphs.")
		linePos += lineHeight

		# Status Message:
		self.w.status = vanilla.TextBox((inset, -16 - inset, -inset, -inset), u"", selectable=True)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Assign", callback=self.CustomUnicodeMain)
		self.w.setDefaultButton(self.w.runButton)

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
		self.w.status.set("")

	def update(self, sender=None):
		self.setPref("unicode", self.lastPUAofCurrentFont())
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
