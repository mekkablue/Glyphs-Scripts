# MenuTitle: Set Label Colors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Override the label colors for glyphs and layers.
"""

import vanilla
from Foundation import NSColor, NSArchiver, NSUnarchiver, NSMutableArray
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


class SetLabelColors(mekkaObject):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 210
		windowHeight = 356
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Set Glyph Label Colors",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 8, 15, 22

		self.w.redText = vanilla.TextBox((inset + 21, linePos, 35, 19), "R", selectable=False)
		self.w.greenText = vanilla.TextBox((inset + 61, linePos, 35, 19), "G", selectable=False)
		self.w.blueText = vanilla.TextBox((inset + 101, linePos, 35, 19), "B", selectable=False)
		self.w.alphaText = vanilla.TextBox((inset + 141, linePos, 35, 19), "A", selectable=False)
		linePos += 19

		self.w.color01 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red01 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.green01 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.blue01 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.alpha01 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		linePos += lineHeight

		self.w.color02 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red02 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.green02 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.blue02 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.alpha02 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		linePos += lineHeight

		self.w.color03 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red03 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.green03 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.blue03 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.alpha03 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		linePos += lineHeight

		self.w.color04 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red04 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.green04 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.blue04 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.alpha04 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		linePos += lineHeight

		self.w.color05 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red05 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.green05 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.blue05 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.alpha05 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		linePos += lineHeight

		self.w.color06 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red06 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.green06 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.blue06 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.alpha06 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		linePos += lineHeight

		self.w.color07 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red07 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.green07 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.blue07 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.alpha07 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		linePos += lineHeight

		self.w.color08 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red08 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.green08 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.blue08 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.alpha08 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		linePos += lineHeight

		self.w.color09 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red09 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.green09 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.blue09 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.alpha09 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		linePos += lineHeight

		self.w.color10 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red10 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.green10 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.blue10 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.alpha10 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		linePos += lineHeight

		self.w.color11 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red11 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.green11 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.blue11 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.alpha11 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		linePos += lineHeight

		self.w.color12 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red12 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.green12 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.blue12 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		self.w.alpha12 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.textFieldAction)
		linePos += lineHeight + 2

		self.w.rAll = vanilla.SquareButton((inset + 20, linePos, 35, 16), "↑ ALL", sizeStyle='mini', callback=self.setAll)
		self.w.gAll = vanilla.SquareButton((inset + 60, linePos, 35, 16), "↑ ALL", sizeStyle='mini', callback=self.setAll)
		self.w.bAll = vanilla.SquareButton((inset + 100, linePos, 35, 16), "↑ ALL", sizeStyle='mini', callback=self.setAll)
		self.w.aAll = vanilla.SquareButton((inset + 140, linePos, 35, 16), "↑ ALL", sizeStyle='mini', callback=self.setAll)
		tooltip = "Type in a value in the LAST line and click this button to apply it to all lines."
		self.w.rAll.getNSButton().setToolTip_(tooltip)
		self.w.gAll.getNSButton().setToolTip_(tooltip)
		self.w.bAll.getNSButton().setToolTip_(tooltip)
		self.w.aAll.getNSButton().setToolTip_(tooltip)
		linePos += lineHeight

		# Run Button:
		# self.w.getButton = vanilla.Button( (-70-80*2-inset, -20-inset, -80*2-inset, -inset), "Current", sizeStyle='regular', callback=self.SetLabelColorsMain )
		self.w.resetButton = vanilla.Button((-70 - 80 - inset, -20 - inset, -80 - inset, -inset), "Reset", sizeStyle='regular', callback=self.resetColors)
		self.w.runButton = vanilla.Button((-70 - inset, -20 - inset, -inset, -inset), "Set", sizeStyle='regular', callback=self.SetLabelColorsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def resetColors(self, sender=None):
		Glyphs.defaults["LabelColors"] = None
		self.LoadPreferences()

	def currentlyStoredColors(self, sender=None):
		# reset to defaults if nothing stored:

		labelColorDatas = Glyphs.defaults["LabelColors"]
		if labelColorDatas:
			labelColors = []
			for colorData in labelColorDatas:
				color = NSUnarchiver.unarchiveObjectWithData_(colorData)
				labelColors.append(color)
		else:
			labelColors = [
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.85, 0.26, 0.06, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.99, 0.62, 0.11, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.65, 0.48, 0.20, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.97, 0.90, 0.00, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.67, 0.95, 0.38, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.04, 0.57, 0.04, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.06, 0.60, 0.98, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.00, 0.20, 0.88, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.50, 0.09, 0.79, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.98, 0.36, 0.67, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.75, 0.75, 0.75, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.25, 0.25, 0.25, 1.0),
			]
		return labelColors

	def setAll(self, sender=None):
		try:
			name = None
			if sender == self.w.rAll:
				name = "red"
			elif sender == self.w.gAll:
				name = "green"
			elif sender == self.w.bAll:
				name = "blue"
			elif sender == self.w.aAll:
				name = "alpha"

			if name:
				originalTextFieldName = "%s12" % name
				originalTextField = getattr(self.w, originalTextFieldName)
				originalValue = originalTextField.get()
				for i in range(1, 12):
					textFieldName = "%s%02i" % (name, i)
					textField = getattr(self.w, textFieldName)
					textField.set(originalValue)
		except:
			import traceback
			print(traceback.format_exc())

		self.updateColorDots()

	def textFieldAction(self, sender=None):
		self.updateColorDots()

	def updateColorDots(self):
		# sets the dots
		for i in range(12):
			color = "color%02i" % (i + 1)
			labelColor = self.labelColorFromUIAtIndex(i)
			print("__labelColor", labelColor)
			getattr(self.w, color).getNSTextField().setTextColor_(labelColor)

	def uiAttributeKeys(self, index):
		index += 1  # the labels start at 1
		color = "color%02i" % index
		r = "red%02i" % index
		g = "green%02i" % index
		b = "blue%02i" % index
		a = "alpha%02i" % index
		return color, r, g, b, a

	def labelColorFromUIAtIndex(self, idx):
		_, rName, gName, bName, aName = self.uiAttributeKeys(idx)
		color = NSColor.colorWithDeviceRed_green_blue_alpha_(
			min(1.0, abs(float(getattr(self.w, rName).get()))),
			min(1.0, abs(float(getattr(self.w, gName).get()))),
			min(1.0, abs(float(getattr(self.w, bName).get()))),
			min(1.0, abs(float(getattr(self.w, aName).get()))),
		)
		return color

	def labelColorArchivesFromUI(self):
		labelColors = NSMutableArray.new()
		for i in range(12):
			labelColor = self.labelColorFromUIAtIndex(i)
			colorData = NSArchiver.archivedDataWithRootObject_(labelColor)
			labelColors.addObject_(colorData)
		return labelColors

	def LoadPreferences(self):
		try:
			labelColors = self.currentlyStoredColors()
			for i, color in enumerate(labelColors):
				r = color.redComponent()
				g = color.greenComponent()
				b = color.blueComponent()
				a = color.alphaComponent()

				colorName, rName, gName, bName, aName = self.uiAttributeKeys(i)
				getattr(self.w, rName).set("%.2f" % r)
				getattr(self.w, gName).set("%.2f" % g)
				getattr(self.w, bName).set("%.2f" % b)
				getattr(self.w, aName).set("%.2f" % a)
				getattr(self.w, colorName).getNSTextField().setTextColor_(color)
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def SetLabelColorsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:

			Glyphs.defaults["LabelColors"] = self.labelColorArchivesFromUI()

			Message(title="New Label Colors Set", message="✅ The new label colors have been set.\n⚠️ Glyphs needs a restart for changes to take effect.", OKButton=None)
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Set Label Colors Error: %s" % e)
			import traceback
			print(traceback.format_exc())


SetLabelColors()
