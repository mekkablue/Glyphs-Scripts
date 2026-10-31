# MenuTitle: Fix STAT Entries (OTVAR)
__doc__ = """
For every axis, renames normal STAT entries to ‘Regular’ (also makes changes in name table if necessary), and makes them elidable (Flags=2). Typically only necessary in italic OTVAR exports with 2 or more axes. Also, fixes Format1/3 duplicates (if a Format 3 exists, there must be no equivalent Format 1 entry).
"""

from fontTools import ttLib
from AppKit import NSString
from otvarLib import currentOTVarExportPath, otVarFileName
from typing import Any
from GlyphsApp import Glyphs, INSTANCETYPEVARIABLE, Message


def fixDuplicatesFormat1and3(axes, axisValueArray, changesMade=False):
	# remove format 1 if format 3 exists:
	# collect format 3:
	format3entries = []
	for statEntry in axisValueArray.AxisValue:
		if statEntry.Format == 3:
			axisTag = axes[statEntry.AxisIndex]
			axisValue = statEntry.Value
			format3entries.append((axisTag, axisValue))

	# go again and delete format 1 entries with same values:
	if format3entries:
		newAxisValues = []  # ttLib.tables.otTables.AxisValueArray()
		for statEntry in statTable.AxisValueArray.AxisValue:
			axisTag = axes[statEntry.AxisIndex]
			if statEntry.Format == 1:
				axisTag = axes[statEntry.AxisIndex]
				axisValue = statEntry.Value
				# actually we rebuild the table without the Format 1 entries
				# because we cannot directly delete out of a table (or did I miss something?)
				if (axisTag, axisValue) in format3entries:
					print(f"⛔️ Deleting Format 1 entry {axisTag}={axisValue} because equivalent Format 3 exists.")
					changesMade = True
				else:
					# add Format 1 only if it is not represented as Format 3 already
					newAxisValues.append(statEntry)
			else:
				# add all other Formats
				newAxisValues.append(statEntry)
		axisValueArray.AxisValue = newAxisValues

	return changesMade


if Glyphs.versionNumber < 3.2:
	Message(
		title="Version Error",
		message="This script requires app version 3.2 or later. In Glyphs > Settings > Updates, activate Cutting Edge Versions, and check for updates.",
		OKButton=None,
	)
else:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print("Report: Fix Italic STAT Entries")

	suffixes = ["ttf"]
	for suffix in ("woff", "woff2"):
		if Glyphs.defaults[f"GXExport{suffix.upper()}"]:
			suffixes.append(suffix)
	print(f"- suffixes: {', '.join(suffixes)}")

	thisFont = Glyphs.font  # frontmost font
	currentExportPath = currentOTVarExportPath()
	print(f"- path: {currentExportPath}")

	variableFontSettings: list[Any] = []
	for instance in thisFont.instances:
		if instance.type == INSTANCETYPEVARIABLE:
			variableFontSettings.append(instance)

	if not variableFontSettings:
		variableFontSettings = [None]

	for variableFontExport in variableFontSettings:
		for suffix in suffixes:
			fontpath = NSString.alloc().initWithString_(currentExportPath).stringByAppendingPathComponent_(otVarFileName(thisFont, thisInstance=variableFontExport, suffix=suffix))
			print(f"\nProcessing: {fontpath}...")
			font = ttLib.TTFont(fontpath)
			changesMade = False

			print("👾 Scanning name table:")
			nameTable = font["name"]
			regularID = None
			normalID = None
			highestID = 0
			for entry in nameTable.names:
				currentID = entry.nameID
				if regularID is None and str(entry) == "Regular":
					regularID = currentID
				elif normalID is None and str(entry) == "Normal":
					normalID = currentID
				if currentID > highestID:
					highestID = currentID
			if regularID is None:
				if normalID is None:
					nameTable.addName("Regular", platforms=((3, 1, 1033), ), minNameID=highestID)
					regularID = highestID + 1
					print(f"📛 Adding name ID {regularID} ‘Regular’.")
				else:
					nameTable.setName("Regular", normalID, 3, 1, 1033)
					regularID = normalID
					print(f"📛 Overwriting existing name ID {regularID} ‘Normal’ → ‘Regular’.")
				changesMade = True
			else:
				print(f"📛 Found existing nameID {regularID} ‘Regular’. No changes necessary in name table.")
			# regularEntry = nameTable.getName(regularID, 3, 1, langID=1033)

			print("👾 Scanning STAT table:")
			statTable = font["STAT"].table

			# collect axes:
			axes = []
			for axisIndex, axis in enumerate(statTable.DesignAxisRecord.Axis):
				axes.append(axis.AxisTag)

			# go through axis values, fix "Regular" naming and elidable flags:
			for statIndex, statEntry in enumerate(statTable.AxisValueArray.AxisValue):
				axisTag = axes[statEntry.AxisIndex]
				if statEntry.Format == 2:
					axisValue = statEntry.NominalValue
				else:
					axisValue = statEntry.Value
				isNormalWdth = axisTag == "wdth" and axisValue == 100
				isNormalWght = axisTag == "wght" and axisValue == 400
				isNormalOtherAxis = axisValue == 0 and axisTag not in ("wght", "wdth")
				if isNormalWdth or isNormalWght or isNormalOtherAxis:
					oldNameID = statEntry.ValueNameID
					oldName = nameTable.getName(oldNameID, 3, 1)
					oldFlags = statEntry.Flags
					print(f"🏛️ STAT axis value {statIndex}, {axisTag}={axisValue}: name ID {oldNameID} ‘{oldName}’ → {regularID} ‘Regular’; flags {oldFlags} → 2 (elidable)")
					if oldNameID != regularID:
						changesMade = True
						statEntry.ValueNameID = regularID
					if oldFlags != 2:
						changesMade = True
						statEntry.Flags = 2

			changesMade = fixDuplicatesFormat1and3(axes, statTable.AxisValueArray, changesMade)

			if changesMade:
				font.save(fontpath, reorderTables=False)
				print(f"💾 Saved {fontpath}\n")
			else:
				print("🤷🏻‍♀️ No changes made. File left unchanged.")
