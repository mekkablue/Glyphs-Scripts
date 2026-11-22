# MenuTitle: Compare Glyph Info
__doc__ = """
Compares open fonts and builds a lits of differing glyph info, including Unicode values and categorisation.
"""

import vanilla
from mekkablue import mekkaObject, UpdateButton, makeWindowResizable
from GlyphsApp import Glyphs
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut

# CONSTANTS:

thingsToCompare = (
	"Unicodes",
	"Category",
	"Subcategory",
	"Production Name",
	"Script",
	"Export Status",
	"Left Kerning Group",
	"Right Kerning Group",
	"Color",
	"Left Metrics Key",
	"Right Metrics Key",
	"Width Metrics Key",
	"Is Aligned",
	"Has Aligned Width",
	"Has Annotations",
	"Has Components",
	"Has Corners",
	"Has Custom Glyph Info",
	"Has Hints",
	"Has PostScript Hints",
	"Has TrueType Hints",
	"Has Special Layers",
	"Is Color Glyph",
	"Is Apple Color Glyph",
	"Is SVG Color Glyph",
	"Is Hangul Key Glyph",
	"Masters Are Compatible",
	"Glyph Note",
)

predefinedColors = (
	"red",
	"orange",
	"brown",
	"yellow",
	"lightgreen",
	"green",
	"lightblue",
	"blue",
	"purple",
	"pink",
	"lightgrey",
	"grey",
)

missingGlyphValue = "(missing glyph)"
missingValue = "–"


class CompareGlyphInfo(mekkaObject):
	metrics = {"inset": 8, "gap": 8}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 500
		windowHeight = 160
		# resizable, so the user can enlarge the list:
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Compare Glyph Info",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		self.w.descriptionText = vanilla.TextBox("auto", "Compare between fonts:", sizeStyle='small', selectable=True)

		self.w.whatToCompare = vanilla.PopUpButton("auto", thingsToCompare, sizeStyle='small', callback=self.Reload)
		self.w.whatToCompare.setToolTip("Choose which glyph info to compare between all open fonts.")

		self.w.ignoreMissingGlyphs = vanilla.CheckBox("auto", "Ignore missing glyphs", value=False, callback=self.Reload, sizeStyle='small')
		self.w.ignoreMissingGlyphs.setToolTip("If activated, will only list glyphs that are present in ALL open fonts.")

		self.w.updateButton = UpdateButton("auto", callback=self.Reload)
		self.w.updateButton.setToolTip("Reload with currently opened fonts. Useful if you just opened or closed a font, or brought another font forward.")

		# the controls above the list hug their content vertically, the list takes the leftover height:
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)
		# label and checkbox hug their text, so the popup takes the leftover width:
		self.w.descriptionText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.ignoreMissingGlyphs.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-gap-[whatToCompare(>=110)]-gap-[ignoreMissingGlyphs]-gap-[updateButton]-inset-|",
				"V:|-inset-[whatToCompare]",
				{"view1": self.w.descriptionText, "attribute1": "centerY", "view2": self.w.whatToCompare, "attribute2": "centerY"},
				{"view1": self.w.ignoreMissingGlyphs, "attribute1": "centerY", "view2": self.w.whatToCompare, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.whatToCompare, "attribute2": "centerY"},
			],
			metrics=self.metrics,
		)

		self.Reload()

		makeWindowResizable(self.w, vertical=True)  # resizable, limits in content sizes

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def getColumnHeaders(self, sender=None):
		# {"title":xxx, "key":xxx, "editable":False, "width":xxx} for every font
		headers = [
			{
				"title": "Glyph Name",
				"key": "glyphName",
				"editable": False,
				"width": 200,
				"maxWidth": 400
			},
		]
		for i, thisFont in enumerate(Glyphs.fonts):
			if thisFont.filepath:
				fileName = thisFont.filepath.lastPathComponent()
			else:
				fileName = "%s (unsaved)" % thisFont.familyName

			columnHeader = {
				"title": fileName,
				"key": "font-%i" % i,
				"editable": False,
				"width": 150,
				"maxWidth": 300
			}
			headers.append(columnHeader)

		return headers

	def returnValue(self, value):
		if value:
			return value
		else:
			return missingValue

	def returnBool(self, value):
		if value:
			return "✅"
		return "🚫"

	def getInfoItemForGlyph(self, glyph):
		if glyph is None:
			return missingGlyphValue

		index = self.w.whatToCompare.get()
		if index == 0:
			if not glyph.unicodes:
				return missingValue
			else:
				return ", ".join(glyph.unicodes)
		elif index == 1:
			return self.returnValue(glyph.category)
		elif index == 2:
			return self.returnValue(glyph.subCategory)
		elif index == 3:
			return self.returnValue(glyph.productionName)
		elif index == 4:
			return self.returnValue(glyph.script)
		elif index == 5:
			return self.returnBool(glyph.export)
		elif index == 6:
			return self.returnValue(glyph.leftKerningGroup)
		elif index == 7:
			return self.returnValue(glyph.rightKerningGroup)
		elif index == 8:
			if glyph.color is None:
				return missingValue
			else:
				return predefinedColors[glyph.color]
		elif index == 9:
			return self.returnValue(glyph.leftMetricsKey)
		elif index == 10:
			return self.returnValue(glyph.rightMetricsKey)
		elif index == 11:
			return self.returnValue(glyph.widthMetricsKey)
		elif index == 12:
			return self.returnBool(glyph.isAligned())
		elif index == 13:
			return self.returnBool(glyph.hasAlignedWidth())
		elif index == 14:
			return self.returnBool(glyph.hasAnnotations())
		elif index == 15:
			return self.returnBool(glyph.hasComponents())
		elif index == 16:
			return self.returnBool(glyph.hasCorners())
		elif index == 17:
			return self.returnBool(glyph.hasCustomGlyphInfo())
		elif index == 18:
			return self.returnBool(glyph.hasHints())
		elif index == 19:
			return self.returnBool(glyph.hasPostScriptHints())
		elif index == 20:
			return self.returnBool(glyph.hasTrueTypeHints())
		elif index == 21:
			return self.returnBool(glyph.hasSpecialLayers())
		elif index == 22:
			return self.returnBool(glyph.isColorGlyph())
		elif index == 23:
			return self.returnBool(glyph.isAppleColorGlyph())
		elif index == 24:
			return self.returnBool(glyph.isSVGColorGlyph())
		elif index == 25:
			return self.returnBool(glyph.isHangulKeyGlyph())
		elif index == 26:
			return self.returnBool(glyph.mastersCompatible)
		elif index == 27:
			return self.returnValue(glyph.note)

		return "⚠️ Error"

	def listContent(self):
		try:
			ignoreMissingGlyphs = self.w.ignoreMissingGlyphs.get()

			allNames = []
			for thisFont in Glyphs.fonts:
				allNames.extend([g.name for g in thisFont.glyphs])
			allNames = sorted(set(allNames))

			displayedLines = []
			for glyphName in allNames:
				line = {
					"glyphName": glyphName
				}
				checkList = []
				for i, thisFont in enumerate(Glyphs.fonts):
					column = "font-%i" % i
					glyph = thisFont.glyphs[glyphName]
					cell = self.getInfoItemForGlyph(glyph)
					line[column] = cell
					checkList.append(cell)

				# check if line contains differences:
				countOfDistinctItems = len(set(checkList))
				if checkList and countOfDistinctItems > 1:
					if ignoreMissingGlyphs and countOfDistinctItems == 2:
						if not all([item != missingGlyphValue for item in checkList]):
							continue
					displayedLines.append(line)

			return displayedLines
		except Exception as e:
			print("listContent Error: %s\n" % e)
			import traceback
			print(traceback.format_exc())
			return None

	def Reload(self, sender=None):
		try:
			try:
				del self.w.List
			except:
				pass

			self.w.List = vanilla.List(
				"auto",
				self.listContent(),
				columnDescriptions=self.getColumnHeaders(),
				drawVerticalLines=True,
				enableDelete=True,
				drawFocusRing=True,
				# selectionCallback = self.selectedAction,
				doubleClickCallback=self.openGlyphInFont,
				# editCallback = self.editAction,
			)

			self.w.List.getNSTableView().setToolTip_("Double click to open the selected glyphs in all fonts. You can select more than one line.")

			# the list is rebuilt with every reload (its columns depend on the open fonts), so it gets its rules here:
			self.w.List.getNSScrollView().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationVertical)
			self.w.addAutoPosSizeRules(
				[
					"H:|[List]|",
					"V:[whatToCompare]-gap-[List(>=80)]|",
				],
				metrics=self.metrics,
			)
		except Exception as e:
			print("Reload Error: %s\n" % e)
			import traceback
			print(traceback.format_exc())
			return None

	def openGlyphInFont(self, sender=None):
		if sender:
			selectedIndexes = sender.getSelection()
			if selectedIndexes:
				tabText = ""
				for index in selectedIndexes:
					item = self.w.List.get()[index]
					tabText += "/%s" % item["glyphName"]

				if tabText:
					for i, thisFont in enumerate(Glyphs.fonts):
						tab = thisFont.currentTab
						if not tab:
							tab = thisFont.newTab()
						tab.text = tabText
						tab.textCursor = 0
						tab.scale = 0.15
						if i > 0:
							tab.viewPort = Glyphs.fonts[0].currentTab.viewPort


CompareGlyphInfo()
