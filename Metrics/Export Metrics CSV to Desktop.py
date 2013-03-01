#MenuTitle: Export Glyph Info CSV
"""Export a CSV to the Desktop containing info about the glyphs."""

import GlyphsApp
import commands
from types import *

Font = Glyphs.font
Doc  = Glyphs.currentDocument
selectedLayers = Doc.selectedLayers()

filename  = Font.familyName + ' metrics'  # filename without ending
ending    = 'csv'       # txt|csv
myDelim   = ";"         # use "\t" for tab
myExportString = ""

def process( thisLayer ):
	myExportList = []
	
	myExportList.append( str(thisLayer.parent.name) )
	myExportList.append( str(thisLayer.name) )
	myExportList.append( str(thisLayer.LSB) )
	myExportList.append( str(thisLayer.RSB) )
	myExportList.append( str(thisLayer.width) )
	
	return myExportList
	

for thisLayer in selectedLayers:
	print "Processing", thisLayer.parent.name
	myExportString = myExportString + ( myDelim.join( process( thisLayer ) ) + '\n' )

directory = commands.getoutput('echo ~') + '/Desktop/'
filepath  = directory + filename + '.' + ending
f = open( filepath, 'w' )
print "Exporting values to:", f.name
f.write( myExportString )
f.close()
