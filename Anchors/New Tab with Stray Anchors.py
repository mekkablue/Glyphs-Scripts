#MenuTitle: New Tab with Stray Anchors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Find all anchors that are not where they are supposed to be.
"""

import vanilla, sys
from mekkablue import mekkaObject, UpdateButton

horizontals = (
	"LSB",
	"RSB",
	"LSB or RSB",
	"Center (1u tolerance)",
	"Center or LSB or RSB",
)

verticals = (
	"Any metric line",
	"Baseline",
	"Cap or x-height",
)


def anchorIsAstray(thisAnchor, thisLayer, shouldHorizontalAlign, shouldVerticalAlign, horizontalAlignment, verticalAlignment):
	x, y = thisAnchor.position

	if shouldHorizontalAlign:
		isNotAtLSB = x != 0
		isNotAtRSB = x != thisLayer.width
		isNotInCenter = not ((thisLayer.width/2-1) < x < (thisLayer.width/2+1))
		
		# none of the positions are taken -> definitely astray
		if all((isNotAtRSB, isNotAtRSB, isNotInCenter)):
			return True

		if horizontalAlignment <= 2 and isNotAtLSB and isNotAtRSB:
			return True

		# LSB
		if horizontalAlignment == 0 and isNotAtLSB:
			return True

		# RSB
		if horizontalAlignment == 1 and isNotAtRSB:
			return True

		# Center (1u tolerance)
		if horizontalAlignment == 3 and isNotInCenter:
			return True
		
	if shouldVerticalAlign:
		xHeight, capHeight = None, None
		for m in thisLayer.metrics:
			if m.name == "x-Height":
				xHeight = m.position
			if m.name == "Cap Height":
				capHeight = m.position
		
		isNotAtBaseline = y != 0
		isNotAtXHeight = y != xHeight
		isNotAtCapHeight = y != capHeight
		isNotOnAnyMetric = y not in [m.position for m in thisLayer.metrics]
		
		# Any metric line
		if verticalAlignment == 0 and isNotOnAnyMetric:
			return True

		# Baseline
		if verticalAlignment == 1 and isNotAtBaseline:
			return True

		# Cap or x-height
		if verticalAlignment == 2 and isNotAtXHeight and isNotAtCapHeight:
			return True

	return False
		
		

class FindStrayAnchors(mekkaObject):
	prefID = "com.mekkablue.FindStrayAnchors"
	prefDict = {
		# "prefName": defaultValue,
		"shouldHorizontalAlign": False,
		"shouldVerticalAlign": False,
		"horizontalAlignment": 2, # LSB or RSB
		"verticalAlignment": 0, # Any Metric Line
		"anchors": "top, bottom, _top, _bottom",
	}

	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 180
		windowWidthResize  = 1000 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Find Stray Anchors", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 40), "Open a new tab with glyphs where anchors are not where they are supposed to be:", sizeStyle="small", selectable=True)
		linePos += int(lineHeight * 1.8)
		
		indent = 78
		tooltip = "All anchors you want to find. Separate multiple names with comma’s, e.g., ‘top, bottom’ or ‘exit, entry’."
		self.w.anchorsText = vanilla.TextBox((inset, linePos+2, indent, 14), "Find anchors", sizeStyle="small", selectable=True)
		self.w.anchors = vanilla.EditText((inset+indent, linePos-1, -inset-19, 19), "top, bottom, _top, _bottom", callback=self.SavePreferences, sizeStyle="small")
		self.w.anchorsText.getNSTextField().setToolTip_(tooltip)
		self.w.anchors.getNSTextField().setToolTip_(tooltip)
		self.w.updateButton = UpdateButton((-inset - 18, linePos - 3, -inset, 18), callback=self.updateAnchorNames)
		self.w.updateButton.getNSButton().setToolTip_("Insert all anchor names of the frontmost font. Resets to default ‘top, bottom, _top, _bottom’ if there is no font open (or no anchors in the frontmost font).")
		linePos += lineHeight

		indent = 120
		self.w.shouldHorizontalAlign = vanilla.CheckBox((inset, linePos-1, indent, 20), "Horizontally not on:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.horizontalAlignment = vanilla.PopUpButton((inset+indent, linePos, -inset, 17), horizontals, sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight

		self.w.shouldVerticalAlign = vanilla.CheckBox((inset, linePos-1, indent, 20), "Vertically not on:", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.verticalAlignment = vanilla.PopUpButton((inset+indent, linePos, -inset, 17), verticals, sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Find", sizeStyle="regular", callback=self.FindStrayAnchorsMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Find Stray Anchors’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()


	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()


	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]


	def updateAnchorNames(self, sender=None):
		anchorText = self.collectAnchors()
		self.w.anchors.set(anchorText)


	def updateUI(self, sender=None):
		activeH = self.uiElement("shouldHorizontalAlign").get()
		activeV = self.uiElement("shouldVerticalAlign").get()
		activeButton = activeH or activeV
		self.uiElement("horizontalAlignment").enable(activeH)
		self.uiElement("verticalAlignment").enable(activeV)
		self.uiElement("runButton").enable(activeButton)


	def collectAnchors(self, default="top, bottom, _top, _bottom"):
		currentFont = Glyphs.font
		if not currentFont:
			return default

		collectedAnchors = []
		for glyph in currentFont.glyphs:
			for layer in glyph.layers:
				if not layer.isMasterLayer and not layer.isSpecialLayer:
					continue
				for anchor in layer.anchors:
					if not anchor.name in collectedAnchors:
						collectedAnchors.append(anchor.name)

		if not collectedAnchors:
			return default

		return ", ".join(sorted(collectedAnchors))


	def FindStrayAnchorsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			self.SavePreferences()
			
			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(sys.modules[__name__], prefName, self.pref(prefName))
				except:
					fallbackValue = self.prefDict[prefName]
					print(f"⚠️ Could not set pref ‘{prefName}’, resorting to default value: ‘{fallbackValue}’.")
					setattr(sys.modules[__name__], prefName, fallbackValue)
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Find Stray Anchors Report for {reportName}")
				print()
				
				anchors = self.pref("anchors")
				if not anchors:
					print("No anchors specified by user. Exiting.")
					Message(
						title="No anchors specified",
						message="Write comma-separated anchor names in the ‘Find anchors’ field, or click on the update button to populate the field with all anchor names of the frontmost font.",
						OKButton=None,
						)
					return

				shouldHorizontalAlign = self.pref("shouldHorizontalAlign")
				shouldVerticalAlign = self.pref("shouldVerticalAlign")
				horizontalAlignment = self.pref("horizontalAlignment")
				verticalAlignment = self.pref("verticalAlignment")

				report = {}
				anchorNames = [a.strip() for a in anchors.split(",")]

				for anchorName in anchorNames:
					report[anchorName] = []

				for thisGlyph in thisFont.glyphs:
					for thisLayer in thisGlyph.layers:
						if not thisLayer.isMasterLayer and not thisLayer.isSpecialLayer:
							continue
						thisLayer.selection = []
						for thisAnchor in thisLayer.anchors:
							if not thisAnchor.name in anchorNames:
								continue

							if anchorIsAstray(thisAnchor, thisLayer, shouldHorizontalAlign, shouldVerticalAlign, horizontalAlignment, verticalAlignment):
								report[thisAnchor.name].append(thisLayer)
								thisLayer.selection.append(thisAnchor)

				# none found, celebrate
				if all([bool(report[a])==False for a in report.keys()]):
					Message(
						title="All good!",
						message="No stray anchors found with the specified settings.",
						OKButton="Cheers🍻",
						)
					return

				# report
				reportTab = thisFont.newTab()
				for anchorName in sorted(report.keys()):
					if not report[anchorName]:
						continue
					for character in anchorName:
						glyph = thisFont.glyphForCharacter_(ord(character))
						if not glyph:
							continue
						reportTab.layers.append(glyph.layers[0])
					reportTab.layers.append(GSControlLayer.newline())
					for reportedLayer in report[anchorName]:
						reportTab.layers.append(reportedLayer)
					for x in range(2):
						reportTab.layers.append(GSControlLayer.newline())

				# self.w.close() # delete if you want window to stay open

			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Find Stray Anchors Error: {e}")
			import traceback
			print(traceback.format_exc())


FindStrayAnchors()