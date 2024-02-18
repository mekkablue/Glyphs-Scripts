# MenuTitle: Remove PS Hints
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Removes PS Hints, selectively or completely.
"""

import vanilla
from GlyphsApp import Glyphs, STEM, BOTTOMGHOST, TOPGHOST
from mekkablue import mekkaObject


class RemovePSHints(mekkaObject):
	prefDict = {
		"horizontalStemHints": 1,
		"verticalStemHints": 1,
		"ghostHints": 1,
		"where": 2,
	}

	wheres = (
		"current layer of selected glyphs",
		"all layers of selected glyphs",
		"this master",
		"⚠️ the complete font",
		"⚠️ all open fonts",
	)

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 170
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Remove PS Hints",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, 160, 14), u"Remove the following hints in", sizeStyle='small', selectable=True)
		self.w.where = vanilla.PopUpButton((inset + 160, linePos, -inset, 17), self.wheres, sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.horizontalStemHints = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Horizontal Stem Hints", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.verticalStemHints = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Vertical Stem Hints", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.ghostHints = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Ghost Hints", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)  # set progress indicator to zero

		self.w.status = vanilla.TextBox((inset, -16 - inset, -inset - 120, 14), "", sizeStyle="small", selectable=True)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Remove Hints", callback=self.RemovePSHintsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self):
		buttonEnable = self.pref("horizontalStemHints") or \
			self.pref("verticalStemHints") or \
			self.pref("ghostHints")
		self.w.runButton.enable(onOff=buttonEnable)

	def removeHintsFromLayer(self, layer, horizontalStemHints, verticalStemHints, ghostHints):
		delCount = 0
		for i in reversed(range(len(layer.hints))):
			h = layer.hints[i]
			if Glyphs.versionNumber >= 3:
				# GLYPHS 3
				isPostScriptHint = h.isPostScript
			else:
				# GLYPHS 2
				isPostScriptHint = h.isPostScript()

			if isPostScriptHint:
				if horizontalStemHints and h.horizontal and h.type == STEM:
					del layer.hints[i]
					delCount += 1
				elif verticalStemHints and not h.horizontal and h.type == STEM:
					del layer.hints[i]
					delCount += 1
				elif ghostHints and h.type in (BOTTOMGHOST, TOPGHOST):
					del layer.hints[i]
					delCount += 1
		return delCount

	def RemovePSHintsMain(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			horizontalStemHints = self.pref("horizontalStemHints")
			verticalStemHints = self.pref("verticalStemHints")
			ghostHints = self.pref("ghostHints")
			where = self.pref("where")

			if where >= 4:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )

			for thisFont in theseFonts:
				print("Remove PS Hints Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				print()

				deletedHintsCount = 0
				if where == 0:
					# Current Layer of Selected Glyphs
					objectList = set(thisFont.selectedLayers)
					count = len(objectList)
					for i, l in enumerate(objectList):
						self.w.progress.set(i / count * 100)
						deletedHintsCount += self.removeHintsFromLayer(l, horizontalStemHints, verticalStemHints, ghostHints)
				elif where == 1:
					# All Layers of Selected Glyphs
					objectList = set(thisFont.selectedLayers)
					count = len(objectList)
					for i, l in enumerate(objectList):
						self.w.progress.set(i / count * 100)
						g = l.parent
						for ll in g.layers:
							deletedHintsCount += self.removeHintsFromLayer(ll, horizontalStemHints, verticalStemHints, ghostHints)
				elif where == 2:
					# this Master
					masterID = thisFont.selectedFontMaster.id
					objectList = thisFont.glyphs
					count = len(objectList)
					for i, g in enumerate(objectList):
						self.w.progress.set(i / count * 100)
						for layer in g.layers:
							if layer.associatedMasterId == masterID:
								deletedHintsCount += self.removeHintsFromLayer(layer, horizontalStemHints, verticalStemHints, ghostHints)
				else:
					# the Complete Font
					objectList = thisFont.glyphs
					count = len(objectList)
					for i, glyph in enumerate(objectList):
						self.w.progress.set(i / count * 100 / len(theseFonts))
						for layer in glyph.layers:
							deletedHintsCount += self.removeHintsFromLayer(layer, horizontalStemHints, verticalStemHints, ghostHints)

			# complete progress bar:
			self.w.progress.set(100)
			self.w.status.set(f"✅ Removed {deletedHintsCount} hint{'' if {deletedHintsCount} == 1 else 's'} in {len(theseFonts)} font{'' if len(theseFonts) == 1 else 's'}")
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove PS Hints Error: %s" % e)
			import traceback
			print(traceback.format_exc())


RemovePSHints()
