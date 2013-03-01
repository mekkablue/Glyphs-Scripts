#MenuTitle: Export Kerning Info CSV
"""Export a CSV containing kerning info."""

import GlyphsApp
import commands
from types import *

Font = Glyphs.font
Doc  = Glyphs.currentDocument
selectedLayers = Doc.selectedLayers()

filename  = Font.familyName + ' kerning'  # filename without ending
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

for m in Font.masters:
	masterID = m.id
	masterName = m.name
	print "Gathering kerning info for Master", masterName
	
	for L in Font.kerning[ masterID ]:
		if L[0] == "@":
			nameL = "@" + L[7:]
		else:
			nameL = Font.glyphForId_(L).name

		for R in Font.kerning[masterID][L]:
			if R[0] == "@":
				nameR = "@" + R[7:]
			else:
				nameR = Font.glyphForId_(R).name

			myKerningPair = [ masterName, nameL, nameR, str(Font.kerning[masterID][L][R]) ]
			myExportString = myExportString + ( myDelim.join( myKerningPair ) + '\n' )

filepath = saveFileDialog( message="Export Kerning CSV", ProposedFileName=filename, filetypes=["csv","txt"] )

f = open( filepath, 'w' )
print "Exporting to:", f.name
f.write( myExportString )
f.close()
