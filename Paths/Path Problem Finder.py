#MenuTitle: Path Problem Finder
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Finds all kinds of potential problems in outlines, and opens a new tab with affected layers.
"""

import vanilla, math
from timeit import default_timer as timer
from GlyphsApp import QCURVE
from AppKit import NSPoint

def reportTimeInNaturalLanguage( seconds ):
	if seconds > 60.0:
		timereport = "%i:%02i minutes" % ( seconds//60, seconds%60 )
	elif seconds < 1.0:
		timereport = "%.2f seconds" % seconds
	elif seconds < 20.0:
		timereport = "%.1f seconds" % seconds
	else:
		timereport = "%i seconds" % seconds
	return timereport

canHaveOpenOutlines = (
	"_cap",
	"_corner",
	"_line",
	"_segment",
)

def hasStrayPoints( thisLayer ):
	for p in thisLayer.paths:
		if len(p.nodes) == 1:
			return True
	return False

def hasDecimalCoordinates( thisLayer ):
	for p in thisLayer.paths:
		for n in p.nodes:
			for coord in (n.x, n.y):
				if coord%1.0 != 0.0:
					return True
	return False
	
def hasQuadraticCurves( thisLayer ):
	for p in thisLayer.paths:
		for n in p.nodes:
			if n.type is QCURVE:
				return True
	return False

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
	firstPath = None
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		if thisLayer.shapes:
			for thisShape in thisLayer.shapes:
				if type(thisShape) is GSPath:
					firstPath = thisShape
					break
	else:
		# GLYPHS 2
		if thisLayer.paths:
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

def hasShortLine( thisLayer, threshold=8.0 ):
	for thisPath in thisLayer.paths:
		for i, thisNode in enumerate(thisPath.nodes):
			if thisNode.type == GSLINE:
				pointA = thisNode.position
				pointB = thisPath.nodes[ (i-1)%len(thisPath.nodes) ].position
				if distance(pointA, pointB) < threshold:
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

def hasBadPathDirections( thisLayer ):
	copyLayer = thisLayer.__copy__()
	copyLayer.correctPathDirection()
	for i in range(len(copyLayer.paths)):
		originalPath = thisLayer.paths[i]
		copyPath = copyLayer.paths[i]
		if copyPath.direction != originalPath.direction:
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
	prefID = "com.mekkablue.PathProblemFinder"
	title = "Path Problem Finder"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 560
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			self.title, # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		indent = 170
		self.w.descriptionText = vanilla.TextBox( (inset, linePos, -inset, 14), "New tab with layers containing path problems:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.zeroHandles = vanilla.CheckBox( (inset, linePos, -inset, 20), "Zero handles", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.zeroHandles.getNSButton().setToolTip_("Zero handles (a.k.a. half-dead curves) can cause problems with screen rendering, hinting and interpolation. Indicated with purple disks in the Show Angled Handles plug-in.")
		linePos += lineHeight
		
		self.w.outwardHandles = vanilla.CheckBox( (inset, linePos, -inset, 20), "Outward-bent handles", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.outwardHandles.getNSButton().setToolTip_("Will find handles that point outside the stretch of their enclosing on-curves. Usually unwanted.")
		linePos += lineHeight
		
		self.w.largeHandles = vanilla.CheckBox( (inset, linePos, -inset, 20), "Overshooting handles (larger than 100%)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.largeHandles.getNSButton().setToolTip_("Handles that are longer than 100%, i.e. going beyond the intersection with the opposing handle. Indicated with laser beams in the Show Angled Handles plug-in.")
		linePos += lineHeight
		
		self.w.shortHandles = vanilla.CheckBox( (inset, linePos, indent, 20), "Handles shorter than:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.shortHandlesThreshold = vanilla.EditText( (inset+indent, linePos, -inset-65, 19), "12", callback=self.SavePreferences, sizeStyle='small' )
		self.w.shortHandlesText = vanilla.TextBox( (-inset-60, linePos+3, -inset, 14), "units", sizeStyle='small', selectable=True )
		tooltipText = "Will find handles shorter than the specified amount in units. Short handles may cause kinks when rounded to the grid."
		self.w.shortHandlesThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.shortHandles.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight
		
		self.w.angledHandles = vanilla.CheckBox( (inset, linePos, indent, 20), "Angled handles up to:", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.angledHandlesAngle = vanilla.EditText( (inset+indent, linePos, -inset-65, 19), "8", callback=self.SavePreferences, sizeStyle='small' )
		self.w.angledHandlesText = vanilla.TextBox( (-inset-60, linePos+3, -inset, 14), "degrees", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.shallowCurveBBox = vanilla.CheckBox( (inset, linePos, indent, 20), "Curve bbox smaller than:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.shallowCurveBBoxThreshold = vanilla.EditText( (inset+indent, linePos, -inset-65, 19), "10", sizeStyle='small' )
		self.w.shallowCurveBBoxText = vanilla.TextBox( (-inset-60, linePos+3, -inset, 14), "units", sizeStyle='small', selectable=True )
		tooltipText = "Will find very flat curve segments. Flat curves leave little manœuvring space for handles (BCPs), or cause very short handles, which in turn causes grid rounding problems. Can usually be fixed by removing an extremum point or adding an overlap."
		self.w.shallowCurveBBoxThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.shallowCurveBBox.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight
		
		self.w.shallowCurve = vanilla.CheckBox( (inset, linePos, indent, 20), "Curves shallower than:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.shallowCurveThreshold = vanilla.EditText( (inset+indent, linePos, -inset-65, 19), "5", sizeStyle='small' )
		self.w.shallowCurveText = vanilla.TextBox( (-inset-60, linePos+3, -inset, 14), "units", sizeStyle='small', selectable=True )
		tooltipText = "Finds curve segments where the handles deviate less than the specified threshold from the enclosing on-curves."
		self.w.shallowCurveThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.shallowCurve.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight
		
		self.w.shortLine = vanilla.CheckBox( (inset, linePos, indent, 20), "Line segments shorter than:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.shortLineThreshold = vanilla.EditText( (inset+indent, linePos, -inset-65, 19), "8", sizeStyle='small' )
		self.w.shortLineText = vanilla.TextBox( (-inset-60, linePos+3, -inset, 14), "units", sizeStyle='small', selectable=True )
		tooltipText = "Finds line segments (two consecutive on-curve nodes) shorter than the specified threshold length. Very short line segments may be deleted because they are barely visible. Also, if not orthogonal, may pose grid rounding problems."
		self.w.shortLineThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.shortLine.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight
		
		self.w.almostOrthogonalLines = vanilla.CheckBox( (inset, linePos, indent, 20), "Non-orthogonal lines:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.almostOrthogonalLinesThreshold = vanilla.EditText( (inset+indent, linePos, -inset-65, 19), "3", callback=self.SavePreferences, sizeStyle='small' )
		self.w.almostOrthogonalLinesText = vanilla.TextBox( (-inset-60, linePos+3, -inset, 14), "units deep", sizeStyle='small', selectable=True )
		tooltipText = "Will find line segments that are close to, but not completely horizontal or vertical. Will look for segments where the x or y distance between the two nodes is less than the specified threshold. Often unintentional."
		self.w.almostOrthogonalLinesThreshold.getNSTextField().setToolTip_(tooltipText)
		self.w.almostOrthogonalLines.getNSButton().setToolTip_(tooltipText)
		linePos += lineHeight
		
		self.w.badOutlineOrder = vanilla.CheckBox( (inset, linePos, -inset, 20), "Bad outline order", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.badOutlineOrder.getNSButton().setToolTip_("If the first path is clockwise, paths are most likely in the wrong order.")
		linePos += lineHeight
		
		self.w.badPathDirections = vanilla.CheckBox( (inset, linePos, -inset, 20), "Bad path directions", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.badPathDirections.getNSButton().setToolTip_("Tries to find paths that have the wrong orientation.")
		linePos += lineHeight
		
		self.w.strayPoints = vanilla.CheckBox( (inset, linePos, -inset, 20), "Stray points (single-node paths)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.strayPoints.getNSButton().setToolTip_("In Glyphs 1, paths with only one node (‘stray points’) used to be a method for disabling auto-alignment of components. But they are probably a mistake. Can be fixed wth mekkablue script Paths > Remove Stray Points.")
		linePos += lineHeight
		
		self.w.twoPointOutlines = vanilla.CheckBox( (inset, linePos, -inset, 20), "Paths with two on-curve nodes only", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.twoPointOutlines.getNSButton().setToolTip_("Paths with only two on-curve nodes are most likely leftover debris from a previous operation.")
		linePos += lineHeight
		
		self.w.offcurveAsStartPoint = vanilla.CheckBox( (inset, linePos, -inset, 20), "Off-curve point (handle) as startpoint", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.offcurveAsStartPoint.getNSButton().setToolTip_("Finds paths where the first point happens to be a BCP. Not really an issue, but you’ll like it if you are going full OCD on your font.")
		linePos += lineHeight
		
		self.w.openPaths = vanilla.CheckBox( (inset, linePos, -inset, 20), "Open paths (except _corner, _cap, etc.)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.openPaths.getNSButton().setToolTip_("Finds unclosed paths. Special glyphs that are supposed to have open paths, like corner and cap components, are ignored.")
		linePos += lineHeight
		
		self.w.quadraticCurves = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Quadratic Curves", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.quadraticCurves.getNSButton().setToolTip_("Finds quadratic (TrueType) curves. Useful if quadratic curves were not intended.")
		linePos += lineHeight
		
		self.w.decimalCoordinates = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Decimal point coordinates", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.decimalCoordinates.getNSButton().setToolTip_("Nodes and handles with decimal coordinates, i.e., points not exactly on the unit grid.")
		linePos += lineHeight
		
		
		# Line Separator:
		
		self.w.line = vanilla.HorizontalLine( (inset, linePos+3, -inset, 1))
		linePos += int(lineHeight/2)
		
		# Script Options:
		self.w.includeAllGlyphs = vanilla.CheckBox( (inset, linePos, -inset, 20), "⚠️ Check all glyphs, ignore selection (slow)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeAllGlyphs.getNSButton().setToolTip_("If enabled, will ignore your current (glyph) selection, and simply go through the complete font. Recommended. May still ignore non-exporting glyph, see following option.")
		linePos += lineHeight
		
		self.w.includeNonExporting = vanilla.CheckBox( (inset, linePos, -inset, 20), "Include non-exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeNonExporting.getNSButton().setToolTip_("If disabled, will ignore glyphs that are set to not export.")
		linePos += lineHeight
		
		self.w.reuseTab = vanilla.CheckBox( (inset, linePos, 125, 20), "Reuse existing tab", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reuseTab.getNSButton().setToolTip_("If enabled, will only open a new tab if none is open. Recommended.")
		linePos += lineHeight
		
		# Progress Bar and Status text:
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		self.w.status = vanilla.TextBox( (inset, -18-inset, -inset-100, 14), "🤖 Ready.", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-100-inset, -20-inset, -inset, -inset), "Open Tab", sizeStyle='regular', callback=self.PathProblemFinderMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: '%s' could not load preferences. Will resort to defaults" % self.title)
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def updateUI(self, sender=None):
		self.w.shallowCurveThreshold.enable( self.w.shallowCurve.get() )
		self.w.shallowCurveBBoxThreshold.enable( self.w.shallowCurveBBox.get() )
		self.w.almostOrthogonalLinesThreshold.enable( self.w.almostOrthogonalLines.get() )
		self.w.shortHandlesThreshold.enable( self.w.shortHandles.get() )
		self.w.angledHandlesAngle.enable( self.w.angledHandles.get() )
		self.w.shortLineThreshold.enable( self.w.shortLine.get() )
		
		anyOptionIsOn = (
			self.w.zeroHandles.get() or 
			self.w.outwardHandles.get() or 
			self.w.largeHandles.get() or 
			self.w.shortHandles.get() or 
			self.w.angledHandles.get() or 
			self.w.shallowCurveBBox.get() or 
			self.w.shallowCurve.get() or 
			self.w.shortLine.get() or
			self.w.almostOrthogonalLines.get() or 
			self.w.badOutlineOrder.get() or 
			self.w.badPathDirections.get() or 
			self.w.strayPoints.get() or
			self.w.twoPointOutlines.get() or 
			self.w.offcurveAsStartPoint.get() or 
			self.w.openPaths.get() or
			self.w.quadraticCurves.get() or
			self.w.decimalCoordinates.get()
		)
		self.w.runButton.enable(anyOptionIsOn)
		
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults[self.domain("zeroHandles")] = self.w.zeroHandles.get()
			Glyphs.defaults[self.domain("outwardHandles")] = self.w.outwardHandles.get()
			Glyphs.defaults[self.domain("largeHandles")] = self.w.largeHandles.get()
			Glyphs.defaults[self.domain("shortHandles")] = self.w.shortHandles.get()
			Glyphs.defaults[self.domain("shortHandlesThreshold")] = self.w.shortHandlesThreshold.get()
			Glyphs.defaults[self.domain("angledHandles")] = self.w.angledHandles.get()
			Glyphs.defaults[self.domain("angledHandlesAngle")] = self.w.angledHandlesAngle.get()
			Glyphs.defaults[self.domain("shallowCurveBBox")] = self.w.shallowCurveBBox.get()
			Glyphs.defaults[self.domain("shallowCurveBBoxThreshold")] = self.w.shallowCurveBBoxThreshold.get()
			Glyphs.defaults[self.domain("shallowCurve")] = self.w.shallowCurve.get()
			Glyphs.defaults[self.domain("shallowCurveThreshold")] = self.w.shallowCurveThreshold.get()
			Glyphs.defaults[self.domain("almostOrthogonalLines")] = self.w.almostOrthogonalLines.get()
			Glyphs.defaults[self.domain("almostOrthogonalLinesThreshold")] = self.w.almostOrthogonalLinesThreshold.get()
			Glyphs.defaults[self.domain("shortLine")] = self.w.shortLine.get()
			Glyphs.defaults[self.domain("shortLineThreshold")] = self.w.shortLineThreshold.get()
			Glyphs.defaults[self.domain("badOutlineOrder")] = self.w.badOutlineOrder.get()
			Glyphs.defaults[self.domain("badPathDirections")] = self.w.badPathDirections.get()
			Glyphs.defaults[self.domain("strayPoints")] = self.w.strayPoints.get()
			Glyphs.defaults[self.domain("twoPointOutlines")] = self.w.twoPointOutlines.get()
			Glyphs.defaults[self.domain("offcurveAsStartPoint")] = self.w.offcurveAsStartPoint.get()
			Glyphs.defaults[self.domain("openPaths")] = self.w.openPaths.get()
			Glyphs.defaults[self.domain("quadraticCurves")] = self.w.quadraticCurves.get()
			Glyphs.defaults[self.domain("decimalCoordinates")] = self.w.decimalCoordinates.get()
			Glyphs.defaults[self.domain("includeAllGlyphs")] = self.w.includeAllGlyphs.get()
			Glyphs.defaults[self.domain("includeNonExporting")] = self.w.includeNonExporting.get()
			Glyphs.defaults[self.domain("reuseTab")] = self.w.reuseTab.get()
			
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault(self.domain("zeroHandles"), 1)
			Glyphs.registerDefault(self.domain("outwardHandles"), 1)
			Glyphs.registerDefault(self.domain("largeHandles"), 1)
			Glyphs.registerDefault(self.domain("shortHandles"), 1)
			Glyphs.registerDefault(self.domain("shortHandlesThreshold"), 12)
			Glyphs.registerDefault(self.domain("angledHandles"), 1)
			Glyphs.registerDefault(self.domain("angledHandlesAngle"), 8)
			Glyphs.registerDefault(self.domain("shallowCurveBBox"), 1)
			Glyphs.registerDefault(self.domain("shallowCurveBBoxThreshold"), 5)
			Glyphs.registerDefault(self.domain("shallowCurve"), 1)
			Glyphs.registerDefault(self.domain("shallowCurveThreshold"), 10)
			Glyphs.registerDefault(self.domain("almostOrthogonalLines"), 1)
			Glyphs.registerDefault(self.domain("almostOrthogonalLinesThreshold"), 3)
			Glyphs.registerDefault(self.domain("shortLine"), 0)
			Glyphs.registerDefault(self.domain("shortLineThreshold"), 8)
			Glyphs.registerDefault(self.domain("badOutlineOrder"), 1)
			Glyphs.registerDefault(self.domain("badPathDirections"), 1)
			Glyphs.registerDefault(self.domain("strayPoints"), 1)
			Glyphs.registerDefault(self.domain("twoPointOutlines"), 1)
			Glyphs.registerDefault(self.domain("offcurveAsStartPoint"), 1)
			Glyphs.registerDefault(self.domain("openPaths"), 1)
			Glyphs.registerDefault(self.domain("quadraticCurves"), 0)
			Glyphs.registerDefault(self.domain("decimalCoordinates"), 0)
			Glyphs.registerDefault(self.domain("includeAllGlyphs"), 1)
			Glyphs.registerDefault(self.domain("includeNonExporting"), 0)
			Glyphs.registerDefault(self.domain("reuseTab"), 1)
			
			# load previously written prefs:
			self.w.zeroHandles.set( self.pref("zeroHandles") )
			self.w.outwardHandles.set( self.pref("outwardHandles") )
			self.w.largeHandles.set( self.pref("largeHandles") )
			self.w.shortHandles.set( self.pref("shortHandles") )
			self.w.shortHandlesThreshold.set( float(self.pref("shortHandlesThreshold")) )
			self.w.angledHandles.set( self.pref("angledHandles") )
			self.w.angledHandlesAngle.set( self.pref("angledHandlesAngle") )
			self.w.shallowCurveBBox.set( self.pref("shallowCurveBBox") )
			self.w.shallowCurveBBoxThreshold.set( float(self.pref("shallowCurveBBoxThreshold")) )
			self.w.shallowCurve.set( self.pref("shallowCurve") )
			self.w.shallowCurveThreshold.set( float(self.pref("shallowCurveThreshold")) )
			self.w.almostOrthogonalLines.set( self.pref("almostOrthogonalLines") )
			self.w.almostOrthogonalLinesThreshold.set( float(self.pref("almostOrthogonalLinesThreshold")) )
			self.w.shortLine.set( self.pref("shortLine") )
			self.w.shortLineThreshold.set( float(self.pref("shortLineThreshold")) )
			self.w.badOutlineOrder.set( self.pref("badOutlineOrder") )
			self.w.badPathDirections.set( self.pref("badPathDirections") )
			self.w.strayPoints.set( self.pref("strayPoints") )
			self.w.twoPointOutlines.set( self.pref("twoPointOutlines") )
			self.w.offcurveAsStartPoint.set( self.pref("offcurveAsStartPoint") )
			self.w.openPaths.set( self.pref("openPaths") )
			self.w.quadraticCurves.set( self.pref("quadraticCurves") )
			self.w.decimalCoordinates.set( self.pref("decimalCoordinates") )
			self.w.includeAllGlyphs.set( self.pref("includeAllGlyphs") )
			self.w.includeNonExporting.set( self.pref("includeNonExporting") )
			self.w.reuseTab.set( self.pref("reuseTab") )
			
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
			
			# start taking time:
			start = timer()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: '%s' could not write preferences." % self.title)
			
			thisFont = Glyphs.font # frontmost font
			if not thisFont:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("%s Report for %s" % (self.title, thisFont.familyName))
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
				
				# Query user settings:
				zeroHandles = self.pref("zeroHandles")
				outwardHandles = self.pref("outwardHandles")
				largeHandles = self.pref("largeHandles")
				shortHandles = self.pref("shortHandles")
				shortHandlesThreshold = self.pref("shortHandlesThreshold")
				angledHandles = self.pref("angledHandles")
				angledHandlesAngle = self.pref("angledHandlesAngle")
				shallowCurve = self.pref("shallowCurve")
				shallowCurveThreshold = self.pref("shallowCurveThreshold")
				shallowCurveBBox = self.pref("shallowCurveBBox")
				shallowCurveBBoxThreshold = self.pref("shallowCurveBBoxThreshold")
				almostOrthogonalLines = self.pref("almostOrthogonalLines")
				almostOrthogonalLinesThreshold = self.pref("almostOrthogonalLinesThreshold")
				shortLine = self.pref("shortLine")
				shortLineThreshold = self.pref("shortLineThreshold")
				badOutlineOrder = self.pref("badOutlineOrder")
				badPathDirections = self.pref("badPathDirections")
				strayPoints = self.pref("strayPoints")
				twoPointOutlines = self.pref("twoPointOutlines")
				offcurveAsStartPoint = self.pref("offcurveAsStartPoint")
				openPaths = self.pref("openPaths")
				quadraticCurves = self.pref("quadraticCurves")
				decimalCoordinates = self.pref("decimalCoordinates")
				
				includeAllGlyphs = self.pref("includeAllGlyphs")
				includeNonExporting = self.pref("includeNonExporting")
				reuseTab = self.pref("reuseTab")
				
				# determine the glyphs to work through:
				if includeAllGlyphs:
					glyphs = [g for g in thisFont.glyphs if includeNonExporting or g.export]
				else:
					glyphs = [l.parent for l in thisFont.selectedLayers]
				
				glyphCount = len(glyphs)
				print("Processing %i glyphs:" % glyphCount)
				
				layersWithZeroHandles = []
				layersWithOutwardHandles = []
				layersWithLargeHandles = []
				layersWithShortHandles = []
				layersWithAngledHandles = []
				layersWithShallowCurve = []
				layersWithShallowCurveBBox = []
				layersWithAlmostOrthogonalLines = []
				layersWithShortLines = []
				layersWithBadOutlineOrder = []
				layersWithBadPathDirections = []
				layersWithOffcurveAsStartpoint = []
				layersWithStrayPoints = []
				layersWithTwoPointOutlines = []
				layersWithOpenPaths = []
				layersWithQuadraticCurves = []
				layersWithDecimalCoordinates = []
				
				progressSteps = glyphCount / 10
				progressCounter = 0
				for i, thisGlyph in enumerate(glyphs):
					# status update:
					if progressCounter > progressSteps:
						self.w.progress.set(100 * i / glyphCount)
						progressCounter = 0
					progressCounter += 1
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
								
							if shortLine and hasShortLine(thisLayer, threshold=float(shortLineThreshold)):
								layersWithShortLines.append(thisLayer)
								print("  ❌ Short line(s) on layer: %s" % thisLayer.name)
								
							if badOutlineOrder and hasBadOutlineOrder(thisLayer):
								layersWithBadOutlineOrder.append(thisLayer)
								print("  ❌ Bad outline order(s) on layer: %s" % thisLayer.name)
								
							if badPathDirections and hasBadPathDirections(thisLayer):
								layersWithBadPathDirections.append(thisLayer)
								print("  ❌ Bad path direction(s) on layer: %s" % thisLayer.name)
								
							if strayPoints and hasStrayPoints(thisLayer):
								layersWithStrayPoints.append(thisLayer)
								print("  ❌ Stray points on layer: %s" % thisLayer.name)
								
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
							
							if decimalCoordinates and hasDecimalCoordinates(thisLayer):
								layersWithDecimalCoordinates.append(thisLayer)
								print("  ❌ Decimal coordinates in layer: %s" % thisLayer.name)
							
							if quadraticCurves and hasQuadraticCurves(thisLayer):
								layersWithQuadraticCurves.append(thisLayer)
								print("  ❌ Quadratic curves in layer: %s" % thisLayer.name)
								
				# take time:
				end = timer()
				timereport = reportTimeInNaturalLanguage( end - start )
				print("\nTime for analysis: %s"%timereport)
				self.w.status.set("Building report…")
			
				anyIssueFound = (
					layersWithZeroHandles or
					layersWithOutwardHandles or
					layersWithLargeHandles or
					layersWithShortHandles or
					layersWithAngledHandles or
					layersWithShallowCurve or
					layersWithShallowCurveBBox or
					layersWithAlmostOrthogonalLines or
					layersWithShortLines or
					layersWithBadOutlineOrder or
					layersWithBadPathDirections or
					layersWithStrayPoints or
					layersWithTwoPointOutlines or
					layersWithOpenPaths or
					layersWithDecimalCoordinates or
					layersWithQuadraticCurves
				)
			
				if anyIssueFound:
					countOfLayers = 0
					tab = thisFont.currentTab
					if not tab or not reuseTab:
						# opens new Edit tab:
						tab = thisFont.newTab()
					tab.direction = 0 # force LTR
					layers = []
				
					currentMaster = thisFont.masters[tab.masterIndex]
					masterID = currentMaster.id
				
					countOfLayers += self.reportInTabAndMacroWindow(layersWithZeroHandles, "Zero Handles", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithOutwardHandles, "Outward Handles", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithLargeHandles, "Large Handles", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithShortHandles, "Short Handles", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithAngledHandles, "Angled Handles", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithShallowCurve, "Shallow Curve", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithShallowCurveBBox, "Small Curve BBox", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithAlmostOrthogonalLines, "Almost Orthogonal Lines", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithShortLines, "Short Line Segments", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithBadOutlineOrder, "Bad Outline Order", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithBadPathDirections, "Bad Path Orientation", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithStrayPoints, "Stray Points", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithTwoPointOutlines, "Two-Point Outlines", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithOffcurveAsStartpoint, "Off-curve as start point", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithOpenPaths, "Open Paths", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithQuadraticCurves, "Quadratic Curves", layers, thisFont, masterID)
					countOfLayers += self.reportInTabAndMacroWindow(layersWithDecimalCoordinates, "Decimal Coordinates", layers, thisFont, masterID)
				
					tab.layers = layers
				
					Glyphs.showNotification( 
						"%s: found path problems" % (thisFont.familyName),
						"%s found %i issues in %i glyphs. Details in Macro Window." % (self.title, countOfLayers, glyphCount),
						)
				else:
					# Final report:
					Glyphs.showNotification( 
						"%s: all clear!" % (thisFont.familyName),
						"%s found no issues, congratulations! Details in Macro Window." % self.title
						)

				self.w.progress.set(100)

				# take time:
				end = timer()
				timereport = reportTimeInNaturalLanguage( end - start )
			
				self.w.status.set("✅ Done. %s." % timereport)
				print("\nTotal time elapsed: %s.\nDone." % timereport)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("%s Error: %s" % (self.title, e))
			import traceback
			print(traceback.format_exc())
			
	def reportInTabAndMacroWindow(self, layerList, title, layers, font, masterID):
		if layerList and font:
			# report in Tab:
			tabtext = "%s:"%title
			
			# split description into layers, so we do not use layers
			# (simply adding to tab.text will reset all layers to the current master)
			for letter in tabtext:
				g = font.glyphs[letter]
				if g:
					l = g.layers[masterID]
					if l:
						layers.append(l)
			layers.append(GSControlLayer.newline())
			for layer in layerList:
				layers.append(layer)
			for i in range(2):
				layers.append(GSControlLayer.newline())
			
			# report in Macro Window:
			print(
				"\n🔠 %s:\n%s" % (
					title,
					"/"+"/".join(set([l.parent.name for l in layerList])),
				))
			
		return len(layerList)
		
PathProblemFinder()