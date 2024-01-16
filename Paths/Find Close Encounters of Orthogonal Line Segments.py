# MenuTitle: Find Close Encounters of Orthogonal Line Segments
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Goes through all vertical and horizontal line segments, and finds pairs that are close, but do not align completely.
"""

import vanilla
import math
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSGuide, Message


def angle(firstPoint, secondPoint):
	xDiff = secondPoint.x - firstPoint.x
	yDiff = secondPoint.y - firstPoint.y
	return math.degrees(math.atan2(yDiff, xDiff))


class FindCloseEncounters(object):
	prefID = "com.mekkablue.FindCloseEncounters"
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
		windowWidth = 370
		windowHeight = 220
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Find Close Encounters of Orthogonal Line Segments",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Find orthogonal line segments that are close but not aligning:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.thresholdText = vanilla.TextBox((inset, linePos + 2, 120, 14), "Max distance in units:", sizeStyle='small', selectable=True)
		self.w.threshold = vanilla.EditText((inset + 120, linePos - 1, 50, 19), self.prefDict["threshold"], callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.includeComposites = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Include composites (otherwise only glyphs with paths)", value=self.prefDict["includeComposites"], callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.includeNonExporting = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Include non-exporting glyphs", value=self.prefDict["includeNonExporting"], callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.excludeGlyphs = vanilla.CheckBox((inset, linePos - 1, 160, 20), "Exclude glyphs containing:", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.excludeGlyphsContaining = vanilla.EditText((inset + 160, linePos - 1, -inset, 19), self.prefDict["excludeGlyphsContaining"], callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Include ⚠️ ALL fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.reuseTab = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Reuse current tab for report", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Find", sizeStyle='regular', callback=self.FindCloseEncountersMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Find Close Encounters of Orthogonal Line Segments’ could not load preferences. Will resort to defaults.")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateGUI(self, sender=None):
		self.w.excludeGlyphsContaining.enable(self.pref("excludeGlyphs"))
		self.w.runButton.enable(abs(float(self.pref("threshold"))) > 0)

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()

	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
			self.updateGUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				getattr(self.w, prefName).set(self.pref(prefName))
			self.updateGUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def FindCloseEncountersMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Find Close Encounters of Orthogonal Line Segments’ could not write preferences.")

			# read prefs:
			threshold = abs(float(self.pref("threshold")))
			includeComposites = self.pref("includeComposites")
			includeNonExporting = self.pref("includeNonExporting")
			excludeGlyphs = self.pref("excludeGlyphs")
			excludeGlyphsContaining = [particle.strip() for particle in self.pref("excludeGlyphsContaining").split(",")]
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
				filePath = thisFont.filepath
				if filePath:
					report = "%s\n📄 %s" % (filePath.lastPathComponent(), filePath)
				else:
					report = "%s\n⚠️ The font file has not been saved yet." % thisFont.familyName
				print("Find Close Encounters of Orthogonal Line Segments Report for %s" % report)
				print()

				collectedLayers = []
				for g in thisFont.glyphs:
					# cleaning up existing guide markers
					for layer in g.layers:
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
