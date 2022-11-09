#MenuTitle: Import Kerning from .fea File
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Choose an .fea file containing a kern feature in AFDKO code, and this script will attempt to import the kerning values into the frontmost font master (see Window > Kerning).
"""
"""
importFea.py

Created by Georg Seifert on 2010-04-03.
Copyright (c) 2010 schriftgestaltung.de. All rights reserved.
"""

import sys, os

def importfea_file(Doc, filePath):
	if os.path.isfile(filePath):
		f = open(filePath)

		Font = Doc.font
		FontMasterIndex = Doc.windowControllers()[0].masterIndex()
		print(FontMasterIndex)
		GlyphsInfo = GSGlyphsInfo.sharedManager()
		FontMaster = Font.masters[FontMasterIndex]
		KerningLines = []
		Line = f.readline()
		while (len(Line) > 0):

			if (Line[0] == "@"):
				key = Line[0:Line.find(" ")]
				GlyphNames = Line[Line.find("[") + 1:-4].split(" ")
				Left = True #1ST
				Right = True
				if key.find("_1ST") > 0:
					Right = False
				elif key.find("_2ND") > 0:
					Left = False

				key = key.split("_")[1]
				key = GlyphsInfo.niceGlpyhNameForName_(key)

				for GlyphName in GlyphNames:
					GlyphName = GlyphsInfo.niceGlpyhNameForName_(GlyphName)
					Glyph = Font.glyphForName_(GlyphName)
					if Glyph:
						if Left:
							Glyph.setRightKerningGroup_(key)
						if Right:
							Glyph.setLeftKerningGroup_(key)
			elif Line.strip().find("pos") == 0:
				KerningLines.append(Line.strip())

			Line = f.readline()

		if len(KerningLines) > 0:
			for i in range(len(KerningLines) - 1, -1, -1):
				Line = KerningLines[i]
				Keys = Line.split(" ")
				LeftKey = Keys[1]
				RightKey = Keys[2]
				Value = Keys[3]
				if LeftKey[0] == "@":
					pass
				else:
					LeftKey = LeftKey.strip("[]")
					LeftKey = Font.glyphs[LeftKey].id

				if RightKey[0] == "@":
					pass
				else:
					RightKey = RightKey.strip("[]")
					RightKey = Font.glyphs[RightKey].id

				Value = float(Value.replace(";", ""))
				Font.setKerningForFontMasterID_LeftKey_RightKey_Value_(FontMaster.id, LeftKey, RightKey, Value)

def main():
	Doc = Glyphs.currentDocument
	if (Doc):
		result = GetFile("Choose fea file.", False, ["fea"])
		if result is not None:
			importfea_file(Doc, result)
	else:
		Message("Please open a document", "")

if __name__ == '__main__':
	main()
