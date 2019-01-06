#MenuTitle: Delete Anchors
# -*- coding: utf-8 -*-
__doc__="""
Delete anchors from selected glyphs, or whole font.
"""

import vanilla

class AnchorDeleter( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 240
		windowHeight = 110
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Delete Anchors", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.AnchorDeleter.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.text_1 = vanilla.TextBox( (inset-1, linePos+2, 80, 14), "Delete anchor", sizeStyle='small' )
		self.w.updateButton = vanilla.SquareButton( (-inset-20, linePos, -inset, 18), u"↺", sizeStyle='small', callback=self.updateAnchors )
		self.w.anchorPopup = vanilla.PopUpButton( (inset+80, linePos, -inset-25, 17), self.updateAnchors(None), callback=self.SavePreferences, sizeStyle='small' )
		
		linePos += lineHeight
		self.w.selectedAnchorsOnly = vanilla.CheckBox( (inset, linePos, -inset, 20), "In selected glyphs only", value=False, callback=self.SavePreferences, sizeStyle='small' )

		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Delete", sizeStyle='regular', callback=self.AnchorDeleterMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Delete Anchors' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.AnchorDeleter.anchorPopup"] = self.w.anchorPopup.get()
			Glyphs.defaults["com.mekkablue.AnchorDeleter.selectedAnchorsOnly"] = self.w.selectedAnchorsOnly.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.AnchorDeleter.anchorPopup", 0)
			Glyphs.registerDefault("com.mekkablue.AnchorDeleter.selectedAnchorsOnly", 0)
			if self.w.anchorPopup.get() < len(self.w.anchorPopup.getItems()):
				self.w.anchorPopup.set( Glyphs.defaults["com.mekkablue.AnchorDeleter.anchorPopup"] )
			else:
				self.w.anchorPopup.set( 0 )
			self.w.selectedAnchorsOnly.set( Glyphs.defaults["com.mekkablue.AnchorDeleter.selectedAnchorsOnly"] )
		except:
			return False
			
		return True
	
	def updateAnchors(self, sender):
		collectedAnchorNames = []
		thisFont = Glyphs.font # frontmost font
		if Glyphs.defaults["com.mekkablue.AnchorDeleter.selectedAnchorsOnly"]:
			glyphs = [l.parent for l in thisFont.selectedLayers]
		else:
			glyphs = thisFont.glyphs
		for thisGlyph in glyphs:
			for thisLayer in thisGlyph.layers:
				for thisAnchor in thisLayer.anchors:
					collectedAnchorNames.append( thisAnchor.name )
		uniqueAnchorNames = set(collectedAnchorNames)
		sortedAnchorNames = sorted(list(uniqueAnchorNames))
		try:
			if not Glyphs.defaults["com.mekkablue.AnchorDeleter.anchorPopup"] < len(uniqueAnchorNames):
				Glyphs.defaults["com.mekkablue.AnchorDeleter.anchorPopup"] = 0
			else:
				self.SavePreferences()
		except:
			pass # exit gracefully
		
		if sender == self.w.updateButton:
			self.w.anchorPopup.setItems(sortedAnchorNames)
		else:
			return sortedAnchorNames

	def AnchorDeleterMain( self, sender ):
		try:
			anchorPopupIndex = Glyphs.defaults["com.mekkablue.AnchorDeleter.anchorPopup"]
			anchorsInPopup = self.w.anchorPopup.getItems()
			anchorName = anchorsInPopup[anchorPopupIndex]
			
			if anchorName:
				thisFont = Glyphs.font # frontmost font
				if Glyphs.defaults["com.mekkablue.AnchorDeleter.selectedAnchorsOnly"]:
					glyphs = [l.parent for l in thisFont.selectedLayers]
				else:
					glyphs = thisFont.glyphs
			
				for thisGlyph in glyphs:
					for thisLayer in thisGlyph.layers:
						del thisLayer.anchors[anchorName]

			if not self.SavePreferences( self ):
				print "Note: 'Delete Anchors' could not write preferences."
			
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Anchor Deleter Error: %s" % e
			import traceback
			print traceback.format_exc()

AnchorDeleter()