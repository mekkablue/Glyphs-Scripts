# MenuTitle: Find and Replace in Font Info
__doc__ = """
Finds and replaces text in Font Info fields across Font, Masters, and Instances/Exports.
Covers both general properties (names, designer, etc.) and custom parameters (string values).
"""

import objc
import vanilla
from mekkablue import mekkaObject, makeWindowResizable
from GlyphsApp import Glyphs
from AppKit import NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut

if Glyphs.versionNumber < 4.0:
	# Glyphs 3 only had the old names, renamed in Glyphs 4:
	from GlyphsApp import GSFontInfoValueLocalized as GSInfoValueLocalized, GSFontInfoValueSingle as GSInfoValueSingle
else:
	from GlyphsApp import GSInfoValueLocalized, GSInfoValueSingle


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
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Find and Replace in Font Info",
			autosaveName=self.domain("mainwindow"),  # stores last window position and width
		)

		# Find row
		tooltipText = "Text to search for in the selected Font Info fields."
		self.w.searchForLabel = vanilla.TextBox("auto", "Find:", sizeStyle="small", selectable=True)
		self.w.searchForLabel.setToolTip(tooltipText)
		self.w.searchFor = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		self.w.searchFor.setToolTip(tooltipText)

		# Replace row
		tooltipText = "Replacement text. Leave empty to delete all occurrences of the search text."
		self.w.replaceWithLabel = vanilla.TextBox("auto", "Replace:", sizeStyle="small", selectable=True)
		self.w.replaceWithLabel.setToolTip(tooltipText)
		self.w.replaceWith = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		self.w.replaceWith.setToolTip(tooltipText)

		# Scope row: Scope: Font Info →  [x] Font  [x] Masters  [x] Instances
		self.w.scopeLabel = vanilla.TextBox("auto", "Scope: Font Info →", sizeStyle="small", selectable=True)
		self.w.scopeFont = vanilla.CheckBox("auto", "Font", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.scopeFont.setToolTip("Search and replace in font-level properties (Font Info > Font tab): family name, designer, manufacturer, copyright, and all other named fields.")
		self.w.scopeMasters = vanilla.CheckBox("auto", "Masters", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.scopeMasters.setToolTip("Search and replace in master properties (Font Info > Masters tab): master names and all other named fields.")
		self.w.scopeInstances = vanilla.CheckBox("auto", "Instances", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.scopeInstances.setToolTip("Search and replace in instance/export properties (Font Info > Instances or Exports tab): style names and all other named fields.")

		# Content row: [x] General properties  [x] Custom parameters — aligned with Font checkbox above
		self.w.contentGeneral = vanilla.CheckBox("auto", "General properties", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.contentGeneral.setToolTip("Search and replace in built-in Font Info fields such as family name, designer, style names, copyright, etc.")
		self.w.contentCustomParameters = vanilla.CheckBox("auto", "Custom parameters", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.contentCustomParameters.setToolTip("Search and replace in the string values of custom parameters at the Font, Master, and Instance levels.")

		# Status line, left of run button
		self.w.statusText = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.statusText.setToolTip("Number of replacements made in the last run.")
		self.w.statusText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run button
		self.w.runButton = vanilla.Button("auto", "Replace", callback=self.run)
		self.w.runButton.setToolTip("Run find and replace on the selected scopes and content types.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned and share the width of the widest one, so the fields line up:
		labelNames = ("searchForLabel", "replaceWithLabel", "scopeLabel")
		widestLabel = "scopeLabel"
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
				"H:|-inset-[searchForLabel]-gap-[searchFor]-inset-|",
				"H:|-inset-[replaceWithLabel]-gap-[replaceWith]-inset-|",
				"H:|-inset-[scopeLabel]-gap-[scopeFont]-gap-[scopeMasters]-gap-[scopeInstances]-(>=inset)-|",
				"H:[contentGeneral]-gap-[contentCustomParameters]-(>=inset)-|",
				"H:|-inset-[statusText]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[searchFor]-row-[replaceWith]-sectionGap-[scopeFont]-checkRow-[contentGeneral]-inset-[runButton]-inset-|",
				{"view1": self.w.searchForLabel, "attribute1": "centerY", "view2": self.w.searchFor, "attribute2": "centerY"},
				{"view1": self.w.replaceWithLabel, "attribute1": "centerY", "view2": self.w.replaceWith, "attribute2": "centerY"},
				{"view1": self.w.scopeLabel, "attribute1": "centerY", "view2": self.w.scopeFont, "attribute2": "centerY"},
				{"view1": self.w.scopeMasters, "attribute1": "centerY", "view2": self.w.scopeFont, "attribute2": "centerY"},
				{"view1": self.w.scopeInstances, "attribute1": "centerY", "view2": self.w.scopeFont, "attribute2": "centerY"},
				{"view1": self.w.contentGeneral, "attribute1": "left", "view2": self.w.scopeFont, "attribute2": "left"},
				{"view1": self.w.contentCustomParameters, "attribute1": "centerY", "view2": self.w.contentGeneral, "attribute2": "centerY"},
				{"view1": self.w.statusText, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": 15, "gap": 8, "row": 6, "checkRow": 5, "sectionGap": 12},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

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
		"""Replace in .properties (GSInfoValueSingle / GSInfoValueLocalized). Returns count."""
		count = 0
		if not hasattr(obj, "properties"):
			return 0
		for prop in obj.properties:
			if isinstance(prop, GSInfoValueSingle):
				if prop.value and searchFor in prop.value:
					newVal, changed = self.replaceInText(prop.value, searchFor, replaceWith, f"{label} > {prop.key}")
					if changed:
						prop.value = newVal
						count += 1
			elif isinstance(prop, GSInfoValueLocalized):
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
				self.w.statusText.set("❌ No font open.")
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
			self.w.statusText.set(f"✅ {totalCount} {changeWord} made. Details in Macro Window.")
			print(f"\nDone: {totalCount} {changeWord} made.")
			Glyphs.showNotification("Find and Replace in Font Info", f"{totalCount} {changeWord} made. Details in Macro Window.")

		except Exception as e:
			Glyphs.showMacroWindow()
			print(f"Find and Replace in Font Info Error: {e}")
			import traceback
			print(traceback.format_exc())
			self.w.statusText.set("❌ Error — see Macro Window.")


FindAndReplaceInFontInfo()
