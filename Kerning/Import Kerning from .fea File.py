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

import vanilla

from mekkablue import mekkaObject

from GlyphsApp import Glyphs, Message, GetOpenFile
try:
	from GlyphsApp import GSRTL
except ImportError:
	from GlyphsApp import RTL as GSRTL

from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut

leftSideMarkers = ("MMK_L_", "_1ST", "_first")
rightSideMarkers = ("MMK_R_", "_2ND", "_second")


def importFeaFileToMaster(font, master, filePath, isRTL=False):
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
			glyphNames = currentLine[currentLine.find("[") + 1:currentLine.find("]")].strip().split(" ")
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
					if isRTL:
						# mirrored: the visually leading side swaps for RTL text
						if right:
							glyph.rightKerningGroup = groupName
						if left:
							glyph.leftKerningGroup = groupName
					else:
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
		for i in range(len(kerningLines) - 1, -1, -1):
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
				leftGlyph = font.glyphs[leftKey]
				if not leftGlyph:
					continue
				leftKey = leftGlyph.id

			if rightKey[0] == "@":
				if rightKey in groupNameDict.keys():
					rightKey = groupNameDict[rightKey]
			else:
				rightKey = rightKey.strip("[]")
				rightGlyph = font.glyphs[rightKey]
				if not rightGlyph:
					continue
				rightKey = rightGlyph.id

			kernValue = float(kernValue.replace(";", ""))
			if isRTL:
				font.setKerningForPair(
					master.id, # fontMasterId (str) – The id of the FontMaster
					leftKey, # leftKey (str) – either a glyph name or a class name
					rightKey, # rightKey (str) – either a glyph name or a class name
					kernValue, # value (float) – kerning value
					direction=GSRTL,
					)
			else:
				font.setKerningForPair(
					master.id, # fontMasterId (str) – The id of the FontMaster
					leftKey, # leftKey (str) – either a glyph name or a class name
					rightKey, # rightKey (str) – either a glyph name or a class name
					kernValue, # value (float) – kerning value
					)


class ImportKerningFromFeaFile(mekkaObject):
	prefDict = {
		"RTL": False,
	}

	def __init__(self):
		windowWidth = 380
		windowHeight = 1 # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Import Kerning from .fea File",
			autosaveName=self.domain("mainwindow"),
			)

		inset = 15

		self.w.chooseButton = vanilla.Button("auto", "Choose .fea…", callback=self.chooseFile)
		self.w.filePathText = vanilla.TextBox("auto", "No file chosen", sizeStyle="small", selectable=True)

		self.w.RTL = vanilla.CheckBox("auto", "Kerning is for a Right-to-Left script", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.RTL.setToolTip("Enable if the .fea file contains kerning for a Right-to-Left script, so kerning classes and pairs are imported with the correct direction.")

		self.w.importButton = vanilla.Button("auto", "Import", callback=self.importFeaFileToCurrentMaster)
		self.w.closeButton = vanilla.Button("auto", "Close", callback=self.closeWindow)
		self.w.setDefaultButton(self.w.importButton)

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[chooseButton]-gap-[filePathText]-inset-|",
				"H:|-inset-[RTL]-(>=inset)-|",
				"H:|-(>=inset)-[closeButton(>=70)]-gap-[importButton(>=70)]-inset-|",
				"V:|-inset-[chooseButton]-row-[RTL]-inset-[importButton]-inset-|",
				"V:[closeButton]-inset-|",
				{"view1": self.w.chooseButton, "attribute1": "centerY", "view2": self.w.filePathText, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8},
			)

		self.selectedPath = None

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def chooseFile(self, sender):
		font = Glyphs.font
		if not font:
			Message(
				title="No Font Open",
				message="This script requires one font for importing kerning.",
				OKButton=None,
				)
			return
		feaFile = GetOpenFile(
			message="Choose .fea file containing kerning.",
			allowsMultipleSelection=False,
			filetypes=["fea"],
			path=os.path.dirname(font.filepath) if font.filepath else None,
			)
		if feaFile:
			self.selectedPath = feaFile
			self.w.filePathText.set(self.selectedPath)
		else:
			self.selectedPath = None
			self.w.filePathText.set("No file chosen")

	def importFeaFileToCurrentMaster(self, sender):
		font = Glyphs.font
		if not font:
			Message(
				title="No Font Open",
				message="This script requires one font for importing kerning.",
				OKButton=None,
				)
			return

		master = font.selectedFontMaster
		if not master:
			Message(
				title="No Font Master Selected",
				message=f"Could not import .fea file because there is no font master selected in font ‘{font.familyName}’.",
				OKButton=None,
				)
			return

		if not self.selectedPath:
			Message(
				title="No .fea File",
				message="Please choose a .fea file first.",
				OKButton=None,
				)
			return

		isRTL = bool(self.w.RTL.get())
		importFeaFileToMaster(font, master, self.selectedPath, isRTL=isRTL)
		Glyphs.showNotification("Import Kerning from .fea File", "Done! Details in Macro Window.")

	def closeWindow(self, sender):
		self.w.close()


ImportKerningFromFeaFile()
