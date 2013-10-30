#MenuTitle: Export Glyph Info CSV
"""Export a CSV containing info about the glyphs."""

import GlyphsApp
import commands
from types import *

Font = Glyphs.font
selectedLayers = Font.selectedLayers

filename  = Font.familyName + ' metrics'  # filename without ending
ending    = 'csv'       # txt|csv
myDelim   = ";"         # use "\t" for tab
myExportString = ""

def saveFileDialog(message=None, ProposedFileName=None, filetypes=None):
	if filetypes is None:
		filetypes = []
	Panel = NSSavePanel.savePanel().retain()
	if message is not None:
		Panel.setTitle_(message)
	Panel.setCanChooseFiles_(True)
	Panel.setCanChooseDirectories_(False)
	Panel.setAllowedFileTypes_(filetypes)
	if ProposedFileName is not None:
		Panel.setNameFieldStringValue_(ProposedFileName)
	pressedButton = Panel.runModalForTypes_(filetypes)
	if pressedButton == 1: # 1=OK, 0=Cancel
		return Panel.filename()
	return None

def process( thisLayer ):
	myExportList = [
		str( thisLayer.parent.name ),
		str( thisLayer.name ),
		str( thisLayer.LSB ),
		str( thisLayer.RSB ),
		str( thisLayer.width )
	]
	return myExportList

for thisLayer in selectedLayers:
	print "Processing", thisLayer.parent.name
	myExportString = myExportString + ( myDelim.join( process( thisLayer ) ) + '\n' )

filepath = saveFileDialog( message="Export Metrics CSV", ProposedFileName=filename, filetypes=["csv","txt"] )

f = open( filepath, 'w' )
print "Exporting to:", f.name
f.write( myExportString )
f.close()
