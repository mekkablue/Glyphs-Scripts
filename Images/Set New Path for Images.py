#MenuTitle: Set New Path for Images
# -*- coding: utf-8 -*-
__doc__="""
Resets the path for placed images in selected glyphs. Useful if you have moved your images.
"""

import GlyphsApp
from PyObjCTools.AppHelper import callAfter
import os

Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = Font.selectedLayers
newFolder = GetFolder( message="Choose location of placed images:", allowsMultipleSelection = False )
#newFolder = callAfter( GetFolder, message="Choose location of placed images:" ) # callAfter returns immediately with None. Glyphs 2 will run this script in the main thread so this is not needed.

Glyphs.clearLog()
Glyphs.showMacroWindow()
print "New image paths for selected glyphs:", newFolder

def process( thisLayer ):
	try:
		thisImage = thisLayer.backgroundImage()
		thisImageFileName = os.path.basename( thisImage.imagePath() )
		thisImageNewFullPath = "%s/%s" % ( newFolder, thisImageFileName )
		print "__path:", thisImageNewFullPath, os.path.join(newFolder, thisImageFileName)
		thisImage.setImagePath_( thisImageNewFullPath )
	except Exception as e:
		if "NoneType" in str(e):
			return "No image found."
		else:
			return "Error: %s." % e
	
	return "OK."

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo()	
	print "-- %s: %s" % ( thisGlyph.name, process( thisLayer ) )
	thisGlyph.endUndo()

Font.enableUpdateInterface()
