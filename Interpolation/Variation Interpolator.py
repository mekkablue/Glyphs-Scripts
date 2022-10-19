#MenuTitle: Variation Interpolator
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Interpolates each layer x times with its background and creates glyph variations with the results.
"""

import vanilla
from Foundation import NSPoint

class VariationInterpolator( object ):
	prefID = "com.mekkablue.VariationInterpolator"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 240
		windowHeight = 130
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Variation Interpolator", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 10, 14, 20
		
		self.w.text_1 = vanilla.TextBox( (inset, linePos+2, 40, 14), "Create", sizeStyle='small' )
		self.w.numberOfInterpolations = vanilla.ComboBox( (inset+42, linePos-1, -inset-135, 19), [x*5 for x in range(1,7)], sizeStyle='small', callback=self.SavePreferences )
		self.w.text_2 = vanilla.TextBox( (-inset-130, linePos+2, -inset, 14), "interpolations between", sizeStyle='small' )
		linePos += lineHeight
		
		self.w.choice = vanilla.PopUpButton( (inset, linePos, -inset-40, 17), ("background and foreground", "foreground and background", "first two selected glyphs", "first two selected glyphs (reversed)"), sizeStyle='small', callback=self.SavePreferences )
		self.w.text_21 = vanilla.TextBox( (-inset-35, linePos+2, -inset, 14), "with", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.suffixText = vanilla.TextBox( (inset, linePos+2, 35, 14), "suffix", sizeStyle='small' )
		self.w.suffix = vanilla.EditText( (inset+35, linePos-1, -130, 20), "var", callback=self.SavePreferences, sizeStyle = 'small')
		self.w.postSuffixText = vanilla.TextBox( (-125, linePos+2, -15, 14), "for selected glyphs.", sizeStyle='small' )
		tooltip = "Select any number of glyphs and the script will create interpolations between foreground and background of each individual glyph. They will be named after their glyph, plus the suffix you provide, plus a continuous number."
		self.w.suffixText.getNSTextField().setToolTip_(tooltip)
		self.w.suffix.getNSTextField().setToolTip_(tooltip)
		self.w.postSuffixText.getNSTextField().setToolTip_(tooltip)
		
		self.w.glyphNameText = vanilla.TextBox( (inset, linePos+2, 70, 14), "glyph name:", sizeStyle='small', selectable=True )
		self.w.glyphName = vanilla.EditText( (inset+70, linePos-1, -inset, 19), "interpolation.", callback=self.SavePreferences, sizeStyle='small' )
		tooltip = "Select exactly two glyphs to interpolate, and the script creates interpolations with this name and a continuous number suffix."
		self.w.glyphName.getNSTextField().setToolTip_(tooltip)
		self.w.glyphNameText.getNSTextField().setToolTip_(tooltip)

		# Run Button:
		self.w.runButton = vanilla.Button((-100-15, -20-15, -15, -15), "Interpolate", sizeStyle='regular', callback=self.VariationInterpolatorMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Variation Interpolator' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.updateUI()
		self.w.open()
		self.w.makeKey()
	
	def updateUI(self, sender=None):
		if self.w.choice.get() > 1:
			self.w.suffixText.show(False)
			self.w.suffix.show(False)
			self.w.postSuffixText.show(False)
			self.w.glyphNameText.show(True)
			self.w.glyphName.show(True)
			self.w.runButton.enable( bool(self.w.glyphName.get().strip()) )
		else:
			self.w.suffixText.show(True)
			self.w.suffix.show(True)
			self.w.postSuffixText.show(True)
			self.w.glyphNameText.show(False)
			self.w.glyphName.show(False)
			self.w.runButton.enable( bool(self.w.suffix.get().strip()) )
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults[self.domain("numberOfInterpolations")] = self.w.numberOfInterpolations.get()
			Glyphs.defaults[self.domain("suffix")] = self.w.suffix.get()
			Glyphs.defaults[self.domain("glyphName")] = self.w.glyphName.get()
			Glyphs.defaults[self.domain("choice")] = self.w.choice.get()
			self.updateUI()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault(self.domain("numberOfInterpolations"), 10)
			Glyphs.registerDefault(self.domain("suffix"), "var")
			Glyphs.registerDefault(self.domain("glyphName"), "interpolated")
			Glyphs.registerDefault(self.domain("choice"), 0)
			self.w.numberOfInterpolations.set( self.pref("numberOfInterpolations") )
			self.w.suffix.set( self.pref("suffix") )
			self.w.glyphName.set( self.pref("glyphName") )
			self.w.choice.set( self.pref("choice") )
			self.updateUI()
		except:
			return False
			
		return True
	
	def createGlyphCopy( self, thisGlyph, newSuffix=None, newName=None ):
		thisFont = thisGlyph.parent
		
		# prepare glyph:
		newGlyph = thisGlyph.copy()
		if newSuffix:
			newGlyphName = "%s.%s" % (newGlyph.name, newSuffix)
		elif newName:
			newGlyphName = newName
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
			for path_index, path in enumerate(thisLayer.paths):
				for node_index, node in enumerate(path.nodes):
					foregroundPosition = node.position
					bPath = thisLayer.background.paths[path_index]
					if bPath:
						backgroundPosition = bPath.nodes[node_index].position
						node.setPosition_(
							self.interpolatedPosition(
								foregroundPosition,
								foregroundFactor,
								backgroundPosition,
								backgroundFactor,
								)
							)
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
			thisFont = Glyphs.font # frontmost font
			thisFont.disableUpdateInterface() # suppresses UI updates in Font View
			try:
				numberOfInterpolations = int(self.pref("numberOfInterpolations"))
				glyphSuffix = self.pref("suffix").strip()
				glyphName = self.pref("glyphName").strip()
				choice = self.pref("choice")
				selectedGlyphs = [ l.parent for l in thisFont.selectedLayers ] # currently selected glyphs
			
				if choice<2: 
					# interpolate between foreground and background
					for thisGlyph in selectedGlyphs:
						for numberOfThisVariation in range(1, numberOfInterpolations+1):
							interpolationFactor = float(numberOfThisVariation-1)/float(numberOfInterpolations)
							if choice == 1: # reverse
								interpolationFactor = 1.0-interpolationFactor
							newSuffix = "%s%03i" % (glyphSuffix, numberOfThisVariation)
							newGlyph = self.createGlyphCopy(thisGlyph, newSuffix)
							thisFont.glyphs.append(newGlyph)
							
							for masterIndex, thisMaster in enumerate(thisFont.masters):
								layerA = thisGlyph.layers[thisMaster.id].copy()
								layerA.layerId = "layerIDA%05i" % masterIndex
								layerB = thisGlyph.layers[thisMaster.id].copy()
								layerB.swapForegroundWithBackground()
								layerB.layerId = "layerIDB%05i" % masterIndex
								
								newGlyph.layers[thisMaster.id] = newGlyph._interpolateLayers_interpolation_masters_decompose_font_error_(
									[layerA, layerB], 
									{
										layerA.layerId:interpolationFactor,
										layerB.layerId:1.0-interpolationFactor,
									}, 
									None, False, thisFont, None)
								
				else:
					# interpolate between first two glyphs
					if not len(selectedGlyphs)==2:
						Message(title="Select exactly two glyphs", message="Please select exactly two glyphs to interpolate.", OKButton=None)
					else:
						glyphA, glyphB = selectedGlyphs
						for numberOfThisVariation in range(1, numberOfInterpolations+1):
							interpolationFactor = float(numberOfThisVariation-1)/float(numberOfInterpolations)
							if choice == 3:
								interpolationFactor = 1.0-interpolationFactor
							newName = "%s.%04i" % (glyphName, numberOfThisVariation)
							newGlyph = self.createGlyphCopy(glyphA, newName=newName)
							thisFont.glyphs.append(newGlyph)
							
							for masterIndex, thisMaster in enumerate(thisFont.masters):
								layerA = glyphA.layers[thisMaster.id].copy()
								layerA.layerId = "layerIDA%05i" % masterIndex
								layerB = glyphB.layers[thisMaster.id].copy()
								layerB.layerId = "layerIDB%05i" % masterIndex
								
								newGlyph.layers[thisMaster.id] = newGlyph._interpolateLayers_interpolation_masters_decompose_font_error_(
									[layerA, layerB], 
									{
										layerA.layerId:interpolationFactor,
										layerB.layerId:1.0-interpolationFactor,
									}, 
									None, False, thisFont, None)
						
			except Exception as e:
				Glyphs.showMacroWindow()
				print("\n⚠️ Script Error:\n")
				import traceback
				print(traceback.format_exc())
				print()
				raise e
				
			finally:
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