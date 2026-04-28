# MenuTitle: Copy Kerning from Caps to Smallcaps
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Looks for cap kerning pairs and reduplicates their kerning for corresponding .sc glyphs, if they are available in the font. Please be careful: Will overwrite existing SC kerning pairs.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject

if Glyphs.versionNumber >= 3:
	from GlyphsApp import GSUppercase, GSSmallcaps

smallcapSuffixes = (
	".sc",
	".c2sc",
	".smcp",
	".small",
)

namingSchemeOptions = (
	"Lowercase names (a.sc)",
	"Uppercase names (A.sc)",
)


def glyphNameIsSCconvertible(glyphName, font, includeNonLetters=False, suffix=".sc", figureSuffix=".lf"):
	"""Tests if the glyph referenced by the supplied glyphname is an uppercase glyph or should otherwise be included in the kerning."""
	try:
		glyph = font.glyphs[glyphName]
		if glyph:
			if isUppercase(glyph):
				return True
			elif isCapFigure(glyph, suffix=figureSuffix):
				if figureSuffix:
					scFigureName = glyphName.replace(figureSuffix, suffix)
				else:
					scFigureName = glyphName + suffix
				if font.glyphs[scFigureName]:
					return True
			elif includeNonLetters:
				if glyphHasSCcounterpart(glyph, font=font, suffix=suffix):
					return True
		return False
	except Exception as e:
		print("\n❌ Cannot determine case for: %s" % glyphName)
		print("Error: %s" % e)
		return False


def smallcapName(glyphName="scGlyph", suffix=".sc", lowercase=True, includeNonLetters=False, figureSuffix=".lf"):
	"""Returns the appropriate smallcap name, e.g. A-->a.sc or a-->a.sc"""
	try:
		returnName = glyphName

		# make lowercase if requested:
		particles = returnName.split(".")
		if lowercase:
			particles[0] = particles[0].lower()

		if len(particles) > 1:
			if includeNonLetters and figureSuffix:
				undottedFigureSuffix = figureSuffix
				if undottedFigureSuffix[0] == ".":
					undottedFigureSuffix = undottedFigureSuffix[1:]
				if undottedFigureSuffix in particles:
					particles.remove(undottedFigureSuffix)

		returnName = ".".join(particles) + suffix
		return returnName
	except Exception as e:
		print("Cannot compute smallcap name for: %s" % glyphName)
		print("Error: %s" % e)
		return None


def isCapFigure(glyph, suffix=".lf"):
	if glyph.category == "Number":
		if glyph.name.endswith(suffix):
			return True
	return False


def isUppercase(glyph):
	if Glyphs.versionNumber >= 3:
		if glyph.case == GSUppercase:
			return True
	else:
		if glyph.subCategory == "Uppercase":
			return True
	return False


def glyphHasSCcounterpart(glyph, font, suffix=".sc"):
	name = glyph.name
	if suffix not in name:
		if font.glyphs[name + suffix]:
			return True
		nameParts = name.split(".")
		if len(nameParts) > 1:
			nameParts.insert(1, suffix.replace(".", ""))
			if font.glyphs[".".join(nameParts)]:
				return True
	return False


def isSmallcap(glyph):
	if Glyphs.versionNumber >= 3:
		if glyph.case == GSSmallcaps:
			return True
	else:
		if glyph.subCategory == "Smallcaps":
			return True
	return False


class CopyKerningFromCapsToSmallcaps(mekkaObject):
	prefDict = {
		"smallcapSuffix": ".sc",
		"namingScheme": 0,
		"includeNonLetters": 1,
		"figureSuffix": ".lf",
		"includeAllMasters": 0,
		"factor": 0.8,
		"roundBy": 5,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 360
		windowHeight = 208
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Copy Kerning from Caps to Smallcaps",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		tab = 105
		self.w.smallcapSuffixText = vanilla.TextBox((inset, linePos + 2, 110, 14), "Smallcap suffix", sizeStyle='small')
		self.w.smallcapSuffix = vanilla.ComboBox((inset + tab, linePos - 1, -inset, 19), smallcapSuffixes, sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.namingSchemeText = vanilla.TextBox((inset, linePos + 2, 110, 14), "SC naming scheme", sizeStyle='small')
		self.w.namingScheme = vanilla.PopUpButton((inset + tab, linePos, -inset, 17), namingSchemeOptions, sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.includeAllMasters = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "⚠️ Include all masters (otherwise current master only)", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# self.w.copyCapCapToCapSC = vanilla.CheckBox((inset + 2, linePos-1, -inset, 20), "Add cap-to-cap → cap-to-smallcap", value=True, callback=self.SavePreferences, sizeStyle='small')
		# linePos += lineHeight

		self.w.includeNonLetters = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Include smallcap non-letters (otherwise only from caps)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonLetters.setToolTip("Includes smallcap figures, punctuation, etc. E.g. copies kerning for parenright if there is  parenright.sc.")
		linePos += lineHeight

		self.w.figureSuffixText = vanilla.TextBox((inset, linePos + 2, 90, 14), "Figure suffix", sizeStyle='small')
		self.w.figureSuffix = vanilla.EditText((inset + tab, linePos, -inset, 19), ".lf", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.factorText = vanilla.TextBox((inset, linePos + 2, 90, 14), "Kerning factor", sizeStyle='small')
		self.w.factor = vanilla.EditText((inset + tab, linePos, -inset, 19), "1.0", callback=self.SavePreferences, sizeStyle='small')
		self.w.factor.setToolTip("Multiplier applied to the source (caps) kerning value before copying it to the smallcap pair. Defaults to 1.0 (= copy as-is). Use e.g. 0.8 to scale down, or 1.2 to scale up.")
		linePos += lineHeight

		self.w.roundByText = vanilla.TextBox((inset, linePos + 2, 90, 14), "Round by", sizeStyle='small')
		self.w.roundBy = vanilla.EditText((inset + tab, linePos, -inset, 19), "5", callback=self.SavePreferences, sizeStyle='small')
		self.w.roundBy.setToolTip("Rounds the resulting kerning value to the nearest multiple of this number. Defaults to 5. Use 1 for no rounding, 10 for coarser snapping, etc.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Copy", callback=self.CopyKerningFromCapsToSmallcapsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.updateUI()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		isEnabled = self.w.includeNonLetters.get()
		self.w.figureSuffixText.enable(isEnabled)
		self.w.figureSuffix.enable(isEnabled)

	def CopyKerningFromCapsToSmallcapsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Copy Kerning from Caps to Smallcaps Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				smallcapSuffix = self.pref("smallcapSuffix")
				areSmallcapsNamedLowercase = self.pref("namingScheme") == 0
				includeNonLetters = self.pref("includeNonLetters")
				# copyCapCapToCapSC = self.pref("copyCapCapToCapSC")
				figureSuffix = self.pref("figureSuffix")
				includeAllMasters = self.pref("includeAllMasters")
				try:
					factor = float(self.pref("factor"))
				except (TypeError, ValueError):
					print("⚠️ Could not parse kerning factor %r, falling back to 1.0." % self.pref("factor"))
					factor = 1.0
				try:
					roundBy = float(self.pref("roundBy"))
				except (TypeError, ValueError):
					print("⚠️ Could not parse 'round by' value %r, falling back to 5." % self.pref("roundBy"))
					roundBy = 5.0
				if roundBy <= 0:
					print("⚠️ 'Round by' must be > 0, falling back to 1 (no rounding).")
					roundBy = 1.0

				# Sync left and right Kerning Groups between UC and SC:
				print("Kerning Groups:")
				UppercaseGroups = set()
				for g in thisFont.glyphs:
					if glyphNameIsSCconvertible(g.name, thisFont, includeNonLetters=includeNonLetters, suffix=smallcapSuffix, figureSuffix=figureSuffix):
						ucGlyphName = g.name
						scGlyphName = smallcapName(
							ucGlyphName, suffix=smallcapSuffix, lowercase=areSmallcapsNamedLowercase, includeNonLetters=includeNonLetters, figureSuffix=figureSuffix
						)
						scGlyph = thisFont.glyphs[scGlyphName]
						if scGlyph is None:
							print("  ⚠️ SC %s not found in font (UC %s exists)" % (scGlyphName, ucGlyphName))
							continue

						LeftKey = g.leftKerningGroupId()
						if LeftKey:
							UppercaseGroups.add(LeftKey)
							scLeftKey = LeftKey[:7] + smallcapName(
								LeftKey[7:], suffix=smallcapSuffix, lowercase=areSmallcapsNamedLowercase, includeNonLetters=includeNonLetters, figureSuffix=figureSuffix
							)
							if scGlyph.leftKerningGroupId() is None:
								scGlyph.setLeftKerningGroupId_(scLeftKey)
								print("  %s: set LEFT group to @%s (was empty)." % (scGlyphName, scLeftKey[7:]))
							elif scGlyph.leftKerningGroupId() != scLeftKey:
								print("  %s: unexpected LEFT group: @%s (should be @%s), not changed." % (scGlyphName, scGlyph.leftKerningGroupId()[7:], scLeftKey[7:]))

						RightKey = g.rightKerningGroupId()
						if RightKey:
							UppercaseGroups.add(RightKey)
							scRightKey = RightKey[:7] + smallcapName(
								RightKey[7:], suffix=smallcapSuffix, lowercase=areSmallcapsNamedLowercase, includeNonLetters=includeNonLetters, figureSuffix=figureSuffix
							)
							if scGlyph.rightKerningGroupId() is None:
								scGlyph.setRightKerningGroupId_(scRightKey)
								print("  %s: set RIGHT group to @%s (was empty)." % (scGlyphName, scRightKey[7:]))
							elif scGlyph.rightKerningGroupId() != scRightKey:
								print("  %s: unexpected RIGHT group: @%s (should be @%s), not changed." % (scGlyphName, scGlyph.rightKerningGroupId()[7:], scRightKey[7:]))

				print("  ✅ Kerning group conversion done.\n")

				if includeAllMasters:
					masters = thisFont.masters
				else:
					masters = (thisFont.selectedFontMaster, )

				for selectedFontMaster in masters:
					fontMasterID = selectedFontMaster.id
					fontMasterName = selectedFontMaster.name
					masterKernDict = thisFont.kerning[fontMasterID]
					# scKerningList = []
					# Report in the Macro Window:
					print("\n🔠 Master: %s\n" % (fontMasterName))

					# Sync Kerning Values between UC and SC:
					print("Kerning Values:")
					kerningToBeAdded = []
					LeftKeys = masterKernDict.keys()
					for LeftKey in LeftKeys:
						# is left key a class?
						leftKeyIsGroup = (LeftKey[0] == "@")
						# prepare SC left key:
						scLeftKey = None
						# determine the SC leftKey:
						if leftKeyIsGroup:  # a kerning group
							leftKeyName = "@%s" % LeftKey[7:]
							if LeftKey in UppercaseGroups:
								scLeftKey = LeftKey[:7] + smallcapName(
									LeftKey[7:], suffix=smallcapSuffix, lowercase=areSmallcapsNamedLowercase, includeNonLetters=includeNonLetters, figureSuffix=figureSuffix
								)
						else:  # a single glyph (exception)
							leftGlyphName = thisFont.glyphForId_(LeftKey).name
							leftKeyName = leftGlyphName
							if glyphNameIsSCconvertible(leftGlyphName, font=thisFont, includeNonLetters=includeNonLetters, suffix=smallcapSuffix, figureSuffix=figureSuffix):
								scLeftGlyphName = smallcapName(
									leftGlyphName, suffix=smallcapSuffix, lowercase=areSmallcapsNamedLowercase, includeNonLetters=includeNonLetters, figureSuffix=figureSuffix
								)
								scLeftGlyph = thisFont.glyphs[scLeftGlyphName]
								if scLeftGlyph:
									scLeftKey = scLeftGlyph.name

						RightKeys = masterKernDict[LeftKey].keys()
						for RightKey in RightKeys:
							# is right key a class?
							rightKeyIsGroup = (RightKey[0] == "@")
							# prepare SC right key:
							scRightKey = None
							# determine the SC rightKey:
							if rightKeyIsGroup:  # a kerning group
								rightKeyName = "@%s" % RightKey[7:]
								if RightKey in UppercaseGroups:
									scRightKey = RightKey[:7] + smallcapName(
										RightKey[7:], suffix=smallcapSuffix, lowercase=areSmallcapsNamedLowercase, includeNonLetters=includeNonLetters, figureSuffix=figureSuffix
									)
							else:  # a single glyph (exception)
								rightGlyphName = thisFont.glyphForId_(RightKey).name
								rightKeyName = rightGlyphName
								if glyphNameIsSCconvertible(rightGlyphName, font=thisFont, includeNonLetters=includeNonLetters, suffix=smallcapSuffix, figureSuffix=figureSuffix):
									scRightGlyphName = smallcapName(
										rightGlyphName, suffix=smallcapSuffix, lowercase=areSmallcapsNamedLowercase, includeNonLetters=includeNonLetters, figureSuffix=figureSuffix
									)
									scRightGlyph = thisFont.glyphs[scRightGlyphName]
									if scRightGlyph:
										scRightKey = scRightGlyph.name

							# If we have one of the left+right keys, create a pair:
							if scRightKey is not None or scLeftKey is not None:

								# fallback:
								if scLeftKey is None:
									scLeftKey = leftKeyName.replace("@", "@MMK_L_")
								if scRightKey is None:
									scRightKey = rightKeyName.replace("@", "@MMK_R_")

								sourceKernValue = masterKernDict[LeftKey][RightKey]
								scaledKernValue = sourceKernValue * factor
								scKernValue = round(scaledKernValue / roundBy) * roundBy
								print(
									"  Set kerning: %s %s %.1f (derived from %s %s = %.1f × %g, rounded to %g)" %
									(scLeftKey.replace("MMK_L_", ""), scRightKey.replace("MMK_R_", ""), scKernValue, leftKeyName, rightKeyName, sourceKernValue, factor, roundBy)
								)
								kerningToBeAdded.append((fontMasterID, scLeftKey, scRightKey, scKernValue))

					# go through the list of SC kern pairs, and add them to the font:
					thisFont.disableUpdateInterface()
					try:
						for thisKernInfo in kerningToBeAdded:
							fontMasterID = thisKernInfo[0]
							scLeftKey = thisKernInfo[1]
							scRightKey = thisKernInfo[2]
							scKernValue = thisKernInfo[3]
							thisFont.setKerningForPair(fontMasterID, scLeftKey, scRightKey, scKernValue)

					except Exception as e:
						Glyphs.showMacroWindow()
						print("\n⚠️ Script Error:\n")
						import traceback
						print(traceback.format_exc())
						print()
						raise e

					finally:
						thisFont.enableUpdateInterface()  # re-enables UI updates in Font View

				print("  Done.")

				self.w.close()  # delete if you want window to stay open

			# Final report:
			Glyphs.showNotification(
				"%s: Done" % (thisFont.familyName),
				"Copy Kerning from Caps to Smallcaps is finished. Details in Macro Window",
			)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Copy Kerning from Caps to Smallcaps Error: %s" % e)
			import traceback
			print(traceback.format_exc())


CopyKerningFromCapsToSmallcaps()
