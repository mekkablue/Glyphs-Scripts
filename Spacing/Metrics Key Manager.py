#MenuTitle: Metrics Key Manager
# -*- coding: utf-8 -*-
__doc__="""
Batch apply metrics keys to the current font.
"""

import vanilla

LeftKeys="""
=H: B D E F I K L N P R Thorn Germandbls M
=O: C G Q
=o: c d e q eth
=h: b k l thorn
=n: idotless m p r 
=|n: u
"""
		
RightKeys="""
=|: A H I M N O T U V W X Y
=O: D
=U: J
=o: b p thorn
=n: h m
=|n: idotless u
"""

class MetricsKeyManager( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 240
		windowWidthResize  = 1000 # user can resize width by this value
		windowHeightResize = 1000 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Metrics Key Manager", # window title
			minSize = ( windowWidth, windowHeight-100 ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.MetricsKeyManager.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight, boxHeight = self.getMeasurements()
		
		self.w.LeftMetricsKeysText = vanilla.TextBox( (inset, linePos+2, 70, 14), u"Left Keys:", sizeStyle='small', selectable=True )
		self.w.LeftMetricsKeys = vanilla.EditText( (inset+70, linePos, -inset, boxHeight), "", callback=self.SavePreferences, sizeStyle='small' )

		linePos += boxHeight + 10
		self.w.RightMetricsKeysText = vanilla.TextBox( (inset, linePos+2, 70, 14), u"Right Keys:", sizeStyle='small', selectable=True )
		self.w.RightMetricsKeys = vanilla.EditText( (inset+70, linePos, -inset, boxHeight), "", callback=self.SavePreferences, sizeStyle='small' )
		
		for editField in (self.w.LeftMetricsKeys, self.w.RightMetricsKeys):
			editField.getNSTextField().setToolTip_(u"Enter a metrics key like '=H', followed by a colon (:), followed by glyph names, spearated by space, comma, or any other separator that cannot be part of a glyph name. (Glyph names can contain A-Z, a-z, 0-9, period, underscore and hyphen.)\nExample: ‘=H: B D E F’.")
		
		# Run Button:
		self.w.resetButton = vanilla.Button( (-180-inset, -20-inset, -inset-90, -inset), u"⟲ Reset", sizeStyle='regular', callback=self.SetDefaults )
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Apply", sizeStyle='regular', callback=self.MetricsKeyManagerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Metrics Key Manager' could not load preferences. Will resort to defaults"

		# Bind resizing method:
		self.w.bind("resize", self.windowResize)

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def getMeasurements(self, sender=None):
		lineHeight = 22
		currentWindowHeight = self.w.getPosSize()[3]
		boxHeight = currentWindowHeight/2 - lineHeight*1.5
		return 12, 15, lineHeight, boxHeight
	
	def windowResize(self, sender=None):
		linePos, inset, lineHeight, boxHeight = self.getMeasurements()
		
		self.w.LeftMetricsKeysText.setPosSize( (inset, linePos+2, 70, 14) )
		self.w.LeftMetricsKeys.setPosSize( (inset+70, linePos, -inset, boxHeight) )

		linePos += boxHeight + 10
		self.w.RightMetricsKeysText.setPosSize( (inset, linePos+2, 70, 14) )
		self.w.RightMetricsKeys.setPosSize( (inset+70, linePos, -inset, boxHeight) )
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.MetricsKeyManager.LeftMetricsKeys"] = self.w.LeftMetricsKeys.get()
			Glyphs.defaults["com.mekkablue.MetricsKeyManager.RightMetricsKeys"] = self.w.RightMetricsKeys.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.MetricsKeyManager.LeftMetricsKeys", LeftKeys)
			Glyphs.registerDefault("com.mekkablue.MetricsKeyManager.RightMetricsKeys", RightKeys)
			self.w.LeftMetricsKeys.set( Glyphs.defaults["com.mekkablue.MetricsKeyManager.LeftMetricsKeys"] )
			self.w.RightMetricsKeys.set( Glyphs.defaults["com.mekkablue.MetricsKeyManager.RightMetricsKeys"] )
		except:
			return False
			
		return True
		
	def SetDefaults(self, sender=None):
		self.w.RightMetricsKeys.set( RightKeys.strip() )
		self.w.LeftMetricsKeys.set( LeftKeys.strip() )
		
		# update settings to the latest user input:
		if not self.SavePreferences( self ):
			print "Note: 'Metrics Key Manager' could not write preferences."
		
	
	def parseGlyphNames(self, glyphNameText):
		possibleChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-_"
		glyphNames = []
		currName = ""
		for currChar in glyphNameText.strip()+" ":
			if currChar in possibleChars:
				currName += currChar
			else:
				if currName:
					glyphNames.append(currName)
					currName = ""
		return tuple(glyphNames)
	
	def parseKeyText(self, keyText):
		parseDict = {}
		keyText = keyText.strip()
		for line in keyText.splitlines():
			line = line.strip()
			if line and ":" in line:
				key, glyphNameText = line.split(":")[:2]
				parseDict[key] = self.parseGlyphNames( glyphNameText )
		return parseDict
	
	def MetricsKeyManagerMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print "Note: 'Metrics Key Manager' could not write preferences."
			
			thisFont = Glyphs.font # frontmost font
			if not thisFont:
				Message(title="Metrics Key Manager Error", message="No font open. Metrics keys can only be applied to the frontmost font.", OKButton=None)
			else:
				print "Metrics Key Manager Report for %s" % thisFont.familyName
				print thisFont.filepath
				print
			
				# to be turned into selectable options:
				# delete all existing keys, respect existing keys, overwrite existing keys
				respectExistingKeys = False
				deleteExistingKeys = False
				includeNonexportingGlyphs = True
				shouldOpenTabWithAffectedGlyphs = False
			
				LeftKeysText = Glyphs.defaults["com.mekkablue.MetricsKeyManager.LeftMetricsKeys"]
				leftDict = self.parseKeyText(LeftKeysText)
			
				RightKeysText = Glyphs.defaults["com.mekkablue.MetricsKeyManager.RightMetricsKeys"]
				rightDict = self.parseKeyText(RightKeysText)
				
				affectedGlyphs = []
				
				for key in leftDict.keys():
					print u"⬅️ Setting Left Key: '%s'" % key
					glyphNames = leftDict[key]
					for glyphName in glyphNames:
						glyph = thisFont.glyphs[glyphName]
						if glyph:
							glyph.leftMetricsKey = key
							affectedGlyphs.append(glyphName)
						else:
							print u"  ❌ Glyph '%s' not in font. Skipped." % glyphName

				for key in rightDict.keys():
					print u"➡️ Right Key: '%s'" % key
					glyphNames = rightDict[key]
					for glyphName in glyphNames:
						glyph = thisFont.glyphs[glyphName]
						if glyph:
							glyph.rightMetricsKey = key
							affectedGlyphs.append(glyphName)
						else:
							print u"  ❌ Glyph '%s' not in font. Skipped." % glyphName
				
				if affectedGlyphs and shouldOpenTabWithAffectedGlyphs:
					affectedGlyphs = set(affectedGlyphs)
					thisFont.newTab( "/"+"/".join(affectedGlyphs) )
					
			
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Metrics Key Manager Error: %s" % e
			import traceback
			print traceback.format_exc()

MetricsKeyManager()