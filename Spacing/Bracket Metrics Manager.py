# MenuTitle: Bracket Metrics Manager
__doc__ = """
Manage the sidebearings and widths of bracket layers.
"""

import vanilla
from mekkablue import mekkaObject, fontFileName
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityWindowSizeStayPut,
)


class BracketMetricsManager(mekkaObject):
	prefDict = {
		"syncLSB": 0,
		"syncRSB": 0,
		"syncWidth": 0,
		"applyToAllGlyphsWithBrackets": 0,
		"reportOnly": 0,
		"openTab": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 330
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Bracket Metrics Manager",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "In selected glyphs, syncs metrics of bracket layers with their associated layer, e.g. ‘Bold [90]’ with ‘Bold’.", sizeStyle='small', selectable=True)
		# the description wraps: it takes the width it is given instead of demanding one long line
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.syncLSB = vanilla.CheckBox("auto", "Sync LSB", value=False, callback=self.syncAction, sizeStyle='small')
		self.w.syncRSB = vanilla.CheckBox("auto", "Sync RSB", value=False, callback=self.syncAction, sizeStyle='small')
		self.w.syncWidth = vanilla.CheckBox("auto", "Sync Width", value=False, callback=self.syncAction, sizeStyle='small')

		self.w.applyToAllGlyphsWithBrackets = vanilla.CheckBox("auto", "Apply to all glyphs in font that have bracket layers", value=False, callback=self.SavePreferences, sizeStyle='small')

		self.w.reportOnly = vanilla.CheckBox("auto", "Only report, do not change metrics", value=False, callback=self.SavePreferences, sizeStyle='small')

		self.w.openTab = vanilla.CheckBox("auto", "Open tab with affected bracket glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Sync", callback=self.BracketMetricsManagerMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[syncLSB]-gap-[syncRSB]-gap-[syncWidth]-(>=inset)-|",
				"H:|-inset-[applyToAllGlyphsWithBrackets]-(>=inset)-|",
				"H:|-inset-[reportOnly]-(>=inset)-|",
				"H:|-inset-[openTab]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=80)]-inset-|",
				"V:|-gap-[descriptionText(28)]-gap-[syncLSB]-checkRow-[applyToAllGlyphsWithBrackets]-checkRow-[reportOnly]-checkRow-[openTab]-inset-[runButton]-inset-|",
				{"view1": self.w.syncRSB, "attribute1": "centerY", "view2": self.w.syncLSB, "attribute2": "centerY"},
				{"view1": self.w.syncWidth, "attribute1": "centerY", "view2": self.w.syncLSB, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def syncAction(self, sender):
		if self.w.syncLSB.get() and self.w.syncRSB.get() and self.w.syncWidth.get():
			if sender == self.w.syncLSB:
				self.w.syncRSB.set(0)
			if sender == self.w.syncRSB:
				self.w.syncWidth.set(0)
			if sender == self.w.syncWidth:
				self.w.syncLSB.set(0)
		self.SavePreferences()

	def updateUI(self, sender=None):
		if self.w.reportOnly.get():
			self.w.runButton.setTitle("Report")
			self.w.runButton.enable(onOff=True)
		else:
			self.w.runButton.setTitle("Sync")
			shouldBeEnabled = (self.w.syncLSB.get() or self.w.syncRSB.get() or self.w.syncWidth.get())
			self.w.runButton.enable(onOff=shouldBeEnabled)

	def syncBrackets(self, glyph):
		bracketLayerCount = 0
		syncLSB = self.pref("syncLSB")
		syncRSB = self.pref("syncRSB")
		syncWidth = self.pref("syncWidth")
		print("%s:" % glyph.name)
		for bracketLayer in glyph.layers:
			associatedMaster = bracketLayer.associatedFontMaster()
			masterID = associatedMaster.id
			if bracketLayer.layerId != masterID and "[" in bracketLayer.name and "]" in bracketLayer.name:
				bracketLayerCount += 1
				mainLayer = glyph.layers[masterID]
				print(u" ✅ Syncing layer ‘%s’ with ‘%s’" % (bracketLayer.name, mainLayer.name))
				if syncRSB and syncWidth:
					bracketLayer.RSB = mainLayer.RSB
					lsbShift = mainLayer.width - bracketLayer.width
					bracketLayer.LSB += lsbShift
				else:
					if syncLSB:
						bracketLayer.LSB = mainLayer.LSB
					if syncRSB:
						bracketLayer.RSB = mainLayer.RSB
					if syncWidth:
						bracketLayer.width = mainLayer.width
		if not bracketLayerCount:
			print(u" ⚠️ Warning: no bracket layers found.")

	def reportBrackets(self, glyph):
		bracketLayerCount = 0
		print("%s:" % glyph.name)
		for bracketLayer in glyph.layers:
			associatedMaster = bracketLayer.associatedFontMaster()
			masterID = associatedMaster.id
			if bracketLayer.layerId != masterID and "[" in bracketLayer.name and "]" in bracketLayer.name:
				mainLayer = glyph.layers[masterID]
				bracketLayerCount += 1
				reports = []
				if bracketLayer.LSB == mainLayer.LSB:
					reports.append(u"✅ LSB in sync")
				else:
					reports.append(u"⛔️ LSB diverging")
				if bracketLayer.RSB == mainLayer.RSB:
					reports.append(u"✅ RSB in sync")
				else:
					reports.append(u"⛔️ RSB diverging")
				if bracketLayer.width == mainLayer.width:
					reports.append(u"✅ width in sync")
				else:
					reports.append(u"⛔️ width diverging")

				print(u" - %s: %s" % (bracketLayer.name, "  ".join(reports)))

		if not bracketLayerCount:
			print(u" ⚠️ Warning: no bracket layers found.")

		print()

	def glyphHasBrackets(self, glyph):
		for layer in glyph.layers:
			if layer.isSpecialLayer and "[" in layer.name and "]" in layer.name:
				return True
		return False

	def BracketMetricsManagerMain(self, sender):
		try:
			thisFont = Glyphs.font
			if not thisFont:
				Message(title="Bracket Metrics Manager needs a font", message="Could not determine the frontmost font. Please open a font and try again.", OKButton="Oops")
			else:
				# Clear macro window log:
				Glyphs.clearLog()
				print("Bracket Metrics for: %s" % thisFont.familyName)
				print("Path: %s" % (fontFileName(thisFont, fullPath=True)))
				print()

				if self.pref("applyToAllGlyphsWithBrackets"):
					glyphsToCheck = [g for g in thisFont.glyphs if self.glyphHasBrackets(g)]
				else:
					glyphsToCheck = [layer.parent for layer in thisFont.selectedLayers if self.glyphHasBrackets(layer.parent)]

				if not glyphsToCheck:
					msg = "Could not find any bracket glyphs to examine."
					Message(title="No Bracket Glyphs", message=msg, OKButton=None)
					print(msg)
				else:
					if self.pref("openTab"):
						glyphNames = [g.name for g in glyphsToCheck]
						tabText = "/" + "/".join(glyphNames)
						thisFont.newTab(tabText)

					if self.pref("reportOnly"):
						# brings macro window to front and clears its log:
						Glyphs.showMacroWindow()
						for glyph in glyphsToCheck:
							self.reportBrackets(glyph)
					else:
						for glyph in glyphsToCheck:
							self.syncBrackets(glyph)

				self.SavePreferences()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Bracket Metrics Manager Error: %s" % e)
			import traceback
			print(traceback.format_exc())


BracketMetricsManager()
