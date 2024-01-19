# MenuTitle: New Tab with Overkerned Pairs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Asks a threshold percentage, and opens a new tab with all kern pairs going beyond the width threshold. Option to fix them too.
"""

import vanilla
from GlyphsApp import Glyphs, GSControlLayer, Message
from mekkablue import mekkaObject


def roundedDownBy(value, base):
	return base * round(value // base)


class NewTabwithOverkernedPairs(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"threshold": 40,
		"limitToExportingGlyphs": 1,
		"rounding": 5,
		"scope": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 290
		windowHeight = 180
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Negative Overkerns in this Master",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.thresholdText = vanilla.TextBox((inset, linePos + 2, 210, 14), "Open tab with kerns beyond threshold:", sizeStyle='small', selectable=True)
		self.w.threshold = vanilla.EditText((inset + 210, linePos - 1, -inset - 15, 19), "40", callback=self.SavePreferences, sizeStyle='small')
		self.w.thresholdPercent = vanilla.TextBox((-inset - 15, linePos + 2, -inset, 14), "%", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.descriptionText2 = vanilla.TextBox((inset, linePos + 2, -inset, 14), "(Max percentage of widths that may be kerned.)", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.roundingText = vanilla.TextBox((inset, linePos + 2, 210, 14), "When fixing, round kerning values by:", sizeStyle='small', selectable=True)
		self.w.rounding = vanilla.EditText((inset + 210, linePos - 1, -inset, 19), "5", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.limitToExportingGlyphs = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Limit to exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.scopeText = vanilla.TextBox((inset, linePos + 2, 50, 14), "Apply to", sizeStyle="small", selectable=True)
		self.w.scope = vanilla.PopUpButton((inset + 50, linePos, -inset, 17), ("current master of current font", "⚠️ ALL masters of current font", "⚠️ ALL masters of ⚠️ ALL open fonts"), sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight

		# Run Button:
		self.w.fixButton = vanilla.Button((-180 - inset, -20 - inset, -110 - inset, -inset), "Fix", sizeStyle='regular', callback=self.NewTabwithOverkernedPairsMain)
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Report", sizeStyle='regular', callback=self.NewTabwithOverkernedPairsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def NewTabwithOverkernedPairsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			shouldFix = sender == self.w.fixButton

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			if self.pref("scope") < 2:
				theseFonts = (thisFont, )
			else:
				theseFonts = Glyphs.fonts

			thresholdFactor = None
			try:
				thresholdFactor = self.prefFloat("threshold") / 100.0
			except:
				Message(title="Value Error", message="The threshold value you entered is invalid", OKButton="Oops")
				return

			overKernCount = 0
			for thisFont in theseFonts:
				filePath = thisFont.filepath
				if filePath:
					report = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					report = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Overkerned Pairs report for {report}")

				rounding = self.prefInt("rounding")

				if self.pref("scope") > 0:
					theseMasters = thisFont.masters
				else:
					theseMasters = (thisFont.selectedFontMaster, )

				layers = []
				for thisMaster in theseMasters:
					print(f"\n\tⓂ️ Master ‘{thisMaster.name}’")
					masterKerning = thisFont.kerning[thisMaster.id]  # kerning dictionary
					# tabText = ""  # the text appearing in the new tab

					# collect minimum widths for every kerning group:
					leftGroupMinimumWidths = {}
					leftGroupNarrowestGlyphs = {}
					rightGroupMinimumWidths = {}
					rightGroupNarrowestGlyphs = {}
					if self.pref("limitToExportingGlyphs"):
						theseGlyphs = [g for g in thisFont.glyphs if g.export]
					else:
						theseGlyphs = thisFont.glyphs
					for thisGlyph in theseGlyphs:
						thisLayer = thisGlyph.layers[thisMaster.id]

						# left side of the glyph (= right side of kern pair)
						if thisGlyph.leftKerningGroup:
							if thisGlyph.leftKerningGroup in leftGroupMinimumWidths.keys():
								if thisLayer.width < leftGroupMinimumWidths[thisGlyph.leftKerningGroup]:
									leftGroupMinimumWidths[thisGlyph.leftKerningGroup] = thisLayer.width
									leftGroupNarrowestGlyphs[thisGlyph.leftKerningGroup] = thisGlyph.name
							else:
								leftGroupMinimumWidths[thisGlyph.leftKerningGroup] = thisLayer.width
								leftGroupNarrowestGlyphs[thisGlyph.leftKerningGroup] = thisGlyph.name

						# right side of the glyph (= left side of kern pair)
						if thisGlyph.rightKerningGroup:
							if thisGlyph.rightKerningGroup in rightGroupMinimumWidths.keys():
								if thisLayer.width < rightGroupMinimumWidths[thisGlyph.rightKerningGroup]:
									rightGroupMinimumWidths[thisGlyph.rightKerningGroup] = thisLayer.width
									rightGroupNarrowestGlyphs[thisGlyph.rightKerningGroup] = thisGlyph.name
							else:
								rightGroupMinimumWidths[thisGlyph.rightKerningGroup] = thisLayer.width
								rightGroupNarrowestGlyphs[thisGlyph.rightKerningGroup] = thisGlyph.name

					# go through kern values and collect them in tabText:
					for leftKey in masterKerning.keys():
						for rightKey in masterKerning[leftKey].keys():
							kernValue = masterKerning[leftKey][rightKey]
							if kernValue < 0:
								leftWidth = None
								rightWidth = None

								try:
									# collect widths for comparison
									if leftKey[0] == "@":
										# leftKey is a group name like "@MMK_L_y"
										groupName = leftKey[7:]
										leftWidth = rightGroupMinimumWidths[groupName]
										leftGlyphName = rightGroupNarrowestGlyphs[groupName]
									else:
										# leftKey is a glyph ID like "59B740DA-A4F4-43DF-B6DD-1DFA213FFFE7"
										leftGlyph = thisFont.glyphForId_(leftKey)
										# exclude if non-exporting and user limited to exporting glyphs:
										if self.pref("limitToExportingGlyphs") and not leftGlyph.export:
											kernValue = 0.0
										leftWidth = leftGlyph.layers[thisMaster.id].width
										leftGlyphName = leftGlyph.name

									if rightKey[0] == "@":
										# rightKey is a group name like "@MMK_R_y"
										groupName = rightKey[7:]
										rightWidth = leftGroupMinimumWidths[groupName]
										rightGlyphName = leftGroupNarrowestGlyphs[groupName]
									else:
										# rightKey is a glyph ID like "59B740DA-A4F4-43DF-B6DD-1DFA213FFFE7"
										rightGlyph = thisFont.glyphForId_(rightKey)
										# exclude if non-exporting and user limited to exporting glyphs:
										if self.pref("limitToExportingGlyphs") and not rightGlyph.export:
											kernValue = 0.0
										rightWidth = rightGlyph.layers[thisMaster.id].width
										rightGlyphName = rightGlyph.name

									# compare widths and collect overkern if it is one:
									# (kernValue of excluded glyphs will be 0.0 and not trigger the if clause)
									maxPossibleKernValue = min(thresholdFactor * leftWidth, thresholdFactor * rightWidth)
									if abs(kernValue) > maxPossibleKernValue:
										overKernCount += 1
										layers.append(thisFont.glyphs[leftGlyphName].layers[thisMaster.id])
										layers.append(thisFont.glyphs[rightGlyphName].layers[thisMaster.id])
										print(f"\tOverkern: {leftGlyphName} ↔️ {rightGlyphName} ({kernValue:.0f} vs. max {maxPossibleKernValue:.1f})")
										if thisFont.glyphs["space"]:
											layers.append(thisFont.glyphs["space"].layers[thisMaster.id])
										if shouldFix:
											masterKerning[leftKey][rightKey] = -roundedDownBy(maxPossibleKernValue, rounding)

								except Exception as e:
									# probably a kerning group name found in the kerning data, but no glyph assigned to it:
									# brings macro window to front and reports warning:
									print(e)
									import traceback
									errormsg = traceback.format_exc()
									for side in ("left", "right"):
										if side not in errormsg.lower():
											print(
												f"⚠️ Warning: The {side} group ‘{groupName}’ found in your kerning data does not appear in any glyph. Clean up your kerning, and run the script again."
											)
											Glyphs.showMacroWindow()

					if layers:
						layers.append(GSControlLayer.newline())
				if layers:
					tab = thisFont.newTab()
					tab.layers = layers

				print()

			message = ""
			if overKernCount > 0:
				message = "%s %i overkerns in %i font%s." % (
					"Fixed" if shouldFix else "Found",
					overKernCount,
					len(theseFonts),
					"" if len(theseFonts) == 1 else "s",
				)
				Message(
					title="Found Overkerns",
					message=message,
					OKButton=None,
				)
			else:
				message = "Could not find any kern pairs beyond the threshold."
				Message(
					title="No Overkerns Found",
					message=message,
					OKButton="🫶Phew!",
				)

			print(f"✅ Done. {message}")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"New Tab with Overkerned Pairs Error: {e}")
			import traceback
			print(traceback.format_exc())


NewTabwithOverkernedPairs()
