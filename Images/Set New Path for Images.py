#MenuTitle: Set New Path for Images
# -*- coding: utf-8 -*-
__doc__="""
Resets the path for placed images in selected glyphs. Useful if you have moved your images.
"""

import os

def process( thisLayer ):
	try:
		thisImage = thisLayer.backgroundImage
		thisImageFileName = os.path.basename( thisImage.path )
		thisImageNewFullPath = "%s/%s" % ( newFolder, thisImageFileName )
		thisImage.setImagePath_( thisImageNewFullPath )
	except Exception as e:
		if "NoneType" in str(e):
			return "No image found."
		else:
			return "Error: %s." % e
	
	return "new path %s" % thisImageNewFullPath

Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = Font.selectedLayers
newFolder = GetFolder( message="Choose location of placed images:", allowsMultipleSelection = False )

Glyphs.clearLog()
Glyphs.showMacroWindow()
Font.disableUpdateInterface()

if newFolder:
	print "New image path for selected glyphs:\n%s" % newFolder
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		thisGlyph.beginUndo()
		print "-- %s: %s" % ( thisGlyph.name, process( thisLayer ) )
		thisGlyph.endUndo()

Font.enableUpdateInterface()
