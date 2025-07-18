"""
winfix.py

Adds fvar and STAT tables to static fonts for Windows compatibility.
Guesses axis values from font metadata and allows custom overrides.

Usage:
	python winfix.py [FONTS] [options]
	python winfix.py *.ttf -o output/ -a "wdth,wght,slnt" -n CUST="Custom Axis"

Options:
	-a, --axes AXES		Comma-separated axis tags (default: wdth,wght,ital)
	-n, --name NAME		Custom axis name (format: TAG="Name"). TAG must be in --axes.
	-o, --output DIR	Output directory (default: overwrites input)
	-f, --force			Overwrite existing fvar/STAT tables
"""

import argparse
import sys
import os
import glob
from fontTools.ttLib import TTFont
from fontTools.otlLib.builder import buildStatTable
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib.tables import otTables

def expandInputFiles(inputPatterns):
	"""Expand input patterns with wildcards to font file paths."""
	files = []
	for pattern in inputPatterns:
		files.extend(glob.glob(pattern))
	return list(set(files))

def axisNameFromTag(tag, customNames=None):
	"""Get human-readable name for axis tag with custom name support."""
	customNames = customNames or {}
	if tag in customNames:
		return customNames[tag]
	axisNames = {
		'wght': 'Weight',
		'wdth': 'Width',
		'slnt': 'Slant',
		'ital': 'Italic',
		'opsz': 'Optical Size'
	}
	return axisNames.get(tag.lower(), tag)

def getNameById(ttFont, nameId, platform=3, encoding=1, language=0x409):
	"""Get name table entry by ID with Windows/Unicode/US English defaults."""
	for entry in ttFont['name'].names:
		if (entry.nameID == nameId 
			and entry.platformID == platform 
			and entry.platEncID == encoding
			and entry.langID == language):
			return entry.toUnicode()
	return None

def getNameString(ttFont, nameID):
	"""Get Windows platform name string by name ID"""
	string = "(not found)"
	for record in ttFont['name'].names:
		if record.nameID == nameID:
			string = record.toUnicode()
			if (record.platformID == 3 
				and record.platEncID == 1 
				and record.langID == 0x409):
				return string
	return string

def reportFvar(ttFont):
	"""Generate detailed report for fvar table"""
	if 'fvar' not in ttFont:
		return "No fvar table present."
	
	fvar = ttFont['fvar']
	report = []
	report.append(f"fvar table version: {fvar.majorVersion}.{fvar.minorVersion}")
	
	# Report axes
	report.append("\nAxes:")
	for axis in fvar.axes:
		name = getNameString(ttFont, axis.axisNameID)
		report.append(f"  Tag: {axis.axisTag}")
		report.append(f"  Min: {axis.minValue}, Default: {axis.defaultValue}, Max: {axis.maxValue}")
		report.append(f"  Name ID: {axis.axisNameID} ('{name}')")
	
	# Report instances
	report.append("\nInstances:")
	for instance in fvar.instances:
		style_name = getNameString(ttFont, instance.subfamilyNameID)
		ps_name = getNameString(ttFont, instance.postscriptNameID)
		
		report.append(f"  Style Name ID: {instance.subfamilyNameID} ('{style_name}')")
		report.append(f"  PostScript Name ID: {instance.postscriptNameID} ('{ps_name}')")
		report.append(f"  Coordinates:")
		
		# Handle different coordinate formats
		if hasattr(instance, 'coordinates') and isinstance(instance.coordinates, dict):
			for tag, value in instance.coordinates.items():
				report.append(f"	{tag}: {value}")
		else:
			report.append("	(No coordinates available)")
	
	return "\n".join(report)

def reportStat(ttFont):
	"""Generate detailed report for STAT table"""
	if 'STAT' not in ttFont:
		return "No STAT table present."
	
	stat = ttFont['STAT']
	report = []
	report.append(f"STAT table version: {stat.tableVersion >> 16}.{stat.tableVersion & 0xFFFF}")
	
	# Report design axis records
	report.append("\nDesign Axis Records:")
	for axis in stat.DesignAxisRecord:
		name = getNameString(ttFont, axis.AxisNameID)
		report.append(f"  Tag: {axis.AxisTag}")
		report.append(f"	Name ID: {axis.AxisNameID} ('{name}')")
		report.append(f"	Ordering: {axis.AxisOrdering}")
	
	# Report axis value records
	report.append("\nAxis Value Records:")
	for i, value in enumerate(stat.AxisValueArray):
		value_name = getNameString(ttFont, value.ValueNameID)
		flags_desc = "Elidable" if value.Flags & 0x02 else "Not elidable"
		
		report.append(f"  Record {i+1}: Format {value.Format}")
		report.append(f"	Axis Index: {value.AxisIndex}")
		report.append(f"	Value: {value.Value}")
		report.append(f"	Name ID: {value.ValueNameID} ('{value_name}')")
		report.append(f"	Flags: {flags_desc}")
		
		# Format-specific fields
		if value.Format == 3:
			report.append(f"	Linked Value: {value.LinkedValue}")
			report.append(f"	Min Value: {value.MinValue}")
			report.append(f"	Max Value: {value.MaxValue}")
		elif value.Format == 2:
			report.append(f"	Axis Value Count: {value.AxisCount}")
			# Additional handling for format 2 could be added here
	
	return "\n".join(report)

def removeMacNames(ttFont):
	"""Remove all platform=1 (Mac) name table entries."""
	nameTable = ttFont['name']
	# Create new names list without Mac entries
	newNames = [rec for rec in nameTable.names if rec.platformID != 1]
	nameTable.names = newNames

def nameDictAndHighestNameID(nameTable):
	nameDict = {}
	highestID = 255
	for nameTableEntry in nameTable.names:
		nameID = nameTableEntry.nameID
		if nameID > highestID:
			highestID = nameID
		nameValue = nameTableEntry.toUnicode()
		if nameValue not in nameDict.keys():
			nameDict[nameValue] = nameID
	return nameDict, highestID

def getOrAddNameID(ttFont, entryName):
	nameTable = ttFont["name"]
	nameDict, highestID = nameDictAndHighestNameID(nameTable)
	if entryName in list(nameDict.keys()):
		return nameDict[entryName]
	
	# Add new name entry
	highestID += 1
	newNameID = highestID
	nameTable.addName(entryName, platforms=((3, 1, 1033),), minNameID=highestID)
	# nameTable.addName(entryName, 3, 1, 0x409, newNameID)
	return newNameID

def guessAxisValue(ttFont, tag):
	"""Guess axis value from font metadata."""
	if tag == 'wght':
		if 'OS/2' in ttFont:
			return float(ttFont['OS/2'].usWeightClass)
		return 400  # Regular weight default
	
	elif tag == 'wdth':
		if 'OS/2' in ttFont:
			widthMap = {1:50, 2:63, 3:75, 4:88, 5:100, 6:113, 7:125, 8:150, 9:200}
			widthClass = ttFont['OS/2'].usWidthClass
			return float(widthMap.get(widthClass, 100))
		return 100  # Normal width default
	
	elif tag == 'ital':
		if 'OS/2' in ttFont and ttFont['OS/2'].fsSelection & 1:
			return 1.0
		if 'head' in ttFont and ttFont['head'].macStyle & 1 << 1:
			return 1.0
		return 0.0
	
	elif tag == 'slnt':
		if 'post' in ttFont and hasattr(ttFont['post'], 'italicAngle'):
			return float(ttFont['post'].italicAngle)
		return 0.0
	
	elif tag == 'opsz':
		return 12.0
	
	raise ValueError(f"No default value for axis '{tag}'. Specify a value.")

def getFallbackNameForAxis(tag):
	"""Get elidable fallback name for axis."""
	if tag == 'ital':
		return "Roman"
	elif tag == 'wdth':
		return "Normal"
	return "Regular"

def getPredefinedValueName(tag, value):
	"""Get predefined name for axis value if available."""
	if tag == 'wght':
		weights = {
			1: "Hairline",
			100: "Thin",
			200: "Extralight",
			300: "Light",
			400: "Regular",
			450: "Book",
			500: "Medium",
			600: "Semibold",
			700: "Bold",
			800: "Extrabold",
			900: "Black",
			1000: "Extrablack"
		}
		# Find closest weight with tolerance
		closest = min(weights.keys(), key=lambda x: abs(x - value))
		if abs(closest - value) < 5:  # Allow small differences
			return weights[closest]
		return None

	elif tag == 'ital':
		if value == 1:
			return "Italic"
		else:
			return "Roman"
	
	elif tag == 'wdth':
		# Updated width ranges as requested
		if value < 50:
			return "Ultracondensed"
		elif value < 70:
			return "Extracondensed"
		elif value < 80:
			return "Condensed"
		elif value < 100:
			return "Semicondensed"
		elif value == 100:
			return "Normal"
		elif value <= 120:
			return "Semiexpanded"
		elif value <= 135:
			return "Expanded"
		elif value <= 160:
			return "Extraexpensed"
		else:
			return "Ultraexpanded"
	
	return None


def addFvarTable(ttFont, axesList, styleName, postScriptNameID=6):
	"""
	Manually add fvar table to the font.
	
	Args:
		ttFont: TTFont object
		axesList: List of axes tuples (tag, minVal, defaultVal, maxVal, axisNameStr)
		styleName: Style name string
		postScript极ID: Name ID for PostScript name (default=6)
	"""
	from fontTools.ttLib.tables._f_v_a_r import table__f_v_a_r, Axis, NamedInstance
	
	# Create fvar table
	fvar = table__f_v_a_r()
	fvar.majorVersion = 1
	fvar.minorVersion = 0
	fvar.axes = []
	fvar.instances = []
	
	# Add axes
	for tag, minVal, defaultVal, maxVal, axisNameStr in axesList:
		axis = Axis()
		axis.axisTag = tag
		axis.minValue = minVal
		axis.defaultValue = defaultVal
		axis.maxValue = maxVal
		axis.axisNameID = getOrAddNameID(ttFont, axisNameStr)
		axis.flags = 0
		fvar.axes.append(axis)
	
	# Create instance 
	instance = NamedInstance()
	instance.subfamilyNameID = getOrAddNameID(ttFont, styleName)
	instance.postscriptNameID = postScriptNameID
	instance.flags = 0
	instance.coordinates = {tag: defaultVal for tag, _, defaultVal, _, _ in axesList}
	print(instance)
	print("subfamilyNameID", instance.subfamilyNameID)
	print("postscriptNameID", instance.postscriptNameID)
	print("flags", instance.flags)
	print("coordinates", instance.coordinates)
	
	fvar.instances.append(instance)
	
	# Add table to font
	ttFont['fvar'] = fvar
	
	

def addStatTable(ttFont, axesList, axisValuesDict):
	"""
	Manually add STAT table to the font.
	
	Args:
		ttFont: TTFont object
		axesList: List of axes tuples (tag, minVal, defaultVal, maxVal, axisNameStr)
		axisValuesDict: Dictionary of axis tags to current values
	"""
	from fontTools.ttLib.tables import otTables
	
	# Create STAT table
	stat = otTables.STAT()
	stat.tableVersion = 0x00010002  # Version 1.2
	stat.DesignAxisRecord = []
	stat.AxisValueArray = []
	
	# Add axis records
	for idx, (tag, minVal, defaultVal, maxVal, axisNameStr) in enumerate(axesList):
		axisRecord = otTables.AxisRecord()
		axisRecord.AxisTag = tag
		axisRecord.AxisNameID = getOrAddNameID(ttFont, axisNameStr)
		axisRecord.AxisOrdering = idx
		stat.DesignAxisRecord.append(axisRecord)
	
	# Add axis value records
	for idx, (tag, minVal, defaultVal, maxVal, axisNameStr) in enumerate(axesList):
		value = axisValuesDict[tag]
		
		# Create axis value record
		axisValue = otTables.AxisValue()
		
		# Determine format based on special cases
		if (tag == 'wght' and value == 400) or (tag == 'ital' and value == 0):
			axisValue.Format = 3
			axisValue.AxisIndex = idx
			axisValue.Flags = 0x02  # ELIDABLE_AXIS_VALUE_NAME
			axisValue.Value = value
			axisValue.LinkedValue = 700 if tag == 'wght' else 1
			axisValue.MinValue = value
			axisValue.MaxValue = value
		else:
			axisValue.Format = 1
			axisValue.AxisIndex = idx
			axisValue.Flags = 0x02  # ELIDABLE_AXIS_VALUE_NAME
			axisValue.Value = value
		
		# Get value name
		predefinedName = getPredefinedValueName(tag, value)
		if predefinedName:
			axisValue.ValueNameID = getOrAddNameID(ttFont, predefinedName)
		else:
			axisValue.ValueNameID = getOrAddNameID(ttFont, axisNameStr)
		
		stat.AxisValueArray.append(axisValue)
	
	# Set elided fallback name
	stat.ElidedFallbackNameID = 17
	
	# Add table to font
	ttFont['STAT'] = stat


def addFvarAndStat(inputPath, outputPath=None, axes=None, customNames=None, force=False):
	"""
	Add fvar and STAT tables to a static font.
	
	Args:
		inputPath: Path to input font
		outputPath: Output path (None = overwrite input)
		axes: Dictionary of axis tags to values
		customNames: Dictionary of custom axis names
		force: Overwrite existing tables
	"""
	ttFont = TTFont(inputPath)
	nameTable = ttFont['name']
	
	# Remove Mac name table entries before any processing
	removeMacNames(ttFont)
	
	if 'gvar' in ttFont:
		raise ValueError("Font contains gvar table - not for variable fonts")
	if not force:
		if 'fvar' in ttFont:
			raise ValueError("fvar table exists (use --force)")
		if 'STAT' in ttFont:
			raise ValueError("STAT table exists (use --force)")
	
	styleName = getNameById(ttFont, 17) or getNameById(ttFont, 2)
	if not styleName:
		raise ValueError("Missing style name (name ID 17 or 2)")
	
	axes = axes or {'wdth': 100, 'wght': 400, 'ital': 0}
	axisValues = {}
	axesList = []
	
	# Process axes and get names
	for tag, value in axes.items():
		finalValue = float(value) if value is not None else guessAxisValue(ttFont, tag)
		axisValues[tag] = finalValue
		
		# Get axis name (use tag if no custom/default name)
		axisNameStr = axisNameFromTag(tag, customNames) or tag
		axesList.append((tag, finalValue, finalValue, finalValue, axisNameStr))
	
	print()
	print("addFvarTable", ttFont, axesList, styleName, sep="\n")
	print()
	print("addStatTable", ttFont, axesList, axisValues, sep="\n")
	print()
	
	# Build tables:
	addFvarTable(ttFont, axesList, styleName)
	print(reportFvar(ttFont))
	print()
	addStatTable(ttFont, axesList, axisValues)
	print(reportStat(ttFont))
	print()
	
	# Remove Mac names again after all processing
	removeMacNames(ttFont)

	outputPath = outputPath or inputPath
	print(ttFont, outputPath)
	ttFont.save(outputPath)

def main():
	parser = argparse.ArgumentParser(description="Add fvar/STAT tables to static fonts")
	parser.add_argument("inputs", nargs='+', help="Input font files/patterns")
	parser.add_argument("-o", "--output", help="Output directory (optional)")
	parser.add_argument("-a", "--axes", default="wdth,wght,ital", help="Comma-separated axis tags (default: wdth,wght,ital)")
	parser.add_argument("-n", "--name", action="append", help='Custom axis name (e.g., -n SERF="Serif Shape")')
	parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing tables")
	args = parser.parse_args()
	
	# Expand input patterns
	inputFiles = expandInputFiles(args.inputs)
	if not inputFiles:
		sys.exit("Error: No valid font files found")
	
	# Parse axes
	axesDict = {}
	for item in args.axes.split(','):
		if '=' in item:
			tag, value = item.split('=', 1)
			axesDict[tag.strip()] = value
		else:
			axesDict[item.strip()] = None
	
	# Parse custom names
	customNames = {}
	if args.name:
		for item in args.name:
			if '=' in item:
				tag, name = item.split('=', 1)
				tag = tag.strip()
				name = name.strip('"')
				if tag not in axesDict:
					sys.exit(f"Error: Custom name for '{tag}' not in --axes")
				customNames[tag] = name
	
	# Process each file
	for inputPath in inputFiles:
		try:
			outputPath = None
			if args.output:
				if not os.path.isdir(args.output):
					os.makedirs(args.output, exist_ok=True)
				outputPath = os.path.join(args.output, os.path.basename(inputPath))
			
			addFvarAndStat(
				inputPath,
				outputPath,
				axesDict,
				customNames,
				args.force,
			)
			print(f"Processed: {inputPath}")
		except Exception as e:
			import traceback
			print(traceback.format_exc())
			print(f"Error processing {inputPath}: {str(e)}")

if __name__ == "__main__":
	main()
