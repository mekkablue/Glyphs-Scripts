# MenuTitle: Add sbix Images to Font
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Will get all PNG, GIF, JPG files in a folder and create iColor layers with them in the current font. File name convention: ‘glyphName resolution.suffix’, e.g., ‘Adieresis 128.png’.
"""

import os
from AppKit import NSFileManager
from GlyphsApp import Glyphs, GSGlyph, GSLayer, GSBackgroundImage, Message, GetFolder


def isAnImage(fileName):
	suffixes = ("png", "jpg", "jpeg", "gif", "pdf", "tif", "tiff")
	for suffix in suffixes:
		if fileName.endswith(".%s" % suffix):
			return True
	return False


def analyseFileName(fileName):
	glyphName = fileName.split(" ")[0]
	resolution = None
	try:
		resolution = int(fileName.split(" ")[1].split(".")[0])
	except Exception as e:
		print("❌ Could not extract image size from file name:\n%s\n\nDetailed error:" % fileName)
		print(e)
		import traceback
		print(traceback.format_exc())
		print()
	return glyphName, resolution


def sortName(name):
	glyphName, resolution = analyseFileName(name)
	if not resolution:
		return name
	else:
		return "%s%10i" % (glyphName, resolution)


fileManager = NSFileManager.alloc().init()
thisFont = Glyphs.font  # frontmost font
if not thisFont:
	Message(title="No Font Error", message="Hey, look, I cannot add images to a font if there is no font open, can I?", OKButton="😬 Sorry")
else:
	Glyphs.clearLog()  # clears log in Macro window
	print("Adding sbix images to %s..." % thisFont.familyName)
	thisFontMaster = thisFont.selectedFontMaster  # active master
	sbixCount = 0

	thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
	try:
		folders = GetFolder(message="Choose one or more folders containing images.", allowsMultipleSelection=True)
		for folder in folders:
			for fileName in sorted(os.listdir(folder), key=lambda filename: sortName(filename)):
				if isAnImage(fileName) and " " in fileName:
					glyphName, resolution = analyseFileName(fileName)
					if resolution:
						layerName = "iColor %i" % resolution

						# determine glyph:
						glyph = thisFont.glyphs[glyphName]
						if not glyph:
							glyph = GSGlyph()
							glyph.name = glyphName
							thisFont.glyphs.append(glyph)
							glyph.updateGlyphInfo()

						# glyph.beginUndo()  # undo grouping causes crashes

						# determine layer:
						if Glyphs.versionNumber >= 3:
							# Glyphs 3
							sbixLayersForThisMaster = [layer for layer in glyph.layers if layer.attributes["sbixSize"] and layer.attributes["sbixSize"] == resolution]
							if len(sbixLayersForThisMaster) > 0:
								layer = sbixLayersForThisMaster[0]
							else:
								layer = GSLayer()
								layer.associatedMasterId = thisFontMaster.id
								glyph.layers.append(layer)
								layer.attributes["sbixSize"] = resolution
						else:
							# Glyphs 2
							sbixLayersForThisMaster = [layer for layer in glyph.layers if layer.name == layerName and layer.master == thisFontMaster]
							if len(sbixLayersForThisMaster) > 0:
								layer = sbixLayersForThisMaster[0]
							else:
								layer = GSLayer()
								layer.setAssociatedMasterId_(thisFontMaster.id)
								glyph.layers.append(layer)
								layer.name = layerName

						# define as sbix and add image:
						layer.setBackgroundImage_(None)
						filePath = os.path.join(folder, fileName)
						image = GSBackgroundImage.alloc().initWithPath_(filePath)
						layer.backgroundImage = image
						sbixCount += 1

						# glyph.endUndo()  # undo grouping causes crashes
						print("✅ %s: added image ‘%s’ on layer ‘%s’" % (glyphName, fileName, layer.name))

	except Exception as e:
		Glyphs.showMacroWindow()
		print("\n⚠️ Script Error:\n")
		import traceback
		print(traceback.format_exc())
		print()
		raise e
	finally:
		thisFont.enableUpdateInterface()  # re-enables UI updates in Font View

	print("Done.")

	# Floating notification:
	Glyphs.showNotification(
		"%s: Done" % (thisFont.familyName),
		"Added %i images to iColor layers. Details in Macro Window" % sbixCount,
	)
