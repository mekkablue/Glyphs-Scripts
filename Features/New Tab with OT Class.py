#MenuTitle: New Tab with OT Class
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Open a new tab with all glyphs contained in a specific OpenType class.
"""

import vanilla

class NewTabWithOTClass( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 60
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"New Tab with OT Class", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.NewTabWithOTClass.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text = vanilla.TextBox( (15-1, 12+2, 100, 14), "Pick an OT class:", sizeStyle='small' )
		self.w.classMenu = vanilla.PopUpButton( (15+100, 12, -130, 17), self.currentFontClasses(None), callback=None, sizeStyle='small' )
		self.w.updateButton = vanilla.Button((-125, 12+1, -100, -15), u"↺", sizeStyle='small', callback=self.populateClassMenu )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-95, 12+3, -15, -15), "New Tab", sizeStyle='regular', callback=self.NewTabWithOTClassMain )
		self.w.setDefaultButton( self.w.runButton )
		
		self.font = Glyphs.font
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def currentFontClasses(self, sender):
		self.font = Glyphs.font
		classNames = [c.name for c in self.font.classes]
		return classNames
	
	def populateClassMenu(self, sender):
		otClasses = self.currentFontClasses(None)
		self.w.classMenu.setItems( otClasses )
		if self.w.classMenu.getItems():
			self.w.classMenu.set(0)
		
	def NewTabWithOTClassMain( self, sender ):
		try:
			classNames = self.w.classMenu.getItems()
			if not classNames:
				Message(title="No OT Class Found", message=u"Found no class to open in a new tab. Please activate a font, press the ↺ update button, and pick a class from the menu.", OKButton=None)
			else:
				selectedClass = classNames[self.w.classMenu.get()]
				for thisClass in self.font.classes:
					if thisClass.name == selectedClass:
						glyphNames = thisClass.code.split()
						escapedGlyphNames = "/"+"/".join(glyphNames)
						self.font.newTab( escapedGlyphNames )
				self.w.close() # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("New Tab with OT Class Error: %s" % e)
			import traceback
			print(traceback.format_exc())

NewTabWithOTClass()