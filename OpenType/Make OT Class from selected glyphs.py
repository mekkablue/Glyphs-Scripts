#MenuTitle: Make OT class from selected glyphs
"""Creates a new OT class based on the selected glyphs."""

import vanilla

class OTClassCreator( object ):
	def __init__( self ):
		self.w = vanilla.FloatingWindow( (300, 80), "Make OT class" )
		
		self.w.text_otclass = vanilla.TextBox((15, 12+2, 130, 14), "OT class name:", sizeStyle='small')
		self.w.class_name = vanilla.EditText((105, 12, -90, 17), "xxxx", sizeStyle='small', callback=self.buttonCheck)
		self.w.overwrite_check = vanilla.CheckBox((105, 32+2, -15, 20), "Overwrite existing class", sizeStyle='small', callback=self.buttonCheck, value=True)
		self.w.class_name_check = vanilla.TextBox((105-2, 32+5+20, -15, 14), "Class name appears to be ok.", sizeStyle='small')
		self.w.make_button = vanilla.Button((-80, 12, -15, 17), "Create", sizeStyle='small', callback=self.createClass)
		#self.w.setDefaultButton( self.w.make_button )

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
		else:
			self.w.make_button.enable( False )
			self.w.class_name_check.set( "Illegal characters." )
	
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
		
		myClassName = str( self.w.class_name.get() )
		myClassCode = " ".join( listOfGlyphNames )
		
		if myClassName in listOfClassNames:
			print "Changing class", myClassName, "to these glyphs:", myClassCode
			Font.classes[ myClassName ].code = myClassCode
			
		else:
			print "Creating class", myClassName, "with these glyphs:", myClassCode
			myNewClass = GSClass()
			myNewClass.name = myClassName
			myNewClass.code = myClassCode
			Font.classes.append( myNewClass )
		
		self.w.close()
		
OTClassCreator()




