# MenuTitle: Font Info Overview
__doc__ = """
Lists some Font Info values for all opened fonts.
"""

import vanilla
from mekkablue import mekkaObject, makeWindowResizable
from GlyphsApp import Glyphs
from AppKit import NSColor, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultLow

keyList = [
	["Family Name", "familyName", 160], ["Major", "versionMajor", 40], ["Minor", "versionMinor", 40], ["Grid", "grid", 40], ["Designer", "designer", 200],
	["Designer URL", "designerURL", 200], ["Manufacturer", "manufacturer", 200], ["Manufacturer URL", "manufacturerURL", 200], ["Copyright", "copyright", 200]
	# ["UPM", "upm"],
	# ["Date", "date", 100]
	# ["Note", "note"]
	# ["Ugly Names", "disablesNiceNames"]
]

keyColumnDescriptions = [{
	"title": kl[0],
	"key": kl[1]
} for kl in keyList]


class FontInfoOverview(mekkaObject):
	changeCount = 0

	def __init__(self):
		# Window 'self.w':
		windowWidth = 600
		windowHeight = 200
		# the list is the main content, so the window stays resizable:
		self.w = vanilla.Window(
			(windowWidth, windowHeight),  # default window size
			"Font Info Overview",  # window title
			autosaveName=self.domain("mainwindow"),  # stores last window position and size
		)

		# List:
		self.w.List = vanilla.List(
			"auto",
			self.listContent(),
			columnDescriptions=[{
				"title": kl[0],
				"key": kl[1],
				"editable": True,
				"width": kl[2]
			} for kl in keyList],
			drawVerticalLines=True,
			enableDelete=True,
			drawFocusRing=True,
			# selectionCallback = self.selectedAction,
			# doubleClickCallback = self.doubleclickedAction,
			editCallback=self.editAction
		)
		self.w.List.getNSTableView().setToolTip_("Font Info values of all open fonts. Double-click a cell to edit it, then click Apply Changes.")

		# Buttons:
		self.w.reloadButton = vanilla.Button("auto", "Reload", callback=self.Reload)
		self.w.applyButton = vanilla.Button("auto", "Apply Changes", callback=self.Apply)
		self.w.reloadButton.setToolTip("Reloads the Font Info values of all open fonts and discards edits that were not applied yet.")
		self.w.applyButton.setToolTip("Writes the edited values back to their fonts, for the selected rows, or for all rows if none is selected.")
		# self.w.setDefaultButton(self.w.reloadButton)

		# Counter:
		self.w.changeCounter = vanilla.TextBox("auto", "Changes: -", sizeStyle='small')

		# Status line:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready. 💬 See tooltips for help.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")
		nsStatus = self.w.status.getNSTextField()
		nsStatus.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		nsStatus.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# the list takes all the height the user gives the window:
		self.w.List.getNSScrollView().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|[List]|",
				"H:|-inset-[changeCounter]-(>=gap)-[reloadButton(>=70)]-gap-[applyButton(>=70)]-inset-|",
				"H:|-inset-[status]-inset-|",
				"V:|[List(>=100)]-inset-[status]-gap-[applyButton]-inset-|",
				{"view1": self.w.reloadButton, "attribute1": "centerY", "view2": self.w.applyButton, "attribute2": "centerY"},
				{"view1": self.w.changeCounter, "attribute1": "centerY", "view2": self.w.applyButton, "attribute2": "centerY"},
			],
			metrics={"inset": 15, "gap": 8},
		)

		self.updateCounter()

		makeWindowResizable(self.w, vertical=True)  # resizable, limits in content sizes

		# open the window
		self.w.open()
		self.w.makeKey()

	def selectedAction(self, sender):
		print("\nSELECTION:")
		selectedIndexes = sender.getSelection()
		print(selectedIndexes)
		for i in selectedIndexes:
			print(sender[i]["fontObj"])

	def doubleclickedAction(self, sender):
		print("\nDOUBLE CLICK:")
		selectedIndexes = sender.getSelection()
		for i in selectedIndexes:
			print(sender[i]["fontObj"].familyName)

	def editAction(self, sender):
		try:
			self.updateCounter()
		except Exception as e:
			print("editAction Error: %s" % e)

	def listContent(self):
		try:
			listDictOfOpenFonts = [dict([[kl[1], getattr(f, kl[1])] for kl in keyList] + [["fontObj", f]]) for f in Glyphs.fonts]
			return listDictOfOpenFonts
		except Exception as e:
			print("listContent Error: %s" % e)
			return []

	def valueForFont(self, currentFontValue, listValue):
		# an edited list cell holds a string, an empty one for a deleted entry,
		# while the font has a number, or None for an unset entry:
		if isinstance(currentFontValue, (int, float)) and not isinstance(listValue, (int, float)):
			try:
				return type(currentFontValue)(listValue)
			except (TypeError, ValueError):
				return currentFontValue  # not a number, keep the value of the font
		if currentFontValue is None and listValue == "":
			return None
		return listValue

	def updateCounter(self):
		try:
			changeCounter = 0
			listOfFontInfos = self.w.List.get()
			for thisFontInfo in listOfFontInfos:
				thisFont = thisFontInfo["fontObj"]
				for thisKey in thisFontInfo.keys():
					if thisKey != "fontObj":
						currentFontValue = getattr(thisFont, thisKey)
						listValue = self.valueForFont(currentFontValue, thisFontInfo[thisKey])
						if currentFontValue != listValue:
							changeCounter += 1
			self.w.changeCounter.set("Unsaved changes: %i" % changeCounter)
		except Exception as e:
			print("updateCounter Error: %s" % e)

	def Reload(self, sender):
		try:
			self.setStatus("🛠️ Reloading…")
			self.w.List.set(self.listContent())
			self.updateCounter()
			fontCount = len(self.w.List.get())
			self.setStatus(f"✅ Listed {fontCount} font{'' if fontCount == 1 else 's'}.")
		except Exception as e:
			Glyphs.showMacroWindow()
			print("Reload Error: %s" % e)
			self.setStatus("❌ Error while reloading. Details in Macro Window.")

	def Apply(self, sender):
		thisFont = None
		try:
			self.setStatus("🛠️ Applying changes…")
			changedValues = 0
			changedFonts = 0
			listOfFontInfos = self.w.List.get()
			selectedIndexes = self.w.List.getSelection()
			nothingIsSelected = False

			if len(selectedIndexes) == 0:
				nothingIsSelected = True

			for fontInfoIndex in range(len(listOfFontInfos)):
				if fontInfoIndex in selectedIndexes or nothingIsSelected:
					thisFontInfo = listOfFontInfos[fontInfoIndex]
					thisFont = thisFontInfo["fontObj"]
					self.setStatus(f"🔠 {thisFont.familyName}")
					fontChanged = False
					for thisKey in thisFontInfo.keys():
						if thisKey != "fontObj":
							currentFontValue = getattr(thisFont, thisKey)
							listValue = self.valueForFont(currentFontValue, thisFontInfo[thisKey])
							if currentFontValue != listValue:
								changedValues += 1
								fontChanged = True
								print("Setting %s to '%s' in %s." % (thisKey, listValue, thisFont))
								setattr(thisFont, thisKey, listValue)
					if fontChanged:
						changedFonts += 1
			self.updateCounter()
			if changedValues:
				self.setStatus(f"✅ Changed {changedValues} value{'' if changedValues == 1 else 's'} in {changedFonts} font{'' if changedFonts == 1 else 's'}.")
			else:
				self.setStatus("⚠️ Nothing to change.")
		except Exception as e:
			print("Apply Error: %s" % e)
			self.setStatus(f"❌ Error at {thisFont.familyName if thisFont else 'start'}. Details in Macro Window.")


FontInfoOverview()
