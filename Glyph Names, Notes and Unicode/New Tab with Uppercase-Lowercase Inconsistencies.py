#MenuTitle: New Tab with Uppercase-Lowercase Inconsistencies
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Opens a new Edit tab containing all glyphs without consistent case folding. Detailed report in Macro Window.
"""

Glyphs.clearLog() # clears log of Macro window
thisFont = Glyphs.font # frontmost font
print("UC/LC Consistency Report for: %s" % thisFont.familyName)

noCaseFolding = []
noCaseFoldingNonExporting = []
cannotToggleCase = []
cannotToggleCaseNonExporting = []
caseFoldDoesNotExport = []

for g in thisFont.glyphs:
	if g.subCategory in ("Uppercase", "Lowercase"):
		if not g.glyphInfo:
			print("⚠️ No glyph info available for: /%s" % g.name)
		else:
			thisChar = g.glyphInfo.unicharString()
			if thisChar:
				otherUnicode, otherName = None, None
				if g.subCategory == "Uppercase":
					otherUnicode = "%04X" % ord(thisChar.lower())
					otherName = Glyphs.glyphInfoForUnicode(otherUnicode).name
				elif g.subCategory == "Lowercase":
					otherUnicode = "%04X" % ord(thisChar.upper())
					otherName = Glyphs.glyphInfoForUnicode(otherUnicode).name

				if otherName:
					if not Font.glyphs[otherName]:
						print("%s Missing: /%s (%s of %s)" % ("❌" if g.export else "⚠️", otherName, "LC" if g.subCategory == "Uppercase" else "UC", g.name))

						if g.export:
							noCaseFolding.append(g.name)
						else:
							noCaseFoldingNonExporting.append(g.name)

					elif g.export and not Font.glyphs[otherName].export:
						print("❌ Casefold does not export: /%s (%s of %s)" % (otherName, "LC" if g.subCategory == "Uppercase" else "UC", g.name))

						caseFoldDoesNotExport.append(g.name)
						caseFoldDoesNotExport.append(otherName)

			else:
				print("⚠️ Cannot toggle case: /%s" % g.name)
				if g.export:
					cannotToggleCase.append(g.name)
				else:
					cannotToggleCaseNonExporting.append(g.name)

print("Done.")

# open a new tab with the affected layers:
if noCaseFolding or cannotToggleCase:
	newTab = thisFont.newTab()
	tabText = ""
	if noCaseFolding:
		tabText += "Missing casefold:\n"
		tabText += "/" + "/".join(noCaseFolding)

	if cannotToggleCase:
		if tabText:
			tabText += "\n\n"
		tabText += "Cannot toggle case:\n"
		tabText += "/" + "/".join(cannotToggleCase)

	if caseFoldDoesNotExport:
		if tabText:
			tabText += "\n\n"
		tabText += "Casefold does not export:\n"
		tabText += "/" + "/".join(caseFoldDoesNotExport)

	if noCaseFoldingNonExporting:
		if tabText:
			tabText += "\n\n"
		tabText += "Missing casefold (not exporting):\n"
		tabText += "/" + "/".join(noCaseFoldingNonExporting)

	if cannotToggleCaseNonExporting:
		if tabText:
			tabText += "\n\n"
		tabText += "Cannot toggle case (not exporting):\n"
		tabText += "/" + "/".join(cannotToggleCaseNonExporting)

	newTab.text = tabText.strip()

# otherwise send a message:
else:
	Message(title="Nothing Found", message="Could not find any glyphs without consistent case folding.", OKButton=u"🥳 Great!")
