#MenuTitle: Variation Interpolator
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Interpolates each layer x times with its background and creates glyph variations with the results.
"""

import vanilla
from Foundation import NSPoint

class VariationInterpolator( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 400
		windowHeight = 120
		windowWidthResize  = 0 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Variation Interpolator", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.VariationInterpolator.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15-1, 12+2, 40, 14), "Create", sizeStyle='small' )
		self.w.numberOfInterpolations = vanilla.PopUpButton( (15+45, 12, 50, 17), [str(x) for x in range( 1, 31 )], callback=self.SavePreferences, sizeStyle='small' )
		self.w.text_2 = vanilla.TextBox( (15+100, 12+2, -15, 14), "background-interpolation glyphs", sizeStyle='small' )

		self.w.text_3 = vanilla.TextBox( (15-1, 40+2, 75, 14), "with suffix", sizeStyle='small' )
		self.w.suffix = vanilla.EditText( (15+65, 40-1, -150, 20), "var", callback=self.SavePreferences, sizeStyle = 'small')
		self.w.text_4 = vanilla.TextBox( (-145, 40+2, -15, 14), "for selected glyphs.", sizeStyle='small' )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-100-15, -20-15, -15, -15), "Create", sizeStyle='regular', callback=self.VariationInterpolatorMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Variation Interpolator' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults[ "com.mekkablue.VariationInterpolator.numberOfInterpolations" ] = self.w.numberOfInterpolations.get()
			Glyphs.defaults[ "com.mekkablue.VariationInterpolator.suffix" ] = self.w.suffix.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.VariationInterpolator.numberOfInterpolations", "10")
			Glyphs.registerDefault("com.mekkablue.VariationInterpolator.suffix", "var")
			self.w.numberOfInterpolations.set( Glyphs.defaults[ "com.mekkablue.VariationInterpolator.numberOfInterpolations" ] )
			self.w.suffix.set( Glyphs.defaults[ "com.mekkablue.VariationInterpolator.suffix" ] )
		except:
			return False
			
		return True
	
	def createGlyphCopy( self, thisGlyph, newSuffix ):
		thisFont = thisGlyph.parent
		
		# prepare glyph:
		newGlyph = thisGlyph.copy()
		newGlyphName = newGlyph.name + ".%s" % newSuffix
		newGlyph.name = newGlyphName
		newGlyph.unicode = None
		
		# remove previously generated glyph with the same name:
		oldGlyph = thisFont.glyphs[newGlyphName]
		if oldGlyph:
			thisFont.removeGlyph_( oldGlyph )
		
		return newGlyph
	
	def interpolatedPosition( self, foregroundPosition, foregroundFactor, backgroundPosition, backgroundFactor  ):
		interpolatedX = foregroundPosition.x * foregroundFactor + backgroundPosition.x * backgroundFactor
		interpolatedY = foregroundPosition.y * foregroundFactor + backgroundPosition.y * backgroundFactor
		interpolatedPosition = NSPoint( interpolatedX, interpolatedY )
		return interpolatedPosition
	
	def interpolatePaths( self, thisLayer, backgroundFactor, foregroundFactor ):
		# interpolate paths only if there is a compatible background:
		if thisLayer.background: # and (thisLayer.compareString() == thisLayer.background.compareString()):
			for thisPathIndex in range(len(thisLayer.paths)):
				thisPath = thisLayer.paths[thisPathIndex]
				for thisNodeIndex in range(len(thisPath.nodes)):
					thisNode = thisPath.nodes[thisNodeIndex]
					foregroundPosition = thisNode.position
					bPath = thisLayer.background.paths[thisPathIndex]
					if bPath:
						backgroundPosition = bPath.nodes[thisNodeIndex].position
						thisNode.setPosition_( self.interpolatedPosition( foregroundPosition, foregroundFactor, backgroundPosition, backgroundFactor ) )
		else:
			thisGlyph = thisLayer.parent
			print("%s: incompatible background layer ('%s'):" % ( thisGlyph.name, thisLayer.name ))
			print("Foreground: %s\nBackground:%s" % (thisLayer.compareString(), thisLayer.background.compareString()))
		
	def interpolateAnchors( self, thisLayer, backgroundFactor, foregroundFactor ):
		# interpolate anchor only if there is an anchor of the same name:
		if thisLayer.anchors:
			for foregroundAnchor in thisLayer.anchors:
				backgroundAnchor = thisLayer.background.anchors[ foregroundAnchor.name ]
				if backgroundAnchor:
					foregroundPosition = foregroundAnchor.position
					backgroundPosition = backgroundAnchor.position
					foregroundAnchor.setPosition_( self.interpolatedPosition( foregroundPosition, foregroundFactor, backgroundPosition, backgroundFactor ) )
				else:
					thisGlyph = thisLayer.parent
					print("%s: Anchor '%s' not in background." % (thisGlyph.name, foregroundAnchor.name))
	
	def interpolateComponents( self, thisLayer, backgroundFactor, foregroundFactor ):
		for i,thisComponent in enumerate(thisLayer.components):
			backgroundComponent = thisLayer.background.components[i]
			if backgroundComponent:
				
				# general component settings:
				thisComponent.position = self.interpolatedPosition(
					thisComponent.position, foregroundFactor,
					backgroundComponent.position, backgroundFactor,
				)
				thisComponent.scale = ( 
					thisComponent.scale[0] * foregroundFactor + backgroundComponent.scale[0] * backgroundFactor,
					thisComponent.scale[1] * foregroundFactor + backgroundComponent.scale[1] * backgroundFactor,
				)
				thisComponent.rotation = (
					thisComponent.rotation * foregroundFactor + backgroundComponent.rotation * backgroundFactor
				)
				
				# smart components:
				thisFont = thisLayer.parent.parent
				if thisFont:
					for axis in thisFont.glyphs[thisComponent.componentName].smartComponentAxes:
						newValue = float(thisComponent.smartComponentValues[axis.name]) * foregroundFactor + float(backgroundComponent.smartComponentValues[axis.name]) * backgroundFactor
						thisComponent.smartComponentValues[axis.name] = ( newValue )
					
		
	
	def interpolateLayerWithBackground( self, thisLayer, backgroundFactor ):
		foregroundFactor = 1.0 - backgroundFactor
		self.interpolatePaths( thisLayer, backgroundFactor, foregroundFactor )
		self.interpolateAnchors( thisLayer, backgroundFactor, foregroundFactor )
		self.interpolateComponents( thisLayer, backgroundFactor, foregroundFactor )
		thisLayer.background = None
		
	def interpolateGlyphWithBackgrounds( self, newGlyph, backgroundFactor ):
		# go through every layer of newGlyph:
		for thisLayer in newGlyph.layers:
			self.interpolateLayerWithBackground( thisLayer, backgroundFactor )
		
	def VariationInterpolatorMain( self, sender ):
		try:
			# get values from the UI:
			numberOfVariations = int( self.w.numberOfInterpolations.get()+1 )
			glyphSuffix = self.w.suffix.get().strip()
			
			thisFont = Glyphs.font # frontmost font
			thisFont.disableUpdateInterface() # suppresses UI updates in Font View
			listOfSelectedGlyphs = [ l.parent for l in thisFont.selectedLayers ] # currently selected glyphs
			
			for thisGlyph in listOfSelectedGlyphs: # loop through glyphs
				for numberOfThisVariation in range(numberOfVariations+1):
					newSuffix = "%s%02i" % ( glyphSuffix, numberOfThisVariation )
					newGlyph = self.createGlyphCopy( thisGlyph, newSuffix )
					
					# prepare interpolation:
					backgroundFactor = float( numberOfThisVariation ) / float( numberOfVariations )
					
					# add the glyph variation to the font:
					thisFont.glyphs.append( newGlyph )
					self.interpolateGlyphWithBackgrounds( newGlyph, backgroundFactor )
					
					
				thisFont.enableUpdateInterface() # re-enables UI updates in Font View
			if not self.SavePreferences( self ):
				print("Note: 'Variation Interpolator' could not write preferences.")
			
			self.w.close() # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Variation Interpolator Error: %s" % e)
			import traceback
			print(traceback.format_exc())

VariationInterpolator()