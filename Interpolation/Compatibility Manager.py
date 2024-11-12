#MenuTitle: Compatibility Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
A better way to reset startpoints and reorder paths.
"""

from vanilla import *
from GlyphsApp import *
import math

class CompatibilityManager:
	def __init__(self):
		self.w = FloatingWindow((400, 90), "Compatibility Manager")
		
		self.w.startPointTitle = TextBox((10, 10, 190, 20), "Start Point Selection", sizeStyle="small")
		self.w.startPointOptions = PopUpButton((10, 30, 190, 20), [
			"Closest to origin",
			"Top, then left",
			"Top, then right",
			"Bottom, then left",
			"Bottom, then right",
			"Left, then top",
			"Left, then bottom",
			"Right, then top",
			"Right, then bottom"
		])
		
		self.w.shapeOrderTitle = TextBox((210, 10, 180, 20), "Shape Order", sizeStyle="small")
		self.w.shapeOrderOptions = PopUpButton((210, 30, 180, 20), [
			"By Size",
			"By Relative Center"
		])
		
		self.w.resetStartPoints = Button((10, -30, 190, 20), "Reset Start Points", callback=self.resetStartPoints)
		self.w.reorderShapes = Button((210, -30, 180, 20), "Reorder Shapes", callback=self.reorderShapes)
		
		self.w.open()

	def resetStartPoints(self, sender):
		font = Glyphs.font
		glyph = font.selectedLayers[0].parent
		layers = [l for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer]

		for layer in layers:
			for path in layer.paths:
				self.findOptimalStartPoint(path)

		self.updateCompatibility(glyph)

	def findOptimalStartPoint(self, path):
		originalStart = path.nodes[0]
		bestStart = originalStart
		minValue = float('inf')
		compatibleStarts = []

		startPointOption = self.w.startPointOptions.get()

		for node in path.nodes:
			if node.type != OFFCURVE:
				path.makeNodeFirst_(node)
				if self.checkLayerCompatibility(path.parent):
					compatibleStarts.append(node)

		if compatibleStarts:
			for start in compatibleStarts:
				path.makeNodeFirst_(start)
				value = self.calculateStartPointValue(start, startPointOption)
				
				if value < minValue:
					minValue = value
					bestStart = start

			path.makeNodeFirst_(bestStart)
		else:
			path.makeNodeFirst_(originalStart)

	def calculateStartPointValue(self, node, option):
		if option == 0:
			return math.hypot(node.x, node.y)
		elif option in [1, 2, 3, 4]:
			primary = -node.y if option in [1, 2] else node.y
			secondary = node.x if option in [1, 3] else -node.x
			return primary * 1000000 + secondary
		else:
			primary = node.x if option in [5, 6] else -node.x
			secondary = -node.y if option in [5, 7] else node.y
			return primary * 1000000 + secondary

	def reorderShapes(self, sender):
		font = Glyphs.font
		glyph = font.selectedLayers[0].parent
		option = self.w.shapeOrderOptions.get()

		if option == 0:
			self.reorderShapesBySize(glyph)
		elif option == 1:
			self.reorderShapesByRelativeCenter(glyph)

		self.updateCompatibility(glyph)

	def reorderShapesBySize(self, glyph):
		layers = [l for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer]
		for layer in layers:
			shapes = list(layer.shapes)
			shapes.sort(key=lambda s: s.bounds.size.width * s.bounds.size.height)
			layer.shapes = shapes

	def reorderShapesByRelativeCenter(self, glyph):
		layers = [l for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer]
		firstLayer = layers[0]
		for i, firstShape in enumerate(firstLayer.shapes):
			firstCenter = self.bboxCenter(firstShape)
			for otherLayer in layers[1:]:
				smallestDistance = float("inf")
				matchedIndex = None
				for j, otherShape in enumerate(otherLayer.shapes[i:]):
					if self.compatible(firstShape, otherShape):
						otherCenter = self.bboxCenter(otherShape)
						currentDistance = self.dist(firstCenter, otherCenter)
						if currentDistance < smallestDistance:
							smallestDistance = currentDistance
							matchedIndex = j
				if matchedIndex is not None and matchedIndex > 0:
					otherLayer.shapes.insert(i, otherLayer.shapes.pop(i+j))

	def bboxCenter(self, shape):
		bounds = shape.bounds
		layer = shape.parent
		glyph = layer.parent
		italicAngle = layer.italicAngle

		# Calculate the italic offset at the vertical center of the shape
		italicOffset = math.tan(math.radians(italicAngle)) * (bounds.origin.y + bounds.size.height/2 - layer.bounds.origin.y)

		# Compensate x for the italic angle
		xCenter = ((bounds.origin.x + bounds.size.width/2 - italicOffset) - layer.bounds.origin.x) / layer.bounds.size.width
		yCenter = (bounds.origin.y + bounds.size.height/2 - layer.bounds.origin.y) / layer.bounds.size.height

		return (xCenter, yCenter)

	def compatible(self, shape1, shape2):
		if shape1.__class__ != shape2.__class__:
			return False
		
		if isinstance(shape1, GSPath):
			if shape1.direction != shape2.direction:
				return False
			if len(shape1.nodes) != len(shape2.nodes):
				return False
		elif isinstance(shape1, GSComponent):
			if shape1.componentName != shape2.componentName:
				return False
		
		return True

	def dist(self, center1, center2):
		x1, y1 = center1
		x2, y2 = center2
		return math.hypot(x1 - x2, y1 - y2)

	def checkLayerCompatibility(self, layer):
		glyph = layer.parent
		baseLayer = glyph.layers[0]
		return layer.compareString() == baseLayer.compareString()

	def updateCompatibility(self, glyph):
		layers = [l for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer]
		baseLayer = layers[0]
		baseString = baseLayer.compareString()

		for layer in layers[1:]:
			if layer.compareString() != baseString:
				print(f"Note: Layer {layer.name} could not be made compatible with the base layer.")

		glyph.updateGlyphInfo()

CompatibilityManager()
