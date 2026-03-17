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
import vanilla
from Foundation import NSAppleScript
from mekkablue import mekkaObject
from GlyphsApp import Glyphs


class StealKerningFromInDesign(mekkaObject):
	prefDict = {
		"zeroPair": "HH",
		"roundBy": 5,
		"minimumKern": 10,
		"letterToLetter": 1,
		"figureToFigure": 1,
		"letterWithPunctuation": 1,
		"figureWithPunctuation": 1,
		"groupKerningOnly": 0,
		"allMasters": 1,
	}

	def __init__(self):
		windowWidth = 360
		windowHeight = 242
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

		# Zero pair + rounding
		self.w.zeroPairLabel = vanilla.TextBox((inset, linePos + 3, 155, 14), "Pair without kerning:", sizeStyle="small")
		self.w.zeroPair = vanilla.EditText((inset + 155, linePos, 50, 19), "HH", callback=self.SavePreferences, sizeStyle="small")
		self.w.zeroPair.getNSTextField().setToolTip_("A pair of glyphs that should have zero optical kerning (i.e., the reference pair used to calibrate the font size for measurement).")
		linePos += lineHeight

		# Round by + Minimum kern on one row
		self.w.roundByLabel = vanilla.TextBox((inset, linePos + 3, 70, 14), "Round by:", sizeStyle="small")
		self.w.roundBy = vanilla.EditText((inset + 70, linePos, 40, 19), "5", callback=self.SavePreferences, sizeStyle="small")
		self.w.roundBy.getNSTextField().setToolTip_("Round imported kern values to this multiple (e.g. 5 = multiples of 5). Set to 1 or 0 to skip rounding.")
		self.w.minimumKernLabel = vanilla.TextBox((inset + 125, linePos + 3, 100, 14), "Minimum kern:", sizeStyle="small")
		self.w.minimumKern = vanilla.EditText((inset + 225, linePos, 40, 19), "10", callback=self.SavePreferences, sizeStyle="small")
		self.w.minimumKern.getNSTextField().setToolTip_("Discard imported kern pairs whose absolute value is smaller than this threshold.")
		linePos += lineHeight

		self.w.divider1 = vanilla.HorizontalLine((inset, linePos + 3, -inset, 1))
		linePos += int(lineHeight * 0.6)

		# Pair type checkboxes
		self.w.letterToLetter = vanilla.CheckBox((inset + 2, linePos - 1, 170, 20), "Letter to Letter", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.letterToLetter.getNSButton().setToolTip_("Kern pairs between uppercase and lowercase letters.")
		self.w.figureToFigure = vanilla.CheckBox((inset + 180, linePos - 1, -inset, 20), "Figure to Figure", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.figureToFigure.getNSButton().setToolTip_("Kern pairs between decimal digit figures.")
		linePos += lineHeight

		self.w.letterWithPunctuation = vanilla.CheckBox((inset + 2, linePos - 1, 170, 20), "Letter with Punctuation", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.letterWithPunctuation.getNSButton().setToolTip_("Kern pairs between letters and punctuation marks (both directions).")
		self.w.figureWithPunctuation = vanilla.CheckBox((inset + 180, linePos - 1, -inset, 20), "Figure with Punctuation", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.figureWithPunctuation.getNSButton().setToolTip_("Kern pairs between figures and punctuation marks (both directions).")
		linePos += lineHeight

		self.w.divider2 = vanilla.HorizontalLine((inset, linePos + 3, -inset, 1))
		linePos += int(lineHeight * 0.6)

		# Options
		self.w.groupKerningOnly = vanilla.CheckBox((inset + 2, linePos - 1, 220, 20), "Group kerning only (no exceptions)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.groupKerningOnly.getNSButton().setToolTip_("If on, only sets group-to-group kerning. Removes all glyph-level exceptions after import.")
		linePos += lineHeight

		self.w.allMasters = vanilla.CheckBox((inset + 2, linePos - 1, 220, 20), "All masters (otherwise current master only)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.allMasters.getNSButton().setToolTip_("Process all masters in the font. If off, only the currently selected master is processed.")
		linePos += lineHeight

		# Status + Run button
		self.w.status = vanilla.TextBox((inset, -20 - inset, -90 - inset, 14), "Ready.", sizeStyle="small", selectable=True)
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Kern", callback=self.run)
		self.w.setDefaultButton(self.w.runButton)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		anyPairType = (
			self.w.letterToLetter.get()
			or self.w.figureToFigure.get()
			or self.w.letterWithPunctuation.get()
			or self.w.figureWithPunctuation.get()
		)
		self.w.runButton.enable(anyPairType)

	# ------------------------------------------------------------------ helpers

	def _runAppleScript(self, source, args=None):
		"""Run an AppleScript string; return its string result or True/False."""
		s = NSAppleScript.alloc().initWithSource_(source)
		result, error = s.executeAndReturnError_(None)
		if error:
			print("AppleScript Error:")
			print(error)
			print("Script:")
			for i, line in enumerate(source.splitlines()):
				print("%03i %s" % (i + 1, line))
			return False
		if result:
			return result.stringValue()
		return True

	def _sanitizeName(self, name):
		"""Keep only A-Z a-z 0-9 and space — safe for PostScript family/style names."""
		return re.sub(r"[^A-Za-z0-9 ]", "", name)

	def _adobeFontsFolder(self):
		"""Return the path to ~/Library/Application Support/Adobe/Fonts, creating it if needed."""
		path = os.path.expanduser("~/Library/Application Support/Adobe/Fonts")
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
			ok = tempFont.export(format="OTF", filePath=filePath)
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
		script = """
tell application "%s"
	set myDoc to make new document with properties {document preferences:{page width:841.89, page height:595.28, pages per document:1, facing pages:false}}
	tell myDoc
		set documentPreferences to document preferences
		set documentPreferences's page orientation to landscape
		-- create a text frame filling the page
		set myFrame to make new text frame with properties {geometric bounds:{0, 0, 595.28, 841.89}}
		tell myFrame
			tell text preferences
				set optical margin alignment to false
			end tell
			set content to "%s"
			tell character 1 of parent story
				set point size to 3
				set applied font to "Kernstealer\\t%s"
				set kerning method to optical
			end tell
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
		# Step up by 1 pt until kern <= 0
		scriptUp = """
tell application "%s"
	tell front document
		tell first text frame
			tell character 1 of parent story
				set curSize to point size
				set kernVal to kerning value of insertion point 2
				if kernVal > 0 then
					set point size to curSize + 1
				end if
				return (point size as string) & "," & (kernVal as string)
			end tell
		end tell
	end tell
end tell
""" % indesign

		size = 3.0
		for _ in range(2000):  # safety cap: 2003 pt max
			result = self._runAppleScript(scriptUp)
			if not result or "," not in result:
				break
			parts = result.split(",")
			try:
				size = float(parts[0])
				kernVal = float(parts[1])
			except ValueError:
				break
			if kernVal <= 0:
				break

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
				size = float(parts[0])
				kernVal = float(parts[1])
			except ValueError:
				break
			if abs(kernVal) < bestAbsKern:
				bestAbsKern = abs(kernVal)
				bestSize = size
			if kernVal >= 0:
				break

		print("\t☑️ Calibrated font size: %.1f pt (kern delta %.2f)" % (bestSize, bestAbsKern))
		return bestSize

	# ------------------------------------------------------------------ run

	def run(self, sender=None):
		self.SavePreferences()
		thisFont = Glyphs.font
		if not thisFont:
			self.w.status.set("⚠️ No font open.")
			return

		Glyphs.clearLog()
		print("Steal Kerning from InDesign\n")

		# Determine which masters to process
		if self.prefBool("allMasters"):
			masters = list(thisFont.masters)
		else:
			masters = [thisFont.selectedFontMaster]

		# --- Step 1: export ---
		self.w.status.set("Exporting fonts…")
		print("Step 1 – Exporting masters to Adobe Fonts folder…")
		exportedMasters = self._exportMasters(thisFont, masters)
		if not exportedMasters:
			self.w.status.set("❌ Export failed.")
			return
		print("  Exported %i master(s).\n" % len(exportedMasters))

		# --- Step 2: InDesign doc + calibration (per master) ---
		self.w.status.set("Connecting to InDesign…")
		print("Step 2 – Creating InDesign document and calibrating font size…")
		indesign = self._getInDesignName()
		if not indesign:
			self.w.status.set("❌ Could not find InDesign.")
			return
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

		self.w.status.set("Step 2 done. Steps 3–6 not yet implemented.")


StealKerningFromInDesign()
