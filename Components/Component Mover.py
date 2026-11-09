# MenuTitle: Component Mover
__doc__ = """
Batch edit (smart) components across selected glyphs. Change positions, scales and smart properties.
"""

import vanilla
from mekkablue import mekkaObject, UpdateButton, match
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSFont,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)
from Foundation import NSPoint


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
		windowWidth = 250
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Component Mover",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		buttonWidth, buttonHeight, gridGap = 60, 34, 2
		gridInset = round((windowWidth - buttonWidth * 3 - gridGap * 2) / 2.0)

		toolTip = "Pick the component attribute to change in all selected glyphs. Position and Size are available for all components. Smart axes will be listed here. Click the Update button to reset the menu for all smart axes for the current glyph selection."
		self.w.changeAttributeText = vanilla.TextBox("auto", "Change", sizeStyle="small", selectable=True)
		self.w.changeAttribute = vanilla.PopUpButton("auto", self.defaultSettings + self.availableAttributes(), sizeStyle="small", callback=self.SavePreferences)
		self.w.changeAttributeUpdate = UpdateButton("auto", callback=self.updateUI)
		self.w.changeAttributeText.setToolTip(toolTip)
		self.w.changeAttribute.setToolTip(toolTip)
		self.w.changeAttributeUpdate.setToolTip(toolTip)

		toolTip = "Pick the name of the component you want to manipulate in (all masters of) all selected glyphs. An empty entry means every component. You can use * and ? as wildcards. Click the Update button to populate the menu with the names of all components in all selected glyphs."
		self.w.searchStringText = vanilla.TextBox("auto", "for", sizeStyle="small", selectable=True)
		self.w.searchString = vanilla.ComboBox("auto", self.availableComponents(), sizeStyle="small", callback=self.SavePreferences)
		self.w.searchString.getNSComboBox().setPlaceholderString_("any component")
		self.w.searchStringUpdate = UpdateButton("auto", callback=self.updateUI)
		self.w.searchStringText.setToolTip(toolTip)
		self.w.searchString.setToolTip(toolTip)
		self.w.searchStringUpdate.setToolTip(toolTip)

		self.w.upLeft = vanilla.SquareButton("auto", "↖", callback=self.ComponentMoverMain)
		self.w.up = vanilla.SquareButton("auto", "↑", callback=self.ComponentMoverMain)
		self.w.upRight = vanilla.SquareButton("auto", "↗", callback=self.ComponentMoverMain)

		self.w.left = vanilla.SquareButton("auto", "←", callback=self.ComponentMoverMain)
		self.w.amount = vanilla.EditText("auto", "10", callback=self.SavePreferences)
		self.w.amount.setToolTip("Amount of the move (units), scale change (percent) or smart component axis change.")
		self.w.amount.getNSTextField().setUsesSingleLineMode_(1)
		self.w.amount.getNSTextField().setAlignment_(NSTextAlignmentRight)
		self.w.amount.getNSTextField().setFont_(NSFont.systemFontOfSize_(20))
		self.w.right = vanilla.SquareButton("auto", "→", callback=self.ComponentMoverMain)

		self.w.downLeft = vanilla.SquareButton("auto", "↙", callback=self.ComponentMoverMain)
		self.w.down = vanilla.SquareButton("auto", "↓", callback=self.ComponentMoverMain)
		self.w.downRight = vanilla.SquareButton("auto", "↘", callback=self.ComponentMoverMain)

		self.w.breakAlignment = vanilla.CheckBox("auto", "Break alignment if necessary", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.breakAlignment.setToolTip("Disables automatic alignment of a component before moving it.")
		self.w.allMasters = vanilla.CheckBox("auto", "Apply to all masters", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allMasters.setToolTip("Also change the components in the other masters (and special layers) of the selected glyphs.")

		# labels: right-aligned, same width
		labelNames = ("changeAttributeText", "searchStringText")
		widestLabel = "changeAttributeText"  # the label with the longest text
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		# checkboxes and square buttons stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		gridRows = (
			("upLeft", "up", "upRight"),
			("left", "amount", "right"),
			("downLeft", "down", "downRight"),
		)
		gridRules = []
		for leftName, centerName, rightName in gridRows:
			gridRules.append(f"H:|-gridInset-[{leftName}(buttonWidth)]-gridGap-[{centerName}(buttonWidth)]-gridGap-[{rightName}(buttonWidth)]-gridInset-|")
			for cellName in (leftName, centerName, rightName):
				gridRules.append(f"V:[{cellName}(buttonHeight)]")
			for cellName in (leftName, rightName):
				gridRules.append({"view1": getattr(self.w, cellName), "attribute1": "centerY", "view2": getattr(self.w, centerName), "attribute2": "centerY"})

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[changeAttributeText]-gap-[changeAttribute]-gap-[changeAttributeUpdate(20)]-inset-|",
				"H:|-inset-[searchStringText]-gap-[searchString]-gap-[searchStringUpdate(20)]-inset-|",
				"H:|-inset-[breakAlignment]-(>=inset)-|",
				"H:|-inset-[allMasters]-(>=inset)-|",
				"V:|-gap-[changeAttribute]-row-[searchString]-gridTop-[up]-gridGap-[amount]-gridGap-[down]-gridBottom-[breakAlignment]-checkRow-[allMasters]-inset-|",
				{"view1": self.w.changeAttributeText, "attribute1": "centerY", "view2": self.w.changeAttribute, "attribute2": "centerY"},
				{"view1": self.w.changeAttributeUpdate, "attribute1": "centerY", "view2": self.w.changeAttribute, "attribute2": "centerY"},
				{"view1": self.w.searchStringText, "attribute1": "centerY", "view2": self.w.searchString, "attribute2": "centerY"},
				{"view1": self.w.searchStringUpdate, "attribute1": "centerY", "view2": self.w.searchString, "attribute2": "centerY"},
			] + widthRules + gridRules,
			metrics={
				"inset": inset,
				"gap": 8,
				"row": 6,
				"checkRow": 5,
				"gridInset": gridInset,
				"gridGap": gridGap,
				"gridTop": 14,
				"gridBottom": 14,
				"buttonWidth": buttonWidth,
				"buttonHeight": buttonHeight,
			},
		)

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
						if not searchString or match(searchString, thisComponent.componentName):
							if smartComponent:
								try:
									axisID = self.getSmartAxisID(thisComponent, attributeToChange)
									if not axisID:
										continue

									originalGlyph = thisComponent.component
									originalLayer = thisComponent.componentLayer

									# check if it is a smart component that has not been touched yet, and initiate it:
									if thisComponent.smartComponentValues[axisID] is None and originalGlyph.isSmartGlyph():
										for originalAxis in originalGlyph.smartComponentAxes:
											poles = (None, originalAxis.bottomValue, originalAxis.topValue)
											index = originalLayer.smartComponentPoleMapping[originalAxis.id]
											originalSmartValue = poles[index]
											if originalSmartValue is not None:
												thisComponent.smartComponentValues[originalAxis.id] = float(originalSmartValue)

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
					thisFont.currentTab.reflow()
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
