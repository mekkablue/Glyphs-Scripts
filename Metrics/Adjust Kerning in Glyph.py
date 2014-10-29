#MenuTitle: Adjust Kerning For Glyph
# -*- coding: utf-8 -*-
__doc__="""
Adjusts all kerning values by a specified amount all pairs containing a specific glyph.
"""

import vanilla
import GlyphsApp

optionList = [ "Multiply by", "Add", "Add Absolute", "Round by" ]

class AdjustKerning( object ):
	def __init__( self ):
		self.w = vanilla.FloatingWindow( (350, 140), "Adjust Kerning", minSize=(280, 140), maxSize=(600, 140), autosaveName="com.mekkablue.AdjustKerning.mainwindow" )

		self.w.text_1 = vanilla.TextBox( (15-1, 12+2, -15, 14), "All kerning pairs in the current Master:", sizeStyle='small' )
		self.w.popup_1 = vanilla.PopUpButton( (15, 36, 100, 17), optionList, callback=self.SavePreferences, sizeStyle='small' )
		self.w.value_1 = vanilla.EditText((15+100+10, 36, -80-15-10, 19), "10", sizeStyle='small', callback=self.SavePreferences)
		
		self.w.runButton = vanilla.Button((-80-15, 36, -15, 17), "Adjust", sizeStyle='small', callback=self.AdjustKerningMain )
		self.w.setDefaultButton( self.w.runButton )
				
		self.w.text_2 = vanilla.TextBox( (15-1, 64, -15, 14), "For glyph name:", sizeStyle='small' )

		self.w.value_2 = vanilla.EditText((15+100+10, 62, -80-15-10, 19), "A", sizeStyle='small', callback=self.SavePreferences)

		self.w.keepWindow = vanilla.CheckBox( (15, 84, -15, 20), "Keep window open", value=False, callback=self.SavePreferences, sizeStyle='small' )

		try:
			self.LoadPreferences( )
		except:
			pass

		self.w.open()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.AdjustKerning.popup_1"] = self.w.popup_1.get()
			Glyphs.defaults["com.mekkablue.AdjustKerning.value_1"] = self.w.value_1.get()
			Glyphs.defaults["com.mekkablue.AdjustKerning.keepWindow"] = self.w.keepWindow.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			self.w.popup_1.set( Glyphs.defaults["com.mekkablue.AdjustKerning.popup_1"] )
			self.w.value_1.set( Glyphs.defaults["com.mekkablue.AdjustKerning.value_1"] )
			self.w.keepWindow.set( Glyphs.defaults["com.mekkablue.AdjustKerning.keepWindow"] )
		except:
			return False
			
		return True
	
	def nameForID( self, Font, ID ):
		try:
			if ID[0] == "@": # is a group
				return ID
			else: # is a glyph
				return Font.glyphForId_( ID ).name
		except Exception as e:
			raise e

	def AdjustKerningMain( self, sender ):
		try:
			Font = Glyphs.font
			Master = Font.selectedFontMaster
			MasterID = Master.id
			MasterKernDict = Font.kerning[ MasterID ]

			Font.disableUpdateInterface()
			
			calculation = str( self.w.popup_1.getItems()[ self.w.popup_1.get() ] )
			value = float( self.w.value_1.get() )
			kernGlyph = self.w.value_2.get()
			
			if calculation == optionList[0]:

				for leftGlyphID in MasterKernDict.keys():
					leftName = self.nameForID( Font, leftGlyphID )
					if leftName[0] =="@" and leftName[7:] == kernGlyph or leftName == kernGlyph:
						for rightGlyphID in MasterKernDict[ leftGlyphID ].keys():
							originalKerning = MasterKernDict[ leftGlyphID ][ rightGlyphID ]
							rightName = nameForID( Font, rightGlyphID )

							Font.setKerningForPair( MasterID, leftName, rightName, originalKerning * value )
							
					for rightGlyphID in MasterKernDict[ leftGlyphID ].keys():
						originalKerning = MasterKernDict[ leftGlyphID ][ rightGlyphID ]
						rightName = self.nameForID( Font, rightGlyphID )

						if rightName[0] =="@" and rightName[7:] == kernGlyph or rightName == kernGlyph:
							Font.setKerningForPair( MasterID, leftName, rightName, originalKerning * value )

			elif calculation == optionList[1]:
				
				for leftGlyphID in MasterKernDict.keys():
					leftName = self.nameForID( Font, leftGlyphID )
					if leftName[0] =="@" and leftName[7:] == kernGlyph or leftName == kernGlyph:
						for rightGlyphID in MasterKernDict[ leftGlyphID ].keys():
							originalKerning = MasterKernDict[ leftGlyphID ][ rightGlyphID ]
							rightName = nameForID( Font, rightGlyphID )

							Font.setKerningForPair( MasterID, leftName, rightName, originalKerning + value )
							
					for rightGlyphID in MasterKernDict[ leftGlyphID ].keys():
						originalKerning = MasterKernDict[ leftGlyphID ][ rightGlyphID ]
						rightName = self.nameForID( Font, rightGlyphID )

						if rightName[0] =="@" and rightName[7:] == kernGlyph or rightName == kernGlyph:
							Font.setKerningForPair( MasterID, leftName, rightName, originalKerning + value )
						
			elif calculation == optionList[2]:
				
				for leftGlyphID in MasterKernDict.keys():
					leftName = self.nameForID( Font, leftGlyphID )
					if leftName[0] =="@" and leftName[7:] == kernGlyph or leftName == kernGlyph:
						for rightGlyphID in MasterKernDict[ leftGlyphID ].keys():
							originalKerning = MasterKernDict[ leftGlyphID ][ rightGlyphID ]
							rightName = nameForID( Font, rightGlyphID )

							Font.setKerningForPair( MasterID, leftName, rightName, originalKerning + factor * value )
							
					for rightGlyphID in MasterKernDict[ leftGlyphID ].keys():
						originalKerning = MasterKernDict[ leftGlyphID ][ rightGlyphID ]
						rightName = self.nameForID( Font, rightGlyphID )

						if rightName[0] =="@" and rightName[7:] == kernGlyph or rightName == kernGlyph:
							Font.setKerningForPair( MasterID, leftName, rightName, originalKerning + factor * value )
						
			elif calculation == optionList[3]:
				
				for leftGlyphID in MasterKernDict.keys():
					leftName = self.nameForID( Font, leftGlyphID )
					if leftName[0] =="@" and leftName[7:] == kernGlyph or leftName == kernGlyph:
						for rightGlyphID in MasterKernDict[ leftGlyphID ].keys():
							originalKerning = MasterKernDict[ leftGlyphID ][ rightGlyphID ]
							rightName = nameForID( Font, rightGlyphID )

							Font.setKerningForPair( MasterID, leftName, rightName, round( originalKerning / value, 0 ) * value )
							
					for rightGlyphID in MasterKernDict[ leftGlyphID ].keys():
						originalKerning = MasterKernDict[ leftGlyphID ][ rightGlyphID ]
						rightName = self.nameForID( Font, rightGlyphID )

						if rightName[0] =="@" and rightName[7:] == kernGlyph or rightName == kernGlyph:
							Font.setKerningForPair( MasterID, leftName, rightName, round( originalKerning / value, 0 ) * value )
				
			Font.enableUpdateInterface()
			
			if not self.SavePreferences( self ):
				print "Note: could not write preferences."
			
			if not self.w.keepWindow.get():
				self.w.close()
		except Exception, e:
			raise e

AdjustKerning()
