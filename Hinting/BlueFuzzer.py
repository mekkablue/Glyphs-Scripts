#MenuTitle: BlueFuzzer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Extends all alignment zones (except for the baseline zone that should stay at 0).
"""

import vanilla

windowHeight = 110

class BlueFuzzer( object ):
	def __init__( self ):
		self.w = vanilla.FloatingWindow( (300, windowHeight), "BlueFuzzer", minSize=(250, windowHeight), maxSize=(500, windowHeight), autosaveName="com.mekkablue.BlueFuzzer.mainwindow" )

		self.w.text_1 = vanilla.TextBox( (15, 12+2, 120, 18), "Extend zones by", sizeStyle='small' )
		self.w.fuzzValue = vanilla.EditText( (120, 12, -15, 18), "1", sizeStyle = 'small')
		self.w.allMasters = vanilla.CheckBox( (15, 35, -15, 20), "Apply to all masters", value=True, callback=self.SavePreferences, sizeStyle='small' )
		
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Fuzz", sizeStyle='regular', callback=self.BlueFuzzerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		try:
			self.LoadPreferences( )
		except:
			pass

		self.w.open()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.BlueFuzzer.fuzzValue"] = self.w.fuzzValue.get()
			Glyphs.defaults["com.mekkablue.BlueFuzzer.allMasters"] = self.w.allMasters.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			self.w.fuzzValue.set( Glyphs.defaults["com.mekkablue.BlueFuzzer.fuzzValue"] )
			self.w.allMasters.set( Glyphs.defaults["com.mekkablue.BlueFuzzer.allMasters"] )
		except:
			return False
			
		return True

	def BlueFuzzerMain( self, sender ):
		try:
			Font = Glyphs.font
			
			fuzzValue = int( self.w.fuzzValue.get() )
			allMasters = bool( self.w.allMasters.get() )
			
			
			if allMasters:
				masterList = Font.masters
			else:
				masterList = [Font.selectedFontMaster]

			for m in masterList:
				numOfZones = len( m.alignmentZones )
				for i in range( numOfZones ):
					thisZone = m.alignmentZones[i]
					factor = 1
					if thisZone.size < 0: # negative zone
						factor = -1
					if thisZone.position == 0 and factor == -1: # baseline zone must stay where it is
						thisZone.setSize_( thisZone.size + fuzzValue * factor )
					else:
						thisZone.setPosition_( thisZone.position - fuzzValue * factor )
						thisZone.setSize_( thisZone.size + (fuzzValue * 2) * factor )
					
			if not self.SavePreferences( self ):
				print("Note: could not write preferences.")
			
			self.w.close()
		except Exception as e:
			raise e

BlueFuzzer()
