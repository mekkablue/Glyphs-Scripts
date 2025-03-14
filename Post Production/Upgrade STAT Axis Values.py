# MenuTitle: Upgrade STAT Axis Values from Discrete to Ranges (OTVAR)
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Turns STAT entries of format 1 (discrete) into format 2 (range) for axes with more than one axis value. Run this right after a variable font export.
"""

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
	print("Report: Upgrade STAT to Format 2")

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
			fileName = otVarFileName(thisFont, thisInstance=variableFontExport, suffix=suffix)
			fontpath = NSString.alloc().initWithString_(currentExportPath).stringByAppendingPathComponent_(fileName)
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
			axisValues = statTable.AxisValueArray.AxisValue
			entries = {}
			styleLinkEntries = {}
			for axis in axes:
				axisTag = axis["tag"]
				entries[axisTag] = []
				styleLinkEntries[axisTag] = []

			usedEntries = []
			for i, axisValue in enumerate(axisValues):
				if axisValue.Format in (1, 3):
					# check if it is in STAT twice:
					entry = (axisValue.AxisIndex, axisValue.Value)
					if entry in usedEntries:
						continue
					usedEntries.append(entry)

					# record entry for conversion to format 2:
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

					# record format 3:
					if axisValue.Format != 3:
						continue
					styleLinkEntries[axisTag].append(axisValue)

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
						newAxisValue = ttLib.tables.otTables.AxisValue()
						newAxisValue.Format = 2
						newAxisValue.ValueNameID = entry["ValueNameID"]
						newAxisValue.Flags = entry["Flags"]
						newAxisValue.AxisIndex = entry["AxisIndex"]
						newAxisValue.RangeMinValue = entry["RangeMinValue"]
						newAxisValue.NominalValue = entry["NominalValue"]
						newAxisValue.RangeMaxValue = entry["RangeMaxValue"]

						# overwrite value
						axisValues[entry["index"]] = newAxisValue
						overwriteCount += 1

						# report
						print("✅ New axis value record, format 2 (range):")
						print(f"\tAxisIndex {newAxisValue.AxisIndex}: {axisTag}, Flags {newAxisValue.Flags}", "(ELIDABLE)" if newAxisValue.Flags == 2 else "")
						print(f"\tValueNameID {newAxisValue.ValueNameID}: {font['name'].getName(newAxisValue.ValueNameID, 3, 1, langID=1033).toStr()}")
						print(f"\tRangeMinValue {newAxisValue.RangeMinValue} → NominalValue {newAxisValue.NominalValue} → RangeMaxValue {newAxisValue.RangeMaxValue}")
						print()

				# reinstate Format 3 entries (style linking):
				if styleLinkEntries[axisTag]:
					styleLinkEntry = styleLinkEntries[axisTag][0]
					axisValues.append(styleLinkEntry)
					overwriteCount += 1
					print("✅ Reordered axis value record, format 3 (style linking):")
					print(f"\tAxisIndex {styleLinkEntry.AxisIndex}: {axisTag}, Flags {styleLinkEntry.Flags}", "(ELIDABLE)" if styleLinkEntry.Flags == 2 else "")
					print(f"\tValueNameID {styleLinkEntry.ValueNameID}: {font['name'].getName(styleLinkEntry.ValueNameID, 3, 1, langID=1033).toStr()}")
					print(f"\tValue {styleLinkEntry.Value} → LinkedValue {styleLinkEntry.LinkedValue}")
					print()

			if overwriteCount > 0:
				statTable.AxisValueCount = len(statTable.AxisValueArray.AxisValue)
				print(f"🔢 {overwriteCount} new/reordered entries.\n🔢 AxisValueCount {statTable.AxisValueCount} for {len(statTable.AxisValueArray.AxisValue)} AxisValueRecords.")
				font.save(fontpath, reorderTables=False)
				print("💾 saved file.")
			else:
				print("🤷🏻‍♀️ no changes, file left unchanged")
