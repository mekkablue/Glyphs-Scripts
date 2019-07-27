#MenuTitle: Copy InDesign Test Text
# -*- coding: utf-8 -*-
__doc__="""
Copies a test text for InDesign into the clipboard.
"""
from AppKit import *

hangingindent = chr(7)
linelength = 45
thisFont = Glyphs.font # frontmost font
glyphs = [g for g in thisFont.glyphs if g.unicode and g.export and g.subCategory != "Nonspacing"]
glyphnames = [g.name for g in glyphs]

copyString = u""
lastCategory = None
j=0
for i in range(len(glyphs)):
	j+=1
	currGlyph = glyphs[i]
	currCategory = currGlyph.category
	if (j%linelength==0 or (lastCategory and lastCategory != currCategory) or currGlyph.name == "a") and not currCategory in ("Separator","Mark"):
		copyString += "\n"
		j=0
	copyString += currGlyph.glyphInfo.unicharString().replace(u"⁄",u" ⁄ ")
	if currGlyph.name == "ldot":
		copyString += "l"
	if currGlyph.name == "Ldot":
		copyString += "L"
	lastCategory = currCategory

languages = {
	"NLD": u"ÍJ́íj́=ÍJíj",
	"PLK": u"ĆŃÓŚŹćńóśź",
	"ROM": u"ŞŢşţ",
	"CAT": u"L·Ll·l",
	"TRK": u"Iıİi"
}

# figures:
allFeatures = [f.name for f in thisFont.features]
figurecount = 4
scFigures = [f for f in thisFont.glyphs if f.category == "Number" and (".c2sc" in f.name or ".smcp" in f.name or ".sc" in f.name)]
figurecount += len(scFigures)//10
figString = u" %s0123456789" % ("0" if "zero" in allFeatures else "")
copyString += ( u"\nfigures: %s%s\n" % (hangingindent, figurecount*figString) )

# small figures:
smallFiguresLine = u""
for smallFigFeature in ("sinf", "subs", "sups", "numr", "dnom"):
	if smallFigFeature in allFeatures and not smallFigFeature in smallFiguresLine:
		smallFiguresLine += u" %s: 0123456789" % smallFigFeature.replace(u"sinf",u"sinf/subs")
copyString += smallFiguresLine[1:] + "\n"

#copyString += "\n"

for feature in thisFont.features:
	if not feature.name in ("aalt", "ccmp", "salt", "cpsp", "numr", "dnom", "subs", "sups", "sinf", "lnum", "onum", "pnum", "tnum"):
		testtext = u""
		
		# hardcoded features:
		if feature.name == "locl":
			listOfFeatures = [f.name for f in Font.features]
			for lang in languages.keys():
				if " %s;"%lang in feature.code:
					langLetters = languages[lang]
					if "smcp" in listOfFeatures or "c2sc" in listOfFeatures:
						langLetters = u"%s %s" % (langLetters,langLetters)
					testtext += u" %s: %s" % (lang, langLetters)
				
		elif feature.name == "ordn":
			ordnDict = {
				"numero": u"No.8 No8",
				"ordfeminine": u"1a2a3a4a5a6a7a8a9a0a",
				"ordmasculine": u"1o2o3o4o5o6o7o8o9o0o"
			}
			for gName in ordnDict:
				if gName in glyphnames:
					testtext += u"%s " % ordnDict[gName]
		
		elif feature.name == "frac":
			testtext += u"12/34 56/78 90/12 34/56 78/90 23/41 67/85 01/29 45/63 89/07 34/12 78/56 12/90 56/34 90/78 41/23 85/67 29/01 63/45 07/89"
		
		# scan feature code for substitutions:
		elif "sub " in feature.code:
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
								if testtext and testtext[-1] != " ":
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
		
		# hardcoded contextual kerning:
		elif feature.name == "kern":
			testtext = u"L’Aquila d’Annunzio l’Oréal"
		
		testtext = testtext.replace("0123456789", " 0123456789 ").replace("  "," ")
		
		if "zero" in allFeatures and "0123456789" in testtext and not "00" in testtext:
			testtext = testtext.replace("0","00")
			
		copyString += u"%s: %s%s\n" % (feature.name, hangingindent, testtext)


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
