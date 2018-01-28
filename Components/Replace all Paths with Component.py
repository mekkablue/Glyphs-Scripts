#MenuTitle: Replace all Paths with Component
# -*- coding: utf-8 -*-
__doc__="""
Replaces all paths with a user-defined component.
"""

import vanilla

def centerOfRect(rect):
	"""
	Returns the center of NSRect rect as an NSPoint.
	"""
	x = rect.origin.x + rect.size.width * 0.5
	y = rect.origin.y + rect.size.height * 0.5
	return NSPoint(x,y)

class ReplaceAllPathsWithComponent( object ):
	alignments = ("Align over BBox Center", "Align with BBox Origin (Bottom Left)", "Scale into BBox")
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 160
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Replace all Paths with Component", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.ReplaceAllPathsWithComponent.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15, 12, -15, 14), "Replace each path in the current font with component:", sizeStyle='small' )
		
		self.w.componentPicker = vanilla.ComboBox( (15, 11+20, -50, 19), (), sizeStyle='small', completes=True, continuous=False, callback=self.SavePreferences )
		self.w.update = vanilla.SquareButton((-40, 12+20, -15, 18), u"↺", sizeStyle='small', callback=self.updateCurrentGlyphs )
		
		self.w.text_2 = vanilla.TextBox( (15, 14+45, 120, 14), "Component Position:", sizeStyle='small' )
		self.w.align = vanilla.PopUpButton( (140, 12+45, -15, 17), self.alignments, callback=self.SavePreferences, sizeStyle='small' )
		
		self.w.onlySelectedGlyphs = vanilla.CheckBox( (15, 12+70, -15, 30), "Replace in selected glyphs only", value=False, callback=self.SavePreferences, sizeStyle='small' )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Replace", sizeStyle='regular', callback=self.ReplaceAllPathsWithComponentMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Replace all Paths with Component' could not load preferences. Will resort to defaults"
		
		self.updateCurrentGlyphs(None)
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def updateCurrentGlyphs(self, sender):
		currentFont = Glyphs.font
		currentGlyphs = [g.name for g in currentFont.glyphs]
		self.w.componentPicker.setItems( currentGlyphs )
		
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.ReplaceAllPathsWithComponent.align"] = self.w.align.get()
			Glyphs.defaults["com.mekkablue.ReplaceAllPathsWithComponent.onlySelectedGlyphs"] = self.w.onlySelectedGlyphs.get()
			Glyphs.defaults["com.mekkablue.ReplaceAllPathsWithComponent.componentPicker"] = self.w.componentPicker.get()
		except:
			import traceback
			print traceback.format_exc()
			return False
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.ReplaceAllPathsWithComponent.align", 0)
			Glyphs.registerDefault("com.mekkablue.ReplaceAllPathsWithComponentMain.onlySelectedGlyphs", False)
			Glyphs.registerDefault("com.mekkablue.ReplaceAllPathsWithComponentMain.componentPicker", "")
			self.w.align.set( Glyphs.defaults["com.mekkablue.ReplaceAllPathsWithComponent.align"] )
			self.w.onlySelectedGlyphs.set( bool(Glyphs.defaults["com.mekkablue.ReplaceAllPathsWithComponentMain.onlySelectedGlyphs"]) )
			self.w.componentPicker.set( Glyphs.defaults["com.mekkablue.ReplaceAllPathsWithComponentMain.componentPicker"] )
		except:
			import traceback
			print traceback.format_exc()
			return False
		return True
	
	def ReplaceAllPathsWithComponentMain( self, sender ):
		try:
			thisFont = Glyphs.font # frontmost font
			masterID = thisFont.selectedFontMaster.id

			if Glyphs.defaults["com.mekkablue.ReplaceAllPathsWithComponentMain.onlySelectedGlyphs"]:
				# active layers of currently selected glyphs
				layers = thisFont.selectedLayers 
			else:
				# all layers of the current font master
				layers = [g.layers[masterID] for g in thisFont.glyphs]
			
			componentName = Glyphs.defaults["com.mekkablue.ReplaceAllPathsWithComponent.componentPicker"]
			alignment = Glyphs.defaults["com.mekkablue.ReplaceAllPathsWithComponent.align"]
			
			componentGlyph = thisFont.glyphs[componentName]
			componentLayer = componentGlyph.layers[masterID]
			componentBounds = componentLayer.bounds
			componentCenter = centerOfRect( componentBounds )
			
			for thisLayer in layers:
				thisLayer.contentToBackgroundCheckSelection_keepOldBackground_(False,False)
				for thisPath in thisLayer.paths:
					pathBounds = thisPath.bounds
					component = GSComponent(componentName)
					thisLayer.components.append(component)
					
					if alignment == 0:
						# Align over BBox Center
						pathCenter = centerOfRect(pathBounds)
						xMove = pathCenter.x - componentCenter.x
						yMove = pathCenter.y - componentCenter.y
						component.position = NSPoint( xMove, yMove )
					elif alignment == 1:
						# Align with BBox Origin (Bottom Left)
						xMove = pathBounds.origin.x - componentBounds.origin.x
						yMove = pathBounds.origin.y - componentBounds.origin.y
						component.position = NSPoint( xMove, yMove )
						
					else:
						# Scale into BBox
						pass
					
				thisLayer.paths = None
			
			if not self.SavePreferences( self ):
				print "Note: 'Replace all Paths with Component' could not write preferences."
			
			
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Replace all Paths with Component Error: %s" % e
			import traceback
			print traceback.format_exc()

ReplaceAllPathsWithComponent()