# -*- coding: utf-8 -*-
"""
python3 fixgdef.py -h     ... help
python3 fixgdef.py *.ttf  ... apply to all TTFs in current dir
"""

from fontTools import ttLib
from argparse import ArgumentParser


parser = ArgumentParser(description="Fix GDEF definition of spacing, non-combining marks. Will switch to class 1 (‘base glyph’, single character, spacing glyph) if necessary.")

parser.add_argument(
	"fonts",
	nargs="+",
	metavar="font",
	help="One or more OTF/TTF files",
)


def fixGDEFinFont(font):
	"""Takes a ttLib.TTFont as argument."""
	madeChanges = False

	if "GDEF" not in font.keys():
		print("⚠️ No GDEF table found, skipping file.\n")
		return madeChanges

	gdef = font["GDEF"].table
	if not hasattr(gdef, "MarkGlyphSetsDef") or not gdef.MarkGlyphSetsDef:
		print("⚠️ No MarkGlyphSetsDef found in GDEF table.")
	else:
		print("Scanning MarkGlyphSetsDef...")
		legacyMarks = (
			"dieresis",
			"dotaccent",
			"grave",
			"acute",
			"hungarumlaut",
			"circumflex",
			"caron",
			"breve",
			"ring",
			"tilde",
			"macron",
			"cedilla",
			"ogonek",
			"uni02BB"
		)
		for coverage in gdef.MarkGlyphSetsDef.Coverage:
			for i in range(len(coverage.glyphs) - 1, -1, -1):
				glyph = coverage.glyphs[i]
				if glyph in legacyMarks:
					coverage.glyphs.pop(i)
					print(f"\t🚫 Removed {glyph} from GDEF.MarkGlyphSetsDef")
					madeChanges = True
				elif not (glyph.startswith("uni03") or "comb" in glyph):
					print(f"\t❓ {glyph}")
				# else:
				# 	print(f"\t✅ {glyph}")

	if not gdef.GlyphClassDef:
		print("⚠️ No GlyphClassDef found in GDEF table.")
	else:
		print("Scanning GlyphClassDef...")
		for legacyMark in legacyMarks:
			if legacyMark in gdef.GlyphClassDef.classDefs:
				classType = gdef.GlyphClassDef.classDefs[legacyMark]
				if classType != 1:
					gdef.GlyphClassDef.classDefs[legacyMark] = 1
					print(f"\t👨🏻‍🔧 Switched {legacyMark} from class {classType} to 1")
					madeChanges = True

	return madeChanges


arguments = parser.parse_args()
fonts = arguments.fonts
for fontpath in fonts:
	print(f"\n📄 {fontpath}")
	font = ttLib.TTFont(fontpath)
	changesMade = fixGDEFinFont(font)
	if changesMade:
		font.save(fontpath, reorderTables=False)
		print(f"💾 Saved {fontpath}\n")
	else:
		print("🤷🏻‍♀️ No changes made. File left unchanged.")

print("✅ Done.")
