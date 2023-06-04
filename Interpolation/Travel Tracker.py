#MenuTitle: Travel Tracker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds interpolations in which points travel more than they should, i.e., can find wrongly hooked-up asterisks and slashes.
"""

import vanilla

def setCurrentTabToShowAllInstances(font):
	previewingTab = font.currentTab
	previewPanel = None
	for p in NSApplication.sharedApplication().delegate().valueForKey_("pluginInstances"):
		if "GlyphspreviewPanel" in p.__class__.__name__:
			previewPanel = p
			break
	try:
		if previewPanel:
			previewPanel.setSelectedInstance_(-1)
		previewingTab.setSelectedInstance_(-1)
		previewingTab.updatePreview()
		previewingTab.forceRedraw()
		font.tool="TextTool"
		previewingTab.textCursor=0
	except Exception as e:
		raise e

class TravelTracker(object):
	prefID = "com.mekkablue.TravelTracker"
	prefDict = {
		# "prefName": defaultValue,
		"includeNonExporting": 1,
		"travelPercentage": 50,
		"normalizeShape": 1,
		"normalizeGlyph": 1,
		"verbose": 0,
		"allFonts": 0,
		}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 290
		windowHeight = 220
		windowWidthResize = 80 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Travel Tracker", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName=self.domain("mainwindow") # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 14, 22

		self.w.descriptionText = vanilla.TextBox(
			(inset, linePos + 2, -inset, lineHeight * 3),
			"Finds master-compatible glyphs with nodes that travel more than they should because they interpolate with a wrong node in another master.",
			sizeStyle='small',
			selectable=True
			)
		linePos += int(lineHeight * 2.2)

		self.w.travelPercentageText = vanilla.TextBox((inset, int(linePos + 2.5), 190, 14), "Acceptable travel ratio in percent:", sizeStyle='small', selectable=True)
		self.w.travelPercentage = vanilla.EditText((inset + 190, linePos, -inset, 19), "50", callback=self.SavePreferences, sizeStyle='small')
		self.w.travelPercentage.getNSTextField().setToolTip_(
			"Anything above 50% is suspicious in a weight interpolation, and above 70% in a width interpolation. (100% is the diagonal of the bounding box of the path the node belongs to.)"
			)
		linePos += lineHeight

		self.w.includeNonExporting = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Include non-exporting glyphs (recommended)", value=True, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.includeNonExporting.getNSButton().setToolTip_("Important if you are using non-exporting glyphs as components inside others, e.g., the slashlongcomb in the oslash.")
		linePos += lineHeight

		self.w.normalizeShape = vanilla.CheckBox((inset, linePos - 1, 140, 20), "Normalize per shape", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.normalizeGlyph = vanilla.CheckBox((inset + 140, linePos - 1, -inset, 20), "Normalize per glyph", value=True, callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Choose what counts as 100%: the diagonal of the shape (path) the node belongs to, or the diagonal of the complete glyph, or both."
		self.w.normalizeShape.getNSButton().setToolTip_(tooltip)
		self.w.normalizeGlyph.getNSButton().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset, linePos-1, 140, 20), "⚠️ Apply to ALL fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allFonts.getNSButton().setToolTip_("If checked, will go through all currently opened fonts. May take a while.")
		
		self.w.verbose = vanilla.CheckBox((inset+140, linePos - 1, -inset, 20), "Verbose reporting", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.verbose.getNSButton().setToolTip_("Reports all glyphs in Macro Window, otherwise only those that exceed the travel threshold.")
		
		linePos += lineHeight
		

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Find", sizeStyle='regular', callback=self.TravelTrackerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Travel Tracker' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()

	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]

	def updateGUI(self, sender=None):
		self.w.runButton.enable(any((
			self.w.normalizeGlyph.get(),
			self.w.normalizeShape.get(),
			)))

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
			self.updateGUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				getattr(self.w, prefName).set(self.pref(prefName))
			self.updateGUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

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
				if pathHasExtension and normalizeShape: # avoid zero width or zero height
					n1NormalizedX, n1NormalizedY = (n1.x - p1offset.x) / p1Width, (n1.y - p1offset.y) / p1Height
					n2NormalizedX, n2NormalizedY = (n2.x - p2offset.x) / p2Width, (n2.y - p1offset.y) / p2Height
					nodeDistance = distance(
						(n1NormalizedX, n1NormalizedY),
						(n2NormalizedX, n2NormalizedY),
						)
					maxTravelRatio = max(nodeDistance / maxPossibleTravel, maxTravelRatio)

				# LAYER NORMALIZATION
				if normalizeGlyph:
					n1NormalizedX, n1NormalizedY = (n1.x - l1offset.x) / l1Width, (n1.y - l1offset.y) / l1Height
					n2NormalizedX, n2NormalizedY = (n2.x - l2offset.x) / l2Width, (n2.y - l1offset.y) / l2Height
					nodeDistance = distance(
						(n1NormalizedX, n1NormalizedY),
						(n2NormalizedX, n2NormalizedY),
						)
					maxTravelRatio = max(nodeDistance / maxPossibleTravel, maxTravelRatio)

		return maxTravelRatio

	def relevantLayersOfGlyph(self, glyph):
		relevantLayers = [l for l in glyph.layers if (l.layerId == l.associatedMasterId or l.isSpecialLayer) and l.paths]
		return relevantLayers

	def hasInterpolatingPaths(self, glyph):
		relevantLayers = self.relevantLayersOfGlyph(glyph)
		if len(relevantLayers) < 2:
			return False
		else:
			return True

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
			if not self.SavePreferences(self):
				print("Note: 'Travel Tracker' could not write preferences.")

			verbose = bool(self.pref("verbose"))
			includeNonExporting = bool(self.pref("includeNonExporting"))
			travelPercentage = float(self.pref("travelPercentage"))
			allFonts = bool(self.pref("allFonts"))
			acceptableTravelRatio = travelPercentage / 100.0

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

				relevantGlyphs = [g for g in thisFont.glyphs if (g.mastersCompatible and self.hasInterpolatingPaths(g)) and (includeNonExporting or g.export)]

				numOfGlyphs = float(len(relevantGlyphs)) # float for calculating the progress indicator below
				totalRelevantGlyphs += numOfGlyphs
				
				print(f"Examining {numOfGlyphs} interpolating glyphs...")
				print()

				affectedGlyphInfos = []
				for i, relevantGlyph in enumerate(relevantGlyphs):
					# push progress bar 1 tick further:
					fontSector = 100/len(theseFonts)
					self.w.progress.set(int(j*fontSector + i/numOfGlyphs*fontSector))
					
					travelRatioInThisGlyph = self.maxNodeTravelRatioForGlyph(relevantGlyph)
					if travelRatioInThisGlyph > acceptableTravelRatio:
						print(f"❌ Node traveling {int(travelRatioInThisGlyph * 100)}%% in: {relevantGlyph.name}")
						affectedGlyphInfos.append((relevantGlyph.name, travelRatioInThisGlyph), )
					elif verbose:
						print(f"✅ Max node travel {int(travelRatioInThisGlyph * 100)}%% in: {relevantGlyph.name}")

				if affectedGlyphInfos:
					# report in macro window
					if verbose:
						Glyphs.showMacroWindow()
					sortedGlyphInfos = sorted(affectedGlyphInfos, key=lambda thisListItem: -thisListItem[1])
					print()
					print("Affected glyphs:")
					for glyphInfo in sortedGlyphInfos:
						percentage = glyphInfo[1] * 100
						glyphName = glyphInfo[0]
						print(f"   {percentage:.1f}% {glyphName}")

					# open tab:
					affectedGlyphNames = [gi[0] for gi in sortedGlyphInfos]
					tabText = "/" + "/".join(affectedGlyphNames)
					thisFont.newTab(tabText)
					setCurrentTabToShowAllInstances(thisFont)

				totalAffectedGlyphs += len(affectedGlyphNames)
			
			if totalAffectedGlyphs==0:
				Message(
					title="No affected glyph found",
					message=f"No glyph found where a node travels more than {travelPercentage}% of its path bounds diagonal. Congratulations!",
					OKButton="🥂 Cheers!",
					)
			else:
				Message(
					title="Found traveling nodes",
					message=f"Found {totalAffectedGlyphs} glyphs with node travels of more than {travelPercentage}% of the bounds diagonal, in a total of {totalRelevantGlyphs} interpolating glyphs in {len(theseFonts)} font{'s' if len(theseFonts)!=1 else ''}.",
					OKButton=None,
					)
			
			# last one finished, progress bar = 100:
			self.w.progress.set(100)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Travel Tracker Error: {e}")
			import traceback
			print(traceback.format_exc())

TravelTracker()
