# MenuTitle: Transfer RTL Kerning
__doc__ = """
Transfers RTL kerning from one master to another.
"""

import vanilla
from AppKit import NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject

if Glyphs.versionNumber < 4.0:
	# Glyphs 3 only had the old name, dropped in Glyphs 4:
	from GlyphsApp import RTL as GSRTL
else:
	from GlyphsApp import GSRTL


class TransferRTLkerning(mekkaObject):
	prefDict = {
		"from_master": 0,
		"to_master": 0,
	}

	def __init__(self):
		self.listOfMasters = []
		self.updateListOfMasters()

		# Window 'self.w':
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Transfer RTL kerning",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.from_text = vanilla.TextBox("auto", "Take RTL kerning from:", sizeStyle='small')
		self.w.from_master = vanilla.PopUpButton("auto", self.listOfMasterNames(), sizeStyle='small', callback=self.SavePreferences)

		self.w.to_text = vanilla.TextBox("auto", "… and put it into:", sizeStyle='small')
		self.w.to_master = vanilla.PopUpButton("auto", self.listOfMasterNames()[::-1], sizeStyle='small', callback=self.SavePreferences)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Transfer", callback=self.TransferRTLkerningMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned, hug their text and share one width:
		for labelName in ("from_text", "to_text"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[from_text]-gap-[from_master]-inset-|",
				"H:|-inset-[to_text]-gap-[to_master]-inset-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[from_master]-row-[to_master]-inset-[runButton]-inset-|",
				{"view1": self.w.from_text, "attribute1": "centerY", "view2": self.w.from_master, "attribute2": "centerY"},
				{"view1": self.w.to_text, "attribute1": "centerY", "view2": self.w.to_master, "attribute2": "centerY"},
				{"view1": self.w.to_text, "attribute1": "width", "view2": self.w.from_text, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateListOfMasters(self):
		try:
			masterList = []

			for thisFont in Glyphs.fonts:
				for thisMaster in thisFont.masters:
					masterList.append(thisMaster)

			masterList.reverse()  # so index accessing works as expected, and the default is: current font = target
			self.listOfMasters = masterList
		except:
			import traceback
			print(traceback.format_exc())

	def listOfMasterNames(self):
		try:
			myMasterNameList = ["%i: %s - %s" % (i + 1, self.listOfMasters[i].font.familyName, self.listOfMasters[i].name) for i in range(len(self.listOfMasters))]
			return myMasterNameList
		except:
			import traceback
			print(traceback.format_exc())

	def updateUI(self, sender=None):
		# disable the action button if both popups point to the same master (or there are no masters):
		fromIndex = self.w.from_master.get()
		toIndex = self.w.to_master.get()
		if fromIndex < 0 or toIndex < 0:
			self.w.runButton.enable(onOff=False)
			return
		fromMaster = self.w.from_master.getItems()[fromIndex]
		toMaster = self.w.to_master.getItems()[toIndex]
		self.w.runButton.enable(onOff=fromMaster != toMaster)

	def outputError(self, errMsg):
		print("Transfer RTL Kerning Warning:", errMsg)

	def TransferRTLkerningMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			else:
				print("Transfer RTL kerning Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				fromFontIndex = self.w.from_master.get()
				toFontIndex = self.w.to_master.get() * -1 - 1
				sourceMaster = self.listOfMasters[fromFontIndex]
				targetMaster = self.listOfMasters[toFontIndex]
				sourceMasterID = sourceMaster.id
				targetMasterID = targetMaster.id
				sourceFont = sourceMaster.font
				targetFont = targetMaster.font
				"""kerningRTL
				Kerning for RTL writing A multi-level dictionary.
				The first level’s key is the GSFontMaster.id (each master has its own kerning),
				the second level’s key is the GSGlyph.id or class id (@MMK_L_XX) of the first glyph,
				the third level’s key is a glyph id or class id (@MMK_R_XX) for the second glyph.
				The values are the actual kerning values.
				"""

				if sourceMasterID not in sourceFont.kerningRTL.keys():
					print("⚠️ No RTL kerning in master ‘%s’ of %s." % (sourceMaster.name, sourceFont.familyName))
					return
				sourceMasterKerning = sourceFont.kerningRTL[sourceMasterID]
				for firstPart in sourceMasterKerning.keys():
					if not firstPart.startswith("@"):
						firstGlyph = sourceFont.glyphForId_(firstPart)
						firstPartName = firstGlyph.name
					else:
						firstPartName = firstPart

					try:
						for secondPart in sourceMasterKerning[firstPart].keys():
							if not secondPart.startswith("@"):
								secondGlyph = sourceFont.glyphForId_(secondPart)
								secondPartName = secondGlyph.name
							else:
								secondPartName = secondPart

							kernValue = sourceFont.kerningForPair(sourceMasterID, firstPartName, secondPartName, direction=GSRTL)
							if kernValue is not None:
								try:
									targetFont.setKerningForPair(targetMasterID, firstPartName, secondPartName, kernValue, direction=GSRTL)
									print("✅ Kerning %s ↔️ %s (%i)" % (firstPartName, secondPartName, kernValue))
								except Exception as e:
									print("⚠️ Could not set kerning %s ↔️ %s (%i):\n   %s" % (firstPartName, secondPartName, kernValue, e))
							else:
								print("❓ kerning for %s %s is none." % (firstPartName, secondPartName))
					except Exception as e:
						print("Weird error when trying to access kerning for %s:\n%s" % (firstPartName, e))
				"""
				setKerningForPair(fontMasterId, leftKey, rightKey, value[, direction = LTR])
				This sets the kerning for the two specified glyphs (leftKey or rightKey is the glyphname) or a kerning group key (@MMK_X_XX).
				Parameters
				fontMasterId (str) – The id of the FontMaster
				leftKey (str) – either a glyph name or a class name
				rightKey (str) – either a glyph name or a class name
				value (float) – kerning value
				direction (str) – optional writing direction (see Constants). Default is LTR.
				# set kerning for group T and group A for currently selected master
				# ('L' = left side of the pair and 'R' = left side of the pair)
				font.setKerningForPair(font.selectedFontMaster.id, '@MMK_L_T', '@MMK_R_A', -75)
				"""

			# Final report:
			Glyphs.showNotification(
				"%s: Done" % (thisFont.familyName),
				"Transfer RTL kerning is finished. Details in Macro Window",
			)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Transfer RTL kerning Error: %s" % e)
			import traceback
			print(traceback.format_exc())


TransferRTLkerning()
