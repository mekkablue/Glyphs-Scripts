#MenuTitle: Rename Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Takes a list of oldglyphname=newglyphname pairs and renames glyphs in the font accordingly, much like the Rename Glyphs parameter.
"""

import vanilla, uuid
from AppKit import NSFont

class RenameGlyphs( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 250
		windowHeight = 200
		windowWidthResize  = 800 # user can resize width by this value
		windowHeightResize = 800 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Rename Glyphs", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.RenameGlyphs.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (10, 12+2, -10, 14), "Add lines like oldname=newname:", sizeStyle='small' )
		self.w.renameList = vanilla.TextEditor( (1, 40, -1, -40), "oldname=newname", callback=self.SavePreferences )
		self.w.renameList.getNSTextView().setFont_( NSFont.userFixedPitchFontOfSize_(-1.0) )
		self.w.renameList.getNSTextView().turnOffLigatures_(1)
		self.w.renameList.getNSTextView().useStandardLigatures_(0)
		self.w.renameList.selectAll()
		
		# Run Button:
		self.w.runButton = vanilla.Button((-100, -35, -15, -15), "Rename", sizeStyle='regular', callback=self.RenameGlyphsMain )
		#self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Rename Glyphs' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.RenameGlyphs.renameList"] = self.w.renameList.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.RenameGlyphs.renameList", "oldname=newname")
			self.w.renameList.set( Glyphs.defaults["com.mekkablue.RenameGlyphs.renameList"] )
		except:
			return False
			
		return True

	def RenameGlyphsMain( self, sender ):
		try:
			thisFont = Glyphs.font # frontmost font
			thisList = Glyphs.defaults["com.mekkablue.RenameGlyphs.renameList"]
			for thisLine in thisList.splitlines():
				if thisLine.strip():
					glyphNameLeft = thisLine.split("=")[0].strip()
					glyphNameRight = thisLine.split("=")[1].strip()
					glyphLeft = thisFont.glyphs[glyphNameLeft]
					glyphRight = thisFont.glyphs[glyphNameRight]
					if glyphLeft:
						if glyphRight:
							uniqueSuffix = ".%s" % uuid.uuid4().hex
							glyphLeft.name = glyphNameRight + uniqueSuffix
							glyphRight.name = glyphNameLeft
							glyphLeft.name = glyphNameRight
						else:
							glyphLeft.name = glyphNameRight
					else:
						print "Warning: %s not in font." % glyphNameLeft
			
			if not self.SavePreferences( self ):
				print "Note: 'Rename Glyphs' could not write preferences."
			
			self.w.close() # delete if you want window to stay open
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Rename Glyphs Error: %s" % e
			import traceback
			print traceback.format_exc()

RenameGlyphs()