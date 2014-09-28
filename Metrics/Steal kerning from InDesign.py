#MenuTitle: Steal kerning from InDesign
# -*- coding: utf-8 -*-
__doc__="""
Use the font in InD, set the kerning method to Optical, run this script.
"""

import GlyphsApp
from subprocess import Popen, PIPE

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
thisFontMasterID = thisFontMaster.id # active master id
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def glyphNameForLetter( letter ):
	glyphName = False
	if len(letter) > 0:
		letter = letter[0]
		utf16value = "%.4X" % ord(letter)
		glyphName = GSGlyphsInfo.alloc().init().nameForUnicode( utf16value )
	return glyphName

def runAppleScript(scpt, args=[]):
	p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate(scpt)
	if stderr:
		print "AppleScript Error:"
		print stderr.decode('utf-8')
	return stdout

getKernValuesFromInDesign = """
set kernvalues to ""
tell application "InDesign"
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
"""

getNameOfDocument = """
tell application "InDesign"
	tell front document
		name
	end tell
end tell
"""

getTextOfFrame = """
tell application "InDesign"
	tell front document
		contents of first text frame
	end tell
end tell
"""

getNameOfFont = """
tell application "InDesign"
	tell front document
		tell character 1 of parent story of first text frame
			applied font
		end tell
	end tell
end tell
"""

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

kernInfo  = unicode(runAppleScript( getKernValuesFromInDesign ), "utf-8")
fontName  = runAppleScript( getNameOfFont )
docName   = runAppleScript( getNameOfDocument )
frameText = runAppleScript( getTextOfFrame )

fontName = fontName.replace("\t", " ").replace("font ","").strip()
docName = docName.strip()
frameText = unicode(frameText.strip(), "utf-8")

if len(frameText) > 60:
	frameText = frameText[:60] + "..."

print "Extracting kerning from InD doc: %s" % docName
print "Found text: %s" % frameText
print "Found font: %s" % fontName
print "Applying kerning to: %s, Master: %s\n" % (thisFont.familyName, thisFontMaster.name)

for thisline in kernInfo.splitlines():
	if len(thisline) > 5:
		leftSide = glyphNameForLetter(thisline[0])
		rightSide = glyphNameForLetter(thisline[1])
		try:
			kernValue = float(thisline[3:])
		except:
			kernValue = 0.0
		try:
			thisFont.setKerningForPair(thisFontMasterID, leftSide, rightSide, kernValue)
			print "  Kerning for %s-%s set to %i." % (leftSide, rightSide, kernValue)
		except Exception as e:
			print "  ERROR: Could not set kerning for %s-%s (%i)." % (leftSide, rightSide, kernValue)
