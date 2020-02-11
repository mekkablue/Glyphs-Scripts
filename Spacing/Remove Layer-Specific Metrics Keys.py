#MenuTitle: Remove Layer-Specific Metrics Keys
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Deletes left and right metrics keys specific to layers (==), in all layers of all selected glyphs. Also simplifies glyph metrics keys (i.e., turns "=H" into "H").
"""

def FilterLayerKey(Key):
	if Key and Key.startswith("==") and Key.find("+") == -1 and Key.find("-") == -1 and Key.find("*") == -1 and Key.find("/") == -1:
		Key = Key[2:]
		return Key
	return None

def FilterGlyphKey(Key):
	if Key and Key.startswith("=") and Key.find("+") == -1 and Key.find("-") == -1 and Key.find("*") == -1 and Key.find("/") == -1:
		Key = Key[1:]
		return Key
	return None

def ReportGlyph(glyphName):
	print("Deleted metrics keys: %s" % thisGlyph.name)

def remove():
	for layer in Glyphs.font.selectedLayers:
		glyph = layer.parent
		deletedKeys = 0
		if glyph:
			for layer in glyph.layers:
				Key = FilterLayerKey(layer.leftMetricsKey)
				if Key is not None:
					layer.setLeftMetricsKey_(Key)
					deletedKeys += 1
				Key = FilterLayerKey(layer.rightMetricsKey)
				if Key is not None:
					layer.setRightMetricsKey_(Key)
					deletedKeys += 1
				Key = FilterLayerKey(layer.widthMetricsKey)
				if Key is not None:
					layer.setWidthMetricsKey_(Key)
					deletedKeys += 1
			Key = FilterGlyphKey(glyph.leftMetricsKey)
			if Key is not None:
				glyph.setLeftMetricsKey_(Key)
				deletedKeys += 1
			Key = FilterGlyphKey(glyph.rightMetricsKey)
			if Key is not None:
				glyph.setRightMetricsKey_(Key)
				deletedKeys += 1
			Key = FilterGlyphKey(glyph.widthMetricsKey)
			if Key is not None:
				glyph.setWidthMetricsKey_(Key)
				deletedKeys += 1
			
			if deletedKeys:
				print("Deleted %i metrics keys: %s" % (deletedKeys, glyph.name))
			
remove()