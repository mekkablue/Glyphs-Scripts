# MenuTitle: Grid Switcher
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Toggles grid between two gridstep values.
"""

import vanilla
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class Gridswitch(mekkaObject):
	prefDict = {
		"grid1": 1,
		"grid2": 0,
	}

	def __init__(self):
		self.gridStep1default = 1
		self.gridStep2default = 0

		currentGridStep = Glyphs.font.gridMain()
		self.w = vanilla.FloatingWindow((170, 100), "Grid Switcher", autosaveName=self.domain("mainwindow"))
		self.w.grid1 = vanilla.EditText((15, 12, 65, 15 + 3), "1", sizeStyle='small')
		self.w.grid2 = vanilla.EditText((-80, 12, -15, 15 + 3), "50", sizeStyle='small')
		self.w.currentGridStep = vanilla.TextBox((15, 38, -15, 22), "Current Grid Step: %i" % currentGridStep, sizeStyle='regular')
		self.w.switchButton = vanilla.Button((15, -22 - 15, -15, -15), "Switch Grid", sizeStyle='regular', callback=self.GridOnOffMain)
		self.w.setDefaultButton(self.w.switchButton)

		self.w.center()
		self.w.open()
		self.w.makeKey()

		# Load Settings:
		self.LoadPreferences()

	def GridOnOffMain(self, sender):
		try:
			self.SavePreferences()

			try:
				gridStep1 = int(Glyphs.defaults["com.mekkablue.gridswitch.grid1"])
			except:
				gridStep1 = self.gridStep1default
				self.w.grid1.set(gridStep1)

			try:
				gridStep2 = int(Glyphs.defaults["com.mekkablue.gridswitch.grid2"])
			except:
				gridStep2 = self.gridStep2default
				self.w.grid2.set(gridStep2)

			gridStep = Glyphs.font.gridMain()
			if gridStep != gridStep1:
				newGridStep = gridStep1
			else:
				newGridStep = gridStep2

			Glyphs.font.setGridMain_(newGridStep)
			self.w.currentGridStep.set("Current Grid Step: %i" % newGridStep)

		except Exception as e:
			raise e


Gridswitch()
