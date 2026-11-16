# MenuTitle: Build Italic Shift Feature
__doc__ = """
Creates and inserts GPOS feature code for shifting glyphs, e.g., parentheses and punctuation for the case feature.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSPoint
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, setClipboard, createOTFeature, updatedCode
from mekkablue.geometry import italicize


class ItalicShiftFeature(mekkaObject):
	prefDict = {
		"edit_1a": "case",
		"edit_1b": "100",
		"edit_1c": "exclamdown questiondown",
		"edit_2a": "case",
		"edit_2b": "50",
		"edit_2c": "parenleft parenright braceleft braceright bracketleft bracketright",
		"edit_3a": "",
		"edit_3b": "",
		"edit_3c": "",
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 520
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Italic Shift Feature",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.text_1 = vanilla.TextBox("auto", "Insert GPOS lookup for shifting punctuation in italic angle of 1st master:", sizeStyle='small')

		self.w.edit_1a = vanilla.EditText("auto", "case", sizeStyle='small', placeholder="smcp,c2sc", callback=self.SavePreferences)
		self.w.edit_1b = vanilla.EditText("auto", "100", sizeStyle='small', placeholder="80", callback=self.SavePreferences)
		self.w.edit_1c = vanilla.EditText("auto", "exclamdown questiondown", sizeStyle='small', placeholder="parenleft parenright bracketleft bracketright", callback=self.SavePreferences)

		self.w.edit_2a = vanilla.EditText("auto", "case", sizeStyle='small', placeholder="smcp,c2sc", callback=self.SavePreferences)
		self.w.edit_2b = vanilla.EditText("auto", "50", sizeStyle='small', placeholder="80", callback=self.SavePreferences)
		self.w.edit_2c = vanilla.EditText("auto", "parenleft parenright braceleft braceright bracketleft bracketright", sizeStyle='small', placeholder="parenleft parenright bracketleft bracketright", callback=self.SavePreferences)

		self.w.edit_3a = vanilla.EditText("auto", "", sizeStyle='small', placeholder="smcp,c2sc", callback=self.SavePreferences)
		self.w.edit_3b = vanilla.EditText("auto", "", sizeStyle='small', placeholder="80", callback=self.SavePreferences)
		self.w.edit_3c = vanilla.EditText("auto", "", sizeStyle='small', placeholder="parenleft parenright bracketleft bracketright", callback=self.SavePreferences)

		# Run Button:
		self.w.copyButton = vanilla.Button("auto", "Copy Code", callback=self.ItalicShiftFeatureMain)
		self.w.runButton = vanilla.Button("auto", "Insert", callback=self.ItalicShiftFeatureMain)
		self.w.setDefaultButton(self.w.runButton)

		# keep everything at its natural height, so the window is exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-inset-|",
				"H:|-inset-[edit_1a(70)]-gap-[edit_1b(55)]-gap-[edit_1c]-inset-|",
				"H:|-inset-[edit_2a(70)]-gap-[edit_2b(55)]-gap-[edit_2c]-inset-|",
				"H:|-inset-[edit_3a(70)]-gap-[edit_3b(55)]-gap-[edit_3c]-inset-|",
				"H:|-(>=inset)-[copyButton(>=70)]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[text_1]-row-[edit_1a]-row-[edit_2a]-row-[edit_3a]-inset-[runButton]-inset-|",
				"V:[copyButton]-inset-|",
				{"view1": self.w.edit_1b, "attribute1": "centerY", "view2": self.w.edit_1a, "attribute2": "centerY"},
				{"view1": self.w.edit_1c, "attribute1": "centerY", "view2": self.w.edit_1a, "attribute2": "centerY"},
				{"view1": self.w.edit_2b, "attribute1": "centerY", "view2": self.w.edit_2a, "attribute2": "centerY"},
				{"view1": self.w.edit_2c, "attribute1": "centerY", "view2": self.w.edit_2a, "attribute2": "centerY"},
				{"view1": self.w.edit_3b, "attribute1": "centerY", "view2": self.w.edit_3a, "attribute2": "centerY"},
				{"view1": self.w.edit_3c, "attribute1": "centerY", "view2": self.w.edit_3a, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def ItalicShiftFeatureMain(self, sender):
		try:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			firstMaster = thisFont.masters[0]
			italicAngle = firstMaster.italicAngle
			features = {}

			for lookupIndex in (1, 2, 3):
				otFeature = self.pref("edit_%ia" % lookupIndex)
				verticalShift = self.pref("edit_%ib" % lookupIndex)
				glyphNames = self.pref("edit_%ic" % lookupIndex)

				if otFeature and len(otFeature) > 3 and glyphNames:
					if verticalShift:
						verticalShift = int(verticalShift)
						if verticalShift != 0:
							horizontalShift = int(round(italicize(NSPoint(0, verticalShift), italicAngle=italicAngle, pivotalY=0).x))
							otCode = "\tpos [%s] <%i %i 0 0>;\n" % (glyphNames, horizontalShift, verticalShift)

							if otFeature in features:
								features[otFeature] += otCode
							else:
								features[otFeature] = otCode

			lookupCodes = {}
			for otFeature in features.keys():
				lookupName = "italicShift_%s" % otFeature
				otCode = "lookup %s {\n" % lookupName
				otCode += features[otFeature]
				otCode += "} %s;" % lookupName
				lookupCodes[otFeature] = otCode

			if sender == self.w.copyButton:
				# Copy Code: do not touch the font
				setClipboard("\n\n".join("feature %s {\n%s\n} %s;" % (otFeature, otCode, otFeature) for otFeature, otCode in lookupCodes.items()))
				Glyphs.showNotification("Italic Shift Feature", "Feature code copied to the clipboard.")
			else:
				for otFeature, otCode in lookupCodes.items():
					codeSig = "ITALIC-SHIFT-%s" % otFeature.upper()
					createOTFeature(
						featureName=otFeature,
						codeSig=codeSig,
						targetFont=thisFont,
						featureCode=otCode,
					)
					# keep the code in the notes too, and make sure Glyphs does not regenerate the feature:
					feature = thisFont.features[otFeature]
					feature.automatic = False
					beginSig = "# BEGIN " + codeSig + "\n"
					endSig = "# END " + codeSig + "\n"
					if beginSig in feature.notes:
						feature.notes = updatedCode(feature.notes, beginSig, endSig, otCode)
					else:
						feature.notes += "\n" + beginSig + otCode + "\n" + endSig
				self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Italic Shift Feature Error: %s" % e)
			import traceback
			print(traceback.format_exc())


ItalicShiftFeature()
