#MenuTitle: Adjust Kerning in Master
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")
__doc__="""
Adjusts all kerning values by a specified amount.
"""

import vanilla

optionList = ( "Multiply by", "Add", "Add Absolute", "Round by" )

class AdjustKerning( object ):
	def __init__( self ):
		# GUI:
		windowWidth  = 260
		windowHeight = 155
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Adjust Kerning", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.AdjustKerning.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 10, 12, 22
		
		self.w.text_1 = vanilla.TextBox( (inset-1, linePos+2, -inset, 14), "In the current font master, do this:", sizeStyle='small' )
		
		linePos += lineHeight
		self.w.doWhat = vanilla.PopUpButton( (inset, linePos, 100, 17), optionList, callback=self.SavePreferences, sizeStyle='small' )
		self.w.howMuch = vanilla.EditText((inset+100+10, linePos-1, -inset, 19), "10", sizeStyle='small', callback=self.SavePreferences)
		
		linePos += lineHeight
		self.w.text_2 = vanilla.TextBox( (inset-1, linePos+4, -inset, 14), "To these kerning pairs:", sizeStyle='small' )

		linePos += lineHeight
		self.w.positive = vanilla.CheckBox( (inset, linePos, 63, 20), "Positive,", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.zero = vanilla.CheckBox( (inset+65, linePos, 65, 20), "zero, and", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.negative = vanilla.CheckBox( (inset+137, linePos, -inset, 20), "negative pairs", value=True, callback=self.SavePreferences, sizeStyle='small' )

		# self.w.keepWindow = vanilla.CheckBox( (25, offset*2+line*4, -15, line), "Keep window open", value=False, callback=self.SavePreferences, sizeStyle='small' )

		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Adjust", sizeStyle='regular', callback=self.AdjustKerningMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Adjust Kerning in Master' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.AdjustKerning.doWhat"] = self.w.doWhat.get()
			Glyphs.defaults["com.mekkablue.AdjustKerning.howMuch"] = self.w.howMuch.get()
			# Glyphs.defaults["com.mekkablue.AdjustKerning.keepWindow"] = self.w.keepWindow.get()
			Glyphs.defaults["com.mekkablue.AdjustKerning.positive"] = self.w.positive.get()
			Glyphs.defaults["com.mekkablue.AdjustKerning.zero"] = self.w.zero.get()
			Glyphs.defaults["com.mekkablue.AdjustKerning.negative"] = self.w.negative.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.AdjustKerning.doWhat", 0)
			Glyphs.registerDefault("com.mekkablue.AdjustKerning.howMuch", "20")
			Glyphs.registerDefault("com.mekkablue.AdjustKerning.positive", True)
			Glyphs.registerDefault("com.mekkablue.AdjustKerning.zero", True)
			Glyphs.registerDefault("com.mekkablue.AdjustKerning.negative", True)
			self.w.doWhat.set( Glyphs.defaults["com.mekkablue.AdjustKerning.doWhat"] )
			self.w.howMuch.set( Glyphs.defaults["com.mekkablue.AdjustKerning.howMuch"] )
			self.w.positive.set( Glyphs.defaults["com.mekkablue.AdjustKerning.positive"] )
			self.w.zero.set( Glyphs.defaults["com.mekkablue.AdjustKerning.zero"] )
			self.w.negative.set( Glyphs.defaults["com.mekkablue.AdjustKerning.negative"] )
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
	
	def userChoosesToProcessKerning( self, kernValue ):
		try:
			if Glyphs.defaults["com.mekkablue.AdjustKerning.positive"] and kernValue > 0:
				return True
			elif Glyphs.defaults["com.mekkablue.AdjustKerning.zero"] and kernValue == 0:
				return True
			elif Glyphs.defaults["com.mekkablue.AdjustKerning.negative"] and kernValue < 0:
				return True
			else:
				return False
		except Exception as e:
			raise e

	def AdjustKerningMain( self, sender ):
		try:
			Font = Glyphs.font
			Master = Font.selectedFontMaster
			MasterID = Master.id
			MasterKernDict = Font.kerning[ MasterID ]
			calculation = str( self.w.doWhat.getItems()[ Glyphs.defaults["com.mekkablue.AdjustKerning.doWhat"] ] )
			value = float( Glyphs.defaults["com.mekkablue.AdjustKerning.howMuch"] )
			
			Font.disableUpdateInterface()
			try:
				if calculation == optionList[0]:

					for leftGlyphID in MasterKernDict.keys():
						leftName = self.nameForID( Font, leftGlyphID )
					
						for rightGlyphID in MasterKernDict[ leftGlyphID ].keys():
							originalKerning = MasterKernDict[ leftGlyphID ][ rightGlyphID ]
							if self.userChoosesToProcessKerning( originalKerning ):
								rightName = self.nameForID( Font, rightGlyphID )
								Font.setKerningForPair( MasterID, leftName, rightName, originalKerning * value )

				elif calculation == optionList[1]:
				
					for leftGlyphID in MasterKernDict.keys():
						leftName = self.nameForID( Font, leftGlyphID )

						for rightGlyphID in MasterKernDict[ leftGlyphID ].keys():
							originalKerning = MasterKernDict[ leftGlyphID ][ rightGlyphID ]
							if self.userChoosesToProcessKerning( originalKerning ):
								rightName = self.nameForID( Font, rightGlyphID )
								Font.setKerningForPair( MasterID, leftName, rightName, originalKerning + value )
						
				elif calculation == optionList[2]:
				
					for leftGlyphID in MasterKernDict.keys():
						leftName = self.nameForID( Font, leftGlyphID )

						for rightGlyphID in MasterKernDict[ leftGlyphID ].keys():
							originalKerning = MasterKernDict[ leftGlyphID ][ rightGlyphID ]
							if self.userChoosesToProcessKerning( originalKerning ):
								rightName = self.nameForID( Font, rightGlyphID )
								if originalKerning < 0:
									factor = -1
								else:
									factor = 1
								Font.setKerningForPair( MasterID, leftName, rightName, originalKerning + factor * value )
						
				elif calculation == optionList[3]:
				
					for leftGlyphID in MasterKernDict.keys():
						leftName = self.nameForID( Font, leftGlyphID )
					
						for rightGlyphID in MasterKernDict[ leftGlyphID ].keys():
							originalKerning = MasterKernDict[ leftGlyphID ][ rightGlyphID ]
							if self.userChoosesToProcessKerning( originalKerning ):
								rightName = self.nameForID( Font, rightGlyphID )
								Font.setKerningForPair( MasterID, leftName, rightName, round( originalKerning / value, 0 ) * value )
								
			except Exception as e:
				Glyphs.showMacroWindow()
				print("\n⚠️ Script Error:\n")
				import traceback
				print(traceback.format_exc())
				print()
				raise e
				
			finally:
				Font.enableUpdateInterface() # re-enables UI updates in Font View
			
			
			if not self.SavePreferences( self ):
				print("Note: could not write preferences.")
		except Exception as e:
			raise e

AdjustKerning()
