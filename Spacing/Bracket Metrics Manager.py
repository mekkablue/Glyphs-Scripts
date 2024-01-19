# MenuTitle: Bracket Metrics Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Manage the sidebearings and widths of bracket layers.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


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
		windowWidth = 350
		windowHeight = 190
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Bracket Metrics Manager",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 30), u"In selected glyphs, syncs metrics of bracket layers with their associated layer, e.g. ‘Bold [90]’ with ‘Bold’.", sizeStyle='small', selectable=True)
		linePos += lineHeight * 2

		self.w.syncLSB = vanilla.CheckBox((inset, linePos - 1, 85, 20), "Sync LSB", value=False, callback=self.syncAction, sizeStyle='small')
		self.w.syncRSB = vanilla.CheckBox((inset + 85, linePos - 1, 85, 20), "Sync RSB", value=False, callback=self.syncAction, sizeStyle='small')
		self.w.syncWidth = vanilla.CheckBox((inset + 85 * 2, linePos - 1, -inset, 20), "Sync Width", value=False, callback=self.syncAction, sizeStyle='small')
		linePos += lineHeight

		self.w.applyToAllGlyphsWithBrackets = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Apply to all glyphs in font that have bracket layers", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.reportOnly = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Only report, do not change metrics", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.openTab = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Open tab with affected bracket glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Sync", sizeStyle='regular', callback=self.BracketMetricsManagerMain)
		self.w.setDefaultButton(self.w.runButton)

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

	def updateUI(self):
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
				print("Path: %s" % thisFont.filepath)
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
