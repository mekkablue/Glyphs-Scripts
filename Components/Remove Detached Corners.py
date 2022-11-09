#MenuTitle: Remove Detached Corners
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Removes the specified component from all (selected) glyphs.
"""

import vanilla

def isLayerAffected(thisLayer):
	for h in thisLayer.hints:
		if h.type == CORNER:
			if not h.originNode:
				deleteCornerComponent(h.name, thisLayer)

def deleteCornerComponent(componentName, thisLayer):
	indToDel = []
	for i, h in enumerate(thisLayer.hints):
		if h.isCorner:
			#help(h)
			if h.name == componentName:
				indToDel += [i]
	indToDel = list(reversed(indToDel))
	for i in indToDel:
		del thisLayer.hints[i]

class RemoveDetachedCorners(object):
	padding = (15, 10, 10)

	def __init__(self):
		# Window 'self.w':
		x, y, p = self.padding
		txtH = 14
		windowWidth = 350
		windowHeight = 144
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Remove Detached Corners", # window title
			autosaveName="com.mekkablue.RemoveDetachedCorners.mainwindow" # stores last window position and size
			)

		# UI elements:
		self.w.backgroundLayersChBox = vanilla.CheckBox((x, y, -p, txtH), "Apply to Background Layers", sizeStyle='small')
		y += p + txtH
		self.w.allMastersChBox = vanilla.CheckBox((x, y, -p, txtH), "Apply to All Masters", sizeStyle='small')
		y += p + txtH

		self.w.fromWhere = vanilla.RadioGroup((x, y, -p, 40), ["from all selected glyphs", "from all glyphs in the font"], callback=self.SavePreferences, sizeStyle='small')
		self.w.fromWhere.set(0)
		y += p + 40

		# Run Button:
		self.w.runButton = vanilla.Button((x + 220, y, -p, 22), "Remove", sizeStyle='regular', callback=self.removeDetachedCornersMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Remove Detached Corners' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def SavePreferences(self, sender):
		try:
			Glyphs.defaults["com.mekkablue.RemoveDetachedCorners.fromWhere"] = self.w.fromWhere.get()
			Glyphs.defaults["com.mekkablue.RemoveDetachedCorners.backgroundLayersChBox"] = self.w.backgroundLayersChBox.get()
			Glyphs.defaults["com.mekkablue.RemoveDetachedCorners.allMastersChBox"] = self.w.allMastersChBox.get()
		except:
			return False

		return True

	def LoadPreferences(self):
		try:
			Glyphs.registerDefault("com.mekkablue.RemoveDetachedCorners.fromWhere", "0")
			self.w.fromWhere.set(Glyphs.defaults["com.mekkablue.RemoveDetachedCorners.fromWhere"])

			Glyphs.registerDefault("com.mekkablue.RemoveDetachedCorners.backgroundLayersChBox", "0")
			self.w.backgroundLayersChBox.set(Glyphs.defaults["com.mekkablue.RemoveDetachedCorners.backgroundLayersChBox"])
			Glyphs.registerDefault("com.mekkablue.RemoveDetachedCorners.allMastersChBox", "0")
			self.w.allMastersChBox.set(Glyphs.defaults["com.mekkablue.RemoveDetachedCorners.allMastersChBox"])
		except:
			return False

		return True

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
			thisFont = Glyphs.font # frontmost font
			listOfGlyphs = thisFont.glyphs

			if Glyphs.defaults["com.mekkablue.RemoveDetachedCorners.fromWhere"] == 0:
				listOfGlyphs = [l.parent for l in thisFont.selectedLayers] # active layers of currently selected glyphs

			for thisGlyph in listOfGlyphs:
				self.removeDetachedCornersGlyph(thisGlyph)

			if not self.SavePreferences(self):
				print("Note: 'Remove Detached Corners' could not write preferences.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Detached Corners Error: %s" % e)

RemoveDetachedCorners()
