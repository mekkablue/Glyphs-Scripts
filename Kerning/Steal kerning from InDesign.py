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
from mekkablue import mekkaObject, reportTimeInNaturalLanguage
from GlyphsApp import Glyphs


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
		"groupKerningOnly": 0,
		"deleteExistingKerning": 0,
		"compressKerning": 1,
		"allMasters": 1,
	}

	def __init__(self):
		windowWidth = 480
		windowHeight = 286
		windowWidthResize = 0
		windowHeightResize = 0
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Steal Kerning from InDesign",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),
			autosaveName=self.domain("mainwindow"),
		)

		linePos, inset, lineHeight = 12, 15, 22

		# No-kern pair + Min kern + Round by — all on one row
		self.w.zeroPairLabel = vanilla.TextBox((inset, linePos + 3, 84, 14), "No-kern pair:", sizeStyle="small")
		self.w.zeroPair = vanilla.EditText((inset + 84, linePos, 40, 19), "HH", callback=self.SavePreferences, sizeStyle="small")
		self.w.zeroPair.getNSTextField().setToolTip_("A pair of glyphs that should have zero optical kerning (i.e., the reference pair used to calibrate the font size for measurement).")
		self.w.minimumKernLabel = vanilla.TextBox((inset + 136, linePos + 3, 57, 14), "Min kern:", sizeStyle="small")
		self.w.minimumKern = vanilla.EditText((inset + 193, linePos, 40, 19), "10", callback=self.SavePreferences, sizeStyle="small")
		self.w.minimumKern.getNSTextField().setToolTip_("Discard imported kern pairs whose absolute value is smaller than this threshold.")
		self.w.roundByLabel = vanilla.TextBox((inset + 245, linePos + 3, 58, 14), "Round by:", sizeStyle="small")
		self.w.roundBy = vanilla.EditText((inset + 303, linePos, 40, 19), "5", callback=self.SavePreferences, sizeStyle="small")
		self.w.roundBy.getNSTextField().setToolTip_("Round imported kern values to this multiple (e.g. 5 = multiples of 5). Set to 1 or 0 to skip rounding.")
		linePos += lineHeight

		self.w.divider1 = vanilla.HorizontalLine((inset, linePos + 3, -inset, 1))
		linePos += int(lineHeight * 0.6)

		# Pair type checkboxes — three columns
		self.w.letterToLetter = vanilla.CheckBox((inset + 2, linePos - 1, 148, 20), "Letter to Letter", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.letterToLetter.getNSButton().setToolTip_("Kern pairs between uppercase and lowercase letters.")
		self.w.figureToFigure = vanilla.CheckBox((inset + 150, linePos - 1, 150, 20), "Figure to Figure", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.figureToFigure.getNSButton().setToolTip_("Kern pairs between decimal digit figures.")
		self.w.letterToFigure = vanilla.CheckBox((inset + 300, linePos - 1, -inset, 20), "Letter to Figure", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.letterToFigure.getNSButton().setToolTip_("Kern pairs between letters and figures (both directions).")
		linePos += lineHeight

		self.w.letterWithPunctuation = vanilla.CheckBox((inset + 2, linePos - 1, 148, 20), "Letter with Punctuation", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.letterWithPunctuation.getNSButton().setToolTip_("Kern pairs between letters and punctuation marks (both directions).")
		self.w.figureWithPunctuation = vanilla.CheckBox((inset + 150, linePos - 1, 150, 20), "Figure with Punctuation", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.figureWithPunctuation.getNSButton().setToolTip_("Kern pairs between figures and punctuation marks (both directions).")
		self.w.punctuationWithItself = vanilla.CheckBox((inset + 300, linePos - 1, -inset, 20), "Punctuation with itself", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.punctuationWithItself.getNSButton().setToolTip_("Kern pairs between punctuation marks and other punctuation marks.")
		linePos += lineHeight

		self.w.divider2 = vanilla.HorizontalLine((inset, linePos + 3, -inset, 1))
		linePos += int(lineHeight * 0.6)

		# Options
		self.w.allMasters = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "All masters (otherwise current master only)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.allMasters.getNSButton().setToolTip_("Process all masters in the font. If off, only the currently selected master is processed.")
		linePos += lineHeight

		self.w.deleteExistingKerning = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Delete existing kerning before import", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.deleteExistingKerning.getNSButton().setToolTip_("Clear all existing kerning for each master before importing new values from InDesign.")
		linePos += lineHeight

		self.w.compressKerning = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Compress kerning (glyph pairs → group pairs)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.compressKerning.getNSButton().setToolTip_("Promote glyph-to-glyph kern pairs to the corresponding group-to-group pair when the value matches.")
		linePos += lineHeight

		self.w.groupKerningOnly = vanilla.CheckBox((inset + 22, linePos - 1, -inset, 20), "Keep group kerning only", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.groupKerningOnly.getNSButton().setToolTip_("After compressing, delete all remaining glyph-to-glyph pairs. Note: compressing cannot always convert every glyph pair to a group pair (e.g. when a glyph has no kerning group), so some pairs may remain.")
		linePos += lineHeight

		# Progress bar + Status + Run button
		self.w.progressBar = vanilla.ProgressBar((inset, -42 - inset, -inset, 16))
		self.w.status = vanilla.TextBox((inset, -18 - inset, -80 - inset, 14), "Ready.", sizeStyle="small", selectable=True)
		self.w.runButton = vanilla.Button((-70 - inset, -20 - inset, -inset, -inset), "Kern", callback=self.run)
		self.w.setDefaultButton(self.w.runButton)

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
		self.w.groupKerningOnly.enable(bool(self.w.compressKerning.get()))

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
		Returns a list of (master, filePath) tuples.
		"""
		adobeFontsFolder = self._adobeFontsFolder()
		exported = []

		for master in masters:
			styleName = self._sanitizeName(master.name) or ("Master%i" % masters.index(master))
			fileName = "Kernstealer-%s.otf" % styleName.replace(" ", "")
			filePath = os.path.join(adobeFontsFolder, fileName)

			# Build a temporary single-master font copy
			import copy
			tempFont = thisFont.copy()
			tempFont.familyName = "Kernstealer"

			# Keep only the matching master; set its name as the style
			masterIdToKeep = master.id
			# Find the matching master in the copy (same index)
			masterIndex = list(thisFont.masters).index(master)
			tempMaster = tempFont.masters[masterIndex]
			tempMaster.name = styleName
			tempMaster.customParameters["preferredSubfamilyName"] = styleName
			tempMaster.customParameters["postscriptSlantAngle"] = 0

			# Remove other masters
			mastersToRemove = [m for m in tempFont.masters if m != tempMaster]
			for m in mastersToRemove:
				tempFont.removeMaster_(m)

			# Export as OTF
			exportOptions = {
				"ExportFormatKey": "OTF",
				"ExportDestinationKey": adobeFontsFolder,
				"AutoHintKey": False,
				"RemoveOverlapsKey": True,
			}
			ok = tempFont.export(format="OTF", fontPath=filePath)
			if ok:
				print("\t✅ Exported: %s → %s" % (master.name, filePath))
				exported.append((master, filePath))
			else:
				print("\t❌ Export failed for master: %s" % master.name)

		return exported

	# ------------------------------------------------------------------ step 2

	def _getInDesignName(self):
		"""Return the running InDesign application name (auto-detect or ask user)."""
		Glyphs.registerDefault("com.mekkablue.StealKerningFromInDesign.indesignAppName", "Adobe InDesign")
		storedName = Glyphs.defaults["com.mekkablue.StealKerningFromInDesign.indesignAppName"]
		script = """
try
	set InDesign to application "%s"
on error
	set InDesign to choose application with title "Please choose Adobe InDesign"
end try
InDesign as string
""" % storedName
		name = self._runAppleScript(script)
		if name and name != storedName:
			Glyphs.defaults["com.mekkablue.StealKerningFromInDesign.indesignAppName"] = name
		return name or storedName

	def _createInDesignDoc(self, indesign, familyName, styleName):
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
tell application "%s"
	set myDoc to make new document
	tell myDoc
		tell document preferences
			set page width to 1190.55
			set page height to 841.89
			set pages per document to 1
			set facing pages to false
		end tell
		set myFrame to make new text frame with properties {geometric bounds:{0, 0, 841.89, 1190.55}}
		set contents of myFrame to "%s"
		tell parent story of myFrame
			set point size to 3
			set applied font to ("Kernstealer" & tab & "%s")
			set kerning method to "optical"
		end tell
	end tell
end tell
true
""" % (indesign, zeroPairAS, styleName)
		result = self._runAppleScript(script)
		return bool(result)

	def _calibrateFontSize(self, indesign, styleName):
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
tell application "%s"
	tell front document
		zoom first layout window given fit page
		tell first text frame
			tell parent story
				set kernVal to 10000
				repeat while kernVal > 0
					set point size to point size + 1
					tell character 1 to set kernVal to kerning value of insertion point 2
				end repeat
				return (point size as string) & ";" & (kernVal as integer)
			end tell
		end tell
	end tell
end tell
""" % indesign

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
tell application "%s"
	tell front document
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
""" % indesign

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

		print("\t☑️ Calibrated font size: %.1f pt (kern delta %.2f)" % (bestSize, bestAbsKern))
		return bestSize

	# ------------------------------------------------------------------ step 3

	def _glyphsForCategory(self, thisFont, category, subcategory=None):
		"""
		Return exporting GSGlyph objects matching category (and optional subcategory).
		Skips glyphs with no Unicode and glyphs made of 2+ components (can't be typed reliably).
		"""
		result = []
		for glyph in thisFont.glyphs:
			if not glyph.export:
				continue
			if not glyph.unicode:
				continue
			if glyph.name == "jdotless":
				continue
			if glyph.category != category:
				continue
			if subcategory and glyph.subCategory != subcategory:
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

	def _buildPairText(self, thisFont):
		"""
		Build a string of all requested pair combinations as '/glyphname/glyphname ' sequences.
		Groupings are driven by user checkboxes.
		Returns the pair text string.
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

		# collect unique pairs as (leftName, rightName)
		pairs = []
		seen = set()

		def addPair(left, right):
			key = (left, right)
			if key not in seen:
				seen.add(key)
				pairs.append(key)

		if doLetterToLetter:
			for L in letters:
				for R in letters:
					addPair(L, R)

		if doFigureToFigure:
			for L in figures:
				for R in figures:
					addPair(L, R)

		if doLetterToFigure:
			for L in letters:
				for R in figures:
					addPair(L, R)
			for L in figures:
				for R in letters:
					addPair(L, R)

		if doLetterWithPunctuation:
			for L in letters:
				for R in punctuation:
					addPair(L, R)
			for L in punctuation:
				for R in letters:
					addPair(L, R)

		if doFigureWithPunctuation:
			for L in figures:
				for R in punctuation:
					addPair(L, R)
			for L in punctuation:
				for R in figures:
					addPair(L, R)

		if doPunctuationWithItself:
			for L in punctuation:
				for R in punctuation:
					addPair(L, R)

		# build the pair text string
		pairText = " ".join("%s%s" % (l, r) for l, r in pairs)
		print("\t☑️ %i pairs to measure." % len(pairs))
		return pairText

	def _setInDesignTextAndFont(self, indesign, pairText, styleName, calibSize):
		"""
		Replace the text frame content with pairText, set the font and
		calibrated point size with optical kerning on every character.
		"""
		# Escape the slash-name string for AppleScript (no special chars expected)
		pairTextAS = pairText.replace("\\", "\\\\").replace('"', '\\"')
		script = """
tell application "%s"
	tell front document
		set contents of first text frame to "%s"
		tell parent story of first text frame
			set point size to %s
			set applied font to ("Kernstealer" & tab & "%s")
			set kerning method to "optical"
		end tell
	end tell
end tell
true
""" % (indesign, pairTextAS, calibSize, styleName)
		return bool(self._runAppleScript(script))

	# ------------------------------------------------------------------ step 4

	# Character descriptions InDesign sometimes returns instead of the literal char
	_REPLACEMENTS = {
		"bullet character": "•",
		"copyright symbol": "©",
		"double left quote": "\u201c",
		"double right quote": "\u201d",
		"ellipsis character": "\u2026",
		"Em dash": "\u2014",
		"En dash": "\u2013",
		"nonbreaking space": "\u00a0",
		"section symbol": "\u00a7",
		"single left quote": "\u2018",
		"single right quote": "\u2019",
		"trademark symbol": "\u2122",
	}

	def _glyphNameForChar(self, char):
		"""Return the Glyphs glyph name for a single Unicode character, or None."""
		if not char:
			return None
		utf16 = "%.4X" % ord(char[0])
		info = Glyphs.glyphInfoForUnicode(utf16)
		if info:
			return info.name
		return None

	def _cleanText(self, text):
		for searchFor, replaceWith in self._REPLACEMENTS.items():
			text = text.replace(searchFor, replaceWith)
		return text

	def _readKernValuesFromInDesign(self, indesign):
		"""
		Read all insertion-point kern values from the front InDesign document in one shot.
		Builds the full list inside AppleScript and returns it as an AppleScript list;
		avoids per-character round-trips for a significant speed boost.
		Returns a list of (leftChar, rightChar, kernValue) tuples.
		"""
		script = """
tell application "%s"
	tell front document
		tell parent story of first text frame
			set numChars to count of characters
			set kernPairs to {}
			repeat with x from 1 to (numChars - 1)
				try
					set charX to character x
					set charNext to character (x + 1)
					if (charX & charNext) does not contain " " then
						set kernValue to kerning value of insertion point 2 of character x
						set end of kernPairs to {charX, charNext, kernValue}
					end if
				end try
			end repeat
			return kernPairs
		end tell
	end tell
end tell
""" % indesign
		raw = self._runAppleScript(script)
		if not raw:
			return []
		return self._parseKernPairs(raw)

	def _parseKernPairs(self, output):
		"""
		Parse osascript's AppleScript list output into a list of (leftChar, rightChar, kernValue) tuples.
		Handles two formats returned by InDesign depending on context:
		  Nested: {{A, B, -1.0}, {T, A, -50.0}, …}
		  Flat:   A, B, -1.0, T, A, -50.0, …
		Applies _cleanText to handle InDesign's descriptive names for special characters.
		"""
		text = output.strip()
		if text.startswith("{") and text.endswith("}"):
			text = text[1:-1]
		pairs = []
		# Try nested format first: inner {char, char, value} triples
		triples = re.findall(r"\{([^{}]+)\}", text)
		if triples:
			for triple in triples:
				parts = [p.strip() for p in triple.split(",")]
				if len(parts) != 3:
					continue
				char1, char2, kernStr = parts
				char1 = self._cleanText(char1.strip('"'))
				char2 = self._cleanText(char2.strip('"'))
				try:
					kernVal = float(kernStr)
				except ValueError:
					kernVal = 0.0
				pairs.append((char1, char2, kernVal))
			return pairs
		# Flat format: char, char, value, char, char, value, …
		items = [p.strip() for p in text.split(",")]
		for i in range(0, len(items) - 2, 3):
			char1 = self._cleanText(items[i].strip('"'))
			char2 = self._cleanText(items[i + 1].strip('"'))
			try:
				kernVal = float(items[i + 2])
			except ValueError:
				kernVal = 0.0
			pairs.append((char1, char2, kernVal))
		return pairs

	def _importKerningForMaster(self, thisFont, master, indesign):
		"""
		Read kern values from InDesign and set them in thisFont for the given master.
		Returns the number of pairs imported.
		"""
		masterID = master.id
		kernPairs = self._readKernValuesFromInDesign(indesign)
		count = 0
		for leftChar, rightChar, kernValue in kernPairs:
			if kernValue == 0:
				continue
			leftName = self._glyphNameForChar(leftChar)
			rightName = self._glyphNameForChar(rightChar)
			if not leftName or not rightName:
				continue
			if not thisFont.glyphs[leftName] or not thisFont.glyphs[rightName]:
				continue
			thisFont.setKerningForPair(masterID, leftName, rightName, kernValue)
			count += 1
		print("\t↔️ Imported %i raw kern pairs for master '%s'." % (count, master.name))
		return count

	# ------------------------------------------------------------------ step 5

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

		removals = []
		for leftID, rightDict in kerning.items():
			for rightID, value in rightDict.items():
				newValue = value
				if roundBy > 0:
					newValue = round(value / roundBy) * roundBy
				if abs(newValue) < minimumKern:
					removals.append((leftID, rightID))
				elif newValue != value:
					# resolve IDs to names for setKerningForPair
					leftName = leftID if leftID.startswith("@") else thisFont.glyphForId_(leftID).name
					rightName = rightID if rightID.startswith("@") else thisFont.glyphForId_(rightID).name
					thisFont.setKerningForPair(masterID, leftName, rightName, newValue)

		for leftID, rightID in removals:
			leftName = leftID if leftID.startswith("@") else thisFont.glyphForId_(leftID).name
			rightName = rightID if rightID.startswith("@") else thisFont.glyphForId_(rightID).name
			thisFont.removeKerningForPair(masterID, leftName, rightName)

		print("\t☑️ Round/filter: removed %i pairs below minimum in master '%s'." % (len(removals), master.name))
		return len(removals)

	def _compressKerning(self, thisFont, master):
		"""
		Repeatedly compress (promote glyph exceptions to group kerning) until
		nothing changes.  A pair is promotable when:
		  - both sides are glyph IDs (not group keys)
		  - the glyph has kerning groups on both sides
		  - value matches the existing group-group value (or there is none yet)
		Returns the total number of pairs promoted.
		"""
		masterID = master.id
		totalPromoted = 0
		while True:
			kerning = thisFont.kerning.get(masterID, {})
			toPromote = []
			for leftID in list(kerning.keys()):
				leftIsGlyph = not leftID.startswith("@")
				for rightID in list(kerning.get(leftID, {}).keys()):
					rightIsGlyph = not rightID.startswith("@")
					if not (leftIsGlyph and rightIsGlyph):
						continue
					leftGlyph = thisFont.glyphForId_(leftID)
					rightGlyph = thisFont.glyphForId_(rightID)
					if not leftGlyph or not rightGlyph:
						continue
					lGroup = leftGlyph.rightKerningGroup
					rGroup = rightGlyph.leftKerningGroup
					if not lGroup or not rGroup:
						continue
					lKey = "@MMK_L_%s" % lGroup
					rKey = "@MMK_R_%s" % rGroup
					value = kerning[leftID][rightID]
					groupValue = thisFont.kerningForPair(masterID, lKey, rKey)
					# promote: set group-group if not already set or matching
					if groupValue is None or groupValue > 100000:
						thisFont.setKerningForPair(masterID, lKey, rKey, value)
						toPromote.append((leftGlyph.name, rightGlyph.name))
					elif groupValue == value:
						toPromote.append((leftGlyph.name, rightGlyph.name))
			if not toPromote:
				break
			for leftName, rightName in toPromote:
				thisFont.removeKerningForPair(masterID, leftName, rightName)
			totalPromoted += len(toPromote)
		if totalPromoted:
			print("\t☑️ Compressed %i pairs to group kerning in master '%s'." % (totalPromoted, master.name))
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
		for leftID, rightID in removals:
			leftName = leftID if leftID.startswith("@") else thisFont.glyphForId_(leftID).name
			rightName = rightID if rightID.startswith("@") else thisFont.glyphForId_(rightID).name
			thisFont.removeKerningForPair(masterID, leftName, rightName)
		print("\t☑️ Removed %i exceptions in master '%s'." % (len(removals), master.name))
		return len(removals)

	def _deleteAllKerningForMaster(self, thisFont, master):
		"""Remove every kern pair for the given master via removeKerningForPair."""
		masterID = master.id
		kerning = thisFont.kerning.get(masterID, {})
		removals = []
		for leftID, rightDict in kerning.items():
			for rightID in rightDict.keys():
				removals.append((leftID, rightID))
		for leftID, rightID in removals:
			leftName = leftID if leftID.startswith("@") else thisFont.glyphForId_(leftID).name
			rightName = rightID if rightID.startswith("@") else thisFont.glyphForId_(rightID).name
			thisFont.removeKerningForPair(masterID, leftName, rightName)
		print("\t🗑 Deleted %i existing kern pairs for master '%s'." % (len(removals), master.name))
		return len(removals)

	# ------------------------------------------------------------------ step 6

	def _closeInDesignDoc(self, indesign):
		"""Close the frontmost InDesign document without saving."""
		script = """
tell application "%s"
	if (count documents) > 0 then
		close front document saving no
	end if
end tell
true
""" % indesign
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

	def _waitForFont(self, indesign, familyName, timeoutSeconds=30):
		"""
		Poll InDesign until familyName is available or timeoutSeconds elapses.
		Calls 'update fonts' each iteration so InDesign rescans for new activations.
		Returns True if the font became available, False if timed out.
		"""
		script = """
tell application "%s"
	update fonts
	set matched to every font whose font family is "%s"
	if (count of matched) > 0 then
		return "yes"
	end if
	return "no"
end tell
""" % (indesign, familyName)
		elapsed = 0
		interval = 2
		while elapsed <= timeoutSeconds:
			result = self._runAppleScript(script)
			if result == "yes":
				print("  Font '%s' available after %is." % (familyName, elapsed))
				return True
			print("  Waiting for font activation… (%is)" % elapsed)
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
		print("Steal Kerning from InDesign\n")

		# Determine which masters to process
		if self.prefBool("allMasters"):
			masters = list(thisFont.masters)
		else:
			masters = [thisFont.selectedFontMaster]

		# Progress tracking: 5 per-master steps + 2 global steps (wait + cleanup)
		totalSteps = 5 * len(masters) + 2
		progressStep = [0]

		def advance():
			progressStep[0] += 1
			self.w.progressBar.set(progressStep[0] / totalSteps * 100)

		self.w.progressBar.set(0)

		# --- Step 1: export ---
		self.w.status.set("Exporting fonts…")
		print("\nStep 1 – Exporting masters to Adobe Fonts folder…")
		exportedMasters = self._exportMasters(thisFont, masters)
		if not exportedMasters:
			self.w.status.set("❌ Export failed.")
			return
		print("  Exported %i master(s).\n" % len(exportedMasters))
		for _ in exportedMasters:
			advance()

		# Locate InDesign first (needed for font availability polling)
		indesign = self._getInDesignName()
		if not indesign:
			self.w.status.set("❌ Could not find InDesign.")
			return

		# Poll InDesign until Kernstealer font is activated (up to 30s)
		self.w.status.set("Waiting for font activation…")
		if not self._waitForFont(indesign, "Kernstealer"):
			self.w.status.set("❌ Font activation timed out.")
			print("\t❌ 'Kernstealer' was not activated in InDesign within 30 seconds.")
			self._deleteFonts(exportedMasters)
			return
		advance()

		# --- Step 2: InDesign doc + calibration (per master) ---
		self.w.status.set("Creating InDesign document…")
		print("\nStep 2 – Creating InDesign document and calibrating font size…")
		print("  Using: %s" % indesign)

		# calibrationSizes maps master → calibrated pt size
		calibrationSizes = {}
		for master, filePath in exportedMasters:
			styleName = self._sanitizeName(master.name) or ("Master%i" % list(thisFont.masters).index(master))
			self.w.status.set("Calibrating '%s'…" % master.name)
			ok = self._createInDesignDoc(indesign, "Kernstealer", styleName)
			if not ok:
				print("\t❌ Could not create InDesign document for master '%s'." % master.name)
				continue
			calibSize = self._calibrateFontSize(indesign, styleName)
			calibrationSizes[master.id] = (styleName, calibSize)
			print("\t↔️ Master '%s' → %.1f pt\n" % (master.name, calibSize))
			advance()

		# --- Step 3: build pair text and fill InDesign text frame ---
		print("\nStep 3 – Building pair text and filling InDesign text frame…")
		pairText = self._buildPairText(thisFont)
		if not pairText:
			self.w.status.set("⚠️ No pairs to kern.")
			return

		# pairText is the same for all masters; only font/size changes per master
		# Store calibration data for use in step 4
		masterCalibData = calibrationSizes  # {masterId: (styleName, calibSize)}

		for master, filePath in exportedMasters:
			if master.id not in masterCalibData:
				continue
			styleName, calibSize = masterCalibData[master.id]
			self.w.status.set("Filling frame '%s'…" % master.name)
			# Re-create the InDesign document for this master (step 2 left one open;
			# close it and open a fresh one for the pair text)
			closeScript = """
tell application "%s"
	if (count documents) > 0 then
		close front document saving no
	end if
end tell
true
""" % indesign
			self._runAppleScript(closeScript)
			ok = self._createInDesignDoc(indesign, "Kernstealer", styleName)
			if not ok:
				print("\t❌ Could not re-create InDesign document for master '%s'." % master.name)
				continue
			ok = self._setInDesignTextAndFont(indesign, pairText, styleName, calibSize)
			if ok:
				print("\t✅ Text frame filled for master '%s'." % master.name)
			else:
				print("\t❌ Failed to fill text frame for master '%s'." % master.name)
			advance()

		# --- Step 4: read kern values from InDesign and import ---
		print("\nStep 4 – Reading kern values from InDesign and importing…")
		pairCount = len(pairText.split())
		totalImported = 0
		for master, filePath in exportedMasters:
			if master.id not in masterCalibData:
				continue
			self.w.status.set("Reading %i kern pairs, may take a while…" % pairCount)
			if self.prefBool("deleteExistingKerning"):
				self._deleteAllKerningForMaster(thisFont, master)
			n = self._importKerningForMaster(thisFont, master, indesign)
			totalImported += n
			advance()
		print("  Total raw pairs imported: %i\n" % totalImported)

		# --- Step 5: round, filter, compress, remove exceptions ---
		print("\nStep 5 – Post-processing kern pairs…")
		try:
			roundBy = float(self.pref("roundBy"))
		except (TypeError, ValueError):
			roundBy = 0.0
		try:
			minimumKern = float(self.pref("minimumKern"))
		except (TypeError, ValueError):
			minimumKern = 0.0
		groupKerningOnly = self.prefBool("groupKerningOnly")

		doCompressKerning = self.prefBool("compressKerning")
		for master, filePath in exportedMasters:
			self.w.status.set("Post-processing '%s'…" % master.name)
			self._roundAndFilter(thisFont, master, roundBy, minimumKern)
			if doCompressKerning:
				self._compressKerning(thisFont, master)
			if groupKerningOnly:
				self._removeExceptions(thisFont, master)
			advance()
		print("  Post-processing done.\n")

		# --- Step 6: cleanup ---
		print("\nStep 6 – Cleanup…")
		self.w.status.set("Cleaning up…")
		self._closeInDesignDoc(indesign)
		self._deleteFonts(exportedMasters)
		print("  Cleanup done.\n")
		advance()

		# Final count of kern pairs across all processed masters
		finalPairCount = sum(
			sum(len(rDict) for rDict in thisFont.kerning.get(m.id, {}).values())
			for m, _ in exportedMasters
		)
		masterWord = "master" if len(exportedMasters) == 1 else "masters"
		elapsed = reportTimeInNaturalLanguage(time.time() - startTime)
		summary = "✅ %i kernings in %i %s. %s." % (finalPairCount, len(exportedMasters), masterWord, elapsed)
		self.w.status.set(summary)
		print(summary)
		Glyphs.showNotification("Steal Kerning from InDesign", summary)


StealKerningFromInDesign()
