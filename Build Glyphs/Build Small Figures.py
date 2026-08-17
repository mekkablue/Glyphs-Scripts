# MenuTitle: Build Small Figures
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Takes a default set of figures (e.g., dnom), and derives the others (.numr, superior/.sups, inferiour/.sinf, .subs) as component copies. Respects the italic angle.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSComponent
from mekkablue import mekkaObject, newGlyphWithName
from mekkablue.geometry import italicize


class smallFigureBuilder(mekkaObject):
	prefDict = {
		"default": ".dnom",
		"derive": ".numr:250, superior:350, inferior:-125",
		"currentMasterOnly": 0,
		"decomposeDefaultFigures": 0,
		"openTab": 1,
		"reuseTab": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 400
		windowHeight = 230  # Auto Layout grows the window if the content needs more
		# no minSize/maxSize: that keeps the window unresizable, and keeps the size limits
		# out of Auto Layout's way
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Build Small Figures",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		# the only multi-line label in this window; its height is fixed, so the layout
		# never has to derive a height from wrapped text:
		self.w.text_0 = vanilla.TextBox("auto", "Takes the Default Suffix figures (e.g. .dnom) and builds compound copies with suffixes in Derivatives (comma-separated suffix:yOffset pairs). Respects Italic Angle when placing components.", sizeStyle='small', selectable=True)

		self.w.text_1 = vanilla.TextBox("auto", "Default Suffix:", sizeStyle='small')
		self.w.default = vanilla.EditText("auto", "", sizeStyle='small', callback=self.SavePreferences)
		self.w.default.setToolTip(u"Small figures with this suffix will be used as components in the derivative figures.")

		self.w.text_2 = vanilla.TextBox("auto", "Derivatives:", sizeStyle='small')
		self.w.derive = vanilla.EditText("auto", "", sizeStyle='small', callback=self.SavePreferences)
		self.w.derive.setToolTip(u"Add suffix:offset pairs (with a colon in between), separated by commas, e.g., ‘.numr:250, superior:350, inferior:-125’. Include the dot if the suffix is a dot suffix. The script will create the figure glyphs or overwrite existing ones.")

		self.w.currentMasterOnly = vanilla.CheckBox("auto", "Only apply to current master (uncheck for all masters)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.currentMasterOnly.setToolTip(u"If checked, will only process the currently selected master in the frontmost font. Useful if you want to use different values for different masters.")

		self.w.decomposeDefaultFigures = vanilla.CheckBox("auto", u"Decompose small figures with Default Suffix", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.decomposeDefaultFigures.setToolTip(u"If checked, will decompose the small figures with the suffix entered in ‘Default Suffix’, before placing them as components in the derivatives. Useful if the current defaults are e.g. numr, and you want to reset it to dnom, and keep all others (numr, superior, inferior) as compounds.")

		self.w.openTab = vanilla.CheckBox("auto", u"Open tab with affected glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.openTab.setToolTip(u"If checked, will open a new tab with all figures that have default and derivative suffixes. Useful for checking.")
		self.w.reuseTab = vanilla.CheckBox("auto", u"Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.setToolTip(u"If checked, will reuse the current tab rather than open a new one. Will open a new one if no tab is currently open and active, though.")

		# Run Button:
		self.w.reportButton = vanilla.Button("auto", "Open Report", callback=self.openMacroWindow)
		self.w.runButton = vanilla.Button("auto", "Build", callback=self.smallFigureBuilderMain)
		self.w.setDefaultButton(self.w.runButton)

		# the description is the one block that wraps: it takes the width it is given
		# (and the height fixed in the rules below) instead of demanding one long line
		self.w.text_0.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# the two field labels hug their text and share a width, so the fields line up:
		for label in (self.w.text_1, self.w.text_2):
			nsLabel = label.getNSTextField()
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes and square buttons do not resist vertical stretching by default; with
		# every control hugging vertically and no flexible gap in the chain, the window ends
		# up exactly as tall as Auto Layout needs. NSLayoutPriorityWindowSizeStayPut (500) is
		# the level at which a constraint starts outranking "keep the window size".
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_0]-inset-|",
				"H:|-inset-[text_1]-gap-[default]-inset-|",
				"H:|-inset-[text_2]-gap-[derive]-inset-|",
				"H:|-inset-[currentMasterOnly]-(>=inset)-|",
				"H:|-inset-[decomposeDefaultFigures]-(>=inset)-|",
				"H:|-inset-[openTab]-gap-[reuseTab]-(>=inset)-|",
				"H:|-(>=inset)-[reportButton(>=70)]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[text_0]-row-[default]-row-[derive]-row-[currentMasterOnly]-row-[decomposeDefaultFigures]-row-[openTab]-inset-[runButton]-inset-|",
				"V:[reportButton]-inset-|",
				{"view1": self.w.text_2, "attribute1": "width", "view2": self.w.text_1, "attribute2": "width"},
				{"view1": self.w.text_1, "attribute1": "centerY", "view2": self.w.default, "attribute2": "centerY"},
				{"view1": self.w.text_2, "attribute1": "centerY", "view2": self.w.derive, "attribute2": "centerY"},
				{"view1": self.w.reuseTab, "attribute1": "centerY", "view2": self.w.openTab, "attribute2": "centerY"},
			],
			metrics={"inset": 15, "gap": 8, "row": 8},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.reuseTab.enable(self.w.openTab.get())

	def openMacroWindow(self, sender=None):
		Glyphs.showMacroWindow()

	def decomposeComponents(self, glyph, masterID=None):
		for layer in glyph.layers:
			if not masterID or layer.associatedMasterId == masterID:
				if layer.components and (layer.isMasterLayer or layer.isSpecialLayer):
					print("   - %i components on layer '%s'" % (len(layer.components), layer.name))
					layer.decomposeComponents()

	def smallFigureBuilderMain(self, sender):
		try:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font

			# report in macro window:
			Glyphs.clearLog()
			print("Build Small Figures, report for: %s" % thisFont.familyName)
			if thisFont.filepath:
				print(thisFont.filepath)
			print()

			# parse user entries and preferences:
			default = self.pref("default").strip()
			derive = self.pref("derive")
			currentMasterOnly = self.pref("currentMasterOnly")
			decomposeDefaultFigures = self.pref("decomposeDefaultFigures")
			figures = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
			offsets = {}
			for suffixPair in [pair.split(":") for pair in derive.split(",")]:
				suffix = suffixPair[0].strip()
				value = float(suffixPair[1].strip())
				offsets[suffix] = value

			createdGlyphCount = 0
			updatedGlyphCount = 0

			# go through 1, 2, 3, 4, 5...
			for i, fig in enumerate(figures):
				# determine default glyph:
				defaultGlyphName = "%s%s" % (fig, default)
				defaultGlyph = thisFont.glyphs[defaultGlyphName]

				if not defaultGlyph:
					print("\nNot found: %s" % defaultGlyphName)
				else:
					print("\n%s Deriving from %s:" % (
						"0️⃣1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣"[i * 3:i * 3 + 3],  # it is actually three unicodes
						defaultGlyphName,
					))

					# decompose if necessary:
					if decomposeDefaultFigures:
						print(" - decomposing %s" % defaultGlyphName)
						if currentMasterOnly:
							mID = thisFont.selectedFontMaster.id
						else:
							mID = None
						self.decomposeComponents(defaultGlyph)

					# step through derivative suffixes:
					for deriveSuffix in offsets:

						# create or overwrite derived glyph:
						deriveGlyphName = "%s%s" % (fig, deriveSuffix)
						deriveGlyph = thisFont.glyphs[deriveGlyphName]
						if not deriveGlyph:
							deriveGlyph = newGlyphWithName(deriveGlyphName)
							thisFont.glyphs.append(deriveGlyph)
							print(" - creating new glyph %s" % deriveGlyphName)
							createdGlyphCount += 1
						else:
							print(" - overwriting glyph %s" % deriveGlyphName)
							updatedGlyphCount += 1

						# copy glyph attributes:
						deriveGlyph.leftKerningGroup = defaultGlyph.leftKerningGroup
						deriveGlyph.rightKerningGroup = defaultGlyph.rightKerningGroup

						# reset category & subcategory:
						deriveGlyph.updateGlyphInfo()

						# add component on each master layer:
						for thisMaster in thisFont.masters:
							isCurrentMaster = thisMaster is thisFont.selectedFontMaster
							if isCurrentMaster or not currentMasterOnly:
								mID = thisMaster.id
								offset = offsets[deriveSuffix]
								offsetPos = NSPoint(0, offset)
								if thisMaster.italicAngle != 0.0:
									offsetPos = italicize(offsetPos, italicAngle=thisMaster.italicAngle)
								defaultComponent = GSComponent(defaultGlyphName, offsetPos)
								deriveLayer = deriveGlyph.layers[mID]
								deriveLayer.clear()
								try:
									# GLYPHS 3:
									deriveLayer.shapes.append(defaultComponent)
								except:
									# GLYPHS 2:
									deriveLayer.components.append(defaultComponent)

			# open a new tab if requested
			if self.pref("openTab"):
				tabText = ""
				for suffix in [default] + sorted(offsets.keys()):
					escapedFigureNames = ["/%s%s" % (fig, suffix) for fig in figures]
					tabText += "".join(escapedFigureNames)
					tabText += "\n"
				tabText = tabText.strip()
				if thisFont.currentTab and self.pref("reuseTab"):
					# reuses current tab:
					thisFont.currentTab.text = tabText
				else:
					# opens new Edit tab:
					thisFont.newTab(tabText)

			# Floating notification:
			Glyphs.showNotification(
				u"%s: small figures built" % (thisFont.familyName),
				u"%i glyph%s created, %i glyph%s updated. Detailed info in Macro Window." % (
					createdGlyphCount,
					"" if createdGlyphCount == 1 else "s",
					updatedGlyphCount,
					"" if updatedGlyphCount == 1 else "s",
				),
			)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Build Small Figures Error: %s" % e)
			import traceback
			print(traceback.format_exc())


smallFigureBuilder()
