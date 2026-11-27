# MenuTitle: Fix STAT (OTVAR)
__doc__ = """
Run this right after a variable font export. Fixes the STAT table of the most recent variable font export(s) of the frontmost font. Choose the fixes you need: Regular names and elidable flags, Format 1/3 duplicates, style linking (Format 3), and upgrading discrete axis values to ranges (Format 2). Needs the FontTools module.
"""

from os import path
import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired
from fontTools import ttLib
from fontTools.ttLib.tables import otTables
from otvarLib import currentOTVarExportPath, otVarFileName
from fixStyleLinking import fixStyleLinking
from mekkablue import mekkaObject, makeWindowResizable
from GlyphsApp import Glyphs, INSTANCETYPEVARIABLE, Message


def statAxisTags(statTable):
	"""Returns the axis tags of the STAT table, or None if there are no design axes or axis values."""
	if not statTable.DesignAxisRecord or getattr(statTable, "AxisValueArray", None) is None:
		return None
	return [axis.AxisTag for axis in statTable.DesignAxisRecord.Axis]


def setAxisValues(statTable, axisValues):
	statTable.AxisValueArray.AxisValue = axisValues
	statTable.AxisValueCount = len(axisValues)


def nameOfID(nameTable, nameID):
	nameRecord = nameTable.getName(nameID, 3, 1, 1033)
	return nameRecord.toUnicode() if nameRecord else None


def isNormalValue(axisTag, axisValue):
	"""Normal axis value: wght=400, wdth=100, and 0 on all other axes."""
	if axisTag == "wght":
		return axisValue == 400
	if axisTag == "wdth":
		return axisValue == 100
	return axisValue == 0


def axisValueOf(statEntry):
	return statEntry.NominalValue if statEntry.Format == 2 else statEntry.Value


def normalNameFor(axisTag, mode):
	"""Name for the normal value of an axis; mode is the index of the popup in the window."""
	if mode == 2 and axisTag == "wdth":
		return "Normal"
	if mode >= 1 and axisTag == "ital":
		return "Roman"
	return "Regular"


def nameIDForString(nameTable, string):
	"""Returns the ID of the name table entry with that string (Windows English first), adds it if there is none."""
	candidates = [entry for entry in nameTable.names if entry.toUnicode() == string]
	candidates.sort(key=lambda entry: (entry.platformID != 3, entry.nameID))
	if candidates:
		return candidates[0].nameID
	nameID = nameTable.addName(string, platforms=((3, 1, 1033), ), minNameID=max([entry.nameID for entry in nameTable.names] + [255]))
	print(f"  📛 Adding name ID {nameID} ‘{string}’.")
	return nameID


def setNormalNames(font, mode):
	"""Sets the names of the normal axis values, see normalNameFor(). Returns True if changed."""
	statTable = font["STAT"].table
	axes = statAxisTags(statTable)
	if axes is None:
		print("  ⚠️ STAT table has no design axes or axis values. Skipping.")
		return False

	nameTable = font["name"]
	changesMade = False
	for statIndex, statEntry in enumerate(statTable.AxisValueArray.AxisValue):
		if statEntry.Format == 4:
			continue
		axisTag = axes[statEntry.AxisIndex]
		axisValue = axisValueOf(statEntry)
		if not isNormalValue(axisTag, axisValue):
			continue
		newName = normalNameFor(axisTag, mode)
		newNameID = nameIDForString(nameTable, newName)
		oldNameID = statEntry.ValueNameID
		if oldNameID == newNameID:
			print(f"  🏛️ STAT axis value {statIndex}, {axisTag}={axisValue}: already ‘{newName}’.")
		else:
			print(f"  🏛️ STAT axis value {statIndex}, {axisTag}={axisValue}: name ID {oldNameID} ‘{nameOfID(nameTable, oldNameID)}’ → {newNameID} ‘{newName}’")
			statEntry.ValueNameID = newNameID
			changesMade = True
	return changesMade


def makeNormalValuesElidable(font):
	"""Makes the normal axis values elidable (Flags bit 2). Returns True if changed."""
	statTable = font["STAT"].table
	axes = statAxisTags(statTable)
	if axes is None:
		print("  ⚠️ STAT table has no design axes or axis values. Skipping.")
		return False

	changesMade = False
	for statIndex, statEntry in enumerate(statTable.AxisValueArray.AxisValue):
		if statEntry.Format == 4:
			continue
		axisTag = axes[statEntry.AxisIndex]
		axisValue = axisValueOf(statEntry)
		if isNormalValue(axisTag, axisValue) and not statEntry.Flags & 2:
			print(f"  🏛️ STAT axis value {statIndex}, {axisTag}={axisValue}: flags {statEntry.Flags} → {statEntry.Flags | 2} (elidable)")
			statEntry.Flags |= 2
			changesMade = True
	return changesMade


def removeFormat1Duplicates(font):
	"""Deletes Format 1 axis values if an equivalent Format 3 exists. Returns True if changed."""
	statTable = font["STAT"].table
	axes = statAxisTags(statTable)
	if axes is None:
		print("  ⚠️ STAT table has no design axes or axis values. Skipping.")
		return False

	axisValues = statTable.AxisValueArray.AxisValue
	format3entries = {(axes[statEntry.AxisIndex], statEntry.Value) for statEntry in axisValues if statEntry.Format == 3}
	if not format3entries:
		print("  🤷🏻‍♀️ No Format 3 axis values, so no duplicates possible.")
		return False

	# the table is rebuilt without the Format 1 duplicates:
	keptAxisValues = []
	for statEntry in axisValues:
		if statEntry.Format == 1 and (axes[statEntry.AxisIndex], statEntry.Value) in format3entries:
			print(f"  ⛔️ Deleting Format 1 axis value {axes[statEntry.AxisIndex]}={statEntry.Value}, because an equivalent Format 3 exists.")
		else:
			keptAxisValues.append(statEntry)
	if len(keptAxisValues) == len(axisValues):
		return False
	setAxisValues(statTable, keptAxisValues)
	return True


def upgradeToRanges(font):
	"""Turns Format 1 (discrete) axis values into Format 2 (range) for axes with more than one value. Returns True if changed."""
	statTable = font["STAT"].table
	axes = statAxisTags(statTable)
	if axes is None:
		print("  ⚠️ STAT table has no design axes or axis values. Skipping.")
		return False
	fvarAxes = {axis.axisTag: axis for axis in font["fvar"].axes} if "fvar" in font else {}

	axisValues = statTable.AxisValueArray.AxisValue
	entriesByTag = {axisTag: [] for axisTag in axes}
	usedEntries = set()
	for index, axisValue in enumerate(axisValues):
		if axisValue.Format not in (1, 3):
			continue
		entryKey = (axisValue.AxisIndex, axisValue.Value)
		if entryKey in usedEntries:
			continue  # same value twice in STAT
		usedEntries.add(entryKey)
		axisTag = axes[axisValue.AxisIndex]
		entriesByTag[axisTag].append((index, axisValue))

	overwriteCount = 0
	replacements = {}  # index → (Format 2 entry, Format 3 entry to keep right behind it, or None)
	for axisTag, axisEntries in entriesByTag.items():
		if len(axisEntries) < 2:
			continue
		axisEntries.sort(key=lambda indexAndValue: indexAndValue[1].Value)
		fvarAxis = fvarAxes.get(axisTag)
		lastIndex = len(axisEntries) - 1
		for position, (index, oldAxisValue) in enumerate(axisEntries):
			currValue = oldAxisValue.Value
			prevValue = axisEntries[max(0, position - 1)][1].Value
			nextValue = axisEntries[min(lastIndex, position + 1)][1].Value
			rangeMin = (prevValue + currValue) / 2
			rangeMax = (nextValue + currValue) / 2

			# the extreme axis values reach out to the ends of the axis:
			if fvarAxis is not None and position == 0:
				rangeMin = min(fvarAxis.minValue, currValue)
			if fvarAxis is not None and position == lastIndex:
				rangeMax = max(fvarAxis.maxValue, currValue)

			newAxisValue = otTables.AxisValue()
			newAxisValue.Format = 2
			newAxisValue.ValueNameID = oldAxisValue.ValueNameID
			newAxisValue.Flags = oldAxisValue.Flags
			newAxisValue.AxisIndex = oldAxisValue.AxisIndex
			newAxisValue.RangeMinValue = rangeMin
			newAxisValue.NominalValue = currValue
			newAxisValue.RangeMaxValue = rangeMax
			replacements[index] = (newAxisValue, oldAxisValue if oldAxisValue.Format == 3 else None)
			overwriteCount += 1
			print(f"  🏛️ {axisTag}: Format {oldAxisValue.Format} → 2 (range): {rangeMin} → {currValue} → {rangeMax}, flags {newAxisValue.Flags}")

	if overwriteCount == 0:
		print("  🤷🏻‍♀️ No axis with more than one discrete axis value.")
		return False
	# a Format 3 entry (style linking) is kept side-by-side with its corresponding Format 2 entry:
	newAxisValues = []
	for index, axisValue in enumerate(axisValues):
		if index in replacements:
			rangeEntry, styleLinkEntry = replacements[index]
			newAxisValues.append(rangeEntry)
			if styleLinkEntry is not None:
				newAxisValues.append(styleLinkEntry)
				print(f"  🏛️ Keeping Format 3 (style linking) entry {styleLinkEntry.Value} → {styleLinkEntry.LinkedValue} right behind its Format 2 entry.")
		else:
			newAxisValues.append(axisValue)
	setAxisValues(statTable, newAxisValues)
	return True


def exportFolderOfInstance(thisFont, instance):
	# instance parameter first, then font-wide
	for owner in (instance, thisFont):
		parameter = owner.customParameterActiveForKey_("Export Folder")
		if parameter:
			return parameter.value
	return None


class FixSTAT(mekkaObject):
	prefDict = {
		"normalNames": True,
		"normalNamesMode": 2,
		"makeElidable": True,
		"styleLinking": True,
		"removeDuplicates": True,
		"upgradeToRanges": False,
	}

	# the popup has no checkbox of its own:
	checkBoxNames = ("normalNames", "makeElidable", "styleLinking", "removeDuplicates", "upgradeToRanges")
	normalNamesOptions = (
		"Regular",
		"Roman (ital=0), Regular (all others)",
		"Normal (wdth=100), Roman (ital=0), Regular (all others)",
	)

	# in the order they are applied (style linking first, so that the elidable step also covers an ital entry it adds):
	fixes = (
		("styleLinking", "Style linking", lambda font, mode: fixStyleLinking(font, setElidable=False)),
		("normalNames", "Set names of normal axis values", lambda font, mode: setNormalNames(font, mode)),
		("makeElidable", "Make normal values elidable", lambda font, mode: makeNormalValuesElidable(font)),
		("removeDuplicates", "Remove Format 1 duplicates", lambda font, mode: removeFormat1Duplicates(font)),
		("upgradeToRanges", "Upgrade discrete to ranges", lambda font, mode: upgradeToRanges(font)),
	)

	def __init__(self):
		windowWidth = 440
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Fix STAT (OTVAR)",
			autosaveName=self.domain("mainwindow"),  # stores last window position and width
		)

		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Fixes STAT in the most recent OTVAR export:", sizeStyle="small", selectable=True)

		self.w.normalNames = vanilla.CheckBox("auto", "Set normal axis values to", value=True, callback=self.SavePreferences, sizeStyle="small")
		normalNamesTip = "Renames the normal axis value of every axis (wght=400, wdth=100, all others 0), adding the name to the name table if necessary. Pick the names in the popup. Typically only necessary in italic exports with two or more axes."
		self.w.normalNames.setToolTip(normalNamesTip)
		self.w.normalNamesMode = vanilla.PopUpButton("auto", self.normalNamesOptions, callback=self.SavePreferences, sizeStyle="small")
		self.w.normalNamesMode.setToolTip(normalNamesTip)
		self.w.makeElidable = vanilla.CheckBox("auto", "Make normal values elidable", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.makeElidable.setToolTip("Sets the elidable flag (Flags=2) on the normal axis values (wght=400, wdth=100, all others 0), so software leaves them out of composed style names.")
		self.w.styleLinking = vanilla.CheckBox("auto", "Style linking: wght 400→700, ital 0→1, slnt 0→−max", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.styleLinking.setToolTip("Turns the axis values wght=400 and ital=0 (or slnt=0 if there is no ital axis) into elidable Format 3 entries linking to wght=700, ital=1 or the most negative slnt. Does not touch the elidable flags, use the elidable option for that.")
		self.w.removeDuplicates = vanilla.CheckBox("auto", "Remove Format 1 duplicates of Format 3", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.removeDuplicates.setToolTip("If an axis value exists as Format 3 (style linking), an equivalent Format 1 entry must not exist. Deletes the Format 1 entry.")
		self.w.upgradeToRanges = vanilla.CheckBox("auto", "Upgrade discrete values to ranges (Format 2)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.upgradeToRanges.setToolTip("Turns discrete axis values (Format 1) into ranges (Format 2) for axes with more than one axis value. Optional: ranges are still hardly supported by software, but may make sense as future-proofing.")

		self.w.checkCheckBoxes = vanilla.TextBox("auto", "Select", sizeStyle="small", selectable=True)
		self.w.checkALL = vanilla.SquareButton("auto", "ALL", sizeStyle="small", callback=self.updateUI)
		self.w.checkALL.setToolTip("Enable all fixes.")
		self.w.checkNONE = vanilla.SquareButton("auto", "NONE", sizeStyle="small", callback=self.updateUI)
		self.w.checkNONE.setToolTip("Disable all fixes.")
		self.w.checkDEFAULT = vanilla.SquareButton("auto", "DEFAULT", sizeStyle="small", callback=self.updateUI)
		self.w.checkDEFAULT.setToolTip("Reset all fixes and the name popup to their defaults: all fixes on except the upgrade to ranges, and the third name option.")

		self.w.status = vanilla.TextBox("auto", "🤖 Ready. 💬 See tooltips for help.", sizeStyle="small", selectable=True)
		self.w.status.setToolTip("Reports what the script is doing, and how it ended.")
		self.w.runButton = vanilla.Button("auto", "Fix", callback=self.fixSTATMain)
		self.w.runButton.setToolTip("Applies the selected fixes to the most recently exported variable font file(s), and saves them.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes hug their titles, buttons never stretch:
		for checkBoxName in self.checkBoxNames:
			nsButton = getattr(self.w, checkBoxName).getNSButton()
			nsButton.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsButton.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		self.w.normalNamesMode.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		nsButton = self.w.runButton.getNSButton()
		nsButton.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsButton.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[normalNames]-gap-[normalNamesMode]-inset-|",
				"H:|-inset-[makeElidable]-(>=inset)-|",
				"H:|-inset-[styleLinking]-(>=inset)-|",
				"H:|-inset-[removeDuplicates]-(>=inset)-|",
				"H:|-inset-[upgradeToRanges]-(>=inset)-|",
				"H:|-inset-[checkCheckBoxes]-gap-[checkALL(>=50)]-gap-[checkNONE(>=50)]-gap-[checkDEFAULT(>=70)]-(>=inset)-|",
				"H:|-inset-[status]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-row-[normalNames]-stackRow-[makeElidable]-stackRow-[styleLinking]-stackRow-[removeDuplicates]-stackRow-[upgradeToRanges]-section-[checkALL]-section-[runButton]-inset-|",
				{"view1": self.w.checkCheckBoxes, "attribute1": "centerY", "view2": self.w.checkALL, "attribute2": "centerY"},
				{"view1": self.w.normalNamesMode, "attribute1": "centerY", "view2": self.w.normalNames, "attribute2": "centerY"},
				{"view1": self.w.checkDEFAULT, "attribute1": "centerY", "view2": self.w.checkALL, "attribute2": "centerY"},
				{"view1": self.w.checkNONE, "attribute1": "centerY", "view2": self.w.checkALL, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8, "stackRow": 8, "section": 12},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		if sender in (self.w.checkALL, self.w.checkNONE, self.w.checkDEFAULT):
			for prefName in self.checkBoxNames:
				value = self.prefDict[prefName] if sender == self.w.checkDEFAULT else int(sender == self.w.checkALL)
				Glyphs.defaults[self.domain(prefName)] = value
			if sender == self.w.checkDEFAULT:
				Glyphs.defaults[self.domain("normalNamesMode")] = self.prefDict["normalNamesMode"]
			self.LoadPreferences()
			return  # LoadPreferences() calls updateUI() again
		self.w.normalNamesMode.enable(self.w.normalNames.get())
		self.w.runButton.enable(any(self.uiElement(prefName).get() for prefName in self.checkBoxNames))

	def SavePreferences(self, sender=None):
		super().SavePreferences(sender)

	def fixSTATMain(self, sender=None):
		thisFont = Glyphs.font  # frontmost font
		if not thisFont:
			self.setStatus("❌ No font open.")
			return
		currentExportPath = currentOTVarExportPath()
		if not currentExportPath:
			self.setStatus("❌ No export path found.")
			Message(title="No Export Path", message="Could not determine the folder of the most recent variable font export.", OKButton=None)
			return

		Glyphs.clearLog()
		print("Report for Fix STAT\n")
		print(f"📄 {thisFont.filepath.lastPathComponent() if thisFont.filepath else f'{thisFont.familyName} (unsaved)'}")
		print(f"- path: {currentExportPath}")

		suffixes = ["ttf"]
		for suffix in ("woff", "woff2"):
			if Glyphs.defaults[f"GXExport{suffix.upper()}"]:
				suffixes.append(suffix)
		print(f"- suffixes: {', '.join(suffixes)}")

		activeFixes = [(title, function) for prefName, title, function in self.fixes if self.prefBool(prefName)]
		normalNamesMode = self.prefInt("normalNamesMode")
		print(f"- fixes: {', '.join(title for title, function in activeFixes)}")

		variableFontSettings = [instance for instance in thisFont.instances if instance.type == INSTANCETYPEVARIABLE]
		if not variableFontSettings:
			variableFontSettings = [None]

		changedCount = 0
		fileCount = 0
		self.setStatus("🛠️")
		try:
			for variableFontExport in variableFontSettings:
				exportFolder = exportFolderOfInstance(thisFont, variableFontExport) if variableFontExport else None
				folderPath = path.join(currentExportPath, exportFolder) if exportFolder else currentExportPath
				for suffix in suffixes:
					fileName = otVarFileName(thisFont, thisInstance=variableFontExport, suffix=suffix)
					fontPath = path.join(folderPath, fileName)
					print(f"\n📄 {fontPath}")
					self.setStatus(f"🛠️ {fileName}")
					if not path.isfile(fontPath):
						print("  ❌ No font file found. Skipping.")
						continue
					if "STAT" not in ttLib.TTFont(fontPath, lazy=True):
						print("  ⚠️ No STAT table. Skipping.")
						continue
					fileCount += 1
					font = ttLib.TTFont(fontPath)
					changesMade = False
					for title, function in activeFixes:
						print(f"  👾 {title}:")
						if function(font, normalNamesMode):
							changesMade = True
					if changesMade:
						font.save(fontPath, reorderTables=False)
						changedCount += 1
						print("  💾 Saved.")
					else:
						print("  🤷🏻‍♀️ No changes made. File left unchanged.")
		except Exception:
			self.setStatus("❌ Error. Details in Macro Window.")
			raise

		if fileCount:
			self.setStatus(f"✅ Changed {changedCount} of {fileCount} files.")
		else:
			self.setStatus("⚠️ No font files found.")
		print(f"\n✅ Done. Changed {changedCount} of {fileCount} files.")
		Glyphs.showNotification("Fix STAT", f"Changed {changedCount} of {fileCount} files. Details in Macro Window.")


if Glyphs.versionNumber < 3.2:
	Message(
		title="Version Error",
		message="This script requires app version 3.2 or later. In Glyphs > Settings > Updates, activate Cutting Edge Versions, and check for updates.",
		OKButton=None,
	)
else:
	FixSTAT()
