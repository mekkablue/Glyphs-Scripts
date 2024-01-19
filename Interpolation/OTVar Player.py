# MenuTitle: OTVar Player
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Plays a glyph in Preview.
"""

import vanilla
import os
import objc
from AppKit import NSTimer
from GlyphsApp import Glyphs, GSInstance, Message
from mekkablue import mekkaObject


def saveFileInLocation(content="blabla", fileName="test.txt", filePath="~/Desktop"):
	saveFileLocation = "%s/%s" % (filePath, fileName)
	saveFileLocation = saveFileLocation.replace("//", "/")
	f = open(saveFileLocation, 'w')
	print("Exporting to:", f.name)
	f.write(content)
	f.close()
	return True


class OTVarGlyphAnimator(mekkaObject):
	prefDict = {
		"slider": 0,
		"delay": 0.05,
		"backAndForth": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 90
		windowWidthResize = 700  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"OTVar Player",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		self.w.slider = vanilla.Slider((15, 12, -15, 15), tickMarkCount=None, callback=self.redrawPreview, continuous=True, sizeStyle="regular", minValue=0, maxValue=100)
		self.w.slower = vanilla.Button((15, -20 - 15, 47, -15), "🚶", sizeStyle='regular', callback=self.slower)
		self.w.slower.getNSButton().setToolTip_("Slower")
		self.w.faster = vanilla.Button((65, -20 - 15, 47, -15), "🏃", sizeStyle='regular', callback=self.faster)
		self.w.faster.getNSButton().setToolTip_("Faster")
		self.w.backAndForth = vanilla.CheckBox((125, -20 - 15, 50, -15), "⇋", value=False, callback=self.SavePreferences, sizeStyle='small')

		# web button:
		self.w.buildWeb = vanilla.Button((-140, -35, -100, -15), "🌍", sizeStyle='regular', callback=self.buildWeb)

		# Run Button:
		self.w.runButton = vanilla.Button((-95, -35, -15, -15), "Play", sizeStyle='regular', callback=self.togglePlay)
		self.w.runButton.getNSButton().setToolTip_("Toggle Play/Pause")
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		self.direction = 1
		self.font = Glyphs.font
		self.originalWeightValue = None
		self.isPlaying = False
		if self.font.instances:
			try:
				# GLYPHS 3
				self.originalWeightValue = self.font.instances[0].axes[0]
			except:
				# GLYPHS 2
				self.originalWeightValue = self.font.instances[0].weightValue

		self.w.bind("close", self.restoreFont)

		# open and initialize the preview area at the bottom
		self.redrawPreview(None)

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def windowIsClosing(self):
		try:
			self.isPlaying = False
			self.setPref("slider", "0")
			return True
		except Exception as e:
			Glyphs.clearLog()
			Glyphs.showMacroWindow()
			print(e)
			print()
			import traceback
			print(traceback.format_exc())
			return False

	def setupWindow(self):
		if not self.font.tabs:
			tabText = "a"
			if self.font.selectedLayers:
				tabText = "".join([layer.parent.name for layer in self.font.selectedLayers])
			self.font.newTab(tabText)
		if self.font.currentTab.previewHeight <= 1.0:
			self.font.currentTab.previewHeight = 200
		if not self.font.instances:
			newInstance = GSInstance()
			newInstance.name = "Preview Instance"
			self.font.instances.append(newInstance)
		self.font.currentTab.previewInstances = self.font.instances[0]

	def restoreFont(self, sender):
		if self.originalWeightValue is not None:
			try:
				# GLYPHS 3
				self.font.instances[0].axes[0] = self.originalWeightValue
			except:
				# GLYPHS 2
				self.font.instances[0].weightValue = self.originalWeightValue

		else:
			self.font.instances = []

		# turn playing off when window is closed, otherwise it goes on forever:
		self.isPlaying = False

		# reset slider and redraw the preview area:
		self.setPref("slider", 0)
		Glyphs.redraw()

	def redrawPreview(self, sender):
		try:
			self.setupWindow()

			# get Slider position
			sliderPos = self.w.slider.get() / 100.0
			try:
				# GLYPHS 3
				weights = [m.axes[0] for m in self.font.masters]
			except:
				# GLYPHS 2
				weights = [m.weightValue for m in self.font.masters]

			if self.font.customParameters["Virtual Master"]:
				weights.append(self.font.customParameters["Virtual Master"][0]["Location"])
			minWt = min(weights)
			maxWt = max(weights)
			sliderWt = minWt + sliderPos * (maxWt - minWt)

			# apply to preview instance and redraw
			try:
				# GLYPHS 3
				self.font.instances[0].axes[0] = sliderWt
				self.font.instances[0].updateInterpolationValues()
			except:
				# GLYPHS 2
				self.font.instances[0].weightValue = sliderWt
				self.font.currentTab.updatePreview()

				# not necessary anymore, I think:
				# self.font.currentTab.forceRedraw()
				# self.font.updateInterface()

			self.SavePreferences()
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("OTVar Glyph Animator Error: %s" % e)
			import traceback
			print(traceback.format_exc())

	def togglePlay(self, sender):
		self.w.makeKey()
		self.isPlaying = not self.isPlaying
		if self.isPlaying:
			self.w.runButton.setTitle("Pause")
			self.play_(None)
		else:
			self.w.runButton.setTitle("Play")

	def play_(self, sender):
		try:
			if not self.prefBool("backAndForth"):
				self.direction = 1

			# finer steps when played slowly:
			smoothnessFactor = 1
			if self.prefFloat("delay") > 0.07:
				smoothnessFactor = 3
			elif self.prefFloat("delay") > 0.05:
				smoothnessFactor = 2

			# execute an animation step:
			if self.isPlaying:
				# Move Slider:
				sliderPos = self.w.slider.get()
				if sliderPos >= 100:
					if not self.prefBool("backAndForth"):
						sliderPos = 0
					else:
						sliderPos = 99.9999
						self.direction = -1
				elif sliderPos <= 0:
					sliderPos = 0.0001
					if self.direction == -1:
						self.direction = 1

				else:
					sliderPos += self.direction * 2.0 / smoothnessFactor
				self.w.slider.set(sliderPos)

				# Trigger Redraw:
				self.redrawPreview(None)
				self.font.currentTab.updatePreview()

				# Call this method again after a delay:
				playSignature = objc.selector(self.play_, signature=b'v@:')
				self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
					self.prefFloat("delay") / smoothnessFactor,  # interval
					self,  # target
					playSignature,  # selector
					None,  # userInfo
					False  # repeat
				)
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("OTVar Glyph Animator Error: %s" % e)
			import traceback
			print(traceback.format_exc())

	def slower(self, sender):
		delay = self.prefFloat("delay")
		if delay <= 0.1:
			delay += 0.01
			self.w.faster.enable(onOff=True)
		else:
			# disable slower button at slowest setting:
			self.w.slower.enable(onOff=False)
		self.setPref("delay", delay)

	def faster(self, sender):
		delay = self.prefFloat("delay")
		if delay > 0.01:
			delay -= 0.005
			self.w.slower.enable(onOff=True)
		else:
			# disable faster button at fastest setting:
			self.w.faster.enable(onOff=False)
		self.setPref("delay", delay)

	def buildWeb(self, sender):
		weightAxisPositions = []
		for m in self.font.masters:
			if m.customParameters["Axis Location"]:
				axisPos = m.customParameters["Axis Location"][0]["Location"]
			else:
				try:
					# GLYPHS 3
					axisPos = m.axes[0]
				except:
					# GLYPHS 2
					axisPos = m.weightValue

			weightAxisPositions.append(int(axisPos))

		if self.font.customParameters["Virtual Master"]:
			weightAxisPositions.append(self.font.customParameters["Virtual Master"][0]["Location"])

		firstAxisTag = "wght"
		if self.font.customParameters["Axes"]:
			firstAxisTag = self.font.customParameters["Axes"][0]["Tag"]

		htmlCode = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@font-face {
	font-family: "%s";
	src: url("%sGX.ttf");
}
@keyframes Looper {
	from {
		font-variation-settings: "%s" %i;
	}
	to {
		font-variation-settings: "%s" %i;
	}
}
body {
	font: 360px "%s";
	animation: Looper %.1fs alternate ease-in-out 0s infinite;
}
</style>
</head>
<body>%s</body>
</html>""" % (
			self.font.familyName, self.font.familyName.replace(" ", ""), firstAxisTag, min(weightAxisPositions), firstAxisTag, max(weightAxisPositions), self.font.familyName,
			self.prefFloat("delay") * 50, " ".join(["&#x%s;" % g.unicode for g in self.font.glyphs if g.unicode and g.export])
		)

		exportPath = None
		if bool(Glyphs.defaults["GXPluginUseExportPath"]):
			exportPath = Glyphs.defaults["GXExportPath"]
		else:
			exportPath = Glyphs.defaults["GXExportPathManual"]

		print("exportPath:", exportPath)
		if exportPath:
			if saveFileInLocation(content=htmlCode, fileName="font_animation.html", filePath=exportPath):
				print("Successfully wrote file to disk.")
				terminalCommand = u'cd "%s"; open .' % exportPath
				os.system(terminalCommand)
			else:
				print("Error writing file to disk.")
		else:
			Message(
				title="Cannot Create HTML for OTVar",
				message="Could not determine export path of your OTVar font. Export an OTVar font first, the HTML will be saved next to it.",
				OKButton=None
			)


OTVarGlyphAnimator()
