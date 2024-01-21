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
		windowHeight = 380
		windowWidthResize = 0  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Set Glyph Label Colors",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.redText = vanilla.TextBox((inset + 20, linePos, 35, 19), "R", sizeStyle='small', selectable=False)
		self.w.greenText = vanilla.TextBox((inset + 60, linePos, 35, 19), "G", sizeStyle='small', selectable=False)
		self.w.blueText = vanilla.TextBox((inset + 100, linePos, 35, 19), "B", sizeStyle='small', selectable=False)
		self.w.alphaText = vanilla.TextBox((inset + 140, linePos, 35, 19), "A", sizeStyle='small', selectable=False)
		linePos += lineHeight

		self.w.color01 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red01 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green01 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue01 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha01 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color02 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red02 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green02 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue02 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha02 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color03 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red03 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green03 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue03 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha03 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color04 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red04 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green04 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue04 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha04 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color05 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red05 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green05 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue05 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha05 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color06 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red06 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green06 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue06 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha06 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color07 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red07 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green07 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue07 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha07 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color08 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red08 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green08 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue08 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha08 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color09 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red09 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green09 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue09 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha09 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color10 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red10 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green10 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue10 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha10 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color11 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red11 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green11 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue11 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha11 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color12 = vanilla.TextBox((inset - 1, linePos + 2, 14, 14), "◼︎", sizeStyle='small')
		self.w.red12 = vanilla.EditText((inset + 20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green12 = vanilla.EditText((inset + 60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue12 = vanilla.EditText((inset + 100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha12 = vanilla.EditText((inset + 140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

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

		self.setTextColors()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def resetColors(self, sender=None):
		labelColors = NSMutableArray.alloc().initWithArray_(
			[
				NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.85, 0.26, 0.06, 0.5)),
				NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.99, 0.62, 0.11, 0.5)),
				NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.65, 0.48, 0.20, 0.5)),
				NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.97, 0.90, 0.00, 0.5)),
				NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.67, 0.95, 0.38, 0.5)),
				NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.04, 0.57, 0.04, 0.5)),
				NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.06, 0.60, 0.98, 0.5)),
				NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.00, 0.20, 0.88, 0.5)),
				NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.50, 0.09, 0.79, 0.5)),
				NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.98, 0.36, 0.67, 0.5)),
				NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.75, 0.75, 0.75, 0.5)),
				NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.25, 0.25, 0.25, 0.5)),
			]
		)
		Glyphs.defaults["LabelColors"] = labelColors
		self.LoadPreferences()
		self.setTextColors()

	def currentlyStoredColors(self, sender=None):
		# reset to defaults if nothing stored:
		if not Glyphs.defaults["LabelColors"]:
			self.resetColors()

		labelColorDatas = Glyphs.defaults["LabelColors"]
		newLabelColors = NSMutableArray.new()
		for colorData in labelColorDatas:
			color = NSUnarchiver.unarchiveObjectWithData_(colorData)
			newLabelColors.addObject_(color)

		# labelColors = NSMutableArray.alloc().initWithArray_([
		# 	NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(*rgba)) for rgba in newLabelColors
		# 	])

		return newLabelColors

	def setAll(self, sender=None):
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

		self.SavePreferences()

	def setTextColors(self, sender=None):
		# sets the dots
		for i in range(1, 13):
			color = "color%02i" % i
			r = "red%02i" % i
			g = "green%02i" % i
			b = "blue%02i" % i
			a = "alpha%02i" % i
			getattr(self.w, color).getNSTextField().setTextColor_(
				NSColor.colorWithRed_green_blue_alpha_(
					float(getattr(self.w, r).get()),
					float(getattr(self.w, g).get()),
					float(getattr(self.w, b).get()),
					float(getattr(self.w, a).get()),
				)
			)

	def colorRGBAstrings(self, index):
		color = "color%02i" % index
		r = "red%02i" % index
		g = "green%02i" % index
		b = "blue%02i" % index
		a = "alpha%02i" % index
		return color, r, g, b, a

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			labelColors = NSMutableArray.alloc().init()
			for i in range(1, 13):
				color, r, g, b, a = self.colorRGBAstrings(i)
				colorData = NSArchiver.archivedDataWithRootObject_(
					NSColor.colorWithDeviceRed_green_blue_alpha_(
						min(1.0, abs(float(getattr(self.w, r).get()))),
						min(1.0, abs(float(getattr(self.w, g).get()))),
						min(1.0, abs(float(getattr(self.w, b).get()))),
						min(1.0, abs(float(getattr(self.w, a).get()))),
					)
				)
				labelColors.addObject_(colorData)

			self.setTextColors()
			return labelColors
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			# register defaults:
			labelColors = self.currentlyStoredColors()
			for i, colorDef in enumerate(labelColors):
				r = colorDef.redComponent()
				g = colorDef.greenComponent()
				b = colorDef.blueComponent()
				a = colorDef.alphaComponent()

				colorName, rName, gName, bName, aName = self.colorRGBAstrings(i + 1)
				getattr(self.w, rName).set("%.2f" % r)
				getattr(self.w, gName).set("%.2f" % g)
				getattr(self.w, bName).set("%.2f" % b)
				getattr(self.w, aName).set("%.2f" % a)

			self.setTextColors()
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
			if not self.SavePreferences():
				print("Error. Could not set colors.")
			else:
				Glyphs.defaults["LabelColors"] = self.SavePreferences()
				Message(title="New Label Colors Set", message="✅ The new label colors have been set.\n⚠️ Glyphs needs a restart for changes to take effect.", OKButton=None)
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Set Label Colors Error: %s" % e)
			import traceback
			print(traceback.format_exc())


SetLabelColors()
