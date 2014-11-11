#MenuTitle: Find And Replace In Anchor Names
# -*- coding: utf-8 -*-
__doc__="""
Replaces strings in anchor names of all selected glyphs.
"""

import vanilla
import GlyphsApp

class SearchAndReplaceInAnchorNames( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 380
		windowHeight = 40
		windowWidthResize  = 0 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Search And Replace In Anchor Names", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.SearchAndReplaceInAnchorNames.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.textSearch = vanilla.TextBox((15, 12+2, 67, 14), "Search for:", sizeStyle='small')
		self.w.searchFor = vanilla.EditText((15+67, 12, 60, 19), "tip", sizeStyle='small')
		
		self.w.textReplace = vanilla.TextBox((150, 12+2, 67, 14), "Replace by:", sizeStyle='small')
		self.w.replaceBy = vanilla.EditText((150+67, 12, 60, 19), "top", sizeStyle='small')

		self.w.replaceButton = vanilla.Button((-80, 12+1, -15, 17), "Replace", sizeStyle='small', callback=self.SearchAndReplaceInAnchorNamesMain)
		self.w.setDefaultButton( self.w.replaceButton )
				
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Search And Replace In Anchor Names' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.SearchAndReplaceInAnchorNames.searchFor"] = self.w.searchFor.get()
			Glyphs.defaults["com.mekkablue.SearchAndReplaceInAnchorNames.replaceBy"] = self.w.replaceBy.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			self.w.searchFor.set( Glyphs.defaults["com.mekkablue.SearchAndReplaceInAnchorNames.searchFor"] )
			self.w.replaceBy.set( Glyphs.defaults["com.mekkablue.SearchAndReplaceInAnchorNames.replaceBy"] )
		except:
			return False
			
		return True

	def SearchAndReplaceInAnchorNamesMain( self, sender ):
		try:
			searchString = self.w.searchFor.get()
			replaceString = self.w.replaceBy.get()
			
			thisFont = Glyphs.font # frontmost font
			listOfSelectedLayers = thisFont.selectedLayers # active layers of currently selected glyphs
						
			for thisLayer in listOfSelectedLayers: # loop through layers
				thisGlyph = thisLayer.parent
				reportString = "Anchors renamed in %s:" % thisGlyph.name
				displayReportString = False
				
				for thisGlyphLayer in thisGlyph.layers:
					for thisAnchor in thisGlyphLayer.anchors:
						oldAnchorName = thisAnchor.name
						newAnchorName = oldAnchorName.replace( searchString, replaceString )
						if oldAnchorName != newAnchorName:
							thisAnchor.setName_( newAnchorName )
							reportString += "\n  layer '%s': %s > %s" % ( thisGlyphLayer.name, oldAnchorName, newAnchorName )
							displayReportString = True
				
				if displayReportString:
					print reportString

			if not self.SavePreferences( self ):
				print "Note: 'Search And Replace In Anchor Names' could not write preferences."
			
			self.w.close() # delete if you want window to stay open
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Search And Replace In Anchor Names Error: %s" % e

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
SearchAndReplaceInAnchorNames()