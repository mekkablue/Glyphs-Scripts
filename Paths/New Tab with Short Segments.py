#MenuTitle: New Tab with Short Segments
# -*- coding: utf-8 -*-
__doc__="""
Goes through all glyphs in the present font(s), and reports segments shorter than a user-specified distance to the Macro Window, and opens a new tab with affected glyphs. Useful for finding alignment errors in exported OTFs.
"""

import vanilla

class FindShortSegmentsInFont( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 250
		windowHeight = 120
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"New Tab with Short Segments", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.FindShortSegmentsInFont.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15-1, 12+2, 160, 14), "Find segments up to length:", sizeStyle='small' )
		self.w.maxDistance = vanilla.EditText( (175, 12, -15, 15+3), "5", sizeStyle = 'small')
		self.w.allFonts = vanilla.CheckBox( (15, 34, -15, 20), "Include all open fonts", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.selectSegments = vanilla.CheckBox( (15, 54, -15, 20), "Select segments", value=False, callback=self.SavePreferences, sizeStyle='small' )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Find", sizeStyle='regular', callback=self.FindShortSegmentsInFontMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'New Tab with Short Segments' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.FindShortSegmentsInFont.maxDistance"] = self.w.maxDistance.get()
			Glyphs.defaults["com.mekkablue.FindShortSegmentsInFont.allFonts"] = self.w.allFonts.get()
			Glyphs.defaults["com.mekkablue.FindShortSegmentsInFont.selectSegments"] = self.w.selectSegments.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.FindShortSegmentsInFont.maxDistance", "5")
			Glyphs.registerDefault("com.mekkablue.FindShortSegmentsInFont.allFonts", False)
			Glyphs.registerDefault("com.mekkablue.FindShortSegmentsInFont.selectSegments", False)
			self.w.maxDistance.set( Glyphs.defaults["com.mekkablue.FindShortSegmentsInFont.maxDistance"] )
			self.w.allFonts.set( Glyphs.defaults["com.mekkablue.FindShortSegmentsInFont.allFonts"] )
			self.w.selectSegments.set( Glyphs.defaults["com.mekkablue.FindShortSegmentsInFont.selectSegments"] )
		except:
			return False
			
		return True

	def FindShortSegmentsInFontMain( self, sender ):
		try:
			includeAllFonts = bool(Glyphs.defaults["com.mekkablue.FindShortSegmentsInFont.allFonts"])
			fontList = Glyphs.fonts
			if not includeAllFonts:
				fontList = (Glyphs.font) # only frontmost font
			
			selectSegments = Glyphs.defaults["com.mekkablue.FindShortSegmentsInFont.selectSegments"]
			maxDistance = float( Glyphs.defaults["com.mekkablue.FindShortSegmentsInFont.maxDistance"] )
			
			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			Glyphs.showMacroWindow()
			print "Segments shorter than %i units:" % maxDistance
			
			self.w.close()
			
			for thisFont in fontList:
				glyphNamesWithShortSegments = []
				print "\nFONT: %s" % thisFont.familyName
				print "FILE: %s" % thisFont.filepath
				print
				for thisGlyph in thisFont.glyphs:
					for thisLayer in thisGlyph.layers:
						layerCount = 0
						for i, thisPath in enumerate(thisLayer.paths):
							for thisSegment in thisPath.segments:
								firstPoint = thisSegment[0].pointValue()
								segmentLength = distance( firstPoint, thisSegment[len(thisSegment)-1].pointValue() )
								if segmentLength < maxDistance:
									if layerCount == 0:
										print "%s (layer: %s)" % ( thisGlyph.name, thisLayer.name )
										if selectSegments:
											thisLayer.clearSelection()
									
									layerCount += 1
									glyphNamesWithShortSegments.append(thisGlyph.name)
									print "- Segment length %.1f in path %i, at %i %i" % ( segmentLength, i, firstPoint.x, firstPoint.y )
									
									if selectSegments:
										for pointInfo in thisSegment:
											thisPoint = pointInfo.pointValue()
											thisNode = thisLayer.nodeAtPoint_excludeNode_tollerance_(thisPoint,None,0.01)
											thisLayer.selection.append(thisNode)
						if layerCount:
							print "  Total: %i short segments on %s (layer %s)" % ( layerCount, thisGlyph.name, thisLayer.name )
							print
				
				if glyphNamesWithShortSegments:
					tabText = "/" + "/".join(set(glyphNamesWithShortSegments))
					thisFont.newTab(tabText)
					print "Affected glyphs in this font:"
					print tabText
					print
				else:
					print "No glyphs affected in this font. Congrats!"
					print
					
			if not self.SavePreferences( self ):
				print "Note: 'New Tab with Short Segments' could not write preferences."
			
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "New Tab with Short Segments Error: %s" % e

FindShortSegmentsInFont()