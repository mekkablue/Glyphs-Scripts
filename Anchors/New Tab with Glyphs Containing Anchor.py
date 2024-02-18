# MenuTitle: New Tab with Glyphs Containing Anchor
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Opens a new tab with all glyphs containing a specific anchor.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


class NewTabWithAnchor(mekkaObject):
	prefDict = {
		"anchorName": "ogonek",
		"allLayers": 0,
		"keepWindowOpen": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 160
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"New Tab with Anchor",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		self.w.text_1 = vanilla.TextBox((15, 15, 100, 14), "Look for anchor", sizeStyle='small')
		self.w.anchorName = vanilla.EditText((110, 12, -15, 20), "ogonek", sizeStyle='small')
		self.w.text_2 = vanilla.TextBox((15, 38, -15, 14), "and open a tab with all glyphs containing it.", sizeStyle='small')

		self.w.allLayers = vanilla.CheckBox((15, 60, -15, 20), "Look on all layers (otherwise only on current master)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.keepWindowOpen = vanilla.CheckBox((15, 80, -15, 20), "Keep window open", value=False, callback=self.SavePreferences, sizeStyle='small')

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - 15, -20 - 15, -15, -15), "Open Tab", callback=self.NewTabWithAnchorMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def layerContainsAnchor(self, thisLayer, anchorName):
		anchorNames = [a.name for a in thisLayer.anchors]
		if anchorName in anchorNames:
			print("Found %s in %s, on layer ‘%s’" % (anchorName, thisLayer.parent.name, thisLayer.name))
			return True
		return False

	def glyphContainsAnchor(self, thisGlyph, anchorName, masterIdToBeChecked):
		if masterIdToBeChecked:
			masterLayer = thisGlyph.layers[masterIdToBeChecked]
			return self.layerContainsAnchor(masterLayer, anchorName)
		else:
			for thisLayer in thisGlyph.layers:
				if self.layerContainsAnchor(thisLayer, anchorName):
					return True
			return False

	def errMsg(self, errorMessage):
		message = "The script 'New Tab with Anchor' encountered the following error: %s" % errorMessage
		print(message)
		Message(title="New Tab with Anchor Error", message=message, OKButton=None)

	def NewTabWithAnchorMain(self, sender):
		thisFont = Glyphs.font  # frontmost font

		print("‘New Tab with Glyphs Containing Anchor’ Report for %s" % thisFont.familyName)
		print(thisFont.filepath)
		print()

		try:
			self.SavePreferences()

			anchorName = self.pref("anchorName")
			allLayers = self.pref("allLayers")
			keepWindowOpen = self.pref("keepWindowOpen")

			if anchorName:
				allGlyphsContainingAnchor = []
				if allLayers:
					masterId = None
				else:
					masterId = thisFont.selectedFontMaster.id  # active master id

				# go through all glyphs and look for anchor:
				for thisGlyph in thisFont.glyphs:
					if self.glyphContainsAnchor(thisGlyph, anchorName, masterId):
						allGlyphsContainingAnchor.append(thisGlyph.name)

				if allGlyphsContainingAnchor:
					# create string with slash-escaped names:
					glyphNameString = "/" + "/".join(allGlyphsContainingAnchor)
					thisFont.newTab(glyphNameString)
				else:
					Message(
						title="Could not find anchor",
						message="No glyph with anchor ‘%s’ found in %s." % (anchorName, thisFont.familyName),
						OKButton=None,
					)

				if not keepWindowOpen:
					self.w.close()  # closes window
			else:
				self.errMsg("No anchor name specified. Please enter an anchor name before pressing the button.")
		except Exception as e:
			self.errorMsg(e)


Glyphs.clearLog()  # clears macro window log
NewTabWithAnchor()
