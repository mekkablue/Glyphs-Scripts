# MenuTitle: Adjust Image Alpha
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Slider for setting the alpha of all images in selected glyphs.
"""

import vanilla
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class AdjustImageAlpha(mekkaObject):
	prefDict = {
		"alphaSlider": 100.0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 60
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Adjust Image Alpha for Selected Glyphs",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset = 12, 15
		self.w.text_1 = vanilla.TextBox((inset - 1, linePos + 2, 40, 14), "Alpha:", sizeStyle='small')
		self.w.text_1.setToolTip("Transparency of the background images: 100% is fully opaque, 10% is almost invisible.")

		self.w.alphaSlider = vanilla.Slider((inset + 40, linePos, -180, 19), value=100.0, minValue=10.0, maxValue=100.0, sizeStyle='small', callback=self.AdjustImageAlphaMain)
		self.w.alphaSlider.setToolTip("Drag to change the alpha of the images in the currently selected glyphs. Updates live.")

		self.w.indicator = vanilla.TextBox((-175, linePos + 2, -145, 14), "100%", sizeStyle='small')
		self.w.indicator.setToolTip("Current alpha value in full percentage points.")

		self.w.applyButton = vanilla.Button((-138, linePos - 2, -79, 20), "Apply", sizeStyle='regular', callback=self.AdjustImageAlphaMain)
		self.w.applyButton.setToolTip("Reapply the current alpha to the images in the currently selected glyphs, without having to move the slider.")

		self.w.globalButton = vanilla.Button((-74, linePos - 2, -inset, 20), "Global", sizeStyle='regular', callback=self.applyToWholeFont)
		self.w.globalButton.setToolTip("Apply the current alpha to ALL images in ALL glyphs (and all masters) of the frontmost font.")

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		# keep the percentage label in sync with the slider:
		self.w.indicator.set("%i%%" % round(self.prefFloat("alphaSlider")))

	def applyAlphaToLayers(self, layers, alpha):
		for thisLayer in layers:
			if thisLayer.backgroundImage:
				thisLayer.backgroundImage.alpha = alpha

	def AdjustImageAlphaMain(self, sender):
		try:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if not thisFont:
				return
			alpha = round(self.prefFloat("alphaSlider"))
			self.applyAlphaToLayers(thisFont.selectedLayers, alpha)  # active layers of currently selected glyphs

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Adjust Image Alpha Error: %s" % e)
			import traceback
			print(traceback.format_exc())

	def applyToWholeFont(self, sender):
		try:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if not thisFont:
				return
			alpha = round(self.prefFloat("alphaSlider"))
			for thisGlyph in thisFont.glyphs:
				self.applyAlphaToLayers(thisGlyph.layers, alpha)

			Glyphs.showNotification("Adjust Image Alpha", "Set all images in %s to %i%% alpha." % (thisFont.familyName, alpha))

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Adjust Image Alpha Error: %s" % e)
			import traceback
			print(traceback.format_exc())


AdjustImageAlpha()
