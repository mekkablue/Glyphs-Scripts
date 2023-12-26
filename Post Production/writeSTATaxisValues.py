# -*- coding: utf-8 -*-
"""
python3 writeSTATaxisValues.py -h     ... help
python3 writeSTATaxisValues.py -a "wdth;100.0=Regular*|ital;0.0>1.0=Regular*" *.ttf  ... apply to all TTFs in current dir
"""
import fontTools
from fontTools import ttLib
from argparse import ArgumentParser

parser = ArgumentParser(
    description = "For every axis, renames normal STAT entries to ‘Regular’ (also makes changes in name table if necessary), and makes them elidable (Flags=2). Typically only necessary in italic OTVAR exports with 2 or more axes. Also, fixes Format1/3 duplicates (if a Format 3 exists, there must be no equivalent Format 1 entry)."
)

parser.add_argument(
    "fonts",
    nargs="+", # one or more font names, e.g. *.otf
    metavar="font",
    help="Any number of OTF or TTF files.",
)

parser.add_argument(
    "-a",
    "--axisvalue",
    dest="axisValueString",
    help="Separate multiple axes with |. Start each axis with tag followed by semicolon. Add comma-separated axis values. Format1: value=name. Format2: minValue:nominalValue:maxValue=name. Format3: value>linkedValue=name. Add * after elidableName. E.g. wdth;75.0=Condensed,100.0=Regular*|ital;0.0>1.0=Regular*",
)

import fontTools
from fontTools import ttLib

def designAxisRecordDict(statTable):
	axes = []
	for axis in statTable.DesignAxisRecord.Axis:
		axes.append(
			{
				"nameID": axis.AxisNameID,
				"tag": axis.AxisTag,
				"ordering": axis.AxisOrdering,
			}
		)
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
		if not nameValue in nameDict.keys():
			nameDict[nameValue] = nameID
	return nameDict, highestID

def getOrAddName(nameTable, entryName):
	nameDict, highestID = nameDictAndHighestNameID(nameTable)
	if entryName in nameDict.keys():
		entryValueNameID = nameDict[entryName]
	else:
		# add name entry:
		highestID += 1
		entryValueNameID = highestID
		nameTable.addName(entryName, platforms=((3, 1, 1033),), minNameID=highestID-1)
		nameDict[entryName] = entryValueNameID
		print(f"- Adding nameID {entryValueNameID}: ‘{entryName}’")
	return entryValueNameID
	
def parameterToSTAT(axisValueArgument, font):
	axisNameDict = {
		"wght": "Weight",
		"wdth": "Width",
		"slnt": "Slant",
		"ital": "Italic",
		"opsz": "Optical Size",
	}
	
	nameTable = font["name"]
	# nameDict, highestID = nameDictAndHighestNameID(nameTable)
	statTable = font["STAT"].table
	
	designAxisRecord = [] # collect axisTags
	newAxisValues = [] # collect axisValues
	
	axisValueStrings = axisValueArgument.split("|")
	for axisIndex, statCode in enumerate(axisValueStrings):
		statCode = statCode.strip()
		print(f"👨🏼‍🏫 Parsing parameter value: {statCode}")
		
		axisTag, axisValueCode = statCode.split(";")
		axisTag = axisTag.strip()
		
		axisName = ""
		if "=" in axisTag:
			axisTag, axisName = [x.strip() for x in axisTag.split("=")]
		if len(axisTag) > 4:
			print(f"⚠️ axis tag ‘{axisTag}’ is too long, will shorten to first 4 characters.")
			axisTag = axisTag[:4]
		if axisName=="" and axisTag in axisNameDict.keys():
			axisName = axisNameDict[axisTag]
		else:
			axisName = axisTag
		designAxisRecord.append((axisTag,axisName))
		
		for entryCode in  axisValueCode.split(","):
			newAxisValue = ttLib.tables.otTables.AxisValue()
			entryValues, entryName = entryCode.split("=")
			entryName = entryName.strip()
			entryFlags = 0
			if entryName.endswith("*"):
				entryFlags = 2
				entryName = entryName[:-1]
			
			entryValueNameID = getOrAddName(nameTable, entryName)
			
			if ">" in entryValues: # Format 3, STYLE LINKING
				entryValue, entryLinkedValue = [float(x.strip()) for x in entryValues.split(">")]
				newAxisValue.Format = 3
				newAxisValue.AxisIndex = axisIndex
				newAxisValue.ValueNameID = entryValueNameID
				newAxisValue.Flags = entryFlags
				newAxisValue.Value = entryValue
				newAxisValue.LinkedValue = entryLinkedValue
				print(f"- AxisValue {axisTag} ‘{entryName}’, Format {newAxisValue.Format}, AxisIndex {newAxisValue.AxisIndex}, ValueNameID {newAxisValue.ValueNameID}, Flags {newAxisValue.Flags}, Value {newAxisValue.Value}, LinkedValue {newAxisValue.LinkedValue}")
				
			elif ":" in entryValues: # Format 2, RANGE
				entryRangeMinValue, entryNominalValue, entryRangeMaxValue = [float(x.strip()) for x in entryValues.split(":")]
				newAxisValue.Format = 2
				newAxisValue.AxisIndex = axisIndex
				newAxisValue.ValueNameID = entryValueNameID
				newAxisValue.Flags = entryFlags
				newAxisValue.RangeMinValue = entryRangeMinValue
				newAxisValue.NominalValue = entryNominalValue
				newAxisValue.RangeMaxValue = entryRangeMaxValue
				print(f"- AxisValue {axisTag} ‘{entryName}’, Format {newAxisValue.Format}, AxisIndex {newAxisValue.AxisIndex}, ValueNameID {newAxisValue.ValueNameID}, Flags {newAxisValue.Flags}, RangeMinValue {newAxisValue.RangeMinValue}, NominalValue {newAxisValue.NominalValue}, RangeMaxValue {newAxisValue.RangeMaxValue}")
				
			else: # Format 1, DISCRETE SPOT
				entryValue = float(entryValues.strip())
				newAxisValue.Format = 1
				newAxisValue.AxisIndex = axisIndex
				newAxisValue.ValueNameID = entryValueNameID
				newAxisValue.Flags = entryFlags
				newAxisValue.Value = entryValue
				print(f"- AxisValue {axisTag} ‘{entryName}’, Format {newAxisValue.Format}, AxisIndex {newAxisValue.AxisIndex}, ValueNameID {newAxisValue.ValueNameID}, Flags {newAxisValue.Flags}, Value {newAxisValue.Value}")
			
			newAxisValues.append(newAxisValue)
	
	print(f"✅ Overwriting STAT AxisValues with {len(newAxisValues)} entries...")
	statTable.AxisValueArray.AxisValue = newAxisValues
	
	statTable.DesignAxisRecord = fontTools.ttLib.tables.otTables.AxisRecordArray()
	axes = []
	for i, designAxis in enumerate(designAxisRecord):
		axis = fontTools.ttLib.tables.otTables.AxisRecord()
		axisTag, axisName = designAxis
		axis.AxisOrdering = i
		axis.AxisTag = axisTag
		nameID = getOrAddName(nameTable, axisName)
		axis.AxisNameID = nameID
		axes.append(axis)
		print(f"- DesignAxisRecord {i} {axisTag}={axisName} (nameID {axis.AxisNameID})")
	print(f"✅ Overwriting STAT DesignAxisRecord with {len(designAxisRecord)} entries...")
	statTable.DesignAxisRecord.Axis = axes
	return len(newAxisValues) + len(designAxisRecord)
	
# def STATtoParameter(font, variableFontExport):
# 	nameTable = font["name"]
# 	nameDict, highestID = nameDictAndHighestNameID(nameTable)
# 	statTable = font["STAT"].table
# 	axes = designAxisRecordDict(statTable)
#
# 	entries = {}
# 	axisValues = statTable.AxisValueArray.AxisValue
# 	for axis in axes:
# 		axisTag = axis["tag"]
# 		entries[axisTag] = []
#
# 	for i, axisValue in enumerate(axisValues):
# 		axisTag = axes[axisValue.AxisIndex]["tag"]
# 		entries[axisTag].append({
# 			"index": i,
# 			"Format": axisValue.Format,
# 			"AxisIndex": axisValue.AxisIndex,
# 			"Flags": axisValue.Flags,
# 			"ValueNameID": axisValue.ValueNameID,
# 			"Value": axisValue.Value if axisValue.Format!=2 else None,
# 			"LinkedValue": axisValue.LinkedValue if axisValue.Format==3 else None,
# 			"NominalValue": axisValue.NominalValue if axisValue.Format==2 else None,
# 			"RangeMinValue": axisValue.RangeMinValue if axisValue.Format==2 else None,
# 			"RangeMaxValue": axisValue.RangeMaxValue if axisValue.Format==2 else None,
# 		})
#
# 	for axisTag in entries.keys():
# 		parameterText = f"{axisTag}; "
# 		for i, entry in enumerate(entries[axisTag]):
# 			# values
# 			if entry["Format"] == 1:
# 				parameterText += f"{entry['Value']}"
# 			elif entry["Format"] == 2:
# 				parameterText += f"{entry['RangeMinValue']}:{entry['Value']}:{entry['RangeMaxValue']}"
# 			elif entry["Format"] == 3:
# 				parameterText += f"{entry['Value']}>{entry['LinkedValue']}"
#
# 			# name
# 			parameterText += "=" + str(nameTable.getName(entry["ValueNameID"], 3, 1))
#
# 			# elidable
# 			if entry["Flags"]==2:
# 				parameterText += "*"
#
# 			# end
# 			if i+1 < len(entries[axisTag]):
# 				parameterText += ", "
#
# 		print(f"🆗 Adding parameter ‘{parameterName}’: {parameterText}")
# 		parameter = GSCustomParameter(parameterName, parameterText)
# 		variableFontExport.customParameters.append(parameter)



print("🔢 Rewriting STAT.DesignAxisRecord and STAT.AxisValues:")

arguments = parser.parse_args()
fonts = arguments.fonts
axisValues = arguments.axisValueString

changed = 0
for i, fontpath in enumerate(fonts):
	print(f"\n📄 {i+1}. {fontpath}")
	font = ttLib.TTFont(fontpath)
	changesMade = parameterToSTAT(axisValues, font)
	if changesMade:
		changed += 1
		font.save(fontpath, reorderTables=False)
		print(f"💾 Saved {fontpath}")
	else:
		print(f"🤷🏻‍♀️ No changes made. File left unchanged.")
	
print(f"✅ Done. Changed {changed} of {i+1} fonts.\n")