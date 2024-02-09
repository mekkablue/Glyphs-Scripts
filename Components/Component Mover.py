# MenuTitle: Component Mover
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Batch edit (smart) components across selected glyphs. Change positions, scales and smart properties.
"""

import vanilla
from AppKit import NSPoint
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


class ComponentMover(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"changeAttribute": 0,
		"searchString": "",
		"allMasters": False,
		"amount": 10,
		"breakAlignment": False,
	}
	defaultSettings = ["Position", "Scale"]

	def __init__(self):
		# Window 'self.w':
		windowWidth = 270
		windowHeight = 220
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Component Mover",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 25

		self.w.changeAttributeText = vanilla.TextBox((inset, linePos + 2, 50, 14), "Change", sizeStyle='small', selectable=True)
		self.w.changeAttributeText.getNSTextField().setAlignment_(2)
		self.w.changeAttribute = vanilla.PopUpButton((inset + 55, linePos - 1, -inset - 25, 20), self.defaultSettings + self.availableAttributes(), sizeStyle='small', callback=self.SavePreferences)
		self.w.changeAttributeUpdate = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.updateUI)
		linePos += lineHeight

		self.w.searchStringText = vanilla.TextBox((inset, linePos + 2, 50, 14), "for", sizeStyle='small', selectable=True)
		self.w.searchStringText.getNSTextField().setAlignment_(2)
		self.w.searchString = vanilla.ComboBox((inset + 55, linePos - 2, -inset - 25, 20), self.availableComponents(), sizeStyle='small', callback=self.SavePreferences)
		self.w.searchString.getNSComboBox().setPlaceholderString_("any component")
		self.w.searchStringUpdate = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.updateUI)
		linePos += int(lineHeight * 1.2)

		size, offset = 50, 60
		self.w.upLeft = vanilla.SquareButton((inset + offset, linePos, size - 1, lineHeight - 1), "↖", sizeStyle='regular', callback=self.ComponentMoverMain)
		self.w.up = vanilla.SquareButton((inset + offset + size, linePos, size - 1, lineHeight - 1), "↑", sizeStyle='regular', callback=self.ComponentMoverMain)
		self.w.upRight = vanilla.SquareButton((inset + offset + size * 2, linePos, size - 1, lineHeight - 1), "↗", sizeStyle='regular', callback=self.ComponentMoverMain)
		linePos += lineHeight

		self.w.left = vanilla.SquareButton((inset + offset, linePos, size - 1, lineHeight - 1), "←", sizeStyle='regular', callback=self.ComponentMoverMain)
		self.w.amount = vanilla.EditText((inset + offset + size, linePos, size - 1, lineHeight - 1), "10", sizeStyle='regular', callback=self.SavePreferences)
		self.w.amount.getNSTextField().setAlignment_(1)
		self.w.right = vanilla.SquareButton((inset + offset + size * 2, linePos, size - 1, lineHeight - 1), "→", sizeStyle='regular', callback=self.ComponentMoverMain)
		linePos += lineHeight

		self.w.downLeft = vanilla.SquareButton((inset + offset, linePos, size - 1, lineHeight - 1), "↙", sizeStyle='regular', callback=self.ComponentMoverMain)
		self.w.down = vanilla.SquareButton((inset + offset + size, linePos, size - 1, lineHeight - 1), "↓", sizeStyle='regular', callback=self.ComponentMoverMain)
		self.w.downRight = vanilla.SquareButton((inset + offset + size * 2, linePos, size - 1, lineHeight - 1), "↘", sizeStyle='regular', callback=self.ComponentMoverMain)
		linePos += int(lineHeight * 1.5)
		
		lineHeight = 20
		self.w.breakAlignment = vanilla.CheckBox((inset + offset, linePos - 1, -inset, 20), "Break alignment if necessary", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.allMasters = vanilla.CheckBox((inset + offset, linePos - 1, -inset, 20), "Apply to all masters", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		if sender is self.w.changeAttributeUpdate:
			self.w.changeAttribute.setItems(self.defaultSettings + self.availableAttributes())
			self.SavePreferences()
		if sender is self.w.searchStringUpdate:
			self.w.searchString.setItems(self.availableComponents())
			self.SavePreferences()
		
		moveOrScale = self.pref("changeAttribute") < 2
		self.w.up.enable(moveOrScale)
		self.w.down.enable(moveOrScale)
		self.w.upLeft.setTitle("↖" if moveOrScale else "←×10")
		self.w.upRight.setTitle("↗" if moveOrScale else "→×10")
		self.w.downLeft.setTitle("↙" if moveOrScale else "←÷10")
		self.w.downRight.setTitle("↘" if moveOrScale else "→÷10")
		
		self.w.breakAlignment.enable(self.pref("changeAttribute") == 0)

	def availableAttributes(self):
		searchString = self.pref("searchString")
		componentValues = []
		font = Glyphs.font
		if font:
			layers = font.selectedLayers
			if layers:
				glyphs = [layer.parent for layer in layers]
				for glyph in glyphs:
					for thisLayer in glyph.layers:
						if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
							for component in thisLayer.components:
								if not searchString or (searchString != "" and searchString in component.componentName):
									originalGlyph = component.componentLayer.parent
									if originalGlyph.smartComponentAxes:
										for axis in originalGlyph.smartComponentAxes:
											if axis.name not in componentValues:
												componentValues.append(axis.name)
		return componentValues

	def availableComponents(self, sender=None):
		components = []
		font = Glyphs.font
		if font:
			layers = font.selectedLayers
			if layers:
				glyphs = [layer.parent for layer in layers]
				for glyph in glyphs:
					for thisLayer in glyph.layers:
						if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
							for component in thisLayer.components:
								if component.name not in components:
									components.append(component.name)
		return components

	def getSmartAxisID(self, component, axisName):
		glyph = component.glyph
		font = glyph.parent
		compName = component.componentName
		baseGlyph = font.glyphs[compName]
		if baseGlyph:
			axis = baseGlyph.smartComponentAxes[axisName]
			if axis:
				return axis.id
		return None

	def ComponentMoverMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				if self.prefBool("allMasters"):
					allLayers = []
					for glyph in [layer.parent for layer in thisFont.selectedLayers]:
						for layer in glyph.layers:
							if layer.isMasterLayer or layer.isSpecialLayer:
								allLayers.append(layer)
				else:
					allLayers = thisFont.selectedLayers
				
				breakAlignment = self.prefBool("breakAlignment")
				changeAttribute = self.prefInt("changeAttribute")
				smartComponent = changeAttribute > 1  # 0=Position, 1=Scale
				attributeToChange = self.w.changeAttribute.getItems()[changeAttribute]
				if smartComponent:
					if sender is self.w.left:
						factor = -1
					elif sender is self.w.right:
						factor = 1
					elif sender is self.w.upLeft:
						factor = -10
					elif sender is self.w.upRight:
						factor = 10
					elif sender is self.w.downLeft:
						factor = -0.1
					elif sender is self.w.downRight:
						factor = 0.1
				else:
					factorX, factorY = 0, 0
					if sender in (self.w.left, self.w.upLeft, self.w.downLeft):
						factorX = -1
					if sender in (self.w.right, self.w.upRight, self.w.downRight):
						factorX = 1
					if sender in (self.w.up, self.w.upLeft, self.w.upRight):
						factorY = 1
					if sender in (self.w.down, self.w.downLeft, self.w.downRight):
						factorY = -1

				amount = self.prefFloat("amount")  # don't know why reading of prefs does not work here
				for thisLayer in allLayers:
					for thisComponent in thisLayer.components:
						searchString = self.pref("searchString")
						if not searchString or searchString in thisComponent.componentName:
							if smartComponent:
								try:
									axisID = self.getSmartAxisID(thisComponent, attributeToChange)
									originalGlyph = thisComponent.component
									originalLayer = thisComponent.componentLayer
									
									# check if it is a smart component that has not been touched yet, and initiate it:
									if thisComponent.smartComponentValues[axisID] is None and originalGlyph.isSmartGlyph():
										for originalAxis in originalGlyph.smartComponentAxes:
											poles = (None, originalAxis.bottomValue, originalAxis.topValue)
											index = originalLayer.smartComponentPoleMapping[originalAxis.id]
											originalSmartValue = poles[index]
											thisComponent.smartComponentValues[originalAxis.id] = originalSmartValue
											
									if thisComponent.smartComponentValues[attributeToChange] is not None:
										thisComponent.smartComponentValues[attributeToChange] += amount * factor
									# should work with axisName, circumventing bug in 3.2 (3198):
									elif thisComponent.smartComponentValues[axisID] is not None:
										thisComponent.smartComponentValues[axisID] += amount * factor
									else:
										print(f"⚠️ {thisLayer.parent.name}: {thisComponent.name} has no property ‘{attributeToChange}’.")
								except:
									import traceback
									print(traceback.format_exc())
									pass  # tried to change a non-existing attribute
							elif attributeToChange == "Position":
								if thisComponent.doesAlign() and breakAlignment:
									thisComponent.makeDisableAlignment()
								thisComponent.x += factorX * amount
								thisComponent.y += factorY * amount
							elif attributeToChange == "Scale":
								percentage = amount / 100.0
								scaleX = thisComponent.scale.x + factorX * percentage
								scaleY = thisComponent.scale.y + factorY * percentage
								thisComponent.scale = NSPoint(scaleX, scaleY)

				if thisFont.currentTab:
					thisFont.currentTab.redraw()
					# NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisFont.currentTab)
				else:
					thisFont.fontView.redraw()
					# NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisFont.fontView)
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Component Mover Error: %s" % e)
			import traceback
			print(traceback.format_exc())


ComponentMover()
