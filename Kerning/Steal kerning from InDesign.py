#MenuTitle: Steal Kerning from InDesign
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Use the font in InD (set up a document with one text box on the first page, set the kerning method to Optical), then run this script.
"""

from Foundation import NSAppleScript, NSAppleEventDescriptor
from timeit import default_timer as timer

# start taking time:
start = timer()

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
thisFontMasterID = thisFontMaster.id # active master id
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

replacements = {
	"bullet character": "•",
	"copyright symbol": "©",
	"double left quote": "“",
	"double right quote": "”",
	"ellipsis character": "…",
	"Em dash": "—",
	"En dash": "–",
	"nonbreaking space": " ",
	"section symbol": "§",
	"single left quote": "‘",
	"single right quote": "’",
	"trademark symbol": "™",
	}

# brings macro window to front and clears its log:
Glyphs.clearLog()
# Glyphs.showMacroWindow()

def reportTimeInNaturalLanguage(seconds):
	if seconds > 60.0:
		timereport = "%i:%02i minutes" % (seconds // 60, seconds % 60)
	elif seconds < 1.0:
		timereport = "%.2f seconds" % seconds
	elif seconds < 20.0:
		timereport = "%.1f seconds" % seconds
	else:
		timereport = "%i seconds" % seconds
	return timereport

def glyphNameForLetter(letter):
	glyphName = False
	if len(letter) > 0:
		letter = letter[0]
		utf16value = "%.4X" % ord(letter)
		glyphName = Glyphs.glyphInfoForUnicode(utf16value).name
	return glyphName

def runAppleScript(scriptSource, args=[]):
	s = NSAppleScript.alloc().initWithSource_(scriptSource)
	result, error = s.executeAndReturnError_(None)
	if error:
		print("AppleScript Error:")
		print(error)
		print("Tried to run:")
		for i, line in enumerate(scriptSource.splitlines()):
			print("%03i" % (i + 1), line)
		return False
	if result:
		return result.stringValue()
	else:
		return True

def cleanText(thisText, cleanDict):
	"""cleanDict={"searchFor":"replaceWith"}"""
	for searchFor in cleanDict.keys():
		replaceWith = cleanDict[searchFor]
		thisText = thisText.replace(searchFor, replaceWith)
	return thisText

# Determine InDesign application name (for use in the AppleScripts):

Glyphs.registerDefault("com.mekkablue.stealKerningFromInDesign.indesignAppName", "Adobe InDesign")

getInDesign = """
try
	set InDesign to application "%s"
on error
	set InDesign to choose application with title "Please choose Adobe InDesign"
end try
InDesign as string
""" % Glyphs.defaults["com.mekkablue.stealKerningFromInDesign.indesignAppName"]

indesign = runAppleScript(getInDesign)
if indesign != Glyphs.defaults["com.mekkablue.stealKerningFromInDesign.indesignAppName"]:
	Glyphs.defaults["com.mekkablue.stealKerningFromInDesign.indesignAppName"] = indesign
print("Accessing: %s" % indesign)

# Define AppleScripts to be run later:

getKernValuesFromInDesign = """
set kernvalues to ""
tell application "%s"
	tell front document
		tell parent story of first text frame
			repeat with i from 1 to (count characters) - 1
				try
					set kernvalue to (kerning value of insertion point 2 of character i) as integer
					set kernvalueline to character i & character (i + 1) & " " & kernvalue
					set kernvalues to kernvalues & kernvalueline & "\n"
				end try
			end repeat
		end tell
	end tell
end tell
kernvalues
""" % indesign

getNameOfDocument = """
tell application "%s"
	tell front document
		name
	end tell
end tell
""" % indesign

getTextOfFrame = """
tell application "%s"
	tell front document
		contents of first text frame
	end tell
end tell
""" % indesign

getNameOfFont = """
tell application "%s"
	tell front document
		tell first text frame
			tell character 1 of parent story
				name of applied font
			end tell
		end tell
	end tell
end tell
""" % indesign

# Execute AppleScripts and store results in variables:

# Extract document name and report:
try:
	docName = runAppleScript(getNameOfDocument)
	docName = unicode(docName).strip()
	print(f"\nExtracting kerning from document: {docName}")
except Exception as e:
	print("\nERROR while trying to extract the name of the first InDesign document.")
	print(
		"Possible causes:\n  1. No permissions in System Preferences > Security & Privacy > Privacy > Automation > Glyphs. Please review.\n  2. No document open in InDesign; will try to continue.\n  3. New document has not been saved yet."
		)
	print(e)
	print()

# Extract text and report:
try:
	frameText = runAppleScript(getTextOfFrame)
	frameText = "%.60s..." % frameText.strip()
	print(f"\nFound text: {frameText}")
except Exception as e:
	print("\nERROR while trying to extract the text of the first text frame.")
	print(
		"Possible causes:\n  1. No permissions in System Preferences > Security & Privacy > Privacy > Automation > Glyphs. Please review.\n  2. No text frame in the frontmost document in InDesign; will try to continue."
		)
	print(e)
	print()

# Extract font name and report:
try:
	fontName = runAppleScript(getNameOfFont)
	fontName = fontName.replace("\t", " ").replace("font ", "").strip()
	print(f"\nFound font: {fontName}")
	print("\nProcessing, please wait. Can take a minute...\n")
except Exception as e:
	print("\nERROR while trying to extract the font in the first text frame.")
	print(
		"Possible causes:\n  1. No permissions in System Preferences > Security & Privacy > Privacy > Automation > Glyphs. Please review.\n  2. No text in the first text frame of the frontmost document in InDesign; will try to continue."
		)
	print(e)
	print()

# Extract kern strings and report:
kernInfo = runAppleScript(getKernValuesFromInDesign)
print(f"Applying kerning to: {thisFont.familyName}, Master: {thisFontMaster.name}\n")

kernPairCount = 0

# Parse kern strings and set kerning in the font:
for thisLine in kernInfo.splitlines():
	if len(thisLine) > 3:
		# sometimes, InD returns a char description rather than a char 🤷🏻‍♀️, this is a hack that fixes it:
		thisLine = cleanText(thisLine, replacements)
		# check for left side:
		leftSide = glyphNameForLetter(thisLine[0])
		if not leftSide:
			print(f"WARNING:\n  Could not determine (left) glyph name: {thisLine[0]}.\n  Skipping pair ‘{thisLine[0]}{thisLine[1]}’.\n")
		else:
			if not thisFont.glyphs[leftSide]:
				print(f"WARNING:\n  Expected (left) glyph /{leftSide} not found in {thisFont.familyName}.\n  Skipping pair ‘{thisLine[0]}{thisLine[1]}’.\n")
			else:
				#check for right side:
				rightSide = glyphNameForLetter(thisLine[1])
				if not rightSide:
					print(f"WARNING:\n  Could not determine (right) glyph name: {thisLine[1]}.\n  Skipping pair ‘{thisLine[0]}{thisLine[1]}’.\n")
				else:
					if not thisFont.glyphs[rightSide]:
						print(f"WARNING:\n  Expected (right) glyph /{rightSide} not found in {thisFont.familyName}.\n  Skipping pair ‘{thisLine[0]}{thisLine[1]}’.\n")
					else:
						try:
							kernValue = float(thisLine[3:])
							if kernValue:
								thisFont.setKerningForPair(thisFontMasterID, leftSide, rightSide, kernValue)
								kernPairCount += 1
								print(f"  Kerning for {leftSide}:{rightSide} set to {kernValue}.")
							else:
								print(f"  No kerning {leftSide}:{rightSide}. Ignored.")
						except Exception as e:
							print(f"  ERROR: Could not set kerning for {leftSide}:{rightSide}.\n")
							print(e)
							print(f"  Offending line:\n  {thisLine}")
							import traceback
							print(traceback.format_exc())

# take time and report:
end = timer()
timereport = reportTimeInNaturalLanguage(end - start)
print(f"\nImported {kernPairCount} kern pairs.\nTime elapsed: {timereport}.")

# Floating notification:
Glyphs.showNotification(
	f"{kernPairCount} pairs for {thisFont.familyName}",
	f"Stolen from InDesign in {timereport}.",
	)
