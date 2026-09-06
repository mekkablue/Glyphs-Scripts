# MenuTitle: Steal Kerning from InDesign
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Exports the current font's masters as temporary fonts to the Adobe Fonts folder,
then creates an InDesign document with optical kerning, measures and imports the
kerning for the selected glyph groupings, and cleans up afterwards.
"""

import os
import re
import subprocess
import time
import vanilla
from copy import copy
from mekkablue import mekkaObject, reportTimeInNaturalLanguage, UpdateButton
from GlyphsApp import Glyphs, GSInstance, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSLineBreakByTruncatingTail,
)


class StealKerningFromInDesign(mekkaObject):
	prefDict = {
		"zeroPair": "HH",
		"roundBy": 5,
		"minimumKern": 10,
		"letterToLetter": 1,
		"figureToFigure": 1,
		"letterToFigure": 1,
		"letterWithPunctuation": 1,
		"figureWithPunctuation": 1,
		"punctuationWithItself": 1,
		"ignoreScripts": "",
		"groupKerningOnly": 0,
		"addExceptions": 0,
		"exceptionChars": "AFJKLPTVWXYfďľ[](){}‚\u2018\u2019\u201e\u201c\u201d/?",
		"exceptionComponents": "dier, dot, acut, grav, tild, brev, macr, ring, circ, slash, bar",
		"deleteExistingKerning": 0,
		"compressKerning": 1,
		"allMasters": 1,
	}

	def __init__(self):
		windowWidth = 520
		windowHeight = 1  # Auto Layout determines the content height.
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Steal Kerning from InDesign",
			autosaveName=self.domain("mainwindow"),
		)

		# No-kern pair + Min kern + Round by — all on one row
		self.w.zeroPairLabel = vanilla.TextBox("auto", "No-kern pair:", sizeStyle="small")
		self.w.zeroPair = vanilla.EditText("auto", "HH", callback=self.SavePreferences, sizeStyle="small")
		self.w.zeroPair.setToolTip("A pair of glyphs that should have zero optical kerning (i.e., the reference pair used to calibrate the font size for measurement). Alternatively, enter a 3+ digit number (e.g. 009 for 9 pt, 100 for 100 pt) to use as a fixed font size and skip calibration entirely.")
		self.w.minimumKernLabel = vanilla.TextBox("auto", "Min kern:", sizeStyle="small")
		self.w.minimumKern = vanilla.EditText("auto", "10", callback=self.SavePreferences, sizeStyle="small")
		self.w.minimumKern.setToolTip("Discard imported kern pairs whose absolute value is smaller than this threshold.")
		self.w.roundByLabel = vanilla.TextBox("auto", "Round by:", sizeStyle="small")
		self.w.roundBy = vanilla.EditText("auto", "5", callback=self.SavePreferences, sizeStyle="small")
		self.w.roundBy.setToolTip("Round imported kern values to this multiple (e.g. 5 = multiples of 5). Set to 1 or 0 to skip rounding.")

		self.w.divider1 = vanilla.HorizontalLine("auto")

		# Pair type checkboxes — three columns
		self.w.letterToLetter = vanilla.CheckBox("auto", "Letter to Letter", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.letterToLetter.setToolTip("Kern pairs between uppercase and lowercase letters.")
		self.w.figureToFigure = vanilla.CheckBox("auto", "Figure to Figure", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.figureToFigure.setToolTip("Kern pairs between decimal digit figures.")
		self.w.letterToFigure = vanilla.CheckBox("auto", "Letter to Figure", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.letterToFigure.setToolTip("Kern pairs between letters and figures (both directions).")

		self.w.letterWithPunctuation = vanilla.CheckBox("auto", "Letter with Punctuation", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.letterWithPunctuation.setToolTip("Kern pairs between letters and punctuation marks (both directions).")
		self.w.figureWithPunctuation = vanilla.CheckBox("auto", "Figure with Punctuation", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.figureWithPunctuation.setToolTip("Kern pairs between figures and punctuation marks (both directions).")
		self.w.punctuationWithItself = vanilla.CheckBox("auto", "Punctuation with itself", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.punctuationWithItself.setToolTip("Kern pairs between punctuation marks and other punctuation marks.")

		self.w.ignoreScriptsLabel = vanilla.TextBox("auto", "Ignore scripts:", sizeStyle="small")
		self.w.ignoreScripts = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		self.w.ignoreScripts.setToolTip("Comma-separated glyph.script values. Glyphs whose script appears in this list are skipped when building kern pairs. Press the update button to populate with all scripts present in the current font.")
		self.w.ignoreScriptsUpdate = UpdateButton("auto", self.updateIgnoreScriptsField)
		self.w.ignoreScriptsUpdate.setToolTip("Populate the field with all scripts found in the current font.")

		self.w.divider2 = vanilla.HorizontalLine("auto")

		# Options
		self.w.allMasters = vanilla.CheckBox("auto", "All masters (otherwise current master only)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.allMasters.setToolTip("Process all masters in the font. If off, only the currently selected master is processed.")

		self.w.deleteExistingKerning = vanilla.CheckBox("auto", "Delete existing kerning before import", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.deleteExistingKerning.setToolTip("Clear all existing kerning for each master before importing new values from InDesign.")

		self.w.compressKerning = vanilla.CheckBox("auto", "Compress kerning (glyph pairs → group pairs)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.compressKerning.setToolTip("Promote glyph-to-glyph kern pairs to the corresponding group-to-group pair when the value matches.")

		self.w.groupKerningOnly = vanilla.CheckBox("auto", "Keep group kerning only", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.groupKerningOnly.setToolTip("After compressing, delete all remaining glyph-to-glyph pairs. Note: compressing cannot always convert every glyph pair to a group pair (e.g. when a glyph has no kerning group), so some pairs may remain.")

		self.w.addExceptions = vanilla.CheckBox("auto", "Add exceptions between:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.addExceptions.setToolTip("Also kern each of the characters in the field against all exporting glyphs whose name contains any of the component particles listed below.")
		self.w.exceptionChars = vanilla.EditText("auto", "AFJKLPTVWXYfďľ[](){}‚\u2018\u2019\u201e\u201c\u201d/?", callback=self.SavePreferences, sizeStyle="small")
		self.w.exceptionChars.setToolTip("Characters to kern against the diacritic glyphs. Each character is used in both directions (e.g. Tä and äT).")
		self.w.exceptionCharsReset = UpdateButton("auto", self.resetExceptionChars)

		self.w.exceptionComponentsLabel = vanilla.TextBox("auto", "…and glyphs containing:", sizeStyle="small")
		self.w.exceptionComponents = vanilla.EditText("auto", "dier, dot, acut, grav, tild, brev, macr, ring, circ, slash, bar", callback=self.SavePreferences, sizeStyle="small")
		self.w.exceptionComponents.setToolTip("Comma-separated name fragments. Any exporting glyph with a Unicode whose name contains one of these is measured against the characters above.")
		self.w.exceptionComponentsReset = UpdateButton("auto", self.resetExceptionComponents)

		# Progress bar + Status + Run button
		self.w.progressBar = vanilla.ProgressBar("auto")
		self.w.progressBar.show(False)
		self.w.status = vanilla.TextBox("auto", "🤖 Ready. 💬 See tooltips for help.", sizeStyle="small", selectable=True)
		self.w.runButton = vanilla.Button("auto", "Kern", callback=self.run)
		self.w.setDefaultButton(self.w.runButton)

		# Fixed vertical gaps and hugging let AppKit size the window to its content.
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)
		for label in (self.w.zeroPairLabel, self.w.minimumKernLabel, self.w.roundByLabel, self.w.ignoreScriptsLabel, self.w.exceptionComponentsLabel):
			nsLabel = label.getNSTextField()
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		# Status messages can be longer than the window; keep them on one line.
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(249, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setContentHuggingPriority_forOrientation_(249, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setLineBreakMode_(NSLineBreakByTruncatingTail)

		rules = [
			"H:|-inset-[zeroPairLabel]-gap-[zeroPair(40)]-inset-[minimumKernLabel]-gap-[minimumKern(40)]-inset-[roundByLabel]-gap-[roundBy(40)]-(>=inset)-|",
			"H:|-inset-[divider1]-inset-|",
			"H:|-inset-[letterToLetter]-gap-[figureToFigure]-gap-[letterToFigure]-inset-|",
			"H:|-inset-[letterWithPunctuation]-gap-[figureWithPunctuation]-gap-[punctuationWithItself]-inset-|",
			"H:|-inset-[ignoreScriptsLabel]-gap-[ignoreScripts(>=80)]-gap-[ignoreScriptsUpdate(20)]-inset-|",
			"H:|-inset-[divider2]-inset-|",
			"H:|-inset-[allMasters]-(>=inset)-|",
			"H:|-inset-[deleteExistingKerning]-(>=inset)-|",
			"H:|-inset-[compressKerning]-(>=inset)-|",
			"H:|-indent-[groupKerningOnly]-(>=inset)-|",
			"H:|-indent-[addExceptions]-gap-[exceptionChars(>=80)]-gap-[exceptionCharsReset(20)]-inset-|",
			"H:|-subindent-[exceptionComponentsLabel]-gap-[exceptionComponents(>=80)]-gap-[exceptionComponentsReset(20)]-inset-|",
			"H:|-inset-[progressBar]-inset-|",
			"H:|-inset-[status]-gap-[runButton]-inset-|",
			"V:|-gap-[zeroPair]-row-[divider1(1)]-row-[letterToLetter]-row-[letterWithPunctuation]-row-[ignoreScripts]-row-[divider2(1)]-row-[allMasters]-row-[deleteExistingKerning]-row-[compressKerning]-row-[groupKerningOnly]-row-[exceptionChars]-row-[exceptionComponents]-row-[progressBar(16)]-row-[runButton]-inset-|",
			"V:[divider1]-row-[figureToFigure]-row-[figureWithPunctuation]",
			"V:[divider1]-row-[letterToFigure]-row-[punctuationWithItself]",
		]
		gridCheckBoxes = [
			self.w.letterToLetter, self.w.figureToFigure, self.w.letterToFigure,
			self.w.letterWithPunctuation, self.w.figureWithPunctuation, self.w.punctuationWithItself,
		]
		for cell in gridCheckBoxes[1:]:
			rules.append({"view1": cell, "attribute1": "width", "view2": gridCheckBoxes[0], "attribute2": "width"})
		for label, field in (
			(self.w.zeroPairLabel, self.w.zeroPair),
			(self.w.minimumKernLabel, self.w.zeroPair),
			(self.w.minimumKern, self.w.zeroPair),
			(self.w.roundByLabel, self.w.zeroPair),
			(self.w.roundBy, self.w.zeroPair),
			(self.w.ignoreScriptsLabel, self.w.ignoreScripts),
			(self.w.ignoreScriptsUpdate, self.w.ignoreScripts),
			(self.w.addExceptions, self.w.exceptionChars),
			(self.w.exceptionCharsReset, self.w.exceptionChars),
			(self.w.exceptionComponentsLabel, self.w.exceptionComponents),
			(self.w.exceptionComponentsReset, self.w.exceptionComponents),
			(self.w.status, self.w.runButton),
		):
			rules.append({"view1": label, "attribute1": "centerY", "view2": field, "attribute2": "centerY"})
		rules.append({"view1": self.w.exceptionComponents, "attribute1": "left", "view2": self.w.exceptionChars, "attribute2": "left"})
		inset = 15
		self.w.addAutoPosSizeRules(rules, metrics={"inset": inset, "gap": 8, "row": 8, "indent": inset + 20, "subindent": inset + 38})

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		anyPairType = (
			self.w.letterToLetter.get()
			or self.w.figureToFigure.get()
			or self.w.letterToFigure.get()
			or self.w.letterWithPunctuation.get()
			or self.w.figureWithPunctuation.get()
			or self.w.punctuationWithItself.get()
		)
		self.w.runButton.enable(anyPairType)
		compressOn = bool(self.w.compressKerning.get())
		self.w.groupKerningOnly.enable(compressOn)
		self.w.addExceptions.enable(compressOn)
		addExceptionsOn = compressOn and bool(self.w.addExceptions.get())
		self.w.exceptionChars.enable(addExceptionsOn)
		self.w.exceptionCharsReset.enable(addExceptionsOn)
		self.w.exceptionComponents.enable(addExceptionsOn)
		self.w.exceptionComponentsReset.enable(addExceptionsOn)

	def resetExceptionChars(self, sender=None):
		self.w.exceptionChars.set("AFJKLPTVWXYf\u010f\u013e[](){}‚\u2018\u2019\u201e\u201c\u201d/?")
		self.SavePreferences()

	def resetExceptionComponents(self, sender=None):
		self.w.exceptionComponents.set("dier, dot, acut, grav, tild, brev, macr, ring, circ, slash, bar")
		self.SavePreferences()

	def updateIgnoreScriptsField(self, sender=None):
		thisFont = Glyphs.font
		if not thisFont:
			return
		scripts = sorted(set(g.script for g in thisFont.glyphs if g.script))
		self.w.ignoreScripts.set(", ".join(scripts))
		self.SavePreferences()

	# ------------------------------------------------------------------ exception pair builder

	def _buildExceptionPairText(self, thisFont):
		"""
		Return a list of (leftCharStr, rightCharStr) pairs for exception kerning:
		each character in exceptionChars × every exporting glyph with a Unicode whose
		name contains any of the comma-separated exceptionComponents particles.
		Both directions are included (e.g. T+ä and ä+T).
		"""
		exceptionChars = self.pref("exceptionChars") or ""
		exceptionComponents = self.pref("exceptionComponents") or ""
		particles = [p.strip() for p in exceptionComponents.split(",") if p.strip()]
		if not exceptionChars or not particles:
			return []

		# Filter exceptionChars to glyphs that are in the font, exporting,
		# have a Unicode, and are not category Mark or Symbol.
		validBaseChars = []
		for char in exceptionChars:
			glyphName = Glyphs.niceGlyphName(char)
			if not glyphName:
				continue
			glyph = thisFont.glyphs[glyphName]
			if not glyph:
				continue
			if not glyph.export:
				continue
			if not glyph.unicode:
				continue
			if glyph.category in ("Mark", "Symbol"):
				continue
			validBaseChars.append(char)

		if not validBaseChars:
			print("\t⚠️ No valid base chars found in font for exceptions.")
			return []

		diacriticStrings = []
		for glyph in thisFont.glyphs:
			if not glyph.export:
				continue
			if not glyph.unicode:
				continue
			if glyph.category in ("Mark", "Symbol"):
				continue
			for particle in particles:
				if particle in glyph.name:
					diacriticStrings.append(glyph.charString())
					break

		if not diacriticStrings:
			return []

		pairs = []
		seen = set()

		def addPair(left, right):
			key = (left, right)
			if key not in seen:
				seen.add(key)
				pairs.append(key)

		for baseChar in validBaseChars:
			for diacriticStr in diacriticStrings:
				addPair(baseChar, diacriticStr)
				addPair(diacriticStr, baseChar)

		print("\t☑️ %i exception pairs to measure." % len(pairs))
		return pairs

	# ------------------------------------------------------------------ helpers

	def _runAppleScript(self, source):
		"""Run an AppleScript string via osascript; return stdout string or False on error."""
		try:
			result = subprocess.run(
				["osascript", "-"],
				input=source,
				text=True,
				capture_output=True,
			)
			if result.returncode != 0:
				print("AppleScript Error:")
				print(result.stderr.strip())
				print("Script:")
				for i, line in enumerate(source.splitlines()):
					print("%03i %s" % (i + 1, line))
				return False
			return result.stdout.strip()
		except Exception as e:
			print("AppleScript runner error: %s" % e)
			return False

	def _sanitizeName(self, name):
		"""Keep only A-Z a-z 0-9 and space — safe for PostScript family/style names."""
		return re.sub(r"[^A-Za-z0-9 ]", "", name)

	def _adobeFontsFolder(self):
		"""Return the path to /Library/Application Support/Adobe/Fonts (global), creating it if needed."""
		path = "/Library/Application Support/Adobe/Fonts"
		os.makedirs(path, exist_ok=True)
		return path

	# ------------------------------------------------------------------ step 1

	def _exportMasters(self, thisFont, masters):
		"""
		Export each master as a standalone OTF into the Adobe Fonts folder.
		Family name: 'Kernstealer'
		Style name:  sanitized master name
		Returns a list of successfully exported (master, filePath) tuples.
		"""
		adobeFontsFolder = self._adobeFontsFolder()
		plannedExports = []

		tempFont = copy(thisFont)
		tempFont.instances = []
		tempFont.familyName = "Kernstealer"

		for tempMaster in masters:
			# create instance same as master
			tempInstance = GSInstance()
			tempFont.instances.append(tempInstance)
			tempInstance.axes = tempMaster.axes
			tempInstance.name = tempMaster.name

			# calculate file names and paths
			try:
				fileName = tempInstance.fileName()
			except TypeError:
				# Glyphs 4: fileName() now requires a format argument
				fileName = tempInstance.fileName("otf")
			filePath = os.path.join(adobeFontsFolder, fileName) # including ".otf" suffix
			if "." in fileName:
				fileName = fileName[:fileName.rfind(".")]
			tempInstance.customParameters["fileName"] = fileName # excluding ".otf" suffix

			styleName = self._sanitizeName(tempMaster.name) or ("Master%i" % masters.index(tempMaster))
			fileName = "Kernstealer-%s.otf" % styleName.replace(" ", "")
			filePath = os.path.join(adobeFontsFolder, fileName)

			plannedExports.append((tempMaster, filePath))

		# export optimized for speed:
		exportResults = tempFont.export(
			format="OTF",
			instances=tempFont.instances,
			fontPath=adobeFontsFolder,
			autoHint=False,
			removeOverlap=False, # reconsider this one, may have influence on the result
			useSubroutines=False,
			useProductionNames=True,
			containers=["plain"],
		)
		if isinstance(exportResults, (str, bytes)) or not hasattr(exportResults, "__iter__"):
			# Glyphs may return one error value for the whole export.
			exportResults = [exportResults] * len(plannedExports)
		else:
			exportResults = list(exportResults)

		exported = []
		missingResult = object()
		for i, (master, filePath) in enumerate(plannedExports):
			exportError = exportResults[i] if i < len(exportResults) else missingResult
			if exportError is None:
				exported.append((master, filePath))
				print("\t✅ Exported: %s → %s" % (master.name, filePath))
			else:
				print("\t❌ Export failed for master: %s" % master.name)
				if exportError is missingResult:
					print("\t   Glyphs returned no result for this master.")
				else:
					print("\t   %s" % exportError)

		return exported

	# ------------------------------------------------------------------ step 2

	def _getOpticalKerningString(self):
		"""
		Read InDesign's locale directly and return the matching localized string
		for its optical kerning method. This avoids requiring Accessibility access.
		"""
		script = """
tell application id "com.adobe.InDesign"
	return locale as string
end tell
"""
		localeName = self._runAppleScript(script) or ""
		localeKey = localeName.lower()
		opticalByLocale = {
			"french": "Optique",
			"german": "Optisch",
			"spanish": "Óptica",
			"portuguese": "Óptica",
			"swedish": "Optisk",
			"danish": "Optisk",
		}
		opticalStr = "optical"
		for localeFragment, localizedOptical in opticalByLocale.items():
			if localeFragment in localeKey:
				opticalStr = localizedOptical
				break
		print('\t🌐 InDesign locale: "%s" → kerning method string: "%s"' % (localeName or "?", opticalStr))
		return opticalStr

	def _createInDesignDoc(self, familyName, styleName, opticalStr="optical"):
		"""
		Create a new A3-landscape InDesign document with a full-page text frame,
		font set to 3 pt with optical kerning, text = zeroPair.
		Returns True on success.
		"""
		zeroPair = self.pref("zeroPair") or "HH"
		# Escape for AppleScript string
		zeroPairAS = zeroPair.replace("\\", "\\\\").replace('"', '\\"')
		# A3 landscape: 420 x 297 mm = 1190.55 x 841.89 pt
		script = """
tell application id "com.adobe.InDesign"
	set myDoc to make new document
	tell myDoc
		set name to "Steal Kerning"
		tell document preferences
			set page width to 1200
			set page height to 850
			set pages per document to 1
			set facing pages to false
		end tell
		set myFrame to make new text frame with properties {geometric bounds:{0, 0, 850, 1200}}
		set contents of myFrame to "%s"
		tell parent story of myFrame
			set point size to 3
			set applied font to ("Kernstealer" & tab & "%s")
			set kerning method to "%s"
		end tell
	end tell
end tell
true
""" % (zeroPairAS, styleName, opticalStr)
		result = self._runAppleScript(script)
		return bool(result)

	def _calibrateFontSize(self, styleName):
		"""
		Starting at 3 pt, step up 1 pt at a time until the optical kern value
		between insertion point 1→2 is <= 0.  Then step back down in 0.1 pt
		increments until the kern value is as close to 0.0 as possible.
		Returns the calibrated point size as a float.
		"""
		def floatFromString(s):
			return float("".join(c for c in s if c.isdigit() or c == "."))

		# Step up by 1 pt until kern <= 0 — done in a single AppleScript repeat loop
		scriptUp = """
on convertPtStringToReal(ptString)
	set oldTIDs to AppleScript's text item delimiters
	try
		set AppleScript's text item delimiters to " pt"
		set theValue to (text item 1 of ptString) as real
		set AppleScript's text item delimiters to oldTIDs
		return theValue
	on error errMsg number errNum
		set AppleScript's text item delimiters to oldTIDs
		error errMsg number errNum
	end try
end convertPtStringToReal

tell application id "com.adobe.InDesign"
	tell front document
		zoom first layout window given fit page
		tell first text frame
			tell parent story
				set point size to 3.0
				set kernVal to 10000
				repeat while kernVal > 1
					set point size to point size + 0.25
					tell character 1 to set kernVal to kerning value of insertion point 2
				end repeat
				set roundedPointSize to round my convertPtStringToReal(point size as string) rounding up
				return (roundedPointSize as string) & ";" & (kernVal as integer)
			end tell
		end tell
	end tell
end tell
"""

		size = 3.0
		result = self._runAppleScript(scriptUp)
		if not result or ";" not in result:
			return size
		parts = result.split(";")
		try:
			size = floatFromString(parts[0])
			kernVal = floatFromString(parts[1])
		except ValueError:
			return size

		# Step down by 0.1 pt to get as close to 0 as possible
		scriptDown = """
tell application id "com.adobe.InDesign"
	tell front document
		zoom first layout window given fit page
		tell first text frame
			tell character 1 of parent story
				set curSize to point size
				set kernVal to kerning value of insertion point 2
				if kernVal < 0 then
					set point size to curSize - 0.1
				end if
				return (point size as string) & "," & (kernVal as string)
			end tell
		end tell
	end tell
end tell
"""

		bestSize = size
		bestAbsKern = 999999.0
		for _ in range(200):  # safety cap: 20 pt fine-search
			result = self._runAppleScript(scriptDown)
			if not result or "," not in result:
				break
			parts = result.split(",")
			try:
				size = floatFromString(parts[0])
				kernVal = floatFromString(parts[1])
			except ValueError:
				break
			if abs(kernVal) < bestAbsKern:
				bestAbsKern = abs(kernVal)
				bestSize = size
			if kernVal >= 0:
				break

		# print("\t🔢 Calibrated font size: %.1f pt (kern delta %.2f)" % (bestSize, bestAbsKern))
		return bestSize

	# ------------------------------------------------------------------ step 3

	def _glyphsForCategory(self, thisFont, category, subcategory=None):
		"""
		Return exporting GSGlyph objects matching category (and optional subcategory).
		Skips glyphs with no Unicode, empty glyphs (no shapes in any master layer),
		glyphs made of 2+ components (can't be typed reliably), and glyphs whose
		script appears in the ignoreScripts preference.
		"""
		ignoreScriptsStr = self.pref("ignoreScripts") or ""
		ignoredScripts = set(s.strip() for s in ignoreScriptsStr.split(",") if s.strip())
		result = []
		for glyph in thisFont.glyphs:
			if not glyph.export:
				continue
			if not glyph.unicode:
				continue
			if glyph.name == "jdotless":
				continue
			if ignoredScripts and glyph.script in ignoredScripts:
				continue
			if glyph.category != category:
				continue
			if subcategory and glyph.subCategory != subcategory:
				continue
			# skip glyphs that are empty in every master layer
			isEmpty = True
			for master in thisFont.masters:
				layer = glyph.layers[master.id]
				if layer and len(layer.shapes) > 0:
					isEmpty = False
					break
			if isEmpty:
				continue
			# skip glyphs that are purely composite (2+ components, no contours)
			# exception: i and j are allowed even if built from components
			isComposite = False
			if glyph.name not in ("i", "j"):
				for master in thisFont.masters:
					layer = glyph.layers[master.id]
					if layer and len(layer.components) >= 2 and len(layer.paths) == 0:
						isComposite = True
						break
			if not isComposite:
				result.append(glyph.charString())
		return result

	def _pickRepresentatives(self, thisFont, charStrings, groupAttr):
		"""
		Reduce charStrings to one representative per kerning group (groupAttr is
		'rightKerningGroup' for glyphs used on the left side of a pair, or
		'leftKerningGroup' for glyphs used on the right side).
		Glyphs with no kerning group are kept individually.
		Within a group, preference order:
		  1. in _PREFER_CHARS and symmetric (leftKerningGroup == rightKerningGroup)
		  2. in _PREFER_CHARS
		  3. symmetric
		  4. first in list
		"""
		charToGlyph = {}
		for cs in charStrings:
			if len(cs) != 1:
				continue
			info = Glyphs.glyphInfoForUnicode("%.4X" % ord(cs))
			if info:
				glyph = thisFont.glyphs[info.name]
				if glyph:
					charToGlyph[cs] = glyph

		groups = {}
		ungrouped = []
		for cs in charStrings:
			glyph = charToGlyph.get(cs)
			groupName = getattr(glyph, groupAttr, None) if glyph else None
			if not groupName:
				ungrouped.append(cs)
			else:
				groups.setdefault(groupName, []).append(cs)

		def score(cs):
			g = charToGlyph.get(cs)
			inPrefer = cs in self._PREFER_CHARS
			symmetric = bool(g and g.leftKerningGroup and g.leftKerningGroup == g.rightKerningGroup)
			if inPrefer and symmetric:
				return 0
			if inPrefer:
				return 1
			if symmetric:
				return 2
			return 3

		result = list(ungrouped)
		for members in groups.values():
			result.append(min(members, key=score))
		return result

	def _glyphScript(self, thisFont, cs):
		"""Return glyph.script for a single-char string, or 'other' if unknown."""
		if len(cs) != 1:
			return "other"
		info = Glyphs.glyphInfoForUnicode("%.4X" % ord(cs))
		if not info:
			return "other"
		glyph = thisFont.glyphs[info.name]
		return (glyph.script or "other") if glyph else "other"

	def _buildPairs(self, thisFont):
		"""
		Build all requested character-pair combinations.
		Returns a list of (leftChar, rightChar) tuples.
		"""
		doLetterToLetter = self.prefBool("letterToLetter")
		doFigureToFigure = self.prefBool("figureToFigure")
		doLetterToFigure = self.prefBool("letterToFigure")
		doLetterWithPunctuation = self.prefBool("letterWithPunctuation")
		doFigureWithPunctuation = self.prefBool("figureWithPunctuation")
		doPunctuationWithItself = self.prefBool("punctuationWithItself")

		needLetters = doLetterToLetter or doLetterToFigure or doLetterWithPunctuation
		needFigures = doFigureToFigure or doLetterToFigure or doFigureWithPunctuation
		needPunctuation = doLetterWithPunctuation or doFigureWithPunctuation or doPunctuationWithItself

		letters = self._glyphsForCategory(thisFont, "Letter") if needLetters else []
		figures = self._glyphsForCategory(thisFont, "Number", "Decimal Digit") if needFigures else []
		punctuation = self._glyphsForCategory(thisFont, "Punctuation") if needPunctuation else []
		print("\t📊 Glyph counts: %i letters, %i figures, %i punctuation." % (len(letters), len(figures), len(punctuation)))

		# When compress kerning is on, reduce each list to one representative per
		# kerning group — separately for the left-side role (rightKerningGroup) and
		# the right-side role (leftKerningGroup).
		doCompress = self.prefBool("compressKerning")
		if doCompress:
			lettersLeft = self._pickRepresentatives(thisFont, letters, "rightKerningGroup")
			lettersRight = self._pickRepresentatives(thisFont, letters, "leftKerningGroup")
			figuresLeft = self._pickRepresentatives(thisFont, figures, "rightKerningGroup")
			figuresRight = self._pickRepresentatives(thisFont, figures, "leftKerningGroup")
			punctuationLeft = self._pickRepresentatives(thisFont, punctuation, "rightKerningGroup")
			punctuationRight = self._pickRepresentatives(thisFont, punctuation, "leftKerningGroup")
			print(
				"\t📐 Grouping: letters %i→%i/%i, figures %i→%i/%i, punctuation %i→%i/%i (L/R)." % (
					len(letters), len(lettersLeft), len(lettersRight),
					len(figures), len(figuresLeft), len(figuresRight),
					len(punctuation), len(punctuationLeft), len(punctuationRight),
				)
			)
		else:
			lettersLeft = lettersRight = letters
			figuresLeft = figuresRight = figures
			punctuationLeft = punctuationRight = punctuation

		# collect unique pairs as (leftName, rightName)
		pairs = []
		seen = set()

		def addPair(left, right):
			key = (left, right)
			if key not in seen:
				seen.add(key)
				pairs.append(key)

		if doLetterToLetter:
			# Only pair letters within the same writing system
			leftByScript = {}
			rightByScript = {}
			for cs in lettersLeft:
				leftByScript.setdefault(self._glyphScript(thisFont, cs), []).append(cs)
			for cs in lettersRight:
				rightByScript.setdefault(self._glyphScript(thisFont, cs), []).append(cs)
			for script, leftChars in leftByScript.items():
				for L in leftChars:
					for R in rightByScript.get(script, []):
						addPair(L, R)

		if doFigureToFigure:
			for L in figuresLeft:
				for R in figuresRight:
					addPair(L, R)

		if doLetterToFigure:
			for L in lettersLeft:
				for R in figuresRight:
					addPair(L, R)
			for L in figuresLeft:
				for R in lettersRight:
					addPair(L, R)

		if doLetterWithPunctuation:
			for L in lettersLeft:
				for R in punctuationRight:
					addPair(L, R)
			for L in punctuationLeft:
				for R in lettersRight:
					addPair(L, R)

		if doFigureWithPunctuation:
			for L in figuresLeft:
				for R in punctuationRight:
					addPair(L, R)
			for L in punctuationLeft:
				for R in figuresRight:
					addPair(L, R)

		if doPunctuationWithItself:
			for L in punctuationLeft:
				for R in punctuationRight:
					addPair(L, R)

		print("\t📏 Found %i pairs to measure." % len(pairs))
		return pairs

	def _setInDesignTextAndFont(self, pairText, styleName, calibSize, opticalStr="optical"):
		"""
		Replace the text frame content with pairText, set the font and
		calibrated point size with optical kerning on every character.
		"""
		# Escape the slash-name string for AppleScript (no special chars expected)
		pairTextAS = pairText.replace("\\", "\\\\").replace('"', '\\"')
		script = """
tell application id "com.adobe.InDesign"
	tell front document
		zoom first layout window given fit page
		set contents of first text frame to "%s"
		tell parent story of first text frame
			set point size to %s
			set applied font to ("Kernstealer" & tab & "%s")
			set kerning method to "%s"
		end tell
	end tell
end tell
true
""" % (pairTextAS, calibSize, styleName, opticalStr)
		return bool(self._runAppleScript(script))

	# ------------------------------------------------------------------ step 4

	# Preferred representatives when reducing glyph lists to one per kerning group.
	# Symmetric glyphs (same left and right group) from this list are preferred first.
	_PREFER_CHARS = frozenset(
		"AHIMNOTUVWXYlovwx08.:!*+"  # Latin
		"ΑΔΗΘΙΛΜΝΞΟΠΤΥΦΧΨΩθοφω·"  # Greek
		"АЖИМНОПТФХШІимноптфхші"   # Cyrillic
		"ᲑᲘᲝᲢთიოტᲶᲾᲿჾჿ"           # Georgian
	)

	def _glyphNameForChar(self, char):
		"""Return the Glyphs glyph name for a single Unicode character, or None."""
		if not char:
			return None
		utf16 = "%.4X" % ord(char[0])
		info = Glyphs.glyphInfoForUnicode(utf16)
		if info:
			return info.name
		return None

	def _readKernValuesFromInDesign(self, expectedPairs, minimumKern=0.0):
		"""
		Read insertion-point kern values inside InDesign's JavaScript engine.
		Only one Apple event crosses the process boundary; the former AppleScript loop
		issued several InDesign object-model requests per character and was very slow.
		The Unicode values of the characters InDesign actually composed are returned,
		so automatic quote substitution behaves exactly like the former reader.
		Returns a list of (leftChar, rightChar, kernValue) tuples.
		"""
		start = time.time()
		javascript = """
(function () {
	var specialCharacterHex = {};
	specialCharacterHex[SpecialCharacters.BULLET_CHARACTER] = "2022";
	specialCharacterHex[SpecialCharacters.COPYRIGHT_SYMBOL] = "00A9";
	specialCharacterHex[SpecialCharacters.DEGREE_SYMBOL] = "00B0";
	specialCharacterHex[SpecialCharacters.DOUBLE_LEFT_QUOTE] = "201C";
	specialCharacterHex[SpecialCharacters.DOUBLE_RIGHT_QUOTE] = "201D";
	specialCharacterHex[SpecialCharacters.DOUBLE_STRAIGHT_QUOTE] = "0022";
	specialCharacterHex[SpecialCharacters.ELLIPSIS_CHARACTER] = "2026";
	specialCharacterHex[SpecialCharacters.EM_DASH] = "2014";
	specialCharacterHex[SpecialCharacters.EN_DASH] = "2013";
	specialCharacterHex[SpecialCharacters.NONBREAKING_HYPHEN] = "2011";
	specialCharacterHex[SpecialCharacters.NONBREAKING_SPACE] = "00A0";
	specialCharacterHex[SpecialCharacters.PARAGRAPH_SYMBOL] = "00B6";
	specialCharacterHex[SpecialCharacters.REGISTERED_TRADEMARK] = "00AE";
	specialCharacterHex[SpecialCharacters.SECTION_SYMBOL] = "00A7";
	specialCharacterHex[SpecialCharacters.SINGLE_LEFT_QUOTE] = "2018";
	specialCharacterHex[SpecialCharacters.SINGLE_RIGHT_QUOTE] = "2019";
	specialCharacterHex[SpecialCharacters.SINGLE_STRAIGHT_QUOTE] = "0027";
	specialCharacterHex[SpecialCharacters.TRADEMARK_SYMBOL] = "2122";

	function characterHex(value) {
		var specialHex = specialCharacterHex[value];
		if (specialHex) return specialHex;
		if (typeof value !== "string" || value.length === 0) return "";
		var codePoint = value.charCodeAt(0);
		if (codePoint >= 0xD800 && codePoint <= 0xDBFF && value.length > 1) {
			var lowSurrogate = value.charCodeAt(1);
			if (lowSurrogate >= 0xDC00 && lowSurrogate <= 0xDFFF) {
				codePoint = 0x10000 + ((codePoint - 0xD800) * 0x400) + (lowSurrogate - 0xDC00);
			}
		}
		return codePoint.toString(16).toUpperCase();
	}

	var story = app.documents[0].textFrames[0].parentStory;
	var chars = story.characters;
	var output = [];
	var pairIndex = 0;
	for (var x = 0; x < chars.length - 1; x++) {
		try {
			var leftHex = characterHex(chars[x].contents);
			var rightHex = characterHex(chars[x + 1].contents);
			if (leftHex !== "20" && rightHex !== "20") {
				var currentPair = pairIndex++;
				var kernValue = chars[x].insertionPoints[1].kerningValue;
				if (Math.abs(kernValue) >= %s) {
					output.push(currentPair, leftHex, rightHex, kernValue);
				}
			}
		} catch (e) {}
	}
	return pairIndex + "-#-" + output.join("-#-");
}());
""" % float(minimumKern)
		javascript = javascript.replace("\\", "\\\\").replace('"', '\\"')
		script = """
tell application id "com.adobe.InDesign"
	set measurementScript to "%s"
	return do script measurementScript language javascript
end tell
""" % javascript
		raw = self._runAppleScript(script)
		print("\t⏱ Read kerning from InDesign in %.2fs." % (time.time() - start))
		if not raw:
			return []
		return self._parseKernValues(raw, expectedPairs)

	def _parseKernValues(self, output, expectedPairs):
		"""
		Parse InDesign's -#-delimited pair indexes, composed characters and values.
		"""
		items = output.split("-#-")
		try:
			measuredPairCount = int(items[0])
		except (IndexError, ValueError):
			print("\t⚠️ Could not parse InDesign's measurement count.")
			return []
		if measuredPairCount != len(expectedPairs):
			print("\t⚠️ InDesign measured %i pair positions; expected %i." % (measuredPairCount, len(expectedPairs)))

		pairs = []
		for i in range(1, len(items) - 3, 4):
			try:
				pairIndex = int(items[i])
				expectedLeft, expectedRight = expectedPairs[pairIndex]
				leftChar = chr(int(items[i + 1], 16)) if items[i + 1] else expectedLeft
				rightChar = chr(int(items[i + 2], 16)) if items[i + 2] else expectedRight
				kernVal = float(items[i + 3].replace(",", "."))
			except (IndexError, TypeError, ValueError):
				continue
			pairs.append((leftChar, rightChar, kernVal))
		return pairs

	def _importKerningForMaster(self, thisFont, master, expectedPairs, minimumKern=0.0, roundBy=0.0):
		"""
		Read kern values from InDesign and set them in thisFont for the given master.
		minimumKern is passed into the AppleScript so only qualifying pairs are returned.
		Returns the number of pairs imported.
		"""
		masterID = master.id
		kernPairs = self._readKernValuesFromInDesign(expectedPairs, minimumKern)
		nameCache = {}
		count = 0
		thisFont.disableUpdateInterface()
		try:
			for leftChar, rightChar, kernValue in kernPairs:
				if kernValue == 0 or abs(kernValue) < minimumKern:
					continue
				if roundBy > 0:
					kernValue = round(kernValue / roundBy) * roundBy
				if abs(kernValue) < minimumKern:
					continue
				if leftChar not in nameCache:
					nameCache[leftChar] = self._glyphNameForChar(leftChar)
				if rightChar not in nameCache:
					nameCache[rightChar] = self._glyphNameForChar(rightChar)
				leftName = nameCache[leftChar]
				rightName = nameCache[rightChar]
				if not leftName or not rightName:
					continue
				if not thisFont.glyphs[leftName] or not thisFont.glyphs[rightName]:
					continue
				thisFont.setKerningForPair(masterID, leftName, rightName, kernValue)
				count += 1
		finally:
			thisFont.enableUpdateInterface()
		print("\t↔️ Imported %i kern pairs for master ‘%s’." % (count, master.name))
		return count

	def _importExceptionKerningForMaster(self, thisFont, master, expectedPairs, minimumKern=0, roundBy=0):
		"""
		Read kern values from InDesign and store them as group-glyph (or glyph-glyph)
		exception pairs.  A pair is only kept if its rounded value differs from the
		existing group-to-group kerning by at least max(min(roundBy, minimumKern), 8 + roundBy/2).
		Group-group pairs that existed before this call are explicitly restored afterwards,
		in case setKerningForPair accidentally resolved a glyph name to its group key.
		Returns the number of exception pairs stored.
		"""
		masterID = master.id
		# Delta threshold: the exception must differ from group-group by at least this much.
		deltaThreshold = max(min(roundBy, minimumKern), 8 + roundBy / 2)

		# Snapshot all group-group pairs so we can restore any that get overwritten.
		savedGroupGroup = {}
		for leftID, rightDict in (thisFont.kerning.get(masterID) or {}).items():
			if leftID.startswith("@"):
				for rightID, val in rightDict.items():
					if rightID.startswith("@"):
						savedGroupGroup[(leftID, rightID)] = val

		# No AppleScript pre-filter: we need raw values to compare against group kern
		kernPairs = self._readKernValuesFromInDesign(expectedPairs, 0)
		totalRaw = len(kernPairs)
		droppedZero = droppedName = droppedGlyph = droppedDelta = 0
		nameCache = {}
		count = 0
		restoredCount = 0
		thisFont.disableUpdateInterface()
		try:
			for leftChar, rightChar, kernValue in kernPairs:
				if kernValue == 0:
					droppedZero += 1
					continue
				if roundBy > 0:
					kernValue = round(kernValue / roundBy) * roundBy
				if kernValue == 0:
					droppedZero += 1
					continue
				if leftChar not in nameCache:
					nameCache[leftChar] = self._glyphNameForChar(leftChar)
				if rightChar not in nameCache:
					nameCache[rightChar] = self._glyphNameForChar(rightChar)
				leftName = nameCache[leftChar]
				rightName = nameCache[rightChar]
				if not leftName or not rightName:
					droppedName += 1
					continue
				leftGlyph = thisFont.glyphs[leftName]
				rightGlyph = thisFont.glyphs[rightName]
				if not leftGlyph or not rightGlyph:
					droppedGlyph += 1
					continue
				# Look up the group kern that already covers this glyph pair.
				groupValue = 0.0
				lGroup = leftGlyph.rightKerningGroup
				rGroup = rightGlyph.leftKerningGroup
				if lGroup and rGroup:
					lKey = "@MMK_L_%s" % lGroup
					rKey = "@MMK_R_%s" % rGroup
					gv = savedGroupGroup.get((lKey, rKey))
					if gv is not None and abs(gv) < 100000:
						groupValue = gv
				if abs(kernValue - groupValue) < deltaThreshold:
					droppedDelta += 1
					continue
				# Use group-glyph pair if the left glyph has a right kerning group,
				# otherwise fall back to glyph-glyph.
				leftKey = ("@MMK_L_%s" % lGroup) if lGroup else leftName
				thisFont.setKerningForPair(masterID, leftKey, rightName, kernValue)
				count += 1

			# Restore any group-group pairs that setKerningForPair may have overwritten
			# (e.g. when Glyphs resolves a glyph name to its kerning group key).
			currentKerning = thisFont.kerning.get(masterID) or {}
			for (leftID, rightID), val in savedGroupGroup.items():
				if currentKerning.get(leftID, {}).get(rightID) != val:
					thisFont.setKerningForPair(masterID, leftID, rightID, val)
					restoredCount += 1
		finally:
			thisFont.enableUpdateInterface()
		if restoredCount:
			print("\t♻️ Restored %i group-group pairs overwritten during exception import." % restoredCount)

		print("\t↔️ Imported %i exception kern pairs for master ‘%s’." % (count, master.name))
		print("\t   (raw: %i | zero/rounded-to-zero: %i | unresolved name: %i | glyph not in font: %i | delta < %g: %i)" % (
			totalRaw, droppedZero, droppedName, droppedGlyph, deltaThreshold, droppedDelta))
		return count

	# ------------------------------------------------------------------ step 5

	def _kerningNameForID(self, thisFont, kerningID, nameCache):
		"""Resolve an internal glyph ID for the kerning API, caching the lookup."""
		if kerningID.startswith("@"):
			return kerningID
		if kerningID not in nameCache:
			glyph = thisFont.glyphForId_(kerningID)
			nameCache[kerningID] = glyph.name if glyph else None
		return nameCache[kerningID]

	def _roundAndFilter(self, thisFont, master, roundBy, minimumKern):
		"""
		For every kern pair in the given master:
		  • round to nearest multiple of roundBy (if > 0)
		  • remove the pair if |value| < minimumKern
		Returns the number of pairs removed.
		"""
		masterID = master.id
		kerning = thisFont.kerning.get(masterID)
		if not kerning:
			return 0

		updates = []
		removals = []
		for leftID, rightDict in kerning.items():
			for rightID, value in rightDict.items():
				newValue = value
				if roundBy > 0:
					newValue = round(value / roundBy) * roundBy
				if abs(newValue) < minimumKern:
					removals.append((leftID, rightID))
				elif newValue != value:
					updates.append((leftID, rightID, newValue))

		nameCache = {}
		for leftID, rightID, newValue in updates:
			leftName = self._kerningNameForID(thisFont, leftID, nameCache)
			rightName = self._kerningNameForID(thisFont, rightID, nameCache)
			if leftName and rightName:
				thisFont.setKerningForPair(masterID, leftName, rightName, newValue)
		for leftID, rightID in removals:
			leftName = self._kerningNameForID(thisFont, leftID, nameCache)
			rightName = self._kerningNameForID(thisFont, rightID, nameCache)
			if leftName and rightName:
				thisFont.removeKerningForPair(masterID, leftName, rightName)

		print("\t☑️ Round/filter: removed %i pairs below minimum in master ‘%s’." % (len(removals), master.name))
		return len(removals)

	def _compressKerning(self, thisFont, master):
		"""
		Compress glyph pairs to group kerning in one planned pass. A pair is
		promotable when:
		  - both sides are glyph IDs (not group keys)
		  - the glyph has kerning groups on both sides
		  - value matches the existing group-group value (or there is none yet)
		Returns the total number of pairs promoted.
		"""
		masterID = master.id
		kerning = thisFont.kerning.get(masterID, {})
		groupValues = {}
		for leftID, rightDict in kerning.items():
			if not leftID.startswith("@"):
				continue
			for rightID, value in rightDict.items():
				if rightID.startswith("@"):
					groupValues[(leftID, rightID)] = value

		glyphCache = {}
		groupPairsToSet = []
		toPromote = []
		missing = object()
		for leftID, rightDict in kerning.items():
			if leftID.startswith("@"):
				continue
			if leftID not in glyphCache:
				glyphCache[leftID] = thisFont.glyphForId_(leftID)
			leftGlyph = glyphCache[leftID]
			if not leftGlyph or not leftGlyph.rightKerningGroup:
				continue
			lKey = "@MMK_L_%s" % leftGlyph.rightKerningGroup
			for rightID, value in rightDict.items():
				if rightID.startswith("@"):
					continue
				if rightID not in glyphCache:
					glyphCache[rightID] = thisFont.glyphForId_(rightID)
				rightGlyph = glyphCache[rightID]
				if not rightGlyph or not rightGlyph.leftKerningGroup:
					continue
				rKey = "@MMK_R_%s" % rightGlyph.leftKerningGroup
				groupKey = (lKey, rKey)
				groupValue = groupValues.get(groupKey, missing)
				if groupValue is missing or groupValue is None or groupValue > 100000:
					groupValues[groupKey] = value
					groupPairsToSet.append((lKey, rKey, value))
					toPromote.append((leftGlyph.name, rightGlyph.name))
				elif groupValue == value:
					toPromote.append((leftGlyph.name, rightGlyph.name))

		for leftKey, rightKey, value in groupPairsToSet:
			thisFont.setKerningForPair(masterID, leftKey, rightKey, value)
		for leftName, rightName in toPromote:
			thisFont.removeKerningForPair(masterID, leftName, rightName)
		totalPromoted = len(toPromote)
		if totalPromoted:
			print("\t☑️ Compressed %i pairs to %i group kernings in master ‘%s’." % (totalPromoted, len(groupPairsToSet), master.name))
		return totalPromoted

	def _removeExceptions(self, thisFont, master):
		"""
		Remove all non-group-to-group kerning pairs (glyph↔glyph, group↔glyph, glyph↔group).
		"""
		masterID = master.id
		kerning = thisFont.kerning.get(masterID, {})
		removals = []
		for leftID, rightDict in kerning.items():
			for rightID in rightDict.keys():
				if leftID.startswith("@") and rightID.startswith("@"):
					continue  # keep group-group
				removals.append((leftID, rightID))
		nameCache = {}
		for leftID, rightID in removals:
			leftName = self._kerningNameForID(thisFont, leftID, nameCache)
			rightName = self._kerningNameForID(thisFont, rightID, nameCache)
			if leftName and rightName:
				thisFont.removeKerningForPair(masterID, leftName, rightName)
		print("\t☑️ Removed %i exceptions in master ‘%s’." % (len(removals), master.name))
		return len(removals)

	def _deleteAllKerningForMaster(self, thisFont, master):
		"""Remove every kern pair for the given master via removeKerningForPair."""
		masterID = master.id
		kerning = thisFont.kerning.get(masterID, {})
		removals = []
		for leftID, rightDict in kerning.items():
			for rightID in rightDict.keys():
				removals.append((leftID, rightID))
		nameCache = {}
		thisFont.disableUpdateInterface()
		try:
			for leftID, rightID in removals:
				leftName = self._kerningNameForID(thisFont, leftID, nameCache)
				rightName = self._kerningNameForID(thisFont, rightID, nameCache)
				if leftName and rightName:
					thisFont.removeKerningForPair(masterID, leftName, rightName)
		finally:
			thisFont.enableUpdateInterface()
		print("\t🗑 Deleted %i existing kern pairs for master ‘%s’." % (len(removals), master.name))
		return len(removals)

	# ------------------------------------------------------------------ step 6

	def _closeInDesignDoc(self):
		"""Close the frontmost InDesign document without saving."""
		script = """
tell application id "com.adobe.InDesign"
	set docs to every document whose name contains "Steal Kerning"
	if (count of docs) > 0 then
		repeat with myDoc in docs
			close myDoc saving no
		end repeat
	end if
end tell
true
"""
		self._runAppleScript(script)

	def _deleteFonts(self, exportedMasters):
		"""Delete all temporary OTF files that were exported."""
		for master, filePath in exportedMasters:
			try:
				if os.path.exists(filePath):
					os.remove(filePath)
					print("\t🗑 Deleted: %s" % filePath)
			except Exception as e:
				print("\t⚠️ Could not delete %s: %s" % (filePath, e))

	def _waitForFont(self, familyName, timeoutSeconds=30):
		"""
		Poll InDesign until familyName is available or timeoutSeconds elapses.
		Calls 'update fonts' each iteration so InDesign rescans for new activations.
		Returns True if the font became available, False if timed out.
		"""
		script = """
tell application id "com.adobe.InDesign"
	update fonts
	set matched to every font whose font family is "%s"
	if (count of matched) > 0 then
		return "yes"
	end if
	return "no"
end tell
""" % familyName
		elapsed = 0
		interval = 2
		while elapsed <= timeoutSeconds:
			result = self._runAppleScript(script)
			if result == "yes":
				print("\t👍 Temporary font ‘%s’ available in InDesign after %is." % (familyName, elapsed))
				return True
			print("\t⏱️ Waiting for font activation… (%is)" % elapsed)
			time.sleep(interval)
			elapsed += interval
		return False

	# ------------------------------------------------------------------ run

	def run(self, sender=None):
		self.SavePreferences()
		thisFont = Glyphs.font
		if not thisFont:
			self.w.status.set("⚠️ No font open.")
			return

		startTime = time.time()
		Glyphs.clearLog()
		print("Steal Kerning from InDesign")

		# Determine which masters to process
		if self.prefBool("allMasters"):
			masters = list(thisFont.masters)
		else:
			masters = [thisFont.selectedFontMaster]

		# Progress tracking: 5 per-master steps + 2 global steps (wait + cleanup)
		# If addExceptions is on, one extra per-master step for the exception pass
		doExceptions = self.prefBool("addExceptions")
		totalSteps = 5 * len(masters) + 2 + (len(masters) if doExceptions else 0)
		progressStep = [0]

		self.w.progressBar.show(True)

		def advance():
			progressStep[0] += 1
			self.w.progressBar.set(progressStep[0] / totalSteps * 100)

		self.w.progressBar.set(0)

		# --- Step 1: export ---
		self.w.status.set("⚙️ Exporting fonts…")
		print("\nStep 1 – Exporting masters to Adobe Fonts folder…")
		exportedMasters = self._exportMasters(thisFont, masters)
		if not exportedMasters:
			failedMasterNames = ", ".join(master.name for master in masters)
			self.w.status.set("❌ All font exports failed. See Macro Window.")
			print("\n❌ No temporary fonts were exported. Stopping before opening InDesign.")
			print("\tFailed masters: %s" % failedMasterNames)
			print("\tDestination: %s" % self._adobeFontsFolder())
			Glyphs.showMacroWindow()
			Message(
				title="Temporary Font Export Failed",
				message="None of the selected masters could be exported, so InDesign was not opened.\n\nFailed masters: %s\n\nSee the Macro Window for details." % failedMasterNames,
				OKButton="OK",
			)
			return
		print(f"\t📥 Exported {len(exportedMasters)} master{'s' if len(exportedMasters) != 1 else ''}.")
		for _ in exportedMasters:
			advance()

		# Poll InDesign until Kernstealer font is activated (up to 30s)
		self.w.status.set("⏱️ Waiting for font activation…")
		if not self._waitForFont("Kernstealer"):
			self.w.status.set("❌ Font activation timed out.")
			print("\t❌ 'Kernstealer' was not activated in InDesign within 30 seconds.")
			self._deleteFonts(exportedMasters)
			return
		advance()

		# Detect InDesign UI language once, for localized "optical" kerning string
		opticalStr = self._getOpticalKerningString()

		# --- Step 2: InDesign doc + kern readout (per master) ---
		self.w.status.set("👨‍🎨 Creating InDesign document…")
		print("\nStep 2 – Reading kerning from InDesign…")

		# If zeroPair is a 3+ digit all-digit string, treat it as a fixed font size
		# and skip calibration (e.g. "009" → 9 pt, "100" → 100 pt).
		zeroPair = self.pref("zeroPair") or "HH"
		fixedFontSize = None
		if len(zeroPair) >= 3 and zeroPair.isdigit():
			fixedFontSize = float(int(zeroPair))
			print("\t📐 Fixed font size: %g pt (calibration skipped)." % fixedFontSize)

		# calibrationSizes maps master → calibrated pt size
		calibrationSizes = {}

		# Read minimumKern now so it can be passed into the AppleScript read step
		try:
			minimumKern = float(self.pref("minimumKern"))
		except (TypeError, ValueError):
			minimumKern = 0.0
		try:
			roundBy = float(self.pref("roundBy"))
		except (TypeError, ValueError):
			roundBy = 0.0

		for master, filePath in exportedMasters:
			styleName = self._sanitizeName(master.name) or ("Master%i" % list(thisFont.masters).index(master))
			self.w.status.set("👩‍🔬 Calibrating ‘%s’…" % master.name)
			ok = self._createInDesignDoc("Kernstealer", styleName, opticalStr)
			if not ok:
				print("\t❌ Could not create InDesign document for master ‘%s’." % master.name)
				continue
			if fixedFontSize is not None:
				calibSize = fixedFontSize
				print("\n\t↔️ Master ‘%s’: using fixed font size %g pt." % (master.name, calibSize))
			else:
				calibSize = self._calibrateFontSize(styleName)
				print("\n\t↔️ Master ‘%s’ calibrated at %.1f pt" % (master.name, calibSize))
			calibrationSizes[master.name] = calibSize
			advance()

			if self.prefBool("deleteExistingKerning"):
				self._deleteAllKerningForMaster(thisFont, master)

			print("\t💬 Preparing pairings for master ‘%s’..." % master.name)
			expectedPairs = self._buildPairs(thisFont)
			if not expectedPairs:
				self.w.status.set("⚠️ No pairs to kern.")
				return
			pairText = " ".join("%s%s" % pair for pair in expectedPairs)

			self.w.status.set("🖼️ Filling frame ‘%s’…" % master.name)
			ok = self._setInDesignTextAndFont(pairText, styleName, calibSize, opticalStr)
			if ok:
				print("\t✅ Text frame filled for master ‘%s’." % master.name)
			else:
				print("\t❌ Failed to fill text frame for master ‘%s’." % master.name)
			advance()

			pairCount = len(expectedPairs)
			totalImported = 0

			self.w.status.set("📖 Reading %i kern pairs, may take a while…" % pairCount)
			n = self._importKerningForMaster(thisFont, master, expectedPairs, minimumKern, roundBy)
			totalImported += n
			advance()

			# close InD document
			closeScript = """
tell application id "com.adobe.InDesign"
	if (count documents) > 0 then
		close front document saving no
	end if
end tell
true
"""
			self._runAppleScript(closeScript)

			print("\t📈 Total pairs imported: %i" % totalImported)

		# --- Step 3: round, filter, compress, remove exceptions ---
		print("\nStep 3 – Post-processing kern pairs…")
		groupKerningOnly = self.prefBool("groupKerningOnly")

		doCompressKerning = self.prefBool("compressKerning")

		postProcessStart = time.time()

		for master, filePath in exportedMasters:
			self.w.status.set("🛠️ Post-processing ‘%s’…" % master.name)
			thisFont.disableUpdateInterface()
			try:
				self._roundAndFilter(thisFont, master, roundBy, minimumKern)
				if doCompressKerning:
					self._compressKerning(thisFont, master)
					if groupKerningOnly:
						self._removeExceptions(thisFont, master)
			finally:
				thisFont.enableUpdateInterface()
			advance()

		print("\t⏱ Post-processing finished in %.2fs." % (time.time() - postProcessStart))

		# --- Step 4: exception kerning (optional) ---
		print("\nStep 4 – Adding exception kerning for diacritic pairs…")
		if not doExceptions:
			print("\t⏭️ Skipped.")
		else:
			exPairs = self._buildExceptionPairText(thisFont)
			if exPairs:
				exPairText = " ".join("%s%s" % (l, r) for l, r in exPairs)
				for master, filePath in exportedMasters:
					if master.name not in calibrationSizes.keys():
						continue
					styleName, calibSize = master.name, calibrationSizes[master.name]
					self.w.status.set("💕 Exception pairs for ‘%s’…" % master.name)

					ok = self._createInDesignDoc("Kernstealer", styleName, opticalStr)
					if not ok:
						print("\t❌ Could not create InDesign document for master ‘%s’." % master.name)
						continue
					ok = self._setInDesignTextAndFont(exPairText, styleName, calibSize, opticalStr)
					if not ok:
						print("\t❌ Failed to fill exception frame for master ‘%s’." % master.name)
						advance()
						continue
					n = self._importExceptionKerningForMaster(thisFont, master, exPairs, minimumKern, roundBy)
					print("\t☑️ Added %i exceptions for master ‘%s’." % (n, master.name))
					advance()

					self._closeInDesignDoc()

		# --- Step 5: cleanup ---
		print("\nStep 5 – Cleanup…")
		self.w.status.set("🧹 Cleaning up…")
		self._closeInDesignDoc() # just in case
		self._deleteFonts(exportedMasters)
		advance()

		# Final count of kern pairs across all processed masters
		finalPairCount = sum(
			sum(len(rDict) for rDict in thisFont.kerning.get(m.id, {}).values())
			for m, _ in exportedMasters
		)
		masterWord = "master" if len(exportedMasters) == 1 else "masters"
		elapsed = reportTimeInNaturalLanguage(time.time() - startTime)
		summary = "\n✅ %i kern pairs in %i %s. %s." % (finalPairCount, len(exportedMasters), masterWord, elapsed)
		self.w.status.set(summary)
		print(summary)
		self.w.progressBar.set(0)
		self.w.progressBar.show(False)
		Glyphs.showNotification("Steal Kerning from InDesign", summary.replace("✅", "").strip())


StealKerningFromInDesign()
