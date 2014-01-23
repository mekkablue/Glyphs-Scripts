#MenuTitle: Compare Font Info for Open Fonts
# -*- coding: utf-8 -*-
"""Analyzes font info entries in all open fonts and outputs differences."""

import GlyphsApp
Glyphs.clearLog()
Glyphs.showMacroWindow()

listOfData = [
	"File Path",
	"Family Name",
	"Version Number",
	"Date",
	"Copyright",
	"Designer",
	"Designer URL",
	"Manufacturer",
	"Manufacturer URL",
	"UPM",
	"Grid Length",
	"Disables Nice Names"
]

def fontinfo( thisFont ):
	return [
		thisFont.filepath,
		thisFont.familyName,
		"%i.%.3i" % (thisFont.versionMajor, thisFont.versionMinor),
		thisFont.date,
		thisFont.copyright,
		thisFont.designer,
		thisFont.designerURL,
		thisFont.manufacturer,
		thisFont.manufacturerURL,
		thisFont.upm,
		thisFont.gridLength,
		thisFont.disablesNiceNames
	]

Fonts = Glyphs.fonts
allFontsInfo = [ fontinfo(f) for f in Fonts ]
numberOfFonts = range(len( allFontsInfo ))

print "Analyzing Open Fonts ...\n"

for i in range( len( allFontsInfo )):
	infolist = [ info[i] for info in allFontsInfo ]
	
	if len(set( infolist ) ) != 1:
		numberedData = zip( numberOfFonts, infolist )
		print "%s:" % listOfData[i]
		print "\n".join( [ "  %i: %s" % ( dat[0], dat[1] ) for dat in numberedData ] )
		print
