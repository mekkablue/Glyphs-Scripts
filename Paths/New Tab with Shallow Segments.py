#MenuTitle: New Tab with Shallow Curve Segments
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__="""
Opens a new tab with all layers that have small outline segments, i.e., not extending far enough horizontally or vertically.
"""

import vanilla

class NewTabwithShallowCurveSegments( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 140
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"New Tab with Shallow Curve Segments", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.NewTabwithShallowCurveSegments.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 36), "Find shallow outline segments that are horizontally or vertically smaller than the specified threshold size:", sizeStyle='small', selectable=True )
		linePos += lineHeight*2
		
		self.w.thresholdLabel = vanilla.TextBox( (inset, linePos+2, 120, 14), "Threshold size", sizeStyle='small', selectable=True )
		self.w.thresholdSize = vanilla.EditText( (inset+120, linePos, -inset, 19), "10", sizeStyle='small' )
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-100-inset, -20-inset, -inset, -inset), "Open Tab", sizeStyle='regular', callback=self.NewTabwithShallowCurveSegmentsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'New Tab with Shallow Curve Segments' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.NewTabwithShallowCurveSegments.thresholdSize"] = self.w.thresholdSize.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.NewTabwithShallowCurveSegments.thresholdSize", 10)
			self.w.thresholdSize.set( Glyphs.defaults["com.mekkablue.NewTabwithShallowCurveSegments.thresholdSize"] )
		except:
			return False
			
		return True
		
	def isLayerAffected(self, thisLayer, minSize):
		thisLayer.selection = None
		for thisPath in thisLayer.paths:
			for thisNode in thisPath.nodes:
				if thisNode.type == CURVE:
					thisSegment = (
						thisNode.prevNode.prevNode.prevNode,
						thisNode.prevNode.prevNode,
						thisNode.prevNode,
						thisNode,
					)

					xCoords = [p.x for p in thisSegment]
					yCoords = [p.y for p in thisSegment]
					xDist = abs( min(xCoords) - max(xCoords) )
					yDist = abs( min(yCoords) - max(yCoords) )
					if xDist < minSize or yDist < minSize:
						for affectedNode in thisSegment:
							affectedNode.selected = True
							
						return True
		return False

	def NewTabwithShallowCurveSegmentsMain( self, sender ):
		try:
			affectedLayers = []
			minSize = abs(int(Glyphs.defaults["com.mekkablue.NewTabwithShallowCurveSegments.thresholdSize"]))
			thisFont = Glyphs.font # frontmost font
			for thisGlyph in thisFont.glyphs:
				for thisLayer in thisGlyph.layers: # loop through layers
					if self.isLayerAffected(thisLayer, minSize):
						affectedLayers.append(thisLayer)
			
			if affectedLayers:
				thisTab = thisFont.newTab()
				thisTab.layers = affectedLayers
			else:
				Message(
					title="No Shallow Curves", 
					message="No layers with shallow curves found in %s. Congratulations!" % thisFont.familyName, 
					OKButton=None)
			
			if not self.SavePreferences( self ):
				print("Note: 'New Tab with Shallow Curve Segments' could not write preferences.")
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("New Tab with Shallow Curve Segments Error: %s" % e)
			import traceback
			print(traceback.format_exc())

NewTabwithShallowCurveSegments()