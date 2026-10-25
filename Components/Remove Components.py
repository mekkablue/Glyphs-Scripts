# MenuTitle: Remove Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Removes the specified component from all (selected) glyphs.
"""
import vanilla
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSWindowStyleMaskResizable,
)
from Foundation import NSSize
from GlyphsApp import Glyphs
from mekkablue import mekkaObject, match, UpdateButton


def deleteCornerComponent(componentName, thisLayer):
	indToDel = []
	count = 0
	for i, h in enumerate(thisLayer.hints):
		if h.isCorner:
			# help(h)
			if match(componentName, h.name):
				indToDel += [i]
	indToDel = list(reversed(indToDel))
	for i in indToDel:
		del thisLayer.hints[i]
		count += 1

	if count:
		print("  ❌ Removed %i corner component%s from layer: %s" % (
			count,
			"" if count == 1 else "s",
			thisLayer.name,
		))


class RemoveComponentfromSelectedGlyphs(mekkaObject):
	prefDict = {
		"componentName": "a",
		"fromWhere": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 250
		windowMinWidth = 230
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Remove Components",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset = 15

		self.w.textDescription = vanilla.TextBox("auto", "Remove component", sizeStyle='small')
		self.w.componentName = vanilla.ComboBox("auto", self.glyphList(), sizeStyle='small')
		tooltip = "Pick a glyph name. All components and corner components referencing this glyph will be deleted. Wildcards * and ? are supported."
		self.w.textDescription.setToolTip(tooltip)
		self.w.componentName.setToolTip(tooltip)

		self.w.updateButton = UpdateButton("auto", callback=self.updateUI)
		self.w.updateButton.setToolTip("Reload a list of glyph names based on the current font (and selection).")

		self.w.fromWhere = vanilla.VerticalRadioGroup("auto", ("from all selected glyphs", "⚠️ from all glyphs in the font"), callback=self.SavePreferences, sizeStyle='small')

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Remove Component", callback=self.RemoveComponentFromSelectedGlyphsMain)
		self.w.setDefaultButton(self.w.runButton)

		# the label hugs its text, so the combo box takes the leftover width:
		nsLabel = self.w.textDescription.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# the window is as tall as the content needs
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[textDescription]-gap-[componentName]-gap-[updateButton]-inset-|",
				"H:|-inset-[fromWhere]-(>=inset)-|",
				"H:|-inset-[runButton]-inset-|",
				"V:|-inset-[componentName]-row-[fromWhere(radioHeight)]-row-[runButton]-inset-|",
				{"view1": self.w.textDescription, "attribute1": "centerY", "view2": self.w.componentName, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.componentName, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8, "radioHeight": self.w.fromWhere.getFittingHeight()},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()

		# resizable horizontally only: the height is dictated by the content
		window = self.w.getNSWindow()
		window.setStyleMask_(window.styleMask() | NSWindowStyleMaskResizable)
		contentSize = window.contentView().frame().size
		window.setContentMinSize_(NSSize(windowMinWidth, contentSize.height))
		window.setContentMaxSize_(NSSize(windowWidth + 500, contentSize.height))
		self.w.makeKey()

	def updateUI(self, sender=None):
		glyphList = self.glyphList()
		if glyphList:
			self.w.componentName.setItems(glyphList)

	def componentsInGlyph(self, glyph):
		components = []
		for layer in glyph.layers:
			if layer.isMasterLayer or layer.isSpecialLayer:
				for component in layer.components:
					name = component.componentName
					if name not in components:
						components.append(name)
				for hint in layer.hints:  # corner components
					if hint.name and hint.name not in components:
						components.append(hint.name)
		return components

	def componentsInGlyphs(self, glyphs):
		components = []
		for glyph in glyphs:
			components.extend(self.componentsInGlyph(glyph))
		return list(set(components))

	def glyphList(self):
		thisFont = Glyphs.font
		if thisFont:
			if self.pref("fromWhere") == 0 and thisFont.selectedLayers:
				return sorted(self.componentsInGlyphs([layer.parent for layer in thisFont.selectedLayers if layer.parent]))
			else:
				return sorted(self.componentsInGlyphs(thisFont.glyphs))
		else:
			return []

	def removeComponentFromLayer(self, componentName, thisLayer):
		theseComponents = thisLayer.components
		numberOfComponents = len(theseComponents)
		removedComponents = []
		if numberOfComponents > 0:
			for i in range(numberOfComponents)[::-1]:
				thisComponent = theseComponents[i]
				if match(componentName, thisComponent.componentName):
					if Glyphs.versionNumber >= 3:
						index = thisLayer.shapes.index(thisComponent)
						del (thisLayer.shapes[index])
						removedComponents.append(thisComponent.componentName)
					else:
						thisLayer.removeComponent_(thisComponent)

		if removedComponents:
			print(
				"  ❌ Removed %i component%s (%s) from layer: %s" % (
					len(removedComponents),
					"" if len(removedComponents) == 1 else "s",
					", ".join(set(removedComponents)),
					thisLayer.name,
				)
			)

		deleteCornerComponent(componentName, thisLayer)

	def removeComponentFromGlyph(self, componentName, thisGlyph):
		print("🔠 %s" % thisGlyph.name)
		for thisLayer in thisGlyph.layers:
			self.removeComponentFromLayer(componentName, thisLayer)

	def RemoveComponentFromSelectedGlyphsMain(self, sender):
		# brings macro window to front and clears its log:
		Glyphs.clearLog()

		try:
			thisFont = Glyphs.font  # frontmost font
			componentName = self.pref("componentName")
			print("Removing component %s from font ‘%s’:" % (componentName, thisFont.familyName))

			if self.pref("fromWhere") == 0:
				listOfGlyphs = [layer.parent for layer in thisFont.selectedLayers]  # active layers of currently selected glyphs
			else:
				listOfGlyphs = thisFont.glyphs

			for thisGlyph in listOfGlyphs:
				self.removeComponentFromGlyph(componentName, thisGlyph)

			self.SavePreferences()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Component Error: %s" % e)


RemoveComponentfromSelectedGlyphs()
