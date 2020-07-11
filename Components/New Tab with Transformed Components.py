#MenuTitle: New Tab with Transformed Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Opens a new edit tab with components that are rotated, scaled or flipped, i.e., any transformation beyond mere shifts.
"""

import vanilla

def containsTransformedComponents( thisGlyph ):
	for thisLayer in thisGlyph.layers:
		for thisComponent in thisLayer.components:
			if thisComponent.transform[:4] != (1.0,0.0,0.0,1.0):
				return True
	return False

def hasScaledComponents(thisLayer, unproportional=False):
	for thisComponent in thisLayer.components:
		if thisComponent.rotation == 0.0:
			hScale, vScale = thisComponent.scale
			scaled = (hScale*vScale > 0.0) and (abs(hScale)!=1.0 or abs(vScale)!=1.0)
			if scaled:
				if unproportional:
					unproportionallyScaled = abs(hScale) != abs(vScale)
					if unproportionallyScaled:
						return True
				else:
					return True
	return False
	
def hasRotatedComponents(thisLayer):
	for thisComponent in thisLayer.components:
		if thisComponent.rotation:
			return True
	return False

def hasMirroredComponents(thisLayer):
	for thisComponent in thisLayer.components:
		hScale, vScale = thisComponent.scale
		if hScale * vScale < 0:
			return True
	return False
	
def hasMerelyShiftedComponents(thisLayer):
	for thisComponent in thisLayer.components:
		hScale, vScale = thisComponent.scale
		degrees = thisComponent.rotation
		if hScale==1.0 and vScale==1.0 and degrees == 0.0:
			x, y = thisComponent.position
			if x!=0 or y!=0:
				return True
	return False

class NewTabWithTransformedComponents( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 280
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"New Tab with Transformed Components", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.NewTabWithTransformedComponents.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Finds and displays components that are transformed:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.findScaled = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Find scaled components", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.findUnproportionallyScaled = vanilla.CheckBox( (inset*2, linePos-1, -inset, 20), u"Only unproportionally scaled (h≠v)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.findRotated = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Find rotated components", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight

		self.w.findMirrored = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Find flipped components", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.findShifted = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Find shifted (otherwise untransformed) components", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.includeNonexporting = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.includeInactiveLayers = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include inactive backup layers", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.reuseTab = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-110-inset, -20-inset, -inset, -inset), "Open Tab", sizeStyle='regular', callback=self.NewTabWithTransformedComponentsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'New Tab with Transformed Components' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		self.updateUI()
		
	def updateUI(self, sender=None):
		self.w.findUnproportionallyScaled.enable( self.w.findScaled.get() )
		self.w.runButton.enable(
			self.w.findScaled.get() or
			self.w.findRotated.get() or
			self.w.findMirrored.get() or
			self.w.findShifted.get()
		)
		
		
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findScaled"] = self.w.findScaled.get()
			Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findUnproportionallyScaled"] = self.w.findUnproportionallyScaled.get()
			Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findRotated"] = self.w.findRotated.get()
			Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findMirrored"] = self.w.findMirrored.get()
			Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findShifted"] = self.w.findShifted.get()
			Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.includeNonexporting"] = self.w.includeNonexporting.get()
			Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.includeInactiveLayers"] = self.w.includeInactiveLayers.get()
			Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.reuseTab"] = self.w.reuseTab.get()
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.NewTabWithTransformedComponents.findScaled", 1)
			Glyphs.registerDefault("com.mekkablue.NewTabWithTransformedComponents.findUnproportionallyScaled", 1)
			Glyphs.registerDefault("com.mekkablue.NewTabWithTransformedComponents.findRotated", 0)
			Glyphs.registerDefault("com.mekkablue.NewTabWithTransformedComponents.findMirrored", 0)
			Glyphs.registerDefault("com.mekkablue.NewTabWithTransformedComponents.findShifted", 0)
			Glyphs.registerDefault("com.mekkablue.NewTabWithTransformedComponents.includeNonexporting", 0)
			Glyphs.registerDefault("com.mekkablue.NewTabWithTransformedComponents.includeInactiveLayers", 0)
			Glyphs.registerDefault("com.mekkablue.NewTabWithTransformedComponents.reuseTab", 1)
			
			# load previously written prefs:
			self.w.findScaled.set( Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findScaled"] )
			self.w.findUnproportionallyScaled.set( Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findUnproportionallyScaled"] )
			self.w.findRotated.set( Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findRotated"] )
			self.w.findMirrored.set( Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findMirrored"] )
			self.w.findShifted.set( Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findShifted"] )
			self.w.includeNonexporting.set( Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.includeNonexporting"] )
			self.w.includeInactiveLayers.set( Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.includeInactiveLayers"] )
			self.w.reuseTab.set( Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.reuseTab"] )
			
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def NewTabWithTransformedComponentsMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'New Tab with Transformed Components' could not write preferences.")
			
			findScaled = Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findScaled"]
			findUnproportionallyScaled = Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findUnproportionallyScaled"]
			findRotated = Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findRotated"]
			findMirrored = Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findMirrored"]
			findShifted = Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.findShifted"]
			includeNonexporting = Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.includeNonexporting"]
			includeInactiveLayers = Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.includeInactiveLayers"]
			reuseTab = Glyphs.defaults["com.mekkablue.NewTabWithTransformedComponents.reuseTab"]
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton="Oooops")
			else:
				print("New Tab with Transformed Components Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
				
				layersWithScaledComponents = []
				layersWithRotatedComponents = []
				layersWithMirroredComponents = []
				layersWithShiftedComponents = []
				
				glyphCount = len(thisFont.glyphs)
				affectedGlyphCount = 0
				for i, thisGlyph in enumerate(thisFont.glyphs):
					self.w.progress.set(i/glyphCount*100)
					if thisGlyph.export or includeNonexporting:
						isAffected = False
						for thisLayer in thisGlyph.layers:
							if thisLayer.components:
								if thisLayer.isMasterLayer or thisLayer.isSpecialLayer or thisLayer.isColorLayer or includeInactiveLayers:
									# scale
									if findScaled and hasScaledComponents(thisLayer, unproportional=findUnproportionallyScaled):
										layersWithScaledComponents.append(thisLayer)
										print("↕️ %s: layer ‘%s’ contains scaled component" % (thisGlyph.name, thisLayer.name))
										isAffected = True
									
									# rotated
									if findRotated and hasRotatedComponents(thisLayer):
										layersWithRotatedComponents.append(thisLayer)
										print("🔄 %s: layer ‘%s’ contains rotated component" % (thisGlyph.name, thisLayer.name))
										isAffected = True
								
									# mirrored
									if findMirrored and hasMirroredComponents(thisLayer):
										layersWithMirroredComponents.append(thisLayer)
										print("🔀 %s: layer ‘%s’ contains mirrored component" % (thisGlyph.name, thisLayer.name))
										isAffected = True
									
									# shifted
									if findShifted and hasMerelyShiftedComponents(thisLayer):
										layersWithShiftedComponents.append(thisLayer)
										print("↗️ %s: layer ‘%s’ contains shifted component" % (thisGlyph.name, thisLayer.name))
										isAffected = True
						
						if isAffected:
							affectedGlyphCount += 1
							print()
			
				allLayers = []
				for foundLayers in (layersWithScaledComponents, layersWithRotatedComponents, layersWithMirroredComponents, layersWithShiftedComponents):
					if foundLayers:
						for foundLayer in foundLayers:
							allLayers.append( foundLayer )
						for i in range(2):
							allLayers.append( GSControlLayer.newline() )
				if len(allLayers) > 0:
					# opens new Edit tab:
					if reuseTab and thisFont.currentTab:
						newTab = thisFont.currentTab
					else:
						newTab = thisFont.newTab()
					newTab.layers = allLayers

			self.w.progress.set(100)
			
			# Final report:
			try:
				Glyphs.showNotification( 
					u"%s: found %i glyph%s" % (
						thisFont.familyName,
						affectedGlyphCount,
						"" if affectedGlyphCount==1 else "s",
						),
					u"Layers found: %s components. Details in Macro Window." % (
						("%s%s%s%s" % (
							"%i scaled, " % len(layersWithScaledComponents), # if layersWithScaledComponents else "",
							"%i rotated, " % len(layersWithRotatedComponents), # if layersWithRotatedComponents else "",
							"%i mirrored, " % len(layersWithMirroredComponents), # if layersWithMirroredComponents else "",
							"%i shifted, " % len(layersWithShiftedComponents), # if layersWithShiftedComponents else "",
						))[:-2]
					),
				
					)
			except:
				# Floating notification:
				Glyphs.showNotification( 
					u"%s: nothing found" % (thisFont.familyName),
					u"Script finished with no results. Details in Macro Window.",
					)
				
			print("\nDone. Processed %i glyphs."%glyphCount)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("New Tab with Transformed Components Error: %s" % e)
			import traceback
			print(traceback.format_exc())

NewTabWithTransformedComponents()
