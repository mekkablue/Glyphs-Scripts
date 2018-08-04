#MenuTitle: New Tab with Small Paths
# -*- coding: utf-8 -*-
__doc__="""
Finds small paths (smaller tahn a user-definable threshold) in glyphs and open a new tab with affected glyphs.
"""

import vanilla


class FindSmallPaths( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 250
		windowHeight = 190
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Find Small Paths", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.FindSmallPaths.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15, 10, -15, 30), "Open a new tab with glyphs that contain paths with an area smaller than:", sizeStyle='small' )
		self.w.minArea = vanilla.TextBox( (15, 42, -15, 15+3), "1000 square units", sizeStyle = 'small', alignment="center")

		self.w.sliderMin = vanilla.EditText( ( 15, 60-1, 50, 19), "10", sizeStyle='small', callback=self.SliderUpdate )
		self.w.sliderMax = vanilla.EditText( (-15-50, 60-1, -15, 19), "10000", sizeStyle='small', callback=self.SliderUpdate )
		self.w.areaSlider= vanilla.Slider((15+50+10, 60, -15-50-10, 19), value=0.1, minValue=0.0, maxValue=1.0, sizeStyle='small', callback=self.SliderUpdate )
		
		self.w.deleteThemRightAway = vanilla.CheckBox( (15, 80+10, -15, 20), "Delete Small Paths Right Away", value=False, callback=self.CheckBoxUpdate, sizeStyle='small' )
		self.w.afterOverlapRemoval = vanilla.CheckBox( (15, 100+10, -15, 20), "After Decomposition and Overlap Removal (slower)", value=False, callback=self.CheckBoxUpdate, sizeStyle='small' )
		
		
		# Run Button:
		self.w.runButton = vanilla.Button((-120, -20-15, -15, -15), "Open Tab", sizeStyle='regular', callback=self.FindSmallPathsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Find Small Paths' could not load preferences. Will resort to defaults"
		
		self.CheckBoxUpdate(None)
		self.SliderUpdate(None)
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.FindSmallPaths.sliderMin"] = self.w.sliderMin.get()
			Glyphs.defaults["com.mekkablue.FindSmallPaths.sliderMax"] = self.w.sliderMax.get()
			Glyphs.defaults["com.mekkablue.FindSmallPaths.areaSlider"] = float(self.w.areaSlider.get())
			Glyphs.defaults["com.mekkablue.FindSmallPaths.deleteThemRightAway"] = int(self.w.deleteThemRightAway.get())
			Glyphs.defaults["com.mekkablue.FindSmallPaths.afterOverlapRemoval"] = int(self.w.afterOverlapRemoval.get())
		except Exception as e:
			print e
			import traceback
			print traceback.format_exc()
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.FindSmallPaths.sliderMin", "10",)
			Glyphs.registerDefault("com.mekkablue.FindSmallPaths.sliderMax", "100000")
			Glyphs.registerDefault("com.mekkablue.FindSmallPaths.areaSlider", 0.1)
			Glyphs.registerDefault("com.mekkablue.FindSmallPaths.deleteThemRightAway", 0)
			Glyphs.registerDefault("com.mekkablue.FindSmallPaths.afterOverlapRemoval", 0)
			self.w.sliderMin.set( Glyphs.defaults["com.mekkablue.FindSmallPaths.sliderMin"] )
			self.w.sliderMax.set( Glyphs.defaults["com.mekkablue.FindSmallPaths.sliderMax"] )
			self.w.areaSlider.set( float(Glyphs.defaults["com.mekkablue.FindSmallPaths.areaSlider"]) )
			self.w.deleteThemRightAway.set( bool(Glyphs.defaults["com.mekkablue.FindSmallPaths.deleteThemRightAway"]) )
			self.w.afterOverlapRemoval.set( bool(Glyphs.defaults["com.mekkablue.FindSmallPaths.afterOverlapRemoval"]) )
		except Exception as e:
			print e
			import traceback
			print traceback.format_exc()
			return False
			
		return True
	
	def CheckBoxUpdate(self, sender):
		try:
			# mutually exclusive check boxes:
			theOne = self.w.afterOverlapRemoval
			theOther = self.w.deleteThemRightAway
			theOther.enable(not bool(theOne.get()))
			theOne.enable(not bool(theOther.get()))
			
			# Hack as long as vanilla.CheckBox.getNSButton is not implemented:
			if theOne.get():
				theOther.set(False)
			if theOther.get():
				theOne.set(False)
							
			# save prefs:
			if not self.SavePreferences( self ):
				print "Note: 'Find Small Paths' could not write preferences."

			return True
		except Exception as e:
			print e
			import traceback
			print traceback.format_exc()
			return False
		
	def SliderUpdate( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.FindSmallPaths.areaSlider"] = self.w.areaSlider.get()
			minArea = self.CurrentMinArea()
			self.w.minArea.set( "%i"%minArea )
			if sender != self.w.areaSlider:
				if not self.SavePreferences( self ):
					print "Note: 'Find Small Paths' could not write preferences."
			return True
		except:
			return False
	
	def CurrentMinArea(self):
		minimum = float( Glyphs.defaults["com.mekkablue.FindSmallPaths.sliderMin"] )
		maximum = float( Glyphs.defaults["com.mekkablue.FindSmallPaths.sliderMax"] )
		
		# check for integrity of min and max values:
		if minimum < 1.0:
			minimum = 1.0
			self.w.sliderMin.set( "%i"%minimum )

		if maximum < minimum:
			maximum = minimum+10.0
			self.w.sliderMax.set( "%i"%maximum )

		sliderPos = float( Glyphs.defaults["com.mekkablue.FindSmallPaths.areaSlider"] )
		minArea = minimum + sliderPos * (maximum-minimum)
		self.w.minArea.set( "%i square units" % minArea )
		return minArea

	def FindSmallPathsMain( self, sender ):
		try:
			minArea = self.CurrentMinArea()
			smallPathsShouldBeDeleted = Glyphs.defaults["com.mekkablue.FindSmallPaths.deleteThemRightAway" ]
			overlapsShouldBeRemovedFirst = Glyphs.defaults["com.mekkablue.FindSmallPaths.afterOverlapRemoval" ]
			
			glyphsWithSmallPaths = []
			
			thisFont = Glyphs.font # frontmost font
			for thisGlyph in thisFont.glyphs:
				thisGlyph.beginUndo() # begin undo grouping
				for thisLayer in thisGlyph.layers:
					if thisLayer.paths:
						if overlapsShouldBeRemovedFirst:
							checkLayer = thisLayer.copyDecomposedLayer()
							checkLayer.removeOverlap()
							for thisPath in checkLayer.paths:
								if thisPath.area() < minArea:
									glyphsWithSmallPaths.append(thisGlyph.name)
						else:
							for i in range(len(thisLayer.paths))[::-1]:
								thisPath = thisLayer.paths[i]
								if thisPath.area() < minArea:
									glyphsWithSmallPaths.append(thisGlyph.name)
									if smallPathsShouldBeDeleted:
										del thisLayer.paths[i]
				thisGlyph.endUndo()   # end undo grouping
			
			if glyphsWithSmallPaths:
				tabString = "/"+"/".join( set(glyphsWithSmallPaths) )
				thisFont.newTab( tabString )
			else:
				Message(title="No Small Paths Found", message="No glyphs with paths smaller than %i square units found in the frontmost font." % minArea, OKButton="Cool")
			
			# listOfSelectedLayers = thisFont.selectedLayers # active layers of currently selected glyphs
			# for thisLayer in listOfSelectedLayers: # loop through layers
			# 	thisGlyph = thisLayer.parent
			# 	print thisGlyph.name, thisLayer.name
			# 	# output all node coordinates:
			# 	for thisPath in thisLayer.paths:
			# 		for thisNode in thisLayer.nodes:
			# 			print "-- %.1f %.1f" % ( thisNode.x, thisNode.y )
			
			
			
			if not self.SavePreferences( self ):
				print "Note: 'Find Small Paths' could not write preferences."
			
			self.w.close() # delete if you want window to stay open
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Find Small Paths Error: %s" % e

FindSmallPaths()