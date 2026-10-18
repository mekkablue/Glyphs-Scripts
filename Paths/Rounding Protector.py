# MenuTitle: Rounding Protector
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Marks nodes so the Round Corners filter leaves them alone (node.name = "c"), and copies the marks of one master to all compatible layers (other masters, brace and bracket layers).
"""

from math import hypot

import vanilla
from mekkablue import mekkaObject, layerGroupsOf
from GlyphsApp import Glyphs, GSNode, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
)

PROTECT_VALUE = "c"
PROBE_DISTANCE = 0.5  # in units, at 1000 upm; probe points are placed this far from the node, on both sides
OFFCURVE = "offcurve"
QCURVE = "qcurve"


# ---- node status ----


def usesUserDataName():
	"""Glyphs 4.0 and 4.1 do not display node.name properly, but node.userData["name"] works."""
	return 4.0 <= Glyphs.versionNumber < 4.2


def nodeMark(node):
	"""The current mark of the node: its name, or None."""
	if usesUserDataName():
		return node.userData["name"]
	return node.name


def switchNode(node, on=True):
	"""Sets (on=True) or removes (on=False) the mark that keeps the Round Corners filter from rounding the node."""
	if usesUserDataName():
		if on:
			node.userData["name"] = PROTECT_VALUE
		elif node.userData["name"] is not None:
			del node.userData["name"]
	else:
		node.setName_(PROTECT_VALUE if on else None)


def isProtected(node):
	return nodeMark(node) == PROTECT_VALUE


def setProtection(node, protect, overwrite):
	"""
	Protects or unprotects an on-curve node.
	Returns False if the node was left alone because it carries a different
	name and overwriting is switched off, True otherwise.
	"""
	currentValue = nodeMark(node)
	hasOtherValue = bool(currentValue) and currentValue != PROTECT_VALUE
	if hasOtherValue and not overwrite:
		return False
	if protect and currentValue != PROTECT_VALUE:
		switchNode(node, True)
	elif not protect and currentValue:
		switchNode(node, False)
	return True


# ---- overlap detection: flatten, then compare the winding number on both sides of a node ----


def pointOf(position):
	return (position.x, position.y)


def midpoint(pointA, pointB):
	return ((pointA[0] + pointB[0]) / 2.0, (pointA[1] + pointB[1]) / 2.0)


def stepsFor(*points):
	length = sum(hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))
	return min(60, max(4, int(length / 10)))


def cubicPoints(p0, p1, p2, p3):
	steps = stepsFor(p0, p1, p2, p3)
	for step in range(1, steps + 1):
		t = step / steps
		s = 1.0 - t
		yield (
			s**3 * p0[0] + 3 * s * s * t * p1[0] + 3 * s * t * t * p2[0] + t**3 * p3[0],
			s**3 * p0[1] + 3 * s * s * t * p1[1] + 3 * s * t * t * p2[1] + t**3 * p3[1],
		)


def quadraticPoints(p0, p1, p2):
	steps = stepsFor(p0, p1, p2)
	for step in range(1, steps + 1):
		t = step / steps
		s = 1.0 - t
		yield (
			s * s * p0[0] + 2 * s * t * p1[0] + t * t * p2[0],
			s * s * p0[1] + 2 * s * t * p1[1] + t * t * p2[1],
		)


def segmentPoints(start, controls, end, isQuadratic):
	"""Polyline for one segment, without its start point, including its end point."""
	if not controls:
		return [end]
	if isQuadratic:
		points = []
		for index, control in enumerate(controls):
			quadStart = start if index == 0 else midpoint(controls[index - 1], control)
			quadEnd = end if index == len(controls) - 1 else midpoint(control, controls[index + 1])
			points.extend(quadraticPoints(quadStart, control, quadEnd))
		return points
	if len(controls) == 2:
		return list(cubicPoints(start, controls[0], controls[1], end))
	return [end]


def pathPolygon(path):
	nodes = path.nodes
	count = len(nodes)
	polygon = []
	for index in range(count):
		node = nodes[index]
		if node.type == OFFCURVE:
			continue
		controls = []
		backIndex = (index - 1) % count
		while nodes[backIndex].type == OFFCURVE and len(controls) < count:
			controls.insert(0, pointOf(nodes[backIndex].position))
			backIndex = (backIndex - 1) % count
		polygon.extend(segmentPoints(pointOf(nodes[backIndex].position), controls, pointOf(node.position), node.type == QCURVE))
	return polygon


def windingNumber(polygons, x, y):
	"""Nonzero-rule winding number at (x, y), ray towards +x. polygons: list of (minX, maxX, minY, maxY, points)."""
	winding = 0
	for minX, maxX, minY, maxY, points in polygons:
		if y < minY or y > maxY or x > maxX:
			continue
		previous = points[-1]
		for current in points:
			if previous[1] <= y:
				if current[1] > y and (current[0] - previous[0]) * (y - previous[1]) - (x - previous[0]) * (current[1] - previous[1]) > 0:
					winding += 1
			elif current[1] <= y and (current[0] - previous[0]) * (y - previous[1]) - (x - previous[0]) * (current[1] - previous[1]) < 0:
				winding -= 1
			previous = current
	return winding


def directionToNeighbor(nodes, index, step):
	"""Unit vector from the node to the nearest distinct neighbor in the given direction (+1 or -1), or None."""
	count = len(nodes)
	origin = nodes[index].position
	for offset in range(1, count):
		other = nodes[(index + step * offset) % count].position
		deltaX, deltaY = other.x - origin.x, other.y - origin.y
		length = hypot(deltaX, deltaY)
		if length > 1e-6:
			return (deltaX / length, deltaY / length)
	return None


def probeNormal(nodes, index):
	"""Unit vector across the outline at the node: perpendicular to the direction of travel (bisector at corners)."""
	forward = directionToNeighbor(nodes, index, 1)
	backward = directionToNeighbor(nodes, index, -1)
	if forward is None or backward is None:
		return None
	travelX, travelY = forward[0] - backward[0], forward[1] - backward[1]  # incoming direction is the reverse of backward
	length = hypot(travelX, travelY)
	if length < 1e-6:  # cusp: incoming and outgoing are opposite
		travelX, travelY = forward
		length = 1.0
	return (-travelY / length, travelX / length)


def nodesInsideOverlaps(layer, distance):
	"""
	On-curve nodes that would not survive Remove Overlap: the fill (nonzero winding)
	is the same on both sides of the outline at the node, i.e. there is no edge of
	the union at the node. Considers all closed paths of the layer, including the node's own.
	"""
	closedPaths = [path for path in layer.paths if path.closed and len(path.nodes) > 2]
	polygons = []
	for path in closedPaths:
		points = pathPolygon(path)
		if len(points) < 3:
			continue
		xs = [point[0] for point in points]
		ys = [point[1] for point in points]
		polygons.append((min(xs), max(xs), min(ys), max(ys), points))
	if not polygons:
		return []

	insideNodes = []
	for path in closedPaths:
		nodes = path.nodes
		for index, node in enumerate(nodes):
			if node.type == OFFCURVE:
				continue
			normal = probeNormal(nodes, index)
			if normal is None:
				continue
			x, y = node.position.x, node.position.y
			filledOneSide = windingNumber(polygons, x + normal[0] * distance, y + normal[1] * distance) != 0
			filledOtherSide = windingNumber(polygons, x - normal[0] * distance, y - normal[1] * distance) != 0
			if filledOneSide == filledOtherSide:
				insideNodes.append(node)
	return insideNodes


# ---- syncing ----


def layerStructure(layer):
	return tuple((path.closed, tuple(node.type for node in path.nodes)) for path in layer.paths)


def syncLayer(sourceLayer, targetLayer, overwrite):
	"""
	Makes the protection of the target layer's on-curve nodes identical to the source layer's.
	Returns (changedCount, skippedCount).
	"""
	changedCount, skippedCount = 0, 0
	for sourcePath, targetPath in zip(sourceLayer.paths, targetLayer.paths):
		for sourceNode, targetNode in zip(sourcePath.nodes, targetPath.nodes):
			if sourceNode.type == OFFCURVE:
				continue
			protect = isProtected(sourceNode)
			wasProtected = isProtected(targetNode)
			if not setProtection(targetNode, protect, overwrite):
				skippedCount += 1
			elif wasProtected != protect:
				changedCount += 1
	return changedCount, skippedCount


def syncGlyph(glyph, sourceLayer, overwrite):
	"""Syncs the source layer to all other layers of the glyph it is interpolation-compatible with."""
	sourceId = sourceLayer.layerId
	sourceStructure = layerStructure(sourceLayer)
	for layerGroup in layerGroupsOf(glyph):
		if sourceId not in layerGroup:
			continue
		for layerId in layerGroup:
			if layerId == sourceId:
				continue
			targetLayer = glyph.layers[layerId]
			if layerStructure(targetLayer) != sourceStructure:
				print("\t⚠️ %s, layer ‘%s’: nodes not compatible with ‘%s’, skipped" % (glyph.name, targetLayer.name, sourceLayer.name))
				continue
			changedCount, skippedCount = syncLayer(sourceLayer, targetLayer, overwrite)
			if changedCount:
				print("\t🔠 %s, layer ‘%s’: %i node%s synced" % (glyph.name, targetLayer.name, changedCount, "" if changedCount == 1 else "s"))
			if skippedCount:
				print("\t⚠️ %s, layer ‘%s’: %i node%s with other name kept" % (glyph.name, targetLayer.name, skippedCount, "" if skippedCount == 1 else "s"))


# ---- GUI ----


class RoundingProtector(mekkaObject):
	prefDict = {
		"master": 0,
		"scope": 0,
		"overwriteNames": True,
		"syncAfter": True,
	}

	def __init__(self):
		windowWidth = 360
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Rounding Protector",
			autosaveName=self.domain("mainwindow"),
		)

		inset = 15

		self.w.descriptionText = vanilla.TextBox(
			"auto",
			"Protects nodes from the Round Corners filter (node name “%s”), and copies the protection of a master to all compatible layers." % PROTECT_VALUE,
			sizeStyle="small",
			selectable=True,
		)

		font = Glyphs.font
		masterNames = [master.name for master in font.masters] if font else ["(no font open)"]

		self.w.masterLabel = vanilla.TextBox("auto", "Source master:", sizeStyle="small", selectable=True)
		self.w.master = vanilla.PopUpButton("auto", masterNames, callback=self.SavePreferences, sizeStyle="small")
		self.w.master.setToolTip("The master that overlap detection reads from, and that ‘Sync’ copies from.")

		self.w.scopeLabel = vanilla.TextBox("auto", "Glyphs:", sizeStyle="small", selectable=True)
		self.w.scope = vanilla.PopUpButton("auto", ["All glyphs in font", "Selected glyphs"], callback=self.SavePreferences, sizeStyle="small")
		self.w.scope.setToolTip("Which glyphs ‘Protect Overlap Nodes’ and ‘Sync’ work on.")

		self.w.overwriteNames = vanilla.CheckBox("auto", "Overwrite other node names", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.overwriteNames.setToolTip(
			"On: protecting replaces any other node name, and unprotecting (also when syncing) removes it. Off: nodes carrying a different name are left alone and reported."
		)

		self.w.syncAfter = vanilla.CheckBox("auto", "Sync to compatible layers afterwards", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.syncAfter.setToolTip(
			"After protecting or unprotecting, copy the result to all compatible layers of the same glyphs, so they match exactly. Selected-node buttons sync from the edited layer, ‘Protect Overlap Nodes’ from the source master."
		)

		self.w.protectSelectedButton = vanilla.Button("auto", "Protect Selected", callback=self.protectSelected)
		self.w.protectSelectedButton.setToolTip("Protects the selected nodes in the selected layers.")
		self.w.unprotectSelectedButton = vanilla.Button("auto", "Unprotect Selected", callback=self.unprotectSelected)
		self.w.unprotectSelectedButton.setToolTip("Removes the protection from the selected nodes in the selected layers.")
		self.w.protectOverlapsButton = vanilla.Button("auto", "Protect Overlap Nodes", callback=self.protectOverlaps)
		self.w.protectOverlapsButton.setToolTip("Protects all nodes of the source master that would disappear in Remove Overlap, because they lie inside another shape.")
		self.w.syncButton = vanilla.Button("auto", "Sync Master to Others", callback=self.syncMaster)
		self.w.syncButton.setToolTip("Makes the protection in all layers compatible with the source master identical to the source master.")
		self.w.setDefaultButton(self.w.syncButton)

		# the description wraps, so it takes the width it is given
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(
			NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal
		)
		# labels hug their text and keep it on one line, popups take the rest
		for label in (self.w.masterLabel, self.w.scopeLabel):
			nsLabel = label.getNSTextField()
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[masterLabel]-gap-[master]-inset-|",
				"H:|-inset-[scopeLabel]-gap-[scope]-inset-|",
				"H:|-inset-[overwriteNames]-(>=inset)-|",
				"H:|-inset-[syncAfter]-(>=inset)-|",
				"H:|-inset-[protectSelectedButton]-gap-[unprotectSelectedButton(==protectSelectedButton)]-inset-|",
				"H:|-inset-[protectOverlapsButton]-gap-[syncButton(==protectOverlapsButton)]-inset-|",
				"V:|-gap-[descriptionText(42)]-row-[master]-row-[scope]-row-[overwriteNames]-row-[syncAfter]-inset-[protectSelectedButton]-row-[protectOverlapsButton]-inset-|",
				{"view1": self.w.masterLabel, "attribute1": "centerY", "view2": self.w.master, "attribute2": "centerY"},
				{"view1": self.w.scopeLabel, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
				{"view1": self.w.scopeLabel, "attribute1": "width", "view2": self.w.masterLabel, "attribute2": "width"},
				{"view1": self.w.unprotectSelectedButton, "attribute1": "centerY", "view2": self.w.protectSelectedButton, "attribute2": "centerY"},
				{"view1": self.w.syncButton, "attribute1": "centerY", "view2": self.w.protectOverlapsButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8},
		)

		self.LoadPreferences()
		if font and self.prefInt("master") >= len(font.masters):
			self.w.master.set(0)
			self.SavePreferences()

		self.w.open()
		self.w.makeKey()

	# ---- helpers ----

	def currentFont(self):
		font = Glyphs.font
		if font is None:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
		return font

	def sourceMaster(self, font):
		masterIndex = self.prefInt("master")
		if masterIndex >= len(font.masters):
			masterIndex = 0
		return font.masters[masterIndex]

	def glyphsInScope(self, font):
		if self.prefInt("scope") == 0:
			return list(font.glyphs)
		glyphs = []
		for layer in font.selectedLayers:
			glyph = layer.parent
			if glyph not in glyphs:
				glyphs.append(glyph)
		return glyphs

	def finish(self, font, title, summary):
		print("\n%s" % summary)
		Glyphs.showNotification("Rounding Protector: %s" % title, "%s Details in Macro Window." % summary)

	def runSafely(self, action):
		try:
			Glyphs.clearLog()
			self.SavePreferences()
			font = self.currentFont()
			if font is None:
				return
			print("Rounding Protector Report for %s" % font.familyName)
			if font.filepath:
				print(font.filepath)
			print()
			font.disableUpdateInterface()
			try:
				action(font)
			finally:
				font.enableUpdateInterface()
		except Exception as e:
			Glyphs.showMacroWindow()
			print("Rounding Protector Error: %s" % e)
			import traceback
			print(traceback.format_exc())

	# ---- actions ----

	def markSelectedNodes(self, protect):

		def action(font):
			overwrite = self.prefBool("overwriteNames")
			sync = self.prefBool("syncAfter")
			nodeCount, keptCount = 0, 0
			for layer in font.selectedLayers:
				nodes = [node for node in layer.selection if isinstance(node, GSNode) and node.type != OFFCURVE]
				for node in nodes:
					if setProtection(node, protect, overwrite):
						nodeCount += 1
					else:
						keptCount += 1
				if nodes:
					print("%s %s, layer ‘%s’: %i node%s" % ("🔒" if protect else "🔓", layer.parent.name, layer.name, len(nodes), "" if len(nodes) == 1 else "s"))
				if sync and nodes:
					syncGlyph(layer.parent, layer, overwrite)
			if keptCount:
				print("⚠️ %i node%s with another name left alone." % (keptCount, "" if keptCount == 1 else "s"))
			if nodeCount == 0 and keptCount == 0:
				print("⚠️ No on-curve nodes selected.")
			self.finish(font, "Done", "%s %i selected node%s." % ("Protected" if protect else "Unprotected", nodeCount, "" if nodeCount == 1 else "s"))

		self.runSafely(action)

	def protectSelected(self, sender=None):
		self.markSelectedNodes(True)

	def unprotectSelected(self, sender=None):
		self.markSelectedNodes(False)

	def protectOverlaps(self, sender=None):

		def action(font):
			overwrite = self.prefBool("overwriteNames")
			sync = self.prefBool("syncAfter")
			master = self.sourceMaster(font)
			distance = PROBE_DISTANCE * font.upm / 1000.0
			glyphs = self.glyphsInScope(font)
			print("Source master: %s, %i glyph%s\n" % (master.name, len(glyphs), "" if len(glyphs) == 1 else "s"))
			nodeCount, keptCount = 0, 0
			for glyph in glyphs:
				layer = glyph.layers[master.id]
				if len(layer.paths) < 1:
					continue
				insideNodes = nodesInsideOverlaps(layer, distance)
				for node in insideNodes:
					if setProtection(node, True, overwrite):
						nodeCount += 1
					else:
						keptCount += 1
				if insideNodes:
					print("🔒 %s: %i node%s in overlaps" % (glyph.name, len(insideNodes), "" if len(insideNodes) == 1 else "s"))
				if sync:
					syncGlyph(glyph, layer, overwrite)
			if keptCount:
				print("⚠️ %i node%s with another name left alone." % (keptCount, "" if keptCount == 1 else "s"))
			self.finish(font, "Done", "Protected %i node%s inside overlaps." % (nodeCount, "" if nodeCount == 1 else "s"))

		self.runSafely(action)

	def syncMaster(self, sender=None):

		def action(font):
			overwrite = self.prefBool("overwriteNames")
			master = self.sourceMaster(font)
			glyphs = self.glyphsInScope(font)
			print("Source master: %s, %i glyph%s\n" % (master.name, len(glyphs), "" if len(glyphs) == 1 else "s"))
			for glyph in glyphs:
				layer = glyph.layers[master.id]
				if len(layer.paths) < 1:
					continue
				syncGlyph(glyph, layer, overwrite)
			self.finish(font, "Done", "Synced protection from master ‘%s’ for %i glyph%s." % (master.name, len(glyphs), "" if len(glyphs) == 1 else "s"))

		self.runSafely(action)


RoundingProtector()
