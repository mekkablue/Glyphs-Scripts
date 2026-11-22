# MenuTitle: Add meta Table
__doc__="""
Adds a meta table entry for the frontmost font in Font Info > Font > Custom Parameters.
"""

from itertools import combinations
import vanilla
from mekkablue import mekkaObject, reportFontName, UpdateButton, makeWindowResizable
from GlyphsApp import Glyphs, Message
from AppKit import NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut


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
	prefDict = {
		# "prefName": defaultValue,
		"slng": "Latn, Arab",
		"dlng": "Latn",
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Add meta Table",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		if Glyphs.font:
			scripts = relevantScriptsInFont(Glyphs.font)
			recombinationsOfScripts = recombinations(scripts)
		else:
			scripts = ["Latn"]
			recombinationsOfScripts = scripts

		# UI elements:
		self.w.descriptionText = vanilla.TextBox("auto", "Tags for meta Table in Font Info → Font:", sizeStyle="small", selectable=True)

		self.w.dlngDescription = vanilla.TextBox("auto", "Designed for:", sizeStyle="small", selectable=True)
		self.w.dlng = vanilla.ComboBox("auto", scripts, sizeStyle="small", callback=self.SavePreferences)
		self.w.dlngUpdate = UpdateButton("auto", callback=self.update)

		self.w.slngDescription = vanilla.TextBox("auto", "Supported:", sizeStyle="small", selectable=True)
		self.w.slng = vanilla.ComboBox("auto", recombinationsOfScripts, sizeStyle="small", callback=self.SavePreferences)
		self.w.slngUpdate = UpdateButton("auto", callback=self.update)

		# Run Button:
		self.w.helpButton = vanilla.HelpButton("auto", callback=self.openURL)
		self.w.runButton = vanilla.Button("auto", "Add to Font Info", sizeStyle="regular", callback=self.AddMetaTableMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned and share the width of the widest one, so the fields line up:
		labelNames = ("dlngDescription", "slngDescription")
		widestLabel = "dlngDescription"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[dlngDescription]-gap-[dlng(>=100)]-gap-[dlngUpdate]-inset-|",
				"H:|-inset-[slngDescription]-gap-[slng(>=100)]-gap-[slngUpdate]-inset-|",
				"H:|-inset-[helpButton]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-headlineGap-[dlng]-row-[slng]-inset-[runButton]-inset-|",
				{"view1": self.w.dlngDescription, "attribute1": "centerY", "view2": self.w.dlng, "attribute2": "centerY"},
				{"view1": self.w.dlngUpdate, "attribute1": "centerY", "view2": self.w.dlng, "attribute2": "centerY"},
				{"view1": self.w.slngDescription, "attribute1": "centerY", "view2": self.w.slng, "attribute2": "centerY"},
				{"view1": self.w.slngUpdate, "attribute1": "centerY", "view2": self.w.slng, "attribute2": "centerY"},
				{"view1": self.w.helpButton, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": 15, "gap": 8, "row": 6, "headlineGap": 10},
		)

		# Tooltips:
		tooltip = "Set dlng (‘design languages’) to the languages and/or scripts that the font was primarily designed for. Separate multiple entries with commas. Possible entries: four-letter script tag (Latn, Cyrl, Grek, Arab, Thai, etc.), or two-letter language tags (de, fr, nl, etc.), or language tags hyphenated with script tags (de-Latn, uk-Cyrl, hi-Deva, etc.)"
		self.w.dlngDescription.setToolTip(tooltip)
		self.w.dlng.setToolTip(tooltip)

		tooltip = "Set slng (‘supported languages’) to the languages and/or scripts that the font is declared to be capable of supporting. Separate multiple entries with commas. Possible entries: four-letter script tag (Latn, Cyrl, Grek, Arab, Thai, etc.), or two-letter language tags (de, fr, nl, etc.), or language tags hyphenated with script tags (de-Latn, uk-Cyrl, hi-Deva, etc.)"
		self.w.slngDescription.setToolTip(tooltip)
		self.w.slng.setToolTip(tooltip)
		
		tooltip = "Updates the list of predefined choices with all scripts in the frontmost font with a significant number of glyphs."
		self.w.slngUpdate.setToolTip(tooltip)
		self.w.dlngUpdate.setToolTip(tooltip)
		
		tooltip = "Opens the OpenType specification for the meta table in your preferred browser."
		self.w.helpButton.setToolTip(tooltip)
		
		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()
		
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
		if not font:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			return
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
			self.SavePreferences()
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				reportName = reportFontName(thisFont)
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
				print(f"✅ Successfully written meta Table in {thisFont.familyName}. See Font Info → Font → Custom Parameters.")
				
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
