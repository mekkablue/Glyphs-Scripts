#MenuTitle: Set Hidden App Preferences
# -*- coding: utf-8 -*-
__doc__="""
GUI for a number of hidden prefs, hard to memorize otherwise.
"""

import vanilla

class SetHiddenAppPreferences( object ):
	prefs = (
		"drawShadowAccents",
		"GSftxenhancerPath",
		"GSKerningIncrementHigh",
		"GSKerningIncrementLow",
		"GSShowVersionNumberInDockIcon",
		"GSShowVersionNumberInTitleBar",
		"GSSpacingIncrementHigh",
		"GSSpacingIncrementLow",
		"MacroCodeFontSize",
		"TextModeNumbersThreshold",
		"TTPreviewAlsoShowOffCurveIndexes",
		"GSFontViewDisableDarkMode",
	)
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 120
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Set Hidden App Preferences", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.SetHiddenAppPreferences.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), "Choose and apply the app defaults:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.pref = vanilla.ComboBox( (inset, linePos-1, -inset-100, 23), self.prefs, callback=self.SavePreferences, sizeStyle='regular' )
		self.w.pref.getNSComboBox().setFont_(NSFont.userFixedPitchFontOfSize_(11))
		self.w.prefValue = vanilla.EditText( (-inset-90, linePos, -inset, 21), "", sizeStyle='regular' )
		linePos += lineHeight
		
		# Run Button:
		self.w.delButton = vanilla.Button( (-170-inset, -20-inset, -90-inset, -inset), "Delete", sizeStyle='regular', callback=self.SetHiddenAppPreferencesMain )
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Apply", sizeStyle='regular', callback=self.SetHiddenAppPreferencesMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Set Hidden App Preferences' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def updatePrefValue( self, sender ):
		self.w.prefValue.set( Glyphs.defaults[self.w.pref.get()] )
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.SetHiddenAppPreferences.pref"] = self.w.pref.get()
			
			if sender == self.w.pref:
				self.updatePrefValue(None)
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.SetHiddenAppPreferences.pref", "")
			self.w.pref.set( Glyphs.defaults["com.mekkablue.SetHiddenAppPreferences.pref"] )
			self.updatePrefValue(None)
		except:
			return False
			
		return True

	def SetHiddenAppPreferencesMain( self, sender ):
		try:
			if sender == self.w.delButton:
				del Glyphs.defaults[ self.w.pref.get() ]
				self.w.prefValue.set( None )
				print "Deleted pref: %s" % self.w.pref.get()
				
			elif sender == self.w.runButton:
				Glyphs.defaults[ self.w.pref.get() ] = self.w.prefValue.get()
				print "Set pref: %s --> %s" % (self.w.pref.get(), self.w.prefValue.get())
				
			if not self.SavePreferences( self ):
				print "Note: 'Set Hidden App Preferences' could not write preferences."
			
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Set Hidden App Preferences Error: %s" % e
			import traceback
			print traceback.format_exc()

SetHiddenAppPreferences()