# MenuTitle: Merge Suffixed Glyphs into Color Layers
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Takes the master layer of suffixed glyphs (e.g., x.shadow, x.body, x.front) and turns them in a specified order into CPAL Color layers of the unsuffixed glyph (e.g., Color 1, Color 0, Color 2 of x).
"""

import vanilla
from copy import copy as copy
from AppKit import NSFont
from GlyphsApp import Glyphs, Message
from mekkaCore import mekkaObject


class MergeSuffixedGlyphsIntoColorLayers(mekkaObject):
	prefDict = {
		"indexToSuffix": "# CPAL index, followed by ‘=’, followed by glyph name suffix\n# list them in chronological order, i.e., bottom-up\n# use hashtags for comments\n0=.shadow\n2=.body\n1=.front",
		"disableSuffixedGlyphs": 1,
		"deletePreexistingColorLayers": 1,
		"processCompleteFont": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 400
		windowHeight = 300
		windowWidthResize = 1000  # user can resize width by this value
		windowHeightResize = 1000  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Merge Suffixed Glyphs into Color Layers",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Merge suffixed glyphs into the following color indexes:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.indexToSuffix = vanilla.TextEditor((2, linePos, -2, -110), "# Syntax: CPAL index = glyph name suffix\n# list them in chronological order (bottom-up)\n# use hashtags for comments\n0=.shadow\n2=.body\n1=.front", callback=self.SavePreferences, checksSpelling=False)
		# self.w.indexToSuffix.getNSTextEditor().setToolTip_("Syntax: colorindex=.suffix, use hashtags for comments. List them in chronological order (bottom-up). Example:\n0=.shadow\n2=.body\n1=.front")

		self.w.indexToSuffix.getNSScrollView().setHasVerticalScroller_(1)
		self.w.indexToSuffix.getNSScrollView().setHasHorizontalScroller_(1)
		self.w.indexToSuffix.getNSScrollView().setRulersVisible_(0)
		try:
			legibleFont = NSFont.legibleFontOfSize_(NSFont.systemFontSize())
		except:
			legibleFont = NSFont.legibileFontOfSize_(NSFont.systemFontSize())
		textView = self.w.indexToSuffix.getNSTextView()
		textView.setFont_(legibleFont)
		textView.setHorizontallyResizable_(1)
		textView.setVerticallyResizable_(1)
		textView.setAutomaticDataDetectionEnabled_(1)
		textView.setAutomaticLinkDetectionEnabled_(1)
		textView.setDisplaysLinkToolTips_(1)
		textSize = textView.minSize()
		textSize.width = 1000
		textView.setMinSize_(textSize)

		linePos = -105

		self.w.disableSuffixedGlyphs = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Deactivate export for glyphs with listed suffixes", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.deletePreexistingColorLayers = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Delete preexisting Color layers in target glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.processCompleteFont = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Process complete font (otherwise only add into selected glyphs)", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Merge", sizeStyle='regular', callback=self.MergeSuffixedGlyphsIntoColorLayersMain)
		# self.w.setDefaultButton( self.w.runButton )

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Merge Suffixed Glyphs into Color Layers' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def nameContainsAnyOfTheseSuffixes(self, glyphName, allSuffixes):
		for suffix in allSuffixes:
			if suffix in glyphName:
				return True
		return False

	def allSuffixes(self, suffixMapping):
		suffixes = []
		for mapping in suffixMapping:
			suffix = mapping[0]
			suffixes.append(suffix)
		return set(suffixes)

	def parseIndexSuffixList(self, textEntry):
		suffixMapping = []
		for line in textEntry.splitlines():
			if "#" in line:
				hashtagOffset = line.find("#")
				line = line[:hashtagOffset]
			if "=" in line:
				items = line.split("=")
				colorIndex = int(items[0].strip())
				suffix = items[1].strip().split()[0]
				suffixMapping.append((suffix, colorIndex))
		return suffixMapping

	def MergeSuffixedGlyphsIntoColorLayersMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Merge Suffixed Glyphs into Color Layers' could not write preferences.")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Merge Suffixed Glyphs into Color Layers Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				indexToSuffix = self.pref("indexToSuffix")
				disableSuffixedGlyphs = self.pref("disableSuffixedGlyphs")
				deletePreexistingColorLayers = self.pref("deletePreexistingColorLayers")
				processCompleteFont = self.pref("processCompleteFont")

				suffixMapping = self.parseIndexSuffixList(indexToSuffix)
				if not suffixMapping:
					Message(title="Merge Error", message="No mapping could be derived from your text entry. Stick to the colorindex=.suffix syntax.", OKButton=None)
				else:
					allSuffixes = self.allSuffixes(suffixMapping)
					if processCompleteFont:
						glyphsToProcess = [g for g in thisFont.glyphs if not self.nameContainsAnyOfTheseSuffixes(g.name, allSuffixes)]
					else:
						glyphsToProcess = [layer.parent for layer in thisFont.selectedLayers if not self.nameContainsAnyOfTheseSuffixes(layer.parent.name, allSuffixes)]

					for targetGlyph in glyphsToProcess:
						glyphName = targetGlyph.name
						print("🔠 %s" % glyphName)

						if deletePreexistingColorLayers:
							print("⚠️ Deleting preexisting Color layers...")
							for i in reversed(range(len(targetGlyph.layers))):
								potentialColorLayer = targetGlyph.layers[i]
								if not potentialColorLayer.isMasterLayer:
									deleteThisLayer = False
									try:
										# GLYPHS 3
										if potentialColorLayer.isColorPaletteLayer():
											deleteThisLayer = True
									except:
										# GLYPHS 2
										if potentialColorLayer.name.startswith("Color "):
											deleteThisLayer = True

									if deleteThisLayer:
										print("  🚫 Removing Color layer ‘%s’" % potentialColorLayer.name)
										currentLayerID = potentialColorLayer.layerId
										try:
											# GLYPHS 3
											targetGlyph.removeLayerForId_(currentLayerID)
										except:
											# GLYPHS 2
											targetGlyph.removeLayerForKey_(currentLayerID)

						for mapping in suffixMapping:
							suffix = mapping[0]
							colorIndex = mapping[1]
							suffixGlyphName = "%s%s" % (glyphName, suffix)
							suffixGlyph = thisFont.glyphs[suffixGlyphName]
							if not suffixGlyph:
								print("⚠️ Not found: %s" % suffixGlyphName)
							else:
								print("✅ Merging %s into CPAL Color %i" % (suffixGlyphName, colorIndex))
								if suffixGlyph.export and disableSuffixedGlyphs:
									suffixGlyph.export = False

								for master in thisFont.masters:
									mID = master.id
									colorLayer = copy(suffixGlyph.layers[mID])
									colorLayer.associatedMasterId = mID
									try:
										# GLYPHS 3
										colorLayer.setColorPaletteLayer_(1)
										colorLayer.setAttribute_forKey_(colorIndex, "colorPalette")
									except:
										# GLYPHS 2
										colorLayer.name = "Color %i" % colorIndex
									targetGlyph.layers.append(colorLayer)

				# self.w.close()  # delete if you want window to stay open

			# Final report:
			Glyphs.showNotification(
				"%s: Done" % (thisFont.familyName),
				"Merge Suffixed Glyphs into Color Layers is finished. Details in Macro Window",
			)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Merge Suffixed Glyphs into Color Layers Error: %s" % e)
			import traceback
			print(traceback.format_exc())


MergeSuffixedGlyphsIntoColorLayers()
