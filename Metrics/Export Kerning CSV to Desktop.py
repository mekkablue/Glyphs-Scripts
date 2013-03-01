#MenuTitle: Export Kerning Info CSV
"""Export a CSV to the Desktop containing kerning info."""

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

directory = commands.getoutput('echo ~') + '/Desktop/'
filepath  = directory + filename + '.' + ending
f = open( filepath, 'w' )
print "Exporting values to:", f.name
f.write( myExportString )
f.close()
