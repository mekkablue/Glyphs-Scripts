#MenuTitle: Adjust Kerning in Master
# -*- coding: utf-8 -*-
__doc__="""
Adjusts all kerning values by a specified amount.
"""

import vanilla


optionList = [ "Multiply by", "Add", "Add Absolute", "Round by" ]

class AdjustKerning( object ):
	def __init__( self ):
		# GUI:
		offset = 10
		line = 20
		windowWidth  = 280
		windowHeight = 2*offset+7*line
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Adjust Kerning", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.AdjustKerning.mainwindow" # stores last window position and size
		)
		
		self.w.text_1 = vanilla.TextBox( (15-1, offset+2, -15, line), "In the current font master, do this:", sizeStyle='small' )
		self.w.doWhat = vanilla.PopUpButton( (25, offset+line, 100, line), optionList, callback=self.SavePreferences, sizeStyle='small' )
		self.w.howMuch = vanilla.EditText((25+100+10, offset+line+1, -15, line), "10", sizeStyle='small', callback=self.SavePreferences)
		
		self.w.text_2 = vanilla.TextBox( (15-1, offset*2+line*2+2, -15, line), "To these kerning pairs:", sizeStyle='small' )
		self.w.positive = vanilla.CheckBox( (25, offset*2+line*3, -15, line), "Positive,", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.zero = vanilla.CheckBox( (90, offset*2+line*3, -15, line), "zero, and", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.negative = vanilla.CheckBox( (162, offset*2+line*3, -15, line), "negative pairs", value=True, callback=self.SavePreferences, sizeStyle='small' )

		# self.w.keepWindow = vanilla.CheckBox( (25, offset*2+line*4, -15, line), "Keep window open", value=False, callback=self.SavePreferences, sizeStyle='small' )

		self.w.runButton = vanilla.Button((-80-15, -offset-line-5, -15, line), "Adjust", sizeStyle='small', callback=self.AdjustKerningMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Adjust Kerning in Master' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
		# Set defaults for class variables
		self.positive = self.w.positive.get()
		self.zero = self.w.zero.get()
		self.negative = self.w.negative.get()
		
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
			NSUserDefaults.standardUserDefaults().registerDefaults_(
				{
					"com.mekkablue.AdjustKerning.doWhat": 0,
					"com.mekkablue.AdjustKerning.howMuch": "20",
					# "com.mekkablue.AdjustKerning.keepWindow": True,
					"com.mekkablue.AdjustKerning.positive": True,
					"com.mekkablue.AdjustKerning.zero": True,
					"com.mekkablue.AdjustKerning.negative": True
				}
			)
			self.w.doWhat.set( Glyphs.defaults["com.mekkablue.AdjustKerning.doWhat"] )
			self.w.howMuch.set( Glyphs.defaults["com.mekkablue.AdjustKerning.howMuch"] )
			# self.w.keepWindow.set( Glyphs.defaults["com.mekkablue.AdjustKerning.keepWindow"] )
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
			if self.positive and kernValue > 0:
				return True
			elif self.zero and kernValue == 0:
				return True
			elif self.negative and kernValue < 0:
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
			
			self.positive = self.w.positive.get()
			self.zero = self.w.zero.get()
			self.negative = self.w.negative.get()

			Font.disableUpdateInterface()
			
			calculation = str( self.w.doWhat.getItems()[ self.w.doWhat.get() ] )
			value = float( self.w.howMuch.get() )
			
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
				
			Font.enableUpdateInterface()
			
			if not self.SavePreferences( self ):
				print "Note: could not write preferences."
			
			# if not self.w.keepWindow.get():
			# 	self.w.close()
		except Exception, e:
			raise e

AdjustKerning()
