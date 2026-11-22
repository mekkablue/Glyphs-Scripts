# MenuTitle: Copy Kerning from Caps to Smallcaps
__doc__ = """
Looks for cap kerning pairs and reduplicates their kerning for corresponding .sc glyphs, if they are available in the font. Please be careful: Will overwrite existing SC kerning pairs.
"""

import vanilla
from mekkablue import mekkaObject, SteppingEditText, decimalFormatter, makeWindowResizable
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)

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
		windowWidth = 370
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Copy Kerning from Caps to Smallcaps",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		self.w.smallcapSuffixText = vanilla.TextBox("auto", "Smallcap suffix", sizeStyle='small')
		self.w.smallcapSuffix = vanilla.ComboBox("auto", smallcapSuffixes, sizeStyle='small', callback=self.SavePreferences)

		self.w.namingSchemeText = vanilla.TextBox("auto", "SC naming scheme", sizeStyle='small')
		self.w.namingScheme = vanilla.PopUpButton("auto", namingSchemeOptions, sizeStyle='small', callback=self.SavePreferences)

		self.w.includeAllMasters = vanilla.CheckBox("auto", "⚠️ Include all masters (otherwise current master only)", value=False, callback=self.SavePreferences, sizeStyle='small')

		self.w.includeNonLetters = vanilla.CheckBox("auto", "Include smallcap non-letters (otherwise only from caps)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonLetters.setToolTip("Includes smallcap figures, punctuation, etc. E.g. copies kerning for parenright if there is  parenright.sc.")

		self.w.figureSuffixText = vanilla.TextBox("auto", "Figure suffix", sizeStyle='small')
		self.w.figureSuffix = vanilla.EditText("auto", ".lf", callback=self.SavePreferences, sizeStyle='small')

		factorFormatter = decimalFormatter(fractionDigits=3)
		self.w.factorText = vanilla.TextBox("auto", "Kerning factor", sizeStyle='small')
		self.w.factor = SteppingEditText("auto", "1.0", callback=self.SavePreferences, sizeStyle='small', formatter=factorFormatter)
		tooltipText = "Multiplier applied to the source (caps) kerning value before copying it to the smallcap pair. Defaults to 1.0 (= copy as-is). Use e.g. 0.8 to scale down, or 1.2 to scale up."
		self.w.factorText.setToolTip(tooltipText)
		self.w.factor.setToolTip(tooltipText)

		roundByFormatter = decimalFormatter(0, fractionDigits=3)
		self.w.roundByText = vanilla.TextBox("auto", "Round by", sizeStyle='small')
		self.w.roundBy = SteppingEditText("auto", "5", callback=self.SavePreferences, sizeStyle='small', formatter=roundByFormatter)
		tooltipText = "Rounds the resulting kerning value to the nearest multiple of this number. Defaults to 5. Use 1 for no rounding, 10 for coarser snapping, etc."
		self.w.roundByText.setToolTip(tooltipText)
		self.w.roundBy.setToolTip(tooltipText)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Copy", callback=self.CopyKerningFromCapsToSmallcapsMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned and share the width of the widest one, so the fields line up:
		labelNames = ("smallcapSuffixText", "namingSchemeText", "figureSuffixText", "factorText", "roundByText")
		widestLabel = "namingSchemeText"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[smallcapSuffixText]-gap-[smallcapSuffix]-inset-|",
				"H:|-inset-[namingSchemeText]-gap-[namingScheme]-inset-|",
				"H:|-inset-[includeAllMasters]-(>=inset)-|",
				"H:|-inset-[includeNonLetters]-(>=inset)-|",
				"H:|-inset-[figureSuffixText]-gap-[figureSuffix]-inset-|",
				"H:|-inset-[factorText]-gap-[factor(60)]-(>=inset)-|",
				"H:|-inset-[roundByText]-gap-[roundBy(60)]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[smallcapSuffix]-row-[namingScheme]-row-[includeAllMasters]-checkRow-[includeNonLetters]-row-[figureSuffix]-row-[factor]-row-[roundBy]-inset-[runButton]-inset-|",
				{"view1": self.w.smallcapSuffixText, "attribute1": "centerY", "view2": self.w.smallcapSuffix, "attribute2": "centerY"},
				{"view1": self.w.namingSchemeText, "attribute1": "centerY", "view2": self.w.namingScheme, "attribute2": "centerY"},
				{"view1": self.w.figureSuffixText, "attribute1": "centerY", "view2": self.w.figureSuffix, "attribute2": "centerY"},
				{"view1": self.w.factorText, "attribute1": "centerY", "view2": self.w.factor, "attribute2": "centerY"},
				{"view1": self.w.roundByText, "attribute1": "centerY", "view2": self.w.roundBy, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

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
