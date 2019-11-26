#MenuTitle: Remove Non-Standard Anchors from Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
Removes all anchors from a glyph that should not be there by default, e.g., ogonek from J.
"""

import vanilla

class RemoveNonStandardAnchors( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 400
		windowHeight = 170
		windowWidthResize  = 0 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Remove Non-Standard Anchors from Selected Glyphs", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.RemoveNonStandardAnchors.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		inset = 10
		currentHeight = 8; self.w.text_1 = vanilla.TextBox( (inset, currentHeight+2, -inset, 28), "Removes anchors from selected glyphs, that should not be there by default, like ogonek from J.", sizeStyle='small' )
		currentHeight += 35; self.w.keepExtensions = vanilla.CheckBox( (inset, currentHeight, -inset, 20), "Keep underscore variants of standard anchors (e.g. top_low)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		currentHeight += 20; self.w.keepExitAndEntry = vanilla.CheckBox( (inset, currentHeight, -inset, 20), "Keep exit and entry anchors", value=False, callback=self.SavePreferences, sizeStyle='small' )
		currentHeight += 20; self.w.keepCarets = vanilla.CheckBox( (inset, currentHeight, -inset, 20), "Keep caret anchors (only in ligatures)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		currentHeight += 20; self.w.keepNoDefaults = vanilla.CheckBox( (inset, currentHeight, -inset, 20), "Ignore glyphs that have no default anchors", value=False, callback=self.SavePreferences, sizeStyle='small' )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Remove", sizeStyle='regular', callback=self.RemoveNonStandardAnchorsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Remove Non-Standard Anchors' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.RemoveNonStandardAnchors.keepExtensions"] = self.w.keepExtensions.get()
			Glyphs.defaults["com.mekkablue.RemoveNonStandardAnchors.keepExitAndEntry"] = self.w.keepExitAndEntry.get()
			Glyphs.defaults["com.mekkablue.RemoveNonStandardAnchors.keepCarets"] = self.w.keepCarets.get()
			Glyphs.defaults["com.mekkablue.RemoveNonStandardAnchors.keepNoDefaults"] = self.w.keepNoDefaults.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.RemoveNonStandardAnchors.keepExtensions", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveNonStandardAnchors.keepExitAndEntry", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveNonStandardAnchors.keepCarets", 1)
			Glyphs.registerDefault("com.mekkablue.RemoveNonStandardAnchors.keepNoDefaults", 0)
			self.w.keepExtensions.set( Glyphs.defaults["com.mekkablue.RemoveNonStandardAnchors.keepExtensions"] )
			self.w.keepExitAndEntry.set( Glyphs.defaults["com.mekkablue.RemoveNonStandardAnchors.keepExitAndEntry"] )
			self.w.keepCarets.set( Glyphs.defaults["com.mekkablue.RemoveNonStandardAnchors.keepCarets"] )
			self.w.keepNoDefaults.set( Glyphs.defaults["com.mekkablue.RemoveNonStandardAnchors.keepNoDefaults"] )
		except:
			return False
			
		return True

	def RemoveNonStandardAnchorsMain( self, sender ):
		try:
			thisFont = Glyphs.font # frontmost font
			listOfSelectedLayers = thisFont.selectedLayers # active layers of currently selected glyphs
			for thisLayer in listOfSelectedLayers: # loop through selected layers
				thisGlyph = thisLayer.parent
				
				# determine default anchors for this glyphs:
				if thisGlyph.glyphInfo.anchors == None:
					defaultAnchors = []
				else:
					defaultAnchors = [a for a in thisGlyph.glyphInfo.anchors]
				
				# clean up default anchor names (top@ascender --> top)
				for i in range(len(defaultAnchors)):
					defaultAnchor = defaultAnchors[i]
					if "@" in defaultAnchor:
						defaultAnchors[i] = defaultAnchor[:defaultAnchor.find("@")]
				
				# determine if we need to remove anchors at all:
				if defaultAnchors or (not defaultAnchors and not Glyphs.defaults["com.mekkablue.RemoveNonStandardAnchors.keepNoDefaults"] ):

					# step through layers:
					for currentLayer in thisGlyph.layers:
						currentAnchorNames = [a.name for a in currentLayer.anchors]
						for currentAnchorName in currentAnchorNames:
							if not currentAnchorName in defaultAnchors:
								# anchor not in defaults for this glyph:
								keepThisAnchor = False
								
								# see if exceptions apply:
								if Glyphs.defaults["com.mekkablue.RemoveNonStandardAnchors.keepExtensions"] and "_" in currentAnchorName and currentAnchorName[:currentAnchorName.find("_")] in defaultAnchors:
									keepThisAnchor = True
								if Glyphs.defaults["com.mekkablue.RemoveNonStandardAnchors.keepExitAndEntry"] and (currentAnchorName in ("exit","entry") or currentAnchorName[1:] in ("exit","entry")):
									keepThisAnchor = True
								if Glyphs.defaults["com.mekkablue.RemoveNonStandardAnchors.keepCarets"] and currentAnchorName.startswith("caret") and (thisGlyph.subCategory=="Ligature" or "_" in thisGlyph.name[1:]):
									keepThisAnchor = True
								
								# Delete if need be:
								if not keepThisAnchor:
									print("Glyph %s, layer '%s': deleting anchor %s" % ( thisGlyph.name, currentLayer.name, currentAnchorName ))
									del currentLayer.anchors[currentAnchorName]
			
			if not self.SavePreferences( self ):
				print("Note: 'Remove Non-Standard Anchors' could not write preferences.")
			
			self.w.close() # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Non-Standard Anchors Error: %s" % e)
			import traceback
			print(traceback.format_exc())

RemoveNonStandardAnchors()