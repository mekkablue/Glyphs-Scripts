# MenuTitle: Composite Variabler
__doc__ = """
Reduplicates Brace and Bracket layers of components in the composites in which they are used. Makes brace and bracket layers work in the composites.
"""

import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, Message, GSLayer
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut


class CompositeVariabler(mekkaObject):
	prefDict = {
		"processBracketLayers": 0,
		"processBraceLayers": 1,
		"allGlyphs": 1,
		"openTab": 0,
		"deleteExistingSpecialLayers": 1,
		"decomposeBrackets": 1,
		"catchNestedComponents": 0,
		"justBackupInstead": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 420
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Composite Variabler",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Reduplicates special layers of components in the composites in which they are used. Makes bracket and brace layers work.", sizeStyle='small', selectable=True)
		# the description wraps: it takes the width it is given, and gets a fixed height in the rules
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.processBracketLayers = vanilla.CheckBox("auto", "Process [BRACKET] layers", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.processBraceLayers = vanilla.CheckBox("auto", "Process {BRACE} layers", value=True, callback=self.SavePreferences, sizeStyle='small')

		self.w.allGlyphs = vanilla.CheckBox("auto", "Include all exporting glyphs in font (otherwise only selected glyphs)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allGlyphs.setToolTip("If checked, all glyphs in the font will be processed and receive the special (brace and bracket) layers of their respective components. If unchecked, only selected composite glyphs get processed.")

		self.w.decomposeBrackets = vanilla.CheckBox("auto", "Decompose special layers in composites (currently broken)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.decomposeBrackets.setToolTip("If checked, will decompose bracket layers. This is necessary for bracket layers to work in OTVAR fonts in Glyphs 2.6.")

		self.w.deleteExistingSpecialLayers = vanilla.CheckBox("auto", "Delete pre-existing special layers in composites", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.deleteExistingSpecialLayers.setToolTip("If checked, will delete all bracket or brace layers found in processed composite glyphs.")

		self.w.justBackupInstead = vanilla.CheckBox("auto", "Don’t delete, just backup and deactivate instead", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.justBackupInstead.setToolTip("If checked, will not delete, but just deactivate the layer by renaming it from ‘[100]’ to ‘#100#’.")

		self.w.openTab = vanilla.CheckBox("auto", "Open tab with affected composites", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.openTab.setToolTip("If checked, will open a tab with all composites that have received new special layers.")

		self.w.catchNestedComponents = vanilla.CheckBox("auto", "Catch all nested components (slower)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.catchNestedComponents.setToolTip("If checked, will count max component depth (number of nestings, i.e. components of components of components, etc.) in the font, and repeat the whole process as many times. Will take significantly longer. Use this only if you need it (unlikely) and know what you are doing.")

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero

		self.w.processedGlyph = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle='small', selectable=True)
		self.w.processedGlyph.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Run", callback=self.CompositeVariablerMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[processBracketLayers]-gap-[processBraceLayers]-(>=inset)-|",
				"H:|-inset-[allGlyphs]-(>=inset)-|",
				"H:|-inset-[decomposeBrackets]-(>=inset)-|",
				"H:|-inset-[deleteExistingSpecialLayers]-(>=inset)-|",
				"H:|-indent-[justBackupInstead]-(>=inset)-|",
				"H:|-inset-[openTab]-(>=inset)-|",
				"H:|-inset-[catchNestedComponents]-(>=inset)-|",
				"H:|-inset-[progress]-inset-|",
				"H:|-inset-[processedGlyph]-(>=gap)-[runButton(>=80)]-inset-|",
				"V:|-inset-[descriptionText(28)]-headlineGap-[processBracketLayers]-checkRow-[allGlyphs]-checkRow-[decomposeBrackets]-checkRow-[deleteExistingSpecialLayers]-checkRow-[justBackupInstead]-checkRow-[openTab]-checkRow-[catchNestedComponents]-barGap-[progress(16)]-inset-[runButton]-inset-|",
				{"view1": self.w.processBraceLayers, "attribute1": "centerY", "view2": self.w.processBracketLayers, "attribute2": "centerY"},
				{"view1": self.w.processedGlyph, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "indent": inset * 2 + 3, "gap": 8, "checkRow": 5, "headlineGap": 10, "barGap": 12},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.updateUI()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.justBackupInstead.enable(self.w.deleteExistingSpecialLayers.get())
		self.w.runButton.enable(self.w.processBracketLayers.get() or self.w.processBraceLayers.get())

	def countNest(self, component):
		thisFont = component.parent.parent.parent
		if thisFont:
			gName = component.componentName
			glyph = thisFont.glyphs[gName]
			if glyph:
				gComponents = glyph.layers[0].components
				if gComponents:
					maxCount = max(self.countNest(cc) for cc in gComponents)
					return 1 + maxCount
		return 1

	def depthOfNesting(self, thisFont):
		depths = []
		for glyph in thisFont.glyphs:
			for layer in glyph.layers:
				if layer.isMasterLayer or layer.isSpecialLayer or (Glyphs.versionNumber >= 3 and layer.isColorLayer):
					for component in layer.components:
						depth = self.countNest(component)
						depths.append(depth)
		return max(depths) if depths else 1

	def isBracketLayer(self, layer):
		if Glyphs.versionNumber >= 4:
			# GLYPHS 4
			return layer.isBracketLayer
		elif Glyphs.versionNumber >= 3:
			# GLYPHS 3
			return layer.isBracketLayer()
		else:
			# GLYPHS 2
			return layer.isSpecialLayer and "[" in layer.name and "]" in layer.name

	def isBraceLayer(self, layer):
		if Glyphs.versionNumber >= 4:
			# GLYPHS 4
			return layer.isBraceLayer
		elif Glyphs.versionNumber >= 3:
			# GLYPHS 3
			return layer.isBraceLayer()
		else:
			# GLYPHS 2
			return layer.isSpecialLayer and "{" in layer.name and "}" in layer.name

	def CompositeVariablerMain(self, sender):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			processBracketLayers = self.pref("processBracketLayers")
			processBraceLayers = self.pref("processBraceLayers")
			allGlyphs = self.pref("allGlyphs")
			openTab = self.pref("openTab")
			deleteExistingSpecialLayers = self.pref("deleteExistingSpecialLayers")
			catchNestedComponents = self.pref("catchNestedComponents")
			decomposeBrackets = self.pref("decomposeBrackets")
			justBackupInstead = self.pref("justBackupInstead")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			else:
				print("Composite Variabler Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

			depth = 1
			if catchNestedComponents:
				print("Catching all component nestings...")
				depth = self.depthOfNesting(thisFont)
				depth = max(1, depth)  # minimum 1, just to make sure
				print("Found components nested up to %i time%s" % (depth, "" if depth == 1 else "s"))

			if allGlyphs:
				glyphs = [glyph for glyph in thisFont.glyphs if glyph.export]
				print("Processing all glyphs (%i in total)..." % len(glyphs))
			else:
				glyphs = set([layer.parent for layer in thisFont.selectedLayers if layer.parent.export])
				print("Processing selected glyphs (%i in total)..." % len(glyphs))

			affectedGlyphs = []  # collected across all nesting iterations
			for depthIteration in range(depth):
				depthStatusAddition = ""
				if depth > 1:
					print("\nNesting iteration %i:" % (depthIteration + 1))
					depthStatusAddition = "%i: " % (depthIteration + 1)

				glyphCount = len(glyphs)
				layersToDecompose = []
				for i, currentGlyph in enumerate(glyphs):

					# status update
					self.w.progress.set(i * 100.0 / glyphCount)
					processMessage = "🔠 %s%s" % (depthStatusAddition, currentGlyph.name)
					self.w.processedGlyph.set(processMessage)
					# print processMessage

					# process layers
					thisLayer = currentGlyph.layers[0]
					if thisLayer.components and not thisLayer.paths:  # pure composites only

						# delete special layers if requested:
						if deleteExistingSpecialLayers:
							layerCount = len(currentGlyph.layers)
							for i in reversed(range(layerCount)):
								thatLayer = currentGlyph.layers[i]
								braceLayer = self.isBraceLayer(thatLayer)
								bracketLayer = self.isBracketLayer(thatLayer)
								if braceLayer or bracketLayer:
									if justBackupInstead:
										for bracket in "[]{}":
											thatLayer.name = thatLayer.name.replace(bracket, "#")
										print("%s: backed up layer: '%s'" % (currentGlyph.name, thatLayer.name))
										if Glyphs.versionNumber >= 3:
											for key in ("coordinates", "axisRules"):
												del thatLayer.attributes[key]
									else:
										print("%s: deleted layer '%s'" % (currentGlyph.name, thatLayer.name))
										del currentGlyph.layers[i]

						for component in thisLayer.components:
							originalGlyph = thisFont.glyphs[component.componentName]
							if originalGlyph and not originalGlyph.isSmartGlyph():
								for originalLayer in originalGlyph.layers:
									braceLayer = (processBraceLayers and self.isBraceLayer(originalLayer))
									bracketLayer = (processBracketLayers and self.isBracketLayer(originalLayer))
									if braceLayer or bracketLayer:
										# namesAndMasterIDsOfSpecialLayers = [(l.name,l.associatedMasterId) for l in currentGlyph.layers if l.isSpecialLayer]
										layerAlreadyExists = False
										for currentGlyphLayer in currentGlyph.layers:
											nameIsTheSame = originalLayer.name == currentGlyphLayer.name
											masterIsTheSame = originalLayer.associatedMasterId == currentGlyphLayer.associatedMasterId
											if nameIsTheSame and masterIsTheSame:
												layerAlreadyExists = True
										if layerAlreadyExists:
											print("%s, layer '%s' already exists. Skipping." % (currentGlyph.name, originalLayer.name))
										else:
											newLayer = GSLayer()
											newLayer.name = originalLayer.name
											newLayer.setAssociatedMasterId_(originalLayer.associatedMasterId)
											newLayer.width = originalLayer.width
											currentGlyph.layers.append(newLayer)
											if Glyphs.versionNumber >= 3:
												for attributeKey in originalLayer.attributes.keys():
													newLayer.setAttribute_forKey_(
														originalLayer.attributes[attributeKey],
														attributeKey,
													)
											newLayer.reinterpolate()
											if Glyphs.versionNumber >= 4:
												newLayer.reinterpolateMetrics_(None)
											else:
												newLayer.reinterpolateMetrics()
											newLayer.syncMetrics()
											if Glyphs.versionNumber >= 3:
												masterLayer = currentGlyph.layers[originalLayer.associatedMasterId]
												for i, masterComponent in enumerate(masterLayer.components):
													newComponent = newLayer.components[i]
													newComponent.setAlignment_(masterComponent.alignment)
													newComponent.setIsAligned_(masterComponent.isAligned())

											affectedGlyphs.append(currentGlyph.name)
											print("🔠 %s, new layer: '%s'%s" % (
												currentGlyph.name,
												newLayer.name,
												" (decomposed)" if decomposeBrackets else "",
											))
											if decomposeBrackets:
												layersToDecompose.append(newLayer)

				# decompose (must happen after all reinterpolations are done):
				for bracketLayer in layersToDecompose:
					for component in bracketLayer.components:
						component.decompose()

			# status update
			self.w.progress.set(100)
			numOfGlyphs = len(set(affectedGlyphs))
			self.w.processedGlyph.set("✅ Added layers to %i composite glyph%s." % (numOfGlyphs, "" if numOfGlyphs == 1 else "s"))
			print("Done.")

			if affectedGlyphs:
				if openTab:
					# opens new Edit tab:
					tabText = "/" + "/".join(set(affectedGlyphs))
					thisFont.newTab(tabText)

				# Floating notification:
				numOfGlyphs = len(set(affectedGlyphs))
				Glyphs.showNotification(
					"%s" % (thisFont.familyName),
					"Composite Variabler added layers to %i composite glyph%s. Details in Macro Window." % (
						numOfGlyphs,
						"" if numOfGlyphs == 1 else "s",
					),
				)

			else:
				# Floating notification:
				Glyphs.showNotification(
					"%s" % (thisFont.familyName),
					"Composite Variabler added no new layers. Details in Macro Window.",
				)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Composite Variabler Error: %s" % e)
			import traceback
			print(traceback.format_exc())


CompositeVariabler()
