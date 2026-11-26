# MenuTitle: Dot Maker
__doc__ = """
Draws the Arabic dot marks (one, two and three dots, above, below and centered) as circles, squares or diamonds, with _top, _bottom and _center anchors. With live preview.
"""

import math
import vanilla
from mekkablue import mekkaObject, newGlyphWithName, newAnchorWithName, SteppingEditText, integerFormatter, decimalFormatter, fontFileName, makeWindowResizable
from mekkablue.geometry import italicize
from GlyphsApp import Glyphs, GSPath, GSNode, GSLINE, GSCURVE, GSOFFCURVE, GSMetricsTypexHeight, Message
from AppKit import (
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSLineBreakByTruncatingTail,
	NSTextAlignmentRight,
)
from Foundation import NSPoint

# glyph name, arrangement of the dots, position relative to the metrics:
dotGlyphs = (
	("dotabove-ar", "single", "above"),
	("dotbelow-ar", "single", "below"),
	("dotcenter-ar", "single", "center"),
	("twodotsverticalabove-ar", "twoVertical", "above"),
	("twodotsverticalbelow-ar", "twoVertical", "below"),
	("twodotshorizontalabove-ar", "twoHorizontal", "above"),
	("twodotshorizontalbelow-ar", "twoHorizontal", "below"),
	("threedotsdownabove-ar", "threeDown", "above"),
	("threedotsdownbelow-ar", "threeDown", "below"),
	("threedotsdowncenter-ar", "threeDown", "center"),
	("threedotsupabove-ar", "threeUp", "above"),
	("threedotsupbelow-ar", "threeUp", "below"),
)
anchorNames = {"above": "_top", "below": "_bottom", "center": "_center"}
stackAnchorNames = {"above": "top", "below": "bottom"}  # for the next mark; the centered ones have none

scopeChoices = (
	"Current font, current master",
	"Current font, all masters",
	"All fonts, current master",
	"All fonts, all masters",
)


# ------------------------------------------------------------------------------
# Geometry. Pure functions, no Glyphs involved. A contour is a closed list of
# (x, y, isOffcurve) tuples. Dots are built around (0, 0) and placed later.
# ------------------------------------------------------------------------------

def circleContour(size, curvature):
	"""Counterclockwise circle with four nodes. The handles are curvature percent of the radius long."""
	radius = size / 2.0
	handle = radius * curvature / 100.0
	return [
		(radius, 0, False), (radius, handle, True), (handle, radius, True),
		(0, radius, False), (-handle, radius, True), (-radius, handle, True),
		(-radius, 0, False), (-radius, -handle, True), (-handle, -radius, True),
		(0, -radius, False), (handle, -radius, True), (radius, -handle, True),
	]


def roundedCorner(vertex, previous, following, radius, curvature):
	"""
	Contour points for one corner of a polygon that is traversed previous > vertex > following.
	With a radius the corner is cut by a curve, whose handles are curvature percent of the way from its ends to the vertex.
	The radius is the one of a circular arc; it shrinks where the adjacent edges are too short for it.
	"""
	vertexX, vertexY = vertex
	lengthA = math.hypot(previous[0] - vertexX, previous[1] - vertexY)
	lengthB = math.hypot(following[0] - vertexX, following[1] - vertexY)
	if radius <= 0 or lengthA == 0 or lengthB == 0:
		return [(vertexX, vertexY, False)]
	directionAX, directionAY = (previous[0] - vertexX) / lengthA, (previous[1] - vertexY) / lengthA
	directionBX, directionBY = (following[0] - vertexX) / lengthB, (following[1] - vertexY) / lengthB
	angle = math.acos(max(-1.0, min(1.0, directionAX * directionBX + directionAY * directionBY)))  # interior angle
	if angle < 1e-6 or abs(angle - math.pi) < 1e-6:
		return [(vertexX, vertexY, False)]
	tangent = min(radius / math.tan(angle / 2.0), lengthA / 2.0, lengthB / 2.0)
	startX, startY = vertexX + directionAX * tangent, vertexY + directionAY * tangent
	endX, endY = vertexX + directionBX * tangent, vertexY + directionBY * tangent
	factor = curvature / 100.0
	return [
		(startX, startY, False),
		(startX + (vertexX - startX) * factor, startY + (vertexY - startY) * factor, True),
		(endX + (vertexX - endX) * factor, endY + (vertexY - endY) * factor, True),
		(endX, endY, False),
	]


def roundedPolygon(vertices, radius, curvature):
	contour = []
	count = len(vertices)
	for index, vertex in enumerate(vertices):
		contour += roundedCorner(vertex, vertices[index - 1], vertices[(index + 1) % count], radius, curvature)
	return contour


def dotContour(shape, size, settings, scale):
	"""Contour of one dot of that size around (0, 0). The bounding box of every shape is size × size."""
	if shape == 0:
		return circleContour(size, settings["curvature"])
	half = size / 2.0
	radius = settings["radius"] * scale  # smaller dots get proportionally smaller corners
	if shape == 1:
		vertices = ((-half, -half), (half, -half), (half, half), (-half, half))
	else:
		# sheared diamond; up to 45° the bounding box stays the same
		shear = math.tan(math.radians(settings["slant"]))
		vertices = ((-half * shear, -half), (half, 0), (half * shear, half), (-half, 0))
	return roundedPolygon(vertices, radius, settings["cornerCurvature"])


def dotContours(settings, scale, template):
	"""Returns (contours, width, height) of one dot around (0, 0), width and height of its bounding box."""
	if template is not None:
		# custom: the outlines of dotabove-ar, resized with the Size field and the compensation
		factor = template["factor"] * scale
		contours = [[(x * factor, y * factor, isOffcurve, smooth) for x, y, isOffcurve, smooth in contour] for contour in template["contours"]]
		return contours, template["width"] * factor, template["height"] * factor
	size = max(1, int(round(settings["size"] * scale)))
	return [dotContour(settings["shape"], size, settings, scale)], size, size


def dotCenters(arrangement, width, height, horizontalGap, verticalGap, twoDotsOffset=0, threeDotsOffset=0):
	"""
	Centers of the dots around (0, 0). The gaps are between the edges of the bounding boxes.
	The offsets move the top row horizontally against the bottom row, negative to the left.
	"""
	column = (width + horizontalGap) / 2.0
	row = (height + verticalGap) / 2.0
	if arrangement == "single":
		return [(0, 0)]
	if arrangement == "twoVertical":
		return [(0, -row), (twoDotsOffset, row)]
	if arrangement == "twoHorizontal":
		return [(-column, 0), (column, 0)]
	if arrangement == "threeDown":  # two on top, one below
		return [(-column + threeDotsOffset, row), (column + threeDotsOffset, row), (0, -row)]
	return [(-column, -row), (column, -row), (threeDotsOffset, row)]  # threeUp: one on top, two below


def removeDuplicates(contour):
	"""Drops on-curve points that sit exactly on the on-curve point before them, e.g. where two rounded corners meet."""
	result = []
	for point in contour:
		if result and not point[2] and not result[-1][2] and point[:2] == result[-1][:2]:
			continue
		result.append(point)
	while len(result) > 1 and not result[0][2] and not result[-1][2] and result[0][:2] == result[-1][:2]:
		result.pop()
	return result


def placedContours(arrangement, position, xHeight, settings, template=None):
	"""All contours of a glyph, in integer coordinates. The dots are centered on x = 0. The template holds the custom dot."""
	scale = 1.0 if arrangement == "single" else settings["compensation"] / 100.0
	dot, width, height = dotContours(settings, scale, template)
	centers = dotCenters(arrangement, width, height, settings["horizontalGap"], settings["verticalGap"], settings["twoDotsOffset"], settings["threeDotsOffset"])
	lowest = min(centerY for centerX, centerY in centers) - height / 2.0
	highest = max(centerY for centerX, centerY in centers) + height / 2.0
	if position == "above":
		shiftY = xHeight + settings["distance"] - lowest
	elif position == "below":
		shiftY = -settings["distance"] - highest
	else:
		shiftY = xHeight / 2.0 - (lowest + highest) / 2.0
	contours = []
	for centerX, centerY in centers:
		for contour in dot:
			rounded = [(int(round(point[0] + centerX)), int(round(point[1] + centerY + shiftY)), point[2]) + tuple(point[3:]) for point in contour]
			contours.append(removeDuplicates(rounded))
	return contours


# ------------------------------------------------------------------------------
# Glyphs helpers
# ------------------------------------------------------------------------------

def metricPosition(font, master, metricType):
	"""Returns the position of the (unfiltered) metric of that type in the master, or None."""
	for metric in font.metrics:
		if metric.type == metricType and metric.filter is None:
			return master.metrics[metric.id].position
	return None


def layerFingerprint(layer):
	"""All node positions and types of the layer, to tell whether somebody edited it since the script drew it."""
	return tuple((int(round(node.position.x)), int(round(node.position.y)), node.type) for path in layer.paths for node in path.nodes)


def templateFromLayer(layer):
	"""The closed contours of the layer, centered on the middle of their bounding box, as a custom dot. None without outlines."""
	contours = [path for path in layer.paths if path.closed and len(path.nodes) > 2]
	if not contours:
		return None
	bounds = layer.bounds
	centerX = bounds.origin.x + bounds.size.width / 2.0
	centerY = bounds.origin.y + bounds.size.height / 2.0
	return {
		"contours": [[(node.position.x - centerX, node.position.y - centerY, node.type == GSOFFCURVE, bool(node.smooth)) for node in path.nodes] for path in contours],
		"width": bounds.size.width,
		"height": bounds.size.height,
	}


def pathFromContour(contour):
	"""
	A closed GSPath. An on-curve node is a curve node if it follows a handle, and smooth if handles are on both sides.
	Points of custom dots carry their own smooth flag as the fourth value.
	"""
	path = GSPath()
	count = len(contour)
	for index, point in enumerate(contour):
		x, y, isOffcurve = point[:3]
		previousIsOffcurve = contour[index - 1][2]
		nextIsOffcurve = contour[(index + 1) % count][2]
		if isOffcurve:
			nodeType = GSOFFCURVE
		else:
			nodeType = GSCURVE if previousIsOffcurve else GSLINE
		node = GSNode(NSPoint(x, y), type=nodeType)
		smooth = point[3] if len(point) > 3 else (previousIsOffcurve and nextIsOffcurve)
		if not isOffcurve and smooth:
			node.smooth = True
		path.nodes.append(node)
	path.closed = True
	return path


class DotMaker(mekkaObject):
	prefDict = {
		"shape": 0,
		"size": 100,
		"compensation": 90,
		"curvature": 58,
		"slant": 0,
		"radius": 0,
		"cornerCurvature": 58,
		"distance": 40,
		"verticalGap": 20,
		"horizontalGap": 30,
		"twoDotsOffset": 0,
		"threeDotsOffset": 0,
		"scope": 0,
		"backup": True,
	}

	def __init__(self):
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Dot Maker",
			autosaveName=self.domain("mainwindow"),  # stores last window position and width
		)
		self.backedUp = set()  # layers whose previous outlines we already looked at in this session
		self.templates = {}  # custom dots by layer ID of dotabove-ar
		self.fingerprints = {}  # what dotabove-ar looked like by layer ID when this script last drew it
		self.references = {}  # size of the custom dot that the Size field belongs to, by font (ID of its first master)

		self.w.descriptionText = vanilla.TextBox(
			"auto",
			"Draws the 12 Arabic dot marks with the shape and measurements below. Changes show live in the font.",
			sizeStyle="small",
			selectable=True,
		)

		tooltipText = "Shape of a single dot. Custom takes the outlines of dotabove-ar, which you draw yourself."
		self.w.shapeLabel = vanilla.TextBox("auto", "Shape", sizeStyle="small")
		self.w.shapeLabel.setToolTip(tooltipText)
		self.w.shape = vanilla.PopUpButton("auto", ("Circle", "Square", "Diamond", "Custom"), callback=self.SavePreferences, sizeStyle="small")
		self.w.shape.setToolTip(tooltipText)
		self.w.customButton = vanilla.Button("auto", "Open dotabove", callback=self.openDotabove, sizeStyle="small")
		self.w.customButton.setToolTip("Custom shape: opens dotabove-ar in a tab, so you can draw your own dot. Its outlines become the dot for all 12 glyphs, and the Size field takes its size (the larger of width and height). Resizing then scales your dot. The glyphs update when you come back to this window.")

		tooltipText = "Width and height of the bounding box of a single dot, in units. Use the arrow keys to step. With a custom shape, the larger of its width and height; the field takes the size of your dot when you edit it, and changing it scales your dot."
		self.w.sizeLabel = vanilla.TextBox("auto", "Size", sizeStyle="small")
		self.w.sizeLabel.setToolTip(tooltipText)
		self.w.size = SteppingEditText("auto", "100", formatter=integerFormatter(1, 999), callback=self.SavePreferences, sizeStyle="small")
		self.w.size.setToolTip(tooltipText)
		self.w.sizeText = vanilla.TextBox("auto", "units, bounding box of one dot", sizeStyle="small")

		tooltipText = "Size of the dots in the marks with two or three dots, in percent of the size above. The corner radius shrinks along; the gaps stay as they are."
		self.w.compensationLabel = vanilla.TextBox("auto", "Compensation", sizeStyle="small")
		self.w.compensationLabel.setToolTip(tooltipText)
		self.w.compensation = SteppingEditText("auto", "90", formatter=integerFormatter(10, 200), callback=self.SavePreferences, sizeStyle="small")
		self.w.compensation.setToolTip(tooltipText)
		self.w.compensationText = vanilla.TextBox("auto", "% size for two and three dots", sizeStyle="small")

		tooltipText = "Circle: length of the handles in percent of the radius. 55 is a round circle; more makes it squarer, less more pointed."
		self.w.fineTuneLabel = vanilla.TextBox("auto", "Fine tune", sizeStyle="small")
		self.w.fineTuneLabel.setToolTip(tooltipText)
		self.w.curvature = SteppingEditText("auto", "58", formatter=decimalFormatter(1, 100), callback=self.SavePreferences, sizeStyle="small")
		self.w.curvature.setToolTip(tooltipText)
		self.w.curvatureText = vanilla.TextBox("auto", "% curvature of the circle", sizeStyle="small")

		self.w.slant = SteppingEditText("auto", "0", formatter=decimalFormatter(-45, 45), callback=self.SavePreferences, sizeStyle="small")
		self.w.slant.setToolTip("Diamond: shears the diamond horizontally by this angle, from -45° to 45°. Positive leans to the right. The bounding box keeps its size.")
		self.w.slantText = vanilla.TextBox("auto", "° slant of the diamond", sizeStyle="small")

		self.w.radius = SteppingEditText("auto", "0", formatter=integerFormatter(0, 500), callback=self.SavePreferences, sizeStyle="small")
		self.w.radius.setToolTip("Square and diamond: radius of the rounded corners, in units. 0 keeps the corners sharp. Where the sides are too short for the radius, it shrinks.")
		self.w.radiusText = vanilla.TextBox("auto", "units radius of rounded corners", sizeStyle="small")

		self.w.cornerCurvature = SteppingEditText("auto", "58", formatter=decimalFormatter(1, 100), callback=self.SavePreferences, sizeStyle="small")
		self.w.cornerCurvature.setToolTip("Square and diamond: curvature of the rounded corners, in percent. The handles are this part of the way from the ends of the curve to the corner. 55 is a circular arc in a right angle; 100 is the sharpest, 1 the roundest.")
		self.w.cornerCurvatureText = vanilla.TextBox("auto", "% curvature of rounded corners", sizeStyle="small")

		tooltipText = "Distance from the baseline (marks below) or from the x-height (marks above) to the nearest edge of the dots, in units. The _bottom anchor sits on the baseline, the _top anchor on the x-height. The top and bottom anchors for stacking another mark sit the same distance beyond the dots, on the italic angle through _top or _bottom. Centered marks sit in the middle of the x-height and get a _center anchor."
		self.w.distanceLabel = vanilla.TextBox("auto", "Distance", sizeStyle="small")
		self.w.distanceLabel.setToolTip(tooltipText)
		self.w.distance = SteppingEditText("auto", "40", formatter=integerFormatter(0, 999), callback=self.SavePreferences, sizeStyle="small")
		self.w.distance.setToolTip(tooltipText)
		self.w.distanceText = vanilla.TextBox("auto", "units from baseline or x-height", sizeStyle="small")

		tooltipText = "Space between the dots, from edge to edge, in units (negative values overlap the dots): vertical between two stacked dots and between the rows of three dots, horizontal between two dots next to each other."
		self.w.gapsLabel = vanilla.TextBox("auto", "Gaps", sizeStyle="small")
		self.w.gapsLabel.setToolTip(tooltipText)
		self.w.verticalGap = SteppingEditText("auto", "20", formatter=integerFormatter(-999, 999), callback=self.SavePreferences, sizeStyle="small")
		self.w.verticalGap.setToolTip("Vertical space between the dots, edge to edge, in units: between two stacked dots and between the rows of three dots.")
		self.w.verticalGapText = vanilla.TextBox("auto", "vertical", sizeStyle="small")
		self.w.horizontalGap = SteppingEditText("auto", "30", formatter=integerFormatter(-999, 999), callback=self.SavePreferences, sizeStyle="small")
		self.w.horizontalGap.setToolTip("Horizontal space between the dots, edge to edge, in units: between two dots next to each other.")
		self.w.horizontalGapText = vanilla.TextBox("auto", "horizontal", sizeStyle="small")

		tooltipText = "Horizontal offset of the top row against the bottom row, in units. Negative moves the top row to the left, e.g. -5 moves it 5 units left of where it would be centered."
		self.w.offsetLabel = vanilla.TextBox("auto", "Offset", sizeStyle="small")
		self.w.offsetLabel.setToolTip(tooltipText)
		self.w.twoDotsOffset = SteppingEditText("auto", "0", formatter=integerFormatter(-999, 999), callback=self.SavePreferences, sizeStyle="small")
		self.w.twoDotsOffset.setToolTip("Two dots stacked vertically: moves the top dot horizontally against the bottom dot, in units. Negative moves it to the left.")
		self.w.twoDotsOffsetText = vanilla.TextBox("auto", "two dots", sizeStyle="small")
		self.w.threeDotsOffset = SteppingEditText("auto", "0", formatter=integerFormatter(-999, 999), callback=self.SavePreferences, sizeStyle="small")
		self.w.threeDotsOffset.setToolTip("Three dots: moves the top row (the single dot, or the two dots) horizontally against the bottom row, in units. Negative moves it to the left.")
		self.w.threeDotsOffsetText = vanilla.TextBox("auto", "three dots", sizeStyle="small")

		tooltipText = "Where the dots are drawn. All masters of a font are drawn together, so they stay compatible; each master gets its own x-height."
		self.w.scopeLabel = vanilla.TextBox("auto", "Scope", sizeStyle="small")
		self.w.scopeLabel.setToolTip(tooltipText)
		self.w.scope = vanilla.PopUpButton("auto", scopeChoices, callback=self.SavePreferences, sizeStyle="small")
		self.w.scope.setToolTip(tooltipText)
		self.w.backup = vanilla.CheckBox("auto", "Backup in background", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.backup.setToolTip("Before the first redraw in this session, copies existing outlines of the dot glyphs into the background, unless the background holds something already.")

		self.w.status = vanilla.TextBox("auto", "🤖 Ready. 💬 See tooltips for help.", sizeStyle="small")
		self.w.status.setToolTip("Reports what the script is doing, and how it ended.")
		self.w.redrawButton = vanilla.Button("auto", "Redraw", callback=self.redraw)
		self.w.redrawButton.setToolTip("Forces a redraw of all dot glyphs with the current values. With a custom shape, it takes your changes of dotabove-ar first.")
		self.w.tabButton = vanilla.Button("auto", "Open Tab", callback=self.openTab)
		self.w.tabButton.setToolTip("Opens a new Edit tab with the dot glyphs.")
		self.w.setDefaultButton(self.w.tabButton)

		# secondary info text takes a semantic color, and shortens instead of widening the window:
		hintNames = ("sizeText", "compensationText", "curvatureText", "slantText", "radiusText", "cornerCurvatureText", "distanceText")
		for hintName in hintNames:
			nsHint = getattr(self.w, hintName).getNSTextField()
			nsHint.setTextColor_(NSColor.tertiaryLabelColor())
			nsHint.setLineBreakMode_(NSLineBreakByTruncatingTail)
			nsHint.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		# the status line shortens instead of widening the window:
		self.w.status.getNSTextField().setLineBreakMode_(NSLineBreakByTruncatingTail)
		self.w.status.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.shape.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.customButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.customButton.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		self.w.redrawButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.redrawButton.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		self.w.tabButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.tabButton.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		# the description wraps: it takes the width it is given instead of demanding one long line
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# the labels end at one x-position:
		labelNames = ("shapeLabel", "sizeLabel", "compensationLabel", "fineTuneLabel", "distanceLabel", "gapsLabel", "offsetLabel", "scopeLabel")
		widestLabel = "compensationLabel"
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		for labelName in ("verticalGapText", "horizontalGapText", "twoDotsOffsetText", "threeDotsOffsetText"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes and buttons stretch vertically by default; hugging makes the window as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		def aligned(viewName, otherName, attribute):
			return {"view1": getattr(self.w, viewName), "attribute1": attribute, "view2": getattr(self.w, otherName), "attribute2": attribute}

		rules = [
			"H:|-inset-[descriptionText]-inset-|",
			"H:|-inset-[shapeLabel]-gap-[shape]-gap-[customButton]-inset-|",
			"H:|-inset-[sizeLabel]-gap-[size(fieldWidth)]-gap-[sizeText]-(>=inset)-|",
			"H:|-inset-[compensationLabel]-gap-[compensation(fieldWidth)]-gap-[compensationText]-(>=inset)-|",
			"H:|-inset-[fineTuneLabel]-gap-[curvature(fieldWidth)]-gap-[curvatureText]-(>=inset)-|",
			"H:[slant(fieldWidth)]-gap-[slantText]-(>=inset)-|",
			"H:[radius(fieldWidth)]-gap-[radiusText]-(>=inset)-|",
			"H:[cornerCurvature(fieldWidth)]-gap-[cornerCurvatureText]-(>=inset)-|",
			"H:|-inset-[distanceLabel]-gap-[distance(fieldWidth)]-gap-[distanceText]-(>=inset)-|",
			"H:|-inset-[gapsLabel]-gap-[verticalGap(fieldWidth)]-tight-[verticalGapText]-pair-[horizontalGap(fieldWidth)]-tight-[horizontalGapText]-(>=inset)-|",
			"H:|-inset-[offsetLabel]-gap-[twoDotsOffset(fieldWidth)]-tight-[twoDotsOffsetText]-pair-[threeDotsOffset(fieldWidth)]-tight-[threeDotsOffsetText]-(>=inset)-|",
			"H:|-inset-[scopeLabel]-gap-[scope]-inset-|",
			"H:[backup]-(>=inset)-|",
			"H:|-inset-[status]-gap-[redrawButton(>=70)]-gap-[tabButton(>=70)]-inset-|",
			(
				"V:|-inset-[descriptionText(42)]-section-[shape]-row-[size]-row-[compensation]-section-[curvature]-row-[slant]-row-[radius]-row-[cornerCurvature]"
				"-section-[distance]-row-[verticalGap]-row-[twoDotsOffset]-section-[scope]-checkRow-[backup]-section-[tabButton]-inset-|"
			),
			# the fine tune fields stand above each other, the backup checkbox under the Scope popup:
			aligned("slant", "curvature", "leading"),
			aligned("radius", "curvature", "leading"),
			aligned("cornerCurvature", "curvature", "leading"),
			aligned("backup", "scope", "leading"),
			# the status line sits on the vertical center of the button:
			aligned("status", "tabButton", "centerY"),
			aligned("redrawButton", "tabButton", "centerY"),
		]
		rules += [aligned(labelName, widestLabel, "width") for labelName in labelNames if labelName != widestLabel]
		# everything in a row sits on the vertical center of its field:
		rowFields = (
			("shape", ("shapeLabel", "customButton")),
			("size", ("sizeLabel", "sizeText")),
			("compensation", ("compensationLabel", "compensationText")),
			("curvature", ("fineTuneLabel", "curvatureText")),
			("slant", ("slantText", )),
			("radius", ("radiusText", )),
			("cornerCurvature", ("cornerCurvatureText", )),
			("distance", ("distanceLabel", "distanceText")),
			("verticalGap", ("gapsLabel", "verticalGapText", "horizontalGap", "horizontalGapText")),
			("twoDotsOffset", ("offsetLabel", "twoDotsOffsetText", "threeDotsOffset", "threeDotsOffsetText")),
			("scope", ("scopeLabel", )),
		)
		for fieldName, otherNames in rowFields:
			for otherName in otherNames:
				rules.append(aligned(otherName, fieldName, "centerY"))
		self.w.addAutoPosSizeRules(rules, metrics={"inset": 15, "gap": 8, "row": 8, "section": 12, "checkRow": 5, "tight": 5, "pair": 10, "fieldWidth": 60})

		# resizable horizontally; the narrowest width at which every row fits is the minimum:
		makeWindowResizable(self.w, fitWidth=True)

		self.w.bind("became key", self.windowBecameKey)  # picks up your edits of a custom dot

		self.LoadPreferences()
		self.updateUI()

		self.draw()  # show the current values right away; the previous outlines go to the background if that option is on
		self.w.open()
		self.w.makeKey()

	# ------------------------------------------------------------------ UI

	def updateUI(self, sender=None):
		shape = self.w.shape.get()
		self.w.curvature.enable(shape == 0)
		self.w.slant.enable(shape == 2)
		self.w.radius.enable(shape in (1, 2))
		self.w.cornerCurvature.enable(shape in (1, 2))
		self.w.customButton.enable(shape == 3)

	def windowBecameKey(self, sender):
		"""With a custom shape, coming back from editing dotabove-ar redraws all glyphs from it."""
		if self.prefInt("shape") == 3:
			self.draw()

	def openDotabove(self, sender):
		font = Glyphs.font
		if not font:
			return
		if font.glyphs["dotabove-ar"] is None:
			self.draw()
		# an existing tab with only this glyph is reused; the tab text holds the character if the glyph has a Unicode value:
		glyph = font.glyphs["dotabove-ar"]
		tabTexts = ["/dotabove-ar"]
		if glyph is not None and glyph.unicode:
			tabTexts.append(chr(int(glyph.unicode, 16)))
		tab = None
		for existingTab in font.tabs:
			if existingTab.text.strip() in tabTexts:
				tab = existingTab
				break
		if tab is None:
			tab = font.newTab("/dotabove-ar")
		else:
			font.currentTab = tab
		tab.textCursor = 0
		font.tool = "SelectTool"  # ready for moving points

	def SavePreferences(self, sender=None):
		super().SavePreferences(sender)
		# live preview:
		self.draw()

	def setStatus(self, text):
		"""Sets the status line and redraws it right away, so it shows while the script is busy."""
		self.w.status.set(text)
		self.w.status.getNSTextField().display()

	def redraw(self, sender):
		self.draw()

	def openTab(self, sender):
		font = Glyphs.font
		if not font:
			return
		font.newTab("".join(f"/{glyphName}" for glyphName, arrangement, position in dotGlyphs))
		font.tool = "TextTool"  # ready for typing

	# ------------------------------------------------------------------ Settings

	def settings(self):
		"""Returns the settings as a dictionary, or None while the fields hold no valid numbers."""
		try:
			settings = {
				"shape": self.prefInt("shape"),
				"size": self.prefFloat("size"),
				"compensation": self.prefFloat("compensation"),
				"curvature": self.prefFloat("curvature"),
				"slant": self.prefFloat("slant"),
				"radius": self.prefFloat("radius"),
				"cornerCurvature": self.prefFloat("cornerCurvature"),
				"distance": self.prefFloat("distance"),
				"verticalGap": self.prefFloat("verticalGap"),
				"horizontalGap": self.prefFloat("horizontalGap"),
				"twoDotsOffset": self.prefFloat("twoDotsOffset"),
				"threeDotsOffset": self.prefFloat("threeDotsOffset"),
				"scope": self.prefInt("scope"),
				"backup": self.prefBool("backup"),
			}
		except (TypeError, ValueError):
			return None
		validRanges = (
			1 <= settings["size"],
			10 <= settings["compensation"] <= 200,
			1 <= settings["curvature"] <= 100,
			-45 <= settings["slant"] <= 45,
			0 <= settings["radius"],
			1 <= settings["cornerCurvature"] <= 100,
			0 <= settings["distance"],
			-999 <= settings["verticalGap"],
			-999 <= settings["horizontalGap"],
			-999 <= settings["twoDotsOffset"] <= 999,
			-999 <= settings["threeDotsOffset"] <= 999,
		)
		if not all(validRanges):
			return None
		return settings

	def targets(self, scope):
		"""Returns (font, master IDs) tuples according to the scope. Master IDs are None for all masters."""
		fonts = list(Glyphs.fonts) if scope in (2, 3) else ([Glyphs.font] if Glyphs.font else [])
		return [(font, None if scope in (1, 3) else {font.selectedFontMaster.id}) for font in fonts]

	# ------------------------------------------------------------------ Drawing

	def backUp(self, glyph, layer):
		"""Once per session, copies the outlines into the background, unless the background holds something already."""
		key = (glyph.name, layer.layerId)
		if key in self.backedUp:
			return
		self.backedUp.add(key)
		if len(layer.shapes) == 0 or len(layer.background.shapes) > 0:
			return
		for shape in layer.shapes:
			layer.background.shapes.append(shape.copy())
		layer.background.decomposeComponents()

	def centerBackground(self, layer):
		"""Moves the background horizontally, so that it is centered in the width of the layer."""
		background = layer.background
		if len(background.shapes) == 0:
			return
		bounds = background.bounds
		shiftX = int(round(layer.width / 2.0 - (bounds.origin.x + bounds.size.width / 2.0)))
		if shiftX:
			background.applyTransform((1, 0, 0, 1, shiftX, 0))

	def customTemplates(self, font, plans, settings):
		"""
		Returns ({master ID: custom dot}, problem). The dot is dotabove-ar as it is, unless the script drew it last and nobody changed it
		since: then the dot from before is still the one. A new dot of the current master overwrites the Size field.
		"""
		glyph = font.glyphs["dotabove-ar"]
		referenceKey = font.masters[0].id
		isCurrentFont = font == Glyphs.font
		for master, xHeight in plans:
			layer = glyph.layers[master.id] if glyph is not None else None
			if layer is None:
				return None, "no dotabove-ar to take the custom shape from"
			cached = self.templates.get(layer.layerId)
			if cached is not None and self.fingerprints.get(layer.layerId) == layerFingerprint(layer):
				continue
			template = templateFromLayer(layer)
			if template is None:
				return None, f"{master.name}: dotabove-ar has no outlines to take the custom shape from"
			self.templates[layer.layerId] = template
			if isCurrentFont and master.id == font.selectedFontMaster.id:
				size = max(1, int(round(max(template["width"], template["height"]))))
				settings["size"] = size
				self.setPref("size", size)
				self.w.size.set(str(size))
				self.references[referenceKey] = size
		self.references.setdefault(referenceKey, settings["size"])
		factor = settings["size"] / float(self.references[referenceKey])
		return {master.id: dict(self.templates[glyph.layers[master.id].layerId], factor=factor) for master, xHeight in plans}, None

	def drawFont(self, font, masterIDs, settings):
		"""Draws the dots in the masters of the font. All masters or none, so they stay compatible. Returns (layer count, problems)."""
		masters = [master for master in font.masters if masterIDs is None or master.id in masterIDs]
		plans, problems = [], []
		for master in masters:
			xHeight = metricPosition(font, master, GSMetricsTypexHeight)
			if xHeight is None:
				problems.append(f"{master.name}: no x-height metric")
			else:
				plans.append((master, xHeight))
		if problems:
			return 0, problems

		templates = {}
		if settings["shape"] == 3:
			templates, problem = self.customTemplates(font, plans, settings)
			if problem:
				return 0, [problem]

		glyphs = {}
		for glyphName, arrangement, position in dotGlyphs:
			glyph = font.glyphs[glyphName]
			if glyph is None:
				font.glyphs.append(newGlyphWithName(glyphName))
				glyph = font.glyphs[glyphName]
			glyphs[glyphName] = glyph

		count = 0
		font.disableUpdateInterface()
		try:
			for master, xHeight in plans:
				for glyphName, arrangement, position in dotGlyphs:
					self.setStatus(f"🔠 {glyphName}")
					glyph = glyphs[glyphName]
					layer = glyph.layers[master.id]
					if settings["backup"]:
						self.backUp(glyph, layer)
					# LSB 50, RSB equals LSB, so the sidebearings follow the dots when they change:
					glyph.leftMetricsKey = "=50"
					glyph.rightMetricsKey = "=|"
					glyph.widthMetricsKey = None
					layer.shapes = None
					for contour in placedContours(arrangement, position, xHeight, settings, templates.get(master.id)):
						layer.shapes.append(pathFromContour(contour))
					layer.cleanUpPaths()
					layer.updateMetrics()
					layer.syncMetrics()
					self.centerBackground(layer)  # whatever is in the background follows the foreground
					# the anchor sits horizontally in the middle of the dots, wherever the metrics keys put them:
					anchorName = anchorNames[position]
					anchorX = int(round(layer.bounds.origin.x + layer.bounds.size.width / 2.0))
					anchorY = {"above": xHeight, "below": 0, "center": int(round(xHeight / 2.0))}[position]
					if anchorName in layer.anchors:
						del layer.anchors[anchorName]
					layer.anchors.append(newAnchorWithName(anchorName, NSPoint(anchorX, anchorY)))
					if position in stackAnchorNames:
						# top or bottom: the Distance beyond the dots, on the same slanted line as the _top or _bottom anchor
						if position == "above":
							stackY = int(round(layer.bounds.origin.y + layer.bounds.size.height + settings["distance"]))
						else:
							stackY = int(round(layer.bounds.origin.y - settings["distance"]))
						stackPosition = italicize(NSPoint(anchorX, stackY), master.italicAngle, anchorY)
						stackAnchorName = stackAnchorNames[position]
						if stackAnchorName in layer.anchors:
							del layer.anchors[stackAnchorName]
						layer.anchors.append(newAnchorWithName(stackAnchorName, NSPoint(int(round(stackPosition.x)), stackY)))
					if glyphName == "dotabove-ar":
						self.fingerprints[layer.layerId] = layerFingerprint(layer)
					count += 1
		finally:
			font.enableUpdateInterface()
		if font.currentTab:
			font.currentTab.redraw()
		return count, []

	def draw(self):
		"""Draws the dot glyphs in the scope. Quiet, the status line reports."""
		settings = self.settings()
		if settings is None:
			self.setStatus("⚠️ Please enter numbers in the fields.")
			return
		targets = self.targets(settings["scope"])
		if not targets:
			self.setStatus("⚠️ No font open.")
			return

		self.setStatus("🛠️ Drawing…")
		total, firstProblem = 0, None
		for font, masterIDs in targets:
			count, problems = self.drawFont(font, masterIDs, settings)
			total += count
			for problem in problems:
				firstProblem = firstProblem or f"{fontFileName(font)}: {problem}"
		if firstProblem:
			self.setStatus(f"⚠️ {firstProblem}")
		else:
			self.setStatus(f"✅ Drew {total} layers.")


font = Glyphs.font
if font:
	DotMaker()
else:
	Message(title="No Font Open", message="Dot Maker needs a font. Please open one and run the script again.", OKButton=None)
