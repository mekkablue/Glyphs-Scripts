#MenuTitle: Fix Punctuation Dots and Heights
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Syncs punctuation dots between ¡!¿? (and their SC+CASE variants). Will use dot from exclam in all other glyphs, and shift ¡¿ in SC and CASE variants. Assumes that ¡¿ are components in !?. Detailed report in Macro Window.
"""

import math
from Foundation import NSPoint, NSAffineTransform, NSAffineTransformStruct
Glyphs.clearLog() # clears log in Macro window

def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
	"""
	Returns an NSAffineTransform object for transforming layers.
	Apply an NSAffineTransform t object like this:
		Layer.transform_checkForSelection_doComponents_(t,False,True)
	Access its transformation matrix like this:
		tMatrix = t.transformStruct() # returns the 6-float tuple
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

def centerOfRect(rect):
	"""
	Returns the center of NSRect rect as an NSPoint.
	"""
	center = NSPoint(rect.origin.x + rect.size.width / 2, rect.origin.y + rect.size.height / 2)
	return center

thisFont = Glyphs.font
for suffix in ("", ".sc"):
	exclamname = "exclam" + suffix
	questionname = "question" + suffix
	exclamdownname = "exclamdown" + suffix
	questiondownname = "questiondown" + suffix
	exclam = thisFont.glyphs[exclamname]
	question = thisFont.glyphs[questionname]
	exclamdown = thisFont.glyphs[exclamdownname]
	questiondown = thisFont.glyphs[questiondownname]

	if exclam and question:
		for thisMaster in thisFont.masters:
			print("\n%s:" % thisMaster.name)
			exclamLayer = exclam.layers[thisMaster.id]
			questionLayer = question.layers[thisMaster.id]
			exclamDot = sorted(exclamLayer.paths, key=lambda thisPath: thisPath.bounds.origin.y)[0]
			questionDot = sorted(questionLayer.paths, key=lambda thisPath: thisPath.bounds.origin.y)[0]
			exclamX = centerOfRect(exclamDot.bounds).x
			questionX = centerOfRect(questionDot.bounds).x
			shift = transform(shiftX=questionX - exclamX).transformStruct()
			newQuestionDot = exclamDot.copy()
			try:
				# GLYPHS 3:
				for i in range(len(questionLayer.shapes))[::-1]:
					if questionLayer.shapes[i] == questionDot:
						del questionLayer.shapes[i]
			except:
				# GLYPHS 2:
				for i in range(len(questionLayer.paths))[::-1]:
					if questionLayer.paths[i] == questionDot:
						del questionLayer.paths[i]
			if len(questionLayer.paths) == 1:
				try:
					questionLayer.shapes.append(newQuestionDot)
				except:
					questionLayer.paths.append(newQuestionDot)
				newQuestionDot.applyTransform(shift)
				print(u"  ✅ OK: dot transplanted in %s, layer %s" % (questionname, questionLayer.name))
			else:
				print(u"  ⛔️ ERROR: dot not deleted in %s, layer %s?" % (questionname, questionLayer.name))

			if not exclamdown:
				print(u"  ⛔️ ERROR: %s not found" % exclamdownname)
			else:
				for glyph in (exclamdown, questiondown):
					glyphLayer = glyph.layers[thisMaster.id]

					# fallback height:
					overshoot = -exclamLayer.bounds.origin.y
					height = thisMaster.xHeight + overshoot

					# calculate height:
					if ".sc" in glyph.name or ".case" in glyph.name:
						refGlyph = thisFont.glyphs[glyph.name.replace("down", "")]
						if refGlyph:
							refLayer = refGlyph.layers[thisMaster.id]
							height = refLayer.bounds.origin.y + refLayer.bounds.size.height

					currentHeight = glyphLayer.bounds.origin.y + glyphLayer.bounds.size.height
					shift = transform(shiftY=height - currentHeight).transformStruct()
					glyphLayer.applyTransform(shift)
					glyphLayer.updateMetrics()
					glyphLayer.syncMetrics()
					print(u"  ✅ synced %s" % glyph.name)
