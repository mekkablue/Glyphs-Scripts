# MenuTitle: Transfer RTL kerning
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Transfers RTL kerning from one master to another.
"""

import vanilla
from GlyphsApp import Glyphs, RTL, Message


class TransferRTLkerning(object):

	def __init__(self):
		self.listOfMasters = []
		self.updateListOfMasters()

		# Window 'self.w':
		windowWidth = 350
		windowHeight = 110
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Transfer RTL kerning",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName="com.mekkablue.TransferRTLkerning.mainwindow"  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.from_text = vanilla.TextBox((inset, linePos + 2, 130, 17), "Take RTL kerning from:", sizeStyle='small')
		self.w.from_master = vanilla.PopUpButton((inset + 130, linePos, -inset, 17), self.listOfMasterNames(), sizeStyle='small', callback=self.buttonCheck)

		linePos += lineHeight
		self.w.to_text = vanilla.TextBox((inset, linePos + 2, 130, 17), "… and put it into:", sizeStyle='small')
		self.w.to_master = vanilla.PopUpButton((inset + 130, linePos, -inset, 17), self.listOfMasterNames()[::-1], sizeStyle='small', callback=self.buttonCheck)

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Transfer", sizeStyle='regular', callback=self.TransferRTLkerningMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Transfer RTL kerning' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.TransferRTLkerning.from_master"] = self.w.from_master.get()
			Glyphs.defaults["com.mekkablue.TransferRTLkerning.to_master"] = self.w.to_master.get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.TransferRTLkerning.from_master", 0)
			Glyphs.registerDefault("com.mekkablue.TransferRTLkerning.to_master", 0)

			# load previously written prefs:
			self.w.from_master.set(Glyphs.defaults["com.mekkablue.TransferRTLkerning.from_master"])
			self.w.to_master.set(Glyphs.defaults["com.mekkablue.TransferRTLkerning.to_master"])
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

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

	def buttonCheck(self, sender):
		try:
			# check if both font selection point to the same font
			# and disable action button if they do:
			fromFont = self.w.from_master.getItems()[self.w.from_master.get()]
			toFont = self.w.to_master.getItems()[self.w.to_master.get()]

			if fromFont == toFont:
				self.w.runButton.enable(onOff=False)
			else:
				self.w.runButton.enable(onOff=True)

			if not self.SavePreferences(self):
				self.outputError("Could not save preferences during buttonCheck().")
		except:
			import traceback
			print(traceback.format_exc())

	def outputError(self, errMsg):
		print("Transfer RTL Kerning Warning:", errMsg)

	def TransferRTLkerningMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Transfer RTL kerning' could not write preferences.")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
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

				sourceMasterKerning = sourceFont.kerningRTL[sourceMaster.id]
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

							kernValue = sourceFont.kerningForPair(sourceMasterID, firstPartName, secondPartName, direction=RTL)
							if kernValue is not None:
								try:
									targetFont.setKerningForPair(targetMasterID, firstPartName, secondPartName, kernValue, direction=RTL)
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
