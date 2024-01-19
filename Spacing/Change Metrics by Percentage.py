# MenuTitle: Change Metrics by Percentage
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Increase sidebearings of selected glyphs by a percentage value.
"""

import vanilla
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class ChangeMetricsbyPercentage(mekkaObject):
	prefDict = {
		"LSB": True,
		"RSB": True,
		"changeValue": "+10.0",
	}

	def __init__(self):
		self.w = vanilla.FloatingWindow(
			(430, 60), "Change Metrics of Selected Glyphs by Percentage", minSize=(430, 60), maxSize=(600, 60), autosaveName=self.domain("mainwindow")
		)

		self.w.text_1 = vanilla.TextBox((15, 12 + 2, 50, 14), "Increase", sizeStyle='small')
		self.w.text_2 = vanilla.TextBox((155, 12 + 2, 20, 14), "by", sizeStyle='small')
		self.w.text_3 = vanilla.TextBox((-190, 12 + 2, -170, 14), "%", sizeStyle='small')
		self.w.LSB = vanilla.CheckBox((15 + 55, 12, 40, 18), "LSB", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.RSB = vanilla.CheckBox((15 + 55 + 45, 12, 40, 18), "RSB", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.changeValue = vanilla.EditText((180, 11, -196, 20), "+10.0", sizeStyle='small')

		self.w.runButton = vanilla.Button((-90, 12, -15, 19), "Change", sizeStyle='small', callback=self.ChangeMetricsbyPercentageMain)
		self.w.revertButton = vanilla.Button((-90 - 80, 12, -95, 19), "⟲ Revert", sizeStyle='small', callback=self.ChangeMetricsbyPercentageMain)

		self.w.setDefaultButton(self.w.runButton)

		self.LoadPreferences()

		self.w.open()
		self.w.makeKey()

	def ChangeMetricsbyPercentageMain(self, sender):
		try:
			Font = Glyphs.font
			selectedLayers = Font.selectedLayers

			changeLSB = self.w.LSB.get()
			changeRSB = self.w.RSB.get()
			change = (100.0 + float(self.w.changeValue.get())) / 100.0

			if sender == self.w.revertButton:
				change = 1.0 / change

			for thisLayer in selectedLayers:
				if len(thisLayer.paths) > 0 or len(thisLayer.components) > 0:
					if changeLSB:
						thisLayer.LSB *= change
					if changeRSB:
						thisLayer.RSB *= change

			self.SavePreferences()

			# self.w.close()
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(" Error: %s" % e)


ChangeMetricsbyPercentage()
