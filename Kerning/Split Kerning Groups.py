#MenuTitle: Split Kerning Groups
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
In existing group kerning, separate some glyphs out of a kerning group, effectively duplicating the kern groups with the new group.
"""

import vanilla, sys
from mekkablue import *

def splitOffGroup(font, newGroup, splitoffs, rightGroup=True):
	totalCount = 0
	firstSplitoff = font.glyphs[splitoffs[0]]
	if not firstSplitoff:
		print(f"❌ Error: glyph {splitoffs[0]} not in font {font.familyName}.")
		return
	if rightGroup:
		group = firstSplitoff.rightKerningGroup
		if not group:
			print(f"❌ Error: primary glyph {splitoffs[0]} has no right kerning group.")
			return
		if group == newGroup:
			print(f"⚠️ Warning: new group name ‘{newGroup}’ is the same as the existing group name. Will only regroup glyphs.")
		else:
			groupName = f"@MMK_L_{group}"
			newGroupName = f"@MMK_L_{newGroup}".replace("@MMK_L_@MMK_L_", "@MMK_L_") # sanity check
			for master in font.masters:
				font.kerning[master.id][newGroupName] = font.kerning[master.id][groupName]
				totalCount += len(font.kerning[master.id][newGroupName])
		regrouped = []
		for glyphName in splitoffs:
			glyph = font.glyphs[glyphName]
			if not glyph:
				print(f"⚠️ Warning: no glyph ‘{glyphName}’ in font. Skipping.")
				continue
			if glyph.rightKerningGroup == newGroup:
				continue
			regrouped.append(glyphName)
			glyph.rightKerningGroup = newGroup
	else:
		group = firstSplitoff.leftKerningGroup
		if not group:
			print(f"❌ Error: primary glyph {splitoffs[0]} has no left kerning group.")
			return
		if group == newGroup:
			print(f"⚠️ Warning: new group name ‘{newGroup}’ is the same as the existing group name. Will only regroup glyphs.")
		else:
			groupName = f"@MMK_R_{group}"
			newGroupName = f"@MMK_R_{newGroup}".replace("@MMK_R_@MMK_R_", "@MMK_R_") # sanity check
			for master in font.masters:
				for leftSide in font.kerning[master.id].keys():
					if groupName in font.kerning[master.id][leftSide].keys():
						font.kerning[master.id][leftSide][newGroupName] = font.kerning[master.id][leftSide][groupName]
						totalCount += 1
		regrouped = []
		for glyphName in splitoffs:
			glyph = font.glyphs[glyphName]
			if not glyph:
				print(f"⚠️ Warning: no glyph ‘{glyphName}’ in font. Skipping.")
				continue
			if glyph.leftKerningGroup == newGroup:
				continue
			regrouped.append(glyphName)
			glyph.leftKerningGroup = newGroup

	messages = ["✅ Done."]
	if newGroup != group:
		messages.append(f"Split @{newGroup} from @{group}.")
	messages.append(f"Added {totalCount} kern pair{'s' if totalCount!=1 else ''} in {len(font.masters)} master{'s' if len(font.masters)!=1 else ''}.")
	if regrouped:
		messages.append(f"Regrouped: {', '.join(regrouped)}.")
	print(" ".join(messages))
	return messages


class SplitKerningGroups(object):
	prefID = "com.mekkablue.SplitKerningGroups"
	prefDict = {
		# "prefName": defaultValue,
		"originalGroupName": "",
		"isRightGroup": 1,
		"newGroupName": "",
		"splitGlyphs": "",
		# "allFonts": False,
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 410
		windowHeight = 140
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 200 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Split Kerning Groups", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos+2, 85, 14), "Move glyphs in", sizeStyle="small", selectable=True)
		self.w.isRightGroup = vanilla.PopUpButton((inset+85, linePos, 85, 17), ("left group", "right group"), sizeStyle="small", callback=self.update)
		self.w.originalGroupName = vanilla.ComboBox((inset+85+85+5, linePos-2, -inset-25-130, 19), [], sizeStyle="small", callback=self.update)
		self.w.updateButton = UpdateButton((-inset-23-130, linePos-2, -inset-130, 18), callback=self.update)
		self.w.newGroupText = vanilla.TextBox((-inset-130, linePos+2, -inset-55, 14), "to new group", sizeStyle="small", selectable=True)
		self.w.newGroupName = vanilla.EditText((-inset-55, linePos-1, -inset, 19), "", callback=self.update, sizeStyle="small")
		linePos += lineHeight

		self.w.splitGlyphs = vanilla.EditText((inset, linePos, -inset, -inset-24), self.pref("splitGlyphs"), callback=self.SavePreferences, sizeStyle="small")
		
		# Buttons at bottom:
		self.w.status = vanilla.TextBox((inset, -20-inset, -inset, -inset), "🤖 Ready.", sizeStyle="small", selectable=True)
		self.w.runButton = vanilla.Button((-60-inset, -20-inset, -inset, -inset), "Split", sizeStyle="regular", callback=self.SplitKerningGroupsMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Split Kerning Groups’ could not load preferences. Will resort to defaults.")

		self.update(sender="first run")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def update(self, sender=None):
		font = Glyphs.font
		if not font:
			return
		if sender is self.w.isRightGroup or sender is self.w.updateButton or sender == "first run":
			self.populateGroups(isRightGroup=self.w.isRightGroup.get())
		if sender is self.w.originalGroupName or sender is self.w.updateButton or sender == "first run":
			self.populateSplitGlyphs(self.w.originalGroupName.get(), isRightGroup=self.w.isRightGroup.get())
		self.w.runButton.enable(self.w.newGroupName.get().strip())
		self.SavePreferences()
	
	def populateGroups(self, isRightGroup=True):
		font = Glyphs.font
		if not font:
			return
		groups = []
		for g in font.glyphs:
			if isRightGroup and not g.rightKerningGroup in groups:
				groups.append(g.rightKerningGroup)
			elif not isRightGroup and not g.leftKerningGroup in groups:
				groups.append(g.leftKerningGroup)
		userEntry = self.w.originalGroupName.get()
		self.w.originalGroupName.setItems(groups) # this deletes user entry
		self.w.originalGroupName.set(userEntry)
		
	def populateSplitGlyphs(self, groupName, isRightGroup=True):
		splitGlyphs = []
		font = Glyphs.font
		if not font:
			return
		for g in font.glyphs:
			if isRightGroup and g.rightKerningGroup == groupName:
				splitGlyphs.append(g.name)
			elif not isRightGroup and g.leftKerningGroup == groupName:
				splitGlyphs.append(g.name)
		self.w.splitGlyphs.set(" ".join(splitGlyphs))
		
	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				getattr(self.w, prefName).set(self.pref(prefName))
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def SplitKerningGroupsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Split Kerning Groups’ could not write preferences.")
			
			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(sys.modules[__name__], prefName, self.pref(prefName))
				except:
					fallbackValue = self.prefDict[prefName]
					print(f"⚠️ Could not set pref ‘{prefName}’, resorting to default value: ‘{fallbackValue}’.")
					setattr(sys.modules[__name__], prefName, fallbackValue)
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Split Kerning Groups: ‘{reportName}’")
				
				newGroupName = self.pref("newGroupName").replace(" ", "").strip()
				glyphNames = self.pref("splitGlyphs").replace(",", " ").replace("  ", " ").split(" ")
				messages = splitOffGroup(thisFont, newGroupName, glyphNames, rightGroup=self.pref("isRightGroup"))
				thisFont.newTab("/" + "/".join(glyphNames))
				
				statusMessages = [m for m in messages[1:] if not "Regrouped" in m]
				self.w.status.set("✅ " + " ".join(statusMessages))

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Split Kerning Groups Error: {e}")
			import traceback
			print(traceback.format_exc())

SplitKerningGroups()