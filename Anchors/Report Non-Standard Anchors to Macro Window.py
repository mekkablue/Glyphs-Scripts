# MenuTitle: Report Non-Standard Anchors to Macro Window
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Goes through all glyphs in the font and reports in the Macro Window if it finds non-default anchors. Lines are copy-pasteable in Edit view.
"""

import vanilla
from GlyphsApp import Glyphs


class ReportNonStandardAnchorsInMacroWindow(object):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 400
		windowHeight = 150
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Report Non-Standard Anchors to Macro Window",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName="com.mekkablue.ReportNonStandardAnchorsInMacroWindow.mainwindow"  # stores last window position and size
		)

		# UI elements:
		inset = 10
		currentHeight = 8
		self.w.text_1 = vanilla.TextBox((inset, currentHeight + 2, -inset, 28), __doc__.strip(), sizeStyle='small')
		currentHeight += 35
		self.w.includeNonExporting = vanilla.CheckBox((inset, currentHeight, -inset, 20), "Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		currentHeight += 20
		self.w.reportExitEntry = vanilla.CheckBox((inset, currentHeight, -inset, 20), "Report exit and entry anchors", value=False, callback=self.SavePreferences, sizeStyle='small')
		currentHeight += 20
		self.w.reportCarets = vanilla.CheckBox((inset, currentHeight, -inset, 20), "Report ligature caret anchors", value=False, callback=self.SavePreferences, sizeStyle='small')

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - 15, -20 - 15, -15, -15), "Report", sizeStyle='regular', callback=self.ReportNonStandardAnchorsInMacroWindowMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Report Non-Standard Anchors to Macro Window' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def SavePreferences(self, sender):
		try:
			Glyphs.defaults["com.mekkablue.ReportNonStandardAnchorsInMacroWindow.includeNonExporting"] = self.w.includeNonExporting.get()
			Glyphs.defaults["com.mekkablue.ReportNonStandardAnchorsInMacroWindow.reportExitEntry"] = self.w.reportExitEntry.get()
			Glyphs.defaults["com.mekkablue.ReportNonStandardAnchorsInMacroWindow.reportCarets"] = self.w.reportCarets.get()
		except:
			return False

		return True

	def LoadPreferences(self):
		try:
			Glyphs.registerDefault("com.mekkablue.ReportNonStandardAnchorsInMacroWindow.includeNonExporting", 0)
			Glyphs.registerDefault("com.mekkablue.ReportNonStandardAnchorsInMacroWindow.reportExitEntry", 0)
			Glyphs.registerDefault("com.mekkablue.ReportNonStandardAnchorsInMacroWindow.reportCarets", 0)
			self.w.includeNonExporting.set(Glyphs.defaults["com.mekkablue.ReportNonStandardAnchorsInMacroWindow.includeNonExporting"])
			self.w.reportExitEntry.set(Glyphs.defaults["com.mekkablue.ReportNonStandardAnchorsInMacroWindow.reportExitEntry"])
			self.w.reportCarets.set(Glyphs.defaults["com.mekkablue.ReportNonStandardAnchorsInMacroWindow.reportCarets"])
		except:
			return False

		return True

	def ReportNonStandardAnchorsInMacroWindowMain(self, sender):
		try:
			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			thisFont = Glyphs.font

			print("Unusual anchors in %s" % thisFont.familyName)
			print("File: %s\n" % thisFont.filepath)

			if thisFont:
				for thisGlyph in Font.glyphs:
					if thisGlyph.export or Glyphs.defaults["com.mekkablue.ReportNonStandardAnchorsInMacroWindow.includeNonExporting"]:
						thisLayer = thisGlyph.layers[0]
						if thisLayer.anchors:

							# determine defaults
							defaultAnchors = None
							glyphinfo = thisFont.glyphsInfo().glyphInfoForName_(thisGlyph.name)
							if glyphinfo:
								defaultAnchors = glyphinfo.anchors

							# find unusual anchors in this glyph
							unusualAnchors = []
							if not defaultAnchors:
								defaultAnchors = ()
							glyphIsLigature = (thisGlyph.subCategory == "Ligature" or "_" in thisGlyph.name[1:])
							for thisAnchor in thisLayer.anchors:
								if not thisAnchor.name in defaultAnchors:
									anchorIsExitEntry = thisAnchor.name in ("exit", "entry") or thisAnchor.name[1:] in ("exit", "entry")
									anchorIsCaret = thisAnchor.name.startswith("caret")

									# see if exceptions apply:
									if anchorIsCaret and glyphIsLigature and not Glyphs.defaults["com.mekkablue.ReportNonStandardAnchorsInMacroWindow.reportCarets"]:
										pass # carets in ligatures
									elif anchorIsExitEntry and not Glyphs.defaults["com.mekkablue.ReportNonStandardAnchorsInMacroWindow.reportExitEntry"]:
										pass # exit and entry anchors
									else:
										unusualAnchors.append(thisAnchor.name)

							if unusualAnchors:
								print("/%s : %s" % (thisGlyph.name, ", ".join(unusualAnchors)))

			print("\n(Hint: Lines can be copied and pasted in Edit view.)")
			Glyphs.showMacroWindow()

			if not self.SavePreferences(self):
				print("Note: 'Report Non-Standard Anchors to Macro Window' could not write preferences.")

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Report Non-Standard Anchors to Macro Window Error: %s" % e)
			import traceback
			print(traceback.format_exc())


ReportNonStandardAnchorsInMacroWindow()
