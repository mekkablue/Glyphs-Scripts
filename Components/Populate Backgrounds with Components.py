# MenuTitle: Populate Layer Backgrounds with Component
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Adds a component to all backgrounds of all layers of all selected glyphs. Useful, e.g., for putting A in the background of (decomposed) Aogonek.
"""

import vanilla
from AppKit import NSEvent
from GlyphsApp import Glyphs, GSComponent, Message
from mekkablue import mekkaObject, UpdateButton
from mekkablue.geometry import transform


class PopulateAllBackgroundswithComponent(mekkaObject):
	prefDict = {
		"componentName": "a",
		"alignRight": 0,
		"replaceBackgrounds": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 380
		windowHeight = 155
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Populate Layer Backgrounds with Component",  # window title
			minSize=(windowWidth - 10, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 10, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "In selected glyphs, insert component in all layer backgrounds:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.text_1 = vanilla.TextBox((inset - 1, linePos + 2, 100, 14), "Add component:", sizeStyle='small')
		self.w.componentName = vanilla.EditText((inset + 92, linePos - 1, -inset - 25, 19), "a", sizeStyle='small', callback=self.SavePreferences)
		self.w.componentName.getNSTextField().setToolTip_("Name of the glyph that should be inserted as component in the background of all layers of the selected glyph(s).")
		self.w.updateButton = UpdateButton((-inset - 18, linePos - 2, -inset, 18), callback=self.update)
		self.w.updateButton.getNSButton().setToolTip_("Guess the component name. Hold down OPTION to ignore the suffix.")
		linePos += lineHeight

		self.w.alignRight = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Align with right edge of layer", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.alignRight.getNSButton().setToolTip_("Right-aligns the component width with the layer width. Useful for the e in ae or oe, for example.")
		linePos += lineHeight

		self.w.replaceBackgrounds = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Replace existing backgrounds", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.replaceBackgrounds.getNSButton().setToolTip_("Deletes existing background content before it inserts the component. Recommended if you want to align selected nodes with the background.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Populate", callback=self.PopulateAllBackgroundswithComponentMain)
		self.w.runButton.getNSButton().setToolTip_("Inserts the specified component in ALL layers of the current glyph(s).")
		self.w.setDefaultButton(self.w.runButton)

		self.w.alignButton = vanilla.Button((-220 - inset, -20 - inset, -110 - inset, -inset), "Align Nodes", callback=self.AlignNodesMain)
		self.w.alignButton.getNSButton().setToolTip_("Aligns selected nodes with the (original) nodes in the background components. Only does this on the CURRENT layer.")

		self.w.nextMasterButton = vanilla.Button((-340 - inset, -20 - inset, -230 - inset, -inset), "Next Master", callback=self.NextMasterMain)
		self.w.nextMasterButton.getNSButton().setToolTip_("Switches the current tab to the next master. Useful if you want to align the same nodes in every master.")

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def update(self, sender):
		# check if Option key is pressed or not:
		optionKeyFlag = 524288
		optionKeyPressed = NSEvent.modifierFlags() & optionKeyFlag == optionKeyFlag

		# some predetermined guesses:
		betterGuesses = {
			"perthousand": "percent",
			"brokenbar": "bar",
			"daggerdbl": "dagger",
			"dollar": "S",
			"cent": "c",
			"Fhook": "florin",
			"endash": "hyphen",
			"emdash": "endash",
			"Eng": "N",
			"eng": "n",
			"thorn": "p",
			"Thorn": "I",
			"ae": "e",
			"oe": "e",
			"AE": "E",
			"OE": "E",
			"germandbls": "f",
			"Germandbls": "F",
		}

		thisFont = Glyphs.font
		if thisFont:
			if thisFont.selectedLayers:
				currentLayer = thisFont.selectedLayers[0]
				currentGlyph = currentLayer.parent

				# do predetermined guesses apply:
				if currentGlyph.name in betterGuesses:
					glyphName = betterGuesses[currentGlyph.name]
					self.w.componentName.set(glyphName)
					self.SavePreferences(sender)
					return True

				# check for the dot suffix:
				suffix = ""
				if "." in currentGlyph.name:
					offset = currentGlyph.name.find(".")
					suffix = currentGlyph.name[offset:]

				# if glyph info has components, take the base letter name:
				thisInfo = currentGlyph.glyphInfo
				if thisInfo and thisInfo.components:
					firstComponentName = thisInfo.components[0].name
					if firstComponentName:
						if not optionKeyPressed:  # hold down OPT to ignore suffix
							firstComponentName += suffix
						self.w.componentName.set(firstComponentName)
						self.SavePreferences(sender)
						return True

				# no first component found, so try same name without suffix:
				if suffix:
					self.w.componentName.set(currentGlyph.name[:offset])
					self.SavePreferences(sender)
					return True

		return False

	def NextMasterMain(self, sender=None):
		try:
			thisFont = Glyphs.font
			if thisFont:
				tab = thisFont.currentTab
				if tab:
					newMasterIndex = (tab.masterIndex + 1) % len(thisFont.masters)
					tab.setMasterIndex_(newMasterIndex)
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Error trying to switch to next master: %s" % e)
			import traceback
			print(traceback.format_exc())

	def PopulateAllBackgroundswithComponentMain(self, sender):
		try:

			# determine component:
			componentName = self.pref("componentName")
			if not componentName:
				Message(title="Component Error", message="No component name specified. Please specify a valid glyph name.", OKButton=None)
			else:
				# determine frontmost font:
				thisFont = Glyphs.font
				if thisFont:
					# verify user input and selection:
					if not thisFont.glyphs[componentName]:
						Message(
							title="Component Name Error",
							message=u"There is no glyph called ‘%s’ in the frontmost font. Please specify a valid glyph name." % componentName,
							OKButton=None
						)
					elif not thisFont.selectedLayers:
						Message(title="Selection Error", message="No glyphs are selected. Please select a glyph and try again.", OKButton=None)
					else:
						# brings macro window to front and clears its log:
						Glyphs.clearLog()
						# Glyphs.showMacroWindow()

						# go through all selected glyphs:
						for thisLayer in thisFont.selectedLayers:
							thisGlyph = thisLayer.parent
							if thisGlyph:
								if thisGlyph.name == componentName:
									print("Skipping %s: cannot insert component of itself." % thisGlyph.name)
								else:
									numOfLayers = len(thisGlyph.layers)
									print("%s: adding %s as component in %i layer background%s." % (thisGlyph.name, componentName, numOfLayers, "s" if numOfLayers != 1 else ""))

									# go through all layers of each glyph:
									for glyphLayer in thisGlyph.layers:

										# delete existing background if user asked for it:
										if self.pref("replaceBackgrounds"):
											glyphLayer.background.clear()

										# add component:
										newComponent = GSComponent(componentName)
										glyphLayer.background.components.append(newComponent)

										# align right if user asked for it:
										if self.pref("alignRight"):

											# determine right edges:
											componentLayer = newComponent.componentLayer
											hShiftAmount = glyphLayer.width - componentLayer.width

											# layerBounds = glyphLayer.bounds
											# rightLayerEdge = layerBounds.origin.x + layerBounds.size.width
											# backgroundBounds = glyphLayer.background.bounds
											# rightBackgroundEdge = backgroundBounds.origin.x + backgroundBounds.size.width
											# hShiftAmount = rightLayerEdge - rightBackgroundEdge

											# move background component:
											newComponent.automaticAlignment = False
											hShift = transform(shiftX=hShiftAmount)
											hShiftMatrix = hShift.transformStruct()
											newComponent.applyTransform(hShiftMatrix)

			self.SavePreferences()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Populate All Backgrounds with Component Error: %s" % e)
			import traceback
			print(traceback.format_exc())

	def alignNodeWithNodeInOtherLayer(self, thisNode, otherLayer, tolerance=5, maxTolerance=80, alreadyTaken=[]):
		while tolerance < maxTolerance:
			try:
				# GLYPHS 3
				nearestNode = otherLayer.nodeAtPoint_excludeNodes_traverseComponents_ignoreLocked_tolerance_(thisNode.position, None, False, False, tolerance)
			except:
				# GLYPHS 2
				nearestNode = otherLayer.nodeAtPoint_excludeNodes_traversComponents_tollerance_(thisNode.position, None, False, tolerance)

			if nearestNode and (thisNode.type == nearestNode.type) and (nearestNode.position not in alreadyTaken):
				thisNode.position = nearestNode.position
				return True
			# else:
			# 	print tolerance
			# 	if nearestNode:
			# 		print "Type:", thisNode.type, nearestNode.type
			# 		print "Pos:", thisNode.position, nearestNode.position
			# 	else:
			# 		print "no Node", otherLayer.paths[0].nodes
			tolerance += 5
		return False

	def anchorWithNameFromAnchorList(self, anchorName, referenceAnchors):
		for thisAnchor in referenceAnchors:
			if thisAnchor.name == anchorName:
				return thisAnchor
		return None

	def syncAnchorPositionWithBackground(self, theseAnchorNames, thisLayer):
		# collect background anchors
		otherAnchorDict = {}
		for otherAnchor in thisLayer.background.anchorsTraversingComponents():
			otherAnchorDict[otherAnchor.name] = otherAnchor.position

		# move anchors in foreground
		if not otherAnchorDict:
			print("Anchors: could not find any anchors in components.")
			return 0
		else:
			count = 0
			for thisAnchorName in theseAnchorNames:
				otherAnchorPosition = otherAnchorDict[thisAnchorName]
				if otherAnchorPosition:
					thisAnchor = thisLayer.anchors[thisAnchorName]
					thisAnchor.position = otherAnchorPosition
					count += 1
			return count

	def alignNodesOnLayer(self, thisLayer):
		backgroundBackup = thisLayer.background.copy()
		for backgroundComponent in thisLayer.background.components:
			thisLayer.background.decomposeComponent_doAnchors_doHints_(backgroundComponent, False, False)

		alignedNodeCount = 0
		selectedNodeCount = 0
		appliedPositions = []

		for thisPath in thisLayer.paths:
			for thisNode in thisPath.nodes:
				if thisNode.selected:
					selectedNodeCount += 1
					if self.alignNodeWithNodeInOtherLayer(thisNode, thisLayer.background, alreadyTaken=appliedPositions):
						alignedNodeCount += 1
						appliedPositions.append(thisNode.position)

		thisLayer.background = backgroundBackup

		anchorsToAlign = []
		numberOfAnchorsMoved = 0
		for thisAnchor in thisLayer.anchors:
			if thisAnchor.selected:
				anchorsToAlign.append(thisAnchor.name)
		if anchorsToAlign:
			numberOfAnchorsMoved = self.syncAnchorPositionWithBackground(anchorsToAlign, thisLayer)

		return selectedNodeCount, alignedNodeCount, numberOfAnchorsMoved

	def AlignNodesMain(self, sender):
		thisFont = Glyphs.font  # frontmost font
		selectedLayers = thisFont.selectedLayers  # active layers of selected glyphs
		# selection = selectedLayers[0].selection  # node selection in edit mode
		Glyphs.clearLog()  # clears log in Macro window

		for thisLayer in selectedLayers:
			thisGlyph = thisLayer.parent
			# thisGlyph.beginUndo()  # undo grouping causes crashes
			selected, aligned, numberOfAnchorsMoved = self.alignNodesOnLayer(thisLayer)
			print("%s: aligned %i of %i selected nodes" % (thisGlyph.name, aligned, selected))
			print("%s: aligned %i of %i anchors." % (thisGlyph.name, numberOfAnchorsMoved, len(thisLayer.anchors)))
			# thisGlyph.endUndo()  # undo grouping causes crashes


PopulateAllBackgroundswithComponent()
