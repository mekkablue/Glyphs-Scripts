#MenuTitle: Export CSV for Glyphs With Entry and Exit
# -*- coding: utf-8 -*-
__doc__="""
Creates a CSV file containing name of the glyph, the x and y distances, and the rectangle area between entry and exit anchors. Works for selected glyphs only.
"""



thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

filename  = thisFont.familyName + ' distances'  # filename without ending
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
	entryAnchor = thisLayer.anchors["entry"]
	exitAnchor = thisLayer.anchors["exit"]
	exportList = []
	if entryAnchor and exitAnchor:
		xDiff = entryAnchor.x - exitAnchor.x
		yDiff = entryAnchor.y - exitAnchor.y
		exportList.append( str(xDiff) )
		exportList.append( str(yDiff) )
		exportList.append( str(xDiff * yDiff) )
	return exportList


for thisLayer in listOfSelectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyphName = thisGlyph.name
	print "Analyzing", thisGlyphName
	glyphEntry = process( thisLayer )
	if glyphEntry:
		myExportString += myDelim.join([thisGlyphName]+glyphEntry)
	
filepath = saveFileDialog( message="Export Exit/Entry CSV", ProposedFileName=filename, filetypes=["csv","txt"] )

f = open( filepath, 'w' )
print "Exporting to:", f.name
f.write( myExportString )
f.close()
