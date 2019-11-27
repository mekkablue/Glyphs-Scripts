#MenuTitle: New OT Class with Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Creates a new OT class containing the selected glyphs.
"""

import vanilla

class OTClassCreator( object ):
	def __init__( self ):
		self.w = vanilla.FloatingWindow( (400, 104), "Make OT Class from Selected Glyphs", minSize=(400, 120), maxSize=(500, 120) )
		
		self.w.text_otclass = vanilla.TextBox((15, 12+2, 130, 14), "OT class name:", sizeStyle='small')
		self.w.class_name = vanilla.EditText((105, 12-1, -90, 20), "xxxx", sizeStyle='small', callback=self.buttonCheck)
		self.w.overwrite_check = vanilla.CheckBox((105, 34, -15, 20), "Overwrite existing class", sizeStyle='small', callback=self.buttonCheck, value=True)
		self.w.keep_window = vanilla.CheckBox((105, 54, -15, 20), "Keep this window open", sizeStyle='small', callback=None, value=True)
		self.w.class_name_check = vanilla.TextBox((15, 80, -15, 14), "Class name appears to be ok.", sizeStyle='small')
		self.w.make_button = vanilla.Button((-80, 12, -15, 17), "Create", sizeStyle='small', callback=self.createClass)
		self.w.setDefaultButton( self.w.make_button )

		self.w.open()
		self.buttonCheck( self.w.class_name )
		
	def buttonCheck( self, sender ):
		myClassName = sender.get()
		existingClasses = [ c.name for c in Glyphs.font.classes ]
		
		#print existingClasses
		
		if myClassName in existingClasses:
			if self.w.overwrite_check.get() == False:
				self.w.make_button.enable( False )
				self.w.class_name_check.set( "Class name already exists." )
			else:
				self.w.make_button.enable( True )
				self.w.class_name_check.set( "Will overwrite existing class." )
		elif len( myClassName ) == 0 :
			self.w.make_button.enable( False )
			self.w.class_name_check.set( "Class name too short." )
		elif self.checkstring( myClassName ):
			self.w.make_button.enable( True )
			self.w.class_name_check.set( "Class name appears to be ok." )
		elif myClassName[0] in "0123456789":
			self.w.make_button.enable( False )
			self.w.class_name_check.set( "Class name must not start with a figure." )
		else:
			self.w.make_button.enable( False )
			self.w.class_name_check.set( "Illegal characters. Only use A-Z, a-z, figures, period, underscore." )
	
	def checkstring(self, teststring, ok=True):
		allowedchars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890._"
		
		if len( teststring ) > 1 :
			return self.checkstring( teststring[:-1], ok ) and ( teststring[-1] in allowedchars )
		else:
			# first char must not be a figure
			return ( teststring[-1] in allowedchars and teststring[-1] not in "1234567890" )
	
	def createClass(self, sender):
		Doc = Glyphs.currentDocument
		Font = Glyphs.font
		
		listOfGlyphNames = [ x.parent.name for x in Font.selectedLayers ]
		listOfClasses = Font.classes
		listOfClassNames = [ c.name for c in listOfClasses ]
		
		myClassName = self.w.class_name.get()
		myClassCode = " ".join( listOfGlyphNames )
		
		if myClassName in listOfClassNames:
			print("Changing class", myClassName, "to these glyphs:", myClassCode)
			Font.classes[ myClassName ].code = myClassCode
			
		else:
			print("Creating class", myClassName, "with these glyphs:", myClassCode)
			myNewClass = GSClass()
			myNewClass.name = myClassName
			myNewClass.code = myClassCode
			Font.classes.append( myNewClass )
		
		if not self.w.keep_window.get():
			self.w.close()
		
OTClassCreator()




