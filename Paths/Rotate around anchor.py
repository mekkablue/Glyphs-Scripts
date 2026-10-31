# MenuTitle: Rotate Around Anchor
__doc__ = """
Rotate selected glyphs (or selected paths and components) around a 'rotate' anchor.
"""

from math import isfinite

import vanilla
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
)
from Foundation import NSPoint, NSAffineTransform
from GlyphsApp import Glyphs
from mekkablue import mekkaObject, newAnchorWithName, UpdateButton
from mekkablue.geometry import centerOfRect

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
		windowWidth = 380
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Rotate Around Anchor",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		self.w.anchor_text = vanilla.TextBox("auto", "Set 'rotate' anchor", sizeStyle='small')
		self.w.anchor_x = vanilla.EditText("auto", "0", sizeStyle='small', callback=self.SavePreferences)
		self.w.anchor_y = vanilla.EditText("auto", "0", sizeStyle='small', callback=self.SavePreferences)
		self.w.updateButton = UpdateButton("auto", callback=self.updateRotateAnchor)
		self.w.anchor_button = vanilla.Button("auto", "Insert", sizeStyle='small', callback=self.insertRotateAnchor)

		self.w.rotate_text1 = vanilla.TextBox("auto", "Rotate by", sizeStyle='small')
		self.w.rotate_degrees = vanilla.EditText("auto", "10", sizeStyle='small', callback=self.SavePreferences)
		self.w.rotate_text2 = vanilla.TextBox("auto", "degrees", sizeStyle='small')
		self.w.rotate_ccw = vanilla.Button("auto", u"↺ ccw", sizeStyle='small', callback=self.rotate)
		self.w.rotate_cw = vanilla.Button("auto", u"↻ cw", sizeStyle='small', callback=self.rotate)

		self.w.stepAndRepeat_text1 = vanilla.TextBox("auto", "Repeat", sizeStyle='small')
		self.w.stepAndRepeat_times = vanilla.EditText("auto", "5", sizeStyle='small', callback=self.SavePreferences)
		self.w.stepAndRepeat_text2 = vanilla.TextBox("auto", "times", sizeStyle='small')
		self.w.stepAndRepeat_ccw = vanilla.Button("auto", u"↺+ ccw", sizeStyle='small', callback=self.rotate)
		self.w.stepAndRepeat_cw = vanilla.Button("auto", u"↻+ cw", sizeStyle='small', callback=self.rotate)

		# the labels of the three rows share one width and resist compression:
		for label in (self.w.anchor_text, self.w.rotate_text1, self.w.stepAndRepeat_text1):
			nsLabel = label.getNSTextField()
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes and buttons stretch vertically by default; hugging makes the window as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		rules = [
			"H:|-inset-[anchor_text]-gap-[anchor_x(41)]-gap-[anchor_y]-gap-[updateButton]-(>=gap)-[anchor_button(>=70)]-inset-|",
			"H:|-inset-[rotate_text1]-gap-[rotate_degrees]-gap-[rotate_text2]-(>=gap)-[rotate_ccw(>=70)]-gap-[rotate_cw]-inset-|",
			"H:|-inset-[stepAndRepeat_text1]-gap-[stepAndRepeat_times]-gap-[stepAndRepeat_text2]-(>=gap)-[stepAndRepeat_ccw(>=70)]-gap-[stepAndRepeat_cw]-inset-|",
			"V:|-inset-[anchor_x]-row-[rotate_degrees]-row-[stepAndRepeat_times]-inset-|",
		]
		equalWidths = (
			(self.w.rotate_text1, self.w.anchor_text),
			(self.w.stepAndRepeat_text1, self.w.anchor_text),
			(self.w.anchor_y, self.w.anchor_x),
			(self.w.rotate_degrees, self.w.anchor_x),
			(self.w.stepAndRepeat_times, self.w.anchor_x),
			(self.w.rotate_cw, self.w.rotate_ccw),
			(self.w.stepAndRepeat_ccw, self.w.rotate_ccw),
			(self.w.stepAndRepeat_cw, self.w.rotate_ccw),
		)
		for view1, view2 in equalWidths:
			rules.append({"view1": view1, "attribute1": "width", "view2": view2, "attribute2": "width"})
		# everything in a row sits on the vertical center of its field:
		rowFields = {
			self.w.anchor_x: (self.w.anchor_text, self.w.anchor_y, self.w.updateButton, self.w.anchor_button),
			self.w.rotate_degrees: (self.w.rotate_text1, self.w.rotate_text2, self.w.rotate_ccw, self.w.rotate_cw),
			self.w.stepAndRepeat_times: (self.w.stepAndRepeat_text1, self.w.stepAndRepeat_text2, self.w.stepAndRepeat_ccw, self.w.stepAndRepeat_cw),
		}
		for field, others in rowFields.items():
			for other in others:
				rules.append({"view1": other, "attribute1": "centerY", "view2": field, "attribute2": "centerY"})
		self.w.addAutoPosSizeRules(rules, metrics={"inset": 12, "gap": 8, "row": 8})

		self.LoadPreferences()

		self.updateRotateAnchor()
		self.w.open()
		self.w.makeKey()

	def insertRotateAnchor(self, sender=None):
		try:
			selectedLayers = Glyphs.currentDocument.selectedLayers()
			myRotationCenter = NSPoint()
			myRotationCenter.x = int(self.pref("anchor_x"))
			myRotationCenter.y = int(self.pref("anchor_y"))
			myRotationAnchor = newAnchorWithName("#%s" % rotateAnchorName, myRotationCenter)
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
			selectionCenter = centerOfRect(selectionRect) if selectionRect else None
			# an empty selection can yield infinite bounds, so check for finite values:
			if selectionCenter and isfinite(selectionCenter.x) and isfinite(selectionCenter.y):
				# take center of selection:
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
			repeatCount = int(self.pref("stepAndRepeat_times"))
		else:
			repeatCount = 0

		rotationDegrees = float(self.pref("rotate_degrees"))
		rotationCenter = NSPoint(
			int(self.pref("anchor_x")),
			int(self.pref("anchor_y")),
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
				# print("rotationCenter, rotationDegrees, rotationDirection:", rotationCenter, rotationDegrees, rotationDirection) # DEBUG
				RotationTransformMatrix = RotationTransform.transformStruct()

				# thisGlyph.beginUndo()  # undo grouping causes crashes

				if repeatCount == 0:  # simple rotation
					for thisShape in thisLayer.shapes:
						if thisShape.selected:
							if hasattr(thisShape, "automaticAlignment"):
								thisShape.automaticAlignment = 0
							thisShape.applyTransform(RotationTransformMatrix)
						# thisLayer.transform_checkForSelection_doComponents_(RotationTransform, selectionCounts, True)
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
								thisComp.automaticAlignment = 0
								rotatedComp = thisComp.copy()
								for j in range(i + 1):
									rotatedComp.applyTransform(RotationTransformMatrix)
								newComps.append(rotatedComp)
					for newPath in newPaths:
						thisLayer.shapes.append(newPath)
					for newComp in newComps:
						thisLayer.shapes.append(newComp)

				# thisGlyph.endUndo()  # undo grouping causes crashes
			except Exception as e:
				print(e)
				import traceback
				print(traceback.format_exc())


Rotator()
