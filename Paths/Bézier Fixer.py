# MenuTitle: Bézier Fixer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Small floating panel combining three curve cleanup steps for the selected glyphs: Realign (fixes out-of-sync BCPs of smooth nodes), Tunnify (balances handle distribution, Tunnify 2 algorithm, adjustable strength), and Harmonize (establishes G2 continuity at smooth nodes, Green Harmony algorithm). Previews live in the active layer as you toggle the checkboxes or drag the slider, without committing anything. A partial node selection restricts preview and fix to the segments touching the selected nodes (unselected segments revert to their previous state); no selection or a full selection (Cmd-A) processes the whole layer. Fix commits the result and, if All Masters is on, propagates it to the other masters/special layers; closing the panel without clicking Fix reverts the preview and leaves the glyph untouched. Replaces the separate Realign BCPs, Tunnify and Tunnify 2.0 scripts.
"""

import math
import vanilla
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSSMOOTH, GSOFFCURVE, GSCURVE, Message, UPDATEINTERFACE
from mekkablue import mekkaObject

# ---------------------------------------------------------------------------
# Selection helper: when a set of selected nodes is passed to the layer
# functions, only segments/nodes that touch the selection are processed.
# selectedNodes=None means "no restriction, process the whole layer".
# ---------------------------------------------------------------------------


def nodesInSelection(selectedNodes, *nodes):
	"""True if the operation may proceed: either unrestricted (None) or at
	least one of the involved nodes is part of the selection."""
	if selectedNodes is None:
		return True
	return any(n in selectedNodes for n in nodes)


# ---------------------------------------------------------------------------
# Realign: fixes out-of-sync BCPs of smooth nodes.
# Algorithm: mekkablue Realign BCPs / RealignHandles.
# ---------------------------------------------------------------------------


def closestPointOnLine(P, A, B):
	AB = NSPoint(B.x - A.x, B.y - A.y)
	AP = NSPoint(P.x - A.x, P.y - A.y)
	dotProduct = AB.x * AP.x + AB.y * AP.y
	ABsquared = AB.x**2 + AB.y**2
	t = dotProduct / ABsquared
	return NSPoint(A.x + t * AB.x, A.y + t * AB.y)


def ortho(n1, n2):
	xDiff = n1.x - n2.x
	yDiff = n1.y - n2.y
	# must not have the same coordinates, and either vertical or horizontal:
	if xDiff != yDiff and xDiff * yDiff == 0.0:
		return True
	return False


def triplet(n1, n2, n3):
	return (*n1.position, *n2.position, *n3.position)


def realignLayer(layer, selectedNodes=None):
	handleCount = 0
	for p in layer.paths:
		for n in p.nodes:
			if n.connection != GSSMOOTH:
				continue
			nn, pn = n.nextNode, n.prevNode
			if not nodesInSelection(selectedNodes, n, nn, pn):
				continue
			if all((nn.type == GSOFFCURVE, pn.type == GSOFFCURVE)):
				# surrounding points are BCPs
				smoothen, center, opposite = None, None, None
				for handle in (nn, pn):
					if ortho(handle, n):
						center = n
						opposite = handle
						smoothen = nn if nn != handle else pn
						oldPos = triplet(smoothen, center, opposite)
						p.setSmooth_withCenterNode_oppositeNode_(smoothen, center, opposite)
						if oldPos != triplet(smoothen, center, opposite):
							handleCount += 1
						break
				if smoothen == center == opposite is None:
					oldPos = triplet(n, nn, pn)
					n.position = closestPointOnLine(n.position, nn, pn)
					if oldPos != triplet(n, nn, pn):
						handleCount += 1
			elif n.type != GSOFFCURVE and (nn.type, pn.type).count(GSOFFCURVE) == 1:
				# only one of the surrounding points is a BCP
				center = n
				if nn.type == GSOFFCURVE:
					smoothen, opposite = nn, pn
				elif pn.type == GSOFFCURVE:
					smoothen, opposite = pn, nn
				else:
					continue  # should never occur
				oldPos = triplet(smoothen, center, opposite)
				p.setSmooth_withCenterNode_oppositeNode_(smoothen, center, opposite)
				if oldPos != triplet(smoothen, center, opposite):
					handleCount += 1
	return handleCount


# ---------------------------------------------------------------------------
# Tunnify: balances the handle distribution of curve segments.
# Algorithm: mekkablue Tunnify 2.0, keeping the point at t=0.5 on the segment.
# strength (0.5–1.0) blends between the original handles (0.0) and the
# fully tunnified handles (1.0), e.g. 0.6 = 60% of a full Tunnify.
# ---------------------------------------------------------------------------


def segmentMaxHandle(a, b, c, d):
	"""
	Intersection of segments a-b and c-d with zero-handle fix.
	a, b, c, d are GSNode. Returns NSPoint or None.
	"""
	pa, pb, pc, pd = a.position, b.position, c.position, d.position

	# Zero-handle fixes
	if pa.x == pb.x and pa.y == pb.y:
		pb = pc
	if pc.x == pd.x and pc.y == pd.y:
		pc = pb

	x1, y1 = pa.x, pa.y
	x2, y2 = pb.x, pb.y
	x3, y3 = pc.x, pc.y
	x4, y4 = pd.x, pd.y

	den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
	if den == 0:
		return None

	t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
	u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / den

	if 0.0 <= t and u <= 1.0:
		return NSPoint(x1 + t * (x2 - x1), y1 + t * (y2 - y1))
	return None


def bezierPoint(a, b, c, d, t):
	"""Point on a cubic Bézier curve at parameter t. a, b, c, d are NSPoint."""
	x = (1 - t)**3 * a.x + 3 * (1 - t)**2 * t * b.x + 3 * (1 - t) * t**2 * c.x + t**3 * d.x
	y = (1 - t)**3 * a.y + 3 * (1 - t)**2 * t * b.y + 3 * (1 - t) * t**2 * c.y + t**3 * d.y
	return NSPoint(x, y)


def vectorFromTo(p1, p2):
	return NSPoint(p2.x - p1.x, p2.y - p1.y)


def scaleVector(v, scale):
	return NSPoint(v.x * scale, v.y * scale)


def addVectors(p, v):
	return NSPoint(p.x + v.x, p.y + v.y)


def distance(p1, p2):
	return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)


def mid(p1, p2):
	return NSPoint((p1.x + p2.x) * 0.5, (p1.y + p2.y) * 0.5)


def mixPoints(p1, p2, t):
	"""Point at percentage t (0.0–1.0) between p1 and p2."""
	return NSPoint(p1.x + (p2.x - p1.x) * t, p1.y + (p2.y - p1.y) * t)


def changeCurvatureToPassThroughPoint(a, b, c, d, passThroughPoint, min_t=0.3, max_t=0.7):
	"""
	Adjusts control points b and c along the a-b and d-c vectors so the
	cubic Bézier curve passes as closely as possible through passThroughPoint.
	Returns (new_b, new_c).
	"""
	vec_ab = vectorFromTo(b, a)
	vec_dc = vectorFromTo(c, d)

	best_scale = 0
	best_dist = float("inf")

	t_values = [min_t + i * (max_t - min_t) / 50 for i in range(51)]
	scale_values = [i * 0.01 for i in range(-100, 101)]

	for t in t_values:
		for scale in scale_values:
			new_b = addVectors(b, scaleVector(vec_ab, scale))
			new_c = addVectors(c, scaleVector(vec_dc, scale))
			pt = bezierPoint(a, new_b, new_c, d, t)
			dist = distance(pt, passThroughPoint)
			if dist < best_dist:
				best_dist = dist
				best_scale = scale

	new_b = addVectors(b, scaleVector(vec_ab, best_scale))
	new_c = addVectors(c, scaleVector(vec_dc, best_scale))
	return new_b, new_c


def tunnifySegment(a, b, c, d, strength=1.0):
	maxPt = segmentMaxHandle(a, b, c, d)
	if maxPt is None:
		return
	origA, origB, origC, origD = a.position, b.position, c.position, d.position
	passThrough = bezierPoint(origA, origB, origC, origD, 0.5)
	newB, newC = changeCurvatureToPassThroughPoint(
		origA,
		mid(origB, maxPt),
		mid(origC, maxPt),
		origD,
		passThrough,
		min_t=0.3,
		max_t=0.7,
	)
	if strength < 1.0:
		newB = mixPoints(origB, newB, strength)
		newC = mixPoints(origC, newC, strength)
	b.position = newB
	c.position = newC


def tunnifyLayer(layer, strength=1.0, selectedNodes=None):
	for p in layer.paths:
		for i, a in enumerate(p.nodes):
			if a.type == GSOFFCURVE:
				continue
			if p.closed is False and i > (len(p.nodes) - 4):
				continue
			b = a.nextNode
			if b.type != GSOFFCURVE:
				continue
			c, d = a.nextNode.nextNode, a.nextNode.nextNode.nextNode
			if c.type != GSOFFCURVE or d.type == GSOFFCURVE:
				continue
			if not nodesInSelection(selectedNodes, a, b, c, d):
				continue
			tunnifySegment(a, b, c, d, strength=strength)


# ---------------------------------------------------------------------------
# Harmonize: establishes G2 continuity at smooth on-curve nodes by moving
# the node (never the handles) to the position dictated by the curvature
# of the two adjoining segments. Algorithm: mekkablue Green Harmony.
# ---------------------------------------------------------------------------


def harmonizeIntersection(x1, y1, x2, y2, x3, y3, x4, y4):
	denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
	if denom == 0.0:
		return None
	px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
	py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
	return NSPoint(px, py)


def harmonizeRemap(oldValue, oldMin, oldMax, newMin, newMax):
	oldRange = oldMax - oldMin
	if oldRange == 0.0:
		return newMin
	newRange = newMax - newMin
	return (((oldValue - oldMin) * newRange) / oldRange) + newMin


def harmonizeNode(node):
	nextHandle, prevHandle = node.nextNode, node.prevNode
	if nextHandle is None or prevHandle is None:
		return False
	if nextHandle.type != GSOFFCURVE or prevHandle.type != GSOFFCURVE:
		return False

	farNext, farPrev = nextHandle.nextNode, prevHandle.prevNode
	if farNext is None or farPrev is None:
		return False

	intersection = harmonizeIntersection(
		nextHandle.x,
		nextHandle.y,
		farNext.x,
		farNext.y,
		prevHandle.x,
		prevHandle.y,
		farPrev.x,
		farPrev.y,
	)
	if intersection is None:
		return False

	distNextToIntersection = distance(nextHandle.position, intersection)
	distPrevToFarPrev = distance(prevHandle.position, farPrev.position)
	if distNextToIntersection == 0.0 or distPrevToFarPrev == 0.0:
		return False

	r0 = distance(farNext.position, nextHandle.position) / distNextToIntersection
	r1 = distance(intersection, prevHandle.position) / distPrevToFarPrev
	product = r0 * r1
	if product < 0.0:
		return False

	ratio = math.sqrt(product)
	t = ratio / (ratio + 1.0)

	newPosition = NSPoint(
		harmonizeRemap(t, 0.0, 1.0, nextHandle.x, prevHandle.x),
		harmonizeRemap(t, 0.0, 1.0, nextHandle.y, prevHandle.y),
	)
	if node.position == newPosition:
		return False
	node.position = newPosition
	return True


def harmonizeLayer(layer, selectedNodes=None):
	handleCount = 0
	for p in layer.paths:
		for n in p.nodes:
			if n.type == GSCURVE and n.connection == GSSMOOTH:
				if not nodesInSelection(selectedNodes, n, n.nextNode, n.prevNode):
					continue
				if harmonizeNode(n):
					handleCount += 1
	return handleCount


# ---------------------------------------------------------------------------
# Shared pipeline: used both for the live preview and for the Fix button,
# so the two can never diverge. If a snapshot is given, the layer is reset
# to that pristine geometry first, so repeated calls (e.g., while dragging
# the slider) never drift and always reflect the current settings only.
# ---------------------------------------------------------------------------


def snapshotLayer(layer):
	"""Captures the current x/y of every node in the layer, keyed by node."""
	return {n: (n.x, n.y) for p in layer.paths for n in p.nodes}


def restoreSnapshot(snapshot):
	for n, (x, y) in snapshot.items():
		n.x, n.y = x, y


def selectedNodesOfLayer(layer):
	"""Set of selected on-/off-curve GSNodes in the layer, ignoring anchors etc."""
	selectionSet = set(layer.selection)
	return {n for p in layer.paths for n in p.nodes if n in selectionSet}


def effectiveSelection(layer):
	"""
	The set of selected path nodes if they form a partial selection,
	or None if the whole layer should be processed. None is returned in
	exactly two cases: no (node) selection at all, and a full selection
	(⌘A, every node of the layer selected). Anything in between restricts
	the fixes to the segments touching the selected nodes, leaving all
	other segments untouched.
	"""
	selectedNodes = selectedNodesOfLayer(layer)
	if not selectedNodes:
		return None
	totalNodeCount = sum(len(p.nodes) for p in layer.paths)
	if len(selectedNodes) >= totalNodeCount:
		return None
	return selectedNodes


def selectedNodeIndices(layer):
	"""Set of (pathIndex, nodeIndex) for every selected node in the layer.
	Used to map a selection onto the corresponding nodes of other (compatible)
	master/special layers when propagating a fix to All Masters."""
	selectionSet = set(layer.selection)
	indices = set()
	for pathIndex, p in enumerate(layer.paths):
		for nodeIndex, n in enumerate(p.nodes):
			if n in selectionSet:
				indices.add((pathIndex, nodeIndex))
	return indices


def nodesAtIndices(layer, indices):
	"""Resolves (pathIndex, nodeIndex) tuples into the GSNodes of the given layer."""
	nodes = set()
	paths = layer.paths
	for pathIndex, nodeIndex in indices:
		if pathIndex < len(paths):
			layerNodes = paths[pathIndex].nodes
			if nodeIndex < len(layerNodes):
				nodes.add(layerNodes[nodeIndex])
	return nodes


def applyFixPipeline(layer, doRealign, doTunnify, tunnifyStrength, doHarmonize, snapshot=None, selectedNodes=None):
	if snapshot is not None:
		restoreSnapshot(snapshot)
	if doRealign:
		realignLayer(layer, selectedNodes=selectedNodes)
	if doTunnify:
		tunnifyLayer(layer, strength=tunnifyStrength, selectedNodes=selectedNodes)
	if doHarmonize:
		harmonizeLayer(layer, selectedNodes=selectedNodes)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------


class BezierFixer(mekkaObject):
	prefDict = {
		"tunnify": True,
		"tunnifyStrength": 100,
		"realign": True,
		"harmonize": True,
		"allMasters": True,
	}

	def __init__(self):
		# live-preview state: which layers we last snapshotted, and their pristine geometry
		self.watchedLayerIDs = ()
		self.watchedSelectionIDs = ()
		self.watchedLayers = []
		self.snapshots = {}
		self.isApplyingPreview = False

		windowWidth = 126
		windowHeight = 160
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Bézier Fixer",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth, windowHeight),
			autosaveName=self.domain("mainwindow"),
		)

		linePos, inset, lineHeight = 12, 15, 18

		self.w.tunnify = vanilla.CheckBox((inset, linePos, -50, 18), "Tunnify", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.tunnify.setToolTip("Evens out the Bézier handle ratio of each curve segment to balance handles (Tunnify 2 algorithm). Keeps the point at t=0.5 on the segment.")
		self.w.tunnifyStrengthLabel = vanilla.TextBox((-55, linePos + 2, -(inset-5), 14), "100%", sizeStyle="small", alignment="right")
		linePos += lineHeight - 5

		self.w.tunnifyStrength = vanilla.Slider(
			(inset + 14, linePos, -(inset-5), 18),
			minValue=50,
			maxValue=100,
			value=100,
			tickMarkCount=6,
			stopOnTickMarks=True,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.tunnifyStrength.setToolTip("How much of the full Tunnify to apply. E.g., 60% = 60% of a full Tunnify, 40% of the original handle distribution.")
		linePos += lineHeight

		self.w.realign = vanilla.CheckBox((inset, linePos, -inset, 18), "Realign BCPs", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.realign.setToolTip("Realigns out-of-sync BCPs (handles) of smooth nodes, e.g. after nudging, interpolating, or changing the grid.")
		linePos += lineHeight

		self.w.harmonize = vanilla.CheckBox((inset, linePos, -inset, 18), "Harmonize", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.harmonize.setToolTip("Establishes G2 continuity at smooth nodes by moving the node, not the handles (see the Green Harmony plug-in).")
		linePos += lineHeight

		# self.w.divider = vanilla.HorizontalLine((inset, linePos + 3, -inset, 1))
		# linePos += lineHeight - 8

		self.w.allMasters = vanilla.CheckBox((inset, linePos, -inset, 18), "All Masters", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.allMasters.setToolTip("Applies the fixes to all masters and special layers of each selected glyph, not just the currently active layer.")
		linePos += lineHeight

		self.w.runButton = vanilla.Button((inset, -20 - inset, -inset, -inset), "Fix", callback=self.BezierFixerMain)
		self.w.runButton.setToolTip("Changes already preview live in the active layer, but are not committed yet. Fix commits them and, if All Masters is on, propagates them to the other masters/special layers too. Closing the panel without clicking Fix reverts the preview.")
		self.w.setDefaultButton(self.w.runButton)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

		# live preview: react to Glyphs' own selection/redraw events instead of polling
		Glyphs.addCallback(self.interfaceUpdated, UPDATEINTERFACE)
		self.w.bind("close", self.windowClose)
		self.interfaceUpdated()

	def windowClose(self, sender=None):
		Glyphs.removeCallback(self.interfaceUpdated)
		self.revertPreview()

	def revertPreview(self):
		"""
		Restores every watched layer back to its last committed baseline
		(the pristine original, or the result of the last Fix click if any),
		undoing whatever was only live-previewed but never committed.
		"""
		if not self.watchedLayers:
			return
		self.isApplyingPreview = True
		try:
			for layer in self.watchedLayers:
				snapshot = self.snapshots.get(layer)
				if snapshot is None:
					continue
				thisGlyph = layer.parent
				thisGlyph.beginUndo()
				try:
					restoreSnapshot(snapshot)
				finally:
					thisGlyph.endUndo()
			Glyphs.redraw()
		finally:
			self.isApplyingPreview = False

	def updateUI(self, sender=None):
		tunnifyOn = self.pref("tunnify")
		self.w.tunnifyStrength.enable(tunnifyOn)
		self.w.tunnifyStrengthLabel.set(f"{int(round(self.pref('tunnifyStrength')))}%")

	def interfaceUpdated(self, sender=None):
		"""
		Registered as the UPDATEINTERFACE callback, which fires very
		frequently (on almost any redraw, not just when the selection
		changes). Stays cheap on every one of those ticks: only when the
		watched layer(s) actually changed does it re-snapshot and re-run
		the (comparatively expensive) preview pipeline.
		"""
		if self.isApplyingPreview:
			return  # ignore redraw events triggered by our own writes below
		font = Glyphs.font
		layers = list(font.selectedLayers) if font else []
		layerIDs = tuple(id(layer) for layer in layers)
		selectionIDs = tuple(sorted(id(item) for layer in layers for item in layer.selection))
		if layerIDs == self.watchedLayerIDs:
			if selectionIDs == self.watchedSelectionIDs:
				return  # nothing relevant changed, don't recompute
			# same layer(s), but the node selection changed: re-run the preview
			# from the existing pristine snapshots, so segments that just left
			# the selection revert to their previous (uncommitted) state.
			self.watchedSelectionIDs = selectionIDs
			self.applyPreview()
			return
		self.watchedLayerIDs = layerIDs
		self.watchedSelectionIDs = selectionIDs
		self.watchedLayers = layers
		self.snapshots = {layer: snapshotLayer(layer) for layer in layers}
		self.applyPreview()

	def applyPreview(self, sender=None):
		"""
		Applies the current checkbox/slider settings to the watched
		layer(s). Always recomputes from the pristine snapshot taken when
		the layer was first seen, so dragging the slider or flipping a
		checkbox back and forth never drifts or compounds.
		"""
		if self.isApplyingPreview or not self.watchedLayers:
			return
		try:
			doTunnify = self.pref("tunnify")
			tunnifyStrength = self.pref("tunnifyStrength") / 100.0
			doRealign = self.pref("realign")
			doHarmonize = self.pref("harmonize")

			# respect a partial node selection when exactly one glyph is selected;
			# no selection or a full selection (⌘A) processes the whole layer
			restrictToSelection = len(self.watchedLayers) == 1

			self.isApplyingPreview = True
			try:
				for layer in self.watchedLayers:
					snapshot = self.snapshots.get(layer)
					if snapshot is None:
						continue
					selectedNodes = effectiveSelection(layer) if restrictToSelection else None
					thisGlyph = layer.parent
					thisGlyph.beginUndo()
					try:
						applyFixPipeline(layer, doRealign, doTunnify, tunnifyStrength, doHarmonize, snapshot=snapshot, selectedNodes=selectedNodes)
					finally:
						thisGlyph.endUndo()
				Glyphs.redraw()
			finally:
				self.isApplyingPreview = False
		except Exception:
			import traceback
			print("\n⚠️ Bézier Fixer live preview error\n")
			print(traceback.format_exc())

	def SavePreferences(self, sender=None):
		super().SavePreferences(sender)
		self.applyPreview()

	def BezierFixerMain(self, sender=None):
		try:
			Glyphs.clearLog()
			self.SavePreferences()

			thisFont = Glyphs.font
			if not thisFont:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			selectedLayers = thisFont.selectedLayers
			if not selectedLayers:
				Message(title="No Selection", message="Select one or more glyphs and try again.", OKButton=None)
				return

			doTunnify = self.pref("tunnify")
			tunnifyStrength = self.pref("tunnifyStrength") / 100.0
			doRealign = self.pref("realign")
			doHarmonize = self.pref("harmonize")
			allMasters = self.pref("allMasters")

			if not any((doTunnify, doRealign, doHarmonize)):
				Glyphs.showNotification("Bézier Fixer", "Nothing to do. Enable Tunnify, Realign, and/or Harmonize.")
				return

			print("Bézier Fixer Report\n")

			# respect a partial node selection when exactly one glyph is selected;
			# no selection or a full selection (⌘A) fixes the whole layer.
			# The selection is defined on the active layer only, so map it onto
			# the corresponding nodes of the other layers via node indices.
			restrictToSelection = len(selectedLayers) == 1 and effectiveSelection(selectedLayers[0]) is not None
			selectionIndices = selectedNodeIndices(selectedLayers[0]) if restrictToSelection else None

			processedGlyphNames = []
			thisFont.disableUpdateInterface()
			try:
				for thisLayer in selectedLayers:
					thisGlyph = thisLayer.parent
					if thisGlyph.name in processedGlyphNames:
						continue
					processedGlyphNames.append(thisGlyph.name)

					if allMasters:
						layersToFix = [l for l in thisGlyph.layers if l.isMasterLayer or l.isSpecialLayer]
					else:
						layersToFix = [thisLayer]

					thisGlyph.beginUndo()
					try:
						for layer in layersToFix:
							# reuse the pristine snapshot for layers already live-previewed,
							# so Fix reproduces exactly what was on screen, never a double-application
							snapshot = self.snapshots.get(layer)
							selectedNodes = nodesAtIndices(layer, selectionIndices) if selectionIndices is not None else None
							applyFixPipeline(layer, doRealign, doTunnify, tunnifyStrength, doHarmonize, snapshot=snapshot, selectedNodes=selectedNodes)
							if layer in self.snapshots:
								# this is now committed: closing the window should no longer revert past this point
								self.snapshots[layer] = snapshotLayer(layer)
					finally:
						thisGlyph.endUndo()

					print(f"\t✅ {thisGlyph.name}")
			finally:
				thisFont.enableUpdateInterface()

			glyphCount = len(processedGlyphNames)
			print(f"\nFixed {glyphCount} glyph{'' if glyphCount == 1 else 's'}.")
			Glyphs.showNotification("Bézier Fixer", f"Fixed {glyphCount} glyph{'' if glyphCount == 1 else 's'}. Details in Macro Window.")

		except Exception as e:
			Glyphs.showMacroWindow()
			print("\n⚠️ Error in Bézier Fixer\n")
			import traceback
			print(traceback.format_exc())
			print()
			raise e


BezierFixer()
