# MenuTitle: Copy Layer to Layer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Copies one master to another master's or background in selected glyphs.
"""

import vanilla
from GlyphsApp import Glyphs, GSPath, GSComponent
from mekkablue import mekkaObject


class CopyLayerToLayer(mekkaObject):
	prefDict = {
		"includePaths": True,
		"includeComponents": True,
		"includeAnchors": True,
		"includeMetrics": True,
		"keepWindowOpen": True,
		"copyBackground": False,
		"keepOriginal": False,
		"verbose": False,

		"fontSource": 0,
		"masterSource": 0,
		"fontTarget": 0,
		"masterTarget": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 340
		windowHeight = 240
		windowWidthResize = 200  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Copy layer to layer",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		linePos, inset, lineHeight, tabStop = 12, 15, 22, 100

		self.w.text_1 = vanilla.TextBox((inset, linePos+2, tabStop, 14), "Copy paths from", sizeStyle='small')
		self.w.fontSource = vanilla.PopUpButton((inset+tabStop, linePos, -inset, 17), self.GetFontNames(), sizeStyle='small', callback=self.FontChangeCallback)
		linePos += lineHeight

		self.w.masterSource = vanilla.PopUpButton((inset+tabStop, linePos, -inset, 17), self.GetMasterNames("source"), sizeStyle='small', callback=self.MasterChangeCallback)
		linePos += lineHeight

		self.w.text_2 = vanilla.TextBox((inset, linePos+2, tabStop, 14), "into selection of", sizeStyle='small')
		self.w.fontTarget = vanilla.PopUpButton((inset+tabStop, linePos, -inset, 17), self.GetFontNames(), sizeStyle='small', callback=self.FontChangeCallback)
		linePos += lineHeight

		self.w.masterTarget = vanilla.PopUpButton((inset+tabStop, linePos, -inset, 17), self.GetMasterNames("target"), sizeStyle='small', callback=self.MasterChangeCallback)
		linePos += lineHeight
		
		tabStop = 160

		self.w.includePaths = vanilla.CheckBox((inset, linePos-1, tabStop, 20), "Include paths", sizeStyle='small', callback=self.SavePreferences, value=True)
		self.w.includeComponents = vanilla.CheckBox((inset + tabStop, linePos-1, -inset, 20), "Include components", sizeStyle='small', callback=self.SavePreferences, value=True)
		linePos += lineHeight

		self.w.includeAnchors = vanilla.CheckBox((inset, linePos-1, tabStop, 20), "Include anchors", sizeStyle='small', callback=self.SavePreferences, value=True)
		self.w.includeMetrics = vanilla.CheckBox((inset + tabStop, linePos-1, -inset, 20), "Include metrics", sizeStyle='small', callback=self.SavePreferences, value=True)
		linePos += lineHeight

		self.w.copyBackground = vanilla.CheckBox((inset, linePos-1, tabStop, 20), "Into background instead", sizeStyle='small', callback=self.SavePreferences, value=False)
		self.w.keepOriginal = vanilla.CheckBox((inset + tabStop, linePos-1, -inset, 20), "Keep target layer content", sizeStyle='small', callback=self.SavePreferences, value=False)
		linePos += lineHeight

		self.w.keepWindowOpen = vanilla.CheckBox((inset, linePos-1, tabStop, 20), "Keep window open", sizeStyle='small', callback=self.SavePreferences, value=True)
		self.w.verbose = vanilla.CheckBox((inset + tabStop, linePos-1, -inset, 20), "Verbose", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.copybutton = vanilla.Button((-80, -30, -15, -10), "Copy", sizeStyle='small', callback=self.buttonCallback)
		self.w.setDefaultButton(self.w.copybutton)

		# Load Settings:
		self.LoadPreferences()

		self.w.open()
		self.w.makeKey()
		self.w.masterTarget.set(1)

	def GetFontNames(self):
		"""Collects names of Open Fonts to populate the menus in the GUI."""
		myFontList = []
		# The active font is at index=0, so the default selection should be the active font.
		for fontIndex in range(len(Glyphs.fonts)):
			thisFont = Glyphs.fonts[fontIndex]
			myFontList.append('%i: %s' % (fontIndex, thisFont.familyName))
		return myFontList

	def GetMasterNames(self, font):
		"""Collects names of masters to populate the submenus in the GUI."""
		try:
			if font == "target":
				fontIndex = self.prefInt("fontTarget")
			else:
				fontIndex = self.prefInt("fontSource")
		except:
			fontIndex = 0

		# reset fontIndex if necessary (outdated prefs):
		if fontIndex > len(Glyphs.fonts) - 1:
			fontIndex = 0

		# reset the prefs if necessary:
		if fontIndex == 0:
			if font == "target":
				self.setPref("fontTarget", fontIndex)
			else:
				self.setPref("fontSource", fontIndex)

		thisFont = Glyphs.fonts[fontIndex]
		myMasterList = []
		for masterIndex in range(len(thisFont.masters)):
			thisMaster = thisFont.masters[masterIndex]
			myMasterList.append('%i: %s' % (masterIndex, thisMaster.name))
		return myMasterList

	def ValidateInput(self, sender):
		"""Disables the button if source and target are the same."""
		sourceAndTargetFontAreTheSame = self.pref("fontSource") == self.pref("fontTarget")
		sourceAndTargetMasterAreTheSame = self.pref("masterSource") == self.pref("masterTarget")
		if sourceAndTargetFontAreTheSame and sourceAndTargetMasterAreTheSame:
			self.w.copybutton.enable(False)
		else:
			self.w.copybutton.enable(True)

	def MasterChangeCallback(self, sender):
		"""Just call ValidateInput."""
		self.SavePreferences(sender)
		self.ValidateInput(None)

	def FontChangeCallback(self, sender):
		"""Update masters menus when font input changes."""
		self.SavePreferences(sender)
		if sender == self.w.fontSource:
			# Refresh source
			self.w.masterSource.setItems(self.GetMasterNames("source"))
		else:
			# Refresh target
			self.w.masterTarget.setItems(self.GetMasterNames("target"))
		self.ValidateInput(None)

	def copyPathsFromLayerToLayer(self, sourceLayer, targetLayer, keepOriginal=False, verbose=False):
		"""Copies all paths from sourceLayer to targetLayer"""
		numberOfPathsInSource = len(sourceLayer.paths)
		numberOfPathsInTarget = len(targetLayer.paths)

		if numberOfPathsInTarget != 0 and not keepOriginal:
			if verbose:
				print("- Deleting %i paths in target layer" % numberOfPathsInTarget)
			try:
				# GLYPHS 3
				for i in reversed(range(len(targetLayer.shapes))):
					if isinstance(targetLayer.shapes[i], GSPath):
						del targetLayer.shapes[i]
			except:
				# GLYPHS 2
				targetLayer.paths = None

		if numberOfPathsInSource > 0:
			if verbose:
				print("- Copying paths")
			for thisPath in sourceLayer.paths:
				newPath = thisPath.copy()
				try:
					# GLYPHS 3
					targetLayer.shapes.append(newPath)
				except:
					# GLYPHS 2
					targetLayer.paths.append(newPath)

	def copyHintsFromLayerToLayer(self, sourceLayer, targetLayer, keepOriginal=False, verbose=False):
		"""Copies all hints, corner and cap components from one layer to the next."""
		numberOfHintsInSource = len(sourceLayer.hints)
		numberOfHintsInTarget = len(targetLayer.hints)

		if numberOfHintsInTarget != 0 and not keepOriginal:
			if verbose:
				print("- Deleting %i hints, caps and corners in target layer" % numberOfHintsInTarget)
			targetLayer.hints = []

		if numberOfHintsInSource > 0:
			if verbose:
				print("- Copying hints, caps and corners")
			for thisHint in sourceLayer.hints:
				newHint = thisHint.copy()
				targetLayer.hints.append(newHint)

	def copyComponentsFromLayerToLayer(self, sourceLayer, targetLayer, keepOriginal=False, verbose=False):
		"""Copies all components from sourceLayer to targetLayer."""
		numberOfComponentsInSource = len(sourceLayer.components)
		numberOfComponentsInTarget = len(targetLayer.components)

		if numberOfComponentsInTarget != 0 and not keepOriginal:
			if verbose:
				print("- Deleting %i components in target layer" % numberOfComponentsInTarget)
			try:
				# GLYPHS 3
				for i in reversed(range(len(targetLayer.shapes))):
					if isinstance(targetLayer.shapes[i], GSComponent):
						del targetLayer.shapes[i]
			except:
				# GLYPHS 2
				targetLayer.components = []

		if numberOfComponentsInSource > 0:
			if verbose:
				print("- Copying components:")
			for thisComp in sourceLayer.components:
				newComp = thisComp.copy()
				if verbose:
					print("   Component: %s" % (thisComp.componentName))
				targetLayer.components.append(newComp)

	def copyAnchorsFromLayerToLayer(self, sourceLayer, targetLayer, keepOriginal=False, verbose=False):
		"""Copies all anchors from sourceLayer to targetLayer."""
		numberOfAnchorsInSource = len(sourceLayer.anchors)
		numberOfAnchorsInTarget = len(targetLayer.anchors)

		if numberOfAnchorsInTarget != 0 and not keepOriginal:
			if verbose:
				print("- Deleting %i anchors in target layer" % numberOfAnchorsInTarget)
			targetLayer.setAnchors_(None)

		if numberOfAnchorsInSource > 0:
			if verbose:
				print("- Copying anchors from source layer:")
			for thisAnchor in sourceLayer.anchors:
				newAnchor = thisAnchor.copy()
				targetLayer.anchors.append(newAnchor)
				if verbose:
					print("   %s (%i, %i)" % (thisAnchor.name, thisAnchor.position.x, thisAnchor.position.y))

	def copyMetricsFromLayerToLayer(self, sourceLayer, targetLayer, verbose=False):
		"""Copies width of sourceLayer to targetLayer."""
		sourceWidth = sourceLayer.width
		if targetLayer.width != sourceWidth:
			targetLayer.width = sourceWidth
			if verbose:
				print("- Copying width (%.1f)" % sourceWidth)
		else:
			if verbose:
				print("- Width not changed (already was %.1f)" % sourceWidth)

	def buttonCallback(self, sender):
		# save prefs, just to be on the safe side:
		self.SavePreferences(sender)

		# prepare macro output:
		Glyphs.clearLog()
		Glyphs.showMacroWindow()

		# This should be the active selection, not necessarily the selection on the inputted fonts
		Font = Glyphs.font
		selectedGlyphs = [layer.parent for layer in Font.selectedLayers if layer.parent.name is not None]

		indexOfSourceFont = self.prefInt("fontSource")
		indexOfTargetFont = self.prefInt("fontTarget")
		indexOfSourceMaster = self.prefInt("masterSource")
		indexOfTargetMaster = self.prefInt("masterTarget")
		pathsYesOrNo = self.prefBool("includePaths")
		componentsYesOrNo = self.prefBool("includeComponents")
		anchorsYesOrNo = self.prefBool("includeAnchors")
		metricsYesOrNo = self.prefBool("includeMetrics")
		copyBackground = self.prefBool("copyBackground")
		keepOriginal = self.prefBool("keepOriginal")
		verbose = self.prefBool("verbose")

		if verbose:
			print("Copy Layer to Layer Protocol:")
		for thisGlyph in selectedGlyphs:
			try:
				if verbose:
					print("🔠 %s" % thisGlyph.name)
				sourceFont = Glyphs.fonts[indexOfSourceFont]
				sourceGlyph = sourceFont.glyphs[thisGlyph.name]
				sourcelayer = sourceGlyph.layers[indexOfSourceMaster]

				targetFont = Glyphs.fonts[indexOfTargetFont]
				targetGlyph = targetFont.glyphs[thisGlyph.name]
				if copyBackground:
					targetlayer = targetGlyph.layers[indexOfTargetMaster].background
				else:
					targetlayer = targetGlyph.layers[indexOfTargetMaster]

				targetFont.disableUpdateInterface()
				try:
					# Copy paths, components, anchors, and metrics:
					if pathsYesOrNo:
						self.copyPathsFromLayerToLayer(sourcelayer, targetlayer, keepOriginal=keepOriginal, verbose=verbose)
					if componentsYesOrNo:
						self.copyComponentsFromLayerToLayer(sourcelayer, targetlayer, keepOriginal=keepOriginal, verbose=verbose)
					if anchorsYesOrNo:
						self.copyAnchorsFromLayerToLayer(sourcelayer, targetlayer, keepOriginal=keepOriginal, verbose=verbose)
					if metricsYesOrNo and not copyBackground:
						self.copyMetricsFromLayerToLayer(sourcelayer, targetlayer, verbose=verbose)

					# copy hints, caps and corners if either paths or components are copied:
					if componentsYesOrNo or pathsYesOrNo:
						self.copyHintsFromLayerToLayer(sourcelayer, targetlayer, keepOriginal=keepOriginal, verbose=verbose)

				except Exception as e:
					raise e

				finally:
					targetFont.enableUpdateInterface()

			except Exception as e:  # noqa: F841
				Glyphs.showMacroWindow()
				print("\n⚠️ Script Error:\n")
				import traceback
				print(traceback.format_exc())

		if not self.pref("keepWindowOpen"):
			self.w.close()


CopyLayerToLayer()
