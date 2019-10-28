#MenuTitle: Punctuation Unifier
# -*- coding: utf-8 -*-
__doc__="""
Tries to sync the shape of the period (and comma) in colon, semicolon, periodcentered, exclam, question, exclamdown, questiondown.
"""

import vanilla
from Foundation import NSPoint

class PunctuationUnifier( object ):
	periodBase = ("comma", "semicolon")
	commaBase = ("period", "colon", "semicolon", "periodcentered", "exclam", "question", "exclamdown", "questiondown", "interrobang", "invertedinterrobang")
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 260
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Punctuation Unifier", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.PunctuationUnifier.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Unifies the shapes of the periods in punctuation.", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.periodBaseText = vanilla.TextBox( (inset, linePos+2, 100, 14), u"Model for period:", sizeStyle='small', selectable=True )
		self.w.periodBase = vanilla.PopUpButton( (inset+100, linePos, -inset, 17), self.periodBase, sizeStyle='small', callback=self.SavePreferences )
		linePos += lineHeight
		
		self.w.commaBaseText = vanilla.TextBox( (inset, linePos+2, 100, 14), u"Model for comma:", sizeStyle='small', selectable=True )
		self.w.commaBase = vanilla.PopUpButton( (inset+100, linePos, -inset, 17), self.commaBase, sizeStyle='small', callback=self.SavePreferences )
		linePos += lineHeight
		
		self.w.scaleToHeight = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Scale to height", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		
		self.w.text_1 = vanilla.TextBox( (inset-1, linePos+2, 75, 14), "inset", sizeStyle='small' )
		self.w.popup_1 = vanilla.PopUpButton( (inset+80, linePos, 50, 17), [str(x) for x in range( 3, 12 )], callback=self.SavePreferences, sizeStyle='small' )
		self.w.edit_1 = vanilla.EditText( (inset+80+55, linePos, -inset, 19), "insert text here", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Run", sizeStyle='regular', callback=self.PunctuationUnifierMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Punctuation Unifier' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.PunctuationUnifier.popup_1"] = self.w.popup_1.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.PunctuationUnifier.popup_1", 0)
			self.w.popup_1.set( Glyphs.defaults["com.mekkablue.PunctuationUnifier.popup_1"] )
		except:
			return False
			
		return True
	
	def centerOfRect(self, rect):
		"""
		Returns the center of NSRect rect as an NSPoint.
		"""
		center = NSPoint( rect.origin.x + rect.size.width/2, rect.origin.y + rect.size.height/2 )
		return center
		

	def PunctuationUnifierMain( self, sender ):
		try:
			thisFont = Glyphs.font # frontmost font
			"""
			period, colon, semicolon, periodcentered, exclam, question, exclamdown questiondown
			comma, semicolon
			"""
			
			
			if not self.SavePreferences( self ):
				print "Note: 'Punctuation Unifier' could not write preferences."
			
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Punctuation Unifier Error: %s" % e
			import traceback
			print traceback.format_exc()

PunctuationUnifier()