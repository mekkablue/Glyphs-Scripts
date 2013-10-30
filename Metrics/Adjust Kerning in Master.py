#MenuTitle: Adjust Kerning in Master
# -*- coding: utf-8 -*-
"""Adjusts all kerning values by a specified amount."""

import vanilla
import GlyphsApp

optionList = [ "Multiply by", "Add", "Round by" ]

class AdjustKerning( object ):
	def __init__( self ):
		self.w = vanilla.FloatingWindow( (350, 90), "Adjust Kerning", minSize=(280, 90), maxSize=(600, 90), autosaveName="com.mekkablue.AdjustKerning.mainwindow" )

		self.w.text_1 = vanilla.TextBox( (15-1, 12+2, -15, 14), "All kerning pairs in the current Master:", sizeStyle='small' )
		self.w.popup_1 = vanilla.PopUpButton( (15, 40, 100, 17), optionList, callback=self.SavePreferences, sizeStyle='small' )
		self.w.value_1 = vanilla.EditText((15+100+10, 40, -80-15-10, 19), "10", sizeStyle='small', callback=self.SavePreferences)
		
		self.w.runButton = vanilla.Button((-80-15, 40, -15, 17), "Adjust", sizeStyle='small', callback=self.AdjustKerningMain )
		self.w.setDefaultButton( self.w.runButton )
		
		try:
			self.LoadPreferences( )
		except:
			pass

		self.w.open()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.AdjustKerning.popup_1"] = self.w.popup_1.get()
			Glyphs.defaults["com.mekkablue.AdjustKerning.value_1"] = self.w.value_1.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			self.w.popup_1.set( Glyphs.defaults["com.mekkablue.AdjustKerning.popup_1"] )
			self.w.value_1.set( Glyphs.defaults["com.mekkablue.AdjustKerning.value_1"] )
		except:
			return False
			
		return True

	def AdjustKerningMain( self, sender ):
		try:
			Font = Glyphs.font
			Master = Font.selectedFontMaster

			Font.disableUpdateInterface()
			
			calculation = str( self.w.popup_1.getItems()[ self.w.popup_1.get() ] )
			value = float( self.w.value_1.get() )
			
			if calculation == optionList[0]:
				for leftGlyphID in Font.kerning[ Master.id ]:
					for rightGlyphID in Font.kerning[ Master.id ][ leftGlyphID ]:
						Font.kerning[ Master.id ][ leftGlyphID ][ rightGlyphID ] *= value
			elif calculation == optionList[1]:
				for leftGlyphID in Font.kerning[ Master.id ]:
					for rightGlyphID in Font.kerning[ Master.id ][ leftGlyphID ]:
						Font.kerning[ Master.id ][ leftGlyphID ][ rightGlyphID ] += value
			elif calculation == optionList[2]:
				for leftGlyphID in Font.kerning[ Master.id ]:
					for rightGlyphID in Font.kerning[ Master.id ][ leftGlyphID ]:
						Font.kerning[ Master.id ][ leftGlyphID ][ rightGlyphID ] = round( Font.kerning[ Master.id ][ leftGlyphID ][ rightGlyphID ] / value, 0 ) * value
				
			Font.enableUpdateInterface()
			
			if not self.SavePreferences( self ):
				print "Note: could not write preferences."
			
			self.w.close()
		except Exception, e:
			raise e

AdjustKerning()
