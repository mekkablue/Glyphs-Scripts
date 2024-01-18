# MenuTitle: Travel Tracker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds interpolations in which points travel more than they should, i.e., can find wrongly hooked-up asterisks and slashes.
"""

import vanilla
from GlyphsApp import Glyphs, GSOFFCURVE, Message, distance
from mekkaCore import mekkaObject, angle


def setCurrentTabToShowAllInstances(font):
	previewingTab = font.currentTab
	previewPanel = None
	for p in Glyphs.delegate().valueForKey_("pluginInstances"):
		if "GlyphspreviewPanel" in p.__class__.__name__:
			previewPanel = p
			break
	try:
		if previewPanel:
			previewPanel.setSelectedInstance_(-1)
		previewingTab.setSelectedInstance_(-1)
		previewingTab.updatePreview()
		previewingTab.forceRedraw()
		font.tool = "TextTool"
		previewingTab.textCursor = 0
	except Exception as e:
		raise e


class TravelTracker(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"includeNonExporting": 1,
		"travelPercentage": 50,
		"normalizeShape": 1,
		"normalizeGlyph": 1,
		"segmentRotation": 1,
		"thresholdAngle": 40,
		"orthogonalToNonOrthogonal": 1,
		"ignoreShortSegments": 1,
		"ignoreShortSegmentsThreshold": 10,
		"verbose": 0,
		"allFonts": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 290
		windowHeight = 340
		windowWidthResize = 80  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Travel Tracker",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 14, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, lineHeight * 3), "Finds master-compatible glyphs with nodes that travel more than they should because they interpolate with a wrong node in another master.", sizeStyle='small', selectable=True)
		linePos += int(lineHeight * 2.2)

		tab, backTab = 100, 110
		self.w.travelPercentageText = vanilla.TextBox((inset, linePos + 3, tab, 14), "Acceptable travel:", sizeStyle='small', selectable=True)
		self.w.travelPercentage = vanilla.EditText((inset + tab, linePos, -inset - backTab, 19), "50", callback=self.SavePreferences, sizeStyle='small')
		self.w.travelPercentageText2 = vanilla.TextBox((-inset - backTab, linePos + 2, -inset, 14), "% of bbox diagonal", sizeStyle="small", selectable=True)
		self.w.travelPercentage.getNSTextField().setToolTip_("Anything above ~50% is suspicious in a weight interpolation, and above 70% in a width interpolation. (100% is the diagonal of the bounding box of the path (or glyph) the node belongs to.)")
		linePos += lineHeight

		self.w.normalizeShape = vanilla.CheckBox((inset, linePos - 1, 140, 20), "Normalize per shape", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.normalizeGlyph = vanilla.CheckBox((inset + 140, linePos - 1, -inset, 20), "Normalize per glyph", value=True, callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Choose what counts as 100%: the diagonal of the shape (path) the node belongs to, or the diagonal of the complete glyph, or both."
		self.w.normalizeShape.getNSButton().setToolTip_(tooltip)
		self.w.normalizeGlyph.getNSButton().setToolTip_(tooltip)
		linePos += int(lineHeight * 1.2)

		self.w.separator1 = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += int(lineHeight * 0.5)

		self.w.segmentRotationDescription = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Find big angle changes of consecutive nodes:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		tab, backTab = 165, 60
		self.w.segmentRotation = vanilla.CheckBox((inset, linePos, tab, 20), "Node pairs may rotate up to", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.thresholdAngle = vanilla.EditText((inset + tab, linePos, -inset - backTab, 19), "40", callback=self.SavePreferences, sizeStyle="small")
		self.w.segmentRotationText = vanilla.TextBox((-inset - backTab, linePos + 3, -inset, 14), "degrees", sizeStyle="small", selectable=True)
		tooltip = "Follows the rotation of consecutive node pairs across the interpolation. A high change in degrees may indicate a wrong start point or an unintentionally different path structure."
		self.w.segmentRotation.getNSButton().setToolTip_(tooltip)
		self.w.thresholdAngle.getNSTextField().setToolTip_(tooltip)
		self.w.segmentRotationText.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.orthogonalToNonOrthogonal = vanilla.CheckBox((inset, linePos, -inset, 20), "Report all segments going non-orthogonal", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.orthogonalToNonOrthogonal.getNSButton().setToolTip_("Will list any glyph where a segment (of minimum length, see below) changes from orthogonal (vertical or horizontal) to any other angle. Usually unintended unless you interpolate from upright to oblique.")
		linePos += lineHeight

		tab, backTab = 165, 60
		self.w.ignoreShortSegments = vanilla.CheckBox((inset, linePos, tab, 20), "Ignore short segments up to", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.ignoreShortSegmentsThreshold = vanilla.EditText((inset + tab, linePos, -inset - backTab, 19), "10", callback=self.SavePreferences, sizeStyle="small")
		self.w.ignoreShortSegmentsText = vanilla.TextBox((-inset - backTab, linePos + 3, -inset, 14), "units long", sizeStyle="small", selectable=True)
		tooltip = "Avoid too many false positives by ignoring the shortest segments, like open corners or the end of serifs."
		self.w.ignoreShortSegments.getNSButton().setToolTip_(tooltip)
		self.w.ignoreShortSegmentsText.getNSTextField().setToolTip_(tooltip)
		self.w.ignoreShortSegmentsThreshold.getNSTextField().setToolTip_(tooltip)
		linePos += int(lineHeight * 1.2)

		self.w.separator2 = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += int(lineHeight * 0.5)

		self.w.includeNonExporting = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Include non-exporting glyphs (recommended)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.getNSButton().setToolTip_("Important if you are using non-exporting glyphs as components inside others, e.g., the slashlongcomb in the oslash.")
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset, linePos - 1, 140, 20), "⚠️ Apply to ALL fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allFonts.getNSButton().setToolTip_("If checked, will go through all currently opened fonts. May take a while.")
		self.w.verbose = vanilla.CheckBox((inset + 140, linePos - 1, -inset, 20), "Verbose reporting", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.verbose.getNSButton().setToolTip_("Reports all glyphs in Macro Window, otherwise only a sorted list of affected glyphs.")
		linePos += lineHeight

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)  # set progress indicator to zero
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Find", sizeStyle='regular', callback=self.TravelTrackerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateGUI(self, sender=None):
		self.w.runButton.enable(any((
			self.w.normalizeGlyph.get(),
			self.w.normalizeShape.get(),
			self.w.segmentRotation.get(),
			self.w.orthogonalToNonOrthogonal.get(),
		)))
		self.w.thresholdAngle.enable(self.w.segmentRotation.get())

	def maxSegmentRotationForLayers(self, layer, otherLayer):
		maxSegmentRotation = 0.0
		maxDeorthogonalization = 0.0

		thresholdAngle = self.prefFloat("thresholdAngle")
		checkForSegmentRotation = self.prefBool("segmentRotation")
		checkForOrthogonalToNonOrthogonal = self.prefBool("orthogonalToNonOrthogonal")
		checkForShortSegments = self.prefBool("ignoreShortSegments")
		thresholdLength = self.prefFloat("ignoreShortSegmentsThreshold")

		layer.selection = None
		otherLayer.selection = None
		for pi, p1 in enumerate(layer.paths):
			p2 = otherLayer.paths[pi]
			for ni, n1 in enumerate(p1.nodes):
				if n1.type == GSOFFCURVE and n1.nextNode.type == GSOFFCURVE or (checkForShortSegments and thresholdLength >= distance(n1.position, n1.nextNode.position)):
					continue
					# skip, we are not interested in BCP to BCP rotation
				n2 = p2.nodes[ni]
				angle1 = angle(n1, n1.nextNode) % 360
				angle2 = angle(n2, n2.nextNode) % 360
				rotation = abs(angle1 - angle2)
				if rotation > 180:
					rotation = 180 - rotation

				# update max rotation:
				if maxSegmentRotation < rotation < 360 - maxSegmentRotation:
					maxSegmentRotation = rotation

				# orthogonal check:
				losingOrthogonalAngle = False
				if checkForOrthogonalToNonOrthogonal:
					losingOrthogonalAngle = losingOrthogonalAngle or ((angle1 % 90 == 0 and angle2 % 90 != 0) or (angle1 % 90 != 0 and angle2 % 90 == 0))
					if losingOrthogonalAngle:
						maxDeorthogonalization = max(maxDeorthogonalization, rotation)

				# select affected nodes if beyond threshold:
				if (checkForSegmentRotation and rotation > thresholdAngle) or losingOrthogonalAngle:
					for node in (n1, n1.nextNode):
						if node not in layer.selection:
							layer.selection.append(node)
					for node in (n2, n2.nextNode):
						if node not in otherLayer.selection:
							otherLayer.selection.append(node)

		return maxSegmentRotation, maxDeorthogonalization

	def maxNodeTravelRatioForLayers(self, layer, otherLayer, pathNormalization=True, layerNormalization=True):
		maxTravelRatio = 0.0
		maxPossibleTravel = 2**0.5

		normalizeShape = self.pref("normalizeShape")
		normalizeGlyph = self.pref("normalizeGlyph")

		# glyph bounds
		l1offset = layer.bounds.origin
		l2offset = otherLayer.bounds.origin
		l1Width, l1Height = layer.bounds.size
		l2Width, l2Height = otherLayer.bounds.size
		layerHasExtension = all((l1Width, l1Height, l2Width, l2Height))

		if not layerHasExtension:
			return 0.0

		for pi, p1 in enumerate(layer.paths):
			p2 = otherLayer.paths[pi]
			p1offset = p1.bounds.origin
			p2offset = p2.bounds.origin
			p1Width, p1Height = p1.bounds.size
			p2Width, p2Height = p2.bounds.size
			pathHasExtension = all((p1Width, p1Height, p2Width, p2Height))

			for ni, n1 in enumerate(p1.nodes):
				n2 = p2.nodes[ni]

				# SHAPE NORMALIZATION
				if pathHasExtension and normalizeShape:  # avoid zero width or zero height
					n1NormalizedX, n1NormalizedY = (n1.x - p1offset.x) / p1Width, (n1.y - p1offset.y) / p1Height
					n2NormalizedX, n2NormalizedY = (n2.x - p2offset.x) / p2Width, (n2.y - p2offset.y) / p2Height
					nodeDistance = distance(
						(n1NormalizedX, n1NormalizedY),
						(n2NormalizedX, n2NormalizedY),
					)
					maxTravelRatio = max(nodeDistance / maxPossibleTravel, maxTravelRatio)

				# LAYER NORMALIZATION
				if normalizeGlyph:
					n1NormalizedX, n1NormalizedY = (n1.x - l1offset.x) / l1Width, (n1.y - l1offset.y) / l1Height
					n2NormalizedX, n2NormalizedY = (n2.x - l2offset.x) / l2Width, (n2.y - l2offset.y) / l2Height
					nodeDistance = distance(
						(n1NormalizedX, n1NormalizedY),
						(n2NormalizedX, n2NormalizedY),
					)
					maxTravelRatio = max(nodeDistance / maxPossibleTravel, maxTravelRatio)
		return maxTravelRatio

	def relevantLayersOfGlyph(self, glyph):
		relevantLayers = [layer for layer in glyph.layers if (layer.layerId == layer.associatedMasterId or layer.isSpecialLayer) and layer.paths]
		return relevantLayers

	def hasInterpolatingPaths(self, glyph):
		relevantLayers = self.relevantLayersOfGlyph(glyph)
		if len(relevantLayers) < 2:
			return False
		else:
			return True

	def maxSegmentRotationForGlyph(self, relevantGlyph):
		maxSegmentRotation = 0.0
		deorthogonalization = 0.0
		relevantLayers = self.relevantLayersOfGlyph(relevantGlyph)
		numOfLayers = len(relevantLayers)
		for i in range(numOfLayers - 1):
			firstLayer = relevantLayers[i]
			for j in range(i + 1, numOfLayers):
				secondLayer = relevantLayers[j]
				if relevantGlyph.mastersCompatibleForLayers_((firstLayer, secondLayer)):
					thisSegmentRotation, thisDeorthogonalization = self.maxSegmentRotationForLayers(firstLayer, secondLayer)
					maxSegmentRotation = max(maxSegmentRotation, thisSegmentRotation)
					deorthogonalization = max(deorthogonalization, thisDeorthogonalization)
		return maxSegmentRotation, deorthogonalization

	def maxNodeTravelRatioForGlyph(self, relevantGlyph):
		maxTravelRatio = 0.0
		relevantLayers = self.relevantLayersOfGlyph(relevantGlyph)
		numOfLayers = len(relevantLayers)
		for i in range(numOfLayers - 1):
			firstLayer = relevantLayers[i]
			for j in range(i + 1, numOfLayers):
				secondLayer = relevantLayers[j]
				if relevantGlyph.mastersCompatibleForLayers_((firstLayer, secondLayer)):
					thisTravelRatio = self.maxNodeTravelRatioForLayers(firstLayer, secondLayer)
					maxTravelRatio = max(maxTravelRatio, thisTravelRatio)
		return maxTravelRatio

	def TravelTrackerMain(self, sender):
		try:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			verbose = self.prefBool("verbose")
			includeNonExporting = self.prefBool("includeNonExporting")
			travelPercentage = self.prefFloat("travelPercentage")
			allFonts = self.prefBool("allFonts")
			acceptableTravelRatio = travelPercentage / 100.0
			acceptableRotation = abs(self.prefFloat("thresholdAngle"))

			shouldCheckNodeTravel = self.prefBool("normalizeGlyph") or self.prefBool("normalizeShape")
			shouldCheckRotation = self.prefBool("segmentRotation") and self.prefBool("thresholdAngle")
			shouldCheckOrthogonals = self.prefBool("orthogonalToNonOrthogonal")

			if not Glyphs.font:
				Message(title="No Font Error", message="This script requires at least one font open.", OKButton=None)
				return

			if allFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )

			totalAffectedGlyphs = 0
			totalRelevantGlyphs = 0
			for j, thisFont in enumerate(theseFonts):
				if thisFont.filepath:
					print(f"Travel Tracker Report for {thisFont.filepath.lastPathComponent()}")
					print(thisFont.filepath)
				else:
					print(f"Travel Tracker Report for {thisFont.familyName}")
					print("⚠️ file not saved yet")
				print()

				tabText = ""
				relevantGlyphs = [g for g in thisFont.glyphs if (g.mastersCompatible and self.hasInterpolatingPaths(g)) and (includeNonExporting or g.export)]
				numOfGlyphs = float(len(relevantGlyphs))  # float for calculating the progress indicator below
				totalRelevantGlyphs += numOfGlyphs

				print(f"Examining {int(numOfGlyphs)} interpolating glyphs...")
				print()

				affectedGlyphInfosNodeTravel = []
				affectedGlyphInfosRotation = []
				affectedGlyphInfosDeorthogonalization = []

				for i, relevantGlyph in enumerate(relevantGlyphs):
					# push progress bar 1 tick further:
					fontSector = 100 / len(theseFonts)
					self.w.progress.set(int(j * fontSector + i / numOfGlyphs * fontSector))

					# NODE TRAVEL
					if shouldCheckNodeTravel:
						travelRatioInThisGlyph = self.maxNodeTravelRatioForGlyph(relevantGlyph)
						if travelRatioInThisGlyph > acceptableTravelRatio:
							affectedGlyphInfosNodeTravel.append((relevantGlyph.name, travelRatioInThisGlyph), )
							if verbose:
								print(f"❌🚀 Node traveling {int(travelRatioInThisGlyph * 100)}% in: {relevantGlyph.name}")
						elif verbose:
							print(f"✅🚀 Max node travel {int(travelRatioInThisGlyph * 100)}% in: {relevantGlyph.name}")

					# ROTATION AND DEORTH
					if shouldCheckRotation or shouldCheckOrthogonals:
						maxRotationInThisGlyph, maxDeorthogonalization = self.maxSegmentRotationForGlyph(relevantGlyph)
						if maxRotationInThisGlyph > acceptableRotation:
							affectedGlyphInfosRotation.append((relevantGlyph.name, maxRotationInThisGlyph))
							if verbose:
								print(f"🚫📐 Max rotation {maxRotationInThisGlyph:.1f}° in: {relevantGlyph.name}")
						elif verbose:
							print(f"✅📐 Max rotation {maxRotationInThisGlyph:.1f}° in: {relevantGlyph.name}")
						if maxDeorthogonalization != 0:
							affectedGlyphInfosDeorthogonalization.append((relevantGlyph.name, maxDeorthogonalization))
							if verbose:
								print(f"🚫☦️ Node pairs going from orthogonal to non-orthogonal in: {relevantGlyph.name}")
						elif verbose:
							print(f"✅☦️ No node pairs going from orthogonal to non-orthogonal in: {relevantGlyph.name}")

				# REPORT IN MACRO WINDOW
				# AND COLLECT SORTED GLYPHS FOR TAB
				if verbose:
					Glyphs.showMacroWindow()

				affectedGlyphNamesNodeTravel = []
				if affectedGlyphInfosNodeTravel:
					sortedGlyphInfos = sorted(affectedGlyphInfosNodeTravel, key=lambda thisListItem: -thisListItem[1])
					print("\n🚀 Node-traveling glyphs:")
					for glyphInfo in sortedGlyphInfos:
						percentage = glyphInfo[1] * 100
						glyphName = glyphInfo[0]
						print(f"{percentage:>8.1f}% {glyphName}")

					affectedGlyphNamesNodeTravel = [gi[0] for gi in sortedGlyphInfos]
					tabText += "Node-traveling:\n/" + "/".join(affectedGlyphNamesNodeTravel) + "\n\n"
				totalAffectedGlyphs += len(affectedGlyphNamesNodeTravel)

				affectedGlyphNamesRotation = []
				if affectedGlyphInfosRotation:
					sortedGlyphInfos = sorted(affectedGlyphInfosRotation, key=lambda thisListItem: -thisListItem[1])
					print("\n📐 Rotating node pairs:")
					for glyphInfo in sortedGlyphInfos:
						degrees = glyphInfo[1]
						glyphName = glyphInfo[0]
						print(f"{degrees:>8.1f}° {glyphName}")

					# open tab:
					affectedGlyphNamesRotation = [gi[0] for gi in sortedGlyphInfos]
					tabText += "Rotation:\n/" + "/".join(affectedGlyphNamesRotation) + "\n\n"
				totalAffectedGlyphs += len(affectedGlyphNamesRotation)

				affectedGlyphNamesDeorthogonalization = []
				if affectedGlyphInfosDeorthogonalization:
					sortedGlyphInfos = sorted(affectedGlyphInfosDeorthogonalization, key=lambda thisListItem: -thisListItem[1])
					print("\n☦️ Nodes going unorthogonal:")
					for glyphInfo in sortedGlyphInfos:
						degrees = glyphInfo[1]
						glyphName = glyphInfo[0]
						print(f"{degrees:>8.1f}° {glyphName}")

					# open tab:
					affectedGlyphNamesDeorthogonalization = [gi[0] for gi in sortedGlyphInfos]
					tabText += "Unorthogonal:\n/" + "/".join(affectedGlyphNamesDeorthogonalization) + "\n\n"
				totalAffectedGlyphs += len(affectedGlyphNamesDeorthogonalization)

				if tabText:
					tab = thisFont.newTab(tabText[:-1])  # cut off the last newline
					setCurrentTabToShowAllInstances(thisFont)
					tab.scale = 0.07
					vp = tab.viewPort
					vp.origin.x = 0
					vp.origin.y = -vp.size.height
					tab.viewPort = vp

			# last one finished, progress bar = 100:
			self.w.progress.set(100)

			if totalAffectedGlyphs == 0:
				Message(
					title="No affected glyph found",
					message="No glyph found where a node travels and rotation exceed the given thresholds. Congratulations!",
					OKButton="🥂 Cheers!",
				)
				print("✅ Done. No issues found.")
			else:
				issues = []
				if len(affectedGlyphNamesNodeTravel) != 0:
					issue = f"{len(affectedGlyphNamesNodeTravel)} glyph{'s' if len(affectedGlyphNamesNodeTravel) != 1 else ''} with nodes traveling more than {int(round(travelPercentage))}%"
					issues.append(issue)
				if len(affectedGlyphNamesRotation) != 0:
					issue = f"{len(affectedGlyphNamesRotation)} glyph{'s' if len(affectedGlyphNamesRotation) != 1 else ''} with node pairs rotating more than {int(round(acceptableRotation))}°"
					issues.append(issue)
				if len(affectedGlyphNamesDeorthogonalization) != 0:
					issue = f"{len(affectedGlyphNamesDeorthogonalization)} glyph{'s' if len(affectedGlyphNamesDeorthogonalization) != 1 else ''} with node pairs going unorthogonal"
					issues.append(issue)

				Message(
					title=f"Found {int(totalAffectedGlyphs)} issue{'s' if totalAffectedGlyphs != 1 else ''}",
					message=f"{', '.join(issues)};\nin a total of {int(totalRelevantGlyphs)} interpolating glyphs in {len(theseFonts)} font{'s' if len(theseFonts) != 1 else ''} examined.",
					OKButton=None,
				)
				print(f"\n✅ Done. Found {int(totalAffectedGlyphs)} issue{'s' if totalAffectedGlyphs != 1 else ''} with issues:\n🔤 {', 🔤 '.join(issues)}.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Travel Tracker Error: {e}")
			import traceback
			print(traceback.format_exc())


TravelTracker()
