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
	return stdout

getKernValuesFromInDesign = """
set kernvalues to ""
tell application "Adobe InDesign CS6"
	tell front document
		tell parent story of first text frame
			repeat with i from 1 to (count characters) - 1
				try
					set kernvalue to (kerning value of insertion point 2 of character i) as integer
					set kernvalueline to character i & character (i + 1) & " " & kernvalue
					log last word of kernvalueline
					set kernvalues to kernvalues & kernvalueline & "\n"
				end try
			end repeat
		end tell
	end tell
end tell
kernvalues
"""

getNameOfFont = """
tell application "Adobe InDesign CS6"
	tell front document
		tell character 1 of parent story of first text frame
			applied font
		end tell
	end tell
end tell
"""

kernInfo = runAppleScript( getKernValuesFromInDesign )
fontNames = runAppleScript( getNameOfFont )[5:-1].split("\t")

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

print "Font found in InDesign: %s (%s)" % (fontNames[0], fontNames[1])
print "Applying kerning to: %s, Master: %s" % (thisFont.familyName, thisFontMaster.name)

for thisline in kernInfo.splitlines():
	if len(thisline) > 5:
		leftSide = glyphNameForLetter(thisline[0])
		rightSide = glyphNameForLetter(thisline[1])
		kernValue = float(thisline[3:])
		try:
			thisFont.setKerningForPair(thisFontMasterID, leftSide, rightSide, kernValue)
			print "  Kerning for %s-%s set to %i." % (leftSide, rightSide, kernValue)
		except Exception as e:
			print "  ERROR: Could not set kerning for %s-%s (%i)." % (leftSide, rightSide, kernValue)
			


