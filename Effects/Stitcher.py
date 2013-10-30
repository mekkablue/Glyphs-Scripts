#MenuTitle: Stitcher
# -*- coding: utf-8 -*-
"""Turn your paths into dotted lines, and specify a component as dot, i.e. stitch components onto paths in selected glyphs. Respects origin anchor in your source component."""

import GlyphsApp
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
	
def derivedNSPoint( segmentObject ):
	"""Hack for deriving an NSPoint from a segment point description."""

	segmentPointString = segmentObject.description()
	xyString = segmentPointString[ segmentPointString.find("{")+1 : segmentPointString.find("}") ]
	
	x = float( xyString[ : xyString.find(",") ] )
	y = float( xyString[ xyString.find(" ") +1 : ] )
	
	return NSPoint( x, y )

def getFineGrainPointsForPath( thisPath, distanceBetweenDots ):
	layerCoords = [ ]
	
	for thisSegment in thisPath.segments:
		
		if len( thisSegment ) == 2:
			# straight line:
			
			beginPoint = derivedNSPoint( thisSegment[0] )
			endPoint   = derivedNSPoint( thisSegment[1] )
			
			dotsPerSegment = int( ( distance( beginPoint, endPoint ) / distanceBetweenDots ) * 11 )
			
			for i in range( dotsPerSegment ):
				x = float( endPoint.x * i ) / dotsPerSegment + float( beginPoint.x * ( dotsPerSegment-i ) ) / dotsPerSegment
				y = float( endPoint.y * i ) / dotsPerSegment + float( beginPoint.y * ( dotsPerSegment-i ) ) / dotsPerSegment
				layerCoords += [ NSPoint( x, y ) ]
				
		elif len( thisSegment ) == 4:
			# curved segment:
			
			bezierPointA = derivedNSPoint( thisSegment[0] )
			bezierPointB = derivedNSPoint( thisSegment[1] )
			bezierPointC = derivedNSPoint( thisSegment[2] )
			bezierPointD = derivedNSPoint( thisSegment[3] )
			
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
		try:
			Font = thisLayer.parent.parent
			FontMasterID = Font.selectedFontMaster.id
			sourceComponent = Font.glyphs[ componentName ]
			xOffset = -sourceComponent.layers[FontMasterID].anchors["origin"].x
			yOffset = -sourceComponent.layers[FontMasterID].anchors["origin"].y
		except Exception as e:
			print "-- Note: no origin anchor in '%s', or no glyph with that name." % ( componentName )
		
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
		
	except Exception as e:
		# raise e
		return False


def process( thisLayer, deleteComponents, componentName, distanceBetweenDots, useBackground ):
	if deleteComponents:
		if not deleteAllComponents( thisLayer ):
			print "-- Error deleting previously placed components."
	
	if useBackground and len( thisLayer.paths ) > 0:
		thisLayer.clearBackground() # this is a little dangerous if background is active (then front layer is considered the background)
		for thisPath in thisLayer.paths:
			thisLayer.background.paths.append( thisPath.copy() )
		
		thisLayer.paths = []
	
	if not placeDots( thisLayer, useBackground, componentName, distanceBetweenDots ):
		print "-- Error placing components."

class ComponentOnLines( object ):
	def __init__( self ):
		windowHeight = 155

		self.w = vanilla.FloatingWindow( (350, windowHeight), "Stitcher", minSize=(300, windowHeight), maxSize=(500, windowHeight), autosaveName="com.mekkablue.ComponentsOnNodes.mainwindow" )

		self.w.text_1   = vanilla.TextBox( (15-1, 12+2,    15+95, 14), "Place component:", sizeStyle='small' )
		self.w.text_2   = vanilla.TextBox( (15-1, 12+25+2, 15+95, 14), "At intervals of:", sizeStyle='small' )
		self.w.componentName = vanilla.EditText( (15+100, 12-1,    -15, 19), "circle", callback=self.SavePreferences, sizeStyle='small' )
		self.w.interval      = vanilla.EditText( (15+100, 12+25-1, -15, 19), "40.0", callback=self.SavePreferences, sizeStyle='small' )
		self.w.replaceComponents = vanilla.CheckBox((15+3, 12+25+25,    -15, 18), "Replace existing components", value=True, sizeStyle='small', callback=self.SavePreferences )
		self.w.useBackground     = vanilla.CheckBox((15+3, 12+25+25+25, -15, 18), "Keep paths in background", value=True, sizeStyle='small', callback=self.SavePreferences )
		
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Stitch", sizeStyle='regular', callback=self.ComponentOnLinesMain )
		self.w.setDefaultButton( self.w.runButton )
		
		try:
			self.LoadPreferences( )
		except:
			pass

		self.w.open()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.ComponentOnLines.componentName"] = self.w.componentName.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.interval"] = self.w.interval.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.replaceComponents"] = self.w.replaceComponents.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.useBackground"] = self.w.useBackground.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			self.w.componentName.set( Glyphs.defaults["com.mekkablue.ComponentOnLines.componentName"] )
			self.w.interval.set( Glyphs.defaults["com.mekkablue.ComponentOnLines.interval"] )
			self.w.replaceComponents.set( Glyphs.defaults["com.mekkablue.ComponentOnLines.replaceComponents"] )
			self.w.useBackground.set( Glyphs.defaults["com.mekkablue.ComponentOnLines.useBackground"] )
		except:
			return False
			
		return True

	def ComponentOnLinesMain( self, sender ):
		try:
			Font = Glyphs.font
			FontMaster = Font.selectedFontMaster
			selectedLayers = Font.selectedLayers
			deleteComponents = bool( self.w.replaceComponents.get() )
			componentName = self.w.componentName.get()
			distanceBetweenDots = float( self.w.interval.get() )
			useBackground = bool( self.w.useBackground.get() )
			
			Font.disableUpdateInterface()

			for thisLayer in selectedLayers:
				thisGlyph = thisLayer.parent
				print "Processing", thisGlyph.name
				
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
