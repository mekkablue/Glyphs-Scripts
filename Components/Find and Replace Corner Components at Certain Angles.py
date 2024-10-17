# MenuTitle: Find and Replace Corner Components at Certain Angles
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Replace Corner Components at blunt or acute angles.
"""

import vanilla
import math
from Foundation import NSPoint
from GlyphsApp import Glyphs, CORNER
from mekkablue import mekkaObject


class ReplaceCornersAtCertainAngles(mekkaObject):
	prefDict = {
		"largerOrSmaller": "0",
		"thresholdAngle": "90"
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 260
		windowHeight = 124
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value

		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Replace Corners At Certain Angles",  # window title
			minSize=(windowWidth, windowHeight + 19),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize + 19),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		self.cornerList = self.getAllCorners()

		# UI elements:
		self.w.text_1 = vanilla.TextBox((15 - 1, 12 + 2, 75, 14), "Replace", sizeStyle='small')
		self.w.searchForCorner = vanilla.PopUpButton((15 + 60, 12, -15, 17), self.cornerList, sizeStyle='small', callback=self.CheckButton)
		self.w.text_2 = vanilla.TextBox((15 - 1, 36 + 2, 75, 14), "with", sizeStyle='small')
		self.w.replaceWithCorner = vanilla.PopUpButton((15 + 60, 36, -15, 17), self.cornerList, sizeStyle='small', callback=self.CheckButton)
		self.w.text_3a = vanilla.TextBox((15 - 1, 60 + 2, 75, 14), "at angles", sizeStyle='small')
		self.w.largerOrSmaller = vanilla.PopUpButton((15 + 60, 60, 70, 17), ("larger", "smaller"), sizeStyle='small', callback=self.SavePreferences)
		self.w.text_3b = vanilla.TextBox((150, 60 + 2, 30, 14), "than", sizeStyle='small')
		self.w.thresholdAngle = vanilla.EditText((180, 60, 55, 15 + 3), "90", sizeStyle='small')

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - 15, -20 - 15, -15, -15), "Replace", callback=self.ReplaceCornersAtCertainAnglesMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.CheckButton(None)
		self.w.open()
		self.w.makeKey()

	def CheckButton(self, sender):
		if self.w.searchForCorner.get() == self.w.replaceWithCorner.get():
			self.w.runButton.enable(onOff=False)
		else:
			self.w.runButton.enable(onOff=True)

	def getAllCorners(self):
		thisFont = Glyphs.font
		corners = [g.name for g in thisFont.glyphs if g.name.startswith("_corner.")]
		return corners

	def angleBetweenVectors(self, P0, P1, P2):
		vector1 = NSPoint(P0.x - P1.x, P0.y - P1.y)
		vector2 = NSPoint(P2.x - P1.x, P2.y - P1.y)
		angle1 = math.degrees(math.atan2(vector1.y, vector1.x))
		angle2 = math.degrees(math.atan2(vector2.y, vector2.x))
		angleBetweenVectors = (angle1 - angle2) % 360.0
		return angleBetweenVectors

	def ReplaceCornersAtCertainAnglesMain(self, sender):
		try:
			fromSelection = self.w.searchForCorner.get()
			fromCornerName = self.cornerList[fromSelection]
			toSelection = self.w.replaceWithCorner.get()
			toCornerName = self.cornerList[toSelection]

			smallerThan = bool(self.w.largerOrSmaller.get())
			thresholdAngle = float(self.w.thresholdAngle.get())

			thisFont = Glyphs.font  # frontmost font
			masterIDs = [m.id for m in thisFont.masters]
			selectedGlyphs = [layer.parent for layer in thisFont.selectedLayers]

			for thisGlyph in selectedGlyphs:
				for masterID in masterIDs:
					masterLayer = thisGlyph.layers[masterID]
					print("Processing %s, layer '%s'" % (thisGlyph.name, masterLayer.name))
					if masterLayer.hints:
						for thisHint in masterLayer.hints:
							if thisHint.type == CORNER and thisHint.name == fromCornerName:
								node = thisHint.originNode
								angle = self.angleBetweenVectors(node.prevNode, node, node.nextNode)
								if (smallerThan and angle < thresholdAngle) or (not smallerThan and angle > thresholdAngle):
									thisHint.name = toCornerName

									print("- replaced hint at %i, %i (angle: %.1f)" % (node.x, node.y, angle))
								else:
									print(angle)

			self.SavePreferences()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Replace Corners At Certain Angles Error: %s" % e)


ReplaceCornersAtCertainAngles()
