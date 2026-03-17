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
		self.w.status.set("Step 1 done. Steps 2–6 not yet implemented.")


StealKerningFromInDesign()
