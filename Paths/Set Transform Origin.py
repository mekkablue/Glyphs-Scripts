#MenuTitle: Set Transform Origin
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Sets origin point for Rotate tool.
"""

import vanilla
from Foundation import NSPoint, NSClassFromString

class SetTransformOriginWindow( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 370
		windowHeight = 60
		windowWidthResize  = 0 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Set Transform Origin", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.SetTransformOriginWindow.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15-1, 12+3, 75, 14), "Origin:", sizeStyle='small' )
		self.w.originX = vanilla.EditText( (65, 12, 70, 15+3), "0.0", sizeStyle = 'small')
		self.w.originY = vanilla.EditText( (65+80, 12, 70, 15+3), "0.0", sizeStyle = 'small')
		
		# Run Button:
		self.w.resetButton = vanilla.Button((65+160, 12+1, 60, 15), "Get", sizeStyle='small', callback=self.GetTransformOrigin )
		self.w.runButton = vanilla.Button((65+160+70, 12+1, 60, 15), "Set", sizeStyle='small', callback=self.SetTransformOriginMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.GetTransformOrigin(None):
			print("Note: 'Set Transform Origin' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def GetTransformOrigin( self, sender ):
		try:
			myController = Glyphs.currentDocument.windowController()
			rotateToolClass = NSClassFromString("GlyphsToolRotate")
			myRotateTool = myController.toolForClass_( rotateToolClass )
			currentOrigin = myRotateTool.transformOrigin()
			
			self.w.originX.set( currentOrigin.x )
			self.w.originY.set( currentOrigin.y )
		except:
			return False
			
		return True

	def SetTransformOriginMain( self, sender ):
		try:
			newOriginX = float(self.w.originX.get())
			newOriginY = float(self.w.originY.get())
			newOriginPoint = NSPoint( newOriginX, newOriginY )

			myController = Glyphs.currentDocument.windowController()
			myController.graphicView().setNeedsDisplay_(False)

			rotateToolClass = NSClassFromString("GlyphsToolRotate")
			myRotateTool = myController.toolForClass_( rotateToolClass )
			myRotateTool.setTransformOrigin_( newOriginPoint )
			
			myController.graphicView().setNeedsDisplay_(True)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Set Transform Origin Error: %s" % e)

SetTransformOriginWindow()