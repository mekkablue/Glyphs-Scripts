#MenuTitle: Build Small Figures
# -*- coding: utf-8 -*-
__doc__="""
Takes a default set of figures (e.g., dnom), and derives the others (.numr, superior/.sups, inferiour/.sinf, .subs) as component copies. Respects the italic angle.
"""

import vanilla, math

def italicize( thisPoint, italicAngle=0.0, pivotalY=0.0 ):
	"""
	Returns the italicized position of an NSPoint 'thisPoint'
	for a given angle 'italicAngle' and the pivotal height 'pivotalY',
	around which the italic slanting is executed, usually half x-height.
	Usage: myPoint = italicize(myPoint,10,xHeight*0.5)
	"""
	x,y = thisPoint
	yOffset = y - pivotalY # calculate vertical offset
	italicAngle = math.radians( italicAngle ) # convert to radians
	tangens = math.tan( italicAngle ) # math.tan needs radians
	horizontalDeviance = tangens * yOffset # vertical distance from pivotal point
	x += horizontalDeviance # x of point that is yOffset from pivotal point
	return NSPoint(x,y)


class smallFigureBuilder( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 400
		windowHeight = 210
		windowWidthResize  = 400 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Build Small Figures", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.smallFigureBuilder.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		inset, linePos, lineHeight = 15, 12, 27
		
		self.w.text_0 = vanilla.TextBox( (inset, linePos+2, -inset, 60), "Takes the Default Suffix figures (e.g. .dnom) and builds compound copies with suffixes in Derivatives (comma-separated suffix:yOffset pairs). Respects Italic Angle when placing components.", sizeStyle='small', selectable=True )
		linePos += lineHeight*2.2
		
		
		self.w.text_1 = vanilla.TextBox( (inset-1, linePos+3, 100, 14), "Default Suffix:", sizeStyle='small' )
		self.w.default = vanilla.EditText( (100, linePos, -inset, 20), "", sizeStyle = 'small', callback=self.SavePreferences )
		linePos += lineHeight
		
		self.w.text_2 = vanilla.TextBox( (inset-1, linePos+3, 75, 14), "Derivatives:", sizeStyle='small' )
		self.w.derive = vanilla.EditText( (100, linePos, -inset, 20), "", sizeStyle = 'small', callback=self.SavePreferences )
		linePos += lineHeight
		
		self.w.currentMasterOnly = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Only apply to current master (uncheck for all masters)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		
		# Run Button:
		self.w.reportButton = vanilla.Button((-200-15, -20-15, -95, -15), "Open Report", sizeStyle='regular', callback=self.openMacroWindow )
		self.w.runButton = vanilla.Button((-70-15, -20-15, -15, -15), "Build", sizeStyle='regular', callback=self.smallFigureBuilderMain )
		self.w.setDefaultButton( self.w.runButton )
		
		
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Build Small Figures' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.smallFigureBuilder.default"] = self.w.default.get()
			Glyphs.defaults["com.mekkablue.smallFigureBuilder.derive"] = self.w.derive.get()
			Glyphs.defaults["com.mekkablue.smallFigureBuilder.currentMasterOnly"] = self.w.currentMasterOnly.get()
			return True
		except:
			return False

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault( "com.mekkablue.smallFigureBuilder.default", ".dnom" )
			Glyphs.registerDefault( "com.mekkablue.smallFigureBuilder.derive", ".numr:276, superior:376, inferior:-124" )
			Glyphs.registerDefault( "com.mekkablue.smallFigureBuilder.currentMasterOnly", 0 )
			self.w.default.set( Glyphs.defaults["com.mekkablue.smallFigureBuilder.default"] )
			self.w.derive.set( Glyphs.defaults["com.mekkablue.smallFigureBuilder.derive"] )
			self.w.currentMasterOnly.set( Glyphs.defaults["com.mekkablue.smallFigureBuilder.currentMasterOnly"] )
			return True
		except:
			return False
	
	def openMacroWindow( self, sender ):
		Glyphs.showMacroWindow()
	
	def smallFigureBuilderMain( self, sender ):
		try:
			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			
			thisFont = Glyphs.font # frontmost font
			default = Glyphs.defaults["com.mekkablue.smallFigureBuilder.default"].strip()
			derive = Glyphs.defaults["com.mekkablue.smallFigureBuilder.derive"]
			figures = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
			
			offsets={}
			for suffixPair in [pair.split(":") for pair in derive.split(",")]:
				suffix = suffixPair[0].strip()
				value = float(suffixPair[1].strip())
				offsets[suffix] = value
			
			# go through
			for fig in figures:
				# determine default glyph:
				defaultGlyphName = "%s%s" % (fig,default)
				defaultGlyph = thisFont.glyphs[defaultGlyphName]
				
				if not defaultGlyph:
					print "\nNot found: %s" % defaultGlyphName
				else:
					print "\nDeriving from %s:" % defaultGlyphName
					for deriveSuffix in offsets:
						# create or overwrite derived glyph:
						deriveGlyphName = "%s%s" % (fig,deriveSuffix)
						deriveGlyph = thisFont.glyphs[deriveGlyphName]
						if not deriveGlyph:
							deriveGlyph = GSGlyph(deriveGlyphName)
							thisFont.glyphs.append(deriveGlyph)
							print " - creating new glyph %s" % deriveGlyphName
						else:
							print " - overwriting glyph %s" % deriveGlyphName
							
						# copy glyph attributes:
						deriveGlyph.leftKerningGroup = defaultGlyph.leftKerningGroup
						deriveGlyph.rightKerningGroup = defaultGlyph.rightKerningGroup
						
						# reset category & subcategory:
						deriveGlyph.updateGlyphInfo()
						
						# add component on each master layer:
						for thisMaster in thisFont.masters:
							isCurrentMaster = thisMaster is thisFont.selectedFontMaster
							if isCurrentMaster or not Glyphs.defaults["com.mekkablue.smallFigureBuilder.currentMasterOnly"]:
								mID = thisMaster.id
								offset = offsets[deriveSuffix]
								offsetPos = NSPoint(0,offset)
								if thisMaster.italicAngle != 0.0:
									offsetPos = italicize(offsetPos,italicAngle=thisMaster.italicAngle)
								defaultComponent = GSComponent(defaultGlyphName,offsetPos)
								deriveLayer = deriveGlyph.layers[mID]
								deriveLayer.clear()
								deriveLayer.components.append(defaultComponent)
			
			if not self.SavePreferences( self ):
				print "Note: 'Build Small Figures' could not write preferences."
			
			# self.w.close() # delete if you want window to stay open
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Build Small Figures Error: %s" % e
			import traceback
			print traceback.format_exc()

smallFigureBuilder()