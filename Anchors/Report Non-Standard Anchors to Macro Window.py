# MenuTitle: Report Non-Standard Anchors to Macro Window
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Goes through all glyphs in the font and reports in the Macro Window if it finds non-default anchors. Lines are copy-paste-able in Editview.
"""

import vanilla
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class ReportNonStandardAnchorsInMacroWindow(mekkaObject):
	prefDict = {
		"includeNonExporting": 0,
		"reportExitEntry": 0,
		"reportCarets": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 158
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Report Non-Standard Anchors to Macro Window",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset = 16
		currentHeight = 8
		self.w.text_1 = vanilla.TextBox((inset, currentHeight + 2, -inset, 42), __doc__.strip(), sizeStyle='small')
		currentHeight += 49
		self.w.includeNonExporting = vanilla.CheckBox((inset + 4, currentHeight, -inset, 20), "Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		currentHeight += 20
		self.w.reportExitEntry = vanilla.CheckBox((inset + 4, currentHeight, -inset, 20), "Report exit and entry anchors", value=False, callback=self.SavePreferences, sizeStyle='small')
		currentHeight += 20
		self.w.reportCarets = vanilla.CheckBox((inset + 4, currentHeight, -inset, 20), "Report ligature caret anchors", value=False, callback=self.SavePreferences, sizeStyle='small')

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - 12, -15, -15), "Report", callback=self.ReportNonStandardAnchorsInMacroWindowMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def ReportNonStandardAnchorsInMacroWindowMain(self, sender):
		try:
			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			thisFont = Glyphs.font
			if not thisFont:
				print("Not Font open")
				return

			print("Unusual anchors in %s" % thisFont.familyName)
			print("File: %s\n" % thisFont.filepath)

			for thisGlyph in thisFont.glyphs:
				if thisGlyph.export or self.pref("includeNonExporting"):
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
							if thisAnchor.name not in defaultAnchors:
								anchorIsExitEntry = thisAnchor.name in ("exit", "entry") or thisAnchor.name[1:] in ("exit", "entry")
								anchorIsCaret = thisAnchor.name.startswith("caret")

								# see if exceptions apply:
								if anchorIsCaret and glyphIsLigature and not self.pref("reportCarets"):
									pass  # carets in ligatures
								elif anchorIsExitEntry and not self.pref("reportExitEntry"):
									pass  # exit and entry anchors
								else:
									unusualAnchors.append(thisAnchor.name)

						if unusualAnchors:
							print("/%s : %s" % (thisGlyph.name, ", ".join(unusualAnchors)))

			print("\n(Hint: Lines can be copied and pasted in Edit view.)")
			Glyphs.showMacroWindow()

			self.SavePreferences()

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Report Non-Standard Anchors to Macro Window Error: %s" % e)
			import traceback
			print(traceback.format_exc())


ReportNonStandardAnchorsInMacroWindow()
