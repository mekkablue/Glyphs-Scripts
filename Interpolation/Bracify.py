# MenuTitle: Bracify
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Turn font masters into brace layers of certain glyphs. A.k.a. Sparsify.
"""

import vanilla
from AppKit import NSFont
from copy import copy as copy
from GlyphsApp import Glyphs, Message
from mekkaCore import mekkaObject


def braceLayerAndAxisDictForGlyphAndMaster(glyph, master):
	# layer:
	mID = master.id
	braceLayer = copy(glyph.layers[mID])
	# coords:
	font = glyph.parent
	coordinates = master.axes
	axisIDs = [a.id for a in font.axes]
	axisDict = dict(zip(axisIDs, coordinates))
	return braceLayer, axisDict


def addBraceLayerToGlyph(braceLayer, axisDict, glyph, associatedMaster):
	braceLayer.parent = glyph
	braceLayer.associatedMasterId = associatedMaster.id
	braceLayer.attributes["coordinates"] = axisDict
	glyph.layers.append(braceLayer)


def layerIsSuperfluous(layer, threshold=2):
	originalLayer = copy(layer)
	originalLayer.parent = layer.parent
	layer.reinterpolate()

	# compare widths:
	if abs(layer.width - originalLayer.width) > threshold:
		layer = originalLayer
		return False

	# compare anchors:
	for anchor in layer.anchors:
		xDiff = abs(anchor.position.x - originalLayer.anchors[anchor.name].position.x)
		yDiff = abs(anchor.position.y - originalLayer.anchors[anchor.name].position.y)
		if xDiff > threshold or yDiff > threshold:
			layer = originalLayer
			return False

	# compare point coordinates:
	for pi, path in enumerate(layer.paths):
		originalPath = originalLayer.paths[pi]
		for ni, node in enumerate(path.nodes):
			originalNode = originalPath.nodes[ni]
			xDiff = abs(originalNode.x - node.x)
			yDiff = abs(originalNode.y - node.y)
			if xDiff > threshold and yDiff > threshold:
				layer = originalLayer
				return False

	layer = originalLayer
	return True


def nonSuperfluousLayersInMaster(font, master, threshold):
	glyphNameList = []
	for glyph in font.glyphs:
		layer = glyph.layers[master.id]
		if layer.paths and not layerIsSuperfluous(layer, threshold):
			glyphNameList.append(glyph.name)
	return glyphNameList


def masterList(font):
	listOfMasters = []
	if font:
		for i, m in enumerate(font.masters):
			entry = f"{i}: {m.name} (ID: {m.id})"
			listOfMasters.append(entry)
	return listOfMasters


class Bracify(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"masterToRemove": 1,
		"associateMaster": 0,
		"threshold": 3,
		"braceGlyphs": "",
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 420
		windowHeight = 300
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 500  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Bracify",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		indent = 130
		self.w.masterToRemoveText = vanilla.TextBox((inset, linePos + 2, indent, 14), "Remove font master:", sizeStyle="small", selectable=True)
		self.w.masterToRemove = vanilla.PopUpButton((inset + indent, linePos, -inset, 17), masterList(Glyphs.font), sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight

		self.w.associateMasterText = vanilla.TextBox((inset, linePos + 2, indent, 14), "Associate with master:", sizeStyle="small", selectable=True)
		self.w.associateMaster = vanilla.PopUpButton((inset + indent, linePos, -inset, 17), masterList(Glyphs.font), sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight

		indent = 190
		self.w.thresholdText = vanilla.TextBox((inset, linePos + 2, indent, 14), "Coordinate threshold for guessing:", sizeStyle="small", selectable=True)
		self.w.threshold = vanilla.EditText((inset + indent, linePos, 50, 19), "3", callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.braceGlyphsText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Add master layer as brace layer to these glyphs:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.braceGlyphs = vanilla.TextEditor((1, linePos, -1, -inset * 3), text="", callback=self.SavePreferences, checksSpelling=False)
		self.w.braceGlyphs.getNSTextView().setToolTip_("Comma-separated list of glyph names. Use the Guess button to add the glyphs that would change too much (more than the threshold) if they didn’t keep a brace layer after master removal.")
		self.w.braceGlyphs.getNSScrollView().setHasVerticalScroller_(1)
		self.w.braceGlyphs.getNSScrollView().setHasHorizontalScroller_(0)
		self.w.braceGlyphs.getNSScrollView().setRulersVisible_(0)
		textView = self.w.braceGlyphs.getNSTextView()
		legibleFont = NSFont.controlContentFontOfSize_(NSFont.systemFontSize())
		textView.setFont_(legibleFont)
		textView.setHorizontallyResizable_(0)
		textView.setVerticallyResizable_(1)
		textView.setAutomaticDataDetectionEnabled_(0)
		textView.setAutomaticLinkDetectionEnabled_(0)
		textView.setDisplaysLinkToolTips_(0)
		textSize = textView.minSize()
		textView.setMinSize_(textSize)

		self.w.guessButton = vanilla.Button((inset, -20 - inset, 80, -inset), "Guess", sizeStyle="regular", callback=self.BracifyGuess)
		self.w.updateButton = vanilla.Button((inset + 90, -20 - inset, 80, -inset), "Update", sizeStyle="regular", callback=self.UpdateForCurrentFont)
		self.w.openTabButton = vanilla.Button((inset + 90 * 2, -20 - inset, 80, -inset), "Open Tab", sizeStyle="regular", callback=self.OpenTab)

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Remove Master", sizeStyle="regular", callback=self.BracifyMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.runButton.enable(self.pref("masterToRemove") != self.pref("associateMaster") and self.pref("braceGlyphs"))

	def UpdateForCurrentFont(self, sender=None):
		font = Glyphs.font
		self.w.associateMaster.setItems(masterList(font))
		self.w.masterToRemove.setItems(masterList(font))
		self.LoadPreferences()

	def OpenTab(self, sender=None):
		font = Glyphs.font
		self.SavePreferences()
		glyphNames = self.pref("braceGlyphs").strip()
		glyphNameList = glyphNames.split(",")
		tabString = ""
		warningGlyphs = []
		for glyphName in glyphNameList:
			glyphName = glyphName.strip()
			if font.glyphs[glyphName]:
				tabString += f"/{glyphName}"
			else:
				warningGlyphs.append(glyphName)
		if warningGlyphs:
			Message(
				title=f"Glyphs Missing in {font.familyName}",
				message=f"{len(warningGlyphs)} glyph{' is' if len(warningGlyphs) == 1 else 's are'} not in the frontmost font: {', '.join(warningGlyphs)}.",
				OKButton=None,
			)
		font.newTab(tabString)

	def BracifyGuess(self, sender=None):
		font = Glyphs.font
		masterIndex = self.prefInt("masterToRemove")
		master = font.masters[masterIndex]
		threshold = self.prefInt("threshold")
		glyphNameList = nonSuperfluousLayersInMaster(font, master, threshold=threshold)
		glyphNameText = ", ".join(glyphNameList)
		self.w.braceGlyphs.set(glyphNameText)
		self.SavePreferences()

	def BracifyMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			font = Glyphs.font  # frontmost font
			if font is None:
				Message(
					title="No Font Open",
					message="The script requires a font with at least three masters. Open a font and run the script again.",
					OKButton=None,
				)
				return

			if len(font.masters) < 3:
				Message(
					title="Not Enough Masters",
					message="This script does not make sense for fonts with less than three masters.",
					OKButton=None,
				)
				return

			filePath = font.filepath
			if filePath:
				reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
			else:
				reportName = f"{font.familyName}\n⚠️ The font file has not been saved yet."
			print(f"Bracify Report for {reportName}")
			print()

			associateMaster = self.prefInt("associateMaster")
			masterToRemove = self.prefInt("masterToRemove")
			master = font.masters[masterToRemove]
			masterName = master.name

			glyphNames = self.pref("braceGlyphs").strip()
			glyphNameList = glyphNames.split(",")
			print(f"💚 Building brace layers for {len(glyphNameList)} glyph{'' if len(glyphNameList) == 1 else 's'}: {glyphNames}.\n")

			for glyphName in glyphNameList:
				glyphName = glyphName.strip()
				glyph = font.glyphs[glyphName]
				if not glyph:
					print(f"⚠️ No glyph with name ‘{glyphName}’, skipping.")
					continue
				braceLayer, axisDict = braceLayerAndAxisDictForGlyphAndMaster(glyph, master)
				addBraceLayerToGlyph(braceLayer, axisDict, glyph, font.masters[associateMaster])
				print(f"✅ Added brace layer: {glyphName}.")

			font.removeFontMaster_(master)
			print(f"\n🚀 Removed master: {masterName}.")

			tab = font.currentTab
			if not tab:
				tab = font.newTab()
			tab.text = "/" + "/".join(glyphNameList)
			print("✅ Done.")

			self.w.close()  # delete if you want window to stay open

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Bracify Error: {e}")
			import traceback
			print(traceback.format_exc())


Bracify()
