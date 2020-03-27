#MenuTitle: Path Problem Finder
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Finds all kinds of potential problems in outlines, and opens a new tab with affected layers.
"""

import vanilla, math

canHaveOpenOutlines = (
	"_cap",
	"_corner",
	"_line",
	"_brush",
)

def hasOffcurveAsStartPoint( Layer ):
	for p in Layer.paths:
		scenario1 = p.nodes[0].type == OFFCURVE and p.nodes[1].type != OFFCURVE
		scenario2 = p.nodes[0].type == CURVE and p.nodes[-1].type == OFFCURVE
		if scenario1 or scenario2:
			return True
	return False

def hasShallowCurveSegment(thisLayer, minSize):
	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			if thisNode.type == CURVE:
				thisSegment = (
					thisNode.prevNode.prevNode.prevNode,
					thisNode.prevNode.prevNode,
					thisNode.prevNode,
					thisNode,
				)
				xCoords = [p.x for p in thisSegment]
				yCoords = [p.y for p in thisSegment]
				xDist = abs( min(xCoords) - max(xCoords) )
				yDist = abs( min(yCoords) - max(yCoords) )
				if xDist < minSize or yDist < minSize:
					for affectedNode in thisSegment:
						thisLayer.selection.append(affectedNode)
					return True
	return False

def hasZeroHandles( thisLayer ):
	for thisPath in thisLayer.paths:
		numberOfNodes = len(thisPath.nodes)
		for i in range(numberOfNodes-1):
			thisNode = thisPath.nodes[i]
			if thisNode.type == GSOFFCURVE:
				prevNodeIndex = (i-1) % numberOfNodes
				nextNodeIndex = (i+1) % numberOfNodes
				prevNode = thisPath.nodes[prevNodeIndex]
				nextNode = thisPath.nodes[nextNodeIndex]
				if thisNode.position == prevNode.position or thisNode.position == nextNode.position:
					return True
	return False
	
def hasTwoPointOutlines( thisLayer ):
	for thisPath in thisLayer.paths:
		onCurveNodes = [n for n in thisPath.nodes if n.type != OFFCURVE]
		if len(onCurveNodes) < 3:
			return True
	return False

def hasOpenPaths( thisLayer ):
	for thisPath in thisLayer.paths:
		if not thisPath.closed:
			return True
	return False

def hasBadOutlineOrder( thisLayer ):
	firstPath = thisLayer.paths[0]
	if firstPath and firstPath.direction != -1:
		return True
	else:
		return False

def hasAlmostOrthogonalLines( thisLayer, threshold=3.0 ):
	for thisPath in thisLayer.paths:
		for i, thisNode in enumerate(thisPath.nodes):
			if thisNode.type == GSLINE:
				prevNodeIndex = (i-1)%len(thisPath.nodes)
				prevNode = thisPath.nodes[prevNodeIndex]
				xDiff = abs(thisNode.x-prevNode.x)
				yDiff = abs(thisNode.y-prevNode.y)
				if (0.1 < xDiff and xDiff < threshold) or (0.1 < yDiff and threshold > yDiff ):
					return True
	return False

def hasShallowCurve( thisLayer, threshold=5.0 ):
	for thisPath in thisLayer.paths:
		for i, thisNode in enumerate(thisPath.nodes):
			if thisNode.type == GSCURVE:
				pointA = thisNode.position
				pointB = thisPath.nodes[ (i-1)%len(thisPath.nodes) ].position
				pointC = thisPath.nodes[ (i-2)%len(thisPath.nodes) ].position
				pointD = thisPath.nodes[ (i-3)%len(thisPath.nodes) ].position
				for handle in (pointC, pointD):
					dist, vect = distanceAndRelativePosition(pointA, pointB, handle)
					if 0.0 < vect < 1.0 and dist < threshold:
						return True
	return False

def hasShallowCurveBBox( thisLayer, threshold=10.0 ):
	for thisPath in thisLayer.paths:
		for i, thisNode in enumerate(thisPath.nodes):
			if thisNode.type == GSCURVE:
				pointA = thisNode.position
				pointD = thisPath.nodes[ (i-3)%len(thisPath.nodes) ].position
				if abs(pointA.x-pointD.x) < threshold or abs(pointA.y-pointD.y) < threshold:
					minX, maxX = sorted((pointA.x,pointD.x))
					minY, maxY = sorted((pointA.y,pointD.y))
					pointB = thisPath.nodes[ (i-1)%len(thisPath.nodes) ].position
					pointC = thisPath.nodes[ (i-2)%len(thisPath.nodes) ].position
					horizontallyWithin = minX-1 < min(pointB.x, pointC.x) and maxX+1 > max(pointB.x, pointC.x)
					verticallyWithin = minY-1 < min(pointB.y, pointC.y) and maxY+1 > max(pointB.y, pointC.y)
					if horizontallyWithin and verticallyWithin:
						return True
	return False

def angleBetweenPoints( firstPoint, secondPoint ):
	"""
	Returns the angle (in degrees) of the straight line between firstPoint and secondPoint,
	0 degrees being the second point to the right of first point.
	firstPoint, secondPoint: must be NSPoint or GSNode
	"""
	xDiff = secondPoint.x - firstPoint.x
	yDiff = secondPoint.y - firstPoint.y
	return math.degrees(math.atan2(yDiff,xDiff))

def hasAngledHandles( thisLayer, threshold=8 ):
	for thisPath in thisLayer.paths:
		for i, handle in enumerate(thisPath.nodes):
			if handle.type == GSOFFCURVE:
				onCurveNodeIndex = (i-1)%len(thisPath.nodes)
				onCurveNode = thisPath.nodes[onCurveNodeIndex]
				if onCurveNode.type == GSOFFCURVE:
					onCurveNodeIndex = (i+1)%len(thisPath.nodes)
					onCurveNode = thisPath.nodes[onCurveNodeIndex]
				handleIsOrthogonal = handle.x == onCurveNode.x or handle.y == onCurveNode.y
				if not handleIsOrthogonal:
					angle = math.fabs(math.fmod(angleBetweenPoints(handle.position, onCurveNode.position), 90.0))
					if angle < threshold or angle > (90-threshold):
						return True
	return False
		
def hasShortHandles( thisLayer, threshold=10.0 ):
	for thisPath in thisLayer.paths:
		for i, handle in enumerate(thisPath.nodes):
			if handle.type == GSOFFCURVE:
				onCurveNodeIndex = (i-1)%len(thisPath.nodes)
				onCurveNode = thisPath.nodes[onCurveNodeIndex]
				if onCurveNode.type == GSOFFCURVE:
					onCurveNodeIndex = (i+1)%len(thisPath.nodes)
					onCurveNode = thisPath.nodes[onCurveNodeIndex]
				if 0.0 < distance( handle.position, onCurveNode.position ) < threshold:
					return True
	return False

def intersect( pointA, pointB, pointC, pointD ):
	"""
	Returns an NSPoint of the intersection AB with CD,
	or None if there is no intersection.
	pointA, pointB: NSPoints or GSNodes representing the first line AB,
	pointC, pointD: NSPoints or GSNodes representing the second line CD.
	"""
	xA, yA = pointA.x, pointA.y
	xB, yB = pointB.x, pointB.y
	xC, yC = pointC.x, pointC.y
	xD, yD = pointD.x, pointD.y
	
	try:
		slopeAB = ( float(yB) - float(yA) ) / ( float(xB) - float(xA) )
	except:
		slopeAB = None # division by zero if vertical
	
	try:
		slopeCD = ( float(yD) - float(yC) ) / ( float(xD) - float(xC) )
	except:
		slopeCD = None # division by zero if vertical
	
	if slopeAB == slopeCD: # parallel, no intersection
		return None
	elif slopeAB is None: # first line is vertical
		x = xA
		y = slopeCD * ( x - xC ) + yC
	elif slopeCD is None: # second line is vertical
		x = xC
		y = slopeAB * ( x - xA ) + yA
	else: # both lines have different angles other than vertical
		x = ( slopeAB * xA - yA - slopeCD * xC + yC ) / ( slopeAB - slopeCD )
		y = slopeAB * ( x - xA ) + yA
	return NSPoint( x, y )

def hasLargeHandles( thisLayer ):
	for thisPath in thisLayer.paths:
		for i, thisNode in enumerate(thisPath.nodes):
			if thisNode.type == GSCURVE:
				pointA = thisNode.position
				pointB = thisPath.nodes[ (i-1)%len(thisPath.nodes) ].position
				pointC = thisPath.nodes[ (i-2)%len(thisPath.nodes) ].position
				pointD = thisPath.nodes[ (i-3)%len(thisPath.nodes) ].position
				intersection = intersect( pointA, pointB, pointC, pointD )
				if intersection:
					firstHandleTooLong = distance(pointA,pointB) > distance(pointA,intersection)
					secondHandleTooLong = distance(pointD,pointC) > distance(pointD,intersection)
					if firstHandleTooLong or secondHandleTooLong:
						return True
	return False
		
def hasOutwardHandles( thisLayer ):
	for thisPath in thisLayer.paths:
		for i, thisNode in enumerate(thisPath.nodes):
			if thisNode.type == GSCURVE:
				pointA = thisNode.position
				pointB = thisPath.nodes[ (i-1)%len(thisPath.nodes) ].position
				pointC = thisPath.nodes[ (i-2)%len(thisPath.nodes) ].position
				pointD = thisPath.nodes[ (i-3)%len(thisPath.nodes) ].position
				if isOutside(pointA, pointD, pointB) or isOutside(pointA, pointD, pointC):
					return True
	return False
	
def isOutside(p1,p2,p3, threshold=0.6):
	"""
	Returns True if p3 is outside p1-p2.
	"""
	deviation, nx = distanceAndRelativePosition(p1,p2,p3)
	if nx < 0.0 or nx > 1.0:
		return True
	return False

def distanceAndRelativePosition(p1,p2,p3):
	"""
	Returns:
	1. distance from p3 to nearest point of p1-p2
	2. relative position (0...1) of p3 between p1 & p2
	"""
	x1,y1 = p1.x,p1.y
	x2,y2 = p2.x,p2.y
	x3,y3 = p3.x,p3.y

	dx = x2 - x1
	dy = y2 - y1
	d2 = dx*dx + dy*dy
	try:
		nx = ((x3-x1)*dx + (y3-y1)*dy) / d2
	except:
		# division by zero
		nx = 0.0

	deviation = distance(p3, NSPoint(dx*nx + x1, dy*nx + y1))
	return deviation, nx

class PathProblemFinder( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 320
		windowHeight = 450
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Path Problem Finder", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.PathProblemFinder.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		indent = 155
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"New tab with layers containing path problems:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.zeroHandles = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Zero handles", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.zeroHandles.getNSButton().setToolTip_(u"Zero handles (a.k.a. half-dead curves) can cause problems with screen rendering, hinting and interpolation. Indicated with purple disks in the Show Angled Handles plug-in.")
		linePos += lineHeight
		
		self.w.outwardHandles = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Outward-bent handles", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.outwardHandles.getNSButton().setToolTip_(u"Will find handles that point outside the stretch of their enclosing on-curves. Usually unwanted.")
		linePos += lineHeight
		
		self.w.largeHandles = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Overshooting handles (larger than 100%)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.largeHandles.getNSButton().setToolTip_(u"Handles that are longer than 100%, i.e. going beyond the intersection with the opposing handle. Indicated with laser beams in the Show Angled Handles plug-in.")
		linePos += lineHeight
		
		self.w.shortHandles = vanilla.CheckBox( (inset, linePos, indent, 20), u"Handles shorter than:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.shortHandlesThreshold = vanilla.EditText( (inset+indent, linePos, -inset-55, 19), "12", callback=self.SavePreferences, sizeStyle='small' )
		self.w.shortHandlesText = vanilla.TextBox( (-inset-50, linePos+2, -inset, 14), u"units", sizeStyle='small', selectable=True )
		tooltipText = u"Will find handles shorter than the specified amount in units. Short handles may cause kinks when rounded to the grid."
		self.w.shortHandlesThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.shortHandles.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight
		
		self.w.angledHandles = vanilla.CheckBox( (inset, linePos, indent, 20), u"Angled handles up to:", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.angledHandlesAngle = vanilla.EditText( (inset+indent, linePos, -inset-55, 19), "8", callback=self.SavePreferences, sizeStyle='small' )
		self.w.angledHandlesText = vanilla.TextBox( (-inset-50, linePos+2, -inset, 14), u"degrees", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.shallowCurveBBox = vanilla.CheckBox( (inset, linePos, indent, 20), u"Curve bbox smaller than:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.shallowCurveBBoxThreshold = vanilla.EditText( (inset+indent, linePos, -inset-55, 19), "10", sizeStyle='small' )
		self.w.shallowCurveBBoxText = vanilla.TextBox( (-inset-50, linePos+2, -inset, 14), u"units", sizeStyle='small', selectable=True )
		tooltipText = u"Will find very flat curve segments. Flat curves leave little manœuvring space for handles (BCPs), or cause very short handles, which in turn causes grid rounding problems. Can usually be fixed by removing an extremum point or adding an overlap."
		self.w.shallowCurveBBoxThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.shallowCurveBBox.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight
		
		self.w.shallowCurve = vanilla.CheckBox( (inset, linePos, indent, 20), u"Curves shallower than:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.shallowCurveThreshold = vanilla.EditText( (inset+indent, linePos, -inset-55, 19), "5", sizeStyle='small' )
		self.w.shallowCurveText = vanilla.TextBox( (-inset-50, linePos+2, -inset, 14), u"units", sizeStyle='small', selectable=True )
		tooltipText = u"Finds curve segments where the handles deviate less than the specified threshold from the enclosing on-curves."
		self.w.shallowCurveThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.shallowCurve.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight
		
		self.w.almostOrthogonalLines = vanilla.CheckBox( (inset, linePos, indent, 20), u"Non-orthogonal lines:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.almostOrthogonalLinesThreshold = vanilla.EditText( (inset+indent, linePos, -inset-75, 19), "3", callback=self.SavePreferences, sizeStyle='small' )
		self.w.almostOrthogonalLinesText = vanilla.TextBox( (-inset-70, linePos+2, -inset, 14), u"units deep", sizeStyle='small', selectable=True )
		tooltipText = u"Will find line segments that are close to, but not completely horizontal or vertical. Will look for segments where the x or y distance between the two nodes is less than the specified threshold. Often unintentional."
		self.w.almostOrthogonalLinesThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.almostOrthogonalLines.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight
		
		self.w.badOutlineOrder = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Bad outline order", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.badOutlineOrder.getNSButton().setToolTip_(u"If the first path is clockwise, paths are most likely in the wrong order.")
		linePos += lineHeight
		
		self.w.twoPointOutlines = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Paths with two on-curve nodes only", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.twoPointOutlines.getNSButton().setToolTip_(u"Paths with only two on-curve nodes are most likely leftover debris from a previous operation.")
		linePos += lineHeight
		
		self.w.offcurveAsStartPoint = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Off-curve point (handle) as startpoint", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.offcurveAsStartPoint.getNSButton().setToolTip_(u"Finds paths where the first point happens to be a BCP. Not really an issue, but you’ll like it if you are going full OCD on your font.")
		linePos += lineHeight
		
		self.w.openPaths = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Open paths (except _corner, _cap, etc.)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.openPaths.getNSButton().setToolTip_(u"Finds unclosed paths. Special glyphs that are supposed to have open paths, like corner and cap components, are ignored.")
		linePos += lineHeight
		
		self.w.line = vanilla.HorizontalLine( (inset, linePos+3, -inset, 1))
		linePos += int(lineHeight/2)
		
		# Script Options:
		self.w.includeAllGlyphs = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Check complete font (i.e., ignore glyph selection)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeAllGlyphs.getNSButton().setToolTip_(u"If enabled, will ignore your current (glyph) selection, and simply go through the complete font. Recommended. May still ignore non-exporting glyph, see following option.")
		linePos += lineHeight
		
		self.w.includeNonExporting = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Include non-exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeNonExporting.getNSButton().setToolTip_(u"If disabled, will ignore glyphs that are set to not export.")
		linePos += lineHeight
		
		self.w.reuseTab = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Reuse existing tab", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reuseTab.getNSButton().setToolTip_(u"If enabled, will only open a new tab if none is open. Recommended.")
		linePos += lineHeight
		
		# Progress Bar and Status text:
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		self.w.status = vanilla.TextBox( (inset, -18-inset, -inset-100, 14), u"🤖 Ready.", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-100-inset, -20-inset, -inset, -inset), "Open Tab", sizeStyle='regular', callback=self.PathProblemFinderMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Path Problem Finder' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def updateUI(self, sender=None):
		self.w.shallowCurveThreshold.enable( self.w.shallowCurve.get() )
		self.w.shallowCurveBBoxThreshold.enable( self.w.shallowCurveBBox.get() )
		self.w.almostOrthogonalLinesThreshold.enable( self.w.almostOrthogonalLines.get() )
		self.w.shortHandlesThreshold.enable( self.w.shortHandles.get() )
		self.w.angledHandlesAngle.enable( self.w.angledHandles.get() )
		
		anyOptionIsOn = (
			self.w.zeroHandles.get() or 
			self.w.outwardHandles.get() or 
			self.w.largeHandles.get() or 
			self.w.shortHandles.get() or 
			self.w.angledHandles.get() or 
			self.w.shallowCurveBBox.get() or 
			self.w.shallowCurve.get() or 
			self.w.almostOrthogonalLines.get() or 
			self.w.badOutlineOrder.get() or 
			self.w.twoPointOutlines.get() or 
			self.w.offcurveAsStartPoint.get() or 
			self.w.openPaths.get()
		)
		self.w.runButton.enable(anyOptionIsOn)
		
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.PathProblemFinder.zeroHandles"] = self.w.zeroHandles.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.outwardHandles"] = self.w.outwardHandles.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.largeHandles"] = self.w.largeHandles.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.shortHandles"] = self.w.shortHandles.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.shortHandlesThreshold"] = self.w.shortHandlesThreshold.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.angledHandles"] = self.w.angledHandles.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.angledHandlesAngle"] = self.w.angledHandlesAngle.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.shallowCurveBBox"] = self.w.shallowCurveBBox.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.shallowCurveBBoxThreshold"] = self.w.shallowCurveBBoxThreshold.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.shallowCurve"] = self.w.shallowCurve.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.shallowCurveThreshold"] = self.w.shallowCurveThreshold.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.almostOrthogonalLines"] = self.w.almostOrthogonalLines.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.almostOrthogonalLinesThreshold"] = self.w.almostOrthogonalLinesThreshold.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.badOutlineOrder"] = self.w.badOutlineOrder.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.twoPointOutlines"] = self.w.twoPointOutlines.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.offcurveAsStartPoint"] = self.w.offcurveAsStartPoint.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.openPaths"] = self.w.openPaths.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.includeAllGlyphs"] = self.w.includeAllGlyphs.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.includeNonExporting"] = self.w.includeNonExporting.get()
			Glyphs.defaults["com.mekkablue.PathProblemFinder.reuseTab"] = self.w.reuseTab.get()
			
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.zeroHandles", 1)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.outwardHandles", 1)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.largeHandles", 1)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.shortHandles", 1)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.shortHandlesThreshold", 12)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.angledHandles", 1)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.angledHandlesAngle", 8)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.shallowCurveBBox", 1)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.shallowCurveBBoxThreshold", 5)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.shallowCurve", 1)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.shallowCurveThreshold", 10)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.almostOrthogonalLines", 1)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.almostOrthogonalLinesThreshold", 3)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.badOutlineOrder", 1)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.twoPointOutlines", 1)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.offcurveAsStartPoint", 1)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.openPaths", 1)
			
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.includeAllGlyphs", 1)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.includeNonExporting", 0)
			Glyphs.registerDefault("com.mekkablue.PathProblemFinder.reuseTab", 1)
			
			
			# load previously written prefs:
			self.w.zeroHandles.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.zeroHandles"] )
			self.w.outwardHandles.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.outwardHandles"] )
			self.w.largeHandles.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.largeHandles"] )
			self.w.shortHandles.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.shortHandles"] )
			self.w.shortHandlesThreshold.set( float(Glyphs.defaults["com.mekkablue.PathProblemFinder.shortHandlesThreshold"]) )
			self.w.angledHandles.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.angledHandles"] )
			self.w.angledHandlesAngle.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.angledHandlesAngle"] )
			self.w.shallowCurveBBox.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.shallowCurveBBox"] )
			self.w.shallowCurveBBoxThreshold.set( float(Glyphs.defaults["com.mekkablue.PathProblemFinder.shallowCurveBBoxThreshold"]) )
			self.w.shallowCurve.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.shallowCurve"] )
			self.w.shallowCurveThreshold.set( float(Glyphs.defaults["com.mekkablue.PathProblemFinder.shallowCurveThreshold"]) )
			self.w.almostOrthogonalLines.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.almostOrthogonalLines"] )
			self.w.almostOrthogonalLinesThreshold.set( float(Glyphs.defaults["com.mekkablue.PathProblemFinder.almostOrthogonalLinesThreshold"]) )
			self.w.badOutlineOrder.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.badOutlineOrder"] )
			self.w.twoPointOutlines.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.twoPointOutlines"] )
			self.w.offcurveAsStartPoint.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.offcurveAsStartPoint"] )
			self.w.openPaths.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.openPaths"] )
			
			self.w.includeAllGlyphs.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.includeAllGlyphs"] )
			self.w.includeNonExporting.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.includeNonExporting"] )
			self.w.reuseTab.set( Glyphs.defaults["com.mekkablue.PathProblemFinder.reuseTab"] )
			
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def PathProblemFinderMain( self, sender ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Path Problem Finder' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if not thisFont:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Path Problem Finder Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
				
				# Query user settings:
				zeroHandles = Glyphs.defaults["com.mekkablue.PathProblemFinder.zeroHandles"]
				outwardHandles = Glyphs.defaults["com.mekkablue.PathProblemFinder.outwardHandles"]
				largeHandles = Glyphs.defaults["com.mekkablue.PathProblemFinder.largeHandles"]
				shortHandles = Glyphs.defaults["com.mekkablue.PathProblemFinder.shortHandles"]
				shortHandlesThreshold = Glyphs.defaults["com.mekkablue.PathProblemFinder.shortHandlesThreshold"]
				angledHandles = Glyphs.defaults["com.mekkablue.PathProblemFinder.angledHandles"]
				angledHandlesAngle = Glyphs.defaults["com.mekkablue.PathProblemFinder.angledHandlesAngle"]
				shallowCurve = Glyphs.defaults["com.mekkablue.PathProblemFinder.shallowCurve"]
				shallowCurveThreshold = Glyphs.defaults["com.mekkablue.PathProblemFinder.shallowCurveThreshold"]
				shallowCurveBBox = Glyphs.defaults["com.mekkablue.PathProblemFinder.shallowCurveBBox"]
				shallowCurveBBoxThreshold = Glyphs.defaults["com.mekkablue.PathProblemFinder.shallowCurveBBoxThreshold"]
				almostOrthogonalLines = Glyphs.defaults["com.mekkablue.PathProblemFinder.almostOrthogonalLines"]
				almostOrthogonalLinesThreshold = Glyphs.defaults["com.mekkablue.PathProblemFinder.almostOrthogonalLinesThreshold"]
				badOutlineOrder = Glyphs.defaults["com.mekkablue.PathProblemFinder.badOutlineOrder"]
				twoPointOutlines = Glyphs.defaults["com.mekkablue.PathProblemFinder.twoPointOutlines"]
				offcurveAsStartPoint = Glyphs.defaults["com.mekkablue.PathProblemFinder.offcurveAsStartPoint"]
				openPaths = Glyphs.defaults["com.mekkablue.PathProblemFinder.openPaths"]
				
				includeAllGlyphs = Glyphs.defaults["com.mekkablue.PathProblemFinder.includeAllGlyphs"]
				includeNonExporting = Glyphs.defaults["com.mekkablue.PathProblemFinder.includeNonExporting"]
				reuseTab = Glyphs.defaults["com.mekkablue.PathProblemFinder.reuseTab"]
				
				# determine the glyphs to work through:
				if includeAllGlyphs:
					glyphs = [g for g in thisFont.glyphs if includeNonExporting or g.export]
				else:
					glyphs = [l.parent for l in thisFont.selectedLayers]
				
				glyphCount = len(glyphs)
				print("Processing %i glyphs:" % glyphCount)
				
				layersWithZeroHandles = []
				layersWithZeroHandles = []
				layersWithOutwardHandles = []
				layersWithLargeHandles = []
				layersWithShortHandles = []
				layersWithAngledHandles = []
				layersWithShallowCurve = []
				layersWithShallowCurveBBox = []
				layersWithAlmostOrthogonalLines = []
				layersWithBadOutlineOrder = []
				layersWithOffcurveAsStartpoint = []
				layersWithTwoPointOutlines = []
				layersWithOpenPaths = []
				
				for i, thisGlyph in enumerate(glyphs):
					# status update:
					self.w.progress.set(100*i/glyphCount)
					self.w.status.set("Processing %s...\n" % thisGlyph.name)
					print("%i. %s" % (i+1,thisGlyph.name))
					
					# step through layers
					for thisLayer in thisGlyph.layers:
						if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
							
							if zeroHandles and hasZeroHandles(thisLayer):
								layersWithZeroHandles.append(thisLayer)
								print("  ❌ Zero handle(s) on layer: %s" % thisLayer.name)
								
							if outwardHandles and hasOutwardHandles(thisLayer):
								layersWithOutwardHandles.append(thisLayer)
								print("  ❌ Outward handle(s) on layer: %s" % thisLayer.name)
								
							if largeHandles and hasLargeHandles(thisLayer):
								layersWithLargeHandles.append(thisLayer)
								print("  ❌ Large handle(s) on layer: %s" % thisLayer.name)
								
							if shortHandles and hasShortHandles(thisLayer, threshold=float(shortHandlesThreshold)):
								layersWithShortHandles.append(thisLayer)
								print("  ❌ Short handle(s) on layer: %s" % thisLayer.name)
								
							if angledHandles and hasAngledHandles(thisLayer):
								layersWithAngledHandles.append(thisLayer)
								print("  ❌ Angled handle(s) on layer: %s" % thisLayer.name)
								
							if shallowCurve and hasShallowCurve(thisLayer, threshold=float(shallowCurveThreshold)):
								layersWithShallowCurve.append(thisLayer)
								print("  ❌ Shallow curve(s) on layer: %s" % thisLayer.name)
								
							if shallowCurveBBox and hasShallowCurveBBox(thisLayer, threshold=float(shallowCurveBBoxThreshold)):
								layersWithShallowCurveBBox.append(thisLayer)
								print("  ❌ Shallow curve bbox(es) on layer: %s" % thisLayer.name)
								
							if almostOrthogonalLines and hasAlmostOrthogonalLines(thisLayer, threshold=float(almostOrthogonalLinesThreshold)):
								layersWithAlmostOrthogonalLines.append(thisLayer)
								print("  ❌ Almost orthogonal line(s) on layer: %s" % thisLayer.name)
								
							if badOutlineOrder and hasBadOutlineOrder(thisLayer):
								layersWithBadOutlineOrder.append(thisLayer)
								print("  ❌ Bad outline order(s) on layer: %s" % thisLayer.name)
								
							if twoPointOutlines and hasTwoPointOutlines(thisLayer):
								layersWithTwoPointOutlines.append(thisLayer)
								print("  ❌ Two-point outline(s) on layer: %s" % thisLayer.name)

							if offcurveAsStartPoint and hasOffcurveAsStartPoint(thisLayer):
								layersWithOffcurveAsStartpoint.append(thisLayer)
								print("  ❌ Off-curve as start point on layer: %s" % thisLayer.name)
								
							if openPaths:
								shouldProcess = True
								for nameStart in canHaveOpenOutlines:
									if nameStart in thisGlyph.name:
										shouldProcess = False
								if shouldProcess and hasOpenPaths(thisLayer):
									layersWithOpenPaths.append(thisLayer)
									print("  ❌ Open path(s) on layer: %s" % thisLayer.name)
								
			self.w.status.set("Building report…")
	
			if layersWithZeroHandles or layersWithOutwardHandles or layersWithLargeHandles or layersWithShortHandles or layersWithAngledHandles or layersWithShallowCurve or layersWithShallowCurveBBox or layersWithAlmostOrthogonalLines or layersWithBadOutlineOrder or layersWithTwoPointOutlines or layersWithOpenPaths:
				countOfLayers = 0
				tab = thisFont.currentTab
				if not tab or not reuseTab:
					# opens new Edit tab:
					tab = thisFont.newTab()
				else:
					tab.text = "\n"
				
				countOfLayers += self.reportInTabAndMacroWindow(layersWithZeroHandles, "Zero Handles", tab, thisFont)
				countOfLayers += self.reportInTabAndMacroWindow(layersWithOutwardHandles, "Outward Handles", tab, thisFont)
				countOfLayers += self.reportInTabAndMacroWindow(layersWithLargeHandles, "Large Handles", tab, thisFont)
				countOfLayers += self.reportInTabAndMacroWindow(layersWithShortHandles, "Short Handles", tab, thisFont)
				countOfLayers += self.reportInTabAndMacroWindow(layersWithAngledHandles, "Angled Handles", tab, thisFont)
				countOfLayers += self.reportInTabAndMacroWindow(layersWithShallowCurve, "Shallow Curve", tab, thisFont)
				countOfLayers += self.reportInTabAndMacroWindow(layersWithShallowCurveBBox, "Small Curve BBox", tab, thisFont)
				countOfLayers += self.reportInTabAndMacroWindow(layersWithAlmostOrthogonalLines, "Almost Orthogonal Lines", tab, thisFont)
				countOfLayers += self.reportInTabAndMacroWindow(layersWithBadOutlineOrder, "Bad Outline Order or Orientation", tab, thisFont)
				countOfLayers += self.reportInTabAndMacroWindow(layersWithTwoPointOutlines, "Two-Point Outlines", tab, thisFont)
				countOfLayers += self.reportInTabAndMacroWindow(layersWithOffcurveAsStartpoint, "Two-Point Outlines", tab, thisFont)
				countOfLayers += self.reportInTabAndMacroWindow(layersWithOpenPaths, "Open Paths", tab, thisFont)
				
				Glyphs.showNotification( 
					u"%s: found path problems" % (thisFont.familyName),
					u"Path Problem Finder found issues on %i layers. Details in Macro Window." % countOfLayers,
					)
				
			else:
				# Final report:
				Glyphs.showNotification( 
					u"%s: all clear!" % (thisFont.familyName),
					u"Path Problem Finder found no issues, congratulations! Details in Macro Window."
					)

			self.w.progress.set(100)
			self.w.status.set("✅ Done.")
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Path Problem Finder Error: %s" % e)
			import traceback
			print(traceback.format_exc())
			
			
	def reportInTabAndMacroWindow(self, layerList, title, tab, font):
		if layerList and font:
			
			# determine master ID:
			currentMaster = font.masters[tab.masterIndex]
			masterID = currentMaster.id
			
			# report in Tab:
			tabtext = "%s:"%title
			# split description into layers, so we do not use layers
			# (simply adding to tab.text will reset all layers to the current master)
			for letter in tabtext:
				g = font.glyphs[letter]
				if g:
					l = g.layers[masterID]
					if l:
						tab.layers.append(l)
			tab.layers.append(GSControlLayer.newline())
			for layer in layerList:
				tab.layers.append(layer)
			for i in range(2):
				tab.layers.append(GSControlLayer.newline())
			
			# report in Macro Window:
			print(
				"\n🔠 %s:\n%s" % (
					title,
					"/"+"/".join(set([l.parent.name for l in layerList]))
				))
		return len(layerList)
		
		
PathProblemFinder()