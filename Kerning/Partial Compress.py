# MenuTitle: Partial Compress
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Compress kerning, but for certain glyphs only.
"""

import vanilla
from GlyphsApp import Glyphs, Message


class PartialCompress(object):
	prefID = "com.mekkablue.PartialCompress"
	prefDict = {
		# "prefName": defaultValue,
		"searchFor": "",
		"allMasters": 1,
		"allFonts": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 280
		windowHeight = 130
		windowWidthResize = 200  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Partial Compress",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Compress kern pairs with glyphs containing:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.searchFor = vanilla.EditText((inset, linePos, -inset, 19), ".dnom", callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.allMasters = vanilla.CheckBox((inset, linePos - 1, 125, 20), "⚠️ on ALL masters", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allFonts = vanilla.CheckBox((inset + 125, linePos - 1, -inset, 20), "⚠️ in ALL fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Compress", sizeStyle="regular", callback=self.PartialCompressMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Partial Compress’ could not load preferences. Will resort to defaults.")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()

	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]

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

	def PartialCompressMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Partial Compress’ could not write preferences.")

			# read prefs:
			searchFor = self.pref("searchFor")
			searchStrings = [x.strip() for x in searchFor.strip().split(",")]
			allMasters = self.pref("allMasters")
			allFonts = self.pref("allFonts")

			print(searchStrings)

			if Glyphs.font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			if allFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )

			for thisFont in theseFonts:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Partial Compress Report for {reportName}")

				removeList = []

				for m in thisFont.masters:
					if not allFonts and (not allMasters and m != thisFont.selectedFontMaster):
						continue

					print(f"  Ⓜ️ {m.name}")
					for lID in thisFont.kerning[m.id].keys():
						if lID.startswith("@"):
							L = lID
							lName = lID
							lGroup = lID
						else:
							L = thisFont.glyphForId_(lID)
							lName = L.name
							lGroup = f"@MMK_L_{L.rightKerningGroup}"

						if not lGroup:
							continue

						for rID in thisFont.kerning[m.id][lID].keys():
							rID = str(rID)
							if rID.startswith("@"):
								R = rID
								rName = rID
								rGroup = rID
							else:
								R = thisFont.glyphForId_(rID)
								rName = R.name
								rGroup = f"@MMK_R_{R.leftKerningGroup}"

							if not rGroup:
								continue

							bothAreGroups = lName[0] == rName[0] == "@"
							if bothAreGroups:
								continue

							for searchString in searchStrings:
								if searchString not in lName and searchString not in rName:
									continue

								value = thisFont.kerning[m.id][lID][rID]
								removeList.append((m.id, lName, rName))
								thisFont.setKerningForPair(m.id, lGroup, rGroup, value)

				print(f"Compressing {len(removeList)} pairs...")
				for removeCandidate in removeList:
					mID, lID, rID = removeCandidate
					thisFont.removeKerningForPair(mID, lID, rID)

				print()

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Partial Compress Error: {e}")
			import traceback
			print(traceback.format_exc())


PartialCompress()
