from __future__ import print_function
#MenuTitle: Find and Replace Cap and Corner Components
# -*- coding: utf-8 -*-
__doc__="""
Replaces Caps/Corners in all selected glyphs.
"""

import vanilla

class FindAndReplaceCorners( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 340
		windowHeight = 135
		self.w = vanilla.Window(
			( windowWidth, windowHeight ), # default window size
			"Replace Corners", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth, windowHeight ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.FindAndReplaceCorners.mainwindow" # stores last window position and size
		)
		
		thisFont = Glyphs.font
		self.corners = self.allCorners(thisFont)
		
		# UI elements:
		margin = 25
		self.w.textSearch = vanilla.TextBox((margin+5, 12+2, 80, 18), "Find:")
		self.w.searchFor = vanilla.PopUpButton((margin+80, 12, -margin, 22), self.corners)
		
		self.w.textReplace = vanilla.TextBox((margin, 32+12+2, 80, 18), "Replace with:")
		self.w.replaceBy = vanilla.PopUpButton((margin+80, 32+12, -margin, 22), self.corners)

		self.w.replaceButton = vanilla.Button((-70 - margin, 63+12+1, -margin, 22), "Replace", callback=self.FindAndReplaceCornersMain)
		self.w.setDefaultButton( self.w.replaceButton )
				
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Replace Corners' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.FindAndReplaceCorners.searchFor"] = self.w.searchFor.get()
			Glyphs.defaults["com.mekkablue.FindAndReplaceCorners.replaceBy"] = self.w.replaceBy.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			self.w.searchFor.set( Glyphs.defaults["com.mekkablue.FindAndReplaceCorners.searchFor"] )
			self.w.replaceBy.set( Glyphs.defaults["com.mekkablue.FindAndReplaceCorners.replaceBy"] )
		except:
			return False
			
		return True
		
	def allCorners(self, font):
		corners = []
		for g in font.glyphs:
			if g.name.startswith("_corner.") or g.name.startswith("_cap."):
				corners.append(g.name)
		return corners
		
	def FindAndReplaceCornersMain( self, sender ):
		try:
			if not self.SavePreferences( self ):
				print("Note: 'Replace Corners' could not write preferences.")
			
			searchString = self.corners[self.w.searchFor.get()]
			replaceString = self.corners[self.w.replaceBy.get()]
			# print "__searchString", searchString, " replaceString", replaceString
			if len(searchString) < 2 or not (searchString.startswith("_cap.") or searchString.startswith("_corner.")):
				Message("Invalid search", "A string needs to given and it has to start with '_cap.' or '_corner.'")
				return
			
			thisFont = Glyphs.font # frontmost font
			listOfSelectedLayers = thisFont.selectedLayers # active layers of currently selected glyphs
			
			newCornerGlyph = thisFont.glyphs[replaceString]
			if newCornerGlyph is None:
				Message("Missing Glyph", "Could not find glyph: \"%s\"" % replaceString)
				return
			
			for thisLayer in listOfSelectedLayers: # loop through layers
				for thisHint in thisLayer.hints:
					if thisHint.type == CORNER or thisHint.type == CAP:
						if thisHint.name == searchString:
							thisHint.setName_(replaceString)
							print(" %s" % ( thisLayer.parent.name ))
							displayReportString = True
				
				if displayReportString:
					Glyphs.showMacroWindow()
			
			self.w.close() # delete if you want window to stay open
			
		except Exception as e:
			# brings macro window to front and reports error:
			import traceback
			print(traceback.format_exc())
			Glyphs.showMacroWindow()

# brings macro window to front and clears its log:
Glyphs.clearLog()
FindAndReplaceCorners()
