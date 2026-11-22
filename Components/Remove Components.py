# MenuTitle: Remove Components
__doc__ = """
Removes the specified component (and corner component) from the glyphs and layers in the chosen scope, with a prediction of how many will be removed.
"""
import vanilla
from AppKit import (
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)
from GlyphsApp import Glyphs
from mekkablue import mekkaObject, match, UpdateButton, makeWindowResizable


scopeOptions = (
	"selected glyphs",
	"all masters of selected glyphs",
	"⚠️ complete current master",
	"⚠️ complete font",
	"⚠️ all open fonts",
)


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
	return count


class RemoveComponentfromSelectedGlyphs(mekkaObject):
	prefDict = {
		"componentName": "a",
		"scope": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 380
		windowMinWidth = 340
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Remove Components",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		self.w.textDescription = vanilla.TextBox("auto", "Remove component", sizeStyle='small')
		self.w.componentName = vanilla.ComboBox("auto", self.glyphList(), callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Pick a glyph name. All components and corner components referencing this glyph will be deleted. Wildcards * and ? are supported."
		self.w.textDescription.setToolTip(tooltip)
		self.w.componentName.setToolTip(tooltip)

		self.w.updateButton = UpdateButton("auto", callback=self.updateComponents)
		self.w.updateButton.setToolTip("Reload a list of glyph names based on the current font (and selection).")

		self.w.scopeLabel = vanilla.TextBox("auto", "Remove in:", sizeStyle="small")
		self.w.scope = vanilla.PopUpButton("auto", scopeOptions, callback=self.SavePreferences, sizeStyle="small")
		scopeTooltip = (
			"Determines which glyphs and layers are affected:\n"
			"• Selected glyphs – current master layer of each selected glyph.\n"
			"• All masters of selected glyphs – all layers of each selected glyph.\n"
			"• ⚠️ Complete current master – all glyphs in the font, current master only.\n"
			"• ⚠️ Complete font – all glyphs in the font, all masters.\n"
			"• ⚠️ All open fonts – all glyphs in every open font, all masters."
		)
		self.w.scopeLabel.setToolTip(scopeTooltip)
		self.w.scope.setToolTip(scopeTooltip)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Remove", callback=self.RemoveComponentFromSelectedGlyphsMain)
		self.w.runButton.setToolTip("Removes the component from the chosen glyphs.")
		self.w.setDefaultButton(self.w.runButton)

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Predicts how many components will be removed, then shows the progress and the result of the run.")
		nsStatus = self.w.status.getNSTextField()
		nsStatus.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		nsStatus.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		# the run button stays as wide as its title needs:
		self.w.runButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# the labels are right-aligned and hug their text, so the combo box and the popup take the leftover width:
		for label in (self.w.textDescription, self.w.scopeLabel):
			nsLabel = label.getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# the window is as tall as the content needs
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[textDescription]-gap-[componentName]-gap-[updateButton]-inset-|",
				"H:|-inset-[scopeLabel]-gap-[scope]-inset-|",
				"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[componentName]-row-[scope]-inset-[runButton]-inset-|",
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.textDescription, "attribute1": "centerY", "view2": self.w.componentName, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.componentName, "attribute2": "centerY"},
				{"view1": self.w.scopeLabel, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
				{"view1": self.w.scopeLabel, "attribute1": "width", "view2": self.w.textDescription, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8},
		)

		makeWindowResizable(self.w, minSize=(windowMinWidth, 0))  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()

		self.w.makeKey()

	def updateComponents(self, sender=None):
		glyphList = self.glyphList()
		if glyphList:
			self.w.componentName.setItems(glyphList)
		self.updateUI()

	def updateUI(self, sender=None):
		self.setStatus(self.predictionText())

	def scopeFonts(self):
		"""The fonts the scope applies to."""
		if self.prefInt("scope") == 4:
			return list(Glyphs.fonts)
		return [Glyphs.font] if Glyphs.font else []

	def glyphsAndLayerScope(self, font):
		"""Returns (glyphs, layerScope) for a font, where layerScope is a master ID or 'all'."""
		scope = self.prefInt("scope")
		masterId = font.selectedFontMaster.id
		if scope in (0, 1):
			glyphs = list(dict.fromkeys(layer.parent for layer in font.selectedLayers if layer.parent))
			return glyphs, (masterId if scope == 0 else "all")
		elif scope == 2:
			return list(font.glyphs), masterId
		return list(font.glyphs), "all"  # complete font and all open fonts

	def layersForGlyph(self, glyph, layerScope):
		"""Returns the layers of a glyph that are in the layer scope."""
		if layerScope == "all":
			return list(glyph.layers)
		return [layer for layer in glyph.layers if layer.associatedMasterId == layerScope]

	def countComponentsInLayer(self, componentName, layer):
		count = sum(1 for component in layer.components if match(componentName, component.componentName))
		count += sum(1 for hint in layer.hints if hint.isCorner and match(componentName, hint.name))
		return count

	def predictionText(self):
		fonts = self.scopeFonts()
		if not fonts:
			return "⚠️ No font open."
		componentName = self.pref("componentName")
		if not componentName:
			return "🤖 Ready."
		componentCount = 0
		glyphCount = 0
		for font in fonts:
			glyphs, layerScope = self.glyphsAndLayerScope(font)
			for glyph in glyphs:
				countInGlyph = sum(self.countComponentsInLayer(componentName, layer) for layer in self.layersForGlyph(glyph, layerScope))
				if countInGlyph:
					componentCount += countInGlyph
					glyphCount += 1
		return "🔮 Will remove %i component%s from %i glyph%s." % (
			componentCount,
			"" if componentCount == 1 else "s",
			glyphCount,
			"" if glyphCount == 1 else "s",
		)

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
			if self.prefInt("scope") in (0, 1) and thisFont.selectedLayers:
				return sorted(self.componentsInGlyphs([layer.parent for layer in thisFont.selectedLayers if layer.parent]))
			elif self.prefInt("scope") == 4:
				return sorted(set(component for font in Glyphs.fonts for component in self.componentsInGlyphs(font.glyphs)))
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

		removedCorners = deleteCornerComponent(componentName, thisLayer)
		return len(removedComponents) + removedCorners

	def removeComponentFromGlyph(self, componentName, thisGlyph, layerScope="all"):
		"""Removes the components from the layers in the layer scope. Returns the number of removed components."""
		print("🔠 %s" % thisGlyph.name)
		removedCount = 0
		for thisLayer in self.layersForGlyph(thisGlyph, layerScope):
			removedCount += self.removeComponentFromLayer(componentName, thisLayer)
		return removedCount

	def RemoveComponentFromSelectedGlyphsMain(self, sender):
		# brings macro window to front and clears its log:
		Glyphs.clearLog()

		thisGlyph = None
		try:
			fonts = self.scopeFonts()  # frontmost font, or all open fonts
			if not fonts:
				self.setStatus("⚠️ No font open.")
				return
			componentName = self.pref("componentName")

			removedCount = 0
			affectedGlyphCount = 0
			glyphCount = 0
			for thisFont in fonts:
				print("Removing component %s from font ‘%s’:" % (componentName, thisFont.familyName))
				listOfGlyphs, layerScope = self.glyphsAndLayerScope(thisFont)
				glyphCount += len(listOfGlyphs)
				self.setStatus("🛠️ Processing %i glyph%s…" % (len(listOfGlyphs), "" if len(listOfGlyphs) == 1 else "s"))
				for thisGlyph in listOfGlyphs:
					self.setStatus("🔠 %s" % thisGlyph.name)
					removedInGlyph = self.removeComponentFromGlyph(componentName, thisGlyph, layerScope)
					if removedInGlyph:
						removedCount += removedInGlyph
						affectedGlyphCount += 1

			self.SavePreferences()
			self.setStatus("✅ Removed %i component%s from %i glyph%s." % (
				removedCount,
				"" if removedCount == 1 else "s",
				affectedGlyphCount,
				"" if affectedGlyphCount == 1 else "s",
			))

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Component Error: %s" % e)
			self.setStatus("❌ Error at %s. Details in Macro Window." % (thisGlyph.name if thisGlyph else "start"))


RemoveComponentfromSelectedGlyphs()
