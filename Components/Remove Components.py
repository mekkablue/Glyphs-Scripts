#MenuTitle: Remove Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Removes the specified component from all (selected) glyphs.
"""

import vanilla, os, sys

# import from enclosing folder:
sys.path.insert(1, os.path.realpath(os.path.pardir))
from mekkablue import match

def deleteCornerComponent(componentName, thisLayer):
	indToDel = []
	count = 0
	for i, h in enumerate(thisLayer.hints):
		if h.isCorner:
			#help(h)
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

class RemoveComponentfromSelectedGlyphs(object):
	prefID = "com.mekkablue.RemoveComponents"

	def __init__(self):
		# Window 'self.w':
		windowWidth = 250
		windowHeight = 135
		windowWidthResize = 500 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Remove Components", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName=self.domain("mainwindow") # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.textDescription = vanilla.TextBox((inset, linePos, 115, 14), "Remove component", sizeStyle='small')
		self.w.componentName = vanilla.ComboBox((inset + 115, linePos - 3, -30 - inset, 19), self.glyphList(), sizeStyle='small')
		tooltip = "Pick a glyph name. All components and corner components referencing this glyph will be deleted. Wildcards * and ? are supported."
		self.w.textDescription.getNSTextField().setToolTip_(tooltip)
		self.w.componentName.getNSComboBox().setToolTip_(tooltip)

		self.w.updateButton = vanilla.SquareButton((-inset - 20, linePos - 2, -inset, 18), "↺", sizeStyle='small', callback=self.updateUI)
		self.w.updateButton.getNSButton().setToolTip_("Reload a list of glyph names based on the current font (and selection).")

		linePos += lineHeight
		self.w.fromWhere = vanilla.RadioGroup(
			(inset, linePos, -inset, 40),
			("from all selected glyphs", "⚠️ from all glyphs in the font"),
			callback=self.SavePreferences,
			sizeStyle='small',
			)

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Remove", sizeStyle='regular', callback=self.RemoveComponentFromSelectedGlyphsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Remove Component from Selected Glyphs' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()

	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]

	def updateUI(self, sender=None):
		glyphList = self.glyphList()
		if glyphList:
			self.w.componentName.setItems(glyphList)

	def SavePreferences(self, sender):
		try:
			Glyphs.defaults[self.domain("componentName")] = self.w.componentName.get()
			Glyphs.defaults[self.domain("fromWhere")] = self.w.fromWhere.get()
		except:
			return False

		return True

	def LoadPreferences(self):
		try:
			Glyphs.registerDefault(self.domain("componentName"), "a")
			Glyphs.registerDefault(self.domain("fromWhere"), "0")
			self.w.componentName.set(self.pref("componentName"))
			self.w.fromWhere.set(self.pref("fromWhere"))
		except:
			return False

		return True

	def componentsInGlyph(self, glyph):
		components = []
		for layer in glyph.layers:
			if layer.isMasterLayer or layer.isSpecialLayer:
				for component in layer.components:
					name = component.componentName
					if not name in components:
						components.append(name)
				for hint in layer.hints: # corner components
					if hint.name and not hint.name in components:
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
				return sorted(self.componentsInGlyphs([l.parent for l in thisFont.selectedLayers if l.parent]))
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
			thisFont = Glyphs.font # frontmost font
			componentName = self.pref("componentName")
			print("Removing component %s from font ‘%s’:" % (componentName, thisFont.familyName))

			if self.pref("fromWhere") == 0:
				listOfGlyphs = [l.parent for l in thisFont.selectedLayers] # active layers of currently selected glyphs
			else:
				listOfGlyphs = thisFont.glyphs

			for thisGlyph in listOfGlyphs:
				self.removeComponentFromGlyph(componentName, thisGlyph)

			if not self.SavePreferences(self):
				print("Note: 'Remove Component from Selected Glyphs' could not write preferences.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Component Error: %s" % e)

RemoveComponentfromSelectedGlyphs()
