# MenuTitle: Compatibility Manager 2
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Rebuilds interpolation compatibility between masters: reorders paths and
components for shortest travel, resets start points, and optionally adds
missing components/anchors. Always removes empty paths and propagates
corner components.
"""

import math
import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, GSPath, GSComponent, GSAnchor, OFFCURVE, CORNER, SEGMENT, CAP
from AppKit import NSPoint


# ─── geometry / travel helpers ───────────────────────────────────────────────

def deSlant(pt, italicAngle):
	"""Return de-slanted NSPoint (applies −italicAngle shear to compensate for italic)."""
	if italicAngle == 0.0:
		return pt
	return NSPoint(pt.x - math.tan(math.radians(italicAngle)) * pt.y, pt.y)


def normalizedPositions(path, italicAngle=0.0):
	"""
	Return list of NSPoint, each in [0,1]×[0,1], derived from path nodes
	de-slanted by italicAngle and normalised within the path's own bounding box.
	"""
	nodes = path.nodes
	if not nodes:
		return []
	pts = [deSlant(n.position, italicAngle) for n in nodes]
	xs = [p.x for p in pts]
	ys = [p.y for p in pts]
	w = (max(xs) - min(xs)) or 1.0
	h = (max(ys) - min(ys)) or 1.0
	ox, oy = min(xs), min(ys)
	return [NSPoint((p.x - ox) / w, (p.y - oy) / h) for p in pts]


def _pointsTravel(pos1, pos2):
	return sum(math.hypot(a.x - b.x, a.y - b.y) for a, b in zip(pos1, pos2))


def minTravelForPaths(path, refPath, italicAngle, refItalicAngle):
	"""
	Return (minTravel, bestOffset) over all start-point rotations of path
	whose node-type sequence matches refPath exactly.
	Returns (inf, 0) when no compatible rotation exists.
	"""
	n = len(path.nodes)
	if n != len(refPath.nodes) or n == 0:
		return float('inf'), 0

	myTypes = [nd.type for nd in path.nodes]
	refTypes = [nd.type for nd in refPath.nodes]
	if sorted(myTypes) != sorted(refTypes):
		return float('inf'), 0

	myPos = normalizedPositions(path, italicAngle)
	refPos = normalizedPositions(refPath, refItalicAngle)

	best = float('inf')
	bestOff = 0
	for off in range(n):
		if myTypes[off:] + myTypes[:off] != refTypes:
			continue
		travel = _pointsTravel(myPos[off:] + myPos[:off], refPos)
		if travel < best:
			best = travel
			bestOff = off
	return best, bestOff


def applyStartOffset(path, offset):
	"""
	Rotate path so that nodes[offset] becomes the new first node.
	makeNodeFirst_ makes the node AFTER the argument the new first node.
	"""
	if offset > 0:
		path.makeNodeFirst_(path.nodes[offset - 1])


def normalizedCenter(shape, layer, italicAngle):
	"""
	De-slanted, layer-bounds-normalised center of a shape as NSPoint in [0,1]².
	"""
	b = shape.bounds
	cx = b.origin.x + b.size.width * 0.5
	cy = b.origin.y + b.size.height * 0.5
	pt = deSlant(NSPoint(cx, cy), italicAngle)
	lb = layer.bounds
	lw = lb.size.width or 1.0
	lh = lb.size.height or 1.0
	return NSPoint((pt.x - lb.origin.x) / lw, (pt.y - lb.origin.y) / lh)


def shapeCost(shape, refShape, layer, refLayer):
	"""
	Travel cost for matching shape to refShape. Returns inf for incompatible types/names.
	Component travel is only calculated when auto-alignment is off (pixel fonts).
	"""
	if type(shape) is not type(refShape):
		return float('inf')

	if isinstance(shape, GSPath):
		travel, _ = minTravelForPaths(shape, refShape, layer.italicAngle, refLayer.italicAngle)
		return travel

	if isinstance(shape, GSComponent):
		if shape.componentName != refShape.componentName:
			return float('inf')
		if shape.automaticAlignment:
			return 0.0
		c1 = normalizedCenter(shape, layer, layer.italicAngle)
		c2 = normalizedCenter(refShape, refLayer, refLayer.italicAngle)
		return math.hypot(c1.x - c2.x, c1.y - c2.y)

	return float('inf')


# ─── layer operations ────────────────────────────────────────────────────────

def removeEmptyPaths(layer):
	"""Remove GSPath objects that have no nodes (reverse-iterates shapes)."""
	for i in range(len(layer.shapes) - 1, -1, -1):
		s = layer.shapes[i]
		if isinstance(s, GSPath) and not s.nodes:
			del layer.shapes[i]


def resetStartPointsInLayer(layer):
	"""
	Set start point of each path in layer to the on-curve node closest to
	y=0 (primary) and x=0 (secondary). Used for the reference layer only.
	"""
	for path in layer.paths:
		candidates = [(i, nd) for i, nd in enumerate(path.nodes) if nd.type != OFFCURVE]
		if not candidates:
			continue
		candidates.sort(key=lambda t: (abs(t[1].position.y), abs(t[1].position.x)))
		idx = candidates[0][0]
		if idx > 0:
			path.makeNodeFirst_(path.nodes[idx - 1])


def reorderShapes(layer, refLayer):
	"""
	Greedily reorder layer.shapes to match refLayer.shapes by lowest shapeCost.
	Returns True on success, False when a shape has no compatible match.
	"""
	remaining = list(layer.shapes)
	newOrder = []
	for refShape in refLayer.shapes:
		bestIdx = None
		bestCost = float('inf')
		for i, shape in enumerate(remaining):
			cost = shapeCost(shape, refShape, layer, refLayer)
			if cost < bestCost:
				bestCost = cost
				bestIdx = i
		if bestIdx is None or math.isinf(bestCost):
			return False
		newOrder.append(remaining.pop(bestIdx))
	newOrder.extend(remaining)
	layer.shapes = newOrder
	return True


def propagateCornerComponents(glyph, refLayer):
	"""Copy CORNER/SEGMENT/CAP hints from refLayer to all structurally compatible layers."""
	supportedTypes = (CORNER, SEGMENT, CAP)
	refCS = refLayer.compareString()
	for layer in glyph.layers:
		if layer is refLayer or not (layer.isMasterLayer or layer.isSpecialLayer):
			continue
		if layer.compareString() != refCS:
			continue
		toRemove = [h for h in layer.hints if h.type in supportedTypes]
		for h in reversed(toRemove):
			layer.removeHint_(h)
		for h in refLayer.hints:
			if h.type in supportedTypes:
				layer.hints.append(h.copy())


def insertMissingAnchors(glyph, verbose=False):
	"""
	Ensure every anchor name present in any master/special layer also exists in
	all other master/special layers. Placement uses the average of relative
	positions (respecting italic angle) from layers that already have the anchor.
	Returns a list of log strings.
	"""
	layers = [l for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer]
	log = []

	# collect relative positions per anchor name: {name: [(relX, relY), ...]}
	anchorData = {}
	for layer in layers:
		w = layer.width or 1.0
		lb = layer.bounds
		lh = lb.size.height or 1.0
		for anchor in layer.anchors:
			pt = deSlant(anchor.position, layer.italicAngle)
			rel = (pt.x / w, (pt.y - lb.origin.y) / lh)
			anchorData.setdefault(anchor.name, []).append(rel)

	for layer in layers:
		existingNames = {a.name for a in layer.anchors}
		w = layer.width or 1.0
		lb = layer.bounds
		lh = lb.size.height or 1.0
		for name, relPositions in anchorData.items():
			if name in existingNames:
				continue
			relX = sum(r[0] for r in relPositions) / len(relPositions)
			relY = sum(r[1] for r in relPositions) / len(relPositions)
			absY = relY * lh + lb.origin.y
			absX = relX * w + math.tan(math.radians(layer.italicAngle)) * absY
			newAnchor = GSAnchor()
			newAnchor.name = name
			newAnchor.position = NSPoint(absX, absY)
			layer.anchors.append(newAnchor)
			if verbose:
				log.append(f"    ➕ {layer.name}: added anchor '{name}' at ({absX:.0f}, {absY:.0f})")
	return log


def addMissingComponents(glyph, refLayer, verbose=False):
	"""
	Add any component present in refLayer but absent from another layer.
	Auto-alignment and name are copied from refLayer. The shapes will be
	reordered in a later step if needed.
	Returns a list of log strings.
	"""
	layers = [l for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer]
	log = []
	refCompNames = [s.componentName for s in refLayer.shapes if isinstance(s, GSComponent)]
	for layer in layers:
		if layer is refLayer:
			continue
		myCompNames = {s.componentName for s in layer.shapes if isinstance(s, GSComponent)}
		for name in refCompNames:
			if name not in myCompNames:
				refComp = next(s for s in refLayer.shapes if isinstance(s, GSComponent) and s.componentName == name)
				newComp = GSComponent(name)
				newComp.automaticAlignment = refComp.automaticAlignment
				layer.components.append(newComp)
				if verbose:
					log.append(f"    ➕ {layer.name}: added component '{name}'")
	return log


def syncComponentAttrs(layer, refLayer):
	"""
	Sync autoAlignment, scale, and shape attributes of components
	from refLayer to layer (matched by index).
	"""
	refComps = [s for s in refLayer.shapes if isinstance(s, GSComponent)]
	myComps = [s for s in layer.shapes if isinstance(s, GSComponent)]
	for myC, refC in zip(myComps, refComps):
		myC.automaticAlignment = refC.automaticAlignment
		try:
			myC.scale = refC.scale
		except Exception:
			pass
		try:
			if hasattr(refC, 'attributes') and refC.attributes:
				myC.attributes = dict(refC.attributes)
		except Exception:
			pass


def incompatibilityReason(layer, refLayer):
	"""
	Return a human-readable explanation of why compatibility cannot be achieved,
	or None if the layers look structurally matchable (modulo ordering).
	"""
	rPaths = refLayer.paths
	mPaths = layer.paths
	rComps = [s for s in refLayer.shapes if isinstance(s, GSComponent)]
	mComps = [s for s in layer.shapes if isinstance(s, GSComponent)]

	if len(mPaths) != len(rPaths):
		return f"differing numbers of paths ({len(mPaths)} vs {len(rPaths)} in reference)"
	if len(mComps) != len(rComps):
		return f"differing numbers of components ({len(mComps)} vs {len(rComps)} in reference)"
	if sorted(c.componentName for c in mComps) != sorted(c.componentName for c in rComps):
		return f"differing component names"
	for i, (mp, rp) in enumerate(zip(mPaths, rPaths)):
		if len(mp.nodes) != len(rp.nodes):
			return f"differing node counts in path #{i} ({len(mp.nodes)} vs {len(rp.nodes)})"
		if sorted(nd.type for nd in mp.nodes) != sorted(nd.type for nd in rp.nodes):
			return f"differing node types in path #{i}"
	return None


def isGlyphCompatible(glyph):
	"""True when all master/special layers share the same compareString."""
	layers = [l for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer]
	if len(layers) < 2:
		return True
	base = layers[0].compareString()
	return all(l.compareString() == base for l in layers[1:])


# ─── main class ──────────────────────────────────────────────────────────────

class CompatibilityManager2(mekkaObject):
	prefDict = {
		"resetStartPoints": 0,
		"addMissingComponents": 0,
		"addMissingAnchors": 1,
		"syncComponentAttributes": 0,
		"verboseReport": 0,
		"processCompleteFont": 0,
		"openIncompatibleInTab": 1,
	}

	def __init__(self):
		linePos, inset, lineHeight = 12, 15, 22
		col2 = 268

		# pre-compute window height
		nCheckboxRows = 4
		windowHeight = linePos + nCheckboxRows * lineHeight + 6 + 1 + 10 + lineHeight + 16 + inset
		windowWidth = 520

		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Compatibility Manager 2",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth, windowHeight),
			autosaveName=self.domain("mainwindow"),
		)

		# ── checkboxes (2 columns × 4 rows) ──
		checkboxDefs = (
			# (prefName, label, col, tooltip)
			(
				"resetStartPoints",
				"Reset start points",
				inset,
				"Before processing, reset the start point of each path in the first "
				"master to the on-curve node closest to y=0 (secondarily to x=0), "
				"for cleaner bottom-anchored interpolation motion.",
			),
			(
				"addMissingComponents",
				"Add missing components",
				col2,
				"If a component exists in some layers but is absent from others, add it "
				"to the missing layers, respecting the reference order and auto-alignment.",
			),
			(
				"addMissingAnchors",
				"Add missing anchors",
				inset,
				"Add any anchor present in some layers but absent from others. The anchor "
				"is placed at the average relative position across layers that have it, "
				"respecting italic angle and vertical metrics.",
			),
			(
				"syncComponentAttributes",
				"Sync component attributes",
				col2,
				"Sync auto-alignment, scale, and other properties (subtract/mask) of "
				"components from the first master layer to all other layers.",
			),
			(
				"verboseReport",
				"Verbose report in Macro Window",
				inset,
				"Log detailed per-glyph and per-layer processing steps to the Macro Window.",
			),
			(
				"processCompleteFont",
				"Process complete font",
				col2,
				"Process every glyph in the font, ignoring the current selection. "
				"If unchecked, only selected glyphs are processed.",
			),
			(
				"openIncompatibleInTab",
				"Open incompatible glyphs in new tab",
				inset,
				"After processing, open all glyphs that could not be made fully "
				"compatible in a new Edit tab for manual review.",
			),
		)

		currentRow = 0
		prevCol = None
		for prefName, label, col, tooltip in checkboxDefs:
			if prevCol is not None and col <= prevCol:
				linePos += lineHeight
			colW = col2 - inset if col == inset else -inset
			cb = vanilla.CheckBox(
				(col, linePos, colW, 20),
				label,
				value=bool(self.prefDict[prefName]),
				callback=self.SavePreferences,
				sizeStyle="small",
			)
			cb.setToolTip(tooltip)
			setattr(self.w, prefName, cb)
			prevCol = col

		linePos += lineHeight

		# ── divider ──
		linePos += 6
		self.w.divider = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 10

		# ── progress bar + run button (same row) ──
		self.w.progress = vanilla.ProgressBar((inset, linePos + 2, -90 - inset * 2, 14))
		self.w.runButton = vanilla.Button((-80 - inset, linePos - 1, -inset, 20), "Run", callback=self.run, sizeStyle="small")
		self.w.setDefaultButton(self.w.runButton)
		linePos += lineHeight

		# ── status text ──
		self.w.status = vanilla.TextBox((inset, linePos, -inset, 14), "", sizeStyle="small")

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		pass

	def SavePreferences(self, sender=None):
		super().SavePreferences(sender)

	def _setStatus(self, msg):
		self.w.status.set(msg)

	def run(self, sender):
		font = Glyphs.font
		if not font:
			self._setStatus("⚠️ No font open.")
			return

		verbose = self.prefBool("verboseReport")
		processAll = self.prefBool("processCompleteFont")
		doReset = self.prefBool("resetStartPoints")
		doAddComps = self.prefBool("addMissingComponents")
		doAddAnchors = self.prefBool("addMissingAnchors")
		doSyncAttrs = self.prefBool("syncComponentAttributes")
		doOpenTab = self.prefBool("openIncompatibleInTab")

		glyphs = list(font.glyphs) if processAll else list({l.parent for l in font.selectedLayers})
		total = len(glyphs)

		Glyphs.clearLog()
		print("Compatibility Manager 2 Report\n")

		self.w.progress.set(0)
		incompatible = []

		font.disableUpdateInterface()
		try:
			for idx, glyph in enumerate(glyphs):
				self._setStatus(f"Processing {glyph.name} …")
				result = self._processGlyph(
					glyph,
					doReset=doReset,
					doAddComps=doAddComps,
					doAddAnchors=doAddAnchors,
					doSyncAttrs=doSyncAttrs,
					verbose=verbose,
				)
				if result is not True:
					incompatible.append((glyph.name, result))
					print(f"❌ {glyph.name}: {result}")
				elif verbose:
					print(f"  ✅ {glyph.name}: compatible")
				self.w.progress.set(int((idx + 1) / total * 100))
		finally:
			font.enableUpdateInterface()

		if doOpenTab and incompatible:
			font.newTab("/" + "/".join(name for name, _ in incompatible))

		summary = f"✅ Done. {total - len(incompatible)}/{total} compatible. See Macro Window."
		self._setStatus(summary)
		Glyphs.showNotification(
			"Compatibility Manager 2",
			f"Done. {len(incompatible)} glyph(s) could not be made compatible.",
		)

	# ── glyph-level processing ────────────────────────────────────────────────

	def _processGlyph(self, glyph, doReset=False, doAddComps=False, doAddAnchors=True, doSyncAttrs=False, verbose=False):
		"""
		Process one glyph. Returns True when the glyph ends up compatible,
		or an error string describing why compatibility could not be achieved.
		If the glyph was already compatible before processing but would become
		incompatible, the changes are reverted and True is returned.
		"""
		layers = [l for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer]
		if len(layers) < 2:
			return True

		wasCompatible = isGlyphCompatible(glyph)

		# snapshot shapes so we can revert if we accidentally break things
		snapshots = {l.layerId: [s.copy() for s in l.shapes] for l in layers}

		refLayer = layers[0]

		if verbose:
			print(f"\n  {glyph.name}:")

		# 1. remove empty paths from all layers
		for layer in layers:
			removeEmptyPaths(layer)

		# 2. optionally reset start points in reference layer
		if doReset:
			resetStartPointsInLayer(refLayer)
			if verbose:
				print(f"    🔄 {refLayer.name}: start points reset")

		# 3. optionally add missing components before reordering
		if doAddComps:
			log = addMissingComponents(glyph, refLayer, verbose=verbose)
			if verbose:
				for msg in log:
					print(msg)

		# 4. make each subsequent layer compatible with refLayer
		errorReason = None
		for layer in layers[1:]:
			removeEmptyPaths(layer)
			reason = self._makeLayerCompatible(layer, refLayer, verbose=verbose)
			if reason and errorReason is None:
				errorReason = reason

		# 5. optionally add missing anchors
		if doAddAnchors:
			log = insertMissingAnchors(glyph, verbose=verbose)
			if verbose:
				for msg in log:
					print(msg)

		# 6. optionally sync component attributes
		if doSyncAttrs:
			for layer in layers[1:]:
				syncComponentAttrs(layer, refLayer)

		# 7. always propagate corner components (only when compatible)
		if errorReason is None:
			propagateCornerComponents(glyph, refLayer)

		# 8. safety: if we broke a previously compatible glyph, revert
		if wasCompatible and not isGlyphCompatible(glyph):
			for layer in layers:
				layer.shapes = snapshots[layer.layerId]
			if verbose:
				print(f"    ↩️ {glyph.name}: reverted (was already compatible; changes would have broken it)")
			return True

		return errorReason or True

	def _makeLayerCompatible(self, layer, refLayer, verbose=False):
		"""
		Attempt to make layer compatible with refLayer.
		Returns None on success, or an explanatory error string on failure.
		"""
		if layer.compareString() == refLayer.compareString():
			if verbose:
				print(f"    ☑️ {layer.name}: already compatible")
			return None

		# fast structural pre-check via compareString-based heuristic
		reason = incompatibilityReason(layer, refLayer)
		if reason:
			return reason

		# reorder shapes (paths + components together) by shortest travel
		if not reorderShapes(layer, refLayer):
			return incompatibilityReason(layer, refLayer) or "shape reordering failed"

		# set best start point for each path pair
		for pathIdx, (path, refPath) in enumerate(zip(layer.paths, refLayer.paths)):
			travel, offset = minTravelForPaths(path, refPath, layer.italicAngle, refLayer.italicAngle)
			if math.isinf(travel):
				return f"incompatible path #{pathIdx}: no valid start-point rotation found"
			applyStartOffset(path, offset)

		# final confirmation
		if layer.compareString() != refLayer.compareString():
			return incompatibilityReason(layer, refLayer) or "incompatible after processing"

		if verbose:
			print(f"    ✅ {layer.name}: made compatible")
		return None


CompatibilityManager2()
