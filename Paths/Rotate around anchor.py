# MenuTitle: Rotate Around Anchor
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Rotate selected glyphs (or selected paths and components) around a 'rotate' anchor.
"""

import vanilla
from Foundation import NSPoint, NSAffineTransform
from GlyphsApp import Glyphs, GSAnchor
from mekkaCore import mekkaObject, centerOfRect

rotateAnchorName = "rotate"


class Rotator(mekkaObject):
	"""GUI for rotating selected glyphs."""
	prefDict = {
		"rotate_degrees": 0,
		"stepAndRepeat_times": 0,
		"anchor_x": 0,
		"anchor_y": 0,
	}

	def __init__(self):
		self.w = vanilla.FloatingWindow((320, 95), "Rotate around anchor")

		# Window 'self.w':
		windowWidth = 320
		windowHeight = 100
		windowWidthResize = 0  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		linePos, inset, lineHeight = 10, 12, 22

		self.w.anchor_text = vanilla.TextBox((inset, linePos + 3, 120, 15), "Set 'rotate' anchor:", sizeStyle='small')
		self.w.anchor_x = vanilla.EditText((inset + 110, linePos, 40, 19), "0", sizeStyle='small', callback=self.SavePreferences)
		self.w.anchor_y = vanilla.EditText((inset + 110 + 45, linePos, 40, 19), "0", sizeStyle='small', callback=self.SavePreferences)
		self.w.updateButton = vanilla.SquareButton((inset + 110 + 90, linePos, 20, 19), u"↺", sizeStyle='small', callback=self.updateRotateAnchor)
		self.w.anchor_button = vanilla.Button((inset + 110 + 120, linePos + 1, -inset, 19), "Insert", sizeStyle='small', callback=self.insertRotateAnchor)
		linePos += lineHeight

		self.w.rotate_text1 = vanilla.TextBox((inset, linePos + 3, 55, 19), "Rotate by", sizeStyle='small')
		self.w.rotate_degrees = vanilla.EditText((inset + 60, linePos, 35, 19), "10", sizeStyle='small', callback=self.SavePreferences)
		self.w.rotate_text2 = vanilla.TextBox((inset + 60 + 40, linePos + 3, 50, 19), "degrees:", sizeStyle='small')
		self.w.rotate_ccw = vanilla.Button((-150, linePos + 1, -70 - inset, 19), u"↺ ccw", sizeStyle='small', callback=self.rotate)
		self.w.rotate_cw = vanilla.Button((-80, linePos + 1, -inset, 19), u"↻ cw", sizeStyle='small', callback=self.rotate)
		linePos += lineHeight

		self.w.stepAndRepeat_text1 = vanilla.TextBox((inset, linePos + 3, 55, 19), "Repeat", sizeStyle='small')
		self.w.stepAndRepeat_times = vanilla.EditText((inset + 60, linePos, 35, 19), "5", sizeStyle='small', callback=self.SavePreferences)
		self.w.stepAndRepeat_text2 = vanilla.TextBox((inset + 60 + 40, linePos + 3, 50, 19), "times:", sizeStyle='small')
		self.w.stepAndRepeat_ccw = vanilla.Button((-150, linePos + 1, -70 - inset, 19), u"↺+ ccw", sizeStyle='small', callback=self.rotate)
		self.w.stepAndRepeat_cw = vanilla.Button((-80, linePos + 1, -inset, 19), u"↻+ cw", sizeStyle='small', callback=self.rotate)

		self.LoadPreferences()

		self.updateRotateAnchor()
		self.w.open()
		self.w.makeKey()

	def insertRotateAnchor(self, sender=None):
		try:
			selectedLayers = Glyphs.currentDocument.selectedLayers()
			myRotationCenter = NSPoint()
			myRotationCenter.x = int(Glyphs.defaults["com.mekkablue.rotateAroundAnchor.anchor_x"])
			myRotationCenter.y = int(Glyphs.defaults["com.mekkablue.rotateAroundAnchor.anchor_y"])
			myRotationAnchor = GSAnchor("#%s" % rotateAnchorName, myRotationCenter)
			for thisLayer in selectedLayers:
				# adds '#rotate' if it doesn't exist, resets it if it exists:
				thisLayer.addAnchor_(myRotationAnchor)
		except Exception as e:  # noqa: F841
			import traceback
			print(traceback.format_exc())

	def updateRotateAnchor(self, sender=None):
		try:
			# (#)rotate anchor present, including those shining through from components:
			selectedLayer = Glyphs.currentDocument.selectedLayers()[0]
			for anchorName in ("#%s" % rotateAnchorName, rotateAnchorName):
				for thisAnchor in selectedLayer.anchorsTraversingComponents():
					if thisAnchor.name == anchorName:
						self.w.anchor_x.set(int(thisAnchor.x))
						self.w.anchor_y.set(int(thisAnchor.y))
						return

			# no anchor present:
			selectionRect = selectedLayer.boundsOfSelection()
			if selectionRect:
				# take center of selection:
				selectionCenter = centerOfRect(selectionRect)
				self.w.anchor_x.set(int(selectionCenter.x))
				self.w.anchor_y.set(int(selectionCenter.y))
				self.insertRotateAnchor()
			else:
				# no selection either: take origin
				self.w.anchor_x.set(0)
				self.w.anchor_y.set(0)
				self.insertRotateAnchor()
		except Exception as e:  # noqa: F841
			import traceback
			print(traceback.format_exc())

	def rotationTransform(self, rotationCenter, rotationDegrees, rotationDirection):
		try:
			rotationX = rotationCenter.x
			rotationY = rotationCenter.y
			rotation = rotationDegrees * rotationDirection
			RotationTransform = NSAffineTransform.transform()
			RotationTransform.translateXBy_yBy_(rotationX, rotationY)
			RotationTransform.rotateByDegrees_(rotation)
			RotationTransform.translateXBy_yBy_(-rotationX, -rotationY)
			return RotationTransform
		except Exception as e:  # noqa: F841
			import traceback
			print(traceback.format_exc())

	def rotate(self, sender):
		# update settings to the latest user input:
		self.SavePreferences()

		selectedLayers = Glyphs.currentDocument.selectedLayers()
		originatingButton = sender.getTitle()

		if "ccw" in originatingButton:
			rotationDirection = 1
		else:
			rotationDirection = -1

		if "+" in originatingButton:
			repeatCount = int(Glyphs.defaults["com.mekkablue.rotateAroundAnchor.stepAndRepeat_times"])
		else:
			repeatCount = 0

		rotationDegrees = float(Glyphs.defaults["com.mekkablue.rotateAroundAnchor.rotate_degrees"])
		rotationCenter = NSPoint(
			int(Glyphs.defaults["com.mekkablue.rotateAroundAnchor.anchor_x"]),
			int(Glyphs.defaults["com.mekkablue.rotateAroundAnchor.anchor_y"]),
		)

		if len(selectedLayers) == 1:
			selectionCounts = True
		else:
			selectionCounts = False

		for thisLayer in selectedLayers:
			# rotate individually selected nodes and components
			try:
				thisGlyph = thisLayer.parent
				selectionCounts = selectionCounts and bool(thisLayer.selection)  # True only if both are True
				RotationTransform = self.rotationTransform(rotationCenter, rotationDegrees, rotationDirection)
				print("rotationCenter, rotationDegrees, rotationDirection:", rotationCenter, rotationDegrees, rotationDirection)
				RotationTransformMatrix = RotationTransform.transformStruct()

				# thisGlyph.beginUndo()  # undo grouping causes crashes

				if repeatCount == 0:  # simple rotation
					for thisThing in selection:
						thisLayer.transform_checkForSelection_doComponents_(RotationTransform, selectionCounts, True)
				else:  # step and repeat paths and components
					newPaths, newComps = [], []
					for i in range(repeatCount):
						for thisPath in thisLayer.paths:
							if thisPath.selected or not selectionCounts:
								rotatedPath = thisPath.copy()
								for j in range(i + 1):
									rotatedPath.applyTransform(RotationTransformMatrix)
								newPaths.append(rotatedPath)
						for thisComp in thisLayer.components:
							if thisComp.selected or not selectionCounts:
								rotatedComp = thisComp.copy()
								for j in range(i + 1):
									rotatedComp.applyTransform(RotationTransformMatrix)
								newComps.append(rotatedComp)
					for newPath in newPaths:
						thisLayer.paths.append(newPath)
					for newComp in newComps:
						thisLayer.components.append(newComp)

				# thisGlyph.endUndo()  # undo grouping causes crashes
			except Exception as e:
				print(e)
				import traceback
				print(traceback.format_exc())


Rotator()
