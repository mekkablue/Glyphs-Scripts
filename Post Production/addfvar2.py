#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, sys, os, glob
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import table__f_v_a_r, Axis, NamedInstance
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e

PREDEFINED_AXES = {
	'wght': {'min': 1, 'max': 1000, 'name': 'Weight'},
	'wdth': {'min': 1, 'max': 1000, 'name': 'Width'},
	'ital': {'min': 0, 'max': 1, 'name': 'Italic'},
	'slnt': {'min': -90, 'max': 90, 'name': 'Slant'},
	'opsz': {'min': 1, 'max': 1000, 'name': 'Optical Size'}
}

def getNameByID(font, nameID):
	nameTable = font.get("name")
	if not nameTable:
		return None
	rec = nameTable.getName(nameID, 3, 1, 0x409)
	return rec.toUnicode() if rec else None

class FvarBuilder:
	def __init__(self, fontPath, outputPath, styleName, axisValues):
		self.fontPath = fontPath
		self.outputPath = outputPath
		self.styleName = styleName
		self.axisValues = axisValues
		self.nameIds = {}

	def getStyleName(self, font):
		"""Robust style name detection with multiple fallbacks"""
		# User-provided name
		if self.styleName:
			return self.styleName
		
		# Name table entries
		styleName = getNameByID(font, 17) or getNameByID(font, 2)
	
		# Filename parsing (e.g. "STCForward-Bold.ttf" → "Bold")
		if not styleName:
			base = os.path.basename(self.fontPath)
			styleName = os.path.splitext(base)[0].split('-')[-1]
			print(f"⚠️ Using filename-derived style name: {styleName}")
	
		# Ultimate fallback
		if not styleName:
			styleName = "Regular"
			print("⚠️ Using default style name: Regular")
		
		return styleName
	
	def resolveAxisValue(self, tag, font):
		if tag not in PREDEFINED_AXES:
			raise ValueError(f"Auto-detection not supported for {tag} axis")
		
		if tag == 'wght':
			return float(font['OS/2'].usWeightClass)
		elif tag == 'wdth':
			return self.widthClassToPercentage(font['OS/2'].usWidthClass)
		elif tag == 'ital':
			# First check OS/2 table
			if 'OS/2' in font:
				italBit = font['OS/2'].fsSelection & 1
				if italBit:
					return 1.0
			# Then check post table
			if 'post' in font and hasattr(font['post'], 'italicAngle'):
				return 1.0 if font['post'].italicAngle != 0 else 0.0
			# Final fallback for italic in filename
			if 'italic' in self.fontPath.lower():
				return 1.0
			return 0.0
		elif tag == 'slnt':
			return abs(font['post'].italicAngle)
		elif tag == 'opsz':
			return float(font['size'].subfamilyIdentifier)

	def widthClassToPercentage(self, widthClass):
		widthMap = {1:50, 2:62.5, 3:75, 4:87.5, 5:100, 6:112.5, 7:125, 8:150, 9:200}
		return widthMap.get(widthClass, 100.0)

	def createFvarTable(self, nameTable, font):
		fvarTable = table__f_v_a_r()
		fvarTable.axes = []
	
		for tag, config in self.axisValues.items():
			axis = Axis()
			axis.axisTag = tag
		
			# Get spec-defined min/max
			spec = PREDEFINED_AXES.get(tag, {'min': 1, 'max': 1000})
			spec_min = spec['min']
			spec_max = spec['max']

			# Resolve default value
			if config['auto']:
				default = self.resolveAxisValue(tag, font)
			else:
				default = config['default']

			# Determine min/max values
			if config.get('min') is None:
				min_val = spec_min
			else:
				min_val = max(config['min'], spec_min)
		
			if config.get('max') is None:
				max_val = spec_max
			else:
				max_val = min(config['max'], spec_max)

			# Clamp default to final min/max range
			default = max(min(default, max_val), min_val)

			# Set axis values
			axis.minValue = float(min_val)
			axis.defaultValue = float(default)
			axis.maxValue = float(max_val)
			axis.axisNameID = self.nameIds[tag]
			fvarTable.axes.append(axis)

		
		# Instance setup
		instance = NamedInstance()
		instance.subfamilyNameID = self.nameIds['styleName']
		instance.coordinates = {a.axisTag: a.defaultValue for a in fvarTable.axes}
		instance.postscriptNameID = 6  # Direct reference to nameID 6
		
		fvarTable.instances = [instance]
		return fvarTable

	def updateNameTable(self, nameTable):
		existing = {(rec.nameID, rec.toUnicode()) for rec in nameTable.names}
		nextID = max([rec.nameID for rec in nameTable.names] + [255]) + 1

		# Style name handling with fallback
		styleNameID = None
		for (nid, name) in existing:
			if name == self.styleName:
				styleNameID = nid
				break
			
		if not styleNameID:
			nameTable.setName(self.styleName, nextID, 3, 1, 0x409)
			styleNameID = nextID
			nextID += 1
		self.nameIds['styleName'] = styleNameID  # Always set this key

		# Axis name handling
		for tag in self.axisValues:
			axisName = PREDEFINED_AXES.get(tag, {}).get('name', f"{tag.upper()} Axis")
			axisExists = False
		
			for (nid, name) in existing:
				if name == axisName:
					self.nameIds[tag] = nid
					axisExists = True
					break
				
			if not axisExists:
				nameTable.setName(axisName, nextID, 3, 1, 0x409)
				self.nameIds[tag] = nextID
				nextID += 1

		return nameTable
	

	def run(self):
		font = TTFont(self.fontPath)
		
		if not self.styleName:
			self.styleName = getNameByID(font, 17) or getNameByID(font, 2)
			if not self.styleName:
				raise ValueError("No valid style name found")
		
		self.updateNameTable(font['name'])
		font['fvar'] = self.createFvarTable(font['name'], font)
		font.save(self.outputPath)
		print(f"✅ Saved {self.outputPath}")

def main():
	parser = argparse.ArgumentParser(description='Create fvar table with axis ranges')
	parser.add_argument('-f', '--font', required=True, help='Input font file(s)', nargs='+')
	parser.add_argument('-o', '--output', help='Output path (optional)')
	parser.add_argument('-s', '--style', help='Style name (optional)')
	parser.add_argument('-a', '--axes', nargs='+', help='Axis configs (tag=default,min,max or tag=*)', default=[])
	
	args = parser.parse_args()
	
	# Parse axis configurations
	axisConfigs = {}
	for entry in args.axes if args.axes else ['wght=*', 'wdth=*', 'ital=*']:
		tag, _, values = entry.partition('=')
		tag = tag.lower()
		
		if values == '*':
			axisConfigs[tag] = {'auto': True}
		else:
			parts = [p.strip() for p in values.split(',')]
			try:
				if len(parts) == 1:
					default = float(parts[0])
					axisConfigs[tag] = {'auto': False, 'default': default, 'min': default, 'max': default}
				elif len(parts) == 3:
					values = sorted([float(p) for p in parts])
					axisConfigs[tag] = {
						'auto': False,
						'default': values[1], # Middle value
						'min': values[0], # Sorted min
						'max': values[2]  # Sorted max
					}
				else:
					raise ValueError
			except:
				print(f"❌ Invalid axis format: {entry}")
				sys.exit(1)

	# Process fonts
	for pattern in args.font:
		for fontPath in glob.glob(pattern):
			outputPath = args.output or fontPath
			try:
				FvarBuilder(
					fontPath=fontPath,
					outputPath=outputPath,
					styleName=args.style,
					axisValues=axisConfigs
				).run()
			except Exception as e:
				print(f"❌ Error processing {fontPath}: {str(e)}")
				import traceback
				print(traceback.format_exc())
				print()

if __name__ == '__main__':
	main()
