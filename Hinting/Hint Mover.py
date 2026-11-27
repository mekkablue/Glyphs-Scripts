# MenuTitle: Hint Mover
__doc__ = """
Transfers PS and/or TT hints from other masters to a target master, and/or removes the hints of other masters, so that only the target master keeps its hints. Optionally adds a ‘Get Hints From Master’ parameter to the font’s Font Info > Exports.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, GSCustomParameter, Message
from mekkablue import mekkaObject, UpdateButton, makeWindowResizable

parameterName = "Get Hints From Master"
allOtherMasters = "all other masters"
separator = "---"
scopes = ("selected glyphs", "all glyphs")


def isPSHint(hint):
	return hint.isPostScript


def isTTHint(hint):
	return hint.isTrueType


class HintMover(mekkaObject):
	prefDict = {
		"targetMaster": 0,
		"psHints": True,
		"ttHints": True,
		"transfer": True,
		"transferFrom": 0,
		"keepTargetOnly": False,
		"addParameter": False,
		"scope": 1,
	}

	def __init__(self):
		windowWidth = 420
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Hint Mover",
			autosaveName=self.domain("mainwindow"),  # stores last window position and width
		)

		inset = 15

		self.w.descriptionText = vanilla.TextBox(
			"auto",
			"Rearrange hints between masters",
			sizeStyle="small",
			selectable=True,
		)

		self.w.targetMasterLabel = vanilla.TextBox("auto", "Target Master:", sizeStyle="small", selectable=True)
		tooltip = "The master that receives the hints, and keeps its hints if you choose to remove the hints in all other masters."
		self.w.targetMasterLabel.setToolTip(tooltip)
		self.w.targetMaster = vanilla.PopUpButton("auto", [], sizeStyle="small", callback=self.SavePreferences)
		self.w.targetMaster.setToolTip(tooltip)
		self.w.updateMasters = UpdateButton("auto", callback=self.updateMasters)
		self.w.updateMasters.setToolTip("Resets the masters in the popups to the masters of the frontmost font.")

		self.w.hintTypesLabel = vanilla.TextBox("auto", "Hint types:", sizeStyle="small", selectable=True)
		self.w.hintTypesLabel.setToolTip("Which kinds of hints the script moves or removes.")
		self.w.psHints = vanilla.CheckBox("auto", "PS hints", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.psHints.setToolTip("PostScript hints: stem hints and ghost hints.")
		self.w.ttHints = vanilla.CheckBox("auto", "TT hints", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.ttHints.setToolTip("TrueType hints: stem, anchor, align, interpolate, diagonal and delta hints.")

		self.w.transfer = vanilla.CheckBox("auto", "Transfer hints to target master from", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.transfer.setToolTip(
			"Copies the hints of the chosen type(s) to the target master. Only applies to compatible masters, i.e., glyphs whose layers have the same paths and nodes; others are skipped. "
			"Never duplicates a hint. PS hints are never attached to the same node twice, except one horizontal and one vertical."
		)
		self.w.transferFrom = vanilla.PopUpButton("auto", [], sizeStyle="small", callback=self.SavePreferences)
		self.w.transferFrom.setToolTip("The master to take the hints from. Only compatible masters receive hints. ‘all other masters’ takes the hints of the first compatible master that has them.")

		self.w.keepTargetOnly = vanilla.CheckBox("auto", "Keep target master hints only", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.keepTargetOnly.setToolTip(
			"Deletes the hints of the chosen type(s) in all other masters, including their special layers (brace and bracket layers). "
			"The target master and its special layers keep their hints. If transferring is on, it happens first."
		)

		self.w.addParameter = vanilla.CheckBox("auto", f"Add ‘{parameterName}’ parameter", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.addParameter.setToolTip(
			f"Adds a ‘{parameterName}’ custom parameter with the target master to Font Info > Exports of the font, "
			"so all instances export with the hints of the target master. Removes any previous parameters of that name."
		)

		self.w.scopeLabel = vanilla.TextBox("auto", "Scope:", sizeStyle="small", selectable=True)
		self.w.scope = vanilla.PopUpButton("auto", scopes, sizeStyle="small", callback=self.SavePreferences)
		self.w.scopeLabel.setToolTip("Which glyphs are processed. Transferring only applies to glyphs whose masters are compatible with the target master.")
		self.w.scope.setToolTip("‘selected glyphs’ processes the glyphs of the selected layers, ‘all glyphs’ processes the complete font.")

		self.w.status = vanilla.TextBox("auto", "🤖 Ready. 💬 See tooltips for help.", sizeStyle="small", selectable=True)
		self.w.status.setToolTip("Reports what the script is doing and what it did.")
		self.w.runButton = vanilla.Button("auto", "Apply", callback=self.run)
		self.w.runButton.setToolTip("Transfers and/or removes hints as set above.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels hug and keep their width, the popups take the leftover width:
		for labelName in ("targetMasterLabel", "hintTypesLabel", "scopeLabel"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		self.w.transfer.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		for popupName in ("targetMaster", "transferFrom", "scope"):
			getattr(self.w, popupName).getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		self.w.updateMasters.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.updateMasters.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		labelNames = ("targetMasterLabel", "hintTypesLabel", "scopeLabel")
		widestLabel = "targetMasterLabel"
		widthRules = [
			{"view1": getattr(self.w, name), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for name in labelNames if name != widestLabel
		]
		for name in labelNames:
			getattr(self.w, name).getNSTextField().setAlignment_(2)  # NSTextAlignmentRight

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[targetMasterLabel]-gap-[targetMaster(>=120)]-gap-[updateMasters]-inset-|",
				"H:|-inset-[hintTypesLabel]-gap-[psHints]-gap-[ttHints]-(>=inset)-|",
				"H:|-inset-[scopeLabel]-gap-[scope(>=120)]-inset-|",
				"H:|-inset-[transfer]-gap-[transferFrom(>=100)]-inset-|",
				"H:|-inset-[keepTargetOnly]-(>=inset)-|",
				"H:|-inset-[addParameter]-(>=inset)-|",
								"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText(30)]-row-[targetMaster]-row-[psHints]-row-[scope]-row-[transferFrom]-stackRow-[keepTargetOnly]-stackRow-[addParameter]-inset-[runButton]-inset-|",
				{"view1": self.w.targetMasterLabel, "attribute1": "centerY", "view2": self.w.targetMaster, "attribute2": "centerY"},
				{"view1": self.w.updateMasters, "attribute1": "centerY", "view2": self.w.targetMaster, "attribute2": "centerY"},
				{"view1": self.w.hintTypesLabel, "attribute1": "centerY", "view2": self.w.psHints, "attribute2": "centerY"},
				{"view1": self.w.ttHints, "attribute1": "centerY", "view2": self.w.psHints, "attribute2": "centerY"},
				{"view1": self.w.transfer, "attribute1": "centerY", "view2": self.w.transferFrom, "attribute2": "centerY"},
				{"view1": self.w.scopeLabel, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 8, "stackRow": 8},
		)

		makeWindowResizable(self.w)

		self.populateMasters()
		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def font(self):
		return Glyphs.font

	def populateMasters(self):
		"""Fills the target and source popups from the frontmost font. Keeps the chosen indexes where possible."""
		font = self.font()
		masterNames = [master.name for master in font.masters] if font else []
		self.w.targetMaster.setItems(masterNames)
		self.updateSourceItems()

	def updateSourceItems(self):
		font = self.font()
		target = self.w.targetMaster.get()
		otherNames = [master.name for index, master in enumerate(font.masters) if index != target] if font else []
		self.w.transferFrom.setItems(otherNames + [separator, allOtherMasters])

	def updateMasters(self, sender=None):
		self.populateMasters()
		self.w.targetMaster.set(0)
		self.SavePreferences()

	def otherMasters(self):
		font = self.font()
		target = self.w.targetMaster.get()
		return [master for index, master in enumerate(font.masters) if index != target] if font else []

	def sourceMasters(self):
		"""The masters chosen in the popup."""
		others = self.otherMasters()
		choice = self.w.transferFrom.get()
		if choice < len(others):
			return [others[choice]]
		return others  # all other masters (the separator is not selectable, but just in case)

	def updateUI(self, sender=None):
		font = self.font()
		hasHintTypes = self.w.psHints.get() or self.w.ttHints.get()
		hasOtherMasters = bool(font) and len(font.masters) > 1
		self.w.transfer.enable(hasOtherMasters)
		self.w.transferFrom.enable(hasOtherMasters and self.w.transfer.get())
		self.w.keepTargetOnly.enable(hasOtherMasters)
		# no hint type, nothing to do:
		self.w.runButton.enable(bool(font) and bool(hasHintTypes))

	def SavePreferences(self, sender=None):
		# changing the target master changes the source popup items:
		if sender is self.w.targetMaster:
			self.updateSourceItems()
			self.w.transferFrom.set(0)
		super().SavePreferences(sender)

	def LoadPreferences(self):
		super().LoadPreferences()
		self.updateSourceItems()
		sourceCount = self.w.transferFrom.getNSPopUpButton().numberOfItems()
		if self.prefInt("transferFrom") < sourceCount:
			self.w.transferFrom.set(self.prefInt("transferFrom"))
		self.updateUI()

	# --- hint handling ---

	@staticmethod
	def nodeKey(layer, node):
		"""(path index, node index) of a node in a layer, or None, e.g. for components or foreign nodes."""
		if node is None:
			return None
		for pathIndex, path in enumerate(layer.paths):
			if node.parent == path:
				return (pathIndex, node.index)
		return None

	@staticmethod
	def nodeAt(layer, key):
		pathIndex, nodeIndex = key
		return layer.paths[pathIndex].nodes[nodeIndex]

	def hintNodeKeys(self, layer, hint):
		"""Keys of all nodes the hint is attached to, in the order origin, target, other 1, other 2. None for missing ones."""
		return tuple(self.nodeKey(layer, node) for node in (hint.originNode, hint.targetNode, hint.otherNode1, hint.otherNode2))

	@staticmethod
	def layersCompatible(layerA, layerB):
		pathsA, pathsB = layerA.paths, layerB.paths
		if len(pathsA) != len(pathsB):
			return False
		return all(len(a.nodes) == len(b.nodes) for a, b in zip(pathsA, pathsB))

	@staticmethod
	def typeMatches(hint, wantPS, wantTT):
		return (wantPS and isPSHint(hint)) or (wantTT and isTTHint(hint))

	def transferHints(self, sourceLayer, targetLayer, wantPS, wantTT):
		"""Copies the wanted hints from sourceLayer to targetLayer. Returns the number of hints added."""
		if not self.layersCompatible(sourceLayer, targetLayer):
			return -1

		# signatures of existing hints, to avoid duplicates:
		existingSignatures = set()
		usedPSNodes = set()  # (node key, horizontal)
		for hint in targetLayer.hints:
			keys = self.hintNodeKeys(targetLayer, hint)
			existingSignatures.add((hint.type, bool(hint.horizontal), keys))
			if isPSHint(hint):
				for key in keys[:2]:
					if key is not None:
						usedPSNodes.add((key, bool(hint.horizontal)))

		addedCount = 0
		for hint in tuple(sourceLayer.hints):
			if not self.typeMatches(hint, wantPS, wantTT):
				continue
			keys = self.hintNodeKeys(sourceLayer, hint)
			if keys[0] is None:
				continue  # detached or attached to a component
			signature = (hint.type, bool(hint.horizontal), keys)
			if signature in existingSignatures:
				continue
			psNodes = [(key, bool(hint.horizontal)) for key in keys[:2] if key is not None]
			if isPSHint(hint) and any(psNode in usedPSNodes for psNode in psNodes):
				continue
			newHint = hint.copy()
			newHint.originNode = self.nodeAt(targetLayer, keys[0])
			newHint.targetNode = self.nodeAt(targetLayer, keys[1]) if keys[1] else None
			newHint.otherNode1 = self.nodeAt(targetLayer, keys[2]) if keys[2] else None
			newHint.otherNode2 = self.nodeAt(targetLayer, keys[3]) if keys[3] else None
			targetLayer.hints.append(newHint)
			existingSignatures.add(signature)
			usedPSNodes.update(psNodes)
			addedCount += 1
		return addedCount

	def removeHints(self, layer, wantPS, wantTT):
		removedCount = 0
		for index in reversed(range(len(layer.hints))):
			if self.typeMatches(layer.hints[index], wantPS, wantTT):
				del layer.hints[index]
				removedCount += 1
		return removedCount

	def setParameter(self, font, targetMaster):
		"""Removes all previous parameters and adds a new one. Returns True."""
		for index in reversed(range(len(font.customParameters))):
			if font.customParameters[index].name == parameterName:
				del font.customParameters[index]
		font.customParameters.append(GSCustomParameter(parameterName, targetMaster.id))

	def run(self, sender=None):
		font = self.font()
		if not font:
			self.setStatus("⚠️ No font open.")
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			return

		self.SavePreferences()
		wantPS, wantTT = self.prefBool("psHints"), self.prefBool("ttHints")
		doTransfer, doRemove = self.prefBool("transfer"), self.prefBool("keepTargetOnly")
		target = font.masters[min(self.prefInt("targetMaster"), len(font.masters) - 1)]
		sources = self.sourceMasters() if doTransfer else []
		otherIDs = tuple(master.id for master in font.masters if master != target)

		if self.prefInt("scope") == 0:
			glyphs = []
			for layer in font.selectedLayers:
				if layer.parent not in glyphs:
					glyphs.append(layer.parent)
		else:
			glyphs = list(font.glyphs)

		Glyphs.clearLog()
		print("Hint Mover Report\n")
		print(f"Font: {font.familyName}, target master: {target.name}")
		addedCount = removedCount = skippedCount = 0
		font.disableUpdateInterface()
		try:
			self.setStatus("🛠️ Moving hints…")
			if wantPS or wantTT:
				for glyph in glyphs:
					self.setStatus(f"🔠 {glyph.name}")
					targetLayer = glyph.layers[target.id]
					if doTransfer:
						for master in sources:
							sourceLayer = glyph.layers[master.id]
							result = self.transferHints(sourceLayer, targetLayer, wantPS, wantTT)
							if result < 0:
								if sourceLayer.shapes and targetLayer.shapes:
									print(f"\t⚠️ {glyph.name}: {master.name} incompatible with {target.name}, skipped")
								skippedCount += 1
							elif result:
								print(f"\t✅ {glyph.name}: {result} hint{'' if result == 1 else 's'} from {master.name}")
								addedCount += result
					if doRemove:
						for layer in glyph.layers:
							if layer.associatedMasterId in otherIDs:
								removedCount += self.removeHints(layer, wantPS, wantTT)
			if self.prefBool("addParameter"):
				self.setParameter(font, target)
				print(f"\n💾 Added ‘{parameterName}’ parameter for {target.name}.")
		except Exception as e:
			Glyphs.showMacroWindow()
			self.setStatus("❌ Error, see Macro Window.")
			print(f"Hint Mover Error: {e}")
			import traceback
			print(traceback.format_exc())
			return
		finally:
			font.enableUpdateInterface()

		parts = []
		if doTransfer:
			parts.append(f"transferred {addedCount} hint{'' if addedCount == 1 else 's'}")
		if doRemove:
			parts.append(f"removed {removedCount} hint{'' if removedCount == 1 else 's'}")
		if self.prefBool("addParameter"):
			parts.append(f"added ‘{parameterName}’")
		summary = ", ".join(parts).capitalize() if parts else "Nothing to do"
		if skippedCount:
			summary += f" ({skippedCount} incompatible layer{'' if skippedCount == 1 else 's'} skipped)"
		self.setStatus(f"✅ {summary}.")
		print(f"\n{summary}.")
		Glyphs.showNotification("Hint Mover", f"{summary}. Details in Macro Window.")


HintMover()
