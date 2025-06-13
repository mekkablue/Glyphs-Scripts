#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, sys, os, glob
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import table__f_v_a_r, Axis, NamedInstance
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e

# Predefined axis names according to OpenType spec
PREDEFINED_AXIS_NAMES = {
	'wght': 'Weight',
	'wdth': 'Width',
	'ital': 'Italic',
	'slnt': 'Slant',
	'opsz': 'Optical Size'
}

WIDTH_VALUES = {
	1: 50.0,
	2: 62.5,
	3: 75.0,
	4: 87.5,
	5: 100.0,
	6: 112.5,
	7: 125.0,
	8: 150.0,
	9: 200.0
}

def getNameByID(font, nameID, platform=3, encoding=1, language=0x409):
	nameTable = font.get("name")
	if not nameTable:
		return None
	nameRec = nameTable.getName(nameID, platform, encoding, language)
	return nameRec.toUnicode() if nameRec else None


class FvarBuilder:
	def __init__(self, fontPath, outputPath, styleName, axisValues):
		self.fontPath = fontPath
		self.outputPath = outputPath
		self.styleName = styleName
		self.axisValues = axisValues
		self.nameIds = {}
		
	def getStyleName(self, font):
		nameTable = font.get("name", None)
		if not nameTable:
			raise ValueError("🥴 Font contains no name table")
		styleName = nameTable.getName(17, 3, 1, 0x409) or nameTable.getName(2, 3, 1, 0x409)
		if not styleName:
			raise ValueError("🥴 No style name found in name IDs 17 or 2")
		return styleName.toUnicode()

	def getPostScriptName(self, font):
		"""Verify and return PostScript name (nameID 6)"""
		psName = getNameByID(font, 6)
		if not psName:
			raise ValueError("🥴 Missing required PostScript name (nameID 6)")
		return psName

	def resolveAxisValue(self, tag, font):
		if tag not in ['wght', 'wdth', 'ital', 'slnt', 'opsz']:
			raise ValueError(f"🥴 Auto-detection not supported for {tag} axis")
		if 'OS/2' not in font and tag in ['wght', 'wdth', 'ital']:
			raise ValueError(f"🥴 Font missing required OS/2 table, cannot autodetect {tag} coordinates.")
			
		if tag == 'wght':
			return float(font['OS/2'].usWeightClass)
		elif tag == 'wdth':
			return WIDTH_VALUES.get(font['OS/2'].usWidthClass, 100.0)
		elif tag == 'ital':
			return 1.0 if font['OS/2'].fsSelection & 1 else 0.0
		elif tag == 'slnt':
			return float(font['post'].italicAngle) if 'post' in font else 0.0
		elif tag == 'opsz':
			if 'size' in font:
				return float(font['size'].subfamilyIdentifier)
			raise ValueError("🥴 Optical Size axis requires 'size' table for auto-detection")

	def createFvarTable(self, nameTable, font):
		fvarTable = table__f_v_a_r()
		fvarTable.axes = []
		fvarTable.instances = []
	
		for tag, value in self.axisValues.items():
			axis = Axis()
			axis.axisTag = tag
			axisValue = value if isinstance(value, float) else self.resolveAxisValue(tag, font)
			# Set all values equal for static font
			axis.minValue = axisValue
			axis.defaultValue = axisValue
			axis.maxValue = axisValue
			axis.axisNameID = self.nameIds[tag]
			fvarTable.axes.append(axis)
		
		instance = NamedInstance()
		instance.subfamilyNameID = self.nameIds['styleName']
		instance.coordinates = {axis.axisTag: axis.defaultValue for axis in fvarTable.axes}
		
		# Set PostScript name ID from existing name table
		self.getPostScriptName(font)  # Validate existence first
		instance.postscriptNameID = 6  # Direct reference to OT spec nameID
		
		fvarTable.instances.append(instance)
		return fvarTable

	def updateNameTable(self, nameTable):
		# Find existing name IDs and initialize next available ID
		existingIds = {rec.nameID: rec.toUnicode() for rec in nameTable.names}
		nextId = max(existingIds.keys()) + 1 if existingIds else 256
		nextId = max(nextId, 256)  # Ensure IDs start at 256 for new entries

		# Add style name if not already exists
		styleNameExists = False
		for nameID, nameStr in existingIds.items():
			if nameStr == self.styleName and nameTable.getName(nameID, 3, 1, 0x409):
				self.nameIds['styleName'] = nameID
				styleNameExists = True
				break
	
		if not styleNameExists:
			nameTable.setName(self.styleName, nextId, 3, 1, 0x409)
			self.nameIds['styleName'] = nextId
			nextId += 1

		# Add axis names with proper checks
		for tag in self.axisValues:
			axisName = PREDEFINED_AXIS_NAMES.get(tag, f"{tag.upper()} Axis")
			axisExists = False
		
			# Check for existing axis name
			for nameID, nameStr in existingIds.items():
				if nameStr == axisName and nameTable.getName(nameID, 3, 1, 0x409):
					self.nameIds[tag] = nameID
					axisExists = True
					break
		
			if not axisExists:
				nameTable.setName(axisName, nextId, 3, 1, 0x409)
				self.nameIds[tag] = nextId
				nextId += 1

		return nameTable
	
	def run(self):
		font = TTFont(self.fontPath)
		
		if not self.styleName:
			self.styleName = self.getStyleName(font)
			
		if 'name' not in font:
			font['name'] = table__n_a_m_e()
			
		nameTable = self.updateNameTable(font['name'])
		fvarTable = self.createFvarTable(nameTable, font)
		font['fvar'] = fvarTable
		font.save(self.outputPath)
		print(f"✅ Saved font with fvar to {self.outputPath}")

def main():
	parser = argparse.ArgumentParser(
		description='Create fvar table with axis definitions',
		formatter_class=argparse.RawTextHelpFormatter
	)
	parser.add_argument('-f', '--font', nargs='+', required=True, help='Input font file(s), supports wildcards (e.g. *.ttf)')
	parser.add_argument('-o', '--output', help='Optional output font file (only for single input file, default: overwrite input file)')
	parser.add_argument('-s', '--style', help='Optional style name (default: name ID 17/2)')
	parser.add_argument('-a', '--axes', nargs='+', 
		help='Axis definitions (default: "wdth=*" "wght=*" "ital=*"):\n'
			'wght=400 → explicit value\n'
			'opsz=*   → auto-detect from size.subfamilyIdentifier\n'
			'wdth=*   → auto width percentage from OS/2.usWidthClass\n'
			'wght=*   → auto-detect from OS/2.usWeightClass\n'
			'ital=*   → auto-detect italic bit in OS/2.fsSelection\n'
			'slnt=*   → auto-detect from post.italicAngle\n',
		default=['wdth=*', 'wght=*', 'ital=*'])
	
	args = parser.parse_args()
	
	axisDict = {}
	for axis in args.axes:
		tag, _, value = axis.partition('=')
		tag = tag.strip().lower()
		axisDict[tag] = float(value) if value != '*' else None
		
	fontPaths = []
	for pattern in args.font:
		fontPaths.extend(glob.glob(pattern))
	if not fontPaths:
		print(f"❌ No font files found matching the given pattern(s): {args.font}.")
		sys.exit(1)

	for fontPath in fontPaths:
		outputPath = fontPath
		if len(fontPaths) == 1 and args.output:
			outputPath = args.output
		try:
			builder = FvarBuilder(
				fontPath=fontPath,
				outputPath=outputPath,
				styleName=args.style,
				axisValues=axisDict
			)
			builder.run()
		except Exception as e:
			print(f"❌ Error processing {fontPath}: {str(e)}")
			import traceback
			print(traceback.format_exc())
			sys.exit(1)

if __name__ == '__main__':
	main()
