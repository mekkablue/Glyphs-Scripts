# MenuTitle: Find and Replace Components
__doc__ = """
Find and replace components across the whole font (all glyphs, all masters).
Handles regular components, cap components (_cap.*), and corner components
(_corner.*). When a corner component is chosen in Find, an optional angle filter
restricts replacement to corners at specific angles. Leaving Replace empty
removes the found component (after a confirmation warning).
Optionally restrict to selected glyphs only.
"""

import math
import vanilla
from AppKit import (
	NSAlert,
	NSAlertFirstButtonReturn,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSSize,
	NSTextAlignmentRight,
	NSWindowStyleMaskResizable,
)
from Foundation import NSPoint
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton, SteppingEditText, integerFormatter, fontFileName


SPECIAL_PREFIXES = ("_cap.", "_corner.", "_segment.", "_brush.", "_head.")

scopeChoices = (
	"Current master",
	"⚠️ All masters of frontmost font",
	"⚠️ Current masters of all open fonts",
	"⚠️ All masters of all open fonts",
)


def specialKind(name):
	"""Returns the matched prefix if name is a special component, else None."""
	for prefix in SPECIAL_PREFIXES:
		if name.startswith(prefix):
			return prefix
	return None


def selectedGlyphsOfFont(thisFont):
	"""The glyphs of the selected layers, each once, in the order of selection."""
	glyphs = {}
	for layer in thisFont.selectedLayers:
		glyph = layer.parent
		if glyph and glyph.id not in glyphs:
			glyphs[glyph.id] = glyph
	return list(glyphs.values())


class FindReplaceComponents(mekkaObject):
	prefDict = {
		"findName": "",
		"replaceName": "",
		"popupScope": 1,
		"showPrediction": True,
		"selectedGlyphsOnly": False,
		"includeBackgrounds": False,
		"useAngleFilter": False,
		"largerOrSmaller": 0,
		"thresholdAngle": 20,
	}

	def __init__(self):
		windowWidth = 370
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Find and Replace Components",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		inset = 15

		# Find row
		tooltipText = "The component to find. The list has all components used in the font and all special glyphs (_cap.*, _corner.*, _segment.*, _brush.*, _head.*)."
		self.w.findLabel = vanilla.TextBox("auto", "Find", sizeStyle="small")
		self.w.findLabel.setToolTip(tooltipText)
		self.w.findName = vanilla.ComboBox("auto", self.getFindItems(), callback=self.findChanged, sizeStyle="small")
		self.w.findName.setToolTip(tooltipText)
		self.w.updateFind = UpdateButton("auto", callback=self.refreshFindItems)
		self.w.updateFind.setToolTip("Refreshes the Find list from the frontmost font. With ‘Selected glyphs only’, lists only components of the selection and picks the most frequent.")

		# Replace row
		tooltipText = "The replacement component. Empty removes the found component. For special components, the list has only the same kind."
		self.w.replaceLabel = vanilla.TextBox("auto", "Replace", sizeStyle="small")
		self.w.replaceLabel.setToolTip(tooltipText)
		self.w.replaceName = vanilla.ComboBox("auto", self.getReplaceItems(), callback=self.SavePreferences, sizeStyle="small")
		self.w.replaceName.setToolTip(tooltipText)
		self.w.updateReplace = UpdateButton("auto", callback=self.refreshReplaceItems)
		self.w.updateReplace.setToolTip("Refreshes the Replace list from the frontmost font, filtered by the kind of the Find component.")

		# the swap button spans both rows
		self.w.swapButton = vanilla.SquareButton("auto", "⇅", callback=self.swapFindReplace, sizeStyle="small")
		self.w.swapButton.setToolTip("Swaps the Find and Replace values.")

		# Scope row
		tooltipText = "Which masters to change. ‘Current master’ also includes its brace and bracket layers. Selected glyphs and the other options below apply in every case."
		self.w.scopeLabel = vanilla.TextBox("auto", "Scope", sizeStyle="small")
		self.w.scopeLabel.setToolTip(tooltipText)
		self.w.popupScope = vanilla.PopUpButton("auto", scopeChoices, callback=self.SavePreferences, sizeStyle="small")
		self.w.popupScope.setToolTip(tooltipText)

		self.w.selectedGlyphsOnly = vanilla.CheckBox("auto", "Selected glyphs only", sizeStyle="small", value=False, callback=self.SavePreferences)
		self.w.selectedGlyphsOnly.setToolTip("Only changes the selected glyphs, not the whole font. Keep all masters in the scope, to stay interpolation compatible.")
		self.w.includeBackgrounds = vanilla.CheckBox("auto", "Include backgrounds", sizeStyle="small", value=False, callback=self.SavePreferences)
		self.w.includeBackgrounds.setToolTip("Also changes the background of every layer.")

		# Angle filter row (only active for _corner.* components)
		self.w.useAngleFilter = vanilla.CheckBox("auto", "Replace corners only on angles", sizeStyle="small", value=False, callback=self.SavePreferences)
		self.w.useAngleFilter.setToolTip("Only for _corner.* components: changes only corners whose interior angle is larger or smaller than the threshold.")
		self.w.largerOrSmaller = vanilla.PopUpButton("auto", ("larger than", "smaller than"), sizeStyle="small", callback=self.SavePreferences)
		self.w.largerOrSmaller.setToolTip("Whether the corner angle has to be larger or smaller than the threshold.")
		formatter = integerFormatter(0, 360)
		self.w.thresholdAngle = SteppingEditText("auto", "20", callback=self.SavePreferences, sizeStyle="small", formatter=formatter)
		self.w.thresholdAngle.setToolTip("Threshold for the interior angle in degrees (0–360), measured at the corner node between its two neighbors.")
		self.w.degreeLabel = vanilla.TextBox("auto", "°", sizeStyle="small")
		self.w.degreeLabel.setToolTip("Degrees.")

		self.w.showPrediction = vanilla.CheckBox("auto", "🔮 Will replace – components", sizeStyle="small", value=True, callback=self.SavePreferences)
		self.w.showPrediction.setToolTip("Counts how many components will be changed with the current settings, and shows it here. Turn off for large fonts, if it slows you down.")

		# Status line and run button at bottom
		self.w.statusLine = vanilla.TextBox("auto", "", sizeStyle="small", selectable=True)
		self.w.statusLine.setToolTip("How many components were changed in the last run.")
		self.w.statusLine.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton = vanilla.Button("auto", "Replace", callback=self.run)
		self.w.runButton.setToolTip("Replaces the found component in the chosen glyphs. With an empty Replace field, removes it (after a warning).")
		self.w.setDefaultButton(self.w.runButton)
		# the button keeps its width, the status line takes the leftover space:
		self.w.runButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.statusLine.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# checkboxes and square buttons stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels: right-aligned, same width, hugging their text
		for labelName in ("findLabel", "replaceLabel", "scopeLabel"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		def alignedWith(viewName, referenceName, attribute):
			return {"view1": getattr(self.w, viewName), "attribute1": attribute, "view2": getattr(self.w, referenceName), "attribute2": attribute}

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[findLabel]-gap-[findName]-gap-[updateFind]-gap-[swapButton(>=26)]-inset-|",
				"H:|-inset-[replaceLabel]-gap-[replaceName]-gap-[updateReplace]-gap-[swapButton]-inset-|",
				"H:|-inset-[scopeLabel]-gap-[popupScope]-inset-|",
				"H:|-inset-[selectedGlyphsOnly]-gap-[includeBackgrounds]-(>=inset)-|",
				"H:|-inset-[useAngleFilter]-gap-[largerOrSmaller]-gap-[thresholdAngle(46)]-gap-[degreeLabel]-inset-|",
				"H:|-inset-[showPrediction]-(>=inset)-|",
				"H:|-inset-[statusLine]-(>=gap)-[runButton(>=80)]-inset-|",
				"V:|-inset-[findName]-row-[replaceName]-row-[popupScope]-checkGap-[selectedGlyphsOnly]-stackRow-[useAngleFilter]-stackRow-[showPrediction]-inset-[runButton]-inset-|",
				alignedWith("scopeLabel", "popupScope", "centerY"),
				alignedWith("statusLine", "runButton", "centerY"),
				alignedWith("replaceLabel", "scopeLabel", "width"),
				alignedWith("findLabel", "findName", "centerY"),
				alignedWith("updateFind", "findName", "centerY"),
				alignedWith("replaceLabel", "replaceName", "centerY"),
				alignedWith("updateReplace", "replaceName", "centerY"),
				alignedWith("includeBackgrounds", "selectedGlyphsOnly", "centerY"),
				alignedWith("largerOrSmaller", "useAngleFilter", "centerY"),
				alignedWith("thresholdAngle", "useAngleFilter", "centerY"),
				alignedWith("degreeLabel", "useAngleFilter", "centerY"),
				# the swap button reaches from the top of the Find row to the bottom of the Replace row:
				{"view1": self.w.swapButton, "attribute1": "top", "view2": self.w.findName, "attribute2": "top"},
				{"view1": self.w.swapButton, "attribute1": "bottom", "view2": self.w.replaceName, "attribute2": "bottom"},
				alignedWith("replaceLabel", "findLabel", "width"),
				alignedWith("updateReplace", "updateFind", "width"),
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkGap": 10, "stackRow": 8},
		)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

		# make the window horizontally resizable, but keep the height that Auto Layout determined.
		# (Content sizes set directly on the NSWindow, so the title bar is not counted twice.)
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()
		contentSize = nsWindow.contentView().frame().size
		nsWindow.setContentMinSize_(NSSize(contentSize.width, contentSize.height))
		nsWindow.setContentMaxSize_(NSSize(contentSize.width + 1000, contentSize.height))

	# -----------------------------------------------------------------------

	def updateUI(self, sender=None):
		try:
			findName = self.w.findName.get() or ""
			replaceName = self.w.replaceName.get() or ""
		except Exception:
			return

		isCorner = findName.startswith("_corner.")
		isEmpty = not replaceName.strip()

		# Angle filter only makes sense for _corner.*
		self.w.useAngleFilter.enable(isCorner)
		angleFilterOn = isCorner and bool(self.w.useAngleFilter.get())
		self.w.largerOrSmaller.enable(angleFilterOn)
		self.w.thresholdAngle.enable(angleFilterOn)

		# Button label: "Remove" when Replace field is empty and Find has a name
		self.w.runButton.setTitle("Remove" if (isEmpty and findName.strip()) else "Replace")

		# Only enable the button when Find has a name and the two fields differ
		self.w.runButton.enable(bool(findName.strip()) and (findName.strip() != replaceName.strip()))

		# prediction in the checkbox title:
		count = self.predictedCount() if self.w.showPrediction.get() else None
		self.w.showPrediction.setTitle(f"🔮 Will {'remove' if (isEmpty and findName.strip()) else 'replace'} {'–' if count is None else f'{count:,}'} component{'' if count == 1 else 's'}")

	# -----------------------------------------------------------------------

	def getFindItems(self):
		"""All component names used anywhere in the font + all special glyphs defined."""
		thisFont = Glyphs.font
		if not thisFont:
			return []

		used = set()
		for glyph in thisFont.glyphs:
			for layer in glyph.layers:
				for comp in layer.components:
					used.add(comp.componentName)
				for hint in layer.hints:
					name = getattr(hint, "name", None)
					if name:
						used.add(name)

		specials = set(
			g.name for g in thisFont.glyphs
			if any(g.name.startswith(p) for p in SPECIAL_PREFIXES)
		)

		return sorted(used | specials)

	def refreshFindItems(self, sender=None):
		thisFont = Glyphs.font
		if thisFont and self.prefBool("selectedGlyphsOnly"):
			# Count how often each component name appears across all layers of the selected glyphs
			counts = {}
			for glyph in selectedGlyphsOfFont(thisFont):
				for layer in glyph.layers:
					for comp in layer.components:
						name = comp.componentName
						counts[name] = counts.get(name, 0) + 1
					for hint in layer.hints:
						name = getattr(hint, "name", None)
						if name:
							counts[name] = counts.get(name, 0) + 1

			items = sorted(counts)
			self.w.findName.setItems(items)
			if items:
				# Pick most frequent; alphabetically first on ties
				best = max(items, key=lambda k: counts[k])
				self.w.findName.set(best)
				self.SavePreferences()
		else:
			self.w.findName.setItems(self.getFindItems())
		self.updateUI()

	def getReplaceItems(self, findName=None):
		"""All glyph names in the font, filtered by special kind if Find is a special component."""
		thisFont = Glyphs.font
		if not thisFont:
			return []

		if findName is None:
			try:
				findName = self.w.findName.get()
			except Exception:
				findName = ""

		kind = specialKind(findName)
		if kind:
			return sorted(g.name for g in thisFont.glyphs if g.name.startswith(kind))
		return sorted(g.name for g in thisFont.glyphs)

	def refreshReplaceItems(self, sender=None):
		self.w.replaceName.setItems(self.getReplaceItems())
		self.updateUI()

	def swapFindReplace(self, sender=None):
		findVal = self.w.findName.get()
		replaceVal = self.w.replaceName.get()
		self.w.findName.set(replaceVal)
		# Refresh Replace items first (they depend on the new Find value),
		# then set the value — otherwise setItems() would wipe the just-set text.
		self.w.replaceName.setItems(self.getReplaceItems())
		self.w.replaceName.set(findVal)
		self.SavePreferences()
		self.updateUI()

	def findChanged(self, sender=None):
		"""Called when the Find field value changes — refresh Replace list and UI."""
		self.SavePreferences()
		self.w.replaceName.setItems(self.getReplaceItems())
		self.updateUI()

	# -----------------------------------------------------------------------

	def angleBetweenVectors(self, P0, P1, P2):
		"""Interior angle at P1 between neighbors P0 and P2, in degrees (0–360)."""
		v1 = NSPoint(P0.x - P1.x, P0.y - P1.y)
		v2 = NSPoint(P2.x - P1.x, P2.y - P1.y)
		a1 = math.degrees(math.atan2(v1.y, v1.x))
		a2 = math.degrees(math.atan2(v2.y, v2.x))
		return (a1 - a2) % 360.0

	def replaceHintsInLayer(self, layer, settings, dryRun=False):
		"""
		Replace or remove special components (cap, corner, segment, brush, head) in a layer. They are hints,
		and found by their name alone, which is unique to each kind (_cap.xxx, _corner.xxx, …).
		Returns (count, messages). With dryRun, only counts.
		"""
		msgs = []
		glyphName = layer.parent.name if layer.parent else "?"
		layerName = layer.name or "—"
		findName, replaceName = settings["findName"], settings["replaceName"]

		indicesToProcess = []
		for i, hint in enumerate(layer.hints):
			if hint.name != findName:
				continue
			if settings["useAngleFilter"]:
				try:
					node = hint.originNode
					angle = self.angleBetweenVectors(node.prevNode, node, node.nextNode)
					if settings["smallerThan"] and angle >= settings["thresholdAngle"]:
						continue
					if not settings["smallerThan"] and angle <= settings["thresholdAngle"]:
						continue
				except (AttributeError, TypeError):
					pass  # skip angle check if node geometry is unavailable
			indicesToProcess.append(i)

		count = len(indicesToProcess)
		if dryRun:
			return count, msgs
		if replaceName:
			for i in indicesToProcess:
				layer.hints[i].name = replaceName
		else:
			for i in reversed(indicesToProcess):
				del layer.hints[i]

		if count > 0:
			action = "Replaced" if replaceName else "Removed"
			kind = settings["kindName"]
			msgs.append(f"\t✅ {action} {count} {kind} component{'s' if count != 1 else ''} in {glyphName}, layer: {layerName}")

		return count, msgs

	def replaceComponentsInLayer(self, layer, settings, dryRun=False):
		"""Replace or remove regular GSComponents in a layer. Returns (count, messages). With dryRun, only counts."""
		msgs = []
		glyphName = layer.parent.name if layer.parent else "?"
		layerName = layer.name or "—"
		findName, replaceName = settings["findName"], settings["replaceName"]

		if replaceName and layer.parent and layer.parent.name == replaceName:
			if not dryRun:
				msgs.append(f"\t⚠️ Cannot insert {replaceName} into itself. Skipping {glyphName}, layer: {layerName}")
			return 0, msgs

		indicesToProcess = [i for i, comp in enumerate(layer.components) if comp.componentName == findName]
		count = len(indicesToProcess)
		if dryRun:
			return count, msgs

		if replaceName:
			for i in indicesToProcess:
				layer.components[i].componentName = replaceName
		else:
			for i in reversed(indicesToProcess):
				if Glyphs.versionNumber >= 3:
					shapeIndex = layer.shapes.index(layer.components[i])
					del layer.shapes[shapeIndex]
				else:
					layer.removeComponent_(layer.components[i])

		if count > 0:
			action = "Replaced" if replaceName else "Removed"
			msgs.append(f"\t✅ {action} {count} component{'s' if count != 1 else ''} in {glyphName}, layer: {layerName}")

		return count, msgs

	def processLayer(self, layer, settings, dryRun=False):
		"""Dispatch to hint- or component-based replacement for one layer."""
		try:
			if settings["kindName"]:
				return self.replaceHintsInLayer(layer, settings, dryRun)
			return self.replaceComponentsInLayer(layer, settings, dryRun)
		except Exception as e:
			import traceback
			glyphName = layer.parent.name if (layer and layer.parent) else "?"
			return 0, [f"\t❌ Error processing {glyphName}: {e}\n{traceback.format_exc()}"]

	# -----------------------------------------------------------------------

	def currentSettings(self):
		findName = (self.pref("findName") or "").strip()
		isCorner = findName.startswith("_corner.")
		return {
			"findName": findName,
			"replaceName": (self.pref("replaceName") or "").strip(),
			"kindName": (specialKind(findName) or "")[1:-1],  # "_cap." becomes "cap"
			"useAngleFilter": self.prefBool("useAngleFilter") and isCorner,
			"smallerThan": bool(self.prefInt("largerOrSmaller")),
			"thresholdAngle": self.prefFloat("thresholdAngle"),
			"selectedGlyphsOnly": self.prefBool("selectedGlyphsOnly"),
			"includeBackgrounds": self.prefBool("includeBackgrounds"),
		}

	def targets(self):
		"""Returns (font, master IDs) tuples according to the scope. Master IDs are None for all masters."""
		scope = self.prefInt("popupScope")
		if scope in (0, 1):
			fonts = [Glyphs.font] if Glyphs.font else []
		else:
			fonts = list(Glyphs.fonts)
		targets = []
		for thisFont in fonts:
			masterIDs = None if scope in (1, 3) else [thisFont.selectedFontMaster.id]
			targets.append((thisFont, masterIDs))
		return targets

	def processFont(self, thisFont, masterIDs, settings, dryRun=False):
		"""Processes the glyphs and layers of one font. Returns (count, messages)."""
		if settings["selectedGlyphsOnly"]:
			glyphs = selectedGlyphsOfFont(thisFont)
		else:
			glyphs = list(thisFont.glyphs)

		totalCount = 0
		allMsgs = []
		for glyph in glyphs:
			for thisLayer in glyph.layers:
				# a master ID restricts the layers to the master, and its brace and bracket layers:
				if masterIDs is not None and thisLayer.associatedMasterId not in masterIDs:
					continue
				layersToProcess = [thisLayer]
				if settings["includeBackgrounds"]:
					layersToProcess.append(thisLayer.background)
				for layerToProcess in layersToProcess:
					count, msgs = self.processLayer(layerToProcess, settings, dryRun)
					totalCount += count
					allMsgs.extend(msgs)
		return totalCount, allMsgs

	def predictedCount(self):
		"""How many components would be replaced or removed with the current settings."""
		settings = self.currentSettings()
		if not settings["findName"]:
			return None
		return sum(self.processFont(thisFont, masterIDs, settings, dryRun=True)[0] for thisFont, masterIDs in self.targets())

	# -----------------------------------------------------------------------

	def run(self, sender):
		self.SavePreferences()
		targets = self.targets()
		if not targets:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			return

		settings = self.currentSettings()
		findName, replaceName = settings["findName"], settings["replaceName"]
		if not findName:
			Message(title="No Component Selected", message="Please enter or select a component name in the 'Find' field.", OKButton=None)
			return

		isEmpty = replaceName == ""
		if isEmpty:
			alert = NSAlert.alloc().init()
			alert.setMessageText_("Remove Components?")
			scope = "the selected glyphs" if settings["selectedGlyphsOnly"] else "all glyphs"
			alert.setInformativeText_(
				f"The Replace field is empty. This will REMOVE all '{findName}' components "
				f"from {scope} in the chosen scope. This action cannot be undone easily.\n\nContinue?"
			)
			alert.addButtonWithTitle_("Remove")
			alert.addButtonWithTitle_("Cancel")
			if alert.runModal() != NSAlertFirstButtonReturn:
				return

		Glyphs.clearLog()
		print("Find and Replace Components Report\n")
		print(f"\t{findName} → {replaceName or '(remove)'}\n")

		totalCount = 0
		for thisFont, masterIDs in targets:
			print(f"📄 {fontFileName(thisFont)}")
			thisFont.disableUpdateInterface()
			try:
				count, msgs = self.processFont(thisFont, masterIDs, settings)
			except Exception:
				Glyphs.showMacroWindow()
				print("\n⚠️ Script Error:\n")
				import traceback
				print(traceback.format_exc())
				raise
			finally:
				thisFont.enableUpdateInterface()
			totalCount += count
			print("\n".join(msgs) if msgs else "\t☑️ Nothing found.")
			print()

		action = "Removed" if isEmpty else "Replaced"
		noun = "hint" if settings["kindName"] else "component"
		summary = f"{action} {totalCount} {noun}{'s' if totalCount != 1 else ''}"
		print(f"Done. {summary}.")

		self.w.statusLine.set(f"✅ {summary}.")
		self.updateUI()
		Glyphs.showNotification(
			f"{noun}s {action.lower()}",
			f"{summary} in total. Details in Macro Window.",
		)


FindReplaceComponents()
