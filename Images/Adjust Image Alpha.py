#MenuTitle: Adjust Image Alpha
# -*- coding: utf-8 -*-
__doc__="""
Slider for setting the alpha of all images in selected glyphs.
"""

import vanilla

class AdjustImageAlpha( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 60
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Adjust Image Alpha for Selected Glyphs", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.AdjustImageAlpha.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15-1, 12+2, 75, 14), "Image Alpha:", sizeStyle='small' )
		self.w.alphaSlider= vanilla.Slider((100, 12, -55, 19), value=100.0, minValue=10.0, maxValue=100.0, sizeStyle='small', callback=self.AdjustImageAlphaMain )
		self.w.indicator = vanilla.TextBox( (-50, 12+2, -15, 14), "100.0", sizeStyle='small' )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Adjust Image Alpha' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.AdjustImageAlpha.alphaSlider"] = self.w.alphaSlider.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			NSUserDefaults.standardUserDefaults().registerDefaults_(
				{
					"com.mekkablue.AdjustImageAlpha.alphaSlider": 100.0
				}
			)
			self.w.alphaSlider.set( Glyphs.defaults["com.mekkablue.AdjustImageAlpha.alphaSlider"] )
		except:
			return False
			
		return True

	def AdjustImageAlphaMain( self, sender ):
		try:
			if not self.SavePreferences( self ):
				print "Note: 'Adjust Image Alpha' could not write preferences."
			
			self.w.indicator.set( "%.1f" % Glyphs.defaults["com.mekkablue.AdjustImageAlpha.alphaSlider"] )
			thisFont = Glyphs.font # frontmost font
			listOfSelectedLayers = thisFont.selectedLayers # active layers of currently selected glyphs
			for thisLayer in listOfSelectedLayers: # loop through layers
				if thisLayer.backgroundImage:
					thisGlyph = thisLayer.parent
					thisLayer.backgroundImage.alpha = Glyphs.defaults["com.mekkablue.AdjustImageAlpha.alphaSlider"]
			
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Adjust Image Alpha Error: %s" % e
			import traceback
			print traceback.format_exc()

AdjustImageAlpha()