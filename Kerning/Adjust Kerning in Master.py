# MenuTitle: Adjust Kerning
__doc__ = """
Adjusts all kerning values by a specified amount.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSNumberFormatter
from GlyphsApp import Glyphs, GSLTR, GSRTL
from mekkablue import mekkaObject, SteppingEditText, makeWindowResizable

optionList = ("Multiply by", "Add", "Add Absolute", "Round by", "Limit to")


class AdjustKerning(mekkaObject):
	prefDict = {
		"doWhat": 0,
		"howMuch": 20,
		"positive": True,
		"zero": True,
		"negative": True,
	}

	def __init__(self):
		# GUI:
		windowWidth = 300
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Adjust Kerning",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 12

		self.w.text_1 = vanilla.TextBox("auto", "In the current font master, do this:", sizeStyle='small')

		self.w.doWhat = vanilla.PopUpButton("auto", optionList, callback=self.SavePreferences, sizeStyle='small')
		self.w.doWhat.setToolTip("Choose the operation to apply to kerning values.")
		formatter = NSNumberFormatter.alloc().init()  # decimals allowed, e.g., for multiplying by 1.1
		self.w.howMuch = SteppingEditText("auto", "10", sizeStyle='small', callback=self.SavePreferences, formatter=formatter)
		self.w.howMuch.setToolTip("The value to use for the selected operation.")

		self.w.text_2 = vanilla.TextBox("auto", "To these kerning pairs:", sizeStyle='small')

		self.w.positive = vanilla.CheckBox("auto", "Positive,", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.positive.setToolTip("Apply operation to positive kerning pairs.")
		self.w.zero = vanilla.CheckBox("auto", "zero, and", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.zero.setToolTip("Apply operation to zero-value kerning pairs.")
		self.w.negative = vanilla.CheckBox("auto", "negative pairs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.negative.setToolTip("Apply operation to negative kerning pairs.")

		self.w.nextMasterButton = vanilla.Button("auto", "Next Master", callback=self.nextMaster)
		self.w.nextMasterButton.setToolTip("Switch to the next font master. Wraps around to the first master after the last.")
		self.w.runButton = vanilla.Button("auto", "Adjust", callback=self.AdjustKerningMain)
		self.w.runButton.setToolTip("Adjust all kerning values in the current master according to the settings above.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-inset-|",
				"H:|-inset-[doWhat(>=100)]-gap-[howMuch]-inset-|",
				"H:|-inset-[text_2]-inset-|",
				"H:|-inset-[positive]-gap-[zero]-gap-[negative]-(>=inset)-|",
				"H:|-inset-[nextMasterButton(>=70)]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-inset-[text_1]-row-[doWhat]-row-[text_2]-row-[positive]-inset-[runButton]-inset-|",
				"V:[nextMasterButton]-inset-|",
				{"view1": self.w.howMuch, "attribute1": "centerY", "view2": self.w.doWhat, "attribute2": "centerY"},
				{"view1": self.w.zero, "attribute1": "centerY", "view2": self.w.positive, "attribute2": "centerY"},
				{"view1": self.w.negative, "attribute1": "centerY", "view2": self.w.positive, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def nextMaster(self, sender):
		font = Glyphs.font
		if not font or len(font.masters) < 2:
			return
		masters = font.masters
		currentIndex = list(masters).index(font.selectedFontMaster)
		font.masterIndex = (currentIndex + 1) % len(masters)

	def nameForID(self, font, ID):
		try:
			if ID[0] == "@":  # is a group
				return ID
			else:  # is a glyph
				return font.glyphForId_(ID).name
		except Exception as e:
			raise e

	def userChoosesToProcessKerning(self, kernValue):
		try:
			if self.pref("positive") and kernValue > 0:
				return True
			elif self.pref("zero") and kernValue == 0:
				return True
			elif self.pref("negative") and kernValue < 0:
				return True
			else:
				return False
		except Exception as e:
			raise e

	def newKerningValue(self, doWhat, originalKerning, value):
		"""Returns the adjusted kerning value for the chosen operation."""
		if doWhat == 0:  # multiply
			return originalKerning * value
		if doWhat == 1:  # add
			return originalKerning + value
		if doWhat == 2:  # add absolute
			factor = -1 if originalKerning < 0 else 1
			return originalKerning + factor * value
		if doWhat == 3:  # round by
			return round(originalKerning / value, 0) * value
		# limit to:
		return max(-abs(value), min(abs(value), originalKerning))

	def AdjustKerningMain(self, sender):
		font = Glyphs.font
		if not font:
			return
		master = font.selectedFontMaster
		masterID = master.id
		doWhat = self.prefInt("doWhat")
		value = self.prefFloat("howMuch")
		if doWhat == 3 and value == 0:
			Glyphs.showNotification("Adjust Kerning", "Cannot round by zero.")
			return

		font.disableUpdateInterface()
		try:
			for i, directionalKerning in enumerate((font.kerningLTR, font.kerningRTL)):
				if masterID not in directionalKerning.keys():
					print(f"No kerning in {('LTR', 'RTL')[i]} direction on master ‘{master.name}’.")
					continue

				currentDirection = (GSLTR, GSRTL)[i]
				masterKernDict = directionalKerning[masterID]
				if not masterKernDict:
					print(f"Empty kerning in {('LTR', 'RTL')[i]} direction on master ‘{master.name}’.")
					continue

				for leftGlyphID in tuple(masterKernDict.keys()):
					leftName = self.nameForID(font, leftGlyphID)
					for rightGlyphID in tuple(masterKernDict[leftGlyphID].keys()):
						originalKerning = masterKernDict[leftGlyphID][rightGlyphID]
						if self.userChoosesToProcessKerning(originalKerning):
							rightName = self.nameForID(font, rightGlyphID)
							newKerning = self.newKerningValue(doWhat, originalKerning, value)
							if newKerning != originalKerning:
								font.setKerningForPair(masterID, leftName, rightName, newKerning, direction=currentDirection)

		except Exception:
			Glyphs.showMacroWindow()
			print("\n⚠️ Script Error:\n")
			import traceback
			print(traceback.format_exc())
			print()
			raise

		finally:
			font.enableUpdateInterface()  # re-enables UI updates in Font View

		self.SavePreferences()


AdjustKerning()
