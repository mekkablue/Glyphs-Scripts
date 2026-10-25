# MenuTitle: Remove Detached Corners
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Removes corner components that are not linked to a node from all (selected) glyphs.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, CORNER
from mekkablue import mekkaObject


def isLayerAffected(thisLayer):
	for h in thisLayer.hints:
		if h.type == CORNER:
			if not h.originNode:
				deleteCornerComponent(h.name, thisLayer)


def deleteCornerComponent(componentName, thisLayer):
	indToDel = []
	for i, h in enumerate(thisLayer.hints):
		if h.isCorner:
			# help(h)
			if h.name == componentName:
				indToDel += [i]
	indToDel = list(reversed(indToDel))
	for i in indToDel:
		del thisLayer.hints[i]


class RemoveDetachedCorners(mekkaObject):
	prefDict = {
		"fromWhere": 0,
		"backgroundLayersChBox": 1,
		"allMastersChBox": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 260
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Remove Detached Corners",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Delete corner components not linked to a node:", sizeStyle='small', selectable=True)
		self.w.backgroundLayersChBox = vanilla.CheckBox("auto", "Include background layers", sizeStyle='small', callback=self.SavePreferences)
		self.w.allMastersChBox = vanilla.CheckBox("auto", "On all masters", sizeStyle='small', callback=self.SavePreferences)
		self.w.fromWhereText = vanilla.TextBox("auto", "Remove from", sizeStyle='small')
		self.w.fromWhere = vanilla.VerticalRadioGroup("auto", ["selected glyphs", "all glyphs in font"], callback=self.SavePreferences, sizeStyle='small')

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Remove", callback=self.removeDetachedCornersMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; hugging makes the window as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[backgroundLayersChBox]-(>=inset)-|",
				"H:|-inset-[allMastersChBox]-(>=inset)-|",
				"H:|-inset-[fromWhereText]-gap-[fromWhere]-(>=inset)-|",
				"H:|-inset-[runButton]-inset-|",
				"V:|-inset-[descriptionText]-row-[backgroundLayersChBox]-[allMastersChBox]-row-[fromWhere(radioHeight)]-row-[runButton]-inset-|",
				# the label sits next to the first radio button:
				{"view1": self.w.fromWhereText, "attribute1": "top", "view2": self.w.fromWhere, "attribute2": "top"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8, "radioHeight": self.w.fromWhere.getFittingHeight()},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def glyphList(self):
		thisFont = Glyphs.font
		if thisFont:
			return sorted([g.name for g in thisFont.glyphs])
		else:
			return []

	def removeDetachedCornersLayer(self, thisLayer):
		for h in thisLayer.hints:
			if h.type == CORNER:
				if not h.originNode:
					deleteCornerComponent(h.name, thisLayer)

	def removeDetachedCornersGlyph(self, thisGlyph):
		if self.w.allMastersChBox.get() == 1:
			for thisLayer in thisGlyph.layers:
				if thisLayer.isMasterLayer:
					if self.w.backgroundLayersChBox.get() == 1:
						self.removeDetachedCornersLayer(thisLayer.background)
					self.removeDetachedCornersLayer(thisLayer)

		else:
			thisLayer = thisGlyph.layers[Glyphs.font.selectedLayers[0].associatedMasterId]
			if self.w.backgroundLayersChBox.get() == 1:
				self.removeDetachedCornersLayer(thisLayer.background)
			self.removeDetachedCornersLayer(thisLayer)

	def removeDetachedCornersMain(self, sender):
		try:
			thisFont = Glyphs.font  # frontmost font
			listOfGlyphs = thisFont.glyphs

			if self.pref("fromWhere") == 0:
				listOfGlyphs = [layer.parent for layer in thisFont.selectedLayers]  # active layers of currently selected glyphs

			for thisGlyph in listOfGlyphs:
				self.removeDetachedCornersGlyph(thisGlyph)

			self.SavePreferences()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Detached Corners Error: %s" % e)


RemoveDetachedCorners()
