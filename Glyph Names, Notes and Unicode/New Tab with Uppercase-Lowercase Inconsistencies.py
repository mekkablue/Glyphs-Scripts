#MenuTitle: New Tab with Uppercase-Lowercase Inconsistencies
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Opens a new Edit tab containing all glyphs without consistent case folding. Detailed report in Macro Window.
"""

Glyphs.clearLog() # clears log of Macro window
thisFont = Glyphs.font # frontmost font
print("UC/LC Consistency Report for: %s" % thisFont.familyName)

noCaseFolding = []
cannotToggleCase = []

for g in thisFont.glyphs:
	if g.subCategory == "Uppercase":
		ucChar = g.glyphInfo.unicharString()
		if ucChar:
			lcUnicode = "%04X"%ord( ucChar.lower() )	
			lcName = Glyphs.glyphInfoForUnicode(lcUnicode).name
			if not Font.glyphs[lcName]:
				print("Missing: /%s (LC of %s)" % (lcName, g.name))
				noCaseFolding.append(g.name)
		else:
			print("Cannot toggle case: /%s" % g.name)
			cannotToggleCase.append(g.name)
			
	elif g.subCategory == "Lowercase":
		lcChar = g.glyphInfo.unicharString()
		if lcChar:
			ucUnicode = "%04X"%ord( lcChar.upper() )	
			ucName = Glyphs.glyphInfoForUnicode(ucUnicode).name
			if not Font.glyphs[ucName]:
				print("Missing: /%s (UC of %s)" % (ucName, g.name))
				noCaseFolding.append(g.name)
		else:
			print("Cannot toggle case, please check manually: /%s" % g.name)
			cannotToggleCase.append(g.name)

print("Done.")

# open a new tab with the affected layers:
if noCaseFolding or cannotToggleCase:
	newTab = thisFont.newTab()
	tabText = ""
	if noCaseFolding:
		tabText += "Missing Casefold:\n"
		tabText += "/"+"/".join(noCaseFolding)
	if cannotToggleCase:
		tabText += "\n\n"
		tabText += "Cannot Toggle Case:\n"
		tabText += "/"+"/".join(cannotToggleCase)
	newTab.text = tabText.strip()
# otherwise send a message:
else:
	Message(
		title = "Nothing Found",
		message = "Could not find any glyphs without consistent case folding.",
		OKButton = u"🥳 Great!"
	)
	
