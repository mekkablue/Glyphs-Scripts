# MenuTitle: Component Problem Finder
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Find and report possible issues with components and corner components.
"""

import vanilla
from timeit import default_timer as timer
from GlyphsApp import Glyphs, Message, CORNER
from mekkablue import mekkaObject, camelCaseSplit, reportTimeInNaturalLanguage


def orthodoxComponentsForGlyph(thisGlyph):
	glyphInfo = thisGlyph.glyphInfo
	if glyphInfo:
		componentInfo = glyphInfo.components
		if componentInfo:
			glyphNameTuple = tuple(c.name for c in componentInfo)
			return glyphNameTuple
	return None


def nameStrippedOfSuffixes(glyphName):
	return glyphName[:glyphName.find(".") % (len(glyphName) + 1)]


def layerAdheresToStructure(thisLayer, glyphNameTuple):
	layerComponents = thisLayer.components
	numOfLayerComponents = len(layerComponents)
	if numOfLayerComponents != len(glyphNameTuple):
		return False
	for i in range(numOfLayerComponents):
		thisComponentName = thisLayer.components[i].componentName
		orthodoxComponentName = glyphNameTuple[i]
		if thisComponentName != orthodoxComponentName:
			componentBaseName = nameStrippedOfSuffixes(thisComponentName)
			orthodoxBaseName = nameStrippedOfSuffixes(orthodoxComponentName)
			if componentBaseName != orthodoxBaseName:
				return False
	return True


class ComponentProblemFinder(mekkaObject):
	prefDict = {
		"composablesWithoutComponents": False,
		"unusualComponents": False,
		"lockedComponents": False,
		"nestedComponents": False,
		"orphanedComponents": False,
		"emptyComponents": False,
		"unalignedComponents": False,
		"scaledComponents": False,
		"unproportionallyScaledComponents": False,
		"rotatedComponents": False,
		"mirroredComponents": False,
		"shiftedComponents": False,
		"detachedCornerComponents": False,
		"transformedCornerComponents": False,
		"includeAllGlyphs": False,
		"includeNonExporting": False,
		"reuseTab": False,
		"verbose": False,
	}
	prefs = (  # used to enable/disable UI
		"composablesWithoutComponents",
		"unusualComponents",
		"lockedComponents",
		"nestedComponents",
		"orphanedComponents",
		"emptyComponents",
		"unalignedComponents",
		"scaledComponents",
		"unproportionallyScaledComponents",
		"rotatedComponents",
		"mirroredComponents",
		"shiftedComponents",
		"detachedCornerComponents",
		"transformedCornerComponents",
	)

	def __init__(self):
		# Window 'self.w':
		windowWidth = 280
		windowHeight = 500
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Component Problem Finder",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "New tab with glyphs containing components:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.composablesWithoutComponents = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Composable glyphs without components", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.composablesWithoutComponents.getNSButton().setToolTip_("Lists glyphs that could be component-based (because they have a recipe in Glyph Info), but are lacking components.")
		linePos += lineHeight

		self.w.unusualComponents = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Unusual composites (or wrong order)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.unusualComponents.getNSButton().setToolTip_("Lists composite glyphs that contain components different from the default recipe in Glyph Info.")
		linePos += lineHeight

		self.w.lockedComponents = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Locked components", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.lockedComponents.getNSButton().setToolTip_("Lists glyphs that contain a locked component on any of its layers.")
		linePos += lineHeight

		self.w.nestedComponents = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Nested components", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.nestedComponents.getNSButton().setToolTip_("Lists glyphs that contain components, which in turn contain components.")
		linePos += lineHeight

		self.w.orphanedComponents = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Orphaned components", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.orphanedComponents.getNSButton().setToolTip_("Lists glyphs that contain components referencing glyphs that do not exist in the font (anymore).")
		linePos += lineHeight

		self.w.emptyComponents = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Empty components", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.emptyComponents.getNSButton().setToolTip_("Lists glyphs that contain components pointing to empty layers (layers without shapes).")
		linePos += lineHeight

		self.w.unalignedComponents = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Unaligned components", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.unalignedComponents.getNSButton().setToolTip_("Lists glyphs that contain unaligned components.")
		linePos += lineHeight

		# Line Separator:
		self.w.line_transformedComponents = vanilla.HorizontalLine((inset, linePos + 3, -inset, 1))
		linePos += int(lineHeight / 2)

		self.w.scaledComponents = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Scaled components", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.scaledComponents.getNSButton().setToolTip_("Lists all components that are not at their original size. Useful for bug tracing in variable fonts.")
		linePos += lineHeight

		self.w.unproportionallyScaledComponents = vanilla.CheckBox((inset * 2, linePos - 1, -inset, 20), "Only unproportionally scaled (h≠v)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.unproportionallyScaledComponents.getNSButton().setToolTip_("Lists glyphs that contain components that are not scaled the same horizontally and vertically. Useful for double checking in TT exports and variable fonts.")
		linePos += lineHeight

		self.w.rotatedComponents = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Rotated components", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.rotatedComponents.getNSButton().setToolTip_("Lists all glyphs that contain rotated components, or components that are flipped BOTH horizontally and vertically. May be a good idea to check their alignment.")
		linePos += lineHeight

		self.w.mirroredComponents = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Flipped components", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.mirroredComponents.getNSButton().setToolTip_("Lists all glyphs containing components that are mirrored EITHER horizontally or vertically.")
		linePos += lineHeight

		self.w.shiftedComponents = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Shifted (but undistorted) components", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.shiftedComponents.getNSButton().setToolTip_("Lists all glyphs containing unaligned components that are not positioned at x=0 y=0.")
		linePos += lineHeight

		# Line Separator:
		self.w.line_cornerComponents = vanilla.HorizontalLine((inset, linePos + 3, -inset, 1))
		linePos += int(lineHeight / 2)

		self.w.detachedCornerComponents = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Detached corner components", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.detachedCornerComponents.getNSButton().setToolTip_("Lists all glyphs containing corner components that have lost their connection point.")
		linePos += lineHeight

		self.w.transformedCornerComponents = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Transformed corner components", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.transformedCornerComponents.getNSButton().setToolTip_("Lists all glyphs containing corner components that are not at 100%% scale.")
		linePos += lineHeight

		# Line Separator:
		self.w.line_scriptOptions = vanilla.HorizontalLine((inset, linePos + 3, -inset, 1))
		linePos += int(lineHeight / 2)

		# Script Options:
		self.w.includeAllGlyphs = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "Check all glyphs in font (recommended)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeAllGlyphs.getNSButton().setToolTip_("If enabled, will ignore your current glyph selection, and simply go through the complete font. Recommended. May still ignore non-exporting glyph, see following option.")
		linePos += lineHeight

		self.w.includeNonExporting = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "Include non-exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.getNSButton().setToolTip_("If disabled, will ignore glyphs that are set to not export.")
		linePos += lineHeight

		self.w.reuseTab = vanilla.CheckBox((inset + 2, linePos, 125, 20), "Reuse existing tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.getNSButton().setToolTip_("If enabled, will only open a new tab if none is open. Recommended.")
		
		self.w.verbose = vanilla.CheckBox((inset+140, linePos, -inset, 20), "Verbose (slow)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose.getNSButton().setToolTip_("Will do verbose reporting in the Macro Window and the status line of this window. Slows down the script significantly, so activate only for small fonts.")
		linePos += lineHeight

		# Progress Bar and Status text:
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)  # set progress indicator to zero
		self.w.status = vanilla.TextBox((inset, -18 - inset, -inset - 100, 14), "🤖 Ready.", sizeStyle='small', selectable=True)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Open Tab", callback=self.ComponentProblemFinderMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		shouldEnableRunButton = any([bool(Glyphs.defaults[self.domain(p)]) for p in self.prefs])
		self.w.runButton.enable(shouldEnableRunButton)

		self.w.unproportionallyScaledComponents.enable(self.w.scaledComponents.get())

	def callMethodWithArg(self, methodName, arg):
		method = getattr(self, methodName)
		return method(arg)

	def glyphHas_composablesWithoutComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			if (thisLayer.isMasterLayer or thisLayer.isSpecialLayer) and not thisLayer.components:
				info = thisGlyph.glyphInfo
				if info and info.components:
					print("\t🙅🏼 missing components %s on layer: %s" % (
						", ".join([i.name for i in info.components]),
						thisLayer.name,
					))
					return True
		return False

	def glyphHas_unusualComponents(self, thisGlyph):
		componentStructure = orthodoxComponentsForGlyph(thisGlyph)
		if componentStructure:
			for thisLayer in thisGlyph.layers:
				if not layerAdheresToStructure(thisLayer, componentStructure):
					print("\t🔒 unusual components %s on layer: %s" % (
						", ".join([c.name for c in thisLayer.components]),
						thisLayer.name,
					))
					return True
		return False

	def glyphHas_lockedComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				if thisComponent.locked:
					print("\t🔒 locked component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
					return True
		return False

	def glyphHas_nestedComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				originalLayer = thisComponent.componentLayer
				if originalLayer and originalLayer.components:
					print("\t🪆 nested component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
					return True
		return False

	def glyphHas_orphanedComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				if thisComponent.component is None:
					print("\t🫥 orphaned component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
					return True
		return False

	def glyphHas_emptyComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			theseComponents = thisLayer.components
			if theseComponents:
				for thisComponent in theseComponents:
					if thisComponent.componentLayer and not thisComponent.componentLayer.shapes:
						print("\t🫙 empty component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
						return True
		return False

	def glyphHas_unalignedComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			theseComponents = thisLayer.components
			if theseComponents:
				for thisComponent in theseComponents:
					if thisComponent.alignment == -1:
						print("\t🤪 unaligned component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
						return True
		return False

	def glyphHas_scaledComponents(self, thisGlyph, unproportional=False):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				if thisComponent.rotation == 0.0:
					hScale, vScale = thisComponent.scale
					scaled = (hScale * vScale > 0.0) and (abs(hScale) != 1.0 or abs(vScale) != 1.0)
					if scaled:
						if unproportional:
							unproportionallyScaled = abs(hScale) != abs(vScale)
							if unproportionallyScaled:
								print("\t🤪 unproportionally scaled component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
								return True
						else:
							print("\t📏 scaled component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
							return True
		return False

	def glyphHas_unproportionallyScaledComponents(self, thisGlyph):
		return self.glyphHas_scaledComponents(thisGlyph, unproportional=True)

	def glyphHas_rotatedComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				hScale, vScale = thisComponent.scale
				rotatedByScaling = hScale == vScale and hScale < 0 and vScale < 0
				if thisComponent.rotation or rotatedByScaling:
					print("\t🎡 rotated component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
					return True
		return False

	def glyphHas_mirroredComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				hScale, vScale = thisComponent.scale
				if hScale * vScale < 0:
					print("\t🪞 mirrored component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
					return True
		return False

	def glyphHas_shiftedComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				hScale, vScale = thisComponent.scale
				degrees = thisComponent.rotation
				if hScale == 1.0 and vScale == 1.0 and degrees == 0.0:
					x, y = thisComponent.position
					if x != 0 or y != 0:
						print("\t🏗 shifted component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
						return True
		return False

	def glyphHas_detachedCornerComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for h in thisLayer.hints:
				if h.type == CORNER:
					if not h.originNode:
						print("\t🚨 detached corner component %s on layer: %s" % (h.name, thisLayer.name))
						return True
		return False

	def glyphHas_transformedCornerComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisHint in thisLayer.hints:
				if thisHint.type == CORNER:
					if abs(thisHint.scale.x) != 1.0 or abs(thisHint.scale.y) != 1.0:
						thisLayer.selection = None
						thisHint.selected = True
						print("\t🦄 transformed corner component %s on layer: %s" % (thisHint.name, thisLayer.name))
						return True
		return False

	def ComponentProblemFinderMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# start taking time:
			start = timer()

			# update settings to the latest user input:
			self.SavePreferences()
			verbose = self.pref("verbose")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Component Problem Finder Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				if self.pref("includeAllGlyphs"):
					glyphs = thisFont.glyphs
				else:
					glyphs = [layer.parent for layer in thisFont.selectedLayers]

				enabledPrefNames = [p for p in self.prefs if self.pref(p)]
				glyphDict = {}
				for dictKey in enabledPrefNames:
					glyphDict[dictKey] = []

				shouldIncludeNonExporting = self.pref("includeNonExporting")

				glyphCount = len(glyphs)
				for i, thisGlyph in enumerate(glyphs):
					self.w.progress.set(100 * i / glyphCount)
					if verbose:
						report = "🔠 %s" % thisGlyph.name
						print(report)
						self.w.status.set(report)

					if shouldIncludeNonExporting or thisGlyph.export:
						for prefName in enabledPrefNames:
							if Glyphs.defaults[self.domain(prefName)]:
								methodName = "glyphHas_%s" % prefName
								isAffected = self.callMethodWithArg(methodName, thisGlyph)
								if isAffected:
									glyphDict[prefName].append(thisGlyph.name)
				
				report = ""
				for prefName in enabledPrefNames:
					affectedGlyphs = glyphDict[prefName]
					if affectedGlyphs:
						report += "\n%s:\n%s\n" % (
							" ".join(camelCaseSplit(prefName)).capitalize(),
							"/" + "/".join(affectedGlyphs),
						)
				if verbose:
					print(report)

				if self.pref("reuseTab") and thisFont.currentTab:
					newTab = thisFont.currentTab
				else:
					newTab = thisFont.newTab()

				newTab.text = report.strip()

				# take time:
				end = timer()
				timereport = reportTimeInNaturalLanguage(end - start)
				print("Time elapsed: %s" % timereport)

				self.w.status.set("✅ Done. %s." % timereport)
				self.w.progress.set(100)

			# Final report:
			Glyphs.showNotification(
				"%s: Done" % (thisFont.familyName),
				"Component Problem Finder is finished. Details in Macro Window",
			)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Component Problem Finder Error: %s" % e)
			import traceback
			print(traceback.format_exc())


ComponentProblemFinder()
