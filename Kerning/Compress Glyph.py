# MenuTitle: Compress Glyph
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Compresses all instances of a glyph to its respective group kerning.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


def match(first, second):
	# https://www.geeksforgeeks.org/wildcard-character-matching/
	if len(first) == 0 and len(second) == 0:
		return True
	if len(first) > 1 and first[0] == '*' and len(second) == 0:
		return False
	if (len(first) > 1 and first[0] == '?') or (len(first) != 0 and len(second) != 0 and first[0] == second[0]):
		return match(first[1:], second[1:])
	if len(first) != 0 and first[0] == '*':
		return match(first[1:], second) or match(first, second[1:])
	return False


class CompressGlyph(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"glyphName": "V",
		"compressLeft": 1,
		"compressRight": 1,
		"allMasters": 0,
		"verbose": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 335
		windowHeight = 160
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Compress Glyph",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "In frontmost font, compress kernings for this glyph:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.glyphName = vanilla.ComboBox((inset, linePos - 4, -inset - 25, 24), (), callback=self.SavePreferences)
		self.w.glyphName.getNSComboBox().setToolTip_("The name of the glyph you want to compress. Use * as wildcard for matching many glyphs.")
		self.w.updateButton = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", callback=self.update)
		linePos += lineHeight + 3

		self.w.compressText = vanilla.TextBox((inset, linePos + 2, 140, 14), "Compress when glyph is", sizeStyle="small", selectable=True)
		self.w.compressLeft = vanilla.CheckBox((inset + 140, linePos - 1, 65, 20), "left side", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.compressRight = vanilla.CheckBox((inset + 205, linePos - 1, -inset, 20), "right side of pair", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.allMasters = vanilla.CheckBox((inset, linePos - 1, 120, 20), "⚠️ ALL masters", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose = vanilla.CheckBox((inset + 120, linePos - 1, -inset, 20), "Verbose report in Macro window", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Compress", callback=self.CompressGlyphMain)
		self.w.setDefaultButton(self.w.runButton)

		self.w.status = vanilla.TextBox((inset, -14 - inset, -inset - 90, 14), "🤖 Ready.", sizeStyle="small", selectable=True)
		linePos += lineHeight

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.update()
		self.w.open()
		self.w.makeKey()

	def update(self, sender=None):
		names = list([g.name for g in Glyphs.font.glyphs])
		names.extend(sorted(set([f'*{g.name[g.name.find("."):]}' for g in Glyphs.font.glyphs if "." in g.name and not g.name.startswith(".")])))
		self.w.glyphName.setItems(names)

	def CompressGlyphMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			# read prefs:
			glyphName = self.pref("glyphName")
			compressLeft = self.pref("compressLeft")
			compressRight = self.pref("compressRight")
			allMasters = self.pref("allMasters")
			verbose = self.pref("verbose")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Compress Glyph Report for {reportName}")
				print()

				fontKerning = thisFont.kerning
				if not fontKerning:
					Message(
						title="No kerning in font",
						message=f"The current font ({thisFont.familyName}) appears to have no kerning at all.",
						OKButton="Oops",
					)
					return

				glyphNames = []
				if "*" in glyphName:
					for g in thisFont.glyphs:
						if match(glyphName, g.name):
							glyphNames.append(g.name)
				else:
					glyphNames.append(glyphName)

				if not glyphNames:
					Message(
						title="No glyphs matching ‘{glyphName}’",
						message=f"In the current font ({thisFont.familyName}), there is no glyph like ‘{glyphName}’.",
						OKButton="Oops",
					)
					return

				totalCount = 0
				for glyphName in glyphNames:
					glyph = thisFont.glyphs[glyphName]
					self.w.status.set(f"🗜️ Compressing {glyphName}...")
					print(f"🗜️ Compressing {glyphName}...")

					gID = glyph.id
					deletePairs = []
					addPairs = []
					for m in thisFont.masters:
						if not allMasters and thisFont.selectedFontMaster != m:
							continue
						print(f"Ⓜ️ Scanning {m.name}...")
						kerning = fontKerning[m.id]
						for leftKey in kerning.keys():
							for rightKey in kerning[leftKey].keys():
								if compressLeft and leftKey == gID and glyph.rightKerningGroup:
									deletePairs.append((m.id, leftKey, rightKey))
									rightSide = None
									if rightKey.startswith("@"):
										rightSide = rightKey
									else:
										rightGlyph = thisFont.glyphForId_(rightKey)
										if rightGlyph:
											rightSide = rightGlyph.name
									if rightSide:
										value = kerning[leftKey][rightKey]
										addPairs.append((m.id, f"@MMK_L_{glyph.rightKerningGroup}", rightSide, value))

								if compressRight and rightKey == gID and glyph.leftKerningGroup:
									deletePairs.append((m.id, leftKey, rightKey))
									leftSide = None
									if leftKey.startswith("@"):
										leftSide = leftKey
									else:
										leftGlyph = thisFont.glyphForId_(leftKey)
										if leftGlyph:
											leftSide = leftGlyph.name
									if leftSide:
										value = kerning[leftKey][rightKey]
										addPairs.append((m.id, leftSide, f"@MMK_R_{glyph.leftKerningGroup}", value))

					for addPair in addPairs:
						try:
							masterID, left, right, value = addPair
							mName = thisFont.masters[masterID].name
							thisFont.setKerningForPair(masterID, left, right, value)
							if verbose:
								print(f"Ⓜ️ {mName} 👈 {left} 👉 {right}: {value}")
						except Exception as e:  # noqa: F841
							print(f"⚠️ could not add pair: {left} - {right} ({value}, MID: {masterID})")
							# raise e

					for deletePair in deletePairs:
						try:
							masterID, leftKey, rightKey = deletePair
							thisFont.removeKerningForPair(
								masterID,
								leftKey if leftKey.startswith("@") else thisFont.glyphForId_(leftKey).name,
								rightKey if rightKey.startswith("@") else thisFont.glyphForId_(rightKey).name,
							)
						except Exception as e:  # noqa: F841
							print(f"⚠️ could not delete pair: {leftKey} - {rightKey}, MID: {masterID}")
							# raise e

					compressCount = len(deletePairs)
					totalCount += compressCount
					self.w.status.set(f"✅ {compressCount} kerns: {glyphName}")
					print(f"✅ Compressed {compressCount} kern pairs with {glyphName} (L: {glyph.leftKerningGroup}, R: {glyph.rightKerningGroup}).\n")

				if len(glyphNames) > 1:
					self.w.status.set(f"✅ {totalCount} kerns for {len(glyphNames)} glyphs")
					print(f"Compressed {len(glyphNames)} glyphs: {', '.join(glyphNames)}.\n")

			print("Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Compress Glyph Error: {e}")
			import traceback
			print(traceback.format_exc())


CompressGlyph()
