# MenuTitle: Batch Insert Anchor
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Insert an anchor in all selected glyphs, on all layers, and pick the approximate spot.
"""

import vanilla
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSAnchor
from mekkablue import mekkaObject

xPositions = ("Center of Width", "LSB", "RSB", "BBox Left Edge", "BBox Horizontal Center", "BBox Right Edge")
yPositions = ("Baseline", "x-Height", "Smallcap Height", "Cap Height", "Ascender", "Shoulder Height", "Descender", "BBox Top", "BBox Center", "BBox Bottom")


class BatchInsertAnchor(mekkaObject):
	prefDict = {
		"anchorName": "top",
		"xPos": 0,
		"yPos": 0,
		"replaceExisting": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 180
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Batch Insert Anchor",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), u"In selected glyphs, insert this anchor on all layers:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.anchorNameText = vanilla.TextBox((inset, linePos + 2, 90, 14), u"Anchor Name:", sizeStyle='small', selectable=True)
		self.w.anchorName = vanilla.EditText((inset + 90, linePos - 1, -inset, 19), "_connect", callback=self.SavePreferences, sizeStyle='small')
		self.w.anchorName.getNSTextField().setToolTip_(u"Name of the anchor that will be inserted.")
		linePos += lineHeight

		self.w.xPosText = vanilla.TextBox((inset, linePos + 2, 90, 14), u"H Position:", sizeStyle='small', selectable=True)
		self.w.xPos = vanilla.PopUpButton((inset + 90, linePos, -inset, 17), xPositions, sizeStyle='small', callback=self.SavePreferences)

		# vanilla legacy support
		try:
			self.w.xPos.getNSPopUpButton().setToolTip_(u"The x coordinate of the anchor.")
		except:
			self.w.xPos.getNSButton().setToolTip_(u"The x coordinate of the anchor.")
		linePos += lineHeight

		self.w.yPosText = vanilla.TextBox((inset, linePos + 2, 90, 14), u"V Position:", sizeStyle='small', selectable=True)
		self.w.yPos = vanilla.PopUpButton((inset + 90, linePos, -inset, 17), yPositions, sizeStyle='small', callback=self.SavePreferences)

		# vanilla legacy support
		try:
			self.w.yPos.getNSPopUpButton().setToolTip_(u"The y coordinate of the anchor.")
		except:
			self.w.yPos.getNSButton().setToolTip_(u"The y coordinate of the anchor.")

		linePos += lineHeight

		self.w.replaceExisting = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Replace Existing Anchors with Same Name", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.replaceExisting.getNSButton().setToolTip_(u"If enabled, will delete anchors that have the same name of the one you are adding, before it is added again at the specified spot. If disabled, the script will skip layers that already have an anchor of the same name.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Insert", callback=self.BatchInsertAnchorMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def BatchInsertAnchorMain(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			print("Batch Insert Anchor Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()

			anchorName = self.pref("anchorName")
			xPos = self.pref("xPos")
			yPos = self.pref("yPos")
			replaceExisting = self.pref("replaceExisting")

			selectedLayers = thisFont.selectedLayers
			selectedGlyphNames = list(set([layer.parent.name for layer in selectedLayers if layer.parent]))

			print("Inserting anchor '%s' at %s and %s in %i glyphs...\n" % (
				anchorName,
				xPositions[xPos],
				yPositions[yPos],
				len(selectedGlyphNames),
			))

			for glyphName in selectedGlyphNames:
				print("🔠 %s" % glyphName)
				glyph = thisFont.glyphs[glyphName]
				if not glyph:
					print("⛔️ Error: could not find glyph %s. Skipping.\n" % glyphName)
				else:
					for thisLayer in glyph.layers:
						if replaceExisting or not thisLayer.anchors[anchorName]:
							if xPos == 0:
								x = thisLayer.width // 2
							elif xPos == 1:  # "LSB"
								x = 0.0
							elif xPos == 2:  # "RSB"
								x = thisLayer.width
							elif xPos == 3:  # "BBox Left Edge"
								x = thisLayer.bounds.origin.x
							elif xPos == 4:  # "BBox Horizontal Center"
								x = thisLayer.bounds.origin.x + thisLayer.bounds.size.width // 2
							elif xPos == 5:  # "BBox Right Edge"
								x = thisLayer.bounds.origin.x + thisLayer.bounds.size.width

							if yPos == 0:  # "Baseline"
								y = 0.0
							if yPos == 1:  # "x-Height"
								y = thisLayer.master.xHeight
							if yPos == 2:  # "Smallcap Height"
								y = thisLayer.master.customParameters["smallCapHeight"]
								if not y:  # Fallback if not set:
									y = thisLayer.master.xHeight
							if yPos == 3:  # "Cap Height"
								y = thisLayer.master.capHeight
							if yPos == 4:  # "Ascender"
								y = thisLayer.master.ascender
							if yPos == 5:  # "Shoulder Height"
								y = thisLayer.master.customParameters["shoulderHeight"]
								if not y:  # Fallback if not set:
									y = thisLayer.master.capHeight
							if yPos == 6:  # "Descender"
								y = thisLayer.master.descender
							if yPos == 7:  # "BBox Top"
								y = thisLayer.bounds.origin.y + thisLayer.bounds.size.height
							if yPos == 8:  # "BBox Center"
								y = thisLayer.bounds.origin.y + thisLayer.bounds.size.height // 2
							if yPos == 9:  # "BBox Bottom"
								y = thisLayer.bounds.origin.y

							anchor = GSAnchor()
							anchor.name = anchorName
							anchor.position = NSPoint(x, y)
							thisLayer.anchors.append(anchor)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Batch Insert Anchor Error: {e}")
			import traceback
			print(traceback.format_exc())


BatchInsertAnchor()
