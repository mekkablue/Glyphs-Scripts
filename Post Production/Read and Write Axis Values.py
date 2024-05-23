# MenuTitle: Read and Write STAT Axis Values (OTVAR)
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
After an OTVAR export, run once, and it will read STAT.AxisValueArray most recently exported from the current Glyphs file, and add ‘Axis Values’ parameters in your Variable Font Settings.

When run with these custom parameters present, it will use them to rewrite STAT.AxisValueArray in the OTVAR most recently exported from the current Glyphs file.

Syntax for the custom parameter:
axisTag; value=name, value=elidableName*, minValue:nominalValue:maxValue=name, value>linkedValue=name

Samples:
wght; 300=Light, 400>700=Regular*, 500=Medium, 600=Semibold, 700=Bold
wdth; 75:75:90=Condensed, 90:100:110=Regular*, 110:150:150=Expanded
ital; 0>1=Regular*
"""

import fontTools
from fontTools import ttLib
from AppKit import NSString
from otvarLib import currentOTVarExportPath, otVarFileName
from GlyphsApp import Glyphs, GSCustomParameter, INSTANCETYPEVARIABLE, Message


# CONSTANTS
parameterName = "Axis Values"


def designAxisRecordDict(statTable):
	axes = []
	for axis in statTable.DesignAxisRecord.Axis:
		axes.append({
			"nameID": axis.AxisNameID,
			"tag": axis.AxisTag,
			"ordering": axis.AxisOrdering,
		})
		print(f"- {axis.AxisTag} axis: AxisNameID {axis.AxisNameID}, AxisOrdering {axis.AxisOrdering}")
	return axes


def nameDictAndHighestNameID(nameTable):
	nameDict = {}
	highestID = 255
	for nameTableEntry in nameTable.names:
		nameID = nameTableEntry.nameID
		if nameID > highestID:
			highestID = nameID
		nameValue = nameTableEntry.toStr()
		if nameValue not in nameDict.keys():
			nameDict[nameValue] = nameID
	return nameDict, highestID


def parameterToSTAT(variableFontExport, font, fontpath, fontFileName):
	nameTable = font["name"]
	nameDict, highestID = nameDictAndHighestNameID(nameTable)
	statTable = font["STAT"].table
	axes = designAxisRecordDict(statTable)

	newAxisValues = []
	for parameter in variableFontExport.customParameters:
		if parameter.name == parameterName and parameter.active:
			statCode = parameter.value
			print(f"\n👨🏼‍🏫 Parsing parameter value: {statCode.strip()}")

			axisTag, axisValueCode = statCode.split(";")
			axisTag = axisTag.strip()
			for i, axisInfo in enumerate(axes):
				if axisTag == axisInfo["tag"]:
					axisIndex = i
					break

			if len(axisTag) > 4:
				print(f"⚠️ axis tag ‘{axisTag}’ is too long, will shorten to first 4 characters.")
				axisTag = axisTag[:4]

			for entryCode in axisValueCode.split(","):
				newAxisValue = fontTools.ttLib.tables.otTables.AxisValue()
				entryValues, entryName = entryCode.split("=")
				entryName = entryName.strip()
				entryFlags = 0
				if entryName.endswith("*"):
					entryFlags = 2
					entryName = entryName[:-1]

				if entryName in nameDict.keys():
					entryValueNameID = nameDict[entryName]
				else:
					# add name entry:
					highestID += 1
					entryValueNameID = highestID
					nameTable.addName(entryName, platforms=((3, 1, 1033), ), minNameID=highestID - 1)
					nameDict[entryName] = entryValueNameID
					print(f"- Adding nameID {entryValueNameID}: ‘{entryName}’")

				if ">" in entryValues:  # Format 3, STYLE LINKING
					entryValue, entryLinkedValue = [float(x.strip()) for x in entryValues.split(">")]
					newAxisValue.Format = 3
					newAxisValue.AxisIndex = axisIndex
					newAxisValue.ValueNameID = entryValueNameID
					newAxisValue.Flags = entryFlags
					newAxisValue.Value = entryValue
					newAxisValue.LinkedValue = entryLinkedValue
					print(f"- AxisValue {axisTag} ‘{entryName}’, Format {newAxisValue.Format}, AxisIndex {newAxisValue.AxisIndex}, ValueNameID {newAxisValue.ValueNameID}, Flags {newAxisValue.Flags}, Value {newAxisValue.Value}, LinkedValue {newAxisValue.LinkedValue}")

				elif ":" in entryValues:  # Format 2, RANGE
					entryRangeMinValue, entryNominalValue, entryRangeMaxValue = [float(x.strip()) for x in entryValues.split(":")]
					newAxisValue.Format = 2
					newAxisValue.AxisIndex = axisIndex
					newAxisValue.ValueNameID = entryValueNameID
					newAxisValue.Flags = entryFlags
					newAxisValue.RangeMinValue = entryRangeMinValue
					newAxisValue.NominalValue = entryNominalValue
					newAxisValue.RangeMaxValue = entryRangeMaxValue
					print(f"- AxisValue {axisTag} ‘{entryName}’, Format {newAxisValue.Format}, AxisIndex {newAxisValue.AxisIndex}, ValueNameID {newAxisValue.ValueNameID}, Flags {newAxisValue.Flags}, RangeMinValue {newAxisValue.RangeMinValue}, NominalValue {newAxisValue.NominalValue}, RangeMaxValue {newAxisValue.RangeMaxValue}")

				else:  # Format 1, DISCRETE SPOT
					entryValue = float(entryValues.strip())
					newAxisValue.Format = 1
					newAxisValue.AxisIndex = axisIndex
					newAxisValue.ValueNameID = entryValueNameID
					newAxisValue.Flags = entryFlags
					newAxisValue.Value = entryValue
					print(f"- AxisValue {axisTag} ‘{entryName}’, Format {newAxisValue.Format}, AxisIndex {newAxisValue.AxisIndex}, ValueNameID {newAxisValue.ValueNameID}, Flags {newAxisValue.Flags}, Value {newAxisValue.Value}")

				newAxisValues.append(newAxisValue)

	print(f"\n✅ Overwriting STAT AxisValues with {len(newAxisValues)} entries...")
	statTable.AxisValueArray.AxisValue = newAxisValues
	font.save(fontpath, reorderTables=False)
	print(f"💾 Saved file: {fontFileName}")


def STATtoParameter(font, variableFontExport):
	nameTable = font["name"]
	nameDict, highestID = nameDictAndHighestNameID(nameTable)
	statTable = font["STAT"].table
	axes = designAxisRecordDict(statTable)

	entries = {}
	axisValues = statTable.AxisValueArray.AxisValue
	for axis in axes:
		axisTag = axis["tag"]
		entries[axisTag] = []

	for i, axisValue in enumerate(axisValues):
		axisTag = axes[axisValue.AxisIndex]["tag"]
		entries[axisTag].append({
			"index": i,
			"Format": axisValue.Format,
			"AxisIndex": axisValue.AxisIndex,
			"Flags": axisValue.Flags,
			"ValueNameID": axisValue.ValueNameID,
			"Value": axisValue.Value if axisValue.Format != 2 else None,
			"LinkedValue": axisValue.LinkedValue if axisValue.Format == 3 else None,
			"NominalValue": axisValue.NominalValue if axisValue.Format == 2 else None,
			"RangeMinValue": axisValue.RangeMinValue if axisValue.Format == 2 else None,
			"RangeMaxValue": axisValue.RangeMaxValue if axisValue.Format == 2 else None,
		})

	for axisTag in entries.keys():
		parameterText = f"{axisTag}; "
		for i, entry in enumerate(entries[axisTag]):
			# values
			if entry["Format"] == 1:
				parameterText += f"{entry['Value']}"
			elif entry["Format"] == 2:
				parameterText += f"{entry['RangeMinValue']}:{entry['NominalValue']}:{entry['RangeMaxValue']}"
			elif entry["Format"] == 3:
				parameterText += f"{entry['Value']}>{entry['LinkedValue']}"

			# name
			parameterText += "=" + str(nameTable.getName(entry["ValueNameID"], 3, 1))

			# elidable
			if entry["Flags"] == 2:
				parameterText += "*"

			# end
			if i + 1 < len(entries[axisTag]):
				parameterText += ", "

		print(f"🆗 Adding parameter ‘{parameterName}’: {parameterText}")
		parameter = GSCustomParameter(parameterName, parameterText)
		variableFontExport.customParameters.append(parameter)


if Glyphs.versionNumber < 3.2:
	Message(
		title="Version Error",
		message="This script requires app version 3.2 or later.",
		OKButton=None,
	)
else:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print("🔢 Axis Values Report:")

	suffixes = ["ttf"]
	for suffix in ("woff", "woff2"):
		if Glyphs.defaults[f"GXExport{suffix.upper()}"]:
			suffixes.append(suffix)
	print(f"- OTVAR suffixes: {', '.join(suffixes)}")

	thisFont = Glyphs.font  # frontmost font
	currentExportPath = currentOTVarExportPath()
	print(f"- OTVAR export path: {currentExportPath}")

	variableFontSettings = []
	for instance in thisFont.instances:
		if instance.type == INSTANCETYPEVARIABLE:
			variableFontSettings.append(instance)

	if not variableFontSettings:
		Message(
			title="No VF Setting",
			message="This script requires a Variable Font Setting in Font Info > Exports.",
			OKButton=None,
		)

	for variableFontExport in variableFontSettings:
		for suffix in suffixes:
			fontFileName = otVarFileName(thisFont, thisInstance=variableFontExport, suffix=suffix)
			fontpath = NSString.alloc().initWithString_(currentExportPath).stringByAppendingPathComponent_(fontFileName)
			font = ttLib.TTFont(fontpath)

			msg = f"📄Processing: {fontpath}..."
			print(f"\n{'-' * len(msg)}\n{msg}\n{'-' * len(msg)}")
			if variableFontExport.customParameters[parameterName]:
				# Axis Values present, so:
				# construct entries and overwrite STAT table in exported font
				print(f"\n🗜️ Found ‘{parameterName}’ parameters: overwriting STAT table")
				parameterToSTAT(variableFontExport, font, fontpath, fontFileName)
			else:
				# no Axis Values present, so:
				# read entries in exported font and add custom parameters in Glyphs file
				print(f"\n🛠️ No ‘{parameterName}’ parameter in VF setting: reading STAT table and adding ‘Axis Values’ parameters")
				STATtoParameter(font, variableFontExport)

print("\n✅ Done.")
