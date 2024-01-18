# MenuTitle: Find And Replace In Anchor Names
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Replaces strings in anchor names of all selected glyphs.
"""

import vanilla
from GlyphsApp import Glyphs
from mekkaCore import mekkaObject


class SearchAndReplaceInAnchorNames(mekkaObject):
	prefDict = {
		"searchFor": "",
		"replaceBy": "",
	}

	def __init__(self):
		windowWidth = 511
		windowHeight = 52
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Search And Replace In Anchor Names",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		baseline = 14
		self.w.textSearch = vanilla.TextBox((20, baseline + 3, 67, 16), "Search for:")
		self.w.searchFor = vanilla.EditText((20 + 50, baseline, 135, 22), "tip")

		self.w.textReplace = vanilla.TextBox((218, baseline + 3, 67, 16), "Replace by:")
		self.w.replaceBy = vanilla.EditText((218 + 57, baseline, 135, 22), "top")

		self.w.replaceButton = vanilla.Button((-85, baseline + 1, -20, 19), "Replace", callback=self.SearchAndReplaceInAnchorNamesMain)
		self.w.setDefaultButton(self.w.replaceButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def SearchAndReplaceInAnchorNamesMain(self, sender):
		searchString = self.w.searchFor.get()
		replaceString = self.w.replaceBy.get()

		thisFont = Glyphs.font  # frontmost font
		listOfSelectedLayers = thisFont.selectedLayers  # active layers of currently selected glyphs

		for thisLayer in listOfSelectedLayers:  # loop through layers
			thisGlyph = thisLayer.parent
			reportString = "Anchors renamed in %s:" % thisGlyph.name
			displayReportString = False

			for thisGlyphLayer in thisGlyph.layers:
				for thisAnchor in thisGlyphLayer.anchors:
					oldAnchorName = thisAnchor.name
					newAnchorName = oldAnchorName.replace(searchString, replaceString)
					if oldAnchorName != newAnchorName:
						thisAnchor.name = newAnchorName
						reportString += "\n  layer '%s': %s > %s" % (thisGlyphLayer.name, oldAnchorName, newAnchorName)
						displayReportString = True

			if displayReportString:
				print(reportString)

		self.SavePreferences()

		self.w.close()  # delete if you want window to stay open


SearchAndReplaceInAnchorNames()
