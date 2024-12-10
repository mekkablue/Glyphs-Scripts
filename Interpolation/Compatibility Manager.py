#MenuTitle: Compatibility Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
A better way to reset startpoints and reorder paths.
"""

from vanilla import FloatingWindow, TextBox, Button, PopUpButton
from GlyphsApp import Glyphs, GSPath, GSComponent, OFFCURVE, distance
import math
from copy import copy
from AppKit import NSAffineTransform, NSNotFound, NSPoint


def slant(thisPoint, italicAngle=0.0, pivotalY=0.0):
	if italicAngle == 0.0:
		return thisPoint
	x = thisPoint.x
	yOffset = thisPoint.y - pivotalY  # calculate vertical offset
	italicAngle = math.radians(italicAngle)  # convert to radians
	tangens = math.tan(italicAngle)  # math.tan needs radians
	horizontalDeviance = tangens * yOffset  # vertical distance from pivotal point
	x += horizontalDeviance  # x of point that is yOffset from pivotal point
	return NSPoint(x, thisPoint.y)


def normalizedPosition_inRect_(absolutePos, refRect):
	x = (absolutePos.x - refRect.origin.x) / refRect.size.width
	y = (absolutePos.y - refRect.origin.y) / refRect.size.height
	return NSPoint(x, y)


def boundsForPath_atItalicAngle_(path, italicAngle=0.0):
	if italicAngle == 0.0:
		return path.bounds
	italicPath = GSPath()
	for node in path.nodes:
		italicNode = copy(node)
		italicPath.nodes.append(italicNode)
		italicNode.position = slant(italicNode.position, -italicAngle)
	return italicPath.bounds


def normalizedPositionsForPath_(path, italicAngle=0.0):
	# todo: implement italic angle
	positions = []
	refRect = boundsForPath_atItalicAngle_(path, italicAngle)
	for node in path.nodes:
		normalizedPosition = normalizedPosition_inRect_(slant(node.position, -italicAngle), refRect)
		positions.append(normalizedPosition)
	return positions


def distancesOfPositions_(positions1, positions2):
	if len(positions1) != len(positions2):
		return NSNotFound

	totalDistance = 0.0
	for i in range(len(positions1)):
		p1 = positions1[i]
		p2 = positions2[i]
		totalDistance += distance(p1, p2)

	return totalDistance


def setBestStartPointForShape_withCompatibleShape_atItalicAngle_compatibleShapeItalicAngle_(path, referencePath, italicAngle=0.0, refItalicAngle=0.0):
	if len(path.nodes) != len(referencePath.nodes):
		raise Exception("Shapes are incompatible. Cannot find start point.")
	# todo: find more incompatibilities (comparestring?)

	positions = normalizedPositionsForPath_(path, italicAngle)
	refPositions = normalizedPositionsForPath_(referencePath, refItalicAngle)

	distances = []
	for offset in range(len(positions)):
		offsetPositions = positions[offset:] + positions[:offset]
		offsetDistance = distancesOfPositions_(offsetPositions, refPositions)
		distances.append((offsetDistance, offset))

	distances = sorted(distances, key=lambda data: data[0])
	nodeStructure = list((n.type for n in path.nodes))
	refNodeStructure = list((n.type for n in referencePath.nodes))
	for distanceData in distances:
		offset = distanceData[1]
		offsetStructure = nodeStructure[offset:] + nodeStructure[:offset]
		reorderedPathIsCompatible = offsetStructure == refNodeStructure
		if reorderedPathIsCompatible:
			path.makeNodeFirst_(path.nodes[offset - 1])
			break


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
			"Right, then bottom",
			"Shortest travel",
		])

		self.w.shapeOrderTitle = TextBox((210, 10, 180, 20), "Shape Order", sizeStyle="small")
		self.w.shapeOrderOptions = PopUpButton((210, 30, 180, 20), [
			"By relative center",
			"By size",
			"By shortest travel",
		])

		self.w.resetStartPoints = Button((10, -30, 190, 20), "Reset Start Points", callback=self.resetStartPoints)
		self.w.reorderShapes = Button((210, -30, 180, 20), "Reorder Shapes", callback=self.reorderShapes)
		self.w.open()

	def resetStartPoints(self, sender):
		font = Glyphs.font
		glyph = font.selectedLayers[0].parent
		layers = [layer for layer in glyph.layers if layer.isMasterLayer or layer.isSpecialLayer]

		startPointOption = self.w.startPointOptions.get()

		if startPointOption == 9:
			# shortest node travel in interpolation
			for layer in layers[1:]:
				firstLayer = layers[0]
				if len(layer.paths) != len(firstLayer.paths):
					print(f"❌ {glyph.name}: different number of paths in layer ‘{layer.name}’")
					return

				for i in range(len(layer.paths)):
					try:
						setBestStartPointForShape_withCompatibleShape_atItalicAngle_compatibleShapeItalicAngle_(
							layer.paths[i], firstLayer.paths[i],
							layer.italicAngle, firstLayer.italicAngle,
						)
					except Exception as e:
						print(f"⚠️ {glyph.name}: {e}")
						continue

		else:
			print("Other options")
			# all other geographic options
			for layer in layers:
				for path in layer.paths:
					self.findOptimalStartPoint(path, startPointOption)

			self.updateCompatibility(glyph)

	def findOptimalStartPoint(self, path, startPointOption):
		originalStart = path.nodes[0]
		bestStart = originalStart
		minValue = float('inf')
		compatibleStarts = []

		for node in path.nodes:
			if node.type != OFFCURVE:
				path.makeNodeFirst_(node)
				if self.checkLayerCompatibility(path.parent):
					compatibleStarts.append(node)

		if compatibleStarts:
			for start in compatibleStarts:
				path.makeNodeFirst_(start)
				value = self.calculateStartPointValue(start, startPointOption)

				if value is None:
					continue

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
		elif option in [5, 6, 7]:
			primary = node.x if option in [5, 6] else -node.x
			secondary = -node.y if option in [5, 7] else node.y
			return primary * 1000000 + secondary

	def reorderShapes(self, sender):
		font = Glyphs.font
		glyph = font.selectedLayers[0].parent
		option = self.w.shapeOrderOptions.get()

		if option == 1:
			self.reorderShapesBySize(glyph)
		elif option == 0:
			self.reorderShapesByRelativeCenter(glyph)
		elif option == 2:
			self.reorderShapesByShortestTravel(glyph)

		self.updateCompatibility(glyph)

	def reorderShapesBySize(self, glyph):
		layers = [layer for layer in glyph.layers if layer.isMasterLayer or layer.isSpecialLayer]
		for layer in layers:
			shapes = list(layer.shapes)
			shapes.sort(key=lambda s: s.bounds.size.width * s.bounds.size.height)
			layer.shapes = shapes

	def italicBoundsOfLayer(self, layer):
		italicAngle = layer.italicAngle
		if italicAngle == 0.0:
			return layer.bounds

		italicLayer = layer.copyDecomposedLayer()
		myTransform = NSAffineTransform.transform()
		myTransform.shearXBy_(math.tan(math.radians(-italicAngle)))
		italicLayer.applyTransform(myTransform.transformStruct())
		return italicLayer.bounds

	def relativeNodePositions(self, path, rect, italicAngle=0.0):
		layer = path.parent
		# TODO
		return ()

	def reorderShapesByShortestTravel(self, glyph):
		layers = [layer for layer in glyph.layers if layer.isMasterLayer or layer.isSpecialLayer]
		firstLayer = layers[0]
		firstLayerBounds = self.italicBoundsOfLayer(firstLayer)

		for i, firstShape in enumerate(firstLayer.shapes):
			firstCenter = self.bboxCenter(firstShape)
			# firstNodes = self.relativeNodePositions(firstShape, firstLayerBounds, italicAngle=firstLayer.italicAngle)
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
					otherLayer.shapes.insert(i, otherLayer.shapes.pop(i + j))

	def reorderShapesByRelativeCenter(self, glyph):
		layers = [layer for layer in glyph.layers if layer.isMasterLayer or layer.isSpecialLayer]
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
					otherLayer.shapes.insert(i, otherLayer.shapes.pop(i + j))

	def bboxCenter(self, shape):
		bounds = shape.bounds
		layer = shape.parent
		glyph = layer.parent
		italicAngle = layer.italicAngle

		# Calculate the italic offset at the vertical center of the shape
		italicOffset = math.tan(math.radians(italicAngle)) * (bounds.origin.y + bounds.size.height / 2 - layer.bounds.origin.y)

		# Compensate x for the italic angle
		xCenter = ((bounds.origin.x + bounds.size.width / 2 - italicOffset) - layer.bounds.origin.x) / layer.bounds.size.width
		yCenter = (bounds.origin.y + bounds.size.height / 2 - layer.bounds.origin.y) / layer.bounds.size.height

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
		layers = [layer for layer in glyph.layers if layer.isMasterLayer or layer.isSpecialLayer]
		baseLayer = layers[0]
		baseString = baseLayer.compareString()

		for layer in layers[1:]:
			if layer.compareString() != baseString:
				print(f"Note: Layer {layer.name} could not be made compatible with the base layer.")

		glyph.updateGlyphInfo()


CompatibilityManager()
