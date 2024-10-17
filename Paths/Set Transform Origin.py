# MenuTitle: Set Transform Origin
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Sets origin point for Rotate tool.
"""

import vanilla
from Foundation import NSPoint, NSClassFromString
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class SetTransformOriginWindow(mekkaObject):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 360
		windowHeight = 42
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Set Transform Origin",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset = 10, 15
		xPos = inset
		self.w.text_1 = vanilla.TextBox((xPos, linePos + 3, 75, 16), "Origin")
		xPos += 45
		self.w.originX = vanilla.EditText((xPos, linePos, 75, 22), "0.0")
		xPos += 80
		self.w.originY = vanilla.EditText((xPos, linePos, 75, 22), "0.0")
		xPos += 80
		# Run Button:
		self.w.resetButton = vanilla.Button((xPos, linePos - 1, 60, 22), "Get", callback=self.GetTransformOrigin)
		xPos += 65
		self.w.runButton = vanilla.Button((xPos, linePos - 1, 60, 22), "Set", callback=self.SetTransformOriginMain)

		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.GetTransformOrigin(None):
			print("Note: 'Set Transform Origin' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def GetTransformOrigin(self, sender):
		try:
			myController = Glyphs.currentDocument.windowController()
			rotateToolClass = NSClassFromString("GlyphsToolRotate")
			myRotateTool = myController.toolForClass_(rotateToolClass)
			currentOrigin = myRotateTool.transformOrigin()

			self.w.originX.set(currentOrigin.x)
			self.w.originY.set(currentOrigin.y)
		except:
			return False

		return True

	def SetTransformOriginMain(self, sender):
		try:
			newOriginX = float(self.w.originX.get())
			newOriginY = float(self.w.originY.get())
			newOriginPoint = NSPoint(newOriginX, newOriginY)

			myController = Glyphs.currentDocument.windowController()
			myController.graphicView().setNeedsDisplay_(False)

			rotateToolClass = NSClassFromString("GlyphsToolRotate")
			myRotateTool = myController.toolForClass_(rotateToolClass)
			myRotateTool.setTransformOrigin_(newOriginPoint)

			myController.graphicView().setNeedsDisplay_(True)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Set Transform Origin Error: %s" % e)


SetTransformOriginWindow()
