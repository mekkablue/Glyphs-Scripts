# MenuTitle: Batch-Add Smart Axes
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Will add smart axes and additional smart layers to selected glyphs.
"""

import vanilla
from copy import copy
from AppKit import NSFont
from GlyphsApp import Glyphs, Message, GSSmartComponentAxis
from mekkaCore import mekkaObject

defaultRecipe = """
Height: Low: 0
Width: Narrow: 0
# comments are ignored
""".strip()


class BatchAddSmartAxes(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"recipe": defaultRecipe,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 260
		windowWidthResize = 1000  # user can resize width by this value
		windowHeightResize = 1000  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Batch-Add Smart Axes",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Per line: axisName:smartLayerName:smartLayerMinMax (0/1)", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.recipe = vanilla.TextEditor((1, linePos, -1, -inset * 3), text=defaultRecipe, callback=self.SavePreferences, checksSpelling=False)
		self.w.recipe.getNSScrollView().setHasVerticalScroller_(1)
		self.w.recipe.getNSScrollView().setHasHorizontalScroller_(1)
		self.w.recipe.getNSScrollView().setRulersVisible_(0)
		self.w.recipe.getNSTextView().setToolTip_("Syntax:\n<NAME FOR PROPERTY>: <NAME PARTICLE FOR NEW LAYER>: <0=NEW LAYER IS MIN, 1=NEW LAYER IS MAX>\n\nE.g.: Height:High:1, Height:Low:0, Width:Narrow:0, Width:Wide:1, Bend:Straight:0, Bend:Curvy:1")
		legibleFont = NSFont.legibleFontOfSize_(NSFont.systemFontSize())
		textView = self.w.recipe.getNSTextView()
		textView.setFont_(legibleFont)
		textView.setHorizontallyResizable_(1)
		textView.setVerticallyResizable_(1)
		textView.setAutomaticDataDetectionEnabled_(1)
		textView.setAutomaticLinkDetectionEnabled_(1)
		textView.setDisplaysLinkToolTips_(1)
		textView.setUsesFindBar_(1)
		textSize = textView.minSize()
		textSize.width = 500
		textView.setMinSize_(textSize)

		# Run Button:
		self.w.resetButton = vanilla.Button((inset, -20 - inset, 70, -inset), "Reset", sizeStyle="regular", callback=self.reset)
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Smartify", sizeStyle="regular", callback=self.BatchAddSmartAxesMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def reset(self, sender=None):
		self.w.recipe.set(defaultRecipe)
		self.SavePreferences()

	def BatchAddSmartAxesMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					report = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					report = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Batch-Add Smart Axes Report for {report}:")
				print()

				# EXAMPLES:
				"""
				Height: Low: 0
				Height: High: 1
				Width: Narrow: 0
				Width: Wide: 1
				Bend: Straight: 0
				Bend: Curvy: 1
				"""

				# prepare axis input:
				input = self.pref("recipe")
				axisInput = [line.replace(" ", "").strip() for line in input.strip().splitlines() if line.split("#")[0].count(":") == 2]

				print("Parsed input:")
				print("\n".join(axisInput))
				print()

				for selectedLayer in thisFont.selectedLayers:
					thisGlyph = selectedLayer.parent
					print(f"🔡 {thisGlyph.name}...")
					existingAxes = []
					if thisGlyph.smartComponentAxes:
						existingAxes = [a.name for a in thisGlyph.smartComponentAxes]

					# add missing smart axes:
					for axisInfo in axisInput:
						axisName, layerName, isMax = axisInfo.split(":")
						if axisName not in existingAxes:
							print(f"   Adding axis {axisName}...")
							axis = GSSmartComponentAxis()
							axis.name = axisName
							axis.topValue = 100
							axis.bottomValue = 0
							thisGlyph.smartComponentAxes.append(axis)
						else:
							print(f"   Axis already exists: {axisName}")

					# set up master layers:
					for master in thisFont.masters:
						mID = master.id
						masterLayer = thisGlyph.layers[mID]
						print(f"   Setting up master layer {masterLayer.name}...")
						for axisInfo in axisInput:
							axisName, layerName, isMax = axisInfo.split(":")
							isMax = int(isMax)
							axis = thisGlyph.smartComponentAxes[axisName]
							masterLayer.smartComponentPoleMapping[axis.id] = 2 if isMax == 0 else 1

					# add and set up smart layers
					for axisInfo in axisInput:
						axisName, layerName, isMax = axisInfo.split(":")
						isMax = int(isMax)
						axis = thisGlyph.smartComponentAxes[axisName]
						for master in thisFont.masters:
							mID = master.id
							masterLayer = thisGlyph.layers[mID]
							smartLayer = copy(masterLayer)
							smartLayer.name = f"{masterLayer.name} {layerName}"
							smartLayer.smartComponentPoleMapping[axis.id] = 1 if isMax == 0 else 2
							smartLayerExistsAlready = False
							for anyLayer in [layer for layer in thisGlyph.layers if layer.associatedMasterId == mID and not layer.isMasterLayer]:
								if anyLayer.smartComponentPoleMapping == smartLayer.smartComponentPoleMapping:
									smartLayerExistsAlready = True
									print(f"   {smartLayer.name} exists already: {anyLayer.name}")
								else:
									# overwrite setting of other layers:
									try:
										anyLayer.smartComponentPoleMapping[axis.id]  # will throw an error if missing
									except:
										print(f"   Resetting {smartLayer.name}...")
										anyLayer.smartComponentPoleMapping[axis.id] = 2 if isMax == 0 else 1
							if not smartLayerExistsAlready:
								print(f"   Adding layer {smartLayer.name}...")
								smartLayer.associatedMasterId = mID
								thisGlyph.layers.append(smartLayer)

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Batch-Add Smart Axes Error: {e}")
			import traceback
			print(traceback.format_exc())


BatchAddSmartAxes()
