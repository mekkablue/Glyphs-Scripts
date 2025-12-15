#MenuTitle: Update Glyph Names in Features
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Like Glyph > Update Glyph Info, but in Font Info > Features.
"""

import re
from GlyphsApp import Glyphs, GSGlyphsInfo

RESERVED = {
	"feature", "lookup", "languagesystem", "script", "language", "table", "include",
	"sub", "substitute", "by", "from", "pos", "position", "enum",
	"markClass", "anchorDef", "valueRecordDef",
	"useExtension", "parameters", "excludeDFLT",
}

GLYPHNAMEREGEX = re.compile(r'([A-Za-z._][A-Za-z0-9_.-]*)')

font = Glyphs.font
if not font:
	raise Exception("No font open.")

Glyphs.clearLog()
print("Update Glyph Names in Features")
print(f"📄 {font.filepath or font.familyName}")
allGlyphNames = [g.name for g in font.glyphs]


def updateName(name):
	if name in allGlyphNames:
		return name
	newName = font.glyphsInfo().niceGlyphNameForName_(name) or name
	if newName not in allGlyphNames:
		print(f"⚠️ Glyph name not in font: {'/'.join(list(set([name, newName])))}. Left unchanged.")
		return name
	return newName


def updateLine(line):
	def repl(m):
		name = m.group(1)
		if name in RESERVED:
			return name
		newName = updateName(name)
		return newName if newName else name
	return GLYPHNAMEREGEX.sub(repl, line)


def convertCodeToNiceNames(feature):
	if feature.automatic:
		return
	featureCode = feature.code
	codeLines = featureCode.splitlines()
	change = 0
	for i in range(len(codeLines)):
		oldLine = codeLines[i]
		newLine = updateLine(oldLine)
		if oldLine != newLine:
			codeLines[i] = newLine
			change += 1
	if change != 0:
		print(f"🕹️ {feature.name}: {change} line{'' if change==1 else 's'} updated.")
		feature.code = "\n".join(codeLines)


print("\n⚙️ Updating OT Features...")
for otFeature in font.features:
	convertCodeToNiceNames(otFeature)

print("\n⚙️ Updating OT Prefixes...")
for otPrefix in font.featurePrefixes:
	convertCodeToNiceNames(otPrefix)

print("\n⚙️ Updating OT Classes...")
for otClass in font.classes:
	convertCodeToNiceNames(otClass)

print("\n✅ Done.")
font.parent.windowController().showFontInfoWindowWithTabSelected_(3)
