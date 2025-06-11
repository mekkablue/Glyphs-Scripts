"""
addstaticfvar.py

A tool for adding an fvar table to a static font using fontTools.
Exports addFvarToFont() for programmatic use and maintains CLI functionality.
"""

import argparse
from fontTools.ttLib import TTFont
from fontTools.fontBuilder import FontBuilder

def axisNameFromTag(tag):
	"""
	Return human-readable axis name for standard tags, or the tag itself.
	"""
	axisNames = {
		'wght': 'Weight',
		'wdth': 'Width',
		'slnt': 'Slant',
		'ital': 'Italic',
		'opsz': 'Optical Size'
	}
	return axisNames.get(tag.lower(), tag)

def getNameByID(ttFont, nameID, platform=3, encoding=1, language=0x409):
	"""
	Get name table entry by ID with Windows/Unicode/US English defaults.
	"""
	for entry in ttFont['name'].names:
		if (entry.nameID == nameID 
			and entry.platformID == platform 
			and entry.platEncID == encoding
			and entry.langID == language):
			return entry.toUnicode()
	return None

def addFvarToFont(inputPath, outputPath=None, axes={'wdth':100, 'wght':400, 'ital':0}):
	"""
	Main functionality exposed as importable method.
	Args:
		inputPath: Path to input font file
		outputPath: Optional output path (defaults to overwriting input)
		axes: Dictionary of axis tags to values (e.g. {'wght':700})
	"""
	ttFont = TTFont(inputPath)
	if 'gvar' in ttFont:
		raise ValueError("Font contains gvar table, hence is not a static font")

	# Process axes
	axisList = []
	axisValues = {}
	for tag, value in axes.items():
		axisValues[tag] = float(value)
		axisList.append((
			tag,
			float(value),
			float(value),
			float(value),
			axisNameFromTag(tag)
		))

	# Get naming data
	styleName = getNameByID(ttFont, 17) or getNameByID(ttFont, 2)
	if not styleName:
		raise ValueError("Missing required name entries (ID 17 or 2)")

	postScriptName = getNameByID(ttFont, 6)
	if not postScriptName:
		raise ValueError("Missing required name entry (ID 6)")

	# Build instance
	instance = {
		'location': axisValues,
		'stylename': styleName
	}
	if postScriptName:
		instance['postscriptfontname'] = postScriptName

	# Build and save
	FontBuilder(font=ttFont).setupFvar(axisList, instances=[instance])
	ttFont.save(outputPath if outputPath else inputPath)

def main():
	"""Command-line interface implementation"""
	parser = argparse.ArgumentParser(description="Add fvar table to static font")
	parser.add_argument("input", help="Input font file")
	parser.add_argument("-o", "--output", help="Output font file (optional)")
	parser.add_argument("axes", nargs="+", help="Axis definitions (e.g. wght=700)")
	args = parser.parse_args()

	# Convert CLI axes to dictionary
	axesDict = {}
	for arg in args.axes:
		try:
			tag, value = arg.split('=')
			axesDict[tag.strip()] = float(value)
		except ValueError:
			raise SystemExit(f"Invalid axis format: {arg}")

	try:
		addFvarToFont(args.input, args.output, axesDict)
	except Exception as e:
		raise SystemExit(f"Error: {str(e)}")

if __name__ == "__main__":
	main()
