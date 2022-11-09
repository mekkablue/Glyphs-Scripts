#MenuTitle: Find And Replace In Anchor Names
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Replaces strings in anchor names of all selected glyphs.
"""

import vanilla
from GlyphsApp import Glyphs
window = None

def SearchAndReplaceInAnchorNames():
	global window
	if window is None:
		windowWidth = 511
		windowHeight = 52
		window = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Search And Replace In Anchor Names", # window title
			autosaveName="com.mekkablue.SearchAndReplaceInAnchorNames.mainwindow" # stores last window position and size
			)

		# UI elements:
		baseline = 14
		window.textSearch = vanilla.TextBox((20, baseline + 3, 67, 16), "Search for:")
		window.searchFor = vanilla.EditText((20 + 50, baseline, 135, 22), "tip")

		window.textReplace = vanilla.TextBox((218, baseline + 3, 67, 16), "Replace by:")
		window.replaceBy = vanilla.EditText((218 + 57, baseline, 135, 22), "top")

		window.replaceButton = vanilla.Button((-85, baseline + 1, -20, 19), "Replace", callback=SearchAndReplaceInAnchorNamesMain)
		window.setDefaultButton(window.replaceButton)

	# Load Settings:
	if not LoadPreferences():
		print("Note: 'Search And Replace In Anchor Names' could not load preferences. Will resort to defaults")

	# Open window and focus on it:
	window.open()
	window.makeKey()

def SavePreferences():
	try:
		Glyphs.defaults["com.mekkablue.SearchAndReplaceInAnchorNames.searchFor"] = window.searchFor.get()
		Glyphs.defaults["com.mekkablue.SearchAndReplaceInAnchorNames.replaceBy"] = window.replaceBy.get()
	except:
		return False
	return True

def LoadPreferences():
	try:
		window.searchFor.set(Glyphs.defaults["com.mekkablue.SearchAndReplaceInAnchorNames.searchFor"])
		window.replaceBy.set(Glyphs.defaults["com.mekkablue.SearchAndReplaceInAnchorNames.replaceBy"])
	except:
		return False
	return True

def SearchAndReplaceInAnchorNamesMain(sender):
	searchString = window.searchFor.get()
	replaceString = window.replaceBy.get()

	thisFont = Glyphs.font # frontmost font
	listOfSelectedLayers = thisFont.selectedLayers # active layers of currently selected glyphs

	for thisLayer in listOfSelectedLayers: # loop through layers
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

	if not SavePreferences():
		print("Note: 'Search And Replace In Anchor Names' could not write preferences.")

	window.close() # delete if you want window to stay open

SearchAndReplaceInAnchorNames()
