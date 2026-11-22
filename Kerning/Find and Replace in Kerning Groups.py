# MenuTitle: Find and Replace in Kerning Groups
__doc__ = """
Finds and replaces text in the metrics keys of selected glyphs. Leave the Find string blank to hang the replace string at the end of the metrics keys.
"""

import vanilla
from mekkablue import mekkaObject, makeWindowResizable
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)


class KerningGroupReplacer(mekkaObject):
	prefDict = {
		"leftSearchFor": "",
		"leftReplaceBy": "",
		"rightSearchFor": "",
		"rightReplaceBy": "",
	}

	def __init__(self):
		windowWidth = 335
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Find and Replace in Kerning Groups",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		inset = 12

		self.w.descriptionText = vanilla.TextBox("auto", "In selected glyphs, replace in group names:", sizeStyle='small', selectable=True)

		self.w.text_left = vanilla.TextBox("auto", "Left Groups", sizeStyle='small')
		self.w.text_right = vanilla.TextBox("auto", "Right Groups", sizeStyle='small')

		self.w.text_Find = vanilla.TextBox("auto", "Find", sizeStyle='small')
		self.w.leftSearchFor = vanilla.EditText("auto", ".tf", callback=self.SavePreferences, sizeStyle='small', placeholder='(leave these blank ...')
		self.w.rightSearchFor = vanilla.EditText("auto", ".tf", callback=self.SavePreferences, sizeStyle='small', placeholder='... to append)')
		self.w.rightSearchFor.setToolTip("The text to find in the right kerning groups of the selected glyphs. Leave blank to append the replacement.")
		self.w.leftSearchFor.setToolTip("The text to find in the left kerning groups of the selected glyphs. Leave blank to append the replacement.")

		self.w.text_Replace = vanilla.TextBox("auto", "Replace", sizeStyle='small')
		self.w.leftReplaceBy = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)')
		self.w.leftReplaceBy.setToolTip("The text that replaces the search text in the left kerning groups.")
		self.w.rightReplaceBy = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)')
		self.w.rightReplaceBy.setToolTip("The text that replaces the search text in the right kerning groups.")

		self.w.runButton = vanilla.Button("auto", "Replace", callback=self.KerningGroupReplaceMain)
		self.w.runButton.setToolTip("Replaces the text in the kerning group names of the selected glyphs.")
		self.w.setDefaultButton(self.w.runButton)

		# with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned and hug their text, so the fields take the leftover width:
		for label in (self.w.text_Find, self.w.text_Replace):
			nsLabel = label.getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[text_Find]-gap-[leftSearchFor]-gap-[rightSearchFor]-inset-|",
				"H:|-inset-[text_Replace]-gap-[leftReplaceBy]-gap-[rightReplaceBy]-inset-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-gap-[text_left]-headGap-[leftSearchFor]-row-[leftReplaceBy]-inset-[runButton]-inset-|",
				{"view1": self.w.text_right, "attribute1": "centerY", "view2": self.w.text_left, "attribute2": "centerY"},
				{"view1": self.w.rightSearchFor, "attribute1": "centerY", "view2": self.w.leftSearchFor, "attribute2": "centerY"},
				{"view1": self.w.rightReplaceBy, "attribute1": "centerY", "view2": self.w.leftReplaceBy, "attribute2": "centerY"},
				{"view1": self.w.text_Find, "attribute1": "centerY", "view2": self.w.leftSearchFor, "attribute2": "centerY"},
				{"view1": self.w.text_Replace, "attribute1": "centerY", "view2": self.w.leftReplaceBy, "attribute2": "centerY"},
				# labels share one width, and so do the two columns:
				{"view1": self.w.text_Find, "attribute1": "width", "view2": self.w.text_Replace, "attribute2": "width"},
				{"view1": self.w.rightSearchFor, "attribute1": "width", "view2": self.w.leftSearchFor, "attribute2": "width"},
				{"view1": self.w.rightReplaceBy, "attribute1": "width", "view2": self.w.leftReplaceBy, "attribute2": "width"},
				# column headers sit above their columns:
				{"view1": self.w.text_left, "attribute1": "leading", "view2": self.w.leftSearchFor, "attribute2": "leading"},
				{"view1": self.w.text_left, "attribute1": "width", "view2": self.w.leftSearchFor, "attribute2": "width"},
				{"view1": self.w.text_right, "attribute1": "leading", "view2": self.w.rightSearchFor, "attribute2": "leading"},
				{"view1": self.w.text_right, "attribute1": "width", "view2": self.w.rightSearchFor, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "headGap": 4},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		self.LoadPreferences()

		self.w.open()
		self.w.makeKey()

	def replaceGroupName(self, groupName, searchString, replaceString):
		try:
			if groupName:
				if searchString == "":
					# simply append replaceString if no search string is supplied:
					return groupName + replaceString
				else:
					return groupName.replace(searchString, replaceString)
			else:
				return None
		except Exception as e:
			print(e)

	def replaceInGroups(self, thisGlyph, LsearchFor, LreplaceBy, RsearchFor, RreplaceBy):
		# thisGlyph.beginUndo()  # undo grouping causes crashes
		thisGlyphName = thisGlyph.name

		# Left Group:
		oldLeftGroup = thisGlyph.leftKerningGroup
		if not oldLeftGroup:
			print("%s: no left group set. Left unchanged." % thisGlyphName)
		else:
			newLeftGroup = self.replaceGroupName(oldLeftGroup, LsearchFor, LreplaceBy)
			if oldLeftGroup == newLeftGroup:
				print("%s: left group unchanged (%s)." % (thisGlyphName, newLeftGroup))
			else:
				thisGlyph.leftKerningGroup = newLeftGroup
				print("%s: new left group: '%s'." % (thisGlyphName, newLeftGroup))

		# Right Group:
		oldRightGroup = thisGlyph.rightKerningGroup
		if not oldRightGroup:
			print("%s: no right group set. Left unchanged." % thisGlyphName)
		else:
			newRightGroup = self.replaceGroupName(oldRightGroup, RsearchFor, RreplaceBy)
			if oldRightGroup == newRightGroup:
				print("%s: right group unchanged (%s)." % (thisGlyph.name, newRightGroup))
			else:
				thisGlyph.rightKerningGroup = newRightGroup
				print("%s: new right group: '%s'." % (thisGlyph.name, newRightGroup))

		# thisGlyph.endUndo()  # undo grouping causes crashes

	def KerningGroupReplaceMain(self, sender):
		Glyphs.clearLog()
		Font = Glyphs.font
		if Font is None:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			return

		Font.disableUpdateInterface()
		try:
			self.SavePreferences()

			selectedLayers = Font.selectedLayers
			currentLayers = [layer for layer in selectedLayers if layer.parent.name is not None]

			LsearchFor = self.pref("leftSearchFor")
			LreplaceBy = self.pref("leftReplaceBy")
			RsearchFor = self.pref("rightSearchFor")
			RreplaceBy = self.pref("rightReplaceBy")

			for thisLayer in currentLayers:
				thisGlyph = thisLayer.parent
				try:
					self.replaceInGroups(thisGlyph, LsearchFor, LreplaceBy, RsearchFor, RreplaceBy)
				except Exception as e:
					print("Error while processing glyph %s:" % thisGlyph.name)
					print(e)

			self.w.close()

		except Exception as e:
			raise e

		finally:
			Font.enableUpdateInterface()


KerningGroupReplacer()
