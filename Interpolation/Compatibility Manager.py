# MenuTitle: Compatibility Manager
__doc__ = """
Fixes the compatibility of the layers of selected glyphs: resets start points and reorders shapes; syncs node types, node connections and anchors; realigns smooth connections; removes empty paths and stray points; backs up layers in their backgrounds.
"""

import math
from copy import copy

import vanilla
from mekkablue import mekkaObject, newAnchorWithName, reportFontName
from GlyphsApp import Glyphs, GSPath, GSComponent, OFFCURVE, GSOFFCURVE, GSSMOOTH, Message, distance
from AppKit import (
	NSAffineTransform,
	NSLayoutAttributeCenterY,
	NSLayoutConstraint,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSLayoutRelationEqual,
	NSTextAlignmentLeft,
	NSTextAlignmentRight,
)
from Foundation import NSNotFound, NSPoint


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


def keyLayersOf(glyph):
	"""Master layers and special (brace and bracket) layers of a glyph."""
	return [layer for layer in glyph.layers if layer.isMasterLayer or layer.isSpecialLayer]


def selectedSourceLayers(font):
	"""The first selected layer of each selected glyph."""
	sourceLayers = []
	glyphNames = set()
	for layer in font.selectedLayers:
		glyphName = layer.parent.name
		if glyphName not in glyphNames:
			glyphNames.add(glyphName)
			sourceLayers.append(layer)
	return sourceLayers


def syncNodeAttribute(glyph, sourceLayer, attributeName):
	"""Copies a node attribute ("type" or "connection") from the source layer to the same nodes in the other key layers."""
	changedCount = 0
	for layer in keyLayersOf(glyph):
		if layer == sourceLayer:
			continue

		print(f"\t➡️ Layer ‘{layer.name}’")
		if len(sourceLayer.compareString()) != len(layer.compareString()):
			print("\t\t🚫 Not compatible due to different point or shape number. Skipping.")
			continue

		for pathIndex, sourcePath in enumerate(sourceLayer.paths):
			if pathIndex >= len(layer.paths):
				break
			path = layer.paths[pathIndex]
			if len(sourcePath.nodes) != len(path.nodes):
				continue
			for nodeIndex, sourceNode in enumerate(sourcePath.nodes):
				node = path.nodes[nodeIndex]
				sourceValue = getattr(sourceNode, attributeName)
				currentValue = getattr(node, attributeName)
				if sourceValue != currentValue:
					print(f"\t\t✅ {attributeName} p{pathIndex} n{nodeIndex}: should be {sourceValue}, but is {currentValue}")
					setattr(node, attributeName, sourceValue)
					changedCount += 1
	return changedCount


def straightenBCPs(layer):

	def closestPointOnLine(P, A, B):
		# vector of line AB
		AB = NSPoint(B.x - A.x, B.y - A.y)
		# vector from point A to point P
		AP = NSPoint(P.x - A.x, P.y - A.y)
		# dot product of AB and AP
		dotProduct = AB.x * AP.x + AB.y * AP.y
		ABsquared = AB.x**2 + AB.y**2
		t = dotProduct / ABsquared
		x = A.x + t * AB.x
		y = A.y + t * AB.y
		return NSPoint(x, y)

	def ortho(n1, n2):
		xDiff = n1.x - n2.x
		yDiff = n1.y - n2.y
		# must not have the same coordinates,
		# and either vertical or horizontal:
		if xDiff != yDiff and xDiff * yDiff == 0.0:
			return True
		return False

	realigned = 0
	for p in layer.paths:
		for n in p.nodes:
			if n.connection != GSSMOOTH:
				continue
			nn, pn = n.nextNode, n.prevNode
			oldCoords = (pn.position, n.position, nn.position)
			if all((nn.type == GSOFFCURVE, pn.type == GSOFFCURVE)):
				# surrounding points are BCPs
				smoothen, center, opposite = None, None, None
				for handle in (nn, pn):
					if ortho(handle, n):
						center = n
						opposite = handle
						smoothen = nn if nn != handle else pn
						p.setSmooth_withCenterNode_oppositeNode_(
							smoothen,
							center,
							opposite,
						)
						break
				if smoothen == center == opposite is None:
					n.position = closestPointOnLine(
						n.position,
						nn,
						pn,
					)

			elif n.type != GSOFFCURVE and (nn.type, pn.type).count(GSOFFCURVE) == 1:
				# only one of the surrounding points is a BCP
				center = n
				if nn.type == GSOFFCURVE:
					smoothen = nn
					opposite = pn
				elif pn.type == GSOFFCURVE:
					smoothen = pn
					opposite = nn
				else:
					continue  # should never occur
				p.setSmooth_withCenterNode_oppositeNode_(
					smoothen,
					center,
					opposite,
				)

			if oldCoords != (pn.position, n.position, nn.position):
				realigned += 1
	return realigned


def realignSmoothConnections(glyph, sourceLayer):
	realignedCount = 0
	for layer in keyLayersOf(glyph):
		count = straightenBCPs(layer)
		if count:
			print(f"\t✅ Layer ‘{layer.name}’: realigned {count} node{'' if count == 1 else 's'}")
			realignedCount += count
	return realignedCount


def removePathsWhere(glyph, condition, description):
	removedCount = 0
	for layer in keyLayersOf(glyph):
		for path in list(layer.paths):
			if condition(path):
				layer.removeShape_(path)
				print(f"\t✅ Layer ‘{layer.name}’: removed {description}")
				removedCount += 1
	return removedCount


def removeEmptyPaths(glyph, sourceLayer):
	return removePathsWhere(glyph, lambda path: len(path.nodes) == 0, "empty path")


def removeStrayPoints(glyph, sourceLayer):
	return removePathsWhere(glyph, lambda path: len(path.nodes) == 1, "stray point (single-node path)")


def backupLayers(glyph, sourceLayer):
	backedUpCount = 0
	for layer in keyLayersOf(glyph):
		layer.contentToBackgroundCheckSelection_keepOldBackground_(False, False)
		print(f"\t💕 Layer ‘{layer.name}’: backed up in background")
		backedUpCount += 1
	return backedUpCount


def anchorPositionsOnOutline(layer, anchor):
	"""
	If the anchor sits on a node, returns ((pathIndex, nodeIndex), None).
	If it only shares the x coordinate of a node, returns ((pathIndex, nodeIndex), anchorY).
	Otherwise returns None.
	"""
	for pathIndex, path in enumerate(layer.paths):
		for nodeIndex, node in enumerate(path.nodes):
			if node.position == anchor.position:
				return (pathIndex, nodeIndex), None
	for pathIndex, path in enumerate(layer.paths):
		for nodeIndex, node in enumerate(path.nodes):
			if node.position.x == anchor.position.x:
				return (pathIndex, nodeIndex), anchor.position.y
	return None


def averageAnchorPosition(relativePositions, width):
	averageX = sum(position[0] for position in relativePositions) / len(relativePositions)
	averageY = sum(position[1] for position in relativePositions) / len(relativePositions)
	return NSPoint(averageX * max(1, width), averageY)


def syncAnchors(glyph, sourceLayer):
	"""
	Adds anchors to every key layer that are missing there but present in other layers of the glyph.
	Position: on the same node (or at the same x of the same node) as in the first layer with that anchor
	where it sits on the outline; otherwise at the average relative position of the anchor in all layers.
	"""
	layers = keyLayersOf(glyph)

	relativePositionsByName = {}
	outlinePositionsByName = {}
	for layer in layers:
		for anchor in layer.anchors:
			relativePositionsByName.setdefault(anchor.name, []).append((anchor.x / max(1, layer.width), anchor.y))
			if anchor.name not in outlinePositionsByName:
				outlinePosition = anchorPositionsOnOutline(layer, anchor)
				if outlinePosition is not None:
					outlinePositionsByName[anchor.name] = outlinePosition

	addedCount = 0
	for layer in layers:
		existingNames = [anchor.name for anchor in layer.anchors]
		missingNames = [name for name in relativePositionsByName if name not in existingNames]
		for anchorName in missingNames:
			position = None
			if anchorName in outlinePositionsByName:
				(pathIndex, nodeIndex), prescribedY = outlinePositionsByName[anchorName]
				if pathIndex < len(layer.paths) and nodeIndex < len(layer.paths[pathIndex].nodes):
					node = layer.paths[pathIndex].nodes[nodeIndex]
					position = node.position if prescribedY is None else NSPoint(node.position.x, prescribedY)
			if position is None:
				position = averageAnchorPosition(relativePositionsByName[anchorName], layer.width)
			layer.anchors.append(newAnchorWithName(anchorName, position))
			print(f"\t✅ Layer ‘{layer.name}’: added anchor {anchorName}")
			addedCount += 1
	return addedCount


class CompatibilityManager(mekkaObject):
	prefDict = {
		"startPointOptions": 9,
		"shapeOrderOptions": 2,
	}

	def __init__(self):
		windowWidth = 1  # Auto Layout grows the window to the width the content needs
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Compatibility Manager",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements, start points and shape order:
		inset = 15

		self.w.startPointTitle = vanilla.TextBox("auto", "Start Point Selection", sizeStyle="small")
		self.w.startPointOptions = vanilla.PopUpButton(
			"auto",
			[
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
			],
			callback=self.SavePreferences,
		)

		self.w.shapeOrderTitle = vanilla.TextBox("auto", "Shape Order", sizeStyle="small")
		self.w.shapeOrderOptions = vanilla.PopUpButton(
			"auto",
			[
				"By relative center",
				"By size",
				"By shortest travel",
			],
			callback=self.SavePreferences,
		)

		self.w.resetStartPoints = vanilla.Button("auto", "Reset Start Points", callback=self.resetStartPoints)
		self.w.reorderShapes = vanilla.Button("auto", "Reorder Shapes", callback=self.reorderShapes)

		# title of the collapsible lower part, set like the other titles, but clickable:
		self.w.extraTitle = vanilla.Button("auto", "", callback=self.toggleExtraOptions, sizeStyle="small")
		self.w.extraTitle.setToolTip("Show or hide the extra options.")
		nsExtraTitle = self.w.extraTitle.getNSButton()
		nsExtraTitle.setBordered_(False)
		nsExtraTitle.setAlignment_(NSTextAlignmentLeft)

		# UI elements, one row per function: description on the left, run button on the right.
		# Grouped in this order: sync, realign, remove, backup.
		enhanceRows = (
			(
				"syncTypes", "Sync on/off node types (esp. for TT):", "Sync", self.syncNodeTypes,
				"Propagates the node types (oncurve vs. offcurve) of the current layer of each selected glyph to the other compatible layers. Useful in TT paths."
			),
			(
				"syncConnections", "Sync smooth/corner connections:", "Sync", self.syncNodeConnections,
				"Propagates the node connections (green vs. blue) of the current layer of each selected glyph to the other compatible layers. Usually just cosmetic."
			),
			(
				"syncAnchors", "Sync all anchors:", "Sync", self.syncAllAnchors,
				"In all masters and special layers of selected glyphs, adds the anchors that are missing there but present in other layers. Anchors on a node follow that node, all others are placed at the average relative position."
			),
			(
				"realign", "Realign smooth connections (prefer orthogonals):", "Realign", self.realignConnections,
				"Realigns handles (BCPs) next to a smooth connection (green node) in all masters and special layers of selected glyphs. Or, if applicable, moves smooth oncurves (green nodes) onto the line between their surrounding handles."
			),
			(
				"removeEmpty", "Remove empty paths:", "Remove", self.removeEmptyPathsInSelection,
				"Sometimes an invisible empty path (a path with no nodes) is blocking compatibility. This removes those empty paths in all masters and special layers of selected glyphs."
			),
			(
				"removeStray", "Remove stray points (single-node paths):", "Remove", self.removeStrayPointsInSelection,
				"Removes paths consisting of a single node in all masters and special layers of selected glyphs."
			),
			(
				"backup", "Backup layers in background:", "Backup", self.backupSelectedLayers,
				"Makes a backup of all masters and special layers of selected glyphs in their respective backgrounds. Careful: will overwrite existing layer backgrounds."
			),
		)
		for name, labelText, buttonTitle, callback, tooltipText in enhanceRows:
			label = vanilla.TextBox("auto", labelText, sizeStyle="small", selectable=True)
			button = vanilla.Button("auto", buttonTitle, callback=callback, sizeStyle="small")
			label.setToolTip(tooltipText)
			button.setToolTip(tooltipText)
			setattr(self.w, f"{name}Text", label)
			setattr(self.w, f"{name}Button", button)

			# labels: right-aligned, same width, hugging their text
			nsLabel = label.getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes and square buttons stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		rowNames = [row[0] for row in enhanceRows]
		widestLabel = "realignText"  # the label with the longest text
		widestButton = "realignButton"  # the button with the longest title

		def equalWidth(viewName, referenceName):
			return {"view1": getattr(self.w, viewName), "attribute1": "width", "view2": getattr(self.w, referenceName), "attribute2": "width"}

		def centerY(viewName, referenceName):
			return {"view1": getattr(self.w, viewName), "attribute1": "centerY", "view2": getattr(self.w, referenceName), "attribute2": "centerY"}

		metrics = {"inset": inset, "gap": 8, "row": 6, "titleGap": 2}
		rules = [
			"H:|-inset-[startPointTitle]-gap-[shapeOrderTitle]-inset-|",
			"H:|-inset-[startPointOptions]-gap-[shapeOrderOptions]-inset-|",
			"H:|-inset-[resetStartPoints]-gap-[reorderShapes]-inset-|",
			"H:|-inset-[extraTitle]-(>=inset)-|",
		]
		# the label ends a fixed gap before its button, so it sits close to it
		rules += [f"H:|-inset-[{name}Text]-gap-[{name}Button(>=80)]-inset-|" for name in rowNames]
		rules += [
			centerY("shapeOrderTitle", "startPointTitle"),
			centerY("shapeOrderOptions", "startPointOptions"),
			centerY("reorderShapes", "resetStartPoints"),
			equalWidth("shapeOrderTitle", "startPointTitle"),
			equalWidth("shapeOrderOptions", "startPointOptions"),
			equalWidth("reorderShapes", "resetStartPoints"),
		]
		rules += [centerY(f"{name}Text", f"{name}Button") for name in rowNames]
		rules += [equalWidth(f"{name}Text", widestLabel) for name in rowNames if f"{name}Text" != widestLabel]
		rules += [equalWidth(f"{name}Button", widestButton) for name in rowNames if f"{name}Button" != widestButton]
		self.w.addAutoPosSizeRules(rules, metrics=metrics)

		# The vertical chain comes in two variants, so the lower part can be collapsed.
		# Built with AppKit constraints directly, because they get switched on and off:
		self.extraRowNames = rowNames
		viewNames = ["startPointTitle", "startPointOptions", "resetStartPoints", "extraTitle"] + [f"{name}Button" for name in rowNames]
		views = {viewName: getattr(self.w, viewName).getNSView() for viewName in viewNames}
		upperChain = "V:|-gap-[startPointTitle]-titleGap-[startPointOptions]-row-[resetStartPoints]-inset-[extraTitle]"
		buttonChain = "-row-".join(f"[{name}Button]" for name in rowNames)
		self.expandedConstraints = NSLayoutConstraint.constraintsWithVisualFormat_options_metrics_views_(
			f"{upperChain}-row-{buttonChain}-inset-|",
			0,
			metrics,
			views,
		)
		# collapsed: the (hidden) buttons are parked on the title, so they take no space
		self.collapsedConstraints = list(NSLayoutConstraint.constraintsWithVisualFormat_options_metrics_views_(
			f"{upperChain}-inset-|",
			0,
			metrics,
			views,
		))
		for name in rowNames:
			self.collapsedConstraints.append(
				NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
					views[f"{name}Button"],
					NSLayoutAttributeCenterY,
					NSLayoutRelationEqual,
					views["extraTitle"],
					NSLayoutAttributeCenterY,
					1.0,
					0.0,
				)
			)
		expanded = Glyphs.defaults[self.domain("extraOptionsExpanded")]
		self.setExtraOptionsExpanded(True if expanded is None else bool(expanded), resizeWindow=False)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def setExtraOptionsExpanded(self, expanded, resizeWindow=True):
		Glyphs.defaults[self.domain("extraOptionsExpanded")] = expanded
		self.w.extraTitle.setTitle(("▼" if expanded else "▶\uFE0E") + " Extra options")
		if expanded:
			NSLayoutConstraint.deactivateConstraints_(self.collapsedConstraints)
			NSLayoutConstraint.activateConstraints_(self.expandedConstraints)
		else:
			NSLayoutConstraint.deactivateConstraints_(self.expandedConstraints)
			NSLayoutConstraint.activateConstraints_(self.collapsedConstraints)
		for name in self.extraRowNames:
			getattr(self.w, f"{name}Text").show(expanded)
			getattr(self.w, f"{name}Button").show(expanded)
		self.extraOptionsExpanded = expanded

		if resizeWindow:
			# fit the window height to the content again, keep the width
			window = self.w.getNSWindow()
			window.layoutIfNeeded()
			fittingHeight = window.contentView().fittingSize().height
			if fittingHeight > 50:
				self.w.resize(self.w.getPosSize()[2], fittingHeight)

	def toggleExtraOptions(self, sender=None):
		self.setExtraOptionsExpanded(not self.extraOptionsExpanded)

	def processSelectedGlyphs(self, title, function, unit):
		"""Calls function(glyph, sourceLayer) for each selected glyph; the function reports and returns a count."""
		font = Glyphs.font
		if font is None or not font.selectedLayers:
			Message(title=title, message="Select at least one glyph in a font and try again.", OKButton=None)
			return

		Glyphs.clearLog()
		print(f"{title}, Report for {reportFontName(font)}\n")

		totalCount = 0
		font.disableUpdateInterface()  # suppresses UI updates in Font View
		try:
			for sourceLayer in selectedSourceLayers(font):
				glyph = sourceLayer.parent
				print(f"🔤 {glyph.name}")
				totalCount += function(glyph, sourceLayer)
		except Exception as e:
			Glyphs.showMacroWindow()
			print(f"\n❌ Error: {e}\n")
			import traceback
			print(traceback.format_exc())
		finally:
			font.enableUpdateInterface()

		self.updateViews()
		if font.currentTab:
			font.currentTab.reflow()
		print(f"\n✅ Done: {totalCount} {unit}.")
		Glyphs.showNotification(title, f"{totalCount} {unit}. Details in Macro Window.")

	def syncNodeTypes(self, sender=None):

		def syncTypes(glyph, sourceLayer):
			return syncNodeAttribute(glyph, sourceLayer, "type")

		self.processSelectedGlyphs("Sync Node Types", syncTypes, "nodes changed")

	def syncNodeConnections(self, sender=None):

		def syncConnections(glyph, sourceLayer):
			return syncNodeAttribute(glyph, sourceLayer, "connection")

		self.processSelectedGlyphs("Sync Node Connections", syncConnections, "nodes changed")

	def syncAllAnchors(self, sender=None):
		self.processSelectedGlyphs("Sync All Anchors", syncAnchors, "anchors added")

	def realignConnections(self, sender=None):
		self.processSelectedGlyphs("Realign Smooth Connections", realignSmoothConnections, "nodes realigned")

	def removeEmptyPathsInSelection(self, sender=None):
		self.processSelectedGlyphs("Remove Empty Paths", removeEmptyPaths, "paths removed")

	def removeStrayPointsInSelection(self, sender=None):
		self.processSelectedGlyphs("Remove Stray Points", removeStrayPoints, "paths removed")

	def backupSelectedLayers(self, sender=None):
		self.processSelectedGlyphs("Backup Layers", backupLayers, "layers backed up")

	def updateViews(self, sender=None):
		for font in Glyphs.fonts:
			if font.currentTab:
				if Glyphs.versionNumber >= 4.0:
					font.currentTab.redraw()
				else:
					font.currentTab.forceRedraw()
				font.currentTab.graphicView().redraw()
				font.currentTab.previewView().update()
			font.fontView.redraw()

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
				for i, shape in enumerate(layer.shapes):
					if not isinstance(shape, GSPath):
						continue
					self.findOptimalStartPoint(layer, i, startPointOption)

			self.updateCompatibility(glyph)
		
		self.updateViews()
		if font.currentTab:
			font.currentTab.reflow()

	def findOptimalStartPoint(self, layer, pathIndex, startPointOption):
		path = layer.shapes[pathIndex]
		originalPath = path.copy()
		originalStart = path.startNode()
		bestStart = originalStart
		maxValue = None
		compatibleStarts = []

		for i, node in enumerate(originalPath.nodes):
			if node.type != OFFCURVE:
				layer.shapes[pathIndex].makeNodeFirst_(layer.shapes[pathIndex].nodes[i])
				if self.checkLayerCompatibility(layer):
					compatibleStarts.append(i)
				layer.shapes[pathIndex] = originalPath.copy()

		if compatibleStarts:
			for startIndex in compatibleStarts:
				startNode = layer.shapes[pathIndex].nodes[startIndex]
				value = self.calculateStartPointValue(startNode, startPointOption)
				if value is None:
					continue

				if maxValue is None or value > maxValue:
					maxValue = value
					bestStartIndex = startIndex
			
			layer.shapes[pathIndex].makeNodeFirst_(layer.shapes[pathIndex].nodes[bestStartIndex])
		else:
			layer.shapes[pathIndex] = originalPath
		
		self.updateViews()

	def calculateStartPointValue(self, node, option):
		if option == 0:
			# 0: Closest to origin
			return -math.hypot(node.x, node.y)

		elif option in (1, 2, 3, 4):
			# 1: Top, then left
			# 2: Top, then right
			# 3: Bottom, then left
			# 4: Bottom, then right
			primary = node.y if option in (1, 2) else -node.y
			secondary = node.x if option in (2, 4) else -node.x
			return primary * 1000000 + secondary

		else: # 5, 6, 7, 8
			# 5: Left, then top
			# 6: Left, then bottom
			# 7: Right, then top
			# 8: Right, then bottom
			primary = node.x if option in (7, 8) else -node.x
			secondary = node.y if option in (5, 7) else -node.y
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
		if font.currentTab:
			font.currentTab.reflow()

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

		# glyph.updateGlyphInfo()


CompatibilityManager()
