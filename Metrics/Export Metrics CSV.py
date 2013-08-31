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

filepath = GetSaveFile( message="Export Metrics CSV", ProposedFileName=filename, filetypes=["csv","txt"] )
if filepath:
	f = open( filepath, 'w' )
	print "Exporting to:", f.name
	f.write( myExportString )
	f.close()
