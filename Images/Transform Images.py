# MenuTitle: Transform Images
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Batch scale and move images in selected layers.
"""

import vanilla
from AppKit import NSAffineTransform
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


def getScale(scaleString, factor):
	if factor == 1:
		return (100.0 + float(scaleString)) / 100.0
	else:
		return 100.0 / (100.0 + float(scaleString))


class TransformImages(mekkaObject):
	prefDict = {
		"scaleX": 100,
		"scaleY": 100,
		"moveX": 0,
		"moveY": 0,
	}

	def __init__(self):
		windowHeight = 120
		self.w = vanilla.FloatingWindow(
			(250, windowHeight), "Transform Images", minSize=(250, windowHeight), maxSize=(250, windowHeight), autosaveName=self.domain("mainwindow")
		)

		self.w.scale_text1 = vanilla.TextBox((15 - 1, 12 + 2, 75, 14), "Scale x/y:", sizeStyle='small')
		self.w.scaleX = vanilla.EditText((15 + 60, 12, 55, 15 + 3), "+10.5", sizeStyle='small')
		self.w.scaleY = vanilla.EditText((15 + 60 + 60, 12, 55, 15 + 3), "-11.0", sizeStyle='small')
		self.w.scale_text2 = vanilla.TextBox((15 + 60 + 60 + 60, 12 + 2, -15, 14), "%", sizeStyle='small')

		self.w.move_text1 = vanilla.TextBox((15 - 1, 25 + 12 + 2, 75, 14), "Move x/y:", sizeStyle='small')
		self.w.moveX = vanilla.EditText((15 + 60, 25 + 12, 55, 15 + 3), "10", sizeStyle='small')
		self.w.moveY = vanilla.EditText((15 + 60 + 60, 25 + 12, 55, 15 + 3), "10", sizeStyle='small')
		self.w.move_text2 = vanilla.TextBox((15 + 60 + 60 + 60, 25 + 12 + 2, -15, 14), "units", sizeStyle='small')

		# self.w.resetButton = vanilla.Button((-80 - 80 - 15, -20 - 15, -85, -15), "Reset", sizeStyle='regular', callback=self.ResetStructs)
		self.w.backButton = vanilla.Button((-60 - 60 - 23, -20 - 15, -60 - 23, -15), "Back", sizeStyle='regular', callback=self.TransformImagesMain)
		self.w.runButton = vanilla.Button((-60 - 15, -20 - 15, -15, -15), "Go", sizeStyle='regular', callback=self.TransformImagesMain)
		self.w.setDefaultButton(self.w.runButton)

		try:
			self.LoadPreferences()
		except:
			pass

		self.w.open()

	def TransformImagesMain(self, sender):
		try:
			Font = Glyphs.font
			selectedLayers = Font.selectedLayers
			if sender == self.w.backButton:
				factor = -1.0
			elif sender == self.w.runButton:
				factor = 1.0

			for thisLayer in selectedLayers:
				thisImage = thisLayer.backgroundImage
				if thisImage:
					moveXpreScaled, moveYpreScaled, scaleXfix, scaleYfix = self.w.moveX.get(), self.w.moveY.get(), self.w.scaleX.get(), self.w.scaleY.get()
					if moveXpreScaled == "":
						moveXpreScaled = 0
					if moveYpreScaled == "":
						moveYpreScaled = 0
					if scaleXfix == "":
						scaleXfix = 0
					if scaleYfix == "":
						scaleYfix = 0
					moveX, moveY = float(moveXpreScaled) * factor, float(moveYpreScaled) * factor
					scaleX, scaleY = getScale(scaleXfix, factor), getScale(scaleYfix, factor)

					ScaleAndMoveTransform = NSAffineTransform.transform()
					ScaleAndMoveTransform.setTransformStruct_(thisImage.transformStruct())
					ScaleAndMoveTransform.scaleXBy_yBy_(scaleX, scaleY)
					ScaleAndMoveTransform.translateXBy_yBy_(moveX, moveY)
					thisImage.setTransformStruct_(ScaleAndMoveTransform.transformStruct())

			self.SavePreferences()

			# self.w.close()
		except Exception as e:
			raise e


TransformImages()
