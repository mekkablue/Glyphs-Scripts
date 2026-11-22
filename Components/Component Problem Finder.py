# MenuTitle: Component Problem Finder
__doc__ = """
Find and report possible issues with components and corner components.
"""

import vanilla
from timeit import default_timer as timer
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message, CORNER
from mekkablue import mekkaObject, camelCaseSplit, reportTimeInNaturalLanguage, fontFileName


def orthodoxComponentsForGlyph(thisGlyph):
	"""Names of the components in the glyph’s recipe (Glyph Info), or None if it has no recipe."""
	glyphInfo = thisGlyph.glyphInfo
	if glyphInfo:
		componentInfo = glyphInfo.components
		if componentInfo:
			return tuple(c.name for c in componentInfo)
	return None


def nameStrippedOfSuffixes(glyphName):
	"""'a.sc' becomes 'a'; a name without period stays as it is (find() gives -1, and -1 % (len + 1) is len)."""
	return glyphName[:glyphName.find(".") % (len(glyphName) + 1)]


def layerAdheresToStructure(thisLayer, glyphNameTuple):
	"""True if the layer has the components of the recipe, in the same order, ignoring suffixes."""
	layerComponents = thisLayer.components
	if len(layerComponents) != len(glyphNameTuple):
		return False
	for thisComponent, orthodoxComponentName in zip(layerComponents, glyphNameTuple):
		thisComponentName = thisComponent.componentName
		if thisComponentName != orthodoxComponentName:
			if nameStrippedOfSuffixes(thisComponentName) != nameStrippedOfSuffixes(orthodoxComponentName):
				return False
	return True


# (preference name, checkbox title, tooltip), in groups separated by lines in the window:
checkGroups = (
	(
		("composablesWithoutComponents", "Composable glyphs without components", "Glyphs that could be built from components, according to their recipe in Glyph Info, but have none."),
		("unusualComponents", "Unusual composites (or wrong order)", "Composites whose components differ from the recipe in Glyph Info, or are in a different order."),
		("lockedComponents", "Locked components", "Glyphs with a locked component on any layer."),
		("nestedComponents", "Nested components", "Glyphs with components that themselves contain components."),
		("orphanedComponents", "Orphaned components", "Glyphs with components that reference glyphs missing from the font."),
		("emptyComponents", "Empty components", "Glyphs with components that point to layers without shapes."),
		("unalignedComponents", "Unaligned components", "Glyphs with components that have automatic alignment turned off."),
	),
	(
		("scaledComponents", "Scaled components", "Glyphs with components that are not at their original size. Useful for tracing bugs in variable fonts."),
		("unproportionallyScaledComponents", "Only unproportionally scaled (h≠v)", "Only components scaled differently horizontally and vertically. Useful for checking TrueType exports and variable fonts."),
		("rotatedComponents", "Rotated components", "Glyphs with rotated components, or components flipped both horizontally and vertically. Check their alignment."),
		("mirroredComponents", "Flipped components", "Glyphs with components flipped either horizontally or vertically."),
		("shiftedComponents", "Shifted (but undistorted) components", "Glyphs with unscaled, unrotated components that are not positioned at x=0 y=0."),
	),
	(
		("detachedCornerComponents", "Detached corner components", "Glyphs with corner components that lost their connection point."),
		("transformedCornerComponents", "Transformed corner components", "Glyphs with corner components that are not at 100% scale."),
	),
)


class ComponentProblemFinder(mekkaObject):
	prefDict = {
		"composablesWithoutComponents": False,
		"unusualComponents": False,
		"lockedComponents": False,
		"nestedComponents": False,
		"orphanedComponents": False,
		"emptyComponents": False,
		"unalignedComponents": False,
		"scaledComponents": True,
		"unproportionallyScaledComponents": True,
		"rotatedComponents": False,
		"mirroredComponents": False,
		"shiftedComponents": False,
		"detachedCornerComponents": False,
		"transformedCornerComponents": False,
		"includeAllGlyphs": True,
		"includeNonExporting": True,
		"reuseTab": True,
		"verbose": False,
	}
	# the problems to look for; used to enable/disable the run button:
	prefs = tuple(prefName for group in checkGroups for prefName, title, tooltip in group)

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Component Problem Finder",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset, indent = 15, 30

		self.w.descriptionText = vanilla.TextBox("auto", "New tab with glyphs containing components", sizeStyle='small', selectable=True)
		self.w.descriptionText.setToolTip("Finds glyphs with the checked problems and lists them in a tab, grouped by problem.")

		# checkboxes for the problems, with a line between the groups:
		verticalChain = "V:|-inset-[descriptionText]"
		rules = ["H:|-inset-[descriptionText]-inset-|"]
		for groupIndex, group in enumerate(checkGroups):
			if groupIndex:
				lineName = f"line{groupIndex}"
				setattr(self.w, lineName, vanilla.HorizontalLine("auto"))
				rules.append(f"H:|-inset-[{lineName}]-inset-|")
				verticalChain += f"-lineGap-[{lineName}(1)]-lineGap-"
			else:
				verticalChain += "-headlineGap-"
			for checkIndex, (prefName, title, tooltip) in enumerate(group):
				setattr(self.w, prefName, vanilla.CheckBox("auto", title, value=self.prefDict[prefName], callback=self.SavePreferences, sizeStyle='small'))
				getattr(self.w, prefName).setToolTip(tooltip)
				rules.append(f"H:|-{indent if prefName == 'unproportionallyScaledComponents' else 'inset'}-[{prefName}]-(>=inset)-|")
				verticalChain += f"-checkRow-[{prefName}]" if checkIndex else f"[{prefName}]"

		# script options:
		self.w.lineOptions = vanilla.HorizontalLine("auto")
		self.w.includeAllGlyphs = vanilla.CheckBox("auto", "Check all glyphs in font (recommended)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeAllGlyphs.setToolTip("Ignores the glyph selection and checks the whole font. Non-exporting glyphs follow the next option.")
		self.w.includeNonExporting = vanilla.CheckBox("auto", "Include non-exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.setToolTip("If off, glyphs that do not export are skipped.")
		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse existing tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.setToolTip("Shows the result in the current tab, and opens a new tab only if none is open. Recommended.")
		self.w.verbose = vanilla.CheckBox("auto", "Verbose (slow)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose.setToolTip("Reports every glyph in the Macro Window and the status line. Slow, so use it only for small fonts.")

		# Progress Bar and Status text:
		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero
		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle='small', selectable=True)
		self.w.status.setToolTip("Progress and result of the last run.")
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Open Tab", callback=self.ComponentProblemFinderMain)
		self.w.runButton.setToolTip("Checks the glyphs for the selected problems and opens a tab with the affected glyphs.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; hug so the window is as tall as its content:
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		verticalChain += "-lineGap-[lineOptions(1)]-lineGap-[includeAllGlyphs]-checkRow-[includeNonExporting]-checkRow-[reuseTab]-checkRow-[verbose]-barGap-[progress(16)]-inset-[runButton]-inset-|"
		rules += [
			"H:|-inset-[lineOptions]-inset-|",
			"H:|-inset-[includeAllGlyphs]-(>=inset)-|",
			"H:|-inset-[includeNonExporting]-(>=inset)-|",
			"H:|-inset-[reuseTab]-(>=inset)-|",
			"H:|-inset-[verbose]-(>=inset)-|",
			"H:|-inset-[progress]-inset-|",
			"H:|-inset-[status]-gap-[runButton(>=100)]-inset-|",
			verticalChain,
			{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
		]
		self.w.addAutoPosSizeRules(rules, metrics={"inset": inset, "gap": 8, "headlineGap": 10, "lineGap": 8, "checkRow": 5, "barGap": 14})

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.runButton.enable(any(self.prefBool(prefName) for prefName in self.prefs))
		self.w.unproportionallyScaledComponents.enable(self.w.scaledComponents.get())

	def glyphHasComposablesWithoutComponents(self, thisGlyph):
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

	def glyphHasUnusualComponents(self, thisGlyph):
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

	def glyphHasLockedComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				if thisComponent.locked:
					print("\t🔒 locked component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
					return True
		return False

	def glyphHasNestedComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				originalLayer = thisComponent.componentLayer
				if originalLayer and originalLayer.components:
					print("\t🪆 nested component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
					return True
		return False

	def glyphHasOrphanedComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				if thisComponent.component is None:
					print("\t🫥 orphaned component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
					return True
		return False

	def glyphHasEmptyComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				if thisComponent.componentLayer and not thisComponent.componentLayer.shapes:
					print("\t🫙 empty component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
					return True
		return False

	def glyphHasUnalignedComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				if thisComponent.alignment == -1:
					print("\t🤪 unaligned component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
					return True
		return False

	def glyphHasScaledComponents(self, thisGlyph, unproportional=False):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				if thisComponent.rotation == 0.0:
					hScale, vScale = thisComponent.scale
					scaled = (hScale * vScale > 0.0) and (abs(hScale) != 1.0 or abs(vScale) != 1.0)
					if scaled:
						if unproportional:
							if abs(hScale) != abs(vScale):
								print("\t🤪 unproportionally scaled component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
								return True
						else:
							print("\t📏 scaled component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
							return True
		return False

	def glyphHasUnproportionallyScaledComponents(self, thisGlyph):
		return self.glyphHasScaledComponents(thisGlyph, unproportional=True)

	def glyphHasRotatedComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				hScale, vScale = thisComponent.scale
				rotatedByScaling = hScale == vScale and hScale < 0 and vScale < 0
				if thisComponent.rotation or rotatedByScaling:
					print("\t🎡 rotated component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
					return True
		return False

	def glyphHasMirroredComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				hScale, vScale = thisComponent.scale
				if hScale * vScale < 0:
					print("\t🪞 mirrored component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
					return True
		return False

	def glyphHasShiftedComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisComponent in thisLayer.components:
				hScale, vScale = thisComponent.scale
				if hScale == 1.0 and vScale == 1.0 and thisComponent.rotation == 0.0:
					x, y = thisComponent.position
					if x != 0 or y != 0:
						print("\t🏗 shifted component %s on layer: %s" % (thisComponent.componentName, thisLayer.name))
						return True
		return False

	def glyphHasDetachedCornerComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisHint in thisLayer.hints:
				if thisHint.type == CORNER and not thisHint.originNode:
					print("\t🚨 detached corner component %s on layer: %s" % (thisHint.name, thisLayer.name))
					return True
		return False

	def glyphHasTransformedCornerComponents(self, thisGlyph):
		for thisLayer in thisGlyph.layers:
			for thisHint in thisLayer.hints:
				if thisHint.type == CORNER and (abs(thisHint.scale.x) != 1.0 or abs(thisHint.scale.y) != 1.0):
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
			verbose = self.prefBool("verbose")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			print("Component Problem Finder Report\n")
			print(f"📄 {fontFileName(thisFont)}\n")

			if self.prefBool("includeAllGlyphs"):
				glyphs = thisFont.glyphs
			else:
				glyphs = [layer.parent for layer in thisFont.selectedLayers]

			enabledPrefNames = [prefName for prefName in self.prefs if self.prefBool(prefName)]
			affectedGlyphNames = {prefName: [] for prefName in enabledPrefNames}
			shouldIncludeNonExporting = self.prefBool("includeNonExporting")

			glyphCount = len(glyphs)
			for index, thisGlyph in enumerate(glyphs):
				self.w.progress.set(100 * index / glyphCount)
				if verbose:
					print(f"🔠 {thisGlyph.name}")
					self.w.status.set(f"🔠 {thisGlyph.name}")

				if shouldIncludeNonExporting or thisGlyph.export:
					for prefName in enabledPrefNames:
						if getattr(self, f"glyphHas{prefName[0].upper()}{prefName[1:]}")(thisGlyph):
							affectedGlyphNames[prefName].append(thisGlyph.name)

			# one paragraph per problem, for the tab and the Macro Window:
			tabText = ""
			for prefName in enabledPrefNames:
				names = affectedGlyphNames[prefName]
				title = " ".join(camelCaseSplit(prefName)).capitalize()
				if names:
					tabText += f"\n{title}:\n/{'/'.join(names)}\n"
				print(f"{'⚠️' if names else '✅'} {title}: {len(names)}")

			if self.prefBool("reuseTab") and thisFont.currentTab:
				newTab = thisFont.currentTab
			else:
				newTab = thisFont.newTab()
			newTab.text = tabText.strip()

			# take time:
			timereport = reportTimeInNaturalLanguage(timer() - start)
			print(f"\nTime elapsed: {timereport}")
			self.w.status.set(f"✅ Done. {timereport}.")
			self.w.progress.set(100)

			# Final report:
			Glyphs.showNotification(thisFont.familyName, "Component Problem Finder is finished. Details in Macro Window.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Component Problem Finder Error: {e}")
			import traceback
			print(traceback.format_exc())


ComponentProblemFinder()
