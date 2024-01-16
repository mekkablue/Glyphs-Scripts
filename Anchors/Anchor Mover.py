# MenuTitle: Anchor Mover
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Batch-process anchor positions in selected glyphs (GUI).
"""

import vanilla
import math
from Foundation import NSPoint
from AppKit import NSAffineTransform, NSAffineTransformStruct
from GlyphsApp import Glyphs, GSOFFCURVE, Message


def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
	"""
	Returns an NSAffineTransform object for transforming layers.
	Apply an NSAffineTransform t object like this:
		Layer.transform_checkForSelection_doComponents_(t,False,True)
	Access its transformation matrix like this:
		tMatrix = t.transformStruct()  # returns the 6-float tuple
	Apply the matrix tuple like this:
		Layer.applyTransform(tMatrix)
		Component.applyTransform(tMatrix)
		Path.applyTransform(tMatrix)
	Chain multiple NSAffineTransform objects t1, t2 like this:
		t1.appendTransform_(t2)
	"""
	myTransform = NSAffineTransform.transform()
	if rotate:
		myTransform.rotateByDegrees_(rotate)
	if scale != 1.0:
		myTransform.scaleBy_(scale)
	if not (shiftX == 0.0 and shiftY == 0.0):
		myTransform.translateXBy_yBy_(shiftX, shiftY)
	if skew:
		skewStruct = NSAffineTransformStruct()
		skewStruct.m11 = 1.0
		skewStruct.m22 = 1.0
		skewStruct.m21 = math.tan(math.radians(skew))
		skewTransform = NSAffineTransform.transform()
		skewTransform.setTransformStruct_(skewStruct)
		myTransform.appendTransform_(skewTransform)
	return myTransform


def italicize(thisPoint, italicAngle=0.0, pivotalY=0.0):
	"""
	Returns the italicized position of an NSPoint 'thisPoint'
	for a given angle 'italicAngle' and the pivotal height 'pivotalY',
	around which the italic slanting is executed, usually half x-height.
	Usage: myPoint = italicize(myPoint,10,xHeight*0.5)
	"""
	x = thisPoint.x
	yOffset = thisPoint.y - pivotalY  # calculate vertical offset
	italicAngle = math.radians(italicAngle)  # convert to radians
	tangens = math.tan(italicAngle)  # math.tan needs radians
	horizontalDeviance = tangens * yOffset  # vertical distance from pivotal point
	x += horizontalDeviance  # x of point that is yOffset from pivotal point
	return NSPoint(x, thisPoint.y)


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
	("bbox right edge", "copyLayer.fastBounds().origin.x + copyLayer.bofastBounds()unds.size.width"),
	("highest node", "highestNodeInLayer(copyLayer).x"),
	("lowest node", "lowestNodeInLayer(copyLayer).x"),
)

listVertical = (
	("current position", "copyAnchor.y"),
	("ascender", "selectedAscender"),
	("cap height", "selectedCapheight"),
	("smallcap height", "originalMaster.customParameters['smallCapHeight']"),
	("x-height", "selectedXheight"),
	("half ascender", "selectedAscender // 2.0"),
	("half cap height", "selectedCapheight // 2.0"),
	("half smallcap height", "originalMaster.customParameters['smallCapHeight']/2"),
	("half x-height", "selectedXheight // 2.0"),
	("baseline", "0.0"),
	("descender", "selectedDescender"),
	("bbox top", "copyLayer.fastBounds().origin.y + copyLayer.fastBounds().size.height"),
	("bbox center", "copyLayer.fastBounds().origin.y + ( copyLayer.fastBounds().size.height // 2.0 )"),
	("bbox bottom", "copyLayer.fastBounds().origin.y"),
	("leftmost node", "leftmostNodeInLayer(copyLayer).y"),
	("rightmost node", "rightmostNodeInLayer(copyLayer).y"),
)


def italicSkew(x, y, angle=10.0):
	"""Skews x/y along the x axis and returns skewed x value."""
	new_angle = (angle / 180.0) * math.pi
	return x + y * math.tan(new_angle)


class AnchorMover2(object):
	prefID = "com.mekkablue.AnchorMover2"

	def __init__(self):
		linePos, inset, lineHeight = 12, 15, 22

		self.w = vanilla.FloatingWindow((500, 175), "Anchor Mover", minSize=(370, 175), maxSize=(1000, 175), autosaveName=self.pref("mainwindow"))

		self.w.text_1 = vanilla.TextBox((inset, linePos + 2, inset + 60, 14), "Move anchor", sizeStyle='small')
		self.w.anchor_name = vanilla.ComboBox((inset + 75, linePos - 1, -110 - inset - 25, 19), self.GetAnchorNames(), sizeStyle='small', callback=self.SavePreferences)
		self.w.button = vanilla.SquareButton((-110 - inset - 20, linePos, -110 - inset, 18), u"↺", sizeStyle='small', callback=self.SetAnchorNames)
		self.w.text_2 = vanilla.TextBox((-105 - 15, linePos + 2, -inset, 14), "in selected glyphs:", sizeStyle='small')
		linePos += lineHeight

		self.w.hText_1 = vanilla.TextBox((inset - 2, linePos, 20, 14), u"↔", sizeStyle='regular')
		self.w.hText_2 = vanilla.TextBox((inset + 20, linePos + 2, 20, 14), "to", sizeStyle='small')
		self.w.hTarget = vanilla.PopUpButton((inset + 40, linePos, -50 - 15 - 15 - inset, 17), [x[0] for x in listHorizontal], sizeStyle='small', callback=self.SavePreferences)
		self.w.hText_3 = vanilla.TextBox((-60 - 15 - 15, linePos + 2, -50 - inset, 14), "+", sizeStyle='small')
		self.w.hChange = vanilla.EditText((-60 - 15, linePos, -inset, 19), "0.0", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.vText_1 = vanilla.TextBox((inset, linePos, 20, 14), u"↕", sizeStyle='regular')
		self.w.vText_2 = vanilla.TextBox((inset + 20, linePos + 2, 20, 14), "to", sizeStyle='small')
		self.w.vTarget = vanilla.PopUpButton((inset + 40, linePos, -50 - 15 - 15 - inset, 17), [y[0] for y in listVertical], sizeStyle='small', callback=self.SavePreferences)
		self.w.vText_3 = vanilla.TextBox((-60 - 15 - 15, linePos + 2, -50 - inset, 14), "+", sizeStyle='small')
		self.w.vChange = vanilla.EditText((-60 - 15, linePos, -inset, 19), "0.0", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.italic = vanilla.CheckBox((inset, linePos, -inset, 18), "Respect italic angle", value=True, sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.allMasters = vanilla.CheckBox((inset, linePos, -inset, 20), u"All masters and special layers (otherwise only current masters)", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.moveButton = vanilla.Button((-80 - 15, -20 - 15, -15, -15), "Move", sizeStyle='regular', callback=self.MoveCallback)
		self.w.setDefaultButton(self.w.moveButton)

		if not self.LoadPreferences():
			print("Error: Could not load preferences. Will resort to defaults.")

		self.w.open()
		self.w.makeKey()

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()

	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			Glyphs.defaults[self.domain("anchor_name")] = self.w.anchor_name.get()
			Glyphs.defaults[self.domain("hTarget")] = self.w.hTarget.get()
			Glyphs.defaults[self.domain("hChange")] = self.w.hChange.get()
			Glyphs.defaults[self.domain("vTarget")] = self.w.vTarget.get()
			Glyphs.defaults[self.domain("vChange")] = self.w.vChange.get()
			Glyphs.defaults[self.domain("italic")] = self.w.italic.get()
			Glyphs.defaults[self.domain("allMasters")] = self.w.allMasters.get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			# register defaults:
			Glyphs.registerDefault(self.domain("anchor_name"), "")
			Glyphs.registerDefault(self.domain("hTarget"), 0.0)
			Glyphs.registerDefault(self.domain("hChange"), 0.0)
			Glyphs.registerDefault(self.domain("vTarget"), 0.0)
			Glyphs.registerDefault(self.domain("vChange"), 0.0)
			Glyphs.registerDefault(self.domain("italic"), True)
			Glyphs.registerDefault(self.domain("allMasters"), False)

			# load previously written prefs:
			self.w.anchor_name.set(self.pref("anchor_name"))
			self.w.hTarget.set(self.pref("hTarget"))
			self.w.hChange.set(self.pref("hChange"))
			self.w.vTarget.set(self.pref("vTarget"))
			self.w.vChange.set(self.pref("vChange"))
			self.w.italic.set(self.pref("italic"))
			self.w.allMasters.set(self.pref("allMasters"))
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def prefAsFloat(self, pref):
		try:
			preference = self.pref(pref)
			return float(preference)
		except:
			Glyphs.defaults[self.domain(pref)] = 0.0
			self.LoadPreferences()
			return 0.0

	def MoveCallback(self, sender):
		# brings macro window to front and clears its log:
		Glyphs.clearLog()

		thisFont = Glyphs.font
		selectedLayers = thisFont.selectedLayers
		anchor_name = self.pref("anchor_name")
		horizontal_index = self.pref("hTarget")
		horizontal_change = self.prefAsFloat("hChange")
		vertical_index = self.pref("vTarget")
		vertical_change = self.prefAsFloat("vChange")
		allMasters = self.pref("allMasters")
		respectItalic = self.pref("italic")

		evalCodeH = listHorizontal[horizontal_index][1]
		evalCodeV = listVertical[vertical_index][1]

		if not selectedLayers:
			print("No glyphs selected.")
			Message(title="No Glyphs Selected", message="Could not move anchors. No glyphs were selected.", OKButton=None)
		else:
			print("Processing %i glyph%s..." % (
				len(selectedLayers),
				"" if len(selectedLayers) == 1 else "s",
			))
			thisFont.disableUpdateInterface()
			try:
				for selectedLayer in selectedLayers:
					selectedGlyph = selectedLayer.glyph()
					if selectedGlyph:
						print("\n🔠 %s" % selectedGlyph.name)
						if allMasters:
							originalLayers = tuple([layer for layer in selectedGlyph.layers if layer.isMasterLayer or layer.isSpecialLayer])
						else:
							originalLayers = (selectedLayer, )

						for originalLayer in originalLayers:
							originalMaster = originalLayer.master
							selectedAscender = originalMaster.ascender
							selectedCapheight = originalMaster.capHeight
							selectedDescender = originalMaster.descender
							selectedXheight = originalMaster.xHeight
							halfXHeight = selectedXheight * 0.5
							italicAngle = originalMaster.italicAngle

							if len(originalLayer.anchors) == 0:
								print("⚠️ no anchors on layer %s." % originalLayer.name)
							else:
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
										if copyAnchor.name == anchor_name:
											old_anchor_x = copyAnchor.x
											old_anchor_y = copyAnchor.y
											xMove = eval(evalCodeH) + horizontal_change
											yMove = eval(evalCodeV) + vertical_change

											# Ignore moves relative to bbox if there are no paths:
											if not copyLayer.paths:
												if "bounds" in evalCodeH:
													xMove = old_anchor_x

												if "bounds" in evalCodeV:
													yMove = old_anchor_y

											# Only move if the calculated position differs from the original one:
											originalAnchor = originalLayer.anchors[anchor_name]
											if int(old_anchor_x) != int(xMove) or int(old_anchor_y) != int(yMove):
												if italicAngle and respectItalic:
													# skew back
													originalAnchor.position = italicize(NSPoint(xMove, yMove), italicAngle, halfXHeight)
												else:
													originalAnchor.position = NSPoint(xMove, yMove)
												print("⚓️ %s → %i, %i in layer: %s." % (anchor_name, originalAnchor.x, originalAnchor.y, originalLayer.name))
											else:
												print("⚓️ %s anchor unchanged in %s." % (anchor_name, originalLayer.name))

								except Exception as e:
									print("ERROR: Failed to move anchor in %s." % thisGlyph.name)
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
				AnchorNames = list(thisLayer.anchors.keys())  # hack to avoid traceback
				for thisAnchorName in AnchorNames:
					if thisAnchorName not in myAnchorList:
						myAnchorList.append(thisAnchorName)
		except:
			print("Error: Cannot collect anchor names from the current selection.")

		return sorted(myAnchorList)

	def SetAnchorNames(self, sender):
		anchorList = self.GetAnchorNames()
		self.w.anchor_name.setItems(anchorList)


AnchorMover2()
