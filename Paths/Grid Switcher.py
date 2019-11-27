#MenuTitle: Grid Switcher
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Toggles grid between two gridstep values.
"""

import vanilla

class GridOnOff( object ):
	def __init__( self ):
		self.gridStep1default = 1
		self.gridStep2default = 0
		
		currentGridStep = Glyphs.font.gridMain()
		self.w = vanilla.FloatingWindow( (170, 110), "Grid Switcher", autosaveName="com.mekkablue.GridOnOff.mainwindow" )
		self.w.grid1 = vanilla.EditText( (15, 12, 65, 15+3), "1", sizeStyle = 'small')
		self.w.grid2 = vanilla.EditText( (-80, 12, -15, 15+3), "50", sizeStyle = 'small')
		self.w.currentGridStep = vanilla.TextBox( (15, 40, -15, 22), "Current Grid Step: %i" % currentGridStep, sizeStyle='regular' )
		self.w.switchButton = vanilla.Button((15, -22-15, -15, -15), "Switch Grid", sizeStyle='regular', callback=self.GridOnOffMain )
		self.w.setDefaultButton( self.w.switchButton )

		self.w.center()
		self.w.open()
		self.w.makeKey()
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Grid Switcher' could not load preferences. Will resort to defaults"
		

	def GridOnOffMain( self, sender ):
		try:
			try:
				gridStep1 = int( Glyphs.defaults["com.mekkablue.gridswitch.grid1"] )
			except:
				gridStep1 = self.gridStep1default
				self.w.grid1.set( gridStep1 )
			
			try:
				gridStep2 = int( Glyphs.defaults["com.mekkablue.gridswitch.grid2"] )
			except:
				gridStep2 = self.gridStep2default
				self.w.grid2.set( gridStep2 )
			
			gridStep = Glyphs.font.gridMain()
			if gridStep != gridStep1:
				newGridStep = gridStep1
			else:
				newGridStep = gridStep2
				
			Glyphs.font.setGridMain_( newGridStep )
			self.w.currentGridStep.set( "Current Grid Step: %i" % newGridStep )
			
			if not self.SavePreferences( self ):
				print "Note: 'Grid Switcher' could not write preferences."
			
		except Exception, e:
			raise e
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.gridswitch.grid1"] = self.w.grid1.get()
			Glyphs.defaults["com.mekkablue.gridswitch.grid2"] = self.w.grid2.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.gridswitch.grid1", 1)
			Glyphs.registerDefault("com.mekkablue.gridswitch.grid2": 0)
			self.w.grid1.set( Glyphs.defaults["com.mekkablue.gridswitch.grid1"] )
			self.w.grid2.set( Glyphs.defaults["com.mekkablue.gridswitch.grid2"] )
			try:
				self.gridStep1default = int( Glyphs.defaults["com.mekkablue.gridswitch.grid1"] )
				self.gridStep2default = int( Glyphs.defaults["com.mekkablue.gridswitch.grid2"] )
			except:
				pass
		except:
			return False
			
		return True
	
GridOnOff()
