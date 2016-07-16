#MenuTitle: Stitcher
# -*- coding: utf-8 -*-
__doc__="""
Turn your paths into dotted lines, and specify a component as dot, i.e. stitch components onto paths in selected glyphs. Respects origin anchor in your source component.
"""

from GlyphsApp import MOVE
import math
import vanilla

def deleteAllComponents( thisLayer ):
	try:
		# print "-- Deleting %i existing components." % ( len(thisLayer.components) ) #DEBUG
		while len(thisLayer.components) > 0:
			# print "  Deleting component", thisLayer.components[0].componentName
			del thisLayer.components[0]
		
		return True
		
	except Exception as e:
		# raise e
		return False

def bezier( A, B, C, D, t ):
	x1, y1 = A.x, A.y
	x2, y2 = B.x, B.y
	x3, y3 = C.x, C.y
	x4, y4 = D.x, D.y
	
	x = x1*(1-t)**3 + x2*3*t*(1-t)**2 + x3*3*t**2*(1-t) + x4*t**3
	y = y1*(1-t)**3 + y2*3*t*(1-t)**2 + y3*3*t**2*(1-t) + y4*t**3

	return x, y

def distance( node1, node2 ):
	return math.hypot( node1.x - node2.x, node1.y - node2.y )

def getFineGrainPointsForPath( thisPath, distanceBetweenDots ):
	layerCoords = [ ]
	pathSegments = thisPath.segments
	
	# fix for new way open paths are stored (including MOVE and LINE segments)
	if thisPath.closed == False and thisPath.segments[0].type == MOVE:
		pathSegments = thisPath.segments[2:]
	
	for thisSegment in pathSegments:
		
		if len( thisSegment ) == 2:
			# straight line:
			
			beginPoint = thisSegment[0].pointValue()
			endPoint   = thisSegment[1].pointValue()
			
			dotsPerSegment = int( ( distance( beginPoint, endPoint ) / distanceBetweenDots ) * 11 )
			
			for i in range( dotsPerSegment ):
				x = float( endPoint.x * i ) / dotsPerSegment + float( beginPoint.x * ( dotsPerSegment-i ) ) / dotsPerSegment
				y = float( endPoint.y * i ) / dotsPerSegment + float( beginPoint.y * ( dotsPerSegment-i ) ) / dotsPerSegment
				layerCoords += [ NSPoint( x, y ) ]
				
		elif len( thisSegment ) == 4:
			# curved segment:
			
			bezierPointA = thisSegment[0].pointValue()
			bezierPointB = thisSegment[1].pointValue()
			bezierPointC = thisSegment[2].pointValue()
			bezierPointD = thisSegment[3].pointValue()
			
			bezierLength = distance( bezierPointA, bezierPointB ) + distance( bezierPointB, bezierPointC ) + distance( bezierPointC, bezierPointD ) # very rough approximation, up to 11% too long
			dotsPerSegment = int( ( bezierLength / distanceBetweenDots ) * 10 )
			
			for i in range( 1, dotsPerSegment ):
				t = float( i ) / float( dotsPerSegment )
				x, y = bezier( bezierPointA, bezierPointB, bezierPointC, bezierPointD, t )
				layerCoords += [ NSPoint( x, y ) ]
			
			layerCoords += [ NSPoint( bezierPointD.x, bezierPointD.y ) ]
	
	return layerCoords

def dotCoordsOnPath( thisPath, distanceBetweenDots ):
	dotPoints = [ thisPath.nodes[0] ]
	fineGrainPoints = getFineGrainPointsForPath( thisPath, distanceBetweenDots )
	
	myLastPoint = dotPoints[-1]
	
	for thisPoint in fineGrainPoints:
		if distance( myLastPoint, thisPoint ) >= distanceBetweenDots:
			dotPoints += [thisPoint]
			myLastPoint = thisPoint
			# print "-- Placed %s at %s." % ( componentName, str(thisPoint) ) # DEBUG
		else:
			pass
	
	return dotPoints

def placeDots( thisLayer, useBackground, componentName, distanceBetweenDots ):
	try:
		# find out component offset:
		xOffset = 0.0
		yOffset = 0.0
		Font = thisLayer.parent.parent
		FontMasterID = thisLayer.associatedMasterId
		sourceComponent = Font.glyphs[ componentName ]
		
		if sourceComponent:
			try:
				(xOffset, yOffset) = sourceAnchor.position
				xOffset = -xOffset
				yOffset = -yOffset
			except:
				pass
				# print "-- Note: no origin anchor in '%s'." % ( componentName )
		
			# use background if specified:
			if useBackground:
				sourceLayer = thisLayer.background
			else:
				sourceLayer = thisLayer
		
			for thisPath in sourceLayer.paths:
				for thisPoint in dotCoordsOnPath( thisPath, distanceBetweenDots ):
					newComp = GSComponent( componentName, NSPoint( thisPoint.x + xOffset, thisPoint.y + yOffset ) )
					thisLayer.addComponent_( newComp )
				
			return True
		else:
			return False
		
	except Exception as e:
		# raise e
		return False

def minimumOfOne( value ):
	try:
		returnValue = float( value )
		if returnValue < 1.0:
			returnValue = 1.0
	except:
		returnValue = 1.0
		
	return returnValue

def process( thisLayer, deleteComponents, componentName, distanceBetweenDots, useBackground ):
	if deleteComponents:
		if not deleteAllComponents( thisLayer ):
			print "-- Error deleting previously placed components."
	
	if useBackground and len( thisLayer.paths ) > 0:
		if thisLayer.className() == "GSBackgroundLayer":
			thisLayer = thisLayer.foreground()
		thisLayer.background.clear()
		for thisPath in thisLayer.paths:
			thisLayer.background.paths.append( thisPath.copy() )
		
		thisLayer.paths = []
	
	if not placeDots( thisLayer, useBackground, componentName, distanceBetweenDots ):
		print "-- Could not place components at intervals of %.1f units." % distanceBetweenDots

class ComponentOnLines( object ):
	def __init__( self ):
		windowHeight = 150

		self.w = vanilla.FloatingWindow( (350, windowHeight), "Stitcher", minSize=(300, windowHeight), maxSize=(500, windowHeight), autosaveName="com.mekkablue.ComponentsOnNodes.mainwindow" )

		self.w.text_1   = vanilla.TextBox( (15-1, 12+2,    15+95, 14), "Place component:", sizeStyle='small' )
		self.w.text_2   = vanilla.TextBox( (15-1, 12+25+2, 15+95, 14), "At intervals of:", sizeStyle='small' )
		self.w.componentName = vanilla.EditText( (15+100, 12-1, -15, 19), "circle", sizeStyle='small', callback=self.SavePreferences )
		self.w.sliderMin = vanilla.EditText( ( 15+100, 12+25-1, 50, 19), "30", sizeStyle='small', callback=self.SavePreferences )
		self.w.sliderMax = vanilla.EditText( (-15-50, 12+25-1, -15, 19), "60", sizeStyle='small', callback=self.SavePreferences )
		self.w.intervalSlider= vanilla.Slider((15+100+50+10, 12+25, -15-50-10, 19), value=0, minValue=0.0, maxValue=1.0, sizeStyle='small', callback=self.ComponentOnLinesMain )

		#self.w.replaceComponents = vanilla.CheckBox((15+3, 12+25+25,    -15, 19), "Replace existing components", value=True, sizeStyle='small', callback=self.SavePreferences )
		self.w.liveSlider    = vanilla.CheckBox((15+3, 12+25+25, -15, 19), "Live slider", value=False, sizeStyle='small' )
		self.w.useBackground = vanilla.CheckBox((15+3, 12+25+25+20, -15, 19), "Keep paths in background", value=True, sizeStyle='small', callback=self.SavePreferences )
		
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Stitch", sizeStyle='regular', callback=self.ComponentOnLinesMain )
		self.w.setDefaultButton( self.w.runButton )
		
		try:
			self.LoadPreferences()
		except:
			pass

		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.ComponentOnLines.componentName"] = self.w.componentName.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.sliderMin"] = self.w.sliderMin.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.sliderMax"] = self.w.sliderMax.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.intervalSlider"] = self.w.intervalSlider.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.liveSlider"] = self.w.liveSlider.get()
			#Glyphs.defaults["com.mekkablue.ComponentOnLines.replaceComponents"] = self.w.replaceComponents.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.useBackground"] = self.w.useBackground.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			NSUserDefaults.standardUserDefaults().registerDefaults_(
				{
					"com.mekkablue.ComponentOnLines.sliderMin": "30", 
					"com.mekkablue.ComponentOnLines.sliderMin": "60"
				}
			)
			self.w.componentName.set( Glyphs.defaults["com.mekkablue.ComponentOnLines.componentName"] )
			self.w.sliderMin.set( Glyphs.defaults["com.mekkablue.ComponentOnLines.sliderMin"] )
			self.w.sliderMax.set( Glyphs.defaults["com.mekkablue.ComponentOnLines.sliderMax"] )
			self.w.intervalSlider.set( Glyphs.defaults["com.mekkablue.ComponentOnLines.intervalSlider"] )
			self.w.liveSlider.set( Glyphs.defaults["com.mekkablue.ComponentOnLines.liveSlider"] )
			#self.w.replaceComponents.set( Glyphs.defaults["com.mekkablue.ComponentOnLines.replaceComponents"] )
			self.w.useBackground.set( Glyphs.defaults["com.mekkablue.ComponentOnLines.useBackground"] )
		except:
			return False
			
		return True

	def ComponentOnLinesMain( self, sender ):
		try:
			if ( bool(self.w.liveSlider.get()) and sender == self.w.intervalSlider ) or sender != self.w.intervalSlider:
				Font = Glyphs.font
				FontMaster = Font.selectedFontMaster
				selectedLayers = Font.selectedLayers
				# deleteComponents = bool( self.w.replaceComponents.get() )
				deleteComponents = True
				componentName = self.w.componentName.get()
				
				sliderMin = minimumOfOne( self.w.sliderMin.get() )
				sliderMax = minimumOfOne( self.w.sliderMax.get() )
					
				sliderPos = float( self.w.intervalSlider.get() )
				distanceBetweenDots = sliderMin * ( 1.0 - sliderPos ) + sliderMax * sliderPos
				useBackground = bool( self.w.useBackground.get() )
		
				Font.disableUpdateInterface()

				for thisLayer in selectedLayers:
					thisGlyph = thisLayer.parent
					# print "Processing", thisGlyph.name
			
					thisGlyph.beginUndo()
					process( thisLayer, deleteComponents, componentName, distanceBetweenDots, useBackground )
					thisGlyph.endUndo()

				Font.enableUpdateInterface()
			
				if not self.SavePreferences( self ):
					print "Note: could not write preferences."
			
			# self.w.close()
		except Exception, e:
			raise e

ComponentOnLines()
