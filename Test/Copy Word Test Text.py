#MenuTitle: Copy Word Test Text
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Copies a test text for Microsoft Word into the clipboard.
"""

from AppKit import NSStringPboardType, NSPasteboard
thisFont = Glyphs.font # frontmost font
Glyphs.clearLog() # clears macro window log
print("Copy Word Test Text")
print("Font: %s\n" % thisFont.familyName)

glyphs = [g for g in thisFont.glyphs if g.unicode and g.export and g.subCategory != "Nonspacing"]
glyphnames = [g.name for g in glyphs]

copyString = u""

# CHARSET:
lastCategory = None
errorCount = 0
for i, currGlyph in enumerate(glyphs):
	print("🔠 %s" % currGlyph.name)
	if currGlyph.category not in ("Number", ):
		currCategory = currGlyph.subCategory
	elif currGlyph.name in ("fraction", ):
		currCategory = "Number"
	else:
		currCategory = currGlyph.category

	if currCategory != lastCategory:
		caseChange = lastCategory in ("Uppercase", "Lowercase") and currGlyph.script == "latin"
		numberSwitch = "Number" in (lastCategory, currCategory)
		if caseChange or numberSwitch:
			copyString += "\n"

	charString = currGlyph.glyphInfo.unicharString()
	if not charString:
		if not currGlyph.unicode:
			print("⚠️ Cannot determine character for glyph: %s. Skipping." % currGlyph.name)
			errorCount += 1
			break
		else:
			Glyphs.glyphInfoForUnicode(currGlyph.unicode).unicharString()
	else:
		copyString += charString.replace(u"⁄", u" ⁄ ") # extra space for fraction
		if currGlyph.name == "ldot":
			copyString += "l"
		elif currGlyph.name == "Ldot":
			copyString += "L"

	lastCategory = currCategory

print("\n👨‍💻 Analysing OT features...")
# FEATURESET:
copyString += "\n\n"
for feature in thisFont.features:
	print("\t%s" % feature.name)
	if "ss" in feature.name or "lig" in feature.name:
		testtext = u""

		# scan feature code for substitutions:
		if "sub " in feature.code:
			lines = feature.code.splitlines()
			for l in lines:
				if l and l.startswith("sub "): # find a sub line
					l = l[4:l.find("by")] # get the glyphnames between sub and by
					featureglyphnames = l.replace("'", "").split(" ") # remove contextual tick, split them at the spaces
					for glyphname in featureglyphnames:
						if glyphname: # exclude a potential empty string
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

def setClipboard(myText):
	"""
	Sets the contents of the clipboard to myText.
	Returns True if successful, False if unsuccessful.
	"""
	try:
		myClipboard = NSPasteboard.generalPasteboard()
		myClipboard.declareTypes_owner_([NSStringPboardType], None)
		myClipboard.setString_forType_(myText, NSStringPboardType)
		return True
	except Exception as e:
		return False

print("\n💕 Copying test text into clipboard...")
if not setClipboard(copyString):
	print("⚠️ Could not set clipboard to ‘%s...’" % (copyString[:12]))

print("Done.")
# Floating notification:
Glyphs.showNotification(
	u"%s: Ready for Pasting" % (thisFont.familyName),
	u"Test text for MS Word in clipboard. Encountered %i error%s processing the font. Details in Macro Window." % (
		errorCount,
		"" if errorCount == 1 else "s",
		),
	)
