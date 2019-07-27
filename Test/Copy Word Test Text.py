#MenuTitle: Copy Word Test Text
# -*- coding: utf-8 -*-
__doc__="""
Copies a test text for Microsoft Word into the clipboard.
"""
from AppKit import *

thisFont = Glyphs.font # frontmost font
glyphs = [g for g in thisFont.glyphs if g.unicode and g.export and g.subCategory != "Nonspacing"]
glyphnames = [g.name for g in glyphs]

copyString = u""


# CHARSET:
lastCategory = None
for i, currGlyph in enumerate(glyphs):
	if currGlyph.category not in ("Number",):
		currCategory = currGlyph.subCategory
		if currCategory != lastCategory:
			if (lastCategory == "Uppercase" or lastCategory == "Lowercase") and currGlyph.script=="latin":
				print currGlyph, currGlyph.script
				copyString += "\n"

		copyString += currGlyph.glyphInfo.unicharString().replace(u"⁄",u" ⁄ ")
		if currGlyph.name == "ldot":
			copyString += "l"
		if currGlyph.name == "Ldot":
			copyString += "L"
		lastCategory = currCategory

# FEATURESET:
copyString += "\n\n"
for feature in thisFont.features:
	if "ss" in feature.name or "lig" in feature.name:
		testtext = u""

		# scan feature code for substitutions:
		if "sub " in feature.code:
			lines = feature.code.splitlines()
			for l in lines:
				if l and l.startswith("sub "): # find a sub line
					l = l[4:l.find("by")]      # get the glyphnames between sub and by
					featureglyphnames = l.replace("'","").split(" ")  # remove contextual tick, split them at the spaces
					for glyphname in featureglyphnames:
						if glyphname:          # exclude a potential empty string
							# suffixed glyphs:
							if "." in glyphname:
								glyphname = glyphname[:glyphname.find(".")]
								
							# ligatures:
							if "_" in glyphname:
								# add spaces between ligatures
								glyphname += "_space"
								if testtext[-1] != " ":
									testtext += " "
							
							# split ligature name, if any:
							subglyphnames = glyphname.split("_")
							for subglyphname in subglyphnames:
								gInfo = Glyphs.glyphInfoForName(subglyphname)
								if gInfo and gInfo.subCategory != "Nonspacing":
									try:
										testtext += gInfo.unicharString()
									except:
										pass
										
					# pad ligature letters in spaces:
					if "lig" in feature.name:
						testtext += " "
						
			if feature.name == "case":
				testtext = u"HO".join(testtext) + "HO"
		
		copyString += u"%s: %s\n" % (feature.name, testtext)

copyString += "\n\n"

def setClipboard( myText ):
	"""
	Sets the contents of the clipboard to myText.
	Returns True if successful, False if unsuccessful.
	"""
	try:
		myClipboard = NSPasteboard.generalPasteboard()
		myClipboard.declareTypes_owner_( [NSStringPboardType], None )
		myClipboard.setString_forType_( myText, NSStringPboardType )
		return True
	except Exception as e:
		return False

if not setClipboard(copyString):
	print "Warning: could not set clipboard to %s..." % ( copyString[:12] )
