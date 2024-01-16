# MenuTitle: New Tabs with Punctuation Kern Strings
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Outputs a kerning string with UC/LC/SC letters, figures, and punctuation. Hold down COMMAND and SHIFT to limit to encoded glyphs.
"""

from AppKit import NSPasteboard, NSStringPboardType, NSEvent, NSEventModifierFlagShift, NSEventModifierFlagCommand
from GlyphsApp import Glyphs, GSUppercase, GSLowercase, GSSmallcaps

keysPressed = NSEvent.modifierFlags()
shiftKeyPressed = keysPressed & NSEventModifierFlagShift == NSEventModifierFlagShift
commandKeyPressed = keysPressed & NSEventModifierFlagCommand == NSEventModifierFlagCommand
unicodeOnly = commandKeyPressed and shiftKeyPressed


def nameNotExcluded(suffix, exclusions):
	for excludedString in exclusions:
		if excludedString in suffix:
			return False
	return True


def pairAddition(i, pair, glyphname, linelength=10):
	if i % (linelength) == (linelength - 1):
		whitespace = "\\n"
	else:
		whitespace = " "
	return "%s/%s %s%s" % (pair[0], glyphname, pair[1], whitespace)


def singleAddition(i, single, glyphname, linelength=10):
	single = single.replace("/", "/slash ").replace("\\", "/backslash ")
	if i % (linelength) == (linelength - 1):
		whitespace = " %s\\n" % single
	else:
		whitespace = " "
	return "%s/%s%s" % (single, glyphname, whitespace)


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
		print(e)
		return False


# ingredients:
thisFont = Glyphs.font
mID = thisFont.selectedFontMaster.id

# disable reporter plugins (speeds up display)
Glyphs.defaults["visibleReporters"] = None

# exclusion list (please create a GitHub issue if you need more)
alwaysExclude = (".punch", ".game", "tic", "youlose", "p1win", "p2win", "RAINER", ".draw", ".win", ".circled")

# collect UC/LC/SC letters and figures:
smallcaps = [
	g.name for g in thisFont.glyphs
	if g.export and g.category == "Letter" and g.case == GSSmallcaps and len(g.layers[mID].paths) > 0 and nameNotExcluded(g.name, alwaysExclude) and (g.unicode or not unicodeOnly)
]
fig = [
	g.name for g in thisFont.glyphs if g.export and g.subCategory == "Decimal Digit" and ".tf" not in g.name and ".tosf" not in g.name and nameNotExcluded(g.name, alwaysExclude)
	and (g.unicode or not unicodeOnly)
]
uppercase = [
	g.name for g in thisFont.glyphs
	if g.export and g.category == "Letter" and g.case == GSUppercase and len(g.layers[mID].paths) > 0 and nameNotExcluded(g.name, alwaysExclude) and (g.unicode or not unicodeOnly)
]
lowercase = [
	g.name for g in thisFont.glyphs
	if g.export and g.category == "Letter" and g.case == GSLowercase and len(g.layers[mID].paths) > 0 and nameNotExcluded(g.name, alwaysExclude) and (g.unicode or not unicodeOnly)
]
smallcaps = [
	g.name for g in thisFont.glyphs
	if g.export and g.category == "Letter" and g.case == GSSmallcaps and len(g.layers[mID].paths) > 0 and nameNotExcluded(g.name, alwaysExclude) and (g.unicode or not unicodeOnly)
]

# collect greek letters for greek punctuation
uppercaseGRK = [g for g in uppercase if Glyphs.glyphInfoForName(g).script == "greek"]
lowercaseGRK = [g for g in lowercase if Glyphs.glyphInfoForName(g).script == "greek"]
smallcapsGRK = [g for g in smallcaps if Glyphs.glyphInfoForName(g).script == "greek"]

# clean up lowercase list:
fixDict = {
	"idotless": "i",
	"jdotless": "j"
}
for searchName in fixDict:
	replaceName = fixDict[searchName]
	if replaceName not in lowercase and searchName in lowercase:
		index = lowercase.index(searchName)
		lowercase[index] = replaceName

# punctuation:
pairsOrSingles = ["¿?", "¡!", ".", ",", ":", ";", "…", "()", "[]", "{}", "„“", "‚‘", "“”", "‘’", "«»", "»«", "‹›", "›‹", "-", "–", "—", "@", "*", "'", '"', "•", "|", "¦"]

# greek-only punctuation:
pairsOrSinglesGRK = ["·", ";"]

# finish up punctuation:
controlString = "".join(pairsOrSingles)

for thisPunctuation in [
	g.charString() for g in thisFont.glyphs
	if g.export and (not g.charString() in controlString) and g.category == "Punctuation" and nameNotExcluded(g.name, alwaysExclude) and (g.unicode or not unicodeOnly)
]:
	pairsOrSingles.append(thisPunctuation)

for thisPunctuation in [
	g.charString() for g in thisFont.glyphs if g.export and (not g.charString() in controlString) and g.category == "Punctuation" and g.script == "greek"
	and nameNotExcluded(g.name, alwaysExclude) and (g.unicode or not unicodeOnly)
]:
	pairsOrSinglesGRK.append(thisPunctuation)

# kern strings:
lower = ""
upper = ""
number = ""

# step through punctuation:
for pair in pairsOrSingles:
	if len(pair) == 2:  # it really is a pair
		for i, x in enumerate(lowercase):
			lower += pairAddition(i, pair, x, linelength=25)
		for i, x in enumerate(uppercase):
			upper += pairAddition(i, pair, x, linelength=25)
		for i, n in enumerate(fig):
			number += pairAddition(i, pair, n)

	else:  # is a single
		for i, x in enumerate(lowercase):
			lower += singleAddition(i, pair, x, linelength=25)
		for i, x in enumerate(uppercase):
			upper += singleAddition(i, pair, x, linelength=25)
		for i, n in enumerate(fig):
			number += singleAddition(i, pair, n)
		lower += pair
		upper += pair
		number += pair

	lower += "\n"
	upper += "\n"
	number += "\n"

# step through greek punctuation:
if uppercaseGRK or lowercaseGRK or smallcapsGRK:
	for pair in pairsOrSinglesGRK:
		if len(pair) == 2:  # it really is a pair
			for i, x in enumerate(lowercaseGRK):
				lower += pairAddition(i, pair, x, linelength=25)
			for i, x in enumerate(uppercaseGRK):
				upper += pairAddition(i, pair, x, linelength=25)
			for i, n in enumerate(fig):
				number += pairAddition(i, pair, n)

		else:  # is a single
			for i, x in enumerate(lowercaseGRK):
				lower += singleAddition(i, pair, x, linelength=25)
			for i, x in enumerate(uppercaseGRK):
				upper += singleAddition(i, pair, x, linelength=25)
			for i, n in enumerate(fig):
				number += singleAddition(i, pair, n)
			lower += pair
			upper += pair
			number += pair

		lower += "\n"
		upper += "\n"
		number += "\n"

Glyphs.clearLog()
Glyphs.showMacroWindow()

print(lower)
print(upper)
print(number)

if not setClipboard(lower + upper + number):
	print("Warning: could not set clipboard to %s" % ("clipboard text"))

# Floating notification:
Glyphs.showNotification(
	"%s kern strings in clipboard" % (thisFont.familyName),
	"Ready for pasting in Preferences > Sample Strings.",
)

newline = "\n"
# Doc = Glyphs.currentDocument
thisFont.newTab(lower.replace("\\n", newline).replace(newline + newline, newline))
thisFont.newTab(upper.replace("\\n", newline).replace(newline + newline, newline))
thisFont.newTab(number.replace("\\n", newline).replace(newline + newline, newline))
