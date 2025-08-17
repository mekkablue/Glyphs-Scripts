#MenuTitle: Add meta Table
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Adds a meta table entry for the frontmost font in Font Info > Font > Custom Parameters.
"""

import vanilla, sys
from itertools import combinations


def recombinations(items):
	result = []
	for r in range(1, len(items) + 1):
		for combo in combinations(items, r):
			result.append(", ".join(combo))
	return result


def relevantScriptsInFont(font, threshold=12):
	scriptsInFont = []
	for glyph in font.allGlyphs():
		if not glyph.export:
			continue
		if not glyph.script:
			continue
		if glyph.script in scriptsInFont:
			continue
		scriptsInFont.append(glyph.script)
	
	relevantScripts = []
	for script in scriptsInFont:
		glyphCount = len([g for g in font.allGlyphs() if g.script==script and g.export])
		if glyphCount >= threshold:
			relevantScripts.append(script)
		print(f"ℹ️ Script {script} has {glyphCount} glyphs in font ‘{font.familyName}’")
	
	print(f"ℹ️ Relevant Scripts: {', '.join(relevantScripts)} (threshold: {threshold} glyphs)")
	
	scriptTags = []
	for script in relevantScripts:
		tag = Glyphs.scriptAbbreviations[script]
		if tag:
			scriptTags.append(tag.title())

	return scriptTags


class AddMetaTable(mekkaObject):
	prefID = "com.mekkablue.AddMetaTable"
	prefDict = {
		# "prefName": defaultValue,
		"slng": "Latn, Arab",
		"dlng": "Latn",
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 250
		windowHeight = 140
		windowWidthResize  = 400 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Add meta Table", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		if Glyphs.font:
			scripts = relevantScriptsInFont(Glyphs.font)
			recombinationsOfScripts = recombinations(scripts)
		else:
			scripts = ["Latn"]
			recombinationsOfScripts = scripts
		
		# UI elements:
		linePos, inset, lineHeight, tabIndent = 12, 15, 22, 80
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Tags for meta Table in Font Info → Font:", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		self.w.dlngDescription = vanilla.TextBox((inset, linePos+2, tabIndent, 14), "Designed for:", sizeStyle="small", selectable=True)
		self.w.dlng = vanilla.ComboBox((inset+tabIndent, linePos-1, -inset-23, 19), scripts, sizeStyle="small", callback=self.SavePreferences)
		self.w.dlngUpdate = UpdateButton((-inset-18, linePos - 2, 20, 18), callback=self.update)
		linePos += lineHeight

		self.w.slngDescription = vanilla.TextBox((inset, linePos+2, tabIndent, 14), "Supported:", sizeStyle="small", selectable=True)
		self.w.slng = vanilla.ComboBox((inset+tabIndent, linePos-1, -inset-23, 19), recombinationsOfScripts, sizeStyle="small", callback=self.SavePreferences)
		self.w.slngUpdate = UpdateButton((-inset-18, linePos - 2, 20, 18), callback=self.update)
		linePos += lineHeight
				
		# Run Button:
		self.w.helpButton = vanilla.HelpButton((inset, -20-inset, 21, 21), callback=self.openURL)
		self.w.runButton = vanilla.Button((-120-inset, -20-inset, -inset, -inset), "Add to Font Info", sizeStyle="regular", callback=self.AddMetaTableMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Tooltips:
		tooltip = "Set dlng (‘design languages’) to the languages and/or scripts that the font was primarily designed for. Separate multiple entries with commas. Possible entries: four-letter script tag (Latn, Cyrl, Grek, Arab, Thai, etc.), or two-letter language tags (de, fr, nl, etc.), or language tags hyphenated with script tags (de-Latn, uk-Cyrl, hi-Deva, etc.)"
		self.w.dlngDescription.getNSTextField().setToolTip_(tooltip)
		self.w.dlng.getNSComboBox().setToolTip_(tooltip)

		tooltip = "Set slng (‘supported languages’) to the languages and/or scripts that the font is declared to be capable of supporting. Separate multiple entries with commas. Possible entries: four-letter script tag (Latn, Cyrl, Grek, Arab, Thai, etc.), or two-letter language tags (de, fr, nl, etc.), or language tags hyphenated with script tags (de-Latn, uk-Cyrl, hi-Deva, etc.)"
		self.w.slngDescription.getNSTextField().setToolTip_(tooltip)
		self.w.slng.getNSComboBox().setToolTip_(tooltip)
		
		tooltip = "Updates the list of predefined choices with all scripts in the frontmost font with a significant number of glyphs."
		self.w.slngUpdate.setToolTip(tooltip)
		self.w.dlngUpdate.setToolTip(tooltip)
		
		tooltip = "Opens the OpenType specification for the meta table in your preferred browser."
		self.w.helpButton.getNSButton().setToolTip_(tooltip)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Add meta Table’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()


	def openURL(self, sender):
		URL = None
		if sender == self.w.helpButton:
			URL = "https://learn.microsoft.com/en-us/typography/opentype/spec/meta"
		if URL:
			import webbrowser
			webbrowser.open(URL)


	def update(self, sender):
		font = Glyphs.font
		scripts = relevantScriptsInFont(font)
		scriptCombos = recombinations(scripts)
		if sender is self.w.dlngUpdate:
			self.w.dlng.setItems(scriptCombos)
		if sender is self.w.slngUpdate:
			self.w.slng.setItems(scriptCombos)


	def AddMetaTableMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Add meta Table’ could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"📄 ‘Add meta Table’ Report for {reportName}")
				print()
				
				parameterName = "meta Table"
				
				# delete all previous parameters
				while thisFont.customParameters[parameterName]:
					del thisFont.customParameters[parameterName]
				
				# build new parameter
				metaTable = [
					{
						"tag": "dlng",
						"data": self.pref("dlng"),
					},
					{
						"tag": "slng",
						"data": self.pref("slng"),
					},
				]
				
				for tag in ("dlng", "slng"):
					print(f"🌍 {tag}: {self.pref(tag)}")
				
				# add to font
				thisFont.customParameters[parameterName] = metaTable
				print("✅ Successfully written meta Table in {reportName}. See Font Info → Font → Custom Parameters.")
				
				self.w.close() # delete if you want window to stay open
				
				# open Font Info window:
				doc = thisFont.parent
				controller = doc.windowController()
				controller.showFontInfoWindowWithTabSelected_(0)

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Add meta Table Error: {e}")
			import traceback
			print(traceback.format_exc())

AddMetaTable()