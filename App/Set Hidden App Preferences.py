# MenuTitle: Set Hidden App Preferences
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
GUI for a number of hidden prefs, hard to memorize otherwise.
"""

import vanilla
from AppKit import NSFont
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class SetHiddenAppPreferences(mekkaObject):
	prefID = "com.mekkablue.SetHiddenAppPreferences"
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
		"GSAlwayShowExportNotification",
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
		windowWidth = 350
		windowHeight = 91
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Set Hidden App Preferences",  # window title
			minSize=(windowWidth, windowHeight + 19),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize + 19),  # maximum size (for resizing)
			autosaveName="com.mekkablue.SetHiddenAppPreferences.mainwindow"  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 8, 12, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Choose and apply the app defaults:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.pref = vanilla.ComboBox((inset, linePos - 2, -inset - 100, 25), self.prefs, callback=self.SavePreferences)
		self.w.pref.getNSComboBox().setFont_(NSFont.userFixedPitchFontOfSize_(11))
		self.w.pref.getNSComboBox().setToolTip_("Pick an app default from the list, or type in an identifier.")
		self.w.pref.getNSComboBox().setNumberOfVisibleItems_(20)
		self.w.prefValue = vanilla.EditText((-inset - 90, linePos, -inset, 21), "")
		self.w.prefValue.getNSTextField().setToolTip_("Enter a value for the chosen app default.")
		linePos += lineHeight

		# Run Button:
		self.w.delButton = vanilla.Button((-170 - inset, -20 - inset, -90 - inset, -inset), "Reset", callback=self.SetHiddenAppPreferencesMain)
		self.w.delButton.getNSButton().setToolTip_("Will delete the setting, effectively resetting it to its default.")

		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Apply", callback=self.SetHiddenAppPreferencesMain)
		self.w.runButton.getNSButton().setToolTip_("Sets the entered value for the chosen app default.")
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		value = Glyphs.defaults[self.w.pref.get()]
		value = str(value)
		value = value.replace("\n", "")
		while "  " in value:
			value = value.replace("  ", " ")
		self.w.prefValue.set(value)

	def SetHiddenAppPreferencesMain(self, sender):
		try:
			if sender == self.w.delButton:
				del Glyphs.defaults[self.w.pref.get()]
				self.w.prefValue.set(None)
				print("Deleted pref: %s" % self.w.pref.get())

			elif sender == self.w.runButton:
				prefName = self.w.pref.get()
				value = eval(self.w.prefValue.get())
				# if prefName in ["com.mekkablue.ShowGlyphFocus.color", "com.mekkablue.ShowGlyphFocus.colorDarkMode"]:
				#
				# 	value = value.strip("(")
				# 	value = value.strip(")")
				# 	value = value.replace('"', '')
				# 	value = value.split(',')
				# 	value = [float(v) for v in value]
				# 	value = tuple(value)
				Glyphs.defaults[prefName] = value
				print("\nSet pref: %s --> %s" % (prefName, value))
				print("Glyphs.defaults['%s'] = %s" % (prefName, value))

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Set Hidden App Preferences Error: %s" % e)
			import traceback
			print(traceback.format_exc())


SetHiddenAppPreferences()
