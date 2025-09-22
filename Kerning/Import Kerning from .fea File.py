# MenuTitle: Import Kerning from .fea File
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Choose an .fea file containing a kern feature in AFDKO code, and this script will attempt to import the kerning values into the frontmost font master (see Window > Kerning).
"""

"""
originally: importFea.py
Created by Georg Seifert on 2010-04-03.
Copyright (c) 2010 schriftgestaltung.de. All rights reserved.
"""

import os
from GlyphsApp import Glyphs, Message, GetOpenFile

leftSideMarkers = ("MMK_L_", "_1ST", "_first")
rightSideMarkers = ("MMK_R_", "_2ND", "_second")

def importFeaFileToCurrentMaster(font, filePath):
	master = font.selectedFontMaster
	if not master:
		Message(
			title="No Font Master Selected",
			message=f"Could not import .fea file because there is no font master selected in font ‘{font.familyName}’.",
			OKButton=None,
			)
		return

	if not os.path.isfile(filePath):
		Message(
			title="No .fea File",
			message=f"Could not import .fea file because there appears to be no such file at {filePath}.",
			OKButton=None,
			)
		return
		
	kerningLines = []
	feaFile = open(filePath)
	currentLine = feaFile.readline()
	groupNameDict = {}
	while (currentLine != ""): # end of file
		if (currentLine[0] == "@"):
			while "  " in currentLine:
				currentLine = currentLine.replace("  ", " ")
			groupName = currentLine[currentLine.find("@"):currentLine.find("=")].strip()
			glyphNames = currentLine[currentLine.find("[")+1:currentLine.find("]")].strip().split(" ")
			left = True
			right = True
			if any(subString in groupName for subString in leftSideMarkers):
				right = False
			elif any(subString in groupName for subString in rightSideMarkers):
				left = False
			oldGroupName = groupName
			for nameParticle in leftSideMarkers + rightSideMarkers + ("@", "."):
				groupName = groupName.replace(nameParticle, "")
			# groupName = Glyphs.niceGlyphName(groupName)
			for glyphName in glyphNames:
				glyphName = Glyphs.niceGlyphName(glyphName)
				glyph = font.glyphs[glyphName]
				if glyph:
					if left:
						glyph.rightKerningGroup = groupName
					if right:
						glyph.leftKerningGroup = groupName
			newGroupName = f"@MMK_{'L' if left else 'R'}_{groupName}"
			groupNameDict[oldGroupName] = newGroupName
		elif currentLine.strip().find("pos") == 0:
			kerningLines.append(currentLine.strip())
		currentLine = feaFile.readline() # read the next line

	if len(kerningLines) > 0:
		for i in range(len(kerningLines)-1, -1, -1):
			line = kerningLines[i]
			keys = line.split(" ")
			leftKey = keys[1]
			rightKey = keys[2]
			kernValue = keys[3]

			if leftKey[0] == "@":
				if leftKey in groupNameDict.keys():
					leftKey = groupNameDict[leftKey]
			else:
				leftKey = leftKey.strip("[]")
				leftKey = font.glyphs[leftKey].id

			if rightKey[0] == "@":
				if rightKey in groupNameDict.keys():
					rightKey = groupNameDict[rightKey]
			else:
				rightKey = rightKey.strip("[]")
				rightKey = font.glyphs[rightKey].id

			kernValue = float(kernValue.replace(";", ""))
			font.setKerningForPair(
				master.id, # fontMasterId (str) – The id of the FontMaster
				leftKey, # leftKey (str) – either a glyph name or a class name
				rightKey, # rightKey (str) – either a glyph name or a class name
				kernValue, # value (float) – kerning value
				)


def main():
	font = Glyphs.font
	if font:
		feaFile = GetOpenFile(
			message="Choose .fea file containing kerning.",
			allowsMultipleSelection=False,
			filetypes=["fea"],
			path=os.path.dirname(font.filepath) if font.filepath else None,
			)
		if feaFile is not None:
			importFeaFileToCurrentMaster(font, feaFile)
	else:
		Message(
			title="No Font Open",
			message="This script requires one font for importing kerning.",
			OKButton=None,
			)


if __name__ == '__main__':
	main()
