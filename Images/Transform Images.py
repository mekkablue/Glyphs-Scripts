#MenuTitle: Transform Images
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__="""
Batch scale and move images in selected layers.
"""

import vanilla, traceback
from AppKit import NSAffineTransform

windowHeight = 120

def getScale( scaleString, factor ):
	if factor == 1:
		return ( 100.0 + float( scaleString ) ) / 100.0
	else:
		return 100.0 / ( 100.0 + float( scaleString ) )
	
class TransformImages( object ):
	def __init__( self ):
		self.w = vanilla.FloatingWindow( (250, windowHeight), "Transform Images", minSize=(250, windowHeight), maxSize=(250, windowHeight), autosaveName="com.mekkablue.TransformImages.mainwindow" )

		self.w.scale_text1 = vanilla.TextBox( (15-1, 12+2, 75, 14), "Scale x/y:", sizeStyle='small' )
		self.w.scale_X = vanilla.EditText( (15+60,    12, 55, 15+3), "+10.5", sizeStyle = 'small')
		self.w.scale_Y = vanilla.EditText( (15+60+60, 12, 55, 15+3), "-11.0", sizeStyle = 'small')
		self.w.scale_text2 = vanilla.TextBox( (15+60+60+60, 12+2, -15, 14), "%", sizeStyle='small' )
		
		self.w.move_text1 = vanilla.TextBox( (15-1,  25+12+2, 75, 14), "Move x/y:", sizeStyle='small' )
		self.w.move_X = vanilla.EditText( (15+60,    25+12, 55, 15+3), "10", sizeStyle = 'small')
		self.w.move_Y = vanilla.EditText( (15+60+60, 25+12, 55, 15+3), "10", sizeStyle = 'small')
		self.w.move_text2 = vanilla.TextBox( (15+60+60+60,  25+12+2, -15, 14), "units", sizeStyle='small' )
		
		#self.w.resetButton = vanilla.Button((-80-80-15, -20-15, -85, -15), "Reset", sizeStyle='regular', callback=self.ResetStructs )
		self.w.backButton   = vanilla.Button((-60-60-23, -20-15, -60-23, -15), "Back", sizeStyle='regular', callback=self.TransformImagesMain )
		self.w.runButton   = vanilla.Button((-60-15, -20-15, -15, -15), "Go", sizeStyle='regular', callback=self.TransformImagesMain )
		self.w.setDefaultButton( self.w.runButton )
		
		try:
			self.LoadPreferences( )
		except:
			pass

		self.w.open()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.TransformImages.scaleX"] = self.w.scale_X.get()
			Glyphs.defaults["com.mekkablue.TransformImages.scaleY"] = self.w.scale_Y.get()
			Glyphs.defaults["com.mekkablue.TransformImages.moveX"]  = self.w.move_X.get()
			Glyphs.defaults["com.mekkablue.TransformImages.moveY"]  = self.w.move_Y.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			self.w.scale_X.set( Glyphs.defaults["com.mekkablue.TransformImages.scaleX"] )
			self.w.scale_Y.set( Glyphs.defaults["com.mekkablue.TransformImages.scaleY"] )
			self.w.move_X.set( Glyphs.defaults["com.mekkablue.TransformImages.moveX"] )
			self.w.move_Y.set( Glyphs.defaults["com.mekkablue.TransformImages.moveY"] )
		except:
			return False
			
		return True

	def TransformImagesMain( self, sender ):
		try:
			Font = Glyphs.font
			selectedLayers = Font.selectedLayers
			if sender == self.w.backButton:
				factor = -1.0
			elif sender == self.w.runButton:
				factor = 1.0
			
			for thisLayer in selectedLayers:
				thisImage = thisLayer.backgroundImage
				if thisImage:
					moveXpreScaled, moveYpreScaled, scaleXfix, scaleYfix  = self.w.move_X.get(), self.w.move_Y.get(), self.w.scale_X.get(), self.w.scale_Y.get()
					if moveXpreScaled == "": moveXpreScaled = 0
					if moveYpreScaled == "": moveYpreScaled = 0
					if scaleXfix == "": scaleXfix = 0
					if scaleYfix == "": scaleYfix = 0
					moveX, moveY   = float( moveXpreScaled ) * factor, float( moveYpreScaled ) * factor
					scaleX, scaleY = getScale( scaleXfix, factor ), getScale( scaleYfix, factor )
			
					ScaleAndMoveTransform = NSAffineTransform.transform()
					ScaleAndMoveTransform.setTransformStruct_( thisImage.transformStruct() )
					ScaleAndMoveTransform.scaleXBy_yBy_( scaleX, scaleY )
					ScaleAndMoveTransform.translateXBy_yBy_( moveX, moveY )
					thisImage.setTransformStruct_( ScaleAndMoveTransform.transformStruct() )

			if not self.SavePreferences( self ):
				print("Note: could not write preferences.")
			
			# self.w.close()
		except Exception as e:
			raise e

TransformImages()
