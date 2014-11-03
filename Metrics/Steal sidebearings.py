#MenuTitle: Steal sidebearings from font
# -*- coding: utf-8 -*-
__doc__="""
Copy sidebearings from one font to another.
"""

import vanilla
windowHeight = 185

class MetricsCopy( object ):
	"""GUI for copying glyph metrics from one font to another"""
	
	def __init__( self ):
		self.w = vanilla.FloatingWindow( (400, windowHeight), "Steal sidebearings", minSize=(350, windowHeight), maxSize=(650, windowHeight), autosaveName="com.mekkablue.MetricsCopy.mainwindow" )
		
		self.w.text_anchor = vanilla.TextBox( (15, 12+2, 130, 17), "Copy metrics from:", sizeStyle='small')
		self.w.from_font = vanilla.PopUpButton( (150, 12, -15, 17), self.listOfFonts(isSourceFont=True), sizeStyle='small', callback=self.buttonCheck)
		
		self.w.text_value = vanilla.TextBox( (15, 12+2+25, 130, 17), "To selected glyphs in:", sizeStyle='small')
		self.w.to_font = vanilla.PopUpButton( (150, 12+25, -15, 17), self.listOfFonts(isSourceFont=False), sizeStyle='small', callback=self.buttonCheck)
		
		self.w.lsb   = vanilla.CheckBox( ( 17, 12+50, 80, 20), "LSB", value=True, callback=self.buttonCheck, sizeStyle='small' )
		self.w.rsb   = vanilla.CheckBox( (97, 12+50, 80, 20), "RSB", value=True, callback=self.buttonCheck, sizeStyle='small' )
		self.w.width = vanilla.CheckBox( (177, 12+50, 80, 20), "Width", value=False, callback=self.buttonCheck, sizeStyle='small' )
		
		self.w.ignoreSuffixes  = vanilla.CheckBox( (15+2, 12+75, -15, 20), "Ignore dotsuffix:", value=False, sizeStyle='small', callback=self.buttonCheck )
		self.w.suffixToBeIgnored = vanilla.EditText( (150, 12+75, -15, 20), ".alt", sizeStyle = 'small')

		self.w.keepWindowOpen  = vanilla.CheckBox( (15+2, 12+100, -15, 20), "Keep this window open", value=False, sizeStyle='small' )
		
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
			
		# Both RSB and Width must not be on:
		if sender:
			if sender == self.w.rsb:
				target = self.w.width
			elif sender == self.w.width:
				target = self.w.rsb
			
			if sender.get() and target.get():
				target.set( not sender.get() )
		
		if not self.SavePreferences( self ):
			self.outputError( "Could not save preferences." )
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.MetricsCopy.ignoreSuffixes"] = self.w.ignoreSuffixes.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.suffixToBeIgnored"] = self.w.suffixToBeIgnored.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.rsb"] = self.w.rsb.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.lsb"] = self.w.lsb.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.width"] = self.w.width.get()
			return True
		except:
			return False

	def LoadPreferences( self ):
		try:
			self.w.ignoreSuffixes.set( Glyphs.defaults["com.mekkablue.MetricsCopy.ignoreSuffixes"] )
			self.w.suffixToBeIgnored.set( Glyphs.defaults["com.mekkablue.MetricsCopy.suffixToBeIgnored"] )
			self.w.lsb.set( Glyphs.defaults["com.mekkablue.MetricsCopy.lsb"] )
			self.w.rsb.set( Glyphs.defaults["com.mekkablue.MetricsCopy.rsb"] )
			self.w.width.set( Glyphs.defaults["com.mekkablue.MetricsCopy.width"] )
			return True
		except:
			return False
	
	def copyMetrics(self, sender):
		fromFont = self.w.from_font.getItems()[ self.w.from_font.get() ]
		toFont   = self.w.to_font.getItems()[ self.w.to_font.get() ]
		ignoreSuffixes = self.w.ignoreSuffixes.get()
		lsbIsSet = self.w.lsb.get()
		rsbIsSet = self.w.rsb.get()
		widthIsSet = self.w.width.get()
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
				
				if lsbIsSet:
					thisLayer.setLSB_( sourceLayer.LSB )
				if rsbIsSet:
					thisLayer.setRSB_( sourceLayer.RSB )
				if widthIsSet:
					thisLayer.setWidth_( sourceLayer.width )

				print "     %i <- %s -> %i (w: %i)" % ( thisLayer.LSB, glyphName, thisLayer.RSB, thisLayer.width )
			except Exception, e:
				if "'objc.native_selector' object has no attribute 'name'" not in e: # CR in the selection string
					print "Error:", e
		
		if not self.w.keepWindowOpen.get():
			self.w.close()
		
MetricsCopy()
