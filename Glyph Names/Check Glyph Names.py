#MenuTitle: Check Glyph Names
# encoding: utf-8
__doc__="""
Goes through all glyph names and looks for illegal characters.
"""

firstChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
otherChars = "0123456789._-"
legalChars = firstChars + otherChars
allowedNameExceptions = (".notdef", ".null")
allowedExceptionsAtBeginning = ("_cap.","_corner.","_smart.","_part.")

def nameBeginsWithAnyOfThese( thisName, beginnings ):
	for beginning in beginnings:
		if thisName.startswith(beginning):
			return True
	return False
	
def illegalCharInName( thisName ):
	for thisChar in thisName[1:]:
		if thisChar not in legalChars:
			return thisChar
	return False

thisFont = Glyphs.font
if not thisFont:
	print "No font open."
else:
	for thisGlyph in thisFont.glyphs: # all Glyphs
		thisName = thisGlyph.name.replace("\U","\u").decode('unicode-escape') 
		thisFirstChar = thisName[0]
		illegalChar = illegalCharInName(thisName)
		if illegalChar:
			print "'%s': illegal character '%s'" % ( thisName, illegalChar )
		elif thisFirstChar not in firstChars and thisName not in allowedNameExceptions:
			if thisFirstChar in otherChars:
				isAllowed = nameBeginsWithAnyOfThese( thisName, allowedExceptionsAtBeginning )
				if thisGlyph.export and isAllowed:
					print "'%s': OK, but should be non-exporting."
				elif not isAllowed:
					print "'%s': potentially problematic first character" % thisName
		
