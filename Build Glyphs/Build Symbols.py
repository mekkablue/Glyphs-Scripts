#MenuTitle: Build Symbols
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Creates an estimated glyph and draws an estimated sign in it. Does the same for bar and brokenbar, for which it respects standard stems and italic angle.
"""

# TODO: further abstraction of existing methods
# TODO: emptyset, currency, lozenge, product, summation, radical

from GlyphsApp import GSOFFCURVE, GSCURVE, GSSMOOTH
from Foundation import NSPoint, NSRect, NSSize, NSAffineTransform, NSAffineTransformStruct
import vanilla, math

def scaleLayerByFactor( thisLayer, scaleFactor ):
	"""
	Scales a layer by this factor.
	"""
	thisLayer.transform_checkForSelection_doComponents_(
		scaleMatrix(scaleFactor), False, True
	)

def scaleMatrix(scaleFactor):
	"""
	Returns a matrix for the scale factor,
	where 100% is represented as 1.0.
	"""
	scaleMatrix = ( scaleFactor, 0.0, 0.0, scaleFactor, 0.0, 0.0 )
	transformMatrix = transformFromMatrix( scaleMatrix )
	return transformMatrix

def transformFromMatrix( matrix ):
	"""
	Returns an NSAffineTransform based on the matrix supplied.
	Matrix needs to be a tuple of 6 floats.
	"""
	transformation = NSAffineTransform.transform()
	transformation.setTransformStruct_( matrix )
	return transformation

def circleInsideRect(rect):
	"""Returns a GSPath for a circle inscribed into the NSRect rect."""
	MAGICNUMBER = 4.0 * ( 2.0**0.5 - 1.0 ) / 3.0
	x = rect.origin.x
	y = rect.origin.y
	height = rect.size.height
	width = rect.size.width
	fullHeight = y+height
	fullWidth = x+width
	halfHeight = y + 0.5 * height
	halfWidth = x + 0.5 * width
	horHandle = width * 0.5 * MAGICNUMBER * 1.05
	verHandle = height * 0.5 * MAGICNUMBER * 1.05
	
	segments = (
		( NSPoint(x,halfHeight-verHandle), NSPoint(halfWidth-horHandle,y), NSPoint(halfWidth,y) ),
		( NSPoint(halfWidth+horHandle,y), NSPoint(fullWidth,halfHeight-verHandle), NSPoint(fullWidth,halfHeight) ),
		( NSPoint(fullWidth,halfHeight+verHandle), NSPoint(halfWidth+horHandle,fullHeight), NSPoint(halfWidth,fullHeight) ),
		( NSPoint(halfWidth-horHandle,fullHeight), NSPoint(x,halfHeight+verHandle), NSPoint(x,halfHeight) )
	)
	
	circlePath = GSPath()
	
	for thisSegment in segments:
		for i in range(3):
			nodeType = (GSOFFCURVE, GSOFFCURVE, GSCURVE)[i]
			nodePos = thisSegment[i]
			newNode = GSNode()
			newNode.position = nodePos
			newNode.type = nodeType
			newNode.connection = GSSMOOTH
			circlePath.nodes.append(newNode)

	# print(circlePath)
	# for n in circlePath.nodes:
	# 	print("   ", n)
	circlePath.closed = True
	return circlePath

def italicize( coords, italicAngle=0.0, pivotalY=0.0 ):
	"""
	Returns the italicized position of an NSPoint 'thisPoint'
	for a given angle 'italicAngle' and the pivotal height 'pivotalY',
	around which the italic slanting is executed, usually half x-height.
	Usage: myPoint = italicize(myPoint,10,xHeight*0.5)
	"""
	x = coords[0]
	y = coords[1]
	yOffset = y - pivotalY # calculate vertical offset
	italicAngle = math.radians( italicAngle ) # convert to radians
	tangens = math.tan( italicAngle ) # math.tan needs radians
	horizontalDeviance = tangens * yOffset # vertical distance from pivotal point
	x += horizontalDeviance # x of point that is yOffset from pivotal point
	return ( x, y )

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
		myTransform.translateXBy_yBy_(shiftX,shiftY)
	if skew:
		skewStruct = NSAffineTransformStruct()
		skewStruct.m11 = 1.0
		skewStruct.m22 = 1.0
		skewStruct.m21 = math.tan(math.radians(skew))
		skewTransform = NSAffineTransform.transform()
		skewTransform.setTransformStruct_(skewStruct)
		myTransform.appendTransform_(skewTransform)
	return myTransform

def isEmpty(layer):
	try:
		# GLYPHS 3:
		if layer.shapes:
			return False
		else:
			return True
	except:
		# GLYPHS 2:
		if layer.paths:
			return False
		elif layer.components:
			return False
		else:
			return True

def createGlyph(font, name, unicodeValue, override=False):
	glyph = font.glyphs[name]
	if not glyph:
		glyph = GSGlyph()
		glyph.name = name
		glyph.unicode = unicodeValue
		font.glyphs.append(glyph)
		glyph.updateGlyphInfo()
		return glyph
		
	else:
		if not override:
			print("Glyph %s already exists. No override chosen. Skipping." % name)
			return None
		
		else:
			print("Overwriting existing glyph %s." % name)
			
			# create backups of layers:
			backupLayers = []
			for layer in glyph.layers:
				if layer.isMasterLayer or layer.isSpecialLayer:
					if isEmpty(layer):
						# nothing on layer? no backup needed:
						print("- Layer ‘%s’ is empty. No backup needed." % (
							layer.name if layer.name else "(empty)",
						))
					else:
						# create and collect backup layers:
						layerCopy = layer.copy()
						layerCopy.background = layer.copyDecomposedLayer()
						layerCopy.name = "Backup: %s" % layer.name # does not work in G3
						backupLayers.append(layerCopy)
						print("- Creating backup of layer: %s" % (
							layer.name if layer.name else "(empty)",
						))
				
					layer.clear()
					layer.background.clear()
					layer.leftMetricsKey=None
					layer.rightMetricsKey=None
					layer.width=500
			
			# add collected backup layers (after the loop)
			for backupLayer in backupLayers:
				glyph.layers.append(backupLayer)
		
			# remove special layers:
			for i in range(len(glyph.layers)-1, -1, -1):
				layer = glyph.layers[i]
				if layer.isSpecialLayer:
					del glyph.layers[i]
			
			return glyph

def areaOfLayer(layer):
	area = 0
	l = layer.copyDecomposedLayer()
	l.removeOverlap()
	try:
		# GLYPHS 3:
		for s in l.shapes:
			area += s.area()
	except:
		# GLYPHS 2:
		for p in l.paths:
			area += p.area()
	return area

def buildNotdef( thisFont, override=False ):
	questionGlyph = thisFont.glyphs["question"]
	if not questionGlyph:
		print("⚠️ Error building .notdef: No question mark is available in your font. Cannot create .notdef." )
	else:
		name = ".notdef"
		notdefGlyph = createGlyph(thisFont, name, None, override=override)
		if notdefGlyph:
			sourceLayer = questionGlyph.layers[0]
			area = areaOfLayer(sourceLayer)
			for qLayer in questionGlyph.layers:
				if qLayer.isMasterLayer or qLayer.isSpecialLayer:
					qArea = areaOfLayer(qLayer)
					if qArea > area:
						sourceLayer = qLayer
						area = qArea
			
			if sourceLayer:
				# Build .notdef from question mark and circle:
				questionmarkLayer = sourceLayer.copyDecomposedLayer()
				scaleLayerByFactor( questionmarkLayer, 0.8 )
				qOrigin = questionmarkLayer.bounds.origin
				qWidth = questionmarkLayer.bounds.size.width
				qHeight = questionmarkLayer.bounds.size.height
				qCenter = NSPoint( qOrigin.x+0.5*qWidth, qOrigin.y+0.5*qHeight )
				side = max((qWidth,qHeight)) * 1.5
				circleRect = NSRect( 
					NSPoint(qCenter.x-0.5*side, qCenter.y-0.5*side),
					NSSize(side,side)
				)
				circle = circleInsideRect(circleRect)
				try:
					# GLYPHS 3
					questionmarkLayer.shapes.append(circle)
				except:
					# GLYPHS 2
					questionmarkLayer.paths.append(circle)
				questionmarkLayer.correctPathDirection()
			
				# Create glyph:
				notdefGlyph.leftMetricsKey = "=40"
				notdefGlyph.rightMetricsKey = "=|"
				for masterID in [m.id for m in thisFont.masters]:
					notdefLayer = notdefGlyph.layers[masterID]
					for thisPath in questionmarkLayer.paths:
						try:
							# GLYPHS 3:
							notdefLayer.shapes.append( thisPath.copy() )
						except:
							# GLYPHS 2:
							notdefLayer.paths.append( thisPath.copy() )
					notdefLayer.syncMetrics()
			else:
				print("⚠️ Error building .notdef: Could not determine source layer of glyph 'question'." )
	

def buildEstimated( thisFont, override=False ):
	glyphname = "estimated"
	estimatedGlyph = createGlyph(thisFont, glyphname, "212E", override=override)
	
	penpoints_estimated = (
		( (416.0,-5.0), ((557.0,-5.0), (635.0,33.0), (724.0,131.0)), (654.0,131.0), ((600.0,70.0), (511.0,22.0), (416.0,22.0)), ((274.0,22.0), (179.0,108.0), (179.0,143.0)), (179.0,311.0), ((179.0,328.0), (185.0,329.0), (194.0,329.0)), (792.0,329.0), ((782.0,557.0), (638.0,682.0), (416.0,682.0)), ((196.0,682.0), (40.0,544.0), (40.0,338.0)), ((40.0,129.0), (196.0,-5.0), (416.0,-5.0)) ),
		( (194.0,350.0), ((183.0,350.0), (179.0,353.0), (179.0,359.0)), (179.0,538.0), ((179.0,568.0), (280.0,658.0), (415.0,658.0)), ((522.0,658.0), (652.0,585.0), (652.0,531.0)), (652.0,366.0), ((652.0,354.0), (650.0,350.0), (636.0,350.0)), (194.0,350.0) )
	)
	
	if estimatedGlyph:
		# set metrics keys and kern groups:
		estimatedGlyph.leftMetricsKey = "=40"
		estimatedGlyph.rightMetricsKey = "=|"
		estimatedGlyph.leftKerningGroup = "estimated"
		estimatedGlyph.rightKerningGroup = "estimated"
		
		# find zero:
		zeroGlyph = thisFont.glyphs["zero.lf"]
		if not zeroGlyph:
			zeroGlyph = thisFont.glyphs["zero.tf"]
			if not zeroGlyph:
				zeroGlyph = thisFont.glyphs["zero"]
		
		# draw in every layer:
		for thisLayer in estimatedGlyph.layers:
			if thisLayer.isMasterLayer:
				for thisPath in penpoints_estimated:
					pen = thisLayer.getPen()
					pen.moveTo( thisPath[0] )
					for thisSegment in thisPath[1:]:
						if len(thisSegment) == 2: # lineto
							pen.lineTo( thisSegment )
						elif len(thisSegment) == 3: # curveto
							pen.curveTo(
								thisSegment[0],
								thisSegment[1],
								thisSegment[2]
							)
						else:
							print("%s: Path drawing error. Could not process this segment:\n" % (glyphname, thisSegment))
					pen.closePath()
					pen.endPath()
		
				# scale estimated to match zero:
				if zeroGlyph:
					zeroBounds = zeroGlyph.layers[thisLayer.associatedMasterId].bounds
					zeroHeight = zeroBounds.size.height
					if zeroHeight: # zero could be empty
						zeroOvershoot = -zeroBounds.origin.y
						overshootDiff = zeroOvershoot - 5.0
						estimatedHeight = 687.0
						correctedEstimatedHeight = zeroHeight - 2 * overshootDiff
						if correctedEstimatedHeight != estimatedHeight:
							scaleFactor = correctedEstimatedHeight/estimatedHeight
							estimatedCorrection = transform(shiftY=5.0)
							estimatedCorrection.appendTransform_( transform(scale=scaleFactor) )
							estimatedCorrection.appendTransform_( transform(-5.0) )
							thisLayer.applyTransform( estimatedCorrection.transformStruct() )
		
				# tidy up paths and set width:
				thisLayer.cleanUpPaths()
				thisLayer.syncMetrics()
				print("✅ Created estimated in master '%s'" % thisLayer.associatedFontMaster().name)
		
	else:
		print("⚠️ Could not create the estimated glyph already exists in this font. Rename or delete it and try again.")

def stemWidthForMaster( thisFont, thisMaster, default=50 ):
	try:
		slash = thisFont.glyphs["slash"].layers[thisMaster.id]
		slashLeft = slash.bounds.origin.x
		slashRight = slashLeft + slash.bounds.size.width
		slashBottom = slash.bounds.origin.x
		slashTop = slashLeft + slash.bounds.size.width
		middleHeight = (slashBottom+slashTop)/2
		measureStart = NSPoint(slashLeft,middleHeight)
		measureEnd = NSPoint(slashRight,middleHeight)
		intersections = list(slash.intersectionsBetweenPoints(measureStart,measureEnd))
		slashStemWidth = distance(intersections[1].pointValue(), intersections[2].pointValue()) # hypotenuse
		angleRAD = math.atan( (slashTop-slashBottom)/(slashRight-slashLeft) ) 
		return ((slashStemWidth * math.cos(angleRAD)) + slashStemWidth) * 0.5
	except:
		print( "⚠️ Error measuring slash, will try Master stem width instead.")
		try:
			return thisMaster.verticalStems[0] * 0.8
		except:
			print( "⚠️ Error building bars: No vertical stems set in Master '%s'. Will default to %i." % (thisMaster.name, default) )
	return default

def buildBars( thisFont, override=False ):
	barGlyph = createGlyph(thisFont, "bar", "007C", override=override)
	brokenbarGlyph = createGlyph(thisFont, "brokenbar", "00A6", override=override)

	if barGlyph or brokenbarGlyph:
		for thisMaster in thisFont.masters:
			goodMeasure = (thisMaster.ascender-thisMaster.descender)*0.2
			descender = round(thisMaster.descender - goodMeasure)
			ascender = round(thisMaster.ascender + goodMeasure)

			mID = thisMaster.id
			italicAngle = thisMaster.italicAngle
			pivot = thisMaster.xHeight * 0.5
			
			stemWidth = stemWidthForMaster(thisFont, thisMaster)

			stemWidth -= stemWidth*math.cos(math.radians(italicAngle))-stemWidth
			sidebearing = max( (350-stemWidth)*0.5, 60.0 )
			gap = max( 250-stemWidth, 120.0 )
			
			bottomLeft = italicize( (sidebearing,descender), italicAngle=italicAngle, pivotalY=pivot )
			bottomRight = italicize( (sidebearing+stemWidth,descender), italicAngle=italicAngle, pivotalY=pivot )
			topRight = italicize( (sidebearing+stemWidth,ascender), italicAngle=italicAngle, pivotalY=pivot )
			topLeft = italicize( (sidebearing,ascender), italicAngle=italicAngle, pivotalY=pivot )

			if barGlyph:
				barLayer = barGlyph.layers[mID]
				pen = barLayer.getPen()
				pen.moveTo( bottomLeft )
				pen.lineTo( bottomRight )
				pen.lineTo( topRight )
				pen.lineTo( topLeft )
				pen.closePath()
				pen.endPath()
				barLayer.RSB = sidebearing
				barGlyph.rightMetricsKey = "=|"
				barGlyph.leftKerningGroup = "bar"
				barGlyph.rightKerningGroup = "bar"
				print("✅ Created bar in master '%s'" % thisMaster.name)
			
			if brokenbarGlyph:
				gapBottomY = ((ascender+descender)-gap)*0.5
				gapTopY = ((ascender+descender)+gap)*0.5
				gapBottomRight = italicize( (sidebearing+stemWidth,gapBottomY), italicAngle=italicAngle, pivotalY=pivot )
				gapBottomLeft = italicize( (sidebearing,gapBottomY), italicAngle=italicAngle, pivotalY=pivot )
				gapTopRight = italicize( (sidebearing+stemWidth,gapTopY), italicAngle=italicAngle, pivotalY=pivot )
				gapTopLeft = italicize( (sidebearing,gapTopY), italicAngle=italicAngle, pivotalY=pivot )
				
				brokenbarLayer = brokenbarGlyph.layers[mID]
				pen = brokenbarLayer.getPen()
				pen.moveTo( bottomLeft )
				pen.lineTo( bottomRight )
				pen.lineTo( gapBottomRight )
				pen.lineTo( gapBottomLeft )
				pen.closePath()
				pen.endPath()
				
				brokenbarLayer = brokenbarGlyph.layers[mID]
				pen = brokenbarLayer.getPen()
				pen.moveTo( gapTopLeft )
				pen.lineTo( gapTopRight )
				pen.lineTo( topRight )
				pen.lineTo( topLeft )
				pen.closePath()
				pen.endPath()
				
				brokenbarLayer.RSB = sidebearing
				brokenbarGlyph.leftMetricsKey = "=bar"
				brokenbarGlyph.rightMetricsKey = "=|"
				brokenbarGlyph.leftKerningGroup = "bar"
				brokenbarGlyph.rightKerningGroup = "bar"
				print("✅ Created brokenbar in master '%s'" % thisMaster.name)
	else:
		print("⚠️ The glyphs bar and brokenbar already exist in this font. Rename or delete them and try again.")

class BuildSymbols( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 430
		windowHeight = 230
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Build Symbols", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.BuildSymbols.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Create the following symbols automatically. See tooltips for requirements.", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.buildEstimated = vanilla.CheckBox( (inset, linePos, -inset, 20), u"estimated", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.buildEstimated.getNSButton().setToolTip_(u"Will build estimated ℮ and scale it to the size of your lining zero, if available.")
		
		self.w.buildBars = vanilla.CheckBox( (inset+120, linePos, -inset, 20), u"bars, brokenbar", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.buildBars.getNSButton().setToolTip_(u"Will build bar | and brokenbar ¦ and use the master’s stem values for their size.")
		
		self.w.buildEmptyset = vanilla.CheckBox( (inset+240, linePos, -inset, 20), u"emptyset", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.buildEmptyset.getNSButton().setToolTip_(u"Will build emptyset. Not yet implemented, sorry.")
		linePos += lineHeight
		
		self.w.buildCurrency = vanilla.CheckBox( (inset, linePos, -inset, 20), u"currency", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.buildCurrency.getNSButton().setToolTip_(u"Will build currency. Not yet implemented, sorry.")
		
		self.w.buildLozenge = vanilla.CheckBox( (inset+120, linePos, -inset, 20), u"lozenge", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.buildLozenge.getNSButton().setToolTip_(u"Will build lozenge. Not yet implemented, sorry.")
		
		self.w.buildProduct = vanilla.CheckBox( (inset+240, linePos, -inset, 20), u"product", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.buildProduct.getNSButton().setToolTip_(u"Will build product. Not yet implemented, sorry.")
		linePos += lineHeight
		
		self.w.buildSummation = vanilla.CheckBox( (inset, linePos, -inset, 20), u"summation", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.buildSummation.getNSButton().setToolTip_(u"Will build summation. Not yet implemented, sorry.")
		
		self.w.buildRadical = vanilla.CheckBox( (inset+120, linePos, -inset, 20), u"radical", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.buildRadical.getNSButton().setToolTip_(u"Will build radical. Not yet implemented, sorry.")

		self.w.buildNotdef = vanilla.CheckBox( (inset+240, linePos, -inset, 20), u".notdef", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.buildNotdef.getNSButton().setToolTip_(u"Will build the mandatory .notdef glyph based on the boldest available question mark.")
		linePos += lineHeight
		
		# ----------- SEPARATOR LINE -----------
		self.w.line = vanilla.HorizontalLine((inset, int(linePos+0.5*lineHeight-1), -inset, 1))
		linePos += lineHeight
		
		# Other options:
		self.w.override = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Overwrite existing symbol glyphs (creates backup layers)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.override.getNSButton().setToolTip_(u"If checked, will create fresh symbols even if they already exist. Current outlines will be copied to a backup layer (if they are different). If unchecked, will skip glyphs that already exist.")
		linePos += lineHeight
		
		self.w.newTab = vanilla.CheckBox( (inset, linePos-1, 180, 20), u"Open tab with new glyphs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.newTab.getNSButton().setToolTip_(u"If checked, will open a new tab with the newly created symbols.")
		self.w.reuseTab = vanilla.CheckBox( (inset+180, linePos-1, -inset, 20), u"Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reuseTab.getNSButton().setToolTip_(u"If checked, will reuse the current tab, and open a new tab only if there is no Edit tab open already. Highly recommended.")
		linePos += lineHeight
		
		# Run Button:
		self.w.uncheckAllButton = vanilla.Button( (-315-inset, -20-inset, -200-inset, -inset), "Uncheck All", sizeStyle='regular', callback=self.checkAll )
		self.w.checkAllButton = vanilla.Button( (-190-inset, -20-inset, -90-inset, -inset), "Check All", sizeStyle='regular', callback=self.checkAll )
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Build", sizeStyle='regular', callback=self.BuildSymbolsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Build Symbols' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def updateUI(self, sender=None):
		# not implemented yet:
		self.w.buildEmptyset.enable(False)
		self.w.buildCurrency.enable(False)
		self.w.buildLozenge.enable(False)
		self.w.buildProduct.enable(False)
		self.w.buildSummation.enable(False)
		self.w.buildRadical.enable(False)
		# Allow "Reuse Tab" only if "Open Tab" is on:
		self.w.reuseTab.enable(self.w.newTab.get())
	
	def checkAll( self, sender=None, onOrOff=True ):
		if sender is self.w.uncheckAllButton:
			onOrOff = False
		Glyphs.defaults["com.mekkablue.BuildSymbols.buildEstimated"] = onOrOff
		Glyphs.defaults["com.mekkablue.BuildSymbols.buildBars"] = onOrOff
		Glyphs.defaults["com.mekkablue.BuildSymbols.buildEmptyset"] = False # onOrOff
		Glyphs.defaults["com.mekkablue.BuildSymbols.buildCurrency"] = False # onOrOff
		Glyphs.defaults["com.mekkablue.BuildSymbols.buildLozenge"] = False # onOrOff
		Glyphs.defaults["com.mekkablue.BuildSymbols.buildProduct"] = False # onOrOff
		Glyphs.defaults["com.mekkablue.BuildSymbols.buildSummation"] = False # onOrOff
		Glyphs.defaults["com.mekkablue.BuildSymbols.buildRadical"] = False # onOrOff
		Glyphs.defaults["com.mekkablue.BuildSymbols.buildNotdef"] = onOrOff
		self.LoadPreferences()
	
	def SavePreferences( self, sender=None ):
		try:
			Glyphs.defaults["com.mekkablue.BuildSymbols.buildEstimated"] = self.w.buildEstimated.get()
			Glyphs.defaults["com.mekkablue.BuildSymbols.buildBars"] = self.w.buildBars.get()
			Glyphs.defaults["com.mekkablue.BuildSymbols.buildEmptyset"] = self.w.buildEmptyset.get()
			Glyphs.defaults["com.mekkablue.BuildSymbols.buildCurrency"] = self.w.buildCurrency.get()
			Glyphs.defaults["com.mekkablue.BuildSymbols.buildLozenge"] = self.w.buildLozenge.get()
			Glyphs.defaults["com.mekkablue.BuildSymbols.buildProduct"] = self.w.buildProduct.get()
			Glyphs.defaults["com.mekkablue.BuildSymbols.buildSummation"] = self.w.buildSummation.get()
			Glyphs.defaults["com.mekkablue.BuildSymbols.buildRadical"] = self.w.buildRadical.get()
			Glyphs.defaults["com.mekkablue.BuildSymbols.buildNotdef"] = self.w.buildNotdef.get()
			
			# ---- OTHER OPTIONS: ----
			Glyphs.defaults["com.mekkablue.BuildSymbols.override"] = self.w.override.get()
			Glyphs.defaults["com.mekkablue.BuildSymbols.newTab"] = self.w.newTab.get()
			Glyphs.defaults["com.mekkablue.BuildSymbols.reuseTab"] = self.w.reuseTab.get()
			self.updateUI()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.BuildSymbols.buildEstimated", 1)
			Glyphs.registerDefault("com.mekkablue.BuildSymbols.buildBars", 1)
			Glyphs.registerDefault("com.mekkablue.BuildSymbols.buildEmptyset", 1)
			Glyphs.registerDefault("com.mekkablue.BuildSymbols.buildCurrency", 1)
			Glyphs.registerDefault("com.mekkablue.BuildSymbols.buildLozenge", 1)
			Glyphs.registerDefault("com.mekkablue.BuildSymbols.buildProduct", 1)
			Glyphs.registerDefault("com.mekkablue.BuildSymbols.buildSummation", 1)
			Glyphs.registerDefault("com.mekkablue.BuildSymbols.buildRadical", 1)
			Glyphs.registerDefault("com.mekkablue.BuildSymbols.buildNotdef", 1)
			
			self.w.buildEstimated.set( Glyphs.defaults["com.mekkablue.BuildSymbols.buildEstimated"] )
			self.w.buildBars.set( Glyphs.defaults["com.mekkablue.BuildSymbols.buildBars"] )
			self.w.buildEmptyset.set( Glyphs.defaults["com.mekkablue.BuildSymbols.buildEmptyset"] )
			self.w.buildCurrency.set( Glyphs.defaults["com.mekkablue.BuildSymbols.buildCurrency"] )
			self.w.buildLozenge.set( Glyphs.defaults["com.mekkablue.BuildSymbols.buildLozenge"] )
			self.w.buildProduct.set( Glyphs.defaults["com.mekkablue.BuildSymbols.buildProduct"] )
			self.w.buildSummation.set( Glyphs.defaults["com.mekkablue.BuildSymbols.buildSummation"] )
			self.w.buildRadical.set( Glyphs.defaults["com.mekkablue.BuildSymbols.buildRadical"] )
			self.w.buildNotdef.set( Glyphs.defaults["com.mekkablue.BuildSymbols.buildNotdef"] )

			Glyphs.registerDefault("com.mekkablue.BuildSymbols.override", 0)
			Glyphs.registerDefault("com.mekkablue.BuildSymbols.newTab", 0)
			Glyphs.registerDefault("com.mekkablue.BuildSymbols.reuseTab", 0)
			self.w.override.set( Glyphs.defaults["com.mekkablue.BuildSymbols.override"] )
			self.w.newTab.set( Glyphs.defaults["com.mekkablue.BuildSymbols.newTab"] )
			self.w.reuseTab.set( Glyphs.defaults["com.mekkablue.BuildSymbols.reuseTab"] )
			
			self.updateUI()
		except:
			return False
			
		return True

	def BuildSymbolsMain( self, sender ):
		try:
			Glyphs.clearLog() # clears macro window log

			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Build Symbols' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			print("Build Symbols Report for %s" % thisFont.familyName)
			if thisFont.filepath:
				print(thisFont.filepath)
			else:
				print("⚠️ File not yet saved.")
			print()
			
			# retrieve user settings:
			override = Glyphs.defaults["com.mekkablue.BuildSymbols.override"]
			newTab = Glyphs.defaults["com.mekkablue.BuildSymbols.newTab"]
			reuseTab = Glyphs.defaults["com.mekkablue.BuildSymbols.reuseTab"]
			
			tabText = ""
			
			# build glyphs:
			if Glyphs.defaults["com.mekkablue.BuildSymbols.buildEstimated"]:
				print("\n🔣 Building estimated:")
				buildEstimated(thisFont, override=override)
				tabText += "/estimated"
				
			if Glyphs.defaults["com.mekkablue.BuildSymbols.buildBars"]:
				print("\n🔣 Building bars:")
				buildBars(thisFont, override=override)
				tabText += "/bar/brokenbar"
				
			if Glyphs.defaults["com.mekkablue.BuildSymbols.buildEmptyset"]:
				print("\n🔣 Building emptyset:")
				print("😢 Not yet implemented, sorry.")
				pass
				
			if Glyphs.defaults["com.mekkablue.BuildSymbols.buildCurrency"]:
				print("\n🔣 Building currency:")
				print("😢 Not yet implemented, sorry.")
				pass
				
			if Glyphs.defaults["com.mekkablue.BuildSymbols.buildLozenge"]:
				print("\n🔣 Building lozenge:")
				print("😢 Not yet implemented, sorry.")
				pass
				
			if Glyphs.defaults["com.mekkablue.BuildSymbols.buildProduct"]:
				print("\n🔣 Building product:")
				print("😢 Not yet implemented, sorry.")
				pass
				
			if Glyphs.defaults["com.mekkablue.BuildSymbols.buildSummation"]:
				print("\n🔣 Building summation:")
				print("😢 Not yet implemented, sorry.")
				pass
				
			if Glyphs.defaults["com.mekkablue.BuildSymbols.buildRadical"]:
				print("\n🔣 Building radical:")
				print("😢 Not yet implemented, sorry.")
				pass
				
			if Glyphs.defaults["com.mekkablue.BuildSymbols.buildNotdef"]:
				print("\n🔣 Building notdef:")
				buildNotdef(thisFont, override=override)
				tabText += "/.notdef"
			
			# Floating notification:
			Glyphs.showNotification( 
				u"%s: symbols built" % (thisFont.familyName),
				u"Script ‘Build Symbols’ is finished.",
				)
			
			if newTab and tabText:
				if reuseTab and thisFont.currentTab:
					# reuses current tab:
					thisFont.currentTab.text = tabText
				else:
					# opens new Edit tab:
					thisFont.newTab( tabText )
			
			self.w.close() # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Build Symbols Error: %s" % e)
			import traceback
			print(traceback.format_exc())

BuildSymbols()