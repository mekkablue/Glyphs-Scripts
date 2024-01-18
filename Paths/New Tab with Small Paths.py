# MenuTitle: New Tab with Small Paths
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
__doc__ = """
Finds small paths (smaller tahn a user-definable threshold) in glyphs and open a new tab with affected glyphs.
"""

import vanilla
from GlyphsApp import Glyphs, Message
from mekkaCore import mekkaObject


def glyphShouldBeIgnored(glyphname):
	beginParticles = ("_corner", "_segment", "_cap")
	for particle in beginParticles:
		if glyphname.startswith(particle):
			return True
	return False


class FindSmallPaths(mekkaObject):
	prefDict = {
		"sliderMin": 10,
		"sliderMax": 1000,
		"areaSlider": 0.1,
		"deleteThemRightAway": 0,
		"afterOverlapRemoval": 1,
		"allFonts": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 250
		windowHeight = 240
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"New Tab with Small Paths",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.text_1 = vanilla.TextBox((inset, linePos, -inset, 30), "Open new tab with glyphs that contain paths with an area smaller than:", sizeStyle='small')
		linePos += lineHeight * 1.7

		self.w.minArea = vanilla.TextBox((inset, linePos, -inset, 15 + 3), "1000 square units", sizeStyle='small', alignment="center")
		linePos += lineHeight

		self.w.sliderMin = vanilla.EditText((inset, linePos, 50, 19), "10", sizeStyle='small', callback=self.SliderUpdate)
		self.w.sliderMax = vanilla.EditText((-inset - 50, linePos, -inset, 19), "1000", sizeStyle='small', callback=self.SliderUpdate)
		self.w.areaSlider = vanilla.Slider((inset + 50 + 10, linePos, -inset - 50 - 10, 19), value=0.1, minValue=0.0, maxValue=1.0, sizeStyle='small', callback=self.SliderUpdate)
		linePos += lineHeight

		self.w.deleteThemRightAway = vanilla.CheckBox((inset, linePos, -inset, 20), "Delete Small Paths Right Away", value=False, callback=self.CheckBoxUpdate, sizeStyle='small')
		linePos += lineHeight

		self.w.afterOverlapRemoval = vanilla.CheckBox((inset, linePos, -inset, 20), "After Decomposition and Overlap Removal (slower)", value=True, callback=self.CheckBoxUpdate, sizeStyle='small')
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset, linePos, -inset, 20), "Apply to all open fonts", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)  # set progress indicator to zero
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120, -20 - inset, -inset, -inset), u"Open Tab", sizeStyle='regular', callback=self.FindSmallPathsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Find Small Paths' could not load preferences. Will resort to defaults")

		self.CheckBoxUpdate(None)
		self.SliderUpdate(None)

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def CheckBoxUpdate(self, sender):
		try:
			# mutually exclusive check boxes:
			theOne = self.w.afterOverlapRemoval
			theOther = self.w.deleteThemRightAway
			theOther.enable(not bool(theOne.get()))
			theOne.enable(not bool(theOther.get()))

			# Hack as long as vanilla.CheckBox.getNSButton is not implemented:
			if theOne.get():
				theOther.set(False)
			if theOther.get():
				theOne.set(False)

			# save prefs:
			if not self.SavePreferences(self):
				print("Note: 'Find Small Paths' could not write preferences.")

			return True
		except Exception as e:
			self.errorReport(e)
			return False

	def SliderUpdate(self, sender):
		try:
			# update the defaults:
			if sender != self.w.areaSlider:
				if not self.SavePreferences(self):
					print("Note: 'Find Small Paths' could not write preferences.")

			# fallback values
			minimum, maximum = 1.0, 1.0

			# validate the min and max entries:
			try:
				minimum = self.prefFloat("sliderMin")
			except Exception as e:  # noqa: F841
				# disable slider and button
				self.w.areaSlider.enable(onOff=False)
				self.w.runButton.enable(onOff=False)
				# put warning message into area text:
				self.w.minArea.set("Please enter a valid min value.")
				return True

			try:
				maximum = self.prefFloat("sliderMax")
			except Exception as e:  # noqa: F841
				# disable slider and button
				self.w.areaSlider.enable(onOff=False)
				self.w.runButton.enable(onOff=False)
				# put warning message into area text:
				self.w.minArea.set("Please enter a valid max value.")
				return True

			# minimum value = 1
			if minimum < 1.0:
				minimum = 1
				self.w.sliderMin.set(minimum)

			# maximum must be larger than minimum:
			if maximum < minimum:
				# disable slider and button
				self.w.areaSlider.enable(onOff=False)
				self.w.runButton.enable(onOff=False)
				# put warning message into area text:
				self.w.minArea.set("Maximum must be larger than minimum.")
			else:
				# enable slider and button
				self.w.areaSlider.enable(onOff=True)
				self.w.runButton.enable(onOff=True)
				# update the current area:
				Glyphs.defaults[self.domain("areaSlider")] = self.w.areaSlider.get()
				minArea = self.CurrentMinArea()

			return True
		except:
			return False

	def CurrentMinArea(self, ):
		minimum = self.prefFloat("sliderMin")
		maximum = self.prefFloat("sliderMax")
		sliderPos = self.prefFloat("areaSlider")
		minArea = minimum + sliderPos * (maximum - minimum)
		self.w.minArea.set("%i square units" % minArea)
		return minArea

	def FindSmallPathsMain(self, sender):
		try:
			if not self.SavePreferences(self):
				print("Note: 'Find Small Paths' could not write preferences.")

			minArea = self.CurrentMinArea()
			smallPathsShouldBeDeleted = self.pref("deleteThemRightAway")
			overlapsShouldBeRemovedFirst = self.pref("afterOverlapRemoval")

			if not Glyphs.fonts:
				Message(
					title="No Fonts Open",
					message="Please open at least one font to process.",
					OKButton=None,
				)

			else:
				if self.pref("allFonts") and len(Glyphs.fonts) > 1:
					fontsToLookAt = Glyphs.fonts
				else:
					fontsToLookAt = (Glyphs.font, )

				Glyphs.clearLog()

				print("Looking for paths smaller than %0.1f square units..." % minArea)

				self.w.progress.set(0)
				quarter = 100.0 / len(fontsToLookAt)
				totalCountOfAffectedFonts = 0
				totalCountOfAffectedGlyphs = 0

				for ii, thisFont in enumerate(fontsToLookAt):
					print("\n🔤")
					print("Font: %s" % thisFont.familyName)
					print("Path: %s" % thisFont.filepath)

					numOfGlyphs = len(thisFont.glyphs)
					layersWithSmallPaths = []

					for jj, thisGlyph in enumerate(thisFont.glyphs):
						self.w.progress.set(ii * quarter + jj * quarter / numOfGlyphs)
						if glyphShouldBeIgnored(thisGlyph.name):
							continue

						for thisLayer in thisGlyph.layers:
							if thisLayer.paths and (thisLayer.isMasterLayer or thisLayer.isSpecialLayer):
								if overlapsShouldBeRemovedFirst:
									checkLayer = thisLayer.copyDecomposedLayer()
									checkLayer.removeOverlap()
									if Glyphs.versionNumber >= 3:
										# GLYPHS 3
										checkLayer.flattenOutlines()
								else:
									checkLayer = thisLayer

								countOfAffectedPaths = 0
								# thisGlyph.beginUndo()  # undo grouping causes crashes
								for i in range(len(checkLayer.paths))[::-1]:
									thisPath = checkLayer.paths[i]
									if thisPath.area() < minArea:
										countOfAffectedPaths += 1
										if smallPathsShouldBeDeleted:
											del thisLayer.paths[i]
								if countOfAffectedPaths:
									layersWithSmallPaths.append(thisLayer)
								# thisGlyph.endUndo()  # undo grouping causes crashes
								if countOfAffectedPaths > 0:
									print(
										"  ⚠️ %s, layer '%s': %i path%s found." % (
											thisGlyph.name,
											thisLayer.name,
											countOfAffectedPaths,
											"" if countOfAffectedPaths == 1 else "s",
										)
									)

					if layersWithSmallPaths:
						newTab = thisFont.newTab()
						newTab.layers = layersWithSmallPaths
						totalCountOfAffectedGlyphs += len(layersWithSmallPaths)
						totalCountOfAffectedFonts += 1

					elif not self.pref("allFonts"):
						Message(
							title="No Small Paths Found",
							message="No glyphs with paths smaller than %i square units found in the frontmost font." % minArea,
							OKButton="Cool",
						)

				if len(fontsToLookAt) > 1:
					Message(
						title="Multi-Font Report",
						message="Found %i glyphs in %i fonts (of %i fonts examined) with paths smaller than %i square units. Detailed report in Macro Window." % (
							totalCountOfAffectedGlyphs,
							totalCountOfAffectedFonts,
							len(fontsToLookAt),
							minArea,
						),
						OKButton=None,
					)

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			self.errorReport(e)

	def errorReport(self, e):
		# brings macro window to front and reports error:
		Glyphs.showMacroWindow()
		print("Find Small Paths Error:\n%s\n" % e)
		import traceback
		print(traceback.format_exc())


FindSmallPaths()
