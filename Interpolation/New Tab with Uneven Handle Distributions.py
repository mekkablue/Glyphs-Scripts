#MenuTitle: New Tab with Uneven Handle Distributions
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Finds glyphs where handle distributions change too much (e.g., from balanced to harmonised).
"""

import vanilla
from Foundation import NSPoint

def intersectionWithNSPoints( pointA, pointB, pointC, pointD ):
	"""
	Returns an NSPoint of the intersection AB with CD.
	Or False if there is no intersection
	"""
	try:
		x1, y1 = pointA.x, pointA.y
		x2, y2 = pointB.x, pointB.y
		x3, y3 = pointC.x, pointC.y
		x4, y4 = pointD.x, pointD.y
		
		try:
			slope12 = ( float(y2) - float(y1) ) / ( float(x2) - float(x1) )
		except:
			# division by zero if vertical
			slope12 = None
			
		try:
			slope34 = ( float(y4) - float(y3) ) / ( float(x4) - float(x3) )
		except:
			# division by zero if vertical
			slope34 = None
		
		if slope12 == slope34:
			# parallel, no intersection
			return None
		elif slope12 is None:
			# first line is vertical
			x = x1
			y = slope34 * ( x - x3 ) + y3
		elif slope34 is None:
			# second line is vertical
			x = x3
			y = slope12 * ( x - x1 ) + y1
		else:
			# both lines have an angle
			x = ( slope12 * x1 - y1 - slope34 * x3 + y3 ) / ( slope12 - slope34 )
			y = slope12 * ( x - x1 ) + y1
			
		intersectionPoint = NSPoint( x, y )
		if bothPointsAreOnSameSideOfOrigin( intersectionPoint, pointB, pointA ) and bothPointsAreOnSameSideOfOrigin( intersectionPoint, pointC, pointD ):
			if pointIsBetweenOtherPoints( intersectionPoint, pointB, pointA ) or pointIsBetweenOtherPoints( intersectionPoint, pointC, pointD ):
				return None
			return intersectionPoint
		else:
			return None
		
	except Exception as e:
		print(e)
		import traceback
		print(traceback.format_exc())
		return None

def bezierWithPoints( A,B,C,D, t ):
	x,y = bezier( A.x,A.y, B.x,B.y, C.x,C.y, D.x,D.y, t )
	return NSPoint(x,y)

def bezier( x1,y1,  x2,y2,  x3,y3,  x4,y4,  t ):
	"""
	Returns coordinates for t (=0.0...1.0) on curve segment.
	x1,y1 and x4,y4: coordinates of on-curve nodes
	x2,y2 and x3,y3: coordinates of BCPs
	"""
	x = x1*(1-t)**3 + x2*3*t*(1-t)**2 + x3*3*t**2*(1-t) + x4*t**3
	y = y1*(1-t)**3 + y2*3*t*(1-t)**2 + y3*3*t**2*(1-t) + y4*t**3

	return x, y

def bothPointsAreOnSameSideOfOrigin( pointA, pointB, pointOrigin ):
	returnValue = True
	xDiff = (pointA.x-pointOrigin.x) * (pointB.x-pointOrigin.x)
	yDiff = (pointA.y-pointOrigin.y) * (pointB.y-pointOrigin.y)
	if xDiff <= 0.0 and yDiff <= 0.0:
		returnValue = False
	return returnValue

def pointIsBetweenOtherPoints( thisPoint, otherPointA, otherPointB) :
	returnValue = False
	
	xDiffAB = otherPointB.x - otherPointA.x
	yDiffAB = otherPointB.y - otherPointA.y
	xDiffAP = thisPoint.x - otherPointA.x
	yDiffAP = thisPoint.y - otherPointA.y
	xDiffFactor = divideAndTolerateZero( xDiffAP, xDiffAB )
	yDiffFactor = divideAndTolerateZero( yDiffAP, yDiffAB )
	
	if xDiffFactor is not None:
		if 0.0<=xDiffFactor<=1.0:
			returnValue = True
	
	if yDiffFactor is not None:
		if 0.0<=yDiffFactor<=1.0:
			returnValue = True
		
	return returnValue

def divideAndTolerateZero( dividend, divisor ):
	if float(divisor) == 0.0:
		return None
	else:
		return dividend/divisor


class NewTabWithUnevenHandleDistributions( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 310
		windowHeight = 170
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"New Tab with Uneven Handle Distributions", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.NewTabWithUnevenHandleDistributions.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 12, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, lineHeight*2), u"Finds compatible glyphs with curve segments in which the handle distribution changes too much:", sizeStyle='small', selectable=True )
		linePos += int(lineHeight*1.8)
		
		self.w.factorChange = vanilla.CheckBox( (inset, linePos, 230, 20), u"Tolerated change factor (BCP1÷BCP2):", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.factorChangeEntry = vanilla.EditText( (inset+230, linePos, -inset, 19), "2.5", callback=self.SavePreferences, sizeStyle='small' )
		factorChangeTooltipText = u"Calculates length ratios of handles in a curve segment in every master. If the ratio differs by more than the given factor in one or more masters, glyph will be reported."
		self.w.factorChange.getNSButton().setToolTip_(factorChangeTooltipText)
		self.w.factorChangeEntry.getNSTextField().setToolTip_(factorChangeTooltipText)
		linePos += lineHeight
		
		self.w.anyMaxToNotMax = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Any handle that changes from 100% to non-100%", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.anyMaxToNotMax.getNSButton().setToolTip_(u"Finds BCPs that are maximized (100%) in one master, but not in other masters.")
		linePos += lineHeight
		
		self.w.markInFirstMaster = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Mark affected curve segments in first master", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.markInFirstMaster.enable(False)
		self.w.markInFirstMaster.getNSButton().setToolTip_(u"Not implemented yet. Sorry.")
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-100-inset, -20-inset, -inset, -inset), "Open Tab", sizeStyle='regular', callback=self.NewTabWithUnevenHandleDistributionsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'New Tab with Uneven Handle Distributions' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.NewTabWithUnevenHandleDistributions.factorChange"] = self.w.factorChange.get()
			Glyphs.defaults["com.mekkablue.NewTabWithUnevenHandleDistributions.factorChangeEntry"] = self.w.factorChangeEntry.get()
			Glyphs.defaults["com.mekkablue.NewTabWithUnevenHandleDistributions.anyMaxToNotMax"] = self.w.anyMaxToNotMax.get()
			Glyphs.defaults["com.mekkablue.NewTabWithUnevenHandleDistributions.markInFirstMaster"] = self.w.markInFirstMaster.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.NewTabWithUnevenHandleDistributions.factorChange", 0)
			Glyphs.registerDefault("com.mekkablue.NewTabWithUnevenHandleDistributions.factorChangeEntry", "2.5")
			Glyphs.registerDefault("com.mekkablue.NewTabWithUnevenHandleDistributions.anyMaxToNotMax", 1)
			Glyphs.registerDefault("com.mekkablue.NewTabWithUnevenHandleDistributions.markInFirstMaster", 0)
			self.w.factorChange.set( Glyphs.defaults["com.mekkablue.NewTabWithUnevenHandleDistributions.factorChange"] )
			self.w.factorChangeEntry.set( Glyphs.defaults["com.mekkablue.NewTabWithUnevenHandleDistributions.factorChangeEntry"] )
			self.w.anyMaxToNotMax.set( Glyphs.defaults["com.mekkablue.NewTabWithUnevenHandleDistributions.anyMaxToNotMax"] )
			self.w.markInFirstMaster.set( Glyphs.defaults["com.mekkablue.NewTabWithUnevenHandleDistributions.markInFirstMaster"] )
		except:
			return False
			
		return True
	
	def factor(self, A, B, C, D, intersection):
		handlePercentage1 = distance(A.position, B.position) / distance(A.position, intersection)
		handlePercentage2 = distance(D.position, C.position) / distance(D.position, intersection)
		return handlePercentage1/handlePercentage2
	
	def factorChangeIsTooBig(self, maxFactorChange, firstFactor, pathIndex, indexA, indexB, indexC, indexD, otherLayers):
		for otherLayer in otherLayers:
			otherPath = otherLayer.paths[pathIndex]
			A = otherPath.nodes[indexA]
			B = otherPath.nodes[indexB]
			C = otherPath.nodes[indexC]
			D = otherPath.nodes[indexD]
			intersection = intersectionWithNSPoints(A.position, B.position, C.position, D.position)
			if intersection:
				otherFactor = self.factor(A, B, C, D, intersection)
				factorChange = otherFactor/firstFactor
				if factorChange > maxFactorChange or factorChange < 1/maxFactorChange:
					return True
		return False
	
	def isMaxTheSameEverywhere(self, firstBCPsMaxed, pathIndex, indexA, indexB, indexC, indexD, otherLayers):
		for otherLayer in otherLayers:
			otherPath = otherLayer.paths[pathIndex]
			A = otherPath.nodes[indexA]
			B = otherPath.nodes[indexB]
			C = otherPath.nodes[indexC]
			D = otherPath.nodes[indexD]
			intersection = intersectionWithNSPoints(A.position, B.position, C.position, D.position)
			if intersection:
				BCPsMaxed = (B.position==intersection, C.position==intersection)
				if BCPsMaxed != firstBCPsMaxed:
					return False
		return True
	
	def insertMark( self, firstLayer, centerPoint ):
		pass
	
	def NewTabWithUnevenHandleDistributionsMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'New Tab with Uneven Handle Distributions' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			
			if not thisFont or not len(thisFont.masters)>1:
				Message(title="Uneven Handle Distribution Error", message="This script requires a multiple-master font, because it measures the difference between BCP distributions of a curve segment in one master to the same curve in other masters.", OKButton="Oops, OK")
			else:
				Glyphs.clearLog()
				print("New Tab with Uneven Handle Distributions\nReport for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				print()
				
				# query user options:
				shouldCheckFactorChange = Glyphs.defaults["com.mekkablue.NewTabWithUnevenHandleDistributions.factorChange"]
				maxFactorChange = float(Glyphs.defaults["com.mekkablue.NewTabWithUnevenHandleDistributions.factorChangeEntry"])
				shouldCheckAnyMaxToNotMax = Glyphs.defaults["com.mekkablue.NewTabWithUnevenHandleDistributions.anyMaxToNotMax"]
				markInFirstMaster = Glyphs.defaults["com.mekkablue.NewTabWithUnevenHandleDistributions.markInFirstMaster"]
				
				glyphs = [g for g in thisFont.glyphs if g.mastersCompatible]
				print(
					u"Found %i compatible glyph%s." % (
						len(glyphs),
						"" if len(glyphs)==1 else "s",
					)
				)
				
				affectedGlyphs = []
				for thisGlyph in glyphs:
					firstLayer = thisGlyph.layers[0]
					if firstLayer.paths:
						otherLayers = [l for l in thisGlyph.layers if l!=firstLayer and (l.isMasterLayer or l.isSpecialLayer) and thisGlyph.mastersCompatibleForLayers_((l,firstLayer))]
						for i,firstPath in enumerate(firstLayer.paths):
							if not thisGlyph in affectedGlyphs and not markInFirstMaster:
								for j,firstNode in enumerate(firstPath.nodes):
									if firstNode.type == CURVE:
										indexPrevNode = (j-3) % len(firstPath.nodes)
										indexBCP1 = (j-2) % len(firstPath.nodes)
										indexBCP2 = (j-1) % len(firstPath.nodes)
									
										firstPrevNode = firstPath.nodes[indexPrevNode]
										firstBCP1 = firstPath.nodes[indexBCP1]
										firstBCP2 = firstPath.nodes[indexBCP2]
									
										firstIntersection = intersectionWithNSPoints(firstPrevNode, firstBCP1, firstBCP2, firstNode)
										if firstIntersection:
											if shouldCheckFactorChange:
												firstFactor = self.factor(firstPrevNode, firstBCP1, firstBCP2, firstNode, firstIntersection)
												if self.factorChangeIsTooBig(maxFactorChange, firstFactor, i, indexPrevNode, indexBCP1, indexBCP2, j, otherLayers):
													if not thisGlyph in affectedGlyphs:
														affectedGlyphs.append(thisGlyph.name)
													if markInFirstMaster:
														centerPoint = bezierWithPoints(firstPrevNode, firstBCP1, firstBCP2, firstNode, 0.5)
														self.insertMark( firstLayer, centerPoint )
													else:
														break
											if shouldCheckAnyMaxToNotMax:
												firstBCPsMaxed = (firstBCP1.position==firstIntersection, firstBCP2.position==firstIntersection)
												if not self.isMaxTheSameEverywhere( firstBCPsMaxed, i, indexPrevNode, indexBCP1, indexBCP2, j, otherLayers):
													if not thisGlyph in affectedGlyphs:
														affectedGlyphs.append(thisGlyph.name)
													if markInFirstMaster:
														centerPoint = bezierWithPoints(firstPrevNode, firstBCP1, firstBCP2, firstNode, 0.5)
														self.insertMark( firstLayer, centerPoint )
													else:
														break
				if affectedGlyphs:
					tabString = "/"+"/".join(affectedGlyphs)
					# opens new Edit tab:
					thisFont.newTab( tabString )
					print("Affected glyphs:\n%s"%tabString)
				else:
					# Floating notification:
					Glyphs.showNotification( 
						u"Handle Distribution %s" % (thisFont.familyName),
						u"Found no uneven BCP distributions in the font.",
						)
					
					
				self.w.close() # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("New Tab with Uneven Handle Distributions Error: %s" % e)
			import traceback
			print(traceback.format_exc())

NewTabWithUnevenHandleDistributions()