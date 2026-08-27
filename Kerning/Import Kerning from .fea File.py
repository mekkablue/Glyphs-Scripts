# MenuTitle: Import Kerning from .fea File
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from GlyphsApp import Glyphs, Message, GetOpenFile
import vanilla
from functools import partial
import os
__doc__ = """
Choose an .fea file containing a kern feature in AFDKO code, and this script will attempt to import the kerning values into the frontmost font master (see Window > Kerning).
"""

"""
originally: importFea.py
Created by Georg Seifert on 2010-04-03.
Copyright (c) 2010 schriftgestaltung.de. All rights reserved.
"""
leftSideMarkers = ("MMK_L_", "_1ST", "_first")
rightSideMarkers = ("MMK_R_", "_2ND", "_second")

class FeaImporterWindow(object):
	def __init__(self):
		self.w = vanilla.FloatingWindow((420, 110), "Import Kerning from .fea File")

		margin = 10

		self.w.chooseButton = vanilla.Button((margin, margin, 120, 24), "Choose .fea…", callback=self.chooseFile)
		self.w.filePathText = vanilla.TextBox((margin + 130, margin + 3, -margin, 20), "No file chosen")

		self.w.RTL = vanilla.CheckBox((margin, 46, 400, 20), "Kernings are for a Right to Left script", value=False)

		self.w.importButton = vanilla.Button((margin, 74, 120, 24), "Import", callback=self.importFeaFileToCurrentMaster)
		self.w.closeButton = vanilla.Button((-130, 74, 120, 24), "Close", callback=self.closeWindow)

		self.selectedPath = None

		self.w.open()
		self.w.makeKey()

	def chooseFile(self, sender):
		font = Glyphs.font
		if font:
			self.feaFile = GetOpenFile(
				message="Choose .fea file containing kerning.",
				allowsMultipleSelection=False,
				filetypes=["fea"],
				path=os.path.dirname(font.filepath) if font.filepath else None,
				)
			if self.feaFile:
				if isinstance(self.feaFile, (list, tuple)):
					feaFilePath = self.feaFile[0]
				else:
					feaFilePath = self.feaFile
				self.selectedPath = feaFilePath
				self.w.filePathText.set(self.selectedPath)
			else:
				self.selectedPath = None
				self.w.filePathText.set("No file chosen")
		else:
			Message(
				title="No Font Open",
				message="This script requires one font for importing kerning.",
				OKButton=None,
				)


	def importFeaFileToCurrentMaster(self,sender):
		font = Glyphs.font
		isRTL = bool(self.w.RTL.get())
		master = font.selectedFontMaster
		kerningLines = []
		feaFile = open(self.feaFile)
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
				if isRTL:
					if glyph:
						if right:
							glyph.rightKerningGroup = groupName
						if left:
							glyph.leftKerningGroup = groupName
				else:
					if glyph:
						if left:
							glyph.rightKerningGroup = groupName
						if right:
							glyph.leftKerningGroup = groupName
				if isRTL:
					newGroupName = f"@MMK_{'L' if right else 'R'}_{groupName}"
				else:
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
					print(font.glyphs[leftKey])
					leftKey = font.glyphs[leftKey].id
	
				if rightKey[0] == "@":
					if rightKey in groupNameDict.keys():
						rightKey = groupNameDict[rightKey]
				else:
					rightKey = rightKey.strip("[]")
					rightKey = font.glyphs[rightKey].id
					
				kernValue = float(kernValue.replace(";", ""))
				if isRTL:
					font.setKerningForPair(
						master.id, # fontMasterId (str) – The id of the FontMaster
						leftKey, # leftKey (str) – either a glyph name or a class name
						rightKey, # rightKey (str) – either a glyph name or a class name
						kernValue, # value (float) – kerning value
						direction=GSRTL
						)
				else:
					font.setKerningForPair(
						master.id, # fontMasterId (str) – The id of the FontMaster
						leftKey, # leftKey (str) – either a glyph name or a class name
						rightKey, # rightKey (str) – either a glyph name or a class name
						kernValue, # value (float) – kerning value
						)
	def closeWindow(self, sender):
		self.w.close()

FeaImporterWindow()
