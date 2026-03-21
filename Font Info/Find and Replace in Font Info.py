# MenuTitle: Find and Replace in Font Info
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds and replaces text in Font Info fields across Font, Masters, and Instances/Exports.
Covers both general properties (names, designer, etc.) and custom parameters (string values).
"""

import vanilla
import objc
from GlyphsApp import Glyphs, GSFontInfoValueLocalized, GSFontInfoValueSingle
from mekkablue import mekkaObject


class FindAndReplaceInFontInfo(mekkaObject):
	prefDict = {
		"searchFor": "",
		"replaceWith": "",
		"scopeFont": 1,
		"scopeMasters": 1,
		"scopeInstances": 1,
		"contentGeneral": 1,
		"contentCustomParameters": 1,
	}

	def __init__(self):
		windowWidth = 400
		windowHeight = 175
		windowWidthResize = 1000
		windowHeightResize = 0
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Find and Replace in Font Info",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),
			autosaveName=self.domain("mainwindow"),
		)

		linePos, inset, lineHeight = 12, 15, 22
		labelW = 55       # width of right-aligned "Find:" / "Replace:" labels
		fieldX = inset + labelW   # x-start of text entry fields (= 70)
		scopeLabelW = 40  # width of "Scope:"
		fontInfoLabelW = 68  # width of "Font Info →"
		checkboxX = inset + scopeLabelW + fontInfoLabelW  # x-start of all checkboxes (= 123)

		# Find row
		self.w.searchForLabel = vanilla.TextBox((inset, linePos + 2, labelW, 14), "Find:", sizeStyle="small", selectable=True, alignment="right")
		self.w.searchFor = vanilla.EditText((fieldX, linePos - 1, -inset, 19), "", callback=self.SavePreferences, sizeStyle="small")
		self.w.searchFor.setToolTip("Text to search for in the selected Font Info fields.")
		linePos += lineHeight

		# Replace row
		self.w.replaceWithLabel = vanilla.TextBox((inset, linePos + 2, labelW, 14), "Replace:", sizeStyle="small", selectable=True, alignment="right")
		self.w.replaceWith = vanilla.EditText((fieldX, linePos - 1, -inset, 19), "", callback=self.SavePreferences, sizeStyle="small")
		self.w.replaceWith.setToolTip("Replacement text. Leave empty to delete all occurrences of the search text.")
		linePos += lineHeight

		linePos += 10  # visual gap between find/replace and scope sections

		# Scope row: Scope:  Font Info →  [x] Font  [x] Masters  [x] Instances
		self.w.scopePrefixLabel = vanilla.TextBox((inset, linePos + 2, scopeLabelW, 14), "Scope:", sizeStyle="small", selectable=True)
		self.w.fontInfoLabel = vanilla.TextBox((inset + scopeLabelW, linePos + 2, fontInfoLabelW, 14), "Font Info →", sizeStyle="small", selectable=True)
		self.w.scopeFont = vanilla.CheckBox((checkboxX, linePos, 52, 20), "Font", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.scopeFont.setToolTip("Search and replace in font-level properties (Font Info > Font tab): family name, designer, manufacturer, copyright, and all other named fields.")
		self.w.scopeMasters = vanilla.CheckBox((checkboxX + 52, linePos, 75, 20), "Masters", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.scopeMasters.setToolTip("Search and replace in master properties (Font Info > Masters tab): master names and all other named fields.")
		self.w.scopeInstances = vanilla.CheckBox((checkboxX + 52 + 75, linePos, 90, 20), "Instances", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.scopeInstances.setToolTip("Search and replace in instance/export properties (Font Info > Instances or Exports tab): style names and all other named fields.")
		linePos += lineHeight

		# Content row: [x] General properties  [x] Custom parameters — aligned with Font checkbox above
		self.w.contentGeneral = vanilla.CheckBox((checkboxX, linePos, 140, 20), "General properties", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.contentGeneral.setToolTip("Search and replace in built-in Font Info fields such as family name, designer, style names, copyright, etc.")
		self.w.contentCustomParameters = vanilla.CheckBox((checkboxX + 140, linePos, -inset, 20), "Custom parameters", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.contentCustomParameters.setToolTip("Search and replace in the string values of custom parameters at the Font, Master, and Instance levels.")
		linePos += lineHeight

		# Status line — bottom-anchored, left of run button
		self.w.statusText = vanilla.TextBox((inset, -20 - inset + 3, -90 - inset - 8, 14), "Ready.", sizeStyle="small")
		self.w.statusText.setToolTip("Number of replacements made in the last run.")

		# Run button — bottom-anchored
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Replace", callback=self.run)
		self.w.runButton.setToolTip("Run find and replace on the selected scopes and content types.")
		self.w.setDefaultButton(self.w.runButton)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		hasSearchText = bool(self.w.searchFor.get())
		hasScope = bool(self.w.scopeFont.get() or self.w.scopeMasters.get() or self.w.scopeInstances.get())
		hasContent = bool(self.w.contentGeneral.get() or self.w.contentCustomParameters.get())
		self.w.runButton.enable(hasSearchText and hasScope and hasContent)

	def replaceInText(self, text, searchFor, replaceWith, label):
		"""Replace searchFor with replaceWith in text string. Returns (newText, changed)."""
		newText = text.replace(searchFor, replaceWith).strip()
		while "  " in newText:
			newText = newText.replace("  ", " ")
		if newText != text:
			print(f"\t✅ {label}: '{text}' → '{newText}'")
			return newText, True
		return text, False

	def replaceInProperties(self, obj, searchFor, replaceWith, label):
		"""Replace in .properties (GSFontInfoValueSingle / GSFontInfoValueLocalized). Returns count."""
		count = 0
		if not hasattr(obj, "properties"):
			return 0
		for prop in obj.properties:
			if isinstance(prop, GSFontInfoValueSingle):
				if prop.value and searchFor in prop.value:
					newVal, changed = self.replaceInText(prop.value, searchFor, replaceWith, f"{label} > {prop.key}")
					if changed:
						prop.value = newVal
						count += 1
			elif isinstance(prop, GSFontInfoValueLocalized):
				for entry in prop.values:
					if entry.value and searchFor in entry.value:
						newVal, changed = self.replaceInText(entry.value, searchFor, replaceWith, f"{label} > {prop.key} ({entry.languageTag})")
						if changed:
							entry.value = newVal
							count += 1
		return count

	def replaceInCustomParameters(self, obj, searchFor, replaceWith, label):
		"""Replace in string-valued custom parameters. Returns count."""
		count = 0
		for param in obj.customParameters:
			if isinstance(param.value, (objc.pyobjc_unicode, str)):
				if searchFor in param.value:
					newVal, changed = self.replaceInText(param.value, searchFor, replaceWith, f"{label} > Custom Parameters > {param.name}")
					if changed:
						param.value = newVal
						count += 1
		return count

	def run(self, sender=None):
		try:
			Glyphs.clearLog()
			self.SavePreferences()

			font = Glyphs.font
			if not font:
				self.w.statusText.set("No font open.")
				return

			searchFor = self.pref("searchFor")
			replaceWith = self.pref("replaceWith")
			scopeFont = self.prefBool("scopeFont")
			scopeMasters = self.prefBool("scopeMasters")
			scopeInstances = self.prefBool("scopeInstances")
			contentGeneral = self.prefBool("contentGeneral")
			contentCustomParameters = self.prefBool("contentCustomParameters")

			totalCount = 0
			fontName = font.familyName or "Untitled"
			print(f"Find and Replace in Font Info — '{fontName}'")
			print(f"Search: '{searchFor}'  →  Replace with: '{replaceWith}'\n")

			# --- Font scope ---
			if scopeFont:
				print("Font Info > Font:")
				if contentGeneral:
					for attr, fieldLabel in (
						("familyName", "Family Name"),
						("designer", "Designer"),
						("manufacturer", "Manufacturer"),
						("copyright", "Copyright"),
					):
						val = getattr(font, attr, None)
						if val and searchFor in val:
							newVal, changed = self.replaceInText(val, searchFor, replaceWith, f"Font > {fieldLabel}")
							if changed:
								setattr(font, attr, newVal)
								totalCount += 1
					totalCount += self.replaceInProperties(font, searchFor, replaceWith, "Font")
				if contentCustomParameters:
					totalCount += self.replaceInCustomParameters(font, searchFor, replaceWith, "Font")

			# --- Masters scope ---
			if scopeMasters:
				print("\nFont Info > Masters:")
				for master in font.masters:
					masterLabel = f"Masters > {master.name or master.id}"
					if contentGeneral:
						if master.name and searchFor in master.name:
							newVal, changed = self.replaceInText(master.name, searchFor, replaceWith, f"{masterLabel} > Name")
							if changed:
								master.name = newVal
								totalCount += 1
						totalCount += self.replaceInProperties(master, searchFor, replaceWith, masterLabel)
					if contentCustomParameters:
						totalCount += self.replaceInCustomParameters(master, searchFor, replaceWith, masterLabel)

			# --- Instances scope ---
			if scopeInstances:
				print("\nFont Info > Instances/Exports:")
				for instance in font.instances:
					instanceLabel = f"Instances > {instance.name or '(unnamed)'}"
					if contentGeneral:
						if instance.name and searchFor in instance.name:
							newVal, changed = self.replaceInText(instance.name, searchFor, replaceWith, f"{instanceLabel} > Style Name")
							if changed:
								instance.name = newVal
								totalCount += 1
						totalCount += self.replaceInProperties(instance, searchFor, replaceWith, instanceLabel)
					if contentCustomParameters:
						totalCount += self.replaceInCustomParameters(instance, searchFor, replaceWith, instanceLabel)

			# --- Final report ---
			changeWord = "change" if totalCount == 1 else "changes"
			self.w.statusText.set(f"{totalCount} {changeWord} made.")
			print(f"\nDone: {totalCount} {changeWord} made.")
			Glyphs.showNotification("Find and Replace in Font Info", f"{totalCount} {changeWord} made. Details in Macro Window.")

		except Exception as e:
			Glyphs.showMacroWindow()
			print(f"Find and Replace in Font Info Error: {e}")
			import traceback
			print(traceback.format_exc())
			self.w.statusText.set("Error — see Macro Window.")


FindAndReplaceInFontInfo()
