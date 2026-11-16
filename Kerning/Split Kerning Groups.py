# MenuTitle: Split Kerning Groups
__doc__ = """
In existing group kerning, separate some glyphs out of a kerning group, effectively duplicating the kern groups with the new group.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSSize, NSWindowStyleMaskResizable
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, reportFontName, UpdateButton

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
				# this does not work:
				# font.kerning[master.id][newGroupName] = copy(font.kerning[master.id][groupName])
				for rightKey in font.kerning[master.id][groupName].keys():
					value = font.kerning[master.id][groupName][rightKey]
					if not rightKey.startswith("@") and not font.glyphs[rightKey]:
						referencedGlyph = font.glyphForId_(rightKey)
						if referencedGlyph:
							rightKey = referencedGlyph.name
						else:
							print("⚠️ Warning: a kern pair is referencing a glyph that has been deleted. Clean up your kerning.")
							continue
					font.setKerningForPair(master.id, newGroupName, rightKey, value)
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


class SplitKerningGroups(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"originalGroupName": "",
		"isRightGroup": 1,
		"newGroupName": "",
		"splitGlyphs": "",
		# "allFonts": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 500
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Split Kerning Groups",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Move glyphs in", sizeStyle="small", selectable=True)
		self.w.isRightGroup = vanilla.PopUpButton("auto", ("left group", "right group"), sizeStyle="small", callback=self.update)
		self.w.originalGroupName = vanilla.ComboBox("auto", [], sizeStyle="small", callback=self.update)
		self.w.updateButton = UpdateButton("auto", callback=self.update)
		self.w.newGroupText = vanilla.TextBox("auto", "to new group", sizeStyle="small", selectable=True)
		self.w.newGroupName = vanilla.EditText("auto", "", callback=self.update, sizeStyle="small")

		self.w.splitGlyphs = vanilla.TextEditor("auto", "", callback=self.SavePreferences)

		# Buttons at bottom:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small", selectable=True)
		self.w.runButton = vanilla.Button("auto", "Split", callback=self.SplitKerningGroupsMain)
		self.w.setDefaultButton(self.w.runButton)

		# every control keeps its height, except the glyph list, which takes the leftover height:
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)
		self.w.splitGlyphs.getNSScrollView().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationVertical)

		# labels hug their text, so the fields take the leftover width:
		for labelName in ("descriptionText", "newGroupText"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# the status text gives way to the button:
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-gap-[isRightGroup]-gap-[originalGroupName(>=70)]-gap-[updateButton]-gap-[newGroupText]-gap-[newGroupName(>=70)]-inset-|",
				"H:|-inset-[splitGlyphs]-inset-|",
				"H:|-inset-[status]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-inset-[isRightGroup]-row-[splitGlyphs(>=60)]-row-[runButton]-inset-|",
				# one baseline per row:
				{"view1": self.w.descriptionText, "attribute1": "centerY", "view2": self.w.isRightGroup, "attribute2": "centerY"},
				{"view1": self.w.originalGroupName, "attribute1": "centerY", "view2": self.w.isRightGroup, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.isRightGroup, "attribute2": "centerY"},
				{"view1": self.w.newGroupText, "attribute1": "centerY", "view2": self.w.isRightGroup, "attribute2": "centerY"},
				{"view1": self.w.newGroupName, "attribute1": "centerY", "view2": self.w.isRightGroup, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				# both group fields get the same width:
				{"view1": self.w.originalGroupName, "attribute1": "width", "view2": self.w.newGroupName, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8},
		)

		# Load Settings:
		self.LoadPreferences()

		self.update(sender="first run")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# make the window resizable, starting at the size that Auto Layout determined.
		# (Content sizes set directly on the NSWindow, so the title bar is not counted twice.)
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()  # make sure the content has its final size before we read it
		contentSize = nsWindow.contentView().frame().size
		nsWindow.setContentMinSize_(NSSize(contentSize.width, contentSize.height))

	def update(self, sender=None):
		font = Glyphs.font
		if font:
			if sender is self.w.isRightGroup or sender is self.w.updateButton or sender == "first run":
				self.populateGroups(isRightGroup=self.w.isRightGroup.get())
			if sender is self.w.originalGroupName or sender is self.w.updateButton or sender == "first run":
				self.populateSplitGlyphs(self.w.originalGroupName.get(), isRightGroup=self.w.isRightGroup.get())
		self.w.runButton.enable(bool(font and self.w.newGroupName.get().strip()))
		self.SavePreferences()

	def populateGroups(self, isRightGroup=True):
		font = Glyphs.font
		if not font:
			return
		groups = []
		for glyph in font.glyphs:
			group = glyph.rightKerningGroup if isRightGroup else glyph.leftKerningGroup
			if group and group not in groups:
				groups.append(group)
		userEntry = self.w.originalGroupName.get()
		self.w.originalGroupName.setItems(groups)  # this deletes user entry
		self.w.originalGroupName.set(userEntry)

	def populateSplitGlyphs(self, groupName, isRightGroup=True):
		splitGlyphs = []
		font = Glyphs.font
		if not font:
			return
		for glyph in font.glyphs:
			group = glyph.rightKerningGroup if isRightGroup else glyph.leftKerningGroup
			if group == groupName:
				splitGlyphs.append(glyph.name)
		self.w.splitGlyphs.set(" ".join(splitGlyphs))

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
				reportName = reportFontName(thisFont)
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
