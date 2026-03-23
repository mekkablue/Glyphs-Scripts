# MenuTitle: Find and Replace Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
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
from AppKit import NSAlert
from Foundation import NSPoint
from GlyphsApp import Glyphs, CORNER, CAP, Message
from mekkablue import mekkaObject, UpdateButton


SPECIAL_PREFIXES = ("_cap.", "_corner.", "_segment.", "_brush.")


def specialKind(name):
	"""Returns the matched prefix if name is a special component, else None."""
	for prefix in SPECIAL_PREFIXES:
		if name.startswith(prefix):
			return prefix
	return None


class FindReplaceComponents(mekkaObject):
	prefDict = {
		"findName": "",
		"replaceName": "",
		"selectedGlyphsOnly": False,
		"includeBackgrounds": False,
		"useAngleFilter": False,
		"largerOrSmaller": 0,
		"thresholdAngle": 20,
	}

	def __init__(self):
		windowWidth = 370
		windowHeight = 170
		windowWidthResize = 600
		windowHeightResize = 0
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Find and Replace Components",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),
			autosaveName=self.domain("mainwindow"),
		)

		linePos, inset, lineHeight = 12, 15, 22

		# Find row
		self.w.findLabel = vanilla.TextBox((inset, linePos + 5, 60, 17), "Find:", sizeStyle="small")
		self.w.findName = vanilla.ComboBox(
			(inset + 57, linePos - 1, -inset - 52, 24),
			self.getFindItems(),
			callback=self.findChanged,
			sizeStyle="small",
		)
		self.w.findName.setToolTip(
			"Component to find. Populated with all components currently used in the font, "
			"plus all special (_cap.*, _corner.*, _segment.*, _brush.*) glyphs defined in the font. "
			"Press ↺ to refresh the list."
		)
		self.w.updateFind = UpdateButton((-inset - 47, linePos + 1, -inset - 26, 18), callback=self.refreshFindItems)
		self.w.updateFind.setToolTip("Refresh the Find list from the frontmost font.")
		self.w.findConnector = vanilla.TextBox((-inset - 21, linePos + 1, -inset, 18), "┓", sizeStyle="small")
		findBtnCenterY = linePos + 1 + 9
		linePos += lineHeight + 6

		# Swap button centred between the two rows
		swapBtnY = (findBtnCenterY + linePos + 1 + 9) // 2 - 9
		self.w.swapButton = vanilla.Button((-inset - 21, swapBtnY, -inset, 18), "↕", callback=self.swapFindReplace, sizeStyle="small")
		self.w.swapButton.setToolTip("Swap the Find and Replace values.")

		# Replace row
		self.w.replaceLabel = vanilla.TextBox((inset, linePos + 5, 60, 17), "Replace:", sizeStyle="small")
		self.w.replaceName = vanilla.ComboBox(
			(inset + 57, linePos - 1, -inset - 52, 24),
			self.getReplaceItems(),
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.replaceName.setToolTip(
			"Replacement component name. Leave empty to remove the found component (button changes to Remove). "
			"If a special component kind is selected in Find, only components of the same kind are listed. "
			"Press ↺ to refresh the list."
		)
		self.w.updateReplace = UpdateButton((-inset - 47, linePos + 1, -inset - 26, 18), callback=self.refreshReplaceItems)
		self.w.updateReplace.setToolTip("Refresh the Replace list from the frontmost font, filtered by the Find component kind.")
		self.w.replaceConnector = vanilla.TextBox((-inset - 21, linePos + 1, -inset, 18), "┛", sizeStyle="small")
		linePos += lineHeight + 6

		# Scope row
		self.w.selectedGlyphsOnly = vanilla.CheckBox(
			(inset, linePos, 165, 18),
			"Selected glyphs only",
			sizeStyle="small",
			value=False,
			callback=self.SavePreferences,
		)
		self.w.selectedGlyphsOnly.setToolTip("Restrict replacement to the currently selected glyphs. By default the whole font is processed. All masters are always included to preserve interpolation compatibility.")
		self.w.includeBackgrounds = vanilla.CheckBox(
			(inset + 170, linePos, -inset, 18),
			"Include backgrounds",
			sizeStyle="small",
			value=False,
			callback=self.SavePreferences,
		)
		self.w.includeBackgrounds.setToolTip("Also process the background layer of every treated layer.")
		linePos += lineHeight

		# Angle filter row (only active for _corner.* components)
		self.w.useAngleFilter = vanilla.CheckBox(
			(inset, linePos, 190, 18),
			"Replace corners only on angles",
			sizeStyle="small",
			value=False,
			callback=self.SavePreferences,
		)
		self.w.useAngleFilter.setToolTip("Only available for _corner.* components. Restrict replacement to corners whose interior angle is larger or smaller than the threshold.")
		self.w.largerOrSmaller = vanilla.PopUpButton(
			(inset + 193, linePos, -inset - 48, 18),
			("larger than", "smaller than"),
			sizeStyle="small",
			callback=self.SavePreferences,
		)
		self.w.largerOrSmaller.setToolTip("Replace at corners with angles larger or smaller than the threshold value.")
		self.w.thresholdAngle = vanilla.EditText(
			(-inset - 44, linePos, 30, 19),
			"20",
			sizeStyle="small",
			callback=self.SavePreferences,
		)
		self.w.thresholdAngle.setToolTip("Interior angle threshold in degrees (0–360). The angle is measured at the corner node between its two neighbors.")
		self.w.degreeLabel = vanilla.TextBox((-inset - 12, linePos + 2, 12, 14), "°", sizeStyle="small")

		# Status line and run button at bottom
		self.w.statusLine = vanilla.TextBox((inset, -inset - 18, -inset - 90, 14), "", sizeStyle="small")
		self.w.statusLine.setToolTip("Reports how many components were exchanged in the last run.")
		self.w.runButton = vanilla.Button((-inset - 80, -inset - 22, -inset, -inset), "Replace", callback=self.run)
		self.w.setDefaultButton(self.w.runButton)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	# -----------------------------------------------------------------------

	def updateUI(self, sender=None):
		try:
			findName = self.w.findName.get()
			replaceName = self.w.replaceName.get()
		except Exception:
			return

		isCorner = findName.startswith("_corner.")
		isEmpty = replaceName.strip() == ""

		# Angle filter only makes sense for _corner.*
		self.w.useAngleFilter.enable(isCorner)
		angleFilterOn = isCorner and bool(self.w.useAngleFilter.get())
		self.w.largerOrSmaller.enable(angleFilterOn)
		self.w.thresholdAngle.enable(angleFilterOn)

		# Button label: "Remove" when Replace field is empty and Find has a name
		self.w.runButton.setTitle("Remove" if (isEmpty and findName.strip()) else "Replace")

		# Only enable the button when Find has a name and the two fields differ
		self.w.runButton.enable(bool(findName.strip()) and (findName.strip() != replaceName.strip()))

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
			# Collect only the glyphs currently selected in the font
			seenIDs = {}
			for layer in thisFont.selectedLayers:
				glyph = layer.parent
				if glyph and glyph.id not in seenIDs:
					seenIDs[glyph.id] = glyph
			selectedGlyphs = list(seenIDs.values())

			# Count how often each component name appears across all layers
			counts = {}
			for glyph in selectedGlyphs:
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
		self.w.replaceName.set(findVal)
		self.SavePreferences()
		self.w.replaceName.setItems(self.getReplaceItems())
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

	def _replaceHintsInLayer(self, layer, findName, replaceName, hintType, useAngleFilter, smallerThan, thresholdAngle):
		"""Replace or remove corner/cap hints in a layer. Returns (count, messages)."""
		count = 0
		msgs = []
		glyphName = layer.parent.name if layer.parent else "?"
		layerName = layer.name or "—"

		indicesToProcess = []
		for i, hint in enumerate(layer.hints):
			if hint.type != hintType or hint.name != findName:
				continue
			if useAngleFilter and hintType == CORNER:
				try:
					node = hint.originNode
					angle = self.angleBetweenVectors(node.prevNode, node, node.nextNode)
					if smallerThan and angle >= thresholdAngle:
						continue
					if not smallerThan and angle <= thresholdAngle:
						continue
				except (AttributeError, TypeError):
					pass  # skip angle check if node geometry is unavailable
			indicesToProcess.append(i)

		count = len(indicesToProcess)
		if replaceName:
			for i in indicesToProcess:
				layer.hints[i].name = replaceName
		else:
			for i in reversed(indicesToProcess):
				del layer.hints[i]

		if count > 0:
			action = "Replaced" if replaceName else "Removed"
			kind = "corner" if hintType == CORNER else "cap"
			msgs.append(f"\t✅ {action} {count} {kind} component{'s' if count != 1 else ''} in {glyphName}, layer: {layerName}")

		return count, msgs

	def _replaceComponentsInLayer(self, layer, findName, replaceName):
		"""Replace or remove regular GSComponents in a layer. Returns (count, messages)."""
		count = 0
		msgs = []
		glyphName = layer.parent.name if layer.parent else "?"
		layerName = layer.name or "—"

		if replaceName and layer.parent and layer.parent.name == replaceName:
			msgs.append(f"\t⚠️ Cannot insert {replaceName} into itself. Skipping {glyphName}, layer: {layerName}")
			return 0, msgs

		indicesToProcess = [
			i for i, comp in enumerate(layer.components)
			if comp.componentName == findName
		]
		count = len(indicesToProcess)

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

	def processLayer(self, layer, findName, replaceName, isCorner, isCap, useAngleFilter, smallerThan, thresholdAngle):
		"""Dispatch to hint- or component-based replacement for one layer."""
		try:
			if isCorner or isCap:
				hintType = CORNER if isCorner else CAP
				return self._replaceHintsInLayer(layer, findName, replaceName, hintType, useAngleFilter, smallerThan, thresholdAngle)
			else:
				return self._replaceComponentsInLayer(layer, findName, replaceName)
		except Exception as e:
			import traceback
			glyphName = layer.parent.name if (layer and layer.parent) else "?"
			return 0, [f"\t❌ Error processing {glyphName}: {e}\n{traceback.format_exc()}"]

	# -----------------------------------------------------------------------

	def run(self, sender):
		thisFont = Glyphs.font
		if not thisFont:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			return

		self.SavePreferences()

		findName = self.pref("findName").strip()
		replaceName = self.pref("replaceName").strip()

		if not findName:
			Message(title="No Component Selected", message="Please enter or select a component name in the 'Find' field.", OKButton=None)
			return

		isEmpty = replaceName == ""
		isCorner = findName.startswith("_corner.")
		isCap = findName.startswith("_cap.")
		useAngleFilter = self.prefBool("useAngleFilter") and isCorner
		smallerThan = bool(self.prefInt("largerOrSmaller"))
		thresholdAngle = self.prefFloat("thresholdAngle")
		selectedGlyphsOnly = self.prefBool("selectedGlyphsOnly")
		includeBackgrounds = self.prefBool("includeBackgrounds")

		if isEmpty:
			alert = NSAlert.alloc().init()
			alert.setMessageText_("Remove Components?")
			scope = "the selected glyphs" if self.prefBool("selectedGlyphsOnly") else "the entire font"
			alert.setInformativeText_(
				f"The Replace field is empty. This will REMOVE all '{findName}' components "
				f"from {scope}. This action cannot be undone easily.\n\nContinue?"
			)
			alert.addButtonWithTitle_("Remove")
			alert.addButtonWithTitle_("Cancel")
			if alert.runModal() != 1000:  # 1000 = NSAlertFirstButtonReturn
				return

		Glyphs.clearLog()
		print(f"Find and Replace Components — {thisFont.familyName}")
		if thisFont.filepath:
			print(thisFont.filepath)
		else:
			print("⚠️ Font has not been saved yet.")
		print()

		totalCount = 0
		allMsgs = []

		# Determine glyph scope: whole font or selected glyphs only.
		# Always process ALL layers of each glyph to keep masters in sync.
		if selectedGlyphsOnly:
			seenIDs = {}
			for layer in thisFont.selectedLayers:
				glyph = layer.parent
				if glyph and glyph.id not in seenIDs:
					seenIDs[glyph.id] = glyph
			glyphs = list(seenIDs.values())
		else:
			glyphs = list(thisFont.glyphs)

		thisFont.disableUpdateInterface()
		try:
			for glyph in glyphs:
				allMsgs.append(f"Processing {glyph.name}:")
				for lyr in glyph.layers:
					c, msgs = self.processLayer(lyr, findName, replaceName, isCorner, isCap, useAngleFilter, smallerThan, thresholdAngle)
					totalCount += c
					allMsgs.extend(msgs)
					if includeBackgrounds:
						c, msgs = self.processLayer(lyr.background, findName, replaceName, isCorner, isCap, useAngleFilter, smallerThan, thresholdAngle)
						totalCount += c
						allMsgs.extend(msgs)

		except Exception as e:
			Glyphs.showMacroWindow()
			print("\n⚠️ Script Error:\n")
			import traceback
			print(traceback.format_exc())
			raise e
		finally:
			thisFont.enableUpdateInterface()

		print("\n".join(allMsgs))

		action = "Removed" if isEmpty else "Replaced"
		noun = "hint" if (isCorner or isCap) else "component"
		summary = f"{action} {totalCount} {noun}{'s' if totalCount != 1 else ''}"
		print(f"\nDone. {summary}.")

		self.w.statusLine.set(f"↔ {summary}.")
		Glyphs.showNotification(
			f"{thisFont.familyName}: {noun}s {action.lower()}",
			f"{summary} in total. Details in Macro Window.",
		)


FindReplaceComponents()
