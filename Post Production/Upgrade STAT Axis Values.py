# MenuTitle: Upgrade STAT Axis Values from Discrete to Ranges (OTVAR)
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Turns STAT entries of format 1 (discrete) into format 2 (range) for axes with more than one axis value. Run this right after a variable font export.
"""

import fontTools
from fontTools import ttLib
from AppKit import NSString
from otvarLib import currentOTVarExportPath, otVarFileName
from GlyphsApp import Glyphs, INSTANCETYPEVARIABLE, Message

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
	print("Report: Fix STAT Names in OTVAR Exports")

	suffixes = ["ttf"]
	for suffix in ("woff", "woff2"):
		if Glyphs.defaults[f"GXExport{suffix.upper()}"]:
			suffixes.append(suffix)
	print(f"- suffixes: {', '.join(suffixes)}")

	thisFont = Glyphs.font  # frontmost font
	currentExportPath = currentOTVarExportPath()
	print(f"- path: {currentExportPath}")

	variableFontSettings = []
	for instance in thisFont.instances:
		if instance.type == INSTANCETYPEVARIABLE:
			variableFontSettings.append(instance)

	if not variableFontSettings:
		variableFontSettings = [None]

	for variableFontExport in variableFontSettings:
		for suffix in suffixes:
			fontpath = NSString.alloc().initWithString_(currentExportPath).stringByAppendingPathComponent_(otVarFileName(thisFont, thisInstance=variableFontExport, suffix=suffix))
			font = ttLib.TTFont(fontpath)
			print(f"\nProcessing: {fontpath}...")
			statTable = font["STAT"].table

			print("\nDetermining axes max and min (fvar):")
			axisDict = {}
			for a in font["fvar"].axes:
				axisDict[a.axisTag] = {
					"axisNameID": a.axisNameID,
					"defaultValue": a.defaultValue,
					"flags": a.flags,
					"maxValue": a.maxValue,
					"minValue": a.minValue,
				}
				print(f"- {a.axisTag}: min {a.minValue}, max {a.maxValue}")

			print("\nDetermining axes in STAT table:")
			axes = []
			for axis in statTable.DesignAxisRecord.Axis:
				axes.append({
					"nameID": axis.AxisNameID,
					"tag": axis.AxisTag,
					"ordering": axis.AxisOrdering,
				})
				print("AxisNameID:", axis.AxisNameID)
				print("AxisOrdering:", axis.AxisOrdering)
				print("AxisTag:", axis.AxisTag)
				print()

			print("--\n")

			# prepare entries:
			entries = {}
			axisValues = statTable.AxisValueArray.AxisValue
			for axis in axes:
				axisTag = axis["tag"]
				entries[axisTag] = []

			for i, axisValue in enumerate(axisValues):
				if axisValue.Format == 1:
					axisTag = axes[axisValue.AxisIndex]["tag"]
					entries[axisTag].append(
						{
							"index": i,
							"AxisIndex": axisValue.AxisIndex,
							"Flags": axisValue.Flags,
							"ValueNameID": axisValue.ValueNameID,
							"RangeMinValue": -1,
							"NominalValue": axisValue.Value,
							"RangeMaxValue": -1,
						}
					)

			overwriteCount = 0
			for axisTag in entries.keys():
				thereIsAnFvarEntry = axisTag in axisDict.keys()
				axisEntries = entries[axisTag]
				if len(axisEntries) > 1:
					for i, entry in enumerate(axisEntries):
						# calculate min and max values:
						prevIndex = max(0, i - 1)
						nextIndex = min(len(axisEntries) - 1, i + 1)
						prevValue = axisEntries[prevIndex]["NominalValue"]
						nextValue = axisEntries[nextIndex]["NominalValue"]
						currValue = entry["NominalValue"]
						entry["RangeMinValue"] = (prevValue + currValue) / 2
						entry["RangeMaxValue"] = (nextValue + currValue) / 2

						# in case the extreme axis values do not coincide with the outer ends of the axis:
						if thereIsAnFvarEntry and prevIndex == i:
							entry["RangeMinValue"] = min(axisDict[axisTag]["minValue"], currValue)
						elif thereIsAnFvarEntry and nextIndex == i:
							entry["RangeMaxValue"] = max(axisDict[axisTag]["maxValue"], currValue)

						# build value record
						newAxisValue = fontTools.ttLib.tables.otTables.AxisValue()
						newAxisValue.Format = 2
						newAxisValue.ValueNameID = entry["ValueNameID"]
						newAxisValue.Flags = entry["Flags"]
						newAxisValue.AxisIndex = entry["AxisIndex"]
						newAxisValue.RangeMinValue = entry["RangeMinValue"]
						newAxisValue.NominalValue = entry["NominalValue"]
						newAxisValue.RangeMaxValue = entry["RangeMaxValue"]

						# overwrite
						axisValues[entry["index"]] = newAxisValue
						overwriteCount += 1

						# report
						print("✅ New axis value record, format 2 (range):")
						print("AxisIndex", newAxisValue.AxisIndex, f" ({axisTag})")
						print("Flags", newAxisValue.Flags, " (ELIDABLE)" if newAxisValue.Flags == 2 else "")
						print("ValueNameID", newAxisValue.ValueNameID, " (" + font["name"].getName(newAxisValue.ValueNameID, 3, 1, langID=1033).toStr() + ")")
						print("RangeMinValue", newAxisValue.RangeMinValue)
						print("NominalValue", newAxisValue.NominalValue)
						print("RangeMaxValue", newAxisValue.RangeMaxValue)
						print()

			if overwriteCount > 0:
				statTable.AxisValueCount = len(statTable.AxisValueArray.AxisValue)
				print(f"🔢 {overwriteCount} new entries.\n🔢 AxisValueCount {statTable.AxisValueCount} for {len(statTable.AxisValueArray.AxisValue)} AxisValueRecords.")
				font.save(fontpath, reorderTables=False)
				print("💾 saved file.")
			else:
				print("🤷🏻‍♀️ no changes, file left unchanged")
