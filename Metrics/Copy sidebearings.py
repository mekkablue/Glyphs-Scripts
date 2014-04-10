#MenuTitle: Steal sidebearings from font
"""Copy sidebearings from one font to another."""

import vanilla
windowHeight = 160

class MetricsCopy( object ):
	"""GUI for copying glyph metrics from one font to another"""
	
	def __init__( self ):
		self.w = vanilla.FloatingWindow( (400, windowHeight), "Steal sidebearings", minSize=(350, windowHeight), maxSize=(650, windowHeight), autosaveName="com.mekkablue.MetricsCopy.mainwindow" )
		
		self.w.text_anchor = vanilla.TextBox( (15, 12+2, 130, 17), "Copy metrics from:", sizeStyle='small')
		self.w.from_font = vanilla.PopUpButton( (150, 12, -15, 17), self.listOfFonts(isSourceFont=True), sizeStyle='small', callback=self.buttonCheck)
		
		self.w.text_value = vanilla.TextBox( (15, 12+2+25, 130, 17), "To selected glyphs in:", sizeStyle='small')
		self.w.to_font = vanilla.PopUpButton( (150, 12+25, -15, 17), self.listOfFonts(isSourceFont=False), sizeStyle='small', callback=self.buttonCheck)

		self.w.ignoreSuffixes  = vanilla.CheckBox( (15+2, 12+50, -15, 20), "Ignore dotsuffix:", value=False, sizeStyle='small', callback=self.buttonCheck )
		self.w.suffixToBeIgnored = vanilla.EditText( (150, 12+50, -15, 20), ".alt", sizeStyle = 'small')

		self.w.keepWindowOpen  = vanilla.CheckBox( (15+2, 12+75, -15, 20), "Keep this window open", value=False, sizeStyle='small', callback=self.buttonCheck )
		
		self.w.copybutton = vanilla.Button((-80, -32, -15, 17), "Copy", sizeStyle='small', callback=self.copyMetrics)
		self.w.setDefaultButton( self.w.copybutton )
		
		if not self.LoadPreferences( ):
			self.outputError( "Could not load preferences at startup. Will resort to defaults." )
		
		self.w.open()
		self.buttonCheck( None )
		
	def listOfFonts( self, isSourceFont ):
		myFontList = [ "%s - %s" % ( d.font.familyName, d.selectedFontMaster().name ) for d in Glyphs.orderedDocuments() ]
		if isSourceFont:
			myFontList.reverse()
		return myFontList
	
	def outputError( self, errMsg ):
		print "Steal Sidebearings Warning:", errMsg
	
	def buttonCheck( self, sender ):
		# check if both font selection point to the same font
		# and disable action button if they do:
		fromFont = self.w.from_font.getItems()[ self.w.from_font.get() ]
		toFont   = self.w.to_font.getItems()[ self.w.to_font.get() ]
		if fromFont == toFont:
			self.w.copybutton.enable( onOff=False )
		else:
			self.w.copybutton.enable( onOff=True )
		
		# check if checkbox is enabled
		# and sync availability of text box
		suffixCheckBoxChecked = self.w.ignoreSuffixes.get()
		if suffixCheckBoxChecked:
			self.w.suffixToBeIgnored.enable( onOff=True )
		else:
			self.w.suffixToBeIgnored.enable( onOff=False )
		
		if not self.SavePreferences( self ):
			self.outputError( "Could not save preferences." )
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.MetricsCopy.ignoreSuffixes"] = self.w.ignoreSuffixes.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.suffixToBeIgnored"] = self.w.suffixToBeIgnored.get()
			return True
		except:
			return False

	def LoadPreferences( self ):
		try:
			self.w.ignoreSuffixes.set( Glyphs.defaults["com.mekkablue.MetricsCopy.ignoreSuffixes"] )
			self.w.suffixToBeIgnored.set( Glyphs.defaults["com.mekkablue.MetricsCopy.suffixToBeIgnored"] )
			return True
		except:
			return False
	
	def copyMetrics(self, sender):
		fromFont = self.w.from_font.getItems()[ self.w.from_font.get() ]
		toFont   = self.w.to_font.getItems()[ self.w.to_font.get() ]
		ignoreSuffixes = self.w.ignoreSuffixes.get()
		suffixToBeIgnored = self.w.suffixToBeIgnored.get().strip(".")
		
		sourceDoc      = [ d for d in Glyphs.orderedDocuments() if ("%s - %s" % ( d.font.familyName, d.selectedFontMaster().name )) == fromFont ][0]
		sourceMaster   = sourceDoc.selectedFontMaster().id
		sourceFont     = sourceDoc.font
		targetFont     = [ d.font for d in Glyphs.orderedDocuments() if ("%s - %s" % ( d.font.familyName, d.selectedFontMaster().name )) == toFont ][0]
		selectedLayers = [ l for l in targetFont.parent.selectedLayers() ]
		
		print "Copying", len(selectedLayers), "glyph metrics from", sourceFont.familyName, "to", targetFont.familyName, ":"
		
		for thisLayer in selectedLayers:
			try:
				glyphName = thisLayer.parent.name
				
				if ignoreSuffixes:
					# replace suffix in the middle of the name:
					glyphName = glyphName.replace( ".%s." % suffixToBeIgnored, "." )
					
					# replace suffix at the end of the name:
					if glyphName.endswith( ".%s" % suffixToBeIgnored ):
						glyphName = glyphName[:-len(suffixToBeIgnored)-1]
						
				sourceLayer = sourceFont.glyphs[ glyphName ].layers[ sourceMaster ]
				thisLayer.setLSB_( sourceLayer.LSB )
				thisLayer.setRSB_( sourceLayer.RSB )
				print "   ", thisLayer.LSB, "<-", glyphName, "->", thisLayer.RSB
			except Exception, e:
				if "'objc.native_selector' object has no attribute 'name'" not in e: # CR in the selection string
					print "Error:", e
		
		if not self.w.keepWindowOpen.get():
			self.w.close()
		
MetricsCopy()
