#MenuTitle: Transform Images
# -*- coding: utf-8 -*-
"""Batch scale and move images in selected layers."""

import vanilla
import GlyphsApp
windowHeight = 120

def getScale( scaleString, factor ):
	return ( 100.0 + float( scaleString ) * factor ) / 100.0
	
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
				thisImage = thisLayer.backgroundImage()
				moveX, moveY   = float( self.w.move_X.get() ) * factor, float( self.w.move_Y.get() ) * factor
				scaleX, scaleY = getScale( self.w.scale_X.get(), factor ), getScale( self.w.scale_Y.get(), factor )
			
				ImageTransform = NSAffineTransform.transform()
				ImageTransform.setTransformStruct_( thisImage.transformStruct() )
				ImageTransform.translateXBy_yBy_( moveX, moveY )
				ImageTransform.scaleXBy_yBy_( scaleX, scaleY )

				t = ImageTransform.transformStruct()
				thisImage.setTransformStruct_( (t.m11, t.m12, t.m21, t.m22, t.tX, t.tY) )
				
			if not self.SavePreferences( self ):
				print "Note: could not write preferences."
			
			# self.w.close()
		except Exception, e:
			raise e

TransformImages()
