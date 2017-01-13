#MenuTitle: New Tab with Correlated Diacritics
# -*- coding: utf-8 -*-
__doc__="""
Goes through your uppercase letters and lists all related glyphs in a new tab. E.g., Eacute, eacute.sc, eacute, eacute.ss01. Useful for seeing if the marks are in sync.
"""

thisFont = Glyphs.font # frontmost font
uppercaseLetters = [g for g in thisFont.glyphs if g.category == "Letter" and g.subCategory == "Uppercase" and g.export and g.layers[0].components]

def lowercaseGlyphName( thisGlyph ):
	oldName = thisGlyph.name
	if "." in oldName:
		dotPosition = oldName.find(".")
		newName = oldName[:dotPosition].lower() + oldName[dotPosition:]
	else:
		newName = oldName.lower()
	return newName
		
		

tabText = ""
#processedGlyphNames = [] # for avoiding duplicate mentions
for uppercaseLetter in uppercaseLetters:
	uppercaseName = uppercaseLetter.name
	print uppercaseLetter.name
	
	lowercaseName = lowercaseGlyphName( uppercaseLetter )
	otherUC = [g.name for g in thisFont.glyphs if g.category == "Letter" and g.name.startswith(uppercaseName) and g.name!=uppercaseName and g.script == uppercaseLetter.script and g.export]
	otherSC = [g.name for g in thisFont.glyphs if g.category == "Letter" and g.name.startswith(lowercaseName) and g.subCategory == "Smallcaps" and g.script == uppercaseLetter.script and g.export]
	otherLC = [g.name for g in thisFont.glyphs if g.category == "Letter" and g.name.startswith(lowercaseName) and g.subCategory == "Lowercase" and g.name!=lowercaseName and g.script == uppercaseLetter.script and g.export]
	
	#processedGlyphNames += otherUC
	
	newLine = "/%s /%s /%s /%s /%s\n" % (uppercaseName, "/".join(otherUC), "/".join(otherSC), lowercaseName, "/".join(otherLC))
	print newLine
	tabText += newLine

if tabText:
	# opens new Edit tab:
	thisFont.newTab( tabText )
	