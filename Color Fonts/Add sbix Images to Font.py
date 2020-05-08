#MenuTitle: Add sbix Images to Font
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Will get all PNG, GIF, JPG files in a folder and create iColor layers with them in the current font. File name convention: ‘glyphName resolution.suffix’, e.g., ‘Adieresis 128.png’.
"""

import os
from AppKit import NSFileManager

def process( thisLayer ):
	for thisPath in thisLayer.paths:
		if thisPath.closed:
			print("- closed path:")
		else:
			print("- open path:")
		for thisNode in thisPath.nodes:
			print("-- node %.1f %.1f (type %s)" % ( thisNode.x, thisNode.y, thisNode.type ))
	for thisComponent in thisLayer.components:
		print("- component %s at %.1f %.1f" % ( thisComponent.componentName, thisComponent.position.x, thisComponent.position.y ))
	for thisAnchor in thisLayer.anchors:
		print("- anchor %s at %.1f %.1f" % ( thisAnchor.name, thisAnchor.x, thisAnchor.y ))

def isAnImage(fileName):
	suffixes = ("png", "jpg", "jpeg", "gif", "pdf", "tif", "tiff")
	for suffix in suffixes:
		if fileName.endswith(".%s"%suffix):
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

fileManager = NSFileManager.alloc().init()
thisFont = Glyphs.font # frontmost font
if not thisFont:
	Message(title="No Font Error", message="Hey, look, I cannot add images to a font if there is no font open, can I?", OKButton="😬 Sorry")
else:
	Glyphs.clearLog() # clears log in Macro window
	print("Adding sbix images to %s..." % thisFont.familyName)
	thisFontMaster = thisFont.selectedFontMaster # active master
	sbixCount = 0

	thisFont.disableUpdateInterface() # suppresses UI updates in Font View

	folders = GetFolder(message="Choose one or more folders containing images.", allowsMultipleSelection = True)
	for folder in folders:
		for fileName in os.listdir(folder):
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
				
					glyph.beginUndo() # begin undo grouping
				
					# determine layer:
					sbixLayersForThisMaster = [l for l in glyph.layers if l.name==layerName and l.master==thisFontMaster]
					if len(sbixLayersForThisMaster)>0:
						layer = sbixLayersForThisMaster[0]
					else:
						layer = GSLayer()
						layer.setAssociatedMasterId_(thisFontMaster.id)
						glyph.layers.append(layer)
						layer.name = layerName
				
					# define as sbix and add image:
					layer.setBackgroundImage_(None)
					filePath = os.path.join(folder,fileName)
					image = GSBackgroundImage.alloc().initWithPath_(filePath)
					layer.backgroundImage = image
					try:
						# GLYPHS 3
						layer.setAppleColorLayer_(1)
					except:
						# GLYPHS 2
						pass
					sbixCount += 1
				
					glyph.endUndo()   # end undo grouping
					print("✅ %s: added image ‘%s’ on layer ‘%s’" % (glyphName, fileName, layer.name))

	thisFont.enableUpdateInterface() # re-enables UI updates in Font View

	print("Done.")
	
	# Floating notification:
	Glyphs.showNotification( 
		"%s: Done" % (thisFont.familyName),
		"Added %i images to iColor layers. Details in Macro Window" % sbixCount,
		)
