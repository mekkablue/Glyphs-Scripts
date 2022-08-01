#MenuTitle: Fix Arrow Positioning
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Fixes the placement and metrics keys of arrows, dependent on a specified default arrow. Adds metric keys and moves arrows vertically. Does not create new glyphs, only works on existing ones.
"""

import vanilla, math
from Foundation import NSPoint, NSAffineTransform, NSAffineTransformStruct

def intersectionsBetweenPoints( thisLayer, startPoint, endPoint ):
	"""
	Returns list of intersection NSPoints from startPoint to endPoint.
	thisLayer ... a glyph layer
	startPoint, endPoint ... NSPoints
	"""
	
	# prepare layer copy for measurement:
	cleanLayer = thisLayer.copyDecomposedLayer()
	cleanLayer.removeOverlap()
	
	# measure and return tuple:
	listOfIntersections = cleanLayer.intersectionsBetweenPoints( startPoint, endPoint )
	if len(listOfIntersections)%2 == 1:
		listOfIntersections = calculateIntersectionsStartPoint_endPoint_decompose_(startPoint, endPoint, True)
	return listOfIntersections


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


class FixArrowPositioning( object ):
	hArrows = ("rightArrow","leftArrow")
	vArrows = ("upArrow","downArrow","upDownArrow")
	dArrows = ("northEastArrow","southEastArrow","southWestArrow","northWestArrow")
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 280
		windowHeight = 240
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Fix Arrow Positioning", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.FixArrowPositioning.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.explanation = vanilla.TextBox( (inset, linePos+2, -inset, 14), "Fixes position and spacing of arrows.", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.referenceForHorizontalArrowsText = vanilla.TextBox( (inset, linePos+2, 130, 14), "Reference for H arrows:", sizeStyle='small' )
		self.w.referenceForHorizontalArrows = vanilla.PopUpButton( (inset+130, linePos, -inset, 17), self.hArrows, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight

		self.w.referenceForVerticalArrowsText = vanilla.TextBox( (inset, linePos+2, 130, 14), "Reference for V arrows:", sizeStyle='small' )
		self.w.referenceForVerticalArrows = vanilla.PopUpButton( (inset+130, linePos, -inset, 17), self.vArrows, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.referenceForDiagonalArrowsText = vanilla.TextBox( (inset, linePos+2, 130, 14), "Reference for D arrows:", sizeStyle='small' )
		self.w.referenceForDiagonalArrows = vanilla.PopUpButton( (inset+130, linePos, -inset, 17), self.dArrows, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.suffixText = vanilla.TextBox( (inset, linePos+2, 70, 14), "Dot suffix:", sizeStyle='small', selectable=False )
		self.w.suffix = vanilla.EditText( (inset+70, linePos, -inset, 19), "", sizeStyle='small' )
		linePos += lineHeight
		
		self.w.verticalPosOfHorizontalArrows = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Fix vertical positioning of horizontal arrows", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.verticalPosOfDiagonalArrows = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Fix vertical positioning of diagonal arrows", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.addAndUpdateMetricsKeys = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Add and update metrics keys", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Fix", sizeStyle='regular', callback=self.FixArrowPositioningMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Fix Arrow Positioning' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.FixArrowPositioning.referenceForHorizontalArrows"] = self.w.referenceForHorizontalArrows.get()
			Glyphs.defaults["com.mekkablue.FixArrowPositioning.referenceForVerticalArrows"] = self.w.referenceForVerticalArrows.get()
			Glyphs.defaults["com.mekkablue.FixArrowPositioning.referenceForDiagonalArrows"] = self.w.referenceForDiagonalArrows.get()
			Glyphs.defaults["com.mekkablue.FixArrowPositioning.verticalPosOfHorizontalArrows"] = self.w.verticalPosOfHorizontalArrows.get()
			Glyphs.defaults["com.mekkablue.FixArrowPositioning.verticalPosOfDiagonalArrows"] = self.w.verticalPosOfDiagonalArrows.get()
			Glyphs.defaults["com.mekkablue.FixArrowPositioning.addAndUpdateMetricsKeys"] = self.w.addAndUpdateMetricsKeys.get()
			Glyphs.defaults["com.mekkablue.FixArrowPositioning.suffix"] = self.w.suffix.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.FixArrowPositioning.referenceForHorizontalArrows", 0)
			Glyphs.registerDefault("com.mekkablue.FixArrowPositioning.referenceForVerticalArrows", 0)
			Glyphs.registerDefault("com.mekkablue.FixArrowPositioning.referenceForDiagonalArrows", 0)
			Glyphs.registerDefault("com.mekkablue.FixArrowPositioning.verticalPosOfHorizontalArrows", 1)
			Glyphs.registerDefault("com.mekkablue.FixArrowPositioning.verticalPosOfDiagonalArrows", 0)
			Glyphs.registerDefault("com.mekkablue.FixArrowPositioning.addAndUpdateMetricsKeys", 1)
			Glyphs.registerDefault("com.mekkablue.FixArrowPositioning.suffix", "")
			self.w.referenceForHorizontalArrows.set( Glyphs.defaults["com.mekkablue.FixArrowPositioning.referenceForHorizontalArrows"] )
			self.w.referenceForVerticalArrows.set( Glyphs.defaults["com.mekkablue.FixArrowPositioning.referenceForVerticalArrows"] )
			self.w.referenceForDiagonalArrows.set( Glyphs.defaults["com.mekkablue.FixArrowPositioning.referenceForDiagonalArrows"] )
			self.w.verticalPosOfHorizontalArrows.set( Glyphs.defaults["com.mekkablue.FixArrowPositioning.verticalPosOfHorizontalArrows"] )
			self.w.verticalPosOfDiagonalArrows.set( Glyphs.defaults["com.mekkablue.FixArrowPositioning.verticalPosOfDiagonalArrows"] )
			self.w.addAndUpdateMetricsKeys.set( Glyphs.defaults["com.mekkablue.FixArrowPositioning.addAndUpdateMetricsKeys"] )
			self.w.suffix.set( Glyphs.defaults["com.mekkablue.FixArrowPositioning.suffix"] )
		except:
			return False
			
		return True
	
	def addSuffixIfAny(self, glyphname, suffix):
		suffix = suffix.strip()
		glyphname = glyphname.strip()
		if suffix:
			# add dot if missing:
			suffix = ".%s" % suffix
			suffix = suffix.replace("..",".")
			glyphname += suffix
		return glyphname
	
	def measureBottomOfCenterStroke(self, layer):
		extra = 5
		hCenter = (layer.bounds.origin.x + layer.bounds.size.width) * 0.5
		startY = layer.bounds.origin.y - extra
		endY = startY + layer.bounds.size.height + 2*extra
		startPoint = NSPoint(hCenter, startY)
		endPoint = NSPoint(hCenter, endY)
		measures = intersectionsBetweenPoints(layer, startPoint, endPoint)
		print(layer.parent.name, len(measures), [round(p.y) for p in measures])
		if len(measures)==8:
			return measures[3].y
		else:
			return measures[1].y
	
	def updateMetricsKeys(self, thisGlyph):
		thisFont = thisGlyph.font
		if thisFont:
			# update all master layers:
			for thisMaster in thisFont.masters:
				thisLayer = thisGlyph.layers[thisMaster.id]
				thisLayer.updateMetrics()
				thisLayer.syncMetrics()
	
	def FixArrowPositioningMain( self, sender ):
		try:
			# query and update reference and other names:
			hArrowName = self.hArrows[Glyphs.defaults["com.mekkablue.FixArrowPositioning.referenceForHorizontalArrows"]]
			vArrowName = self.vArrows[Glyphs.defaults["com.mekkablue.FixArrowPositioning.referenceForVerticalArrows"]]
			dArrowName = self.dArrows[Glyphs.defaults["com.mekkablue.FixArrowPositioning.referenceForDiagonalArrows"]]
			
			suffix = Glyphs.defaults["com.mekkablue.FixArrowPositioning.suffix"]
			hArrowName = self.addSuffixIfAny(hArrowName, suffix)
			vArrowName = self.addSuffixIfAny(vArrowName, suffix)
			dArrowName = self.addSuffixIfAny(dArrowName, suffix)
			
			allHArrowNames = self.hArrows + ("leftRightArrow",) # add leftRightArrow because it cannot be a reference glyph
			allHorizontalArrowGlyphNames = [self.addSuffixIfAny(name,suffix) for name in allHArrowNames]
			
			allDiagonalArrowGlyphNames = [self.addSuffixIfAny(name,suffix) for name in self.dArrows]
			
			# bools for what we should do:
			shouldFixHorizontalArrows = bool(Glyphs.defaults["com.mekkablue.FixArrowPositioning.verticalPosOfHorizontalArrows"])
			shouldFixDiagonalArrows = bool(Glyphs.defaults["com.mekkablue.FixArrowPositioning.verticalPosOfDiagonalArrows"])
			shouldTakeCareOfMetricsKeys = bool(Glyphs.defaults["com.mekkablue.FixArrowPositioning.addAndUpdateMetricsKeys"])
			
			thisFont = Glyphs.font
			
			if not Glyphs.font:
				Message(title="Fix Arrow Positioning Error", message="The script requires that a font is open for editing.", OKButton=None)
			else:
				# clears macro window log:
				Glyphs.clearLog()
				warnAboutLayers=[]
				
				# HORIZONTAL ARROWS:
				if shouldFixHorizontalArrows:
					hReferenceGlyph = thisFont.glyphs[hArrowName]
					if not hReferenceGlyph:
						Message(title="Fix Arrow Positioning Error", message=u"No glyph found with name: ‘%s’. Cannot fix horizontal arrows."%hArrowName, OKButton=None)
					else:
						print("\nFIXING VERTICAL POSITIONS OF HORIZONTAL ARROWS:")
						
						# step through arrow glyphs
						for thisMaster in thisFont.masters:
							referenceHeight = self.measureBottomOfCenterStroke(hReferenceGlyph.layers[thisMaster.id])
							print("\nChecking for master %s..." % thisMaster.name)
							for horizontalArrowName in allHorizontalArrowGlyphNames:
								horizontalArrow = thisFont.glyphs[horizontalArrowName]
								if not horizontalArrow:
									print(u"⚠️ WARNING: no glyph found for '%s'." % horizontalArrowName)
								else:
									# do we need to warn?
									if len(horizontalArrow.layers) > len(thisFont.masters):
										warnAboutLayers.append(horizontalArrowName)
									
									# measure the layer for the current master:
									horizontalArrowLayer = horizontalArrow.layers[thisMaster.id]
									thisHeight = self.measureBottomOfCenterStroke(horizontalArrowLayer)
									shift = referenceHeight-thisHeight
									
									# shift if necessary:
									if abs(shift) > 0.6:
										shiftTransformMatrix = transform(shiftY=shift).transformStruct()
										horizontalArrowLayer.applyTransform(shiftTransformMatrix)
										print(u"⚠️ %s: layer '%s' shifted %i units." % (
											horizontalArrow.name,
											horizontalArrowLayer.name,
											shift,
										))
									else:
										print(u"💚 %s: layer '%s' is already OK." % (
											horizontalArrow.name,
											horizontalArrowLayer.name,
										))
				
				# DIAGONAL METRICS:
				if shouldFixDiagonalArrows:
					dReferenceGlyph = thisFont.glyphs[dArrowName]
					if not dReferenceGlyph:
						Message(title="Fix Arrow Positioning Error", message=u"No glyph found with name: ‘%s’. Cannot fix diagonal arrows."%dArrowName, OKButton=None)
					else:
						print("\nFIXING VERTICAL POSITIONS OF DIAGONAL ARROWS:")
						
						# step through arrow glyphs
						warnAboutLayers=[]
						for thisMaster in thisFont.masters:
							referenceLayer = dReferenceGlyph.layers[thisMaster.id]
							referenceHeight = referenceLayer.bounds.origin.y + referenceLayer.bounds.size.height * 0.5
							print("\nChecking for master %s..." % thisMaster.name)
							for diagonalArrowName in allDiagonalArrowGlyphNames:
								diagonalArrow = thisFont.glyphs[diagonalArrowName]
								if not diagonalArrow:
									print(u"⚠️ WARNING: no glyph found for '%s'." % diagonalArrowName)
								else:
									# do we need to warn?
									if len(diagonalArrow.layers) > len(thisFont.masters):
										warnAboutLayers.append(diagonalArrowName)
									
									# measure the layer for the current master:
									diagonalArrowLayer = diagonalArrow.layers[thisMaster.id]
									thisHeight = diagonalArrowLayer.bounds.origin.y + diagonalArrowLayer.bounds.size.height * 0.5
									shift = referenceHeight-thisHeight
									
									# shift if necessary:
									if abs(shift) > 0.6:
										shiftTransformMatrix = transform(shiftY=shift).transformStruct()
										diagonalArrowLayer.applyTransform(shiftTransformMatrix)
										print(u"⚠️ %s: layer '%s' shifted %i units." % (
											diagonalArrow.name,
											diagonalArrowLayer.name,
											shift,
										))
									else:
										print(u"💚 %s: layer '%s' is already OK." % (
											diagonalArrow.name,
											diagonalArrowLayer.name,
										))
				
				# SET METRICS KEYS ...
				if shouldTakeCareOfMetricsKeys:
					print("\nSETTING METRICS:")
					
					# ... FOR HORIZONTAL ARROWS:
					if not thisFont.glyphs[hArrowName]:
						print(u"❌ Reference glyph not found: %s. Cannot update metrics for horizontal arrows." % hArrowName)
					else:
						for thisName in allHArrowNames:
							if thisName != hArrowName:
								thisGlyph = thisFont.glyphs[thisName]
								if not thisGlyph:
									print(u"⚠️ Warning: '%s' not found in font." % thisName)
								else:
									if "left" in hArrowName and "left" in thisName.lower():
										thisGlyph.leftMetricsKey = "=%s"%hArrowName
										thisGlyph.rightMetricsKey = "=|%s"%hArrowName
									elif "right" in hArrowName and "right" in thisName.lower():
										thisGlyph.leftMetricsKey = "=|%s"%hArrowName
										thisGlyph.rightMetricsKey = "=%s"%hArrowName
									else:
										thisGlyph.leftMetricsKey = "=|%s"%hArrowName
										thisGlyph.rightMetricsKey = "=|%s"%hArrowName
									self.updateMetricsKeys(thisGlyph)
									print(u"✅ Metrics updated: %s" % thisName)

					# ... FOR DIAGONAL ARROWS:
					if not thisFont.glyphs[dArrowName]:
						print(u"❌ Reference glyph not found: %s. Cannot update metrics for diagonal arrows." % dArrowName)
					else:
						for thisName in self.dArrows:
							if thisName != dArrowName:
								thisGlyph = thisFont.glyphs[thisName]
								if not thisGlyph:
									print(u"⚠️ Warning: '%s' not found in font." % thisName)
								else:
									# northEastArrow, southEastArrow, southWestArrow, northWestArrow:
									if ("East" in dArrowName and "West" in thisName) or ("West" in dArrowName and "East" in thisName):
										thisGlyph.leftMetricsKey = "=|%s" % dArrowName
										thisGlyph.rightMetricsKey = "=|%s" % dArrowName
									else:
										thisGlyph.leftMetricsKey = "=%s" % dArrowName
										thisGlyph.rightMetricsKey = "=%s" % dArrowName
									self.updateMetricsKeys(thisGlyph)
									print(u"✅ Metrics updated: %s" % thisName)
					
					# ... FOR VERTICAL ARROWS:
					if not thisFont.glyphs[vArrowName]:
						print(u"❌ Reference glyph not found: %s. Cannot update metrics for vertical arrows." % vArrowName)
					else:
						for thisName in self.vArrows:
							if thisName != vArrowName:
								thisGlyph = thisFont.glyphs[thisName]
								if not thisGlyph:
									print(u"⚠️ Warning: '%s' not found in font." % thisName)
								else:
									thisGlyph.leftMetricsKey = "=%s"%vArrowName
									thisGlyph.rightMetricsKey = "=%s"%vArrowName
									self.updateMetricsKeys(thisGlyph)
									print(u"✅ Metrics updated: %s" % thisName)
								
				if warnAboutLayers:
					Message(title="Warning", message="The script only corrected the master layers. Double check for brace or bracket layers. These glyphs have non-master layers: %s"%", ".join(warnAboutLayers), OKButton=None)
				
			if not self.SavePreferences( self ):
				print(u"⚠️ 'Fix Arrow Positioning' could not write preferences.")
			
			Glyphs.showMacroWindow()
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Fix Arrow Positioning Error: %s" % e)
			import traceback
			print(traceback.format_exc())

FixArrowPositioning()