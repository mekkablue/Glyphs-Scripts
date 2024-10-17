# MenuTitle: Anchor Mover
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Batch-process anchor positions in selected glyphs (GUI).
"""

import vanilla
import math
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSOFFCURVE, Message, GSMetricsTypexHeight, GSMetricsTypeItalicAngle, GSMetricsTypeAscender, GSMetricsTypeCapHeight, GSMetricsTypeDescender, GSMetricsTypeMidHeight, GSMetricsTypeBodyHeight, GSMetricsTypeSlantHeight, GSMetricsTypeBaseline
from mekkablue import mekkaObject, UpdateButton
from mekkablue.geometry import transform, italicize


def highestNodeInLayer(layer):
	highest = None
	for p in layer.paths:
		for n in p.nodes:
			if n.type != GSOFFCURVE:
				if highest is None or highest.y < n.y:
					highest = n
	return highest


def lowestNodeInLayer(layer):
	lowest = None
	for p in layer.paths:
		for n in p.nodes:
			if n.type != GSOFFCURVE:
				if lowest is None or lowest.y > n.y:
					lowest = n
	return lowest


def rightmostNodeInLayer(layer):
	rightmost = None
	for p in layer.paths:
		for n in p.nodes:
			if n.type != GSOFFCURVE:
				if rightmost is None or rightmost.x < n.x:
					rightmost = n
	return rightmost


def leftmostNodeInLayer(layer):
	leftmost = None
	for p in layer.paths:
		for n in p.nodes:
			if n.type != GSOFFCURVE:
				if leftmost is None or leftmost.x > n.x:
					leftmost = n
	return leftmost


listHorizontal = (
	("current position", "copyAnchor.x"),
	("LSB", "0.0"),
	("RSB", "copyLayer.width"),
	("center", "copyLayer.width // 2.0"),
	("bbox left edge", "copyLayer.fastBounds().origin.x"),
	("bbox center", "copyLayer.fastBounds().origin.x + copyLayer.fastBounds().size.width // 2.0"),
	("bbox right edge", "copyLayer.fastBounds().origin.x + copyLayer.fastBounds().size.width"),
	("highest node", "highestNodeInLayer(copyLayer).x"),
	("lowest node", "lowestNodeInLayer(copyLayer).x"),
)

listVertical = (
	("current position", "copyAnchor.y"),
	("ascender", "selectedAscender"),
	("cap height", "selectedCapheight"),
	("mid height", "selectedMidHeight"),
	("body height", "selectedBodyHeight"),
	("x-height/smallcap height", "selectedXheight"),
	("slant height", "selectedSlantHeight"),
	("half ascender", "selectedAscender // 2.0"),
	("half cap height", "selectedCapheight // 2.0"),
	("half mid height", "selectedMidHeight // 2.0"),
	("half body height", "selectedBodyHeight // 2.0"),
	("half x-height/smallcap height", "halfXHeight"),
	("baseline", "selectedBaseline"),
	("descender", "selectedDescender"),
	("bbox top", "copyLayer.fastBounds().origin.y + copyLayer.fastBounds().size.height"),
	("bbox center", "copyLayer.fastBounds().origin.y + (copyLayer.fastBounds().size.height // 2.0)"),
	("bbox bottom", "copyLayer.fastBounds().origin.y"),
	("leftmost node", "leftmostNodeInLayer(copyLayer).y"),
	("rightmost node", "rightmostNodeInLayer(copyLayer).y"),
)


def italicSkew(x, y, angle=10.0):
	"""Skews x/y along the x-axis and returns skewed x value."""
	newAngle = (angle / 180.0) * math.pi
	return x + y * math.tan(newAngle)


class AnchorMover2(mekkaObject):
	prefDict = {
		"anchorName": "",
		"hTarget": 0.0,
		"hChange": 0.0,
		"vTarget": 0.0,
		"vChange": 0.0,
		"italic": True,
		"allMasters": False,
		"verbose": False,
	}

	def __init__(self):
		windowWidth = 500
		windowHeight = 200
		windowWidthResize = 700  # user can resize width by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Anchor Mover",  # window title
			minSize=(windowWidth - 130, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		linePos, inset, lineHeight = 12, 15, 22

		self.w.text_1 = vanilla.TextBox((inset, linePos + 1, inset + 60, 14), "Move anchor", sizeStyle='small')
		self.w.anchorName = vanilla.ComboBox((inset + 75, linePos - 2, -105 - inset - 25, 18), self.GetAnchorNames(), sizeStyle='small', callback=self.SavePreferences)
		self.w.button = UpdateButton((-105 - inset - 16, linePos - 3, -110 - inset, 16), callback=self.SetAnchorNames)
		self.w.text_2 = vanilla.TextBox((-105 - 12, linePos + 1, -inset, 14), "in selected glyphs", sizeStyle='small')
		linePos += lineHeight

		self.w.hText_1 = vanilla.TextBox((inset - 2, linePos, 20, 14), "↔")
		self.w.hText_2 = vanilla.TextBox((inset + 20, linePos + 2, 20, 14), "to", sizeStyle='small')
		self.w.hTarget = vanilla.PopUpButton((inset + 40, linePos, -50 - 15 - 15 - inset, 17), [x[0] for x in listHorizontal], sizeStyle='small', callback=self.SavePreferences)
		self.w.hText_3 = vanilla.TextBox((-60 - 15 - 15, linePos + 2, -50 - inset, 14), "+", sizeStyle='small')
		self.w.hChange = vanilla.EditText((-60 - 15, linePos, -inset, 19), "0.0", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.vText_1 = vanilla.TextBox((inset, linePos, 20, 14), "↕")
		self.w.vText_2 = vanilla.TextBox((inset + 20, linePos + 2, 20, 14), "to", sizeStyle='small')
		self.w.vTarget = vanilla.PopUpButton((inset + 40, linePos, -50 - 15 - 15 - inset, 17), [y[0] for y in listVertical], sizeStyle='small', callback=self.SavePreferences)
		self.w.vText_3 = vanilla.TextBox((-60 - 15 - 15, linePos + 2, -50 - inset, 14), "+", sizeStyle='small')
		self.w.vChange = vanilla.EditText((-60 - 15, linePos, -inset, 19), "0.0", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.italic = vanilla.CheckBox((inset + 2, linePos, -inset, 18), "Respect italic angle", value=True, sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.allMasters = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "All masters and special layers (otherwise only current masters)", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.verbose = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Log in Macro window (slow, use for tracking errors)", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.moveButton = vanilla.Button((-80 - 15, -20 - 15, -15, -15), "Move", callback=self.MoveCallback)
		self.w.setDefaultButton(self.w.moveButton)

		self.LoadPreferences()

		self.w.open()
		self.w.makeKey()

	def MoveCallback(self, sender):
		# brings macro window to front and clears its log:
		Glyphs.clearLog()

		thisFont = Glyphs.font
		selectedLayers = thisFont.selectedLayers
		anchorName = self.pref("anchorName")
		horizontalIndex = self.prefInt("hTarget")
		horizontalChange = self.prefFloat("hChange")
		verticalIndex = self.prefInt("vTarget")
		verticalChange = self.prefFloat("vChange")
		allMasters = self.pref("allMasters")
		respectItalic = self.pref("italic")
		verbose = self.pref("verbose")

		evalCodeH = listHorizontal[horizontalIndex][1]
		evalCodeV = listVertical[verticalIndex][1]

		if not selectedLayers:
			if verbose:
				print("No glyphs selected.")
			Message(title="No Glyphs Selected", message="Could not move anchors. No glyphs were selected.", OKButton=None)
		else:
			if verbose:
				print("Processing %i glyph%s..." % (
					len(selectedLayers),
					"" if len(selectedLayers) == 1 else "s",
				))
			thisFont.disableUpdateInterface()
			try:
				for selectedLayer in selectedLayers:
					selectedGlyph = selectedLayer.glyph()
					if not selectedGlyph:
						continue
					if verbose:
						print(f"\n🔠 {selectedGlyph.name}")
					if allMasters:
						originalLayers = tuple([layer for layer in selectedGlyph.layers if layer.isMasterLayer or layer.isSpecialLayer])
					else:
						originalLayers = (selectedLayer, )

					for originalLayer in originalLayers:
						selectedAscender = originalLayer.metricForType_(GSMetricsTypeAscender)
						selectedCapheight = originalLayer.metricForType_(GSMetricsTypeCapHeight)
						selectedDescender = originalLayer.metricForType_(GSMetricsTypeDescender)
						selectedXheight = originalLayer.metricForType_(GSMetricsTypexHeight)
						if selectedXheight == 0.0:  # bug in Glyphs 3.3?
							selectedXheight = originalLayer.associatedFontMaster().xHeight
						halfXHeight = selectedXheight * 0.5
						selectedMidHeight = originalLayer.metricForType_(GSMetricsTypeMidHeight)
						selectedBodyHeight = originalLayer.metricForType_(GSMetricsTypeBodyHeight)
						selectedSlantHeight = originalLayer.metricForType_(GSMetricsTypeSlantHeight)
						selectedBaseline = originalLayer.metricForType_(GSMetricsTypeBaseline)
						italicAngle = originalLayer.metricForType_(GSMetricsTypeItalicAngle)

						if len(originalLayer.anchors) == 0:
							if verbose:
								print(f"⚠️ no anchors on layer ‘{originalLayer.name}’.")
							continue

						thisGlyph = originalLayer.parent

						# create a layer copy that can be slanted backwards if necessary
						copyLayer = originalLayer.copyDecomposedLayer()
						copyLayer.decomposeCorners()
						# thisGlyph.beginUndo()  # undo grouping causes crashes

						try:
							if italicAngle and respectItalic:
								# slant the layer copy backwards
								moveDown = transform(shiftY=-halfXHeight).transformStruct()
								skewBack = transform(skew=-italicAngle).transformStruct()
								moveUp = transform(shiftY=halfXHeight).transformStruct()
								copyLayer.applyTransform(moveDown)
								copyLayer.applyTransform(skewBack)
								copyLayer.applyTransform(moveUp)

							for copyAnchor in copyLayer.anchors:
								if copyAnchor.name != anchorName:
									continue

								oldAnchorX = copyAnchor.x
								oldAnchorY = copyAnchor.y
								xMove = eval(evalCodeH) + horizontalChange
								yMove = eval(evalCodeV) + verticalChange

								# Ignore moves relative to bbox if there are no paths:
								if not copyLayer.paths:
									if "bounds" in evalCodeH:
										xMove = oldAnchorX

									if "bounds" in evalCodeV:
										yMove = oldAnchorY

								# Only move if the calculated position differs from the original one:
								originalAnchor = originalLayer.anchors[anchorName]
								if int(oldAnchorX) != int(xMove) or int(oldAnchorY) != int(yMove):
									if italicAngle and respectItalic:
										# skew back
										originalAnchor.position = italicize(NSPoint(xMove, yMove), italicAngle, halfXHeight)
									else:
										originalAnchor.position = NSPoint(xMove, yMove)
									if verbose:
										print(f"⚓️ {anchorName} → {originalAnchor.x}, {originalAnchor.y} in layer: {originalLayer.name}.")
								elif verbose:
									print(f"⚓️ {anchorName} anchor unchanged in {originalLayer.name}.")

						except Exception as e:
							print(f"ERROR: Failed to move anchor in {thisGlyph.name}.")
							print(e)
							import traceback
							print(traceback.format_exc())

			except Exception as e:
				raise e
			finally:
				thisFont.enableUpdateInterface()
		print("Done.")

	def GetAnchorNames(self):
		myAnchorList = []
		selectedLayers = Glyphs.currentDocument.selectedLayers()
		try:
			for thisLayer in selectedLayers:
				anchorNames = list(thisLayer.anchors.keys())  # hack to avoid traceback
				for thisAnchorName in anchorNames:
					if thisAnchorName not in myAnchorList:
						myAnchorList.append(thisAnchorName)
		except:
			print("Error: Cannot collect anchor names from the current selection.")

		return sorted(myAnchorList)

	def SetAnchorNames(self, sender):
		anchorList = self.GetAnchorNames()
		self.w.anchorName.setItems(anchorList)


AnchorMover2()
