# MenuTitle: Set Hidden App Preferences
__doc__ = """
GUI for a number of hidden prefs, hard to memorize otherwise.
"""

import vanilla
from ast import literal_eval
from AppKit import (
	NSFont,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityWindowSizeStayPut,
	NSWindowStyleMaskResizable,
)
from Foundation import NSSize
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class SetHiddenAppPreferences(mekkaObject):
	prefDict = {
		"pref": ""
	}
	prefs = (
		"GSMakeSmoothNodes",
		"GSKerningIncrementHigh",
		"GSKerningIncrementLow",
		"GSSpacingIncrementHigh",
		"GSSpacingIncrementLow",
		"GSShowVersionNumberInDockIcon",
		"GSShowVersionNumberInTitleBar",
		"GSFontViewMinIconSize",
		"GSFontViewMaxIconSize",
		"GSFontViewShowCustomGlyphInfoIndicator",
		"IgnoreRecentScriptInvokedByKeyboard",
		"moveToApplicationsFolderAlertSuppress",
		"DebugMode",
		"GSPluginManagerDisableAutomaticUpdates",
		"AlwaysShowAllMetrics",
		"GSPreview_MoreSpaceAbove",
		"GSPreview_MoreSpaceBelow",
		"GSClickTolerance",
		"GSAlwayShowExportNotification",
		"GSShowStrokePanel",
		"GSTidyUpThreshold",
		"GSAutosaveAsSingleFile",
		"AppleLanguages",
		"drawShadowAccents",
		"GSftxenhancerPath",
		"GSCenterSelectionOnMasterSwitch",
		"MacroCodeFontSize",
		"GSMacroWindowAllowNoneAsciiInput" if Glyphs.buildNumber < 3203 else "GSMacroWindowAllowNonAsciiInput",
		"showShadowPath",
		"GSDrawOutlinesAliased",
		"TextModeNumbersThreshold",
		"TTPreviewAlsoShowOffCurveIndexes",
		"GSFontViewSmallestNameHeight",
		"GSHideUnicodeInFontView" if Glyphs.versionNumber < 3.0 else "GSFontViewShowUnicode",
		"GSFontViewDrawLabelColor",
		"GSFontViewDarkMode",
		"GSEditViewDarkMode",
		"UFOWriteSparseInfo",
		"com.mekkablue.KernIndicator.offset",
		"com.mekkablue.ShowFilledPreview.opacity",
		"com.mekkablue.ShowGlyphFocus.color",
		"com.mekkablue.ShowGlyphFocus.colorDarkMode",
		"com.mekkablue.ShowItalic.drawItalicsForInactiveGlyphs",
		"com.mekkablue.ShowMarkPreview.extension",
		"com.mekkablue.ShowStyles.anchors",
		"com.mekkablue.ttAutoinstructSelectedGlyphs.alwaysUseNoStem",
		"com.mekkablue.colorCompositesInShadeOfBaseGlyph.shadeFactor",
		"com.RicardGarcia.ChangeCase.verboseReport",
		"com.FlorianPircher.Keyboard-Selection-Travel.UseAlternativeShortcuts",
	)

	def __init__(self):
		# Window 'self.w':
		windowWidth = 470
		windowWidthResize = 800  # user can widen the window by this value
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Set Hidden App Preferences",
			autosaveName=self.domain("mainwindow"),  # stores last window position and size
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Choose and apply the app defaults:", sizeStyle="small", selectable=True)

		self.w.pref = vanilla.ComboBox("auto", self.prefs, callback=self.SavePreferences, sizeStyle="small")
		self.w.pref.getNSComboBox().setFont_(NSFont.userFixedPitchFontOfSize_(11))
		self.w.pref.getNSComboBox().setNumberOfVisibleItems_(20)
		self.w.pref.setToolTip("Pick an app default from the list, or type in an identifier.")

		self.w.prefValue = vanilla.EditText("auto", "", sizeStyle="small")
		self.w.prefValue.getNSTextField().setPlaceholderString_("value, e.g. True, 42 or 'text'")
		self.w.prefValue.setToolTip("Enter a value for the chosen app default: a number, True or False, or text in quotes (also lists and dictionaries).")

		# Run Button:
		self.w.delButton = vanilla.Button("auto", "Reset", callback=self.SetHiddenAppPreferencesMain)
		self.w.delButton.setToolTip("Will delete the setting, effectively resetting it to its default.")

		self.w.runButton = vanilla.Button("auto", "Apply", callback=self.SetHiddenAppPreferencesMain)
		self.w.runButton.setToolTip("Sets the entered value for the chosen app default.")
		self.w.setDefaultButton(self.w.runButton)

		# the long identifiers must not widen the window; the combo box takes the leftover width:
		self.w.pref.getNSComboBox().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[pref]-gap-[prefValue(150)]-inset-|",
				"H:|-(>=inset)-[delButton(>=70)]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[pref]-inset-[runButton]-inset-|",
				"V:[delButton]-inset-|",
				{"view1": self.w.prefValue, "attribute1": "centerY", "view2": self.w.pref, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# Resizable in width only. Vanilla's minSize/maxSize would count the title bar twice,
		# so set the limits on the NSWindow, in content sizes, with the height Auto Layout asks for:
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		contentHeight = nsWindow.contentView().fittingSize().height
		nsWindow.setContentMinSize_(NSSize(windowWidth, contentHeight))
		nsWindow.setContentMaxSize_(NSSize(windowWidth + windowWidthResize, contentHeight))

	def updateUI(self, sender=None):
		prefName = self.w.pref.get()
		value = Glyphs.defaults[prefName] if prefName else None
		if isinstance(value, str):
			# show text in quotes, so it can be applied again as it is:
			value = repr(str(value))
		else:
			value = str(value) if value is not None else ""
			value = value.replace("\n", "")
			while "  " in value:
				value = value.replace("  ", " ")
		self.w.prefValue.set(value)

	def SetHiddenAppPreferencesMain(self, sender):
		try:
			prefName = self.w.pref.get().strip()
			if not prefName:
				Glyphs.showNotification("Set Hidden App Preferences", "Please choose or enter an app default first.")
				return

			if sender == self.w.delButton:
				del Glyphs.defaults[prefName]
				self.w.prefValue.set("")
				print(f"🗑️ Deleted pref: {prefName}")

			elif sender == self.w.runButton:
				try:
					value = literal_eval(self.w.prefValue.get().strip())
				except (ValueError, SyntaxError):
					# literal_eval, because the field content should never be executed as code
					Glyphs.showMacroWindow()
					print(f"❌ Could not read the value ‘{self.w.prefValue.get()}’ for {prefName}.")
					print("Enter a number, True or False, text in quotes (e.g. 'text'), or a list or dictionary of these.")
					return
				Glyphs.defaults[prefName] = value
				print(f"\n✅ Set pref: {prefName} --> {value}")
				print(f"Glyphs.defaults['{prefName}'] = {value!r}")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Set Hidden App Preferences Error: {e}")
			import traceback
			print(traceback.format_exc())


SetHiddenAppPreferences()
