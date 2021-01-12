#MenuTitle: Remove Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Removes the specified component from all (selected) glyphs.
"""

import vanilla

class RemoveComponentfromSelectedGlyphs( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 130
		windowWidthResize  = 200 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Remove Component from Selected Glyphs", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.RemoveComponentfromSelectedGlyphs.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text1 = vanilla.TextBox( (15, 12+3, 130, 14), "Remove component", sizeStyle='small' )
		self.w.componentName  = vanilla.ComboBox(
				(15+130, 12, -15, 19), 
				self.glyphList(), 
				sizeStyle='small' 
			)
		self.w.fromWhere = vanilla.RadioGroup((15, 40, -15, 40), [ "from all selected glyphs", "from all glyphs in the font" ], callback=self.SavePreferences, sizeStyle = 'small' )
		self.w.fromWhere.set( 0 )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-100-15, -20-15, -15, -15), "Remove", sizeStyle='regular', callback=self.RemoveComponentfromSelectedGlyphsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Remove Component from Selected Glyphs' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.RemoveComponentfromSelectedGlyphs.componentName"] = self.w.componentName.get()
			Glyphs.defaults["com.mekkablue.RemoveComponentfromSelectedGlyphs.fromWhere"] = self.w.fromWhere.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.RemoveComponentfromSelectedGlyphs.componentName", "a")
			Glyphs.registerDefault("com.mekkablue.RemoveComponentfromSelectedGlyphs.fromWhere", "0")
			self.w.componentName.set( Glyphs.defaults["com.mekkablue.RemoveComponentfromSelectedGlyphs.componentName"] )
			self.w.fromWhere.set( Glyphs.defaults["com.mekkablue.RemoveComponentfromSelectedGlyphs.fromWhere"] )
		except:
			return False
			
		return True
		
	def glyphList(self):
		thisFont = Glyphs.font
		if thisFont:
			return sorted([g.name for g in thisFont.glyphs])
		else:
			return []
	
	def removeComponentFromLayer(self, componentName, thisLayer):
		theseComponents = thisLayer.components
		numberOfComponents = len( theseComponents )
		if numberOfComponents > 0:
			for i in range(numberOfComponents)[::-1]:
				thisComponent = theseComponents[i]
				if thisComponent.componentName == componentName:
					if Glyphs.versionNumber >= 3:
						index = thisLayer.shapes.index(thisComponent)
						del(thisLayer.shapes[index])
					else:
						thisLayer.removeComponent_( thisComponent )
		
	def removeComponentFromGlyph(self, componentName, thisGlyph):
		for thisLayer in thisGlyph.layers:
			self.removeComponentFromLayer( componentName, thisLayer )

	def RemoveComponentfromSelectedGlyphsMain( self, sender ):
		try:
			thisFont = Glyphs.font # frontmost font
			listOfGlyphs = thisFont.glyphs 
			
			if Glyphs.defaults["com.mekkablue.RemoveComponentfromSelectedGlyphs.fromWhere"] == 0:
				listOfGlyphs = [l.parent for l in thisFont.selectedLayers] # active layers of currently selected glyphs
				
			componentName = Glyphs.defaults["com.mekkablue.RemoveComponentfromSelectedGlyphs.componentName"]
			for thisGlyph in listOfGlyphs:
				self.removeComponentFromGlyph( componentName, thisGlyph )
			
			if not self.SavePreferences( self ):
				print("Note: 'Remove Component from Selected Glyphs' could not write preferences.")
			
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Component from Selected Glyphs Error: %s" % e)

RemoveComponentfromSelectedGlyphs()