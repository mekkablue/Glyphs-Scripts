# MenuTitle: Adjust Image Alpha
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Slider for setting the alpha of all images in selected glyphs.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut, NSWindowStyleMaskResizable
from Foundation import NSSize
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class AdjustImageAlpha(mekkaObject):
	prefDict = {
		"alphaSlider": 100.0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 420
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Adjust Image Alpha for Selected Glyphs",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset, gap = 15, 8
		self.w.text_1 = vanilla.TextBox("auto", "Alpha:", sizeStyle='small')
		self.w.text_1.setToolTip("Transparency of the background images: 100% is fully opaque, 10% is almost invisible.")

		self.w.alphaSlider = vanilla.Slider("auto", value=100.0, minValue=10.0, maxValue=100.0, sizeStyle='small', callback=self.AdjustImageAlphaMain)
		self.w.alphaSlider.setToolTip("Drag to change the alpha of the images in the currently selected glyphs. Updates live.")

		self.w.indicator = vanilla.TextBox("auto", "100%", sizeStyle='small', alignment="right")
		self.w.indicator.setToolTip("Current alpha value in full percentage points.")

		self.w.applyButton = vanilla.Button("auto", "Apply", callback=self.AdjustImageAlphaMain)
		self.w.applyButton.setToolTip("Reapply the current alpha to the images in the currently selected glyphs, without having to move the slider.")

		self.w.globalButton = vanilla.Button("auto", "Global", callback=self.applyToWholeFont)
		self.w.globalButton.setToolTip("Apply the current alpha to ALL images in ALL glyphs (and all masters) of the frontmost font.")

		# everything hugs vertically, so the window ends up exactly as tall as the content:
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-gap-[alphaSlider(>=100)]-gap-[indicator(36)]-inset-[applyButton(>=70)]-gap-[globalButton(>=70)]-inset-|",
				"V:|-inset-[applyButton]-inset-|",
				"V:[globalButton]-inset-|",
				{"view1": self.w.text_1, "attribute1": "centerY", "view2": self.w.applyButton, "attribute2": "centerY"},
				{"view1": self.w.alphaSlider, "attribute1": "centerY", "view2": self.w.applyButton, "attribute2": "centerY"},
				{"view1": self.w.indicator, "attribute1": "centerY", "view2": self.w.applyButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": gap},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()

		# resizable horizontally only: the height is dictated by the content
		window = self.w.getNSWindow()
		window.setStyleMask_(window.styleMask() | NSWindowStyleMaskResizable)
		contentSize = window.contentView().frame().size
		window.setContentMinSize_(NSSize(windowWidth, contentSize.height))
		window.setContentMaxSize_(NSSize(2000, contentSize.height))
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
