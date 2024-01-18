# MenuTitle: Compare Kerning Between Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Report differences in kerning structures between two masters.
"""

import vanilla
from GlyphsApp import Glyphs, GSControlLayer, Message
from mekkaCore import mekkaObject


class CompareKerningBetweenMasters(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"firstMaster": 0,
		"secondMaster": 0,
		"group2group": True,
		"group2glyph": True,
		"glyph2group": True,
		"glyph2glyph": True,
		"reuseTab": True,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 240
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Compare Kerning Between Masters",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 10, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Compare kerning between two masters in frontmost font:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		tab = 70
		self.w.firstMasterText = vanilla.TextBox((inset, linePos + 2, tab, 14), "1st Master:", sizeStyle="small", selectable=True)
		self.w.firstMaster = vanilla.PopUpButton((inset + tab, linePos, -inset, 17), self.menuItemsForFrontMostFont(), sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight

		self.w.secondMasterText = vanilla.TextBox((inset, linePos + 2, tab, 14), "2nd Master:", sizeStyle="small", selectable=True)
		self.w.secondMaster = vanilla.PopUpButton((inset + tab, linePos, -inset, 17), self.menuItemsForFrontMostFont(), sizeStyle="small", callback=self.SavePreferences)
		linePos += int(lineHeight * 1.5)

		self.w.kernTypeText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Types of kerning to compare:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		tab = 140
		self.w.group2group = vanilla.CheckBox((inset, linePos - 1, tab, 20), "@group ↔︎ @group", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.group2glyph = vanilla.CheckBox((inset + tab, linePos - 1, -inset + tab, 20), "@group ↔︎ glyph", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		self.w.glyph2group = vanilla.CheckBox((inset, linePos - 1, tab, 20), "glyph ↔︎ @group", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.glyph2glyph = vanilla.CheckBox((inset + tab, linePos - 1, -inset + tab, 20), "glyph ↔︎ glyph", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += int(lineHeight * 1.5)

		self.w.reuseTab = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		# Run Button:
		self.w.updateButton = vanilla.Button((-190 - inset, -20 - inset, -100 - inset, -inset), "Update", sizeStyle="regular", callback=self.updateUI)
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Compare", sizeStyle="regular", callback=self.CompareKerningBetweenMastersMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Compare Kerning Between Masters’ could not load preferences. Will resort to defaults.")

		# Open window and focus on it:
		self.verifyButtonStatus()
		self.w.open()
		self.w.makeKey()

	def menuItemsForFrontMostFont(self, sender=None):
		font = Glyphs.font
		if font:
			return [f"{m.name} (ID: {m.id})" for m in font.masters]
		else:
			return []

	def verifyButtonStatus(self, sender=None):
		font = Glyphs.font
		if not font or self.pref("firstMaster") == self.pref("secondMaster"):
			self.w.runButton.enable(False)
		else:
			self.w.runButton.enable(True)

	def updateUI(self, sender=None):
		menu = self.menuItemsForFrontMostFont()

		self.w.firstMaster.setItems(menu)
		leftChoice = self.pref("firstMaster")
		if len(menu) > leftChoice:
			self.w.firstMaster.set(leftChoice)

		self.w.secondMaster.setItems(menu)
		rightChoice = self.pref("secondMaster")
		if len(menu) > rightChoice:
			self.w.secondMaster.set(rightChoice)

		font = Glyphs.font
		if not font or self.pref("firstMaster") == self.pref("secondMaster"):
			self.w.runButton.enable(False)
		else:
			self.w.runButton.enable(True)

	def namesForGroupName(self, groupName, font, isLeft=True):
		names = []
		for g in font.glyphs:
			if isLeft:  # left side = right group
				if groupName[7:] == g.rightKerningGroup:
					names.append(g.name)
			else:
				if groupName[7:] == g.leftKerningGroup:
					names.append(g.name)
		return names

	def glyphNameForKerningName(self, name, font, isLeft=True):
		glyphName = None
		if name[0] == "@":
			names = self.namesForGroupName(name, font, isLeft=isLeft)
			if name.startswith("@MMK_"):
				glyphName = name.split("_")[2]
				if glyphName == "KO":
					glyphName = name.split("_")[3]
				if not font.glyphs[glyphName] or glyphName not in names:
					glyphName = None
			if not glyphName:
				for name in names:
					if font.glyphs[name]:
						glyphName = name
						break
		else:
			glyph = font.glyphForId_(name)
			if glyph:
				glyphName = glyph.name

		if glyphName:
			return glyphName
		else:
			print(f"⚠️ No glyph found for: {name}")
			return None

	def CompareKerningBetweenMastersMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Compare Kerning Between Masters’ could not write preferences.")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Compare Kerning  Between Masters Report for {reportName}")
				print()

				group2group = bool(self.pref("group2group"))
				group2glyph = bool(self.pref("group2glyph"))
				glyph2group = bool(self.pref("glyph2group"))
				glyph2glyph = bool(self.pref("glyph2glyph"))
				firstMaster = self.prefInt("firstMaster")
				secondMaster = self.prefInt("secondMaster")

				group2groupLayersMissingFirst = []
				group2glyphLayersMissingFirst = []
				glyph2groupLayersMissingFirst = []
				glyph2glyphLayersMissingFirst = []
				group2groupLayersMissingSecond = []
				group2glyphLayersMissingSecond = []
				glyph2groupLayersMissingSecond = []
				glyph2glyphLayersMissingSecond = []

				firstMasterChoice = self.w.firstMaster.getItems()[firstMaster]
				firstMasterID = firstMasterChoice.split("(ID: ")[1][:-1]
				firstMaster = thisFont.masters[firstMasterID]
				firstKerning = thisFont.kerning[firstMaster.id]

				secondMasterChoice = self.w.secondMaster.getItems()[secondMaster]
				secondMasterID = secondMasterChoice.split("(ID: ")[1][:-1]
				secondMaster = thisFont.masters[secondMasterID]
				secondKerning = thisFont.kerning[secondMaster.id]

				missingKernCount = 0

				for L in set(firstKerning.keys() + secondKerning.keys()):
					LisGroup = L[0] == "@"
					RKeys = []
					for kerning in (firstKerning, secondKerning):
						if L in kerning.keys():
							RKeys.extend(kerning[L].keys())
					for R in set(RKeys):
						RisGroup = R[0] == "@"
						Lname = L if LisGroup else thisFont.glyphForId_(L).name
						Rname = R if RisGroup else thisFont.glyphForId_(R).name
						kerningInFirstMaster = thisFont.kerningForPair(firstMasterID, Lname, Rname)
						kerningInSecondMaster = thisFont.kerningForPair(secondMasterID, Lname, Rname)
						if kerningInFirstMaster is None or kerningInSecondMaster is None:
							missingKernCount += 1
							targetList = None
							if LisGroup and RisGroup and group2group:
								if kerningInFirstMaster is None:
									targetList = group2groupLayersMissingFirst
								if kerningInSecondMaster is None:
									targetList = group2groupLayersMissingSecond
							if LisGroup and not RisGroup and group2glyph:
								if kerningInFirstMaster is None:
									targetList = group2glyphLayersMissingFirst
								if kerningInSecondMaster is None:
									targetList = group2glyphLayersMissingSecond
							if not LisGroup and not RisGroup and glyph2glyph:
								if kerningInFirstMaster is None:
									targetList = glyph2glyphLayersMissingFirst
								if kerningInSecondMaster is None:
									targetList = glyph2glyphLayersMissingSecond
							if not LisGroup and RisGroup and glyph2group:
								if kerningInFirstMaster is None:
									targetList = glyph2groupLayersMissingFirst
								if kerningInSecondMaster is None:
									targetList = glyph2groupLayersMissingSecond

							if targetList is not None:
								glyphNameOnLSide = self.glyphNameForKerningName(L, thisFont, isLeft=True)
								glyphNameOnRSide = self.glyphNameForKerningName(R, thisFont, isLeft=False)
								glyphOnLSide = thisFont.glyphs[glyphNameOnLSide]
								glyphOnRSide = thisFont.glyphs[glyphNameOnRSide]
								targetList.append(glyphOnLSide.layers[firstMaster.id])
								targetList.append(glyphOnRSide.layers[firstMaster.id])
								targetList.append(thisFont.glyphs["space"].layers[firstMaster.id])
								targetList.append(glyphOnLSide.layers[secondMaster.id])
								targetList.append(glyphOnRSide.layers[secondMaster.id])
								targetList.append(GSControlLayer.newline())

				if not missingKernCount:
					Message(
						title="No kern pair missing",
						message=f"Nothing missing in the kerning structure between masters ‘{firstMaster.name}’ and ‘{secondMaster.name}’, given your selection.",
						OKButton=None,
					)
				else:
					if self.pref("reuseTab") and thisFont.currentTab:
						tab = thisFont.currentTab
						tab.text = ""
					else:
						tab = thisFont.newTab()
					tab.graphicView().setDoSpacing_(0)
					tab.graphicView().setDoKerning_(1)
					tab.updateKerningButton()

					def addNewline():
						tab.layers.append(GSControlLayer.newline())

					def addToTab(text, masterID=firstMasterID):
						for char in text:
							glyph = thisFont.glyphForCharacter_(ord(char))
							if glyph:
								tab.layers.append(glyph.layers[masterID])
						addNewline()

					if group2groupLayersMissingFirst:
						addToTab(f"Group-group missing in {firstMaster.name}:")
						tab.layers.extend(group2groupLayersMissingFirst)
						addNewline()
					if group2groupLayersMissingSecond:
						addToTab(f"Group-group missing in {secondMaster.name}:", masterID=secondMasterID)
						tab.layers.extend(group2groupLayersMissingSecond)
						addNewline()

					if group2glyphLayersMissingFirst:
						addToTab(f"Group-glyph missing in {firstMaster.name}:")
						tab.layers.extend(group2glyphLayersMissingFirst)
						addNewline()
					if group2glyphLayersMissingSecond:
						addToTab(f"Group-glyph missing in {secondMaster.name}:", masterID=secondMasterID)
						tab.layers.extend(group2glyphLayersMissingSecond)
						addNewline()

					if glyph2groupLayersMissingFirst:
						addToTab(f"Glyph-group missing in {firstMaster.name}:")
						tab.layers.extend(glyph2groupLayersMissingFirst)
						addNewline()
					if glyph2groupLayersMissingSecond:
						addToTab(f"Glyph-group missing in {secondMaster.name}:", masterID=secondMasterID)
						tab.layers.extend(glyph2groupLayersMissingSecond)
						addNewline()

					if glyph2glyphLayersMissingFirst:
						addToTab(f"Glyph-glyph missing in {firstMaster.name}:")
						tab.layers.extend(glyph2glyphLayersMissingFirst)
						addNewline()
					if glyph2glyphLayersMissingSecond:
						addToTab(f"Glyph-glyph missing in {secondMaster.name}:", masterID=secondMasterID)
						tab.layers.extend(glyph2glyphLayersMissingSecond)
						addNewline()

			print(f"\nDone. Found {missingKernCount} cases of misisng kern pairs.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Compare Kerning  Between Masters Error: {e}")
			import traceback
			print(traceback.format_exc())


CompareKerningBetweenMasters()
