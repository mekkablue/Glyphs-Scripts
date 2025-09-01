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
		windowWidth = 390
		windowHeight = 42
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Change Metrics of Selected Glyphs by Percentage",
			autosaveName=self.domain("mainwindow")
		)

		linePos, inset = 12, 15
		xPos = inset
		self.w.text_1 = vanilla.TextBox((xPos, linePos + 2, 50, 14), "Increase", sizeStyle='small')
		xPos += 55
		self.w.LSB = vanilla.CheckBox((xPos, linePos, 40, 18), "LSB", value=True, sizeStyle='small', callback=self.SavePreferences)
		xPos += 44
		self.w.RSB = vanilla.CheckBox((xPos, linePos, 50, 18), "RSB by", value=True, sizeStyle='small', callback=self.SavePreferences)
		xPos += 57
		self.w.changeValue = vanilla.EditText((xPos, linePos - 1, 55, 20), "+10.0", sizeStyle='small')
		xPos += 56
		self.w.text_3 = vanilla.TextBox((xPos, linePos + 2, 17, 14), "%", sizeStyle='small')
		xPos += 20
		self.w.revertButton = vanilla.Button((xPos, linePos, 60, 19), "⟲ Revert", sizeStyle='small', callback=self.ChangeMetricsbyPercentageMain)
		xPos += 66
		self.w.runButton = vanilla.Button((xPos, linePos, 60, 19), "Change", sizeStyle='small', callback=self.ChangeMetricsbyPercentageMain)

		self.w.setDefaultButton(self.w.runButton)

		self.LoadPreferences()

		self.w.open()
		self.w.makeKey()

	def findGlyphsThatReferenceGlyphAsComponent(self, glyph):
		Font = Glyphs.font
		glyphs = []
		for g in Font.glyphs:
			if g != glyph and glyph.name in [c.componentName for c in g.layers[0].components]:
				glyphs.append(g)
		return glyphs

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

				layer_id = thisLayer.layerId
				if len(thisLayer.paths) > 0 or len(thisLayer.components) > 0:
					if changeLSB:

						LSB_change = (thisLayer.LSB * change) - thisLayer.LSB

						thisLayer.LSB *= change

						# counteract movement in glyphs that reference this glyph as a component:
						for g in self.findGlyphsThatReferenceGlyphAsComponent(thisLayer.parent):
							for c in g.layers[layer_id].components:
								if c.componentName == thisLayer.parent.name:

									# if component is rotated or mirrored, we need to reverse the LSB change
									if c.transform[0] < 0 or c.transform[3] < 0:
										c.position = (c.position[0] + LSB_change, c.position[1])

									# otherwise, we can just offset the LSB change directly
									else:
										c.position = (c.position[0] - LSB_change, c.position[1])


					if changeRSB:
						thisLayer.RSB *= change

			self.SavePreferences()

			# self.w.close()
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(" Error: %s" % e)


ChangeMetricsbyPercentage()
