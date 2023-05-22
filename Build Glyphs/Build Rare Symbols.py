#MenuTitle: Build Rare Symbols
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Builds white and black, small and large, circles, triangles and squares.
"""

import vanilla, math
from Foundation import NSClassFromString, NSPoint
from AppKit import NSAffineTransform, NSAffineTransformStruct, NSButtLineCapStyle

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

def offsetLayer(thisLayer, offset, makeStroke=False, position=0.5, autoStroke=False):
	offsetFilter = NSClassFromString("GlyphsFilterOffsetCurve")
	try:
		# GLYPHS 3:
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyleStart_capStyleEnd_keepCompatibleOutlines_(
			thisLayer,
			offset,
			offset, # horizontal and vertical offset
			makeStroke, # if True, creates a stroke
			autoStroke, # if True, distorts resulting shape to vertical metrics
			position, # stroke distribution to the left and right, 0.5 = middle
			None,
			None,
			None,
			0,
			0,
			True
			)
	except:
		# GLYPHS 2:
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyle_keepCompatibleOutlines_(
			thisLayer,
			offset,
			offset, # horizontal and vertical offset
			makeStroke, # if True, creates a stroke
			autoStroke, # if True, distorts resulting shape to vertical metrics
			position, # stroke distribution to the left and right, 0.5 = middle
			thisLayer.glyphMetrics(), # metrics (G3)
			None,
			None, # error, shadow
			0, # NSButtLineCapStyle, # cap style
			True, # keep compatible
			)

def createGlyph(
		thisFont, glyphName, pathData, scaleFactor=1.0, rotation=0, overwrite=False, fill=True, stroke=50, sidebearing=50, closePath=True, belowBase=0.1, setMetricsKeys=True
	):
	glyph = None
	if thisFont.glyphs[glyphName]:
		if overwrite:
			print("🔣 %s: exists. Overwriting." % glyphName)
			glyph = thisFont.glyphs[glyphName]
	else:
		print("🔣 %s created." % glyphName)
		glyph = GSGlyph()
		glyph.name = glyphName
		thisFont.glyphs.append(glyph)
		glyph.updateGlyphInfo()

	if glyph:
		originalLayer = GSLayer()
		drawPenDataInLayer(originalLayer, pathData, closePath=closePath)
		originalHeight = originalLayer.fastBounds().size.height # FIX 3.2

		# scale:

		if fill:
			scaleCorrection = 0
		else:
			scaleCorrection = stroke
		scaleToHeight = originalHeight * scaleFactor - scaleCorrection
		currentHeight = originalLayer.fastBounds().size.height # TEMP FIX 3.2
		if not currentHeight:
			print("❌ ERROR: No content (height=0) for %s." % glyphName)
			return
		else:
			scaleFactor = scaleToHeight / currentHeight
			if scaleFactor != 1.0:
				matrix = transform(scale=scaleFactor).transformStruct()
				originalLayer.applyTransform(matrix)

		# rotate if necessary:
		if rotation:
			matrix = transform(rotate=rotation).transformStruct()
			originalLayer.applyTransform(matrix)

		# shift vertically:
		whereBottomShouldBe = -belowBase * originalHeight + (originalHeight - originalHeight * scaleFactor) / 2 # full height 10% below baseline, but respect scaleFactor
		whereItCurrentlyIs = originalLayer.fastBounds().origin.y # FIX 3.2
		verticalShift = whereBottomShouldBe - whereItCurrentlyIs
		if verticalShift:
			matrix = transform(shiftY=verticalShift).transformStruct()
			originalLayer.applyTransform(matrix)

		# stroke if necessary:
		if stroke > 1 and not fill:
			offset = stroke / 2
			offsetLayer(originalLayer, offset, makeStroke=True, position=0.5, autoStroke=False)

		# remove a node in 3D arrows:
		specialTreatmentOf3DArrows(originalLayer, glyphName)

		# set metrics keys:
		if setMetricsKeys:
			glyph.leftMetricsKey = "=%i" % sidebearing
			glyph.rightMetricsKey = "=|"
		else:
			glyph.leftMetricsKey = None
			glyph.rightMetricsKey = None

		# go through all layers:
		for thisLayer in glyph.layers:
			if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
				# make sure it's empty:
				thisLayer.clear()
				# put paths onto the actual layer:
				for originalPath in originalLayer.paths:
					thisLayer.paths.append(originalPath.copy())
				# update metrics:
				thisLayer.roundCoordinates()
				if not setMetricsKeys:
					if thisLayer.italicAngle == 0.0:
						thisLayer.leftMetricsKey = "==%i" % sidebearing
						thisLayer.rightMetricsKey = "==|"
					else:
						# set LSB:
						shiftX = sidebearing - thisLayer.bounds.origin.x
						layerShiftForLSB = transform(shiftX=shiftX).transformStruct()
						thisLayer.applyTransform(layerShiftForLSB)
						# set width/RSB:
						rightEdge = thisLayer.bounds.origin.x + thisLayer.bounds.size.width
						thisLayer.width = rightEdge + sidebearing
				# update metrics keys:
				if setMetricsKeys or thisLayer.italicAngle == 0.0:
					thisLayer.updateMetrics()
					thisLayer.syncMetrics()

				print("\t✅ Layer: %s" % thisLayer.name)
		return True
	else:
		print("⚠️ %s: already exists. Skipping." % glyphName)
		return False

def specialTreatmentOf3DArrows(thisLayer, glyphName):
	if "threeD" in glyphName and len(thisLayer.paths) == 2:
		smallestPath = sorted(thisLayer.paths, key=lambda thisPath: thisPath.area())[0]
		if "RightLightedUp" in glyphName:
			nodeIndex = sorted(smallestPath.nodes, key=lambda node: node.x)[0].index
			del smallestPath.nodes[nodeIndex]
		elif "LeftLightedDown" in glyphName:
			nodeIndex = sorted(smallestPath.nodes, key=lambda node: -node.x)[0].index
			del smallestPath.nodes[nodeIndex]
		elif "TopLighted" in glyphName:
			nodeIndex = sorted(smallestPath.nodes, key=lambda node: node.y)[0].index
			del smallestPath.nodes[nodeIndex]

def hashtagCoordsForHeight(s):
	"""
	Hashtag
	origin = 0,0
	"""
	coords = (
		( # path
			(s / 3, 0),
			(s / 3, s),
			),
		( # path
			(2 * s / 3, 0),
			(2 * s / 3, s),
			),
		( # path
			(0, s / 3),
			(s, s / 3),
			),
		( # path
			(0, 2 * s / 3),
			(s, 2 * s / 3),
			),
		)
	return coords

def triangleCoordsForSide(s):
	"""
	Upwards pointing equilateral triangle with equal sides s
	origin = 0,0
	"""
	factor = 3**0.5 / 2
	coords = (
		( # path
			(0, 0),
			(s, 0),
			(s / 2, factor * s),
			),
		)
	return coords

def arrowheadCoordsForSide(s):
	"""
	Upwards pointing equilateral triangle with equal sides s
	origin = 0,0
	"""
	factor = 3**0.5 / 2
	coords = (
		( # path
			(0, 0),
			(s / 2, factor * s / 4),
			(s, 0),
			(s / 2, factor * s),
			),
		)
	return coords

def arrowhead3DCoordsForSide(s):
	"""
	Upwards pointing equilateral triangle with equal sides s
	origin = 0,0
	"""
	factor = 3**0.5 / 2
	coords = (
		( # path
			(0, 0),
			(s / 2, factor * s / 4),
			(s, 0),
			(s / 2, factor * s),
			),
		)
	return coords

def squareCoordsForSide(s):
	"""
	Square with side s
	origin = 0,0
	"""
	coords = (
		( # path
			(0, 0),
			(s, 0),
			(s, s),
			(0, s),
			),
		)
	return coords

def diamondCoordsForHeight(s):
	"""
	Diamond with height s
	origin = 0,0
	"""
	coords = (
		( # path
			(s / 2, 0),
			(s, s / 2),
			(s / 2, s),
			(0, s / 2),
			),
		)
	return coords

def optionCoordsForHeight(s):
	"""
	Option with height s
	origin = 0,0
	"""
	coords = (
		( # path
			(0, s),
			(s / 3, s),
			(s * 7 / 9, 0),
			(s * 13 / 10, 0),
			),
		( # path
			(s * 2 / 3, s),
			(s * 13 / 10, s),
			),
		)
	return coords

def shiftCoordsForHeight(s):
	"""
	Shift with height s
	origin = 0,0
	"""
	coords = (
		( # path
			(s / 2, s),
			(0, s * 4 / 9),
			(s * 4 / 15, s * 4 / 9),
			(s * 4 / 15, 0),
			(s * 11 / 15, 0),
			(s * 11 / 15, s * 4 / 9),
			(s, s * 4 / 9),
			),
		)
	return coords

def propellorCoordsForHeight(s):
	"""
	Propellor with height s
	origin = 0,0
	"""
	coords = (
		( # path
		(s*0.652, s*0.239),
		((s*0.652, s*0.077), (s*0.716, s*0.000), (s*0.831, s*0.000)),
		((s*0.936, s*0.000), (s*1.000, s*0.064), (s*1.000, s*0.169)),
		((s*1.000, s*0.284), (s*0.923, s*0.348), (s*0.761, s*0.348)),
		(s*0.239, s*0.348),
		((s*0.077, s*0.348), (s*0.000, s*0.284), (s*0.000, s*0.169)),
		((s*0.000, s*0.064), (s*0.064, s*0.000), (s*0.169, s*0.000)),
		((s*0.284, s*0.000), (s*0.348, s*0.077), (s*0.348, s*0.239)),
		(s*0.348, s*0.761),
		((s*0.348, s*0.923), (s*0.284, s*1.000), (s*0.169, s*1.000)),
		((s*0.064, s*1.000), (s*0.000, s*0.936), (s*0.000, s*0.831)),
		((s*0.000, s*0.716), (s*0.077, s*0.652), (s*0.239, s*0.652)),
		(s*0.761, s*0.652),
		((s*0.923, s*0.652), (s*1.000, s*0.716), (s*1.000, s*0.831)),
		((s*1.000, s*0.936), (s*0.936, s*1.000), (s*0.831, s*1.000)),
		((s*0.716, s*1.000), (s*0.652, s*0.923), (s*0.652, s*0.761)),
		),
	)
	return coords

def circleCoordsForHeight(s):
	radius = s / 2
	x = s / 2
	y = s / 2
	bcp = 4.0 * (2.0**0.5 - 1.0) / 3.0
	handle = radius * bcp
	coords=(
		( # path
		(x, y-radius),
		((x+handle, y-radius), (x+radius, y-handle), (x+radius, y)),
		((x+radius, y+handle), (x+handle, y+radius), (x, y+radius)),
		((x-handle, y+radius), (x-radius, y+handle), (x-radius, y)),
		((x-radius, y-handle), (x-handle, y-radius), (x, y-radius)),
		),
	)
	return coords

def drawPenDataInLayer(thisLayer, penData, closePath=True):
	for thisPath in penData:
		pen = thisLayer.getPen()
		pen.moveTo(thisPath[0])
		for thisSegment in thisPath[1:]:
			if len(thisSegment) == 2: # lineto (2 coordinates: x,y)
				pen.lineTo(thisSegment)
			elif len(thisSegment) == 3: # curveto (3 x/y tuples)
				pen.curveTo(thisSegment[0], thisSegment[1], thisSegment[2])
			else:
				print("%s: Path drawing error. Could not process this segment:\n" % (glyphName, thisSegment))
		if closePath:
			pen.closePath()
		pen.endPath()

	# clean up:
	# thisLayer.correctPathDirection()
	thisLayer.cleanUpPaths()
	return thisLayer

class BuildCirclesSquaresTriangles(object):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 325
		windowWidthResize = 100 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Build Rare Symbols", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName="com.mekkablue.BuildCirclesSquaresTriangles.mainwindow" # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		column = 170

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Build the following glyphs, see tooltips for details:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.whiteTriangles = vanilla.CheckBox((inset, linePos - 1, column, 20), "White Triangles △▷▽◁", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.whiteTriangles.getNSButton().setToolTip_("Will create upWhiteTriangle, rightWhiteTriangle, downWhiteTriangle, leftWhiteTriangle.")
		self.w.blackTriangles = vanilla.CheckBox((inset + column, linePos - 1, -inset, 20), "Black Triangles ▲▶▼◀", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.blackTriangles.getNSButton().setToolTip_("Will create upBlackTriangle, rightBlackTriangle, downBlackTriangle, leftBlackTriangle.")
		linePos += lineHeight

		self.w.blackArrowheads = vanilla.CheckBox((inset, linePos - 1, column, 20), "Black Arrowheads", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.blackArrowheads.getNSButton(
		).setToolTip_("Will create blackUpEquilateralArrowhead, blackRightEquilateralArrowhead, blackDownEquilateralArrowhead, blackLeftEquilateralArrowhead.")
		self.w.black3DArrowheads = vanilla.CheckBox(
			(inset + column, linePos - 1, -inset, 20), "Black 3D Arrowheads", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.black3DArrowheads.getNSButton().setToolTip_(
			"Will create threeDRightLightedUpEquilateralArrowhead, threeDTopLightedRightEquilateralArrowhead, threeDLeftLightedDownEquilateralArrowhead, threeDTopLightedLeftEquilateralArrowhead."
			)
		linePos += lineHeight

		self.w.whiteShapes = vanilla.CheckBox((inset, linePos - 1, column, 20), "White Shapes ○◇□", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.whiteShapes.getNSButton().setToolTip_("Will create whiteCircle, whiteDiamond, whiteSquare.")
		self.w.blackShapes = vanilla.CheckBox((inset + column, linePos - 1, -inset, 20), "Black Shapes ●◆■", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.blackShapes.getNSButton().setToolTip_("Will create blackCircle, blackDiamond, blackSquare.")
		linePos += lineHeight

		self.w.whiteLargeSquare = vanilla.CheckBox((inset, linePos - 1, column, 20), "White Large Square ⬜", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.whiteLargeSquare.getNSButton().setToolTip_("Will create whiteLargeSquare.")
		self.w.blackLargeSquare = vanilla.CheckBox(
			(inset + column, linePos - 1, -inset, 20), "Black Large Square ⬛", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.blackLargeSquare.getNSButton().setToolTip_("Will create blackLargeSquare.")
		linePos += lineHeight

		self.w.propellor = vanilla.CheckBox((inset, linePos - 1, column, 20), "Cmd Opt Shift ⌘⌥⇧", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.propellor.getNSButton().setToolTip_("Will create propellor, optionKey, upWhiteArrow.")
		self.w.viewdataSquare = vanilla.CheckBox((inset + column, linePos - 1, -inset, 20), "Viewdata Square ⌗", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.viewdataSquare.getNSButton().setToolTip_("Will create viewdataSquare.")
		linePos += lineHeight

		self.w.line = vanilla.HorizontalLine((inset, linePos + 2, -inset, 1))
		linePos += 12

		self.w.strokeText = vanilla.TextBox((inset, linePos + 2, 80, 14), "Stroke width:", sizeStyle='small', selectable=True)
		self.w.stroke = vanilla.EditText((inset + 80, linePos - 1, 70, 19), "50", callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Uniform stroke width for icons. Does not apply to filled (‘black’) shapes."
		self.w.strokeText.getNSTextField().setToolTip_(tooltip)
		self.w.stroke.getNSTextField().setToolTip_(tooltip)
		self.w.heightText = vanilla.TextBox((inset + column, linePos + 2, 85, 14), "Symbol size:", sizeStyle='small', selectable=True)
		self.w.height = vanilla.EditText((inset + column + 85, linePos - 1, -inset, 19), "700", callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Reference height for symbols. Each symbol has an individual scale factor. This reference height times the symbol’s scale factor will yield the actual size of each symbol."
		self.w.heightText.getNSTextField().setToolTip_(tooltip)
		self.w.height.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.sidebearingText = vanilla.TextBox((inset, linePos + 2, 80, 14), "Sidebearings:", sizeStyle='small', selectable=True)
		self.w.sidebearing = vanilla.EditText((inset + 80, linePos - 1, 70, 19), "50", callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Will be used for both LSB and RSB, effectively centering the shape in its width. Unless the Disrespect Italic Angle option is used, will insert it as metrics keys (e.g., LSB ‘=60’, RSB ‘=|’) for the glyph."
		self.w.sidebearingText.getNSTextField().setToolTip_(tooltip)
		self.w.sidebearing.getNSTextField().setToolTip_(tooltip)
		self.w.belowBaseText = vanilla.TextBox((inset + column, linePos + 2, 85, 14), "% below base:", sizeStyle='small', selectable=True)
		self.w.belowBase = vanilla.EditText((inset + column + 85, linePos - 1, -inset, 19), "10", callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Determines the vertical position. This percentage of the symbol size will be below, the rest above the baseline."
		self.w.belowBaseText.getNSTextField().setToolTip_(tooltip)
		self.w.belowBase.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.disrespectItalicAngle = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Sidebearings disrespect italic angle (useful for italics)", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.disrespectItalicAngle.getNSButton().setToolTip_(
			"If activated, will not set sidebearing metrics keys if there is an italic angle other than zero. If the italic angle is zero, will set (and update) layer-specific metrics keys (with double equals sign ==). Highly recommended if you want the symbols to have the same widths in upright and italic."
			)
		linePos += lineHeight

		self.w.overwriteExistingGlyphs = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "⚠️ Overwrite existing glyphs", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.overwriteExistingGlyphs.getNSButton(
		).setToolTip_("If set, will simply replace the symbol glyphs that already exist. Careful with this option if you made any manual changes you want to keep.")
		linePos += lineHeight

		self.w.openTab = vanilla.CheckBox((inset, linePos - 1, column, 20), "Open tab with new glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.openTab.getNSButton().setToolTip_("If set, will open a new Edit tab containing all the glyphs for which a checkbox is set further above.")
		self.w.reuseTab = vanilla.CheckBox((inset + column, linePos - 1, -inset, 20), "Reuse current tab", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.getNSButton().setToolTip_("If set, will reuse the frontmost Edit tab, rather than open a new one. Only opens a new tab if no Edit tab is active.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Build", sizeStyle='regular', callback=self.BuildCirclesSquaresTrianglesMain)
		self.w.setDefaultButton(self.w.runButton)

		# (un)check all checkboxes:
		self.w.checkAllButton = vanilla.Button((-180 - inset, -20 - inset, -90 - inset, -inset), "Check All", sizeStyle='regular', callback=self.checkOrUncheckAll)
		self.w.checkAllButton.getNSButton().setToolTip_("Activates all checkboxes above the separator line.")
		self.w.uncheckAllButton = vanilla.Button((-300 - inset, -20 - inset, -190 - inset, -inset), "Uncheck All", sizeStyle='regular', callback=self.checkOrUncheckAll)
		self.w.uncheckAllButton.getNSButton().setToolTip_("Deactivates all checkboxes above the separator line.")

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Build Rare Symbols' could not load preferences. Will resort to defaults.")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def checkOrUncheckAll(self, sender=None):
		toggle = sender == self.w.checkAllButton
		self.w.whiteTriangles.set(toggle)
		self.w.blackTriangles.set(toggle)
		self.w.black3DArrowheads.set(toggle)
		self.w.blackArrowheads.set(toggle)
		self.w.whiteShapes.set(toggle)
		self.w.blackShapes.set(toggle)
		self.w.whiteLargeSquare.set(toggle)
		self.w.blackLargeSquare.set(toggle)
		self.w.propellor.set(toggle)
		self.w.viewdataSquare.set(toggle)
		self.SavePreferences()

	def updateUI(self, sender=None):
		toggle = (
			self.w.whiteTriangles.get() or self.w.blackTriangles.get() or self.w.black3DArrowheads.get() or self.w.blackArrowheads.get() or self.w.whiteShapes.get()
			or self.w.blackShapes.get() or self.w.whiteLargeSquare.get() or self.w.blackLargeSquare.get() or self.w.propellor.get() or self.w.viewdataSquare.get()
			)
		self.w.runButton.enable(toggle)
		self.w.reuseTab.enable(self.w.openTab.get())

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.whiteTriangles"] = self.w.whiteTriangles.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.blackTriangles"] = self.w.blackTriangles.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.black3DArrowheads"] = self.w.black3DArrowheads.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.blackArrowheads"] = self.w.blackArrowheads.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.whiteShapes"] = self.w.whiteShapes.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.blackShapes"] = self.w.blackShapes.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.whiteLargeSquare"] = self.w.whiteLargeSquare.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.blackLargeSquare"] = self.w.blackLargeSquare.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.propellor"] = self.w.propellor.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.viewdataSquare"] = self.w.viewdataSquare.get()

			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.stroke"] = self.w.stroke.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.height"] = self.w.height.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.belowBase"] = self.w.belowBase.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.sidebearing"] = self.w.sidebearing.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.disrespectItalicAngle"] = self.w.disrespectItalicAngle.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.overwriteExistingGlyphs"] = self.w.overwriteExistingGlyphs.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.openTab"] = self.w.openTab.get()
			Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.reuseTab"] = self.w.reuseTab.get()

			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.whiteTriangles", 0)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.blackTriangles", 0)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.black3DArrowheads", 0)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.blackArrowheads", 0)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.whiteShapes", 0)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.blackShapes", 0)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.whiteLargeSquare", 0)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.blackLargeSquare", 0)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.propellor", 0)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.viewdataSquare", 0)

			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.stroke", 50)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.height", 700)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.belowBase", 10)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.sidebearing", 50)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.disrespectItalicAngle", 0)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.overwriteExistingGlyphs", 0)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.openTab", 1)
			Glyphs.registerDefault("com.mekkablue.BuildCirclesSquaresTriangles.reuseTab", 1)

			# load previously written prefs:
			self.w.whiteTriangles.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.whiteTriangles"])
			self.w.blackTriangles.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.blackTriangles"])
			self.w.black3DArrowheads.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.black3DArrowheads"])
			self.w.blackArrowheads.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.blackArrowheads"])
			self.w.whiteShapes.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.whiteShapes"])
			self.w.blackShapes.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.blackShapes"])
			self.w.whiteLargeSquare.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.whiteLargeSquare"])
			self.w.blackLargeSquare.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.blackLargeSquare"])
			self.w.propellor.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.propellor"])
			self.w.viewdataSquare.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.viewdataSquare"])

			self.w.stroke.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.stroke"])
			self.w.height.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.height"])
			self.w.belowBase.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.belowBase"])
			self.w.sidebearing.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.sidebearing"])
			self.w.disrespectItalicAngle.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.disrespectItalicAngle"])
			self.w.overwriteExistingGlyphs.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.overwriteExistingGlyphs"])
			self.w.openTab.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.openTab"])
			self.w.reuseTab.set(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.reuseTab"])

			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def BuildCirclesSquaresTrianglesMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Build Rare Symbols' could not write preferences.")

			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Build Rare Symbols Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				whiteTriangles = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.whiteTriangles"]
				blackTriangles = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.blackTriangles"]
				black3DArrowheads = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.black3DArrowheads"]
				blackArrowheads = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.blackArrowheads"]
				whiteShapes = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.whiteShapes"]
				blackShapes = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.blackShapes"]
				whiteLargeSquare = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.whiteLargeSquare"]
				blackLargeSquare = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.blackLargeSquare"]
				propellor = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.propellor"]
				viewdataSquare = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.viewdataSquare"]

				stroke = float(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.stroke"])
				height = float(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.height"])
				belowBase = float(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.belowBase"]) / 100.0
				sidebearing = float(Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.sidebearing"])

				disrespectItalicAngle = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.disrespectItalicAngle"]
				overwriteExistingGlyphs = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.overwriteExistingGlyphs"]
				openTab = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.openTab"]
				reuseTab = Glyphs.defaults["com.mekkablue.BuildCirclesSquaresTriangles.reuseTab"]

				trianglePath = triangleCoordsForSide(height)
				propellorPath = propellorCoordsForHeight(height)
				optionPath = optionCoordsForHeight(height)
				shiftPath = shiftCoordsForHeight(height)
				diamondPath = diamondCoordsForHeight(height)
				squarePath = squareCoordsForSide(height)
				viewdataSquarePath = hashtagCoordsForHeight(height)
				circlePath = circleCoordsForHeight(height)
				arrowheadPath = arrowheadCoordsForSide(height)
				arrowhead3DPath = arrowhead3DCoordsForSide(height)

				processedGlyphs = []

				if whiteTriangles:
					triangleInfo = (
						{
							"name": "upWhiteTriangle",
							"rotation": 0
							},
						{
							"name": "rightWhiteTriangle",
							"rotation": -90
							},
						{
							"name": "downWhiteTriangle",
							"rotation": 180
							},
						{
							"name": "leftWhiteTriangle",
							"rotation": +90
							},
						)
					for shape in triangleInfo:
						glyphName = shape["name"]
						rotation = shape["rotation"]
						if createGlyph(
							thisFont,
							glyphName,
							trianglePath,
							scaleFactor=0.95,
							rotation=rotation,
							overwrite=overwriteExistingGlyphs,
							fill=False,
							stroke=stroke,
							belowBase=belowBase,
							sidebearing=sidebearing,
							setMetricsKeys=(not disrespectItalicAngle)
							):
							processedGlyphs.append(glyphName)

				if blackTriangles:
					triangleInfo = (
						{
							"name": "upBlackTriangle",
							"rotation": 0
							},
						{
							"name": "rightBlackTriangle",
							"rotation": -90
							},
						{
							"name": "downBlackTriangle",
							"rotation": 180
							},
						{
							"name": "leftBlackTriangle",
							"rotation": +90
							},
						)
					for shape in triangleInfo:
						glyphName = shape["name"]
						rotation = shape["rotation"]
						if createGlyph(
							thisFont,
							glyphName,
							trianglePath,
							scaleFactor=0.95,
							rotation=rotation,
							overwrite=overwriteExistingGlyphs,
							fill=True,
							belowBase=belowBase,
							sidebearing=sidebearing,
							setMetricsKeys=(not disrespectItalicAngle)
							):
							processedGlyphs.append(glyphName)

				if blackArrowheads:
					triangleInfo = (
						{
							"name": "blackUpEquilateralArrowhead",
							"rotation": 0
							},
						{
							"name": "blackRightEquilateralArrowhead",
							"rotation": -90
							},
						{
							"name": "blackDownEquilateralArrowhead",
							"rotation": 180
							},
						{
							"name": "blackLeftEquilateralArrowhead",
							"rotation": +90
							},
						)
					for shape in triangleInfo:
						glyphName = shape["name"]
						rotation = shape["rotation"]
						if createGlyph(
							thisFont,
							glyphName,
							arrowheadPath,
							scaleFactor=0.95,
							rotation=rotation,
							overwrite=overwriteExistingGlyphs,
							fill=True,
							belowBase=belowBase,
							sidebearing=sidebearing,
							setMetricsKeys=(not disrespectItalicAngle)
							):
							processedGlyphs.append(glyphName)

				if black3DArrowheads:
					triangleInfo = (
						{
							"name": "threeDRightLightedUpEquilateralArrowhead",
							"rotation": 0
							},
						{
							"name": "threeDTopLightedRightEquilateralArrowhead",
							"rotation": -90
							},
						{
							"name": "threeDLeftLightedDownEquilateralArrowhead",
							"rotation": 180
							},
						{
							"name": "threeDTopLightedLeftEquilateralArrowhead",
							"rotation": +90
							},
						)
					for shape in triangleInfo:
						glyphName = shape["name"]
						rotation = shape["rotation"]
						if createGlyph(
							thisFont,
							glyphName,
							arrowheadPath,
							scaleFactor=0.95,
							rotation=rotation,
							overwrite=overwriteExistingGlyphs,
							fill=False,
							belowBase=belowBase,
							sidebearing=sidebearing,
							setMetricsKeys=(not disrespectItalicAngle)
							):
							processedGlyphs.append(glyphName)

				if whiteShapes:
					glyphName = "whiteSquare"
					if createGlyph(
						thisFont,
						glyphName,
						squarePath,
						scaleFactor=0.78,
						overwrite=overwriteExistingGlyphs,
						fill=False,
						stroke=stroke,
						belowBase=belowBase,
						sidebearing=sidebearing,
						setMetricsKeys=(not disrespectItalicAngle)
						):
						processedGlyphs.append(glyphName)
						glyphName = "whiteDiamond"
					if createGlyph(
						thisFont,
						glyphName,
						diamondPath,
						scaleFactor=0.93,
						overwrite=overwriteExistingGlyphs,
						fill=False,
						stroke=stroke,
						belowBase=belowBase,
						sidebearing=sidebearing,
						setMetricsKeys=(not disrespectItalicAngle)
						):
						processedGlyphs.append(glyphName)
						glyphName = "whiteCircle"
					if createGlyph(
						thisFont,
						glyphName,
						circlePath,
						scaleFactor=0.87,
						overwrite=overwriteExistingGlyphs,
						fill=False,
						stroke=stroke,
						belowBase=belowBase,
						sidebearing=sidebearing,
						setMetricsKeys=(not disrespectItalicAngle)
						):
						processedGlyphs.append(glyphName)

				if blackShapes:
					glyphName = "blackSquare"
					if createGlyph(
						thisFont,
						glyphName,
						squarePath,
						scaleFactor=0.78,
						overwrite=overwriteExistingGlyphs,
						fill=True,
						belowBase=belowBase,
						sidebearing=sidebearing,
						setMetricsKeys=(not disrespectItalicAngle)
						):
						processedGlyphs.append(glyphName)
						glyphName = "blackDiamond"
					if createGlyph(
						thisFont,
						glyphName,
						diamondPath,
						scaleFactor=0.93,
						overwrite=overwriteExistingGlyphs,
						fill=True,
						belowBase=belowBase,
						sidebearing=sidebearing,
						setMetricsKeys=(not disrespectItalicAngle)
						):
						processedGlyphs.append(glyphName)
						glyphName = "blackCircle"
					if createGlyph(
						thisFont,
						glyphName,
						circlePath,
						scaleFactor=0.87,
						overwrite=overwriteExistingGlyphs,
						fill=True,
						belowBase=belowBase,
						sidebearing=sidebearing,
						setMetricsKeys=(not disrespectItalicAngle)
						):
						processedGlyphs.append(glyphName)

				if whiteLargeSquare:
					glyphName = "whiteLargeSquare"
					if createGlyph(
						thisFont,
						glyphName,
						squarePath,
						scaleFactor=1.2,
						overwrite=overwriteExistingGlyphs,
						fill=False,
						stroke=stroke,
						belowBase=belowBase,
						sidebearing=sidebearing,
						setMetricsKeys=(not disrespectItalicAngle)
						):
						processedGlyphs.append(glyphName)

				if blackLargeSquare:
					glyphName = "blackLargeSquare"
					if createGlyph(
						thisFont,
						glyphName,
						squarePath,
						scaleFactor=1.2,
						overwrite=overwriteExistingGlyphs,
						fill=True,
						belowBase=belowBase,
						sidebearing=sidebearing,
						setMetricsKeys=(not disrespectItalicAngle)
						):
						processedGlyphs.append(glyphName)

				if propellor:
					propellorInfo = (
						{
							"name": "propellor",
							"path": propellorPath,
							"scale": 0.98,
							"close": True
							},
						{
							"name": "optionKey",
							"path": optionPath,
							"scale": 0.84,
							"close": False
							},
						{
							"name": "upWhiteArrow",
							"path": shiftPath,
							"scale": 1.02,
							"close": True
							},
						)
					for shape in propellorInfo:
						glyphName = shape["name"]
						path = shape["path"]
						scale = shape["scale"]
						close = shape["close"]
						if createGlyph(
							thisFont,
							glyphName,
							path,
							scaleFactor=scale,
							overwrite=overwriteExistingGlyphs,
							fill=False,
							stroke=stroke,
							closePath=close,
							belowBase=belowBase,
							sidebearing=sidebearing,
							setMetricsKeys=(not disrespectItalicAngle)
							):
							processedGlyphs.append(glyphName)

				if viewdataSquare:
					glyphName = "viewdataSquare"
					if createGlyph(
						thisFont,
						glyphName,
						viewdataSquarePath,
						scaleFactor=1.0,
						overwrite=overwriteExistingGlyphs,
						fill=False,
						stroke=stroke,
						closePath=False,
						belowBase=belowBase,
						sidebearing=sidebearing,
						setMetricsKeys=(not disrespectItalicAngle)
						):
						processedGlyphs.append(glyphName)

				# self.w.close() # delete if you want window to stay open

				# Final report:
				Glyphs.showNotification(
					"%s: Done" % (thisFont.familyName),
					"Build Rare Symbols: (re)created %i glyph%s. Details in Macro Window" % (
						len(processedGlyphs),
						"" if len(processedGlyphs) == 1 else "s",
						),
					)
				print("\nDone.")

				if openTab and processedGlyphs:
					tabText = "/" + "/".join(processedGlyphs)
					tab = thisFont.currentTab
					if not reuseTab or not tab:
						tab = thisFont.newTab(tabText)
					else:
						tab.text = tabText

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Build Rare Symbols Error: %s" % e)
			import traceback
			print(traceback.format_exc())

BuildCirclesSquaresTriangles()
