#MenuTitle: Pixelate
# -*- coding: utf-8 -*-
__doc__="""
Turns outline glyphs into pixel glyphs by inserting pixel components, resetting widths and moving outlines to the background.
"""

import vanilla, traceback

def drawGlyphIntoBackground(layer, info):

        # Due to internal Glyphs.app structure, we need to catch and print exceptions
        # of these callback functions with try/except like so:
        try:

                # Your drawing code here
                NSColor.redColor().set()
                layer.bezierPath.fill()

        # Error. Print exception.
        except:
                import traceback
                print(traceback.format_exc())

# add your function to the hook



class Pixelate( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 250
		windowHeight = 185
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Pixelate", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.Pixelate.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		
		self.w.pixelRasterText = vanilla.TextBox( (15-1, 12+2, 140, 14), "Pixel grid step", sizeStyle='small' )
		self.w.pixelRasterWidth = vanilla.EditText( (140+10, 12, -15, 15+4), "50", callback=self.SavePreferences, sizeStyle = 'small')
		self.w.pixelRasterWidth.getNSTextField().setToolTip_("The distance between all pixel elements.")
		
		self.w.pixelComponentText = vanilla.TextBox( (15-1, 12+26, 140, 14), "Pixel component name", sizeStyle='small' )
		self.w.pixelComponentName = vanilla.EditText( (140+10, 12+24, -15, 15+4), "pixel", callback=self.EnablePixelateButton, sizeStyle = 'small' )
		self.w.pixelComponentName.getNSTextField().setToolTip_("The name of the glyph containing the pixel element. If it does not exist in the font, the Insert button will deactivate.")
		
		self.w.resetWidths = vanilla.CheckBox( (15, 63, -15, 20), "Snap widths to pixel grid", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.resetWidths.getNSButton().setToolTip_(u"Also snaps the glyph’s advance width (RSB) to the pixel grid.")
		
		self.w.decomposeComponents = vanilla.CheckBox( (15, 63+20, -15, 20), "Decompose compounds", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.decomposeComponents.getNSButton().setToolTip_("If on, will insert outlines instead of components.")
		
		self.w.keepWindowOpen = vanilla.CheckBox( (15, 63+40, -15, 20), "Keep window open", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.keepWindowOpen.getNSButton().setToolTip_("If off, the window will close after pressing the Insert button.")
		
		# Run Button:
		self.w.runButton = vanilla.Button((-120-15, -20-15, -15, -15), "Insert Pixels", sizeStyle='regular', callback=self.PixelateMain )
		self.w.runButton.getNSButton().setToolTip_("The button will deactivate if there is no glyph with the name entered above.")
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Pixelate' could not load preferences. Will resort to defaults"
		
		# Check if run button should be enabled:
		self.EnablePixelateButton()
		Glyphs.addCallback(self.EnablePixelateButton, UPDATEINTERFACE)
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def __del__(self):
		"""docstring for __del__"""
		Glyphs.removeCallback(self.EnablePixelateButton)
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.Pixelate.pixelComponentName"] = self.w.pixelComponentName.get()
			Glyphs.defaults["com.mekkablue.Pixelate.pixelRasterWidth"] = self.w.pixelRasterWidth.get()
			Glyphs.defaults["com.mekkablue.Pixelate.resetWidths"] = self.w.resetWidths.get()
			Glyphs.defaults["com.mekkablue.Pixelate.decomposeComponents"] = self.w.decomposeComponents.get()
			Glyphs.defaults["com.mekkablue.Pixelate.keepWindowOpen"] = self.w.keepWindowOpen.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.Pixelate.pixelComponentName", "pixel")
			Glyphs.registerDefault("com.mekkablue.Pixelate.pixelRasterWidth", "50")
			Glyphs.registerDefault("com.mekkablue.Pixelate.resetWidths", True)
			Glyphs.registerDefault("com.mekkablue.Pixelate.decomposeComponents", True)
			Glyphs.registerDefault("com.mekkablue.Pixelate.keepWindowOpen", True)
			self.w.pixelComponentName.set( Glyphs.defaults["com.mekkablue.Pixelate.pixelComponentName"] )
			self.w.pixelRasterWidth.set( Glyphs.defaults["com.mekkablue.Pixelate.pixelRasterWidth"] )
			self.w.resetWidths.set( Glyphs.defaults["com.mekkablue.Pixelate.resetWidths"] )
			self.w.decomposeComponents.set( Glyphs.defaults["com.mekkablue.Pixelate.decomposeComponents"] )
			self.w.keepWindowOpen.set( Glyphs.defaults["com.mekkablue.Pixelate.keepWindowOpen"] )
		except:
			return False
			
		return True
	
	def EnablePixelateButton( self, layer=None, info=None, sender=None ):
		"""
		Checks if the pixel component entered by the user actually exists,
		and enables/disables the Run button accordingly.
		"""
		self.SavePreferences(None)
		onOff = False
		pixelNameEntered = Glyphs.defaults["com.mekkablue.Pixelate.pixelComponentName"]
		if Glyphs.font.glyphs[pixelNameEntered]:
			onOff = True
		self.w.runButton.enable(onOff)

	def PixelateMain( self, sender ):
		try:
			# save prefs:
			if not self.SavePreferences( self ):
				print "Note: 'Pixelate' could not write preferences."
			
			thisFont = Glyphs.font # frontmost font
			listOfSelectedLayers = thisFont.selectedLayers # active layers of currently selected glyphs
			pixelRasterWidth = float( Glyphs.defaults["com.mekkablue.Pixelate.pixelRasterWidth"] )
			pixelNameEntered = str( Glyphs.defaults["com.mekkablue.Pixelate.pixelComponentName"] )
			pixel = thisFont.glyphs[ pixelNameEntered ]
			widthsShouldBeReset = Glyphs.defaults["com.mekkablue.Pixelate.resetWidths"]
			componentsMustBeDecomposed = Glyphs.defaults["com.mekkablue.Pixelate.decomposeComponents"]
			
			for thisLayer in listOfSelectedLayers: # loop through layers
				thisGlyph = thisLayer.parent
				
				if len(thisLayer.paths) > 0 or (componentsMustBeDecomposed and len(thisLayer.components) > 0):
					
					# get all possible pixel positions within layer bounds:
					thisLayerBezierPath = thisLayer.copyDecomposedLayer().bezierPath # necessary for containsPoint_() function
					layerBounds = thisLayer.bounds
					xStart = int(round( layerBounds.origin.x / pixelRasterWidth ))
					yStart = int(round( layerBounds.origin.y / pixelRasterWidth ))
					xIterations = int(round( layerBounds.size.width / pixelRasterWidth ))
					yIterations = int(round( layerBounds.size.height / pixelRasterWidth ))
					pixelCount = 0

					# move current layer to background and clean foreground:
					# thisLayer.background = thisLayer.copy()
					# thisLayer.clear()
					# workaround for a bug in the current API, until this works again:
					thisLayer.background.clear()
					thisLayer.swapForegroundWithBackground()
					
					# snap width to pixel grid:
					widthReport = ""
					if widthsShouldBeReset:
						originalWidth = thisLayer.width
						pixelatedWidth = round( originalWidth / pixelRasterWidth ) * pixelRasterWidth
						thisLayer.setWidth_( pixelatedWidth )
						if originalWidth != thisLayer.width: # only if it really changed
							widthReport = ", snapped width to %.1f" % pixelatedWidth
					
					# add pixels:
					for x in range(xStart, xStart + xIterations):
						for y in range( yStart, yStart + yIterations):
							# if the pixel center is black, insert a pixel component here:
							pixelCenter = NSPoint( (x+0.5) * pixelRasterWidth, (y+0.5) * pixelRasterWidth )
							if thisLayerBezierPath.containsPoint_( pixelCenter ):
								pixelCount += 1
								pixelComponent = GSComponent( pixel, NSPoint( x * pixelRasterWidth, y * pixelRasterWidth ) )
								pixelComponent.automaticAlignment = False
								thisLayer.addComponent_( pixelComponent )
					
					print u"✅ %s: added %i pixels to layer '%s'%s." % ( thisGlyph.name, pixelCount, thisLayer.name, widthReport )
				else:
					print u"⚠️ No paths in '%s' (layer '%s'), skipping." % ( thisGlyph.name, thisLayer.name )
			
			
			# keep window open if requested:
			if not Glyphs.defaults["com.mekkablue.Pixelate.keepWindowOpen"]:
				self.w.close()
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print u"❌ Pixelate Error: %s" % e
			print traceback.format_exc()

Pixelate()