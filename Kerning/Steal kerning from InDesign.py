#MenuTitle: Steal Kerning from InDesign
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__="""
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

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

def reportTimeInNaturalLanguage( seconds ):
	if seconds > 60.0:
		timereport = "%i:%02i minutes" % ( seconds//60, seconds%60 )
	elif seconds < 1.0:
		timereport = "%.2f seconds" % seconds
	elif seconds < 20.0:
		timereport = "%.1f seconds" % seconds
	else:
		timereport = "%i seconds" % seconds
	return timereport

def glyphNameForLetter( letter ):
	glyphName = False
	if len(letter) > 0:
		letter = letter[0]
		utf16value = "%.4X" % ord(letter)
		glyphName = Glyphs.glyphInfoForUnicode( utf16value ).name
	return glyphName

def runAppleScript(scriptSource, args=[]):
	s = NSAppleScript.alloc().initWithSource_(scriptSource)
	result, error = s.executeAndReturnError_(None)
	if error:
		print("AppleScript Error:")
		print(error)
		print("Tried to run:")
		for i, line in enumerate(scriptSource.splitlines()):
			print("%03i"%(i+1), line)
		return False
	if result:
		return result.stringValue()
	else:
		return True

# Determine InDesign application name (for use in the AppleScripts):

Glyphs.registerDefault("com.mekkablue.stealKerningFromInDesign.indesignAppName","Adobe InDesign")

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
	docName = runAppleScript( getNameOfDocument )
	docName = unicode(docName).strip()
	print("\nExtracting kerning from document: %s" % docName)
except Exception as e:
	print("\nERROR while trying to extract the name of the first InDesign document.")
	print("Possible causes:\n  1. No permissions in System Preferences > Security & Privacy > Privacy > Automation > Glyphs. Please review.\n  2. No document open in InDesign; will try to continue.")
	print(e)
	print()

# Extract text and report:
try:
	frameText = runAppleScript( getTextOfFrame )
	frameText = "%.60s..." % frameText.strip()
	print("\nFound text: %s" % frameText)
except Exception as e:
	print("\nERROR while trying to extract the text of the first text frame.")
	print("Possible causes:\n  1. No permissions in System Preferences > Security & Privacy > Privacy > Automation > Glyphs. Please review.\n  2. No text frame in the frontmost document in InDesign; will try to continue.")
	print(e)
	print()

# Extract font name and report:
try:
	fontName = runAppleScript( getNameOfFont )
	fontName = fontName.replace("\t", " ").replace("font ","").strip()
	print("\nFound font: %s" % fontName)
	print("\nProcessing, please wait. Can take a minute...\n")
except Exception as e:
	print("\nERROR while trying to extract the font in the first text frame.")
	print("Possible causes:\n  1. No permissions in System Preferences > Security & Privacy > Privacy > Automation > Glyphs. Please review.\n  2. No text in the first text frame of the frontmost document in InDesign; will try to continue.")
	print(e)
	print()
	

# Extract kern strings and report:
kernInfo = runAppleScript( getKernValuesFromInDesign )
print(u"Applying kerning to: %s, Master: %s\n" % (thisFont.familyName, thisFontMaster.name))

kernPairCount = 0

# Parse kern strings and set kerning in the font:
for thisline in kernInfo.splitlines():
	if len(thisline) > 3:
		
		# check for left side:
		leftSide = glyphNameForLetter(thisline[0])
		if not leftSide:
			print(u"WARNING:\n  Could not determine (left) glyph name: %s.\n  Skipping pair ‘%s%s’.\n" % ( thisline[0], thisline[0], thisline[1]))
		else:
			if not thisFont.glyphs[leftSide]:
				print(u"WARNING:\n  Expected (left) glyph /%s not found in %s.\n  Skipping pair ‘%s%s’.\n" % ( leftSide, thisFont.familyName, thisline[0], thisline[1] ))
			else:
				#check for right side:
				rightSide = glyphNameForLetter(thisline[1])
				if not rightSide:
					print(u"WARNING:\n  Could not determine (right) glyph name: %s.\nS  kipping pair ‘%s%s’.\n" % ( thisline[1], thisline[0], thisline[1]))
				else:
					if not thisFont.glyphs[rightSide]:
						print(u"WARNING:\n  Expected (right) glyph /%s not found in %s.\n  Skipping pair ‘%s%s’.\n" % ( rightSide, thisFont.familyName, thisline[0], thisline[1] ))
					else:
						try:
							kernValue = float(thisline[3:])
							if kernValue:
								thisFont.setKerningForPair(thisFontMasterID, leftSide, rightSide, kernValue)
								kernPairCount += 1
								print("  Kerning for %s:%s set to %i." % (leftSide, rightSide, kernValue))
							else:
								print("  No kerning %s:%s. Ignored." % (leftSide, rightSide))
						except Exception as e:
							print("  ERROR: Could not set kerning for %s:%s.\n" % (leftSide, rightSide))
							print(e)
							import traceback
							print(traceback.format_exc())

# take time and report:
end = timer()
timereport = reportTimeInNaturalLanguage( end - start )
print("\nImported %i kern pairs.\nTime elapsed: %s." % (kernPairCount, timereport))

# Floating notification:
Glyphs.showNotification( 
	u"%i pairs for %s" % (kernPairCount, thisFont.familyName),
	u"Stolen from InDesign in %s." % timereport,
	)

