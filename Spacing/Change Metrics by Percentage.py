#MenuTitle: Change Metrics by Percentage
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
Increase sidebearings of selected glyphs by a percentage value.
"""

import vanilla

class ChangeMetricsbyPercentage( object ):
	def __init__( self ):
		self.w = vanilla.FloatingWindow( (430, 60), "Change Metrics of Selected Glyphs by Percentage", minSize=(430, 60), maxSize=(600, 60), autosaveName="com.mekkablue.ChangeMetricsbyPercentage.mainwindow" )

		self.w.text_1 = vanilla.TextBox( (15, 12+2, 50, 14), "Increase", sizeStyle='small' )
		self.w.text_2 = vanilla.TextBox( (155, 12+2, 20, 14), "by", sizeStyle='small' )
		self.w.text_3 = vanilla.TextBox( (-190, 12+2, -170, 14), "%", sizeStyle='small' )
		self.w.LSB = vanilla.CheckBox( (15+55,    12, 40, 18), "LSB", value=True, sizeStyle='small', callback=self.SavePreferences )
		self.w.RSB = vanilla.CheckBox( (15+55+45, 12, 40, 18), "RSB", value=True, sizeStyle='small', callback=self.SavePreferences )
		self.w.changeValue = vanilla.EditText( (180, 12, -196, 15+3), "+10.0", sizeStyle = 'small')
		
		self.w.runButton    = vanilla.Button((-90,    12-1, -15, 19), "Change", sizeStyle='small', callback=self.ChangeMetricsbyPercentageMain )
		self.w.revertButton = vanilla.Button((-90-80, 12-1, -95, 19), "Revert", sizeStyle='small', callback=self.ChangeMetricsbyPercentageMain )

		self.w.setDefaultButton( self.w.runButton )
		
		if not self.LoadPreferences():
			print("Could not load preferences. Will resort to defaults.")

		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.ChangeMetricsbyPercentage.LSB"] = self.w.LSB.get()
			Glyphs.defaults["com.mekkablue.ChangeMetricsbyPercentage.RSB"] = self.w.RSB.get()
			Glyphs.defaults["com.mekkablue.ChangeMetricsbyPercentage.changeValue"] = self.w.changeValue.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.ChangeMetricsbyPercentage.LSB", True)
			Glyphs.registerDefault("com.mekkablue.ChangeMetricsbyPercentage.RSB", True)
			Glyphs.registerDefault("com.mekkablue.ChangeMetricsbyPercentage.changeValue", "+10.0")
			self.w.LSB.set( Glyphs.defaults["com.mekkablue.ChangeMetricsbyPercentage.LSB"] )
			self.w.RSB.set( Glyphs.defaults["com.mekkablue.ChangeMetricsbyPercentage.RSB"] )
			self.w.changeValue.set( Glyphs.defaults["com.mekkablue.ChangeMetricsbyPercentage.changeValue"] )
		except:
			return False
			
		return True

	def ChangeMetricsbyPercentageMain( self, sender ):
		try:
			Font = Glyphs.font
			selectedLayers = Font.selectedLayers
			
			changeLSB = self.w.LSB.get()
			changeRSB = self.w.RSB.get()
			change = ( 100.0 + float( self.w.changeValue.get() ) ) / 100.0

			if sender == self.w.revertButton:
				change = 1.0 / change
			
			for thisLayer in selectedLayers:
				if len(thisLayer.paths)>0 or len(thisLayer.components)>0:
					if changeLSB:
						thisLayer.LSB *= change
					if changeRSB:
						thisLayer.RSB *= change
			
			if not self.SavePreferences( self ):
				print("Note: could not write preferences.")
			
			# self.w.close()
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(" Error: %s" % e)

ChangeMetricsbyPercentage()
