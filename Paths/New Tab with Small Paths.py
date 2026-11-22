# MenuTitle: New Tab with Small Paths
__doc__ = """
Finds small paths (smaller than a user-definable threshold) in glyphs and open a new tab with affected glyphs.
"""

import math
import vanilla
from AppKit import NSColor, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, SteppingEditText, integerFormatter, fontFileName, makeWindowResizable


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
		windowWidth = 360
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"New Tab with Small Paths",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		self.w.text_1 = vanilla.TextBox("auto", "Open new tab with glyphs that contain paths with an area smaller than:", sizeStyle='small')
		self.w.text_1.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.text_1.setToolTip("Glyphs with paths smaller than the area set by the slider below are collected in a new tab.")

		self.w.minArea = vanilla.TextBox("auto", "1000 square units", sizeStyle='small', alignment="center")
		self.w.minArea.setToolTip("The current area threshold in square units, with the side of a square of that size in parentheses (= if exact, ≈ if rounded to full units), or a hint if the minimum and maximum are invalid.")

		formatter = integerFormatter(1)
		self.w.sliderMin = SteppingEditText("auto", "10", sizeStyle='small', callback=self.SliderUpdate, formatter=formatter)
		self.w.sliderMin.setToolTip("Lowest area in square units that the slider can select. Minimum: 1.")
		self.w.sliderMax = SteppingEditText("auto", "1000", sizeStyle='small', callback=self.SliderUpdate, formatter=formatter)
		self.w.sliderMax.setToolTip("Highest area in square units that the slider can select. Must be larger than the minimum.")
		self.w.areaSlider = vanilla.Slider("auto", value=0.1, minValue=0.0, maxValue=1.0, sizeStyle='small', callback=self.SliderUpdate)
		self.w.areaSlider.setToolTip("Sets the area threshold between the minimum and maximum: paths smaller than this are reported.")

		self.w.deleteThemRightAway = vanilla.CheckBox("auto", "Delete Small Paths Right Away", value=False, callback=self.CheckBoxUpdate, sizeStyle='small')
		self.w.deleteThemRightAway.setToolTip("Deletes the small paths immediately instead of only opening a tab. Cannot be combined with the option below.")
		self.w.afterOverlapRemoval = vanilla.CheckBox("auto", "After Decomposition and Overlap Removal (slower)", value=True, callback=self.CheckBoxUpdate, sizeStyle='small')
		self.w.afterOverlapRemoval.setToolTip("Measures path areas after decomposing components and removing overlaps, on a temporary copy of each layer. Cannot be combined with deleting right away.")
		self.w.allFonts = vanilla.CheckBox("auto", "Apply to all open fonts", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allFonts.setToolTip("Processes all open fonts instead of only the frontmost one.")

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero

		# Status line:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready. 💬 See tooltips for help.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows what the script is doing and the result.")
		nsStatus = self.w.status.getNSTextField()
		nsStatus.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		nsStatus.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Open Tab", callback=self.FindSmallPathsMain)
		self.w.runButton.setToolTip("Finds paths below the area threshold and opens a tab with the affected glyphs.")
		self.w.setDefaultButton(self.w.runButton)
		nsRunButton = self.w.runButton.getNSButton()
		nsRunButton.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsRunButton.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes stretch vertically by default; with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-inset-|",
				"H:|-inset-[minArea]-inset-|",
				"H:|-inset-[sliderMin(55)]-gap-[areaSlider]-gap-[sliderMax(55)]-inset-|",
				"H:|-inset-[deleteThemRightAway]-(>=inset)-|",
				"H:|-inset-[afterOverlapRemoval]-(>=inset)-|",
				"H:|-inset-[allFonts]-(>=inset)-|",
				"H:|-inset-[progress]-inset-|",
				"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[text_1(30)]-row-[minArea]-row-[sliderMin]-row-[deleteThemRightAway]-checkRow-[afterOverlapRemoval]-checkRow-[allFonts]-row-[progress(16)]-inset-[runButton]-inset-|",
					{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.areaSlider, "attribute1": "centerY", "view2": self.w.sliderMin, "attribute2": "centerY"},
				{"view1": self.w.sliderMax, "attribute1": "centerY", "view2": self.w.sliderMin, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8, "checkRow": 5},
		)

		# horizontally resizable: the slider, the progress bar and the texts stretch
		makeWindowResizable(self.w)

		# Load Settings:
		self.LoadPreferences()

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
			self.SavePreferences()

			return True
		except Exception as e:
			self.errorReport(e)
			return False

	def SliderUpdate(self, sender):
		try:
			# update the defaults:
			if sender != self.w.areaSlider:
				self.SavePreferences()

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

	def CurrentMinArea(self):
		minimum = self.prefFloat("sliderMin")
		maximum = self.prefFloat("sliderMax")
		sliderPos = self.prefFloat("areaSlider")
		minArea = minimum + sliderPos * (maximum - minimum)
		# the side of a square with that area, rounded to full units: ≈ if it is rounded, = if it is exact
		area = int(minArea)
		side = int(round(math.sqrt(area)))
		sign = "=" if side * side == area else "≈"
		self.w.minArea.set("%i square units (%s%i×%i units)" % (area, sign, side, side))
		return minArea

	def FindSmallPathsMain(self, sender):
		lastItem = "start"
		try:
			self.SavePreferences()

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
				self.setStatus("🛠️ Processing %i font%s…" % (len(fontsToLookAt), "" if len(fontsToLookAt) == 1 else "s"))

				print("Looking for paths smaller than %0.1f square units..." % minArea)

				self.w.progress.set(0)
				quarter = 100.0 / len(fontsToLookAt)
				totalCountOfAffectedFonts = 0
				totalCountOfAffectedGlyphs = 0

				for ii, thisFont in enumerate(fontsToLookAt):
					print("\n🔤")
					print("Font: %s" % thisFont.familyName)
					print("Path: %s" % (fontFileName(thisFont, fullPath=True)))

					numOfGlyphs = len(thisFont.glyphs)
					layersWithSmallPaths = []

					for jj, thisGlyph in enumerate(thisFont.glyphs):
						self.w.progress.set(ii * quarter + jj * quarter / numOfGlyphs)
						if glyphShouldBeIgnored(thisGlyph.name):
							continue

						for thisLayer in thisGlyph.layers:
							if thisLayer.paths and (thisLayer.isMasterLayer or thisLayer.isSpecialLayer):
								lastItem = "%s, layer '%s'" % (thisGlyph.name, thisLayer.name)
								self.setStatus("🔠 %s" % lastItem)
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

				if totalCountOfAffectedGlyphs:
					self.setStatus("✅ Found %i glyph%s in %i font%s with small paths." % (
						totalCountOfAffectedGlyphs,
						"" if totalCountOfAffectedGlyphs == 1 else "s",
						totalCountOfAffectedFonts,
						"" if totalCountOfAffectedFonts == 1 else "s",
					))
				else:
					self.setStatus("⚠️ Nothing found.")

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
			self.setStatus("❌ Error at %s. Details in Macro Window." % lastItem)
			self.errorReport(e)

	def errorReport(self, e):
		# brings macro window to front and reports error:
		Glyphs.showMacroWindow()
		print("Find Small Paths Error:\n%s\n" % e)
		import traceback
		print(traceback.format_exc())


FindSmallPaths()
