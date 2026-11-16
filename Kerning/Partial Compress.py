# MenuTitle: Partial Compress
__doc__ = """
Compress kerning, but for certain glyphs only.
"""

import vanilla
from mekkablue import mekkaObject, reportFontName
from GlyphsApp import Glyphs, Message
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut


class PartialCompress(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"searchFor": "",
		"allMasters": 1,
		"allFonts": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 280
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Partial Compress",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Compress kern pairs with glyphs containing:", sizeStyle="small", selectable=True)

		self.w.searchFor = vanilla.EditText("auto", ".dnom", callback=self.SavePreferences, sizeStyle="small")

		self.w.allMasters = vanilla.CheckBox("auto", "⚠️ on ALL masters", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allFonts = vanilla.CheckBox("auto", "⚠️ in ALL fonts", value=False, callback=self.SavePreferences, sizeStyle="small")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Compress", callback=self.PartialCompressMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[searchFor]-inset-|",
				"H:|-inset-[allMasters]-inset-[allFonts]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[searchFor]-gap-[allMasters]-inset-[runButton]-inset-|",
				{"view1": self.w.allFonts, "attribute1": "centerY", "view2": self.w.allMasters, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def PartialCompressMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

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
				reportName = reportFontName(thisFont)
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
							if L is None:
								continue  # stale glyph ID
							lName = L.name
							# a glyph without a group cannot be compressed:
							lGroup = f"@MMK_L_{L.rightKerningGroup}" if L.rightKerningGroup else None

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
								if R is None:
									continue  # stale glyph ID
								rName = R.name
								# a glyph without a group cannot be compressed:
								rGroup = f"@MMK_R_{R.leftKerningGroup}" if R.leftKerningGroup else None

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
								break  # one match is enough, do not list the pair twice

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
