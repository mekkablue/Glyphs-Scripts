#MenuTitle: Steal sidebearings from font
"""Copy sidebearings from one font to another."""

import vanilla

class MetricsCopy(object):
	"""GUI for copying glyph metrics from one font to another"""
	def __init__(self):
		self.w = vanilla.FloatingWindow((400, 70), "Steal sidebearings")
		
		self.w.text_anchor = vanilla.TextBox((15, 12+2, 130, 14), "Copy metrics from:", sizeStyle='small')
		self.w.from_font = vanilla.PopUpButton((150, 12, 150, 17), self.GetFonts(isSourceFont=True), sizeStyle='small', callback=self.buttonCheck)
		
		self.w.text_value = vanilla.TextBox((15, 12+2+25, 130, 14), "To selected glyphs in:", sizeStyle='small')
		self.w.to_font = vanilla.PopUpButton((150, 12+25, 150, 17), self.GetFonts(isSourceFont=False), sizeStyle='small', callback=self.buttonCheck)

		self.w.copybutton = vanilla.Button((-80, 12+25, -15, 17), "Copy", sizeStyle='small', callback=self.copyMetrics)
		self.w.setDefaultButton( self.w.copybutton )

		self.w.open()
		self.buttonCheck(None)
		
	def GetFonts(self, isSourceFont):
		myFontList = [ "%s - %s" % ( x.font.familyName, x.selectedFontMaster().name ) for x in Glyphs.orderedDocuments() ]

		if isSourceFont:
			myFontList.reverse()
		
		return myFontList
	
	def buttonCheck(self, sender):
		fromFont = self.w.from_font.getItems()[ self.w.from_font.get() ]
		toFont   = self.w.to_font.getItems()[ self.w.to_font.get() ]

		if fromFont == toFont:
			self.w.copybutton.enable( onOff=False )
		else:
			self.w.copybutton.enable( onOff=True )
	
	def copyMetrics(self, sender):
		fromFont = self.w.from_font.getItems()[ self.w.from_font.get() ]
		toFont   = self.w.to_font.getItems()[ self.w.to_font.get() ]
		
		Doc_source      = [ x for x in Glyphs.orderedDocuments() if ("%s - %s" % ( x.font.familyName, x.selectedFontMaster().name )) == fromFont ][0]
		Master_source   = Doc_source.selectedFontMaster().id
		Font_source     = Doc_source.font
		Font_target     = [ x.font for x in Glyphs.orderedDocuments() if ("%s - %s" % ( x.font.familyName, x.selectedFontMaster().name )) == toFont ][0]
		Glyphs_selected = [x for x in Font_target.parent.selectedLayers()]
		
		print "Copying", len(Glyphs_selected), "glyph metrics from", Font_source.familyName, "to", Font_target.familyName, ":"
		
		for thisLayer in Glyphs_selected:
			try:
				glyphName = thisLayer.parent.name
				sourceLayer = Font_source.glyphs[ glyphName ].layers[ Master_source ]
			
				thisLayer.setLSB_( sourceLayer.LSB )
				thisLayer.setRSB_( sourceLayer.RSB )
			
				print "   ", thisLayer.LSB, "<-", glyphName, "->", thisLayer.RSB
			except Exception, e:
				if "'objc.native_selector' object has no attribute 'name'" not in e: # CR in the selection string
					print "Error:", e

		self.w.close()
		
MetricsCopy()
