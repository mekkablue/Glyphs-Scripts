#MenuTitle: Modify Components
# -*- coding: utf-8 -*-
__doc__="""
In selected glyphs, replaces accents with their dot suffix variant where possible.
"""

import vanilla


class ModifyComponents( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 220
		windowHeight = 90
		windowWidthResize  = 200 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Modify Components", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.ModifyComponents.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15-1, 12+3, 135, 14), "Suffix components with:", sizeStyle='small' )
		self.w.dotSuffix = vanilla.EditText( (15+135, 12, -15, 20), ".case", sizeStyle = 'small')
		
		# Run Button:
		self.w.runButton = vanilla.Button((-90-15, -20-15, -15, -15), "Modify", sizeStyle='regular', callback=self.ModifyComponentsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Modify Components' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.ModifyComponents.dotSuffix"] = self.w.dotSuffix.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			NSUserDefaults.standardUserDefaults().registerDefaults_(
				{
					"com.mekkablue.ModifyComponents.dotSuffix": ".case"
				}
			)
			self.w.dotSuffix.set( Glyphs.defaults["com.mekkablue.ModifyComponents.dotSuffix"] )
		except:
			return False
			
		return True
	
	def ModifyComponentsMain( self, sender ):
		try:
			dotSuffix = self.w.dotSuffix.get()
			if not dotSuffix[0] == ".":
				dotSuffix = ".%s" % dotSuffix
			
			thisFont = Glyphs.font # frontmost font
			listOfGlyphNames = [g.name for g in thisFont.glyphs]
			
			listOfSelectedLayers = thisFont.selectedLayers # active layers of currently selected glyphs
			for thisLayer in listOfSelectedLayers: # loop through layers
				theseComponents = thisLayer.components
				numberOfComponents = len(theseComponents)
				if numberOfComponents > 0:
					for compIndex in range(numberOfComponents):
						thisComponent = theseComponents[compIndex]
						thisComponentName = thisComponent.componentName
						newComponentName = "%s%s" % ( thisComponentName, dotSuffix )
						if newComponentName in listOfGlyphNames:
							thisGlyph = thisLayer.parent
							for eachLayer in thisGlyph.layers:
								thoseComponents = eachLayer.components
								thatComponent = thoseComponents[compIndex]
								if len(thoseComponents) > compIndex and thatComponent.componentName == thisComponentName:
									thatComponent.setComponentName_( newComponentName )
			
			if not self.SavePreferences( self ):
				print "Note: 'Modify Components' could not write preferences."
			
			# close the window
			self.w.close()
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Modify Components Error: %s" % e

ModifyComponents()