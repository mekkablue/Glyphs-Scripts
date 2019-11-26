from __future__ import print_function
#MenuTitle: Build Italic Shift Feature
# -*- coding: utf-8 -*-
__doc__="""
Creates and inserts GPOS feature code for shifting glyphs, e.g., parentheses and punctuation for the case feature.
"""

import vanilla, math
from Foundation import NSPoint

def updatedCode( oldCode, beginSig, endSig, newCode ):
	"""Replaces text in oldCode with newCode, but only between beginSig and endSig."""
	beginOffset = oldCode.find( beginSig )
	endOffset   = oldCode.find( endSig ) + len( endSig )
	newCode = oldCode[:beginOffset] + beginSig + newCode + "\n" + endSig + oldCode[endOffset:]
	return newCode

def createOTFeature( featureName = "case", 
                     featureCode = "# empty feature code", 
                     targetFont  = Glyphs.font,
                     codeSig     = "SHIFTED-GLYPHS" ):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	featureName: name of the feature (str),
	featureCode: the AFDKO feature code (str),
	targetFont: the GSFont object receiving the feature,
	codeSig: the code signature (str) used as delimiters.
	"""
	
	beginSig = "# BEGIN " + codeSig + "\n"
	endSig   = "# END "   + codeSig + "\n"
	
	if featureName in [ f.name for f in targetFont.features ]:
		# feature already exists:
		targetFeature = targetFont.features[ featureName ]
		targetFeature.automatic = 0
		
		# FEATURE:
		if beginSig in targetFeature.code:
			targetFeature.code = updatedCode( targetFeature.code, beginSig, endSig, featureCode )
		else:
			targetFeature.code += "\n" + beginSig + featureCode + "\n" + endSig
		
		# NOTES:
		if beginSig in targetFeature.notes:
			targetFeature.notes = updatedCode( targetFeature.notes, beginSig, endSig, featureCode )
		else:
			targetFeature.notes += "\n" + beginSig + featureCode + "\n" + endSig
			
		return "Updated existing OT feature '%s'." % featureName
	else:
		# create feature with new code:
		newFeature = GSFeature()
		newFeature.name = featureName
		newCode = beginSig + featureCode + "\n" + endSig
		newFeature.code = newCode
		newFeature.notes = newCode
		targetFont.features.append( newFeature )
		return "Created new OT feature '%s'" % featureName



class ItalicShiftFeature( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 440
		windowHeight = 160
		windowWidthResize  = 600 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Italic Shift Feature", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.ItalicShiftFeature.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		inset = 15
		lineStep = 22
		lineheight = 12
		self.w.text_1 = vanilla.TextBox( (inset-1, lineheight+2, -inset, 14), "Insert GPOS lookup for shifting punctuation in italic angle of 1st master:", sizeStyle='small' )
		
		lineheight += lineStep
		self.w.edit_1a = vanilla.EditText( (inset, lineheight, 70, 19), "case", sizeStyle = 'small', placeholder="smcp,c2sc", callback=self.SavePreferences)
		self.w.edit_1b = vanilla.EditText( (75+inset, lineheight, 55, 19), "100", sizeStyle = 'small', placeholder="80", callback=self.SavePreferences)
		self.w.edit_1c = vanilla.EditText( (75+75, lineheight, -inset, 19), "exclamdown questiondown", sizeStyle = 'small', placeholder="parenleft parenright bracketleft bracketright", callback=self.SavePreferences)

		lineheight += lineStep
		self.w.edit_2a = vanilla.EditText( (inset, lineheight, 70, 19), "case", sizeStyle = 'small', placeholder="smcp,c2sc", callback=self.SavePreferences)
		self.w.edit_2b = vanilla.EditText( (75+inset, lineheight, 55, 19), "50", sizeStyle = 'small', placeholder="80", callback=self.SavePreferences)
		self.w.edit_2c = vanilla.EditText( (75+75, lineheight, -inset, 19), "parenleft parenright braceleft braceright bracketleft bracketright", sizeStyle = 'small', placeholder="parenleft parenright bracketleft bracketright", callback=self.SavePreferences)

		lineheight += lineStep
		self.w.edit_3a = vanilla.EditText( (inset, lineheight, 70, 19), "", sizeStyle = 'small', placeholder="smcp,c2sc", callback=self.SavePreferences)
		self.w.edit_3b = vanilla.EditText( (75+inset, lineheight, 55, 19), "", sizeStyle = 'small', placeholder="80", callback=self.SavePreferences)
		self.w.edit_3c = vanilla.EditText( (75+75, lineheight, -inset, 19), "", sizeStyle = 'small', placeholder="parenleft parenright bracketleft bracketright", callback=self.SavePreferences)

		
		# Run Button:
		self.w.copyButton = vanilla.Button((-180-inset, -20-inset, -inset-90, -inset), "Copy Code", sizeStyle='regular', callback=self.ItalicShiftFeatureMain )
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Insert", sizeStyle='regular', callback=self.ItalicShiftFeatureMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Italic Shift Feature' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_1a"] = self.w.edit_1a.get()
			Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_1b"] = self.w.edit_1b.get()
			Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_1c"] = self.w.edit_1c.get()
			Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_2a"] = self.w.edit_2a.get()
			Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_2b"] = self.w.edit_2b.get()
			Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_2c"] = self.w.edit_2c.get()
			Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_3a"] = self.w.edit_3a.get()
			Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_3b"] = self.w.edit_3b.get()
			Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_3c"] = self.w.edit_3c.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.ItalicShiftFeature.edit_1a", "case")
			Glyphs.registerDefault("com.mekkablue.ItalicShiftFeature.edit_1b", "100")
			Glyphs.registerDefault("com.mekkablue.ItalicShiftFeature.edit_1c", "exclamdown questiondown")
			Glyphs.registerDefault("com.mekkablue.ItalicShiftFeature.edit_2a", "case")
			Glyphs.registerDefault("com.mekkablue.ItalicShiftFeature.edit_2b", "50")
			Glyphs.registerDefault("com.mekkablue.ItalicShiftFeature.edit_2c", "parenleft parenright braceleft braceright bracketleft bracketright")
			Glyphs.registerDefault("com.mekkablue.ItalicShiftFeature.edit_3a", "")
			Glyphs.registerDefault("com.mekkablue.ItalicShiftFeature.edit_3b", "")
			Glyphs.registerDefault("com.mekkablue.ItalicShiftFeature.edit_3c", "")
			self.w.edit_1a.set( Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_1a"] )
			self.w.edit_1b.set( Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_1b"] )
			self.w.edit_1c.set( Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_1c"] )
			self.w.edit_2a.set( Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_2a"] )
			self.w.edit_2b.set( Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_2b"] )
			self.w.edit_2c.set( Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_2c"] )
			self.w.edit_3a.set( Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_3a"] )
			self.w.edit_3b.set( Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_3b"] )
			self.w.edit_3c.set( Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_3c"] )
		except:
			return False
			
		return True

	def italicize( self, shift=100.0, italicAngle=0.0, pivotalY=0.0 ):
		"""
		Returns the italicized position of an NSPoint 'thisPoint'
		for a given angle 'italicAngle' and the pivotal height 'pivotalY',
		around which the italic slanting is executed, usually half x-height.
		Usage: myPoint = italicize(myPoint,10,xHeight*0.5)
		"""
		yOffset = shift - pivotalY # calculate vertical offset
		italicAngle = math.radians( italicAngle ) # convert to radians
		tangens = math.tan( italicAngle ) # math.tan needs radians
		horizontalDeviance = tangens * yOffset # vertical distance from pivotal point
		horizontalDeviance # x of point that is yOffset from pivotal point
		return horizontalDeviance
	
	def ItalicShiftFeatureMain( self, sender ):
		try:
			thisFont = Glyphs.font # frontmost font
			firstMaster = thisFont.masters[0]
			italicAngle = firstMaster.italicAngle
			features = {}
			
			for lookupIndex in (1,2,3):
				otFeature = Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_%ia"%lookupIndex]
				verticalShift = Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_%ib"%lookupIndex]
				glyphNames = Glyphs.defaults["com.mekkablue.ItalicShiftFeature.edit_%ic"%lookupIndex]
				
				if otFeature and len(otFeature)>3 and glyphNames:
					if verticalShift:
						verticalShift = int(verticalShift)
						if verticalShift != 0:
							otCode = "\tpos [%s] <%i %i 0 0>;\n" % ( 
								glyphNames, 
								self.italicize(shift=verticalShift, 
								italicAngle=italicAngle), 
								verticalShift 
								)
							
							if otFeature in features:
								features[otFeature] += otCode
							else:
								features[otFeature] = otCode
							
			for otFeature in features.keys():
				lookupName = "italicShift_%s" % otFeature
				otCode = "lookup %s {\n" % lookupName
				otCode += features[otFeature]
				otCode += "} %s;" % lookupName
				createOTFeature( 
					featureName=otFeature, 
					codeSig="ITALIC-SHIFT-%s"%otFeature.upper() ,
					targetFont = thisFont,
					featureCode = otCode,
					)
				
			
			if not self.SavePreferences( self ):
				print("Note: 'Italic Shift Feature' could not write preferences.")
			
			self.w.close() # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Italic Shift Feature Error: %s" % e)
			import traceback
			print(traceback.format_exc())

ItalicShiftFeature()