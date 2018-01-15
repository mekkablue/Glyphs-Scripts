#MenuTitle: Check Glyph Names
# encoding: utf-8
__doc__="""
Goes through all glyph names and looks for illegal characters.
"""

firstChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
otherChars = "0123456789._-"
legalChars = firstChars + otherChars
exceptionList = [".notdef", ".null"]


allGlyphs = Glyphs.font.glyphs

def process( thisName ):
	thisFirstChar = thisName[0]
	
	if thisFirstChar not in firstChars and thisName not in exceptionList:
		if thisFirstChar in otherChars:
			print "'%s': potentially problematic first character" % thisName
		else:
			print "'%s': illegal first character" % thisName
		
	for thisChar in thisName[1:]:
		if thisChar not in legalChars:
			print "'%s': illegal character '%s'" % ( thisName, thisChar )

for thisGlyph in allGlyphs:
	process( thisGlyph.name.replace("\U","\u").decode('unicode-escape') )

