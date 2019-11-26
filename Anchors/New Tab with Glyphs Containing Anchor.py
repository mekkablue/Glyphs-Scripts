#MenuTitle: New Tab with Glyphs Containing Anchor
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
Opens a new tab with all glyphs containing a specific anchor.
"""

import vanilla


class NewTabWithAnchor( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 160
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"New Tab with Anchor", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.NewTabWithAnchor.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15, 15, 100, 14), "Look for anchor", sizeStyle='small' )
		self.w.anchorName = vanilla.EditText( (110, 12, -15, 20), "ogonek", sizeStyle = 'small')
		self.w.text_2 = vanilla.TextBox( (15, 38, -15, 14), "and open a tab with all glyphs containing it.", sizeStyle='small' )
		
		self.w.allLayers = vanilla.CheckBox( (15, 60, -15, 20), "Look for anchor an all layers (otherwise only on current master)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.keepWindowOpen = vanilla.CheckBox( (15, 80, -15, 20), "Keep window open", value=False, callback=self.SavePreferences, sizeStyle='small' )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Open Tab", sizeStyle='regular', callback=self.NewTabWithAnchorMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'New Tab with Anchor' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.NewTabWithAnchor.anchorName"] = self.w.anchorName.get()
			Glyphs.defaults["com.mekkablue.NewTabWithAnchor.allLayers"] = self.w.allLayers.get()
			Glyphs.defaults["com.mekkablue.NewTabWithAnchor.keepWindowOpen"] = self.w.keepWindowOpen.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.NewTabWithAnchor.anchorName", "ogonek")
			Glyphs.registerDefault("com.mekkablue.NewTabWithAnchor.allLayers", "0")
			Glyphs.registerDefault("com.mekkablue.NewTabWithAnchor.keepWindowOpen", "0")
			self.w.anchorName.set( Glyphs.defaults["com.mekkablue.NewTabWithAnchor.anchorName"] )
			self.w.allLayers.set( Glyphs.defaults["com.mekkablue.NewTabWithAnchor.allLayers"] )
			self.w.keepWindowOpen.set( Glyphs.defaults["com.mekkablue.NewTabWithAnchor.keepWindowOpen"] )
		except:
			return False
			
		return True

	def layerContainsAnchor( self, thisLayer, anchorName ):
		print("%s on %s" % (anchorName, thisLayer.name))
		anchorNames = [a.name for a in thisLayer.anchors]
		if anchorName in anchorNames:
			return True
		return False
		
	def glyphContainsAnchor( self, thisGlyph, anchorName, masterIdToBeChecked ):
		if masterIdToBeChecked:
			masterLayer = thisGlyph.layers[masterIdToBeChecked]
			return self.layerContainsAnchor( masterLayer, anchorName )
		else:
			for thisLayer in thisGlyph.layers:
				if self.layerContainsAnchor( thisLayer, anchorName ):
					return True
			return False
	
	def errMsg(self, errorMessage):
		message = "The script 'New Tab with Anchor' encountered the following error: %s" % errorMessage
		Message(title="New Tab with Anchor Error", message=message, OKButton=None)

	def NewTabWithAnchorMain( self, sender ):
		try:
			anchorName = self.w.anchorName.get()
			if anchorName:
				listOfAllGlyphsContainingAnchor = []
				thisFont = Glyphs.font # frontmost font
				masterId = None
				if self.w.allLayers.get():
					masterId = thisFont.selectedFontMaster.id # active master id
			
				# go through all glyphs and look for anchor:
				for thisGlyph in thisFont.glyphs:
					if self.glyphContainsAnchor( thisGlyph, anchorName, masterId ):
						listOfAllGlyphsContainingAnchor.append( thisGlyph.name )
				
				# create string with slash-escaped names:
				glyphNameString = "/" + "/".join(listOfAllGlyphsContainingAnchor)
				thisFont.newTab( glyphNameString )
			
			
				if not self.SavePreferences( self ):
					print("Note: 'New Tab with Anchor' could not write preferences.")
			
				if not self.w.keepWindowOpen.get():
					self.w.close() # closes window
			else:
				self.errMsg(
					"No anchor name specified. Please enter an anchor name before pressing the button."
				)
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("New Tab with Anchor Error: %s" % e)

NewTabWithAnchor()