# MenuTitle: Find Close Encounters of Orthogonal Line Segments
__doc__ = """
Goes through all vertical and horizontal line segments, and finds pairs that are close, but do not align completely.
"""

import objc
import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSPoint, NSNumberFormatter
from GlyphsApp import Glyphs, GSGuide, Message
from mekkablue import mekkaObject, reportFontName
from mekkablue.geometry import angle


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


class FindCloseEncounters(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"threshold": 2,
		"includeComposites": True,
		"includeNonExporting": True,
		"excludeGlyphs": True,
		"excludeGlyphsContaining": ".ornm, .dnom, .numr, superior, inferior, .blackCircled, apple, BlackIndex",
		"reuseTab": True,
		"allFonts": False,
	}
	markerEmoji = "😰"

	def __init__(self):
		# Window 'self.w':
		windowWidth = 440
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Find Close Encounters of Orthogonal Line Segments",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Find orthogonal line segments that are close but not aligning:", sizeStyle='small', selectable=True)

		formatter = NSNumberFormatter.alloc().init()
		formatter.setMinimum_(0)
		self.w.thresholdText = vanilla.TextBox("auto", "Max distance in units:", sizeStyle='small', selectable=True)
		self.w.threshold = SteppingEditText("auto", self.prefDict["threshold"], callback=self.SavePreferences, sizeStyle='small', formatter=formatter)

		self.w.includeComposites = vanilla.CheckBox("auto", "Include composites (otherwise only glyphs with paths)", value=self.prefDict["includeComposites"], callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting = vanilla.CheckBox("auto", "Include non-exporting glyphs", value=self.prefDict["includeNonExporting"], callback=self.SavePreferences, sizeStyle='small')

		self.w.excludeGlyphs = vanilla.CheckBox("auto", "Exclude glyphs containing:", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.excludeGlyphsContaining = vanilla.EditText("auto", self.prefDict["excludeGlyphsContaining"], callback=self.SavePreferences, sizeStyle='small')

		self.w.allFonts = vanilla.CheckBox("auto", "Include ⚠️ ALL fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab for report", value=False, callback=self.SavePreferences, sizeStyle='small')

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Find", callback=self.FindCloseEncountersMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the checkbox hugs its title, the field behind it takes the leftover width:
		self.w.excludeGlyphs.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.excludeGlyphsContaining.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[thresholdText]-gap-[threshold(50)]-(>=inset)-|",
				"H:|-inset-[includeComposites]-(>=inset)-|",
				"H:|-inset-[includeNonExporting]-(>=inset)-|",
				"H:|-inset-[excludeGlyphs]-gap-[excludeGlyphsContaining]-inset-|",
				"H:|-inset-[allFonts]-(>=inset)-|",
				"H:|-inset-[reuseTab]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-row-[threshold]-row-[includeComposites]-stackRow-[includeNonExporting]-stackRow-[excludeGlyphsContaining]-stackRow-[allFonts]-stackRow-[reuseTab]-inset-[runButton]-inset-|",
				{"view1": self.w.thresholdText, "attribute1": "centerY", "view2": self.w.threshold, "attribute2": "centerY"},
				{"view1": self.w.excludeGlyphs, "attribute1": "centerY", "view2": self.w.excludeGlyphsContaining, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8, "stackRow": 8},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.excludeGlyphsContaining.enable(self.pref("excludeGlyphs"))
		self.w.runButton.enable(abs(self.prefFloat("threshold")) > 0)

	def FindCloseEncountersMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			# read prefs:
			threshold = abs(self.prefFloat("threshold"))
			includeComposites = self.pref("includeComposites")
			includeNonExporting = self.pref("includeNonExporting")
			excludeGlyphs = self.pref("excludeGlyphs")
			excludeGlyphsContaining = [particle.strip() for particle in self.pref("excludeGlyphsContaining").split(",") if particle.strip()]
			reuseTab = self.pref("reuseTab")
			allFonts = self.pref("allFonts")

			if len(Glyphs.fonts) == 0:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			if allFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )

			for thisFont in theseFonts:
				report = reportFontName(thisFont)
				print("Find Close Encounters of Orthogonal Line Segments Report for %s" % report)
				print()

				collectedLayers = []
				for g in thisFont.glyphs:
					# cleaning up existing guide markers
					for layer in g.layers:
						if not layer.isMasterLayer and not layer.isSpecialLayer:
							continue
						if layer.guides:
							for i in range(len(layer.guides) - 1, -1, -1):
								guide = layer.guides[i]
								if guide.name and guide.name.startswith(self.markerEmoji):
									del layer.guides[i]

					# see if glyph/layer needs to be skipped:
					if not g.export and not includeNonExporting:
						continue
					if excludeGlyphs:
						particleInGlyphName = [particle in g.name for particle in excludeGlyphsContaining]
						if any(particleInGlyphName):
							continue
					for layer in g.layers:
						if not layer.isMasterLayer and not layer.isSpecialLayer:
							continue
						if not layer.paths and not includeComposites:
							continue

						# look for line segments:
						decomposedLayer = layer.copyDecomposedLayer()
						segmentDict = {
							0: [],
							90: [],
						}
						for path in decomposedLayer.paths:
							for segment in path.segments:
								if len(segment) == 2:
									segmentAngle = int(angle(segment[0], segment.lastPoint()) % 180)
									if segmentAngle in segmentDict.keys():
										#  0 deg --> compare y
										# 90 deg --> compare x
										segmentDict[segmentAngle].append(segment.middlePoint()[int(1 - segmentAngle / 90)])
						for segmentAngle in segmentDict.keys():
							coords = sorted(set(segmentDict[segmentAngle]))
							if len(coords) > 1:
								for i in range(1, len(coords)):
									prevCoord = coords[i - 1]
									thisCoord = coords[i]
									dist = abs(thisCoord - prevCoord)
									if dist <= threshold:
										print("%s 📐%i 🔢 %i ~ %i 🔠 %s (%s)" % (
											self.markerEmoji,
											segmentAngle,
											prevCoord,
											thisCoord,
											g.name,
											layer.name,
										))
										for coord in prevCoord, thisCoord:
											gd = GSGuide()
											gd.angle = segmentAngle
											gd.name = "%s %i" % (self.markerEmoji, coord)
											gd.position = NSPoint(
												0 if segmentAngle == 0 else coord,
												0 if segmentAngle == 90 else coord,
											)
											layer.guides.append(gd)
										if layer not in collectedLayers:
											collectedLayers.append(layer)

				if collectedLayers:
					if reuseTab and thisFont.currentTab:
						tab = thisFont.currentTab
					else:
						tab = thisFont.newTab()
					tab.layers = collectedLayers
				elif len(theseFonts) == 1:
					Message(
						title="No close encounters found",
						message="Congratulations! No non-aliging line segments not further than %iu in this font." % abs(threshold),
						OKButton=None,
					)
				else:
					print("✅ No close encounters found in this font.")

			self.w.close()  # delete if you want window to stay open

			# Final report:
			Glyphs.showNotification(
				f"{thisFont.familyName}: Done",
				"Find Close Encounters of Orthogonal Line Segments is finished. Details in Macro Window",
			)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Find Close Encounters of Orthogonal Line Segments Error: {e}")
			import traceback
			print(traceback.format_exc())


FindCloseEncounters()
