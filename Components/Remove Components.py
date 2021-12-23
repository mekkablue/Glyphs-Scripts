#MenuTitle: Remove Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Removes the specified component from all (selected) glyphs.
"""

import vanilla

def match(first, second):
	# https://www.geeksforgeeks.org/wildcard-character-matching/
	
	# If we reach at the end of both strings, we are done
	if len(first) == 0 and len(second) == 0:
		return True

	# Make sure that the characters after '*' are present
	# in second string. This function assumes that the first
	# string will not contain two consecutive '*'
	if len(first) > 1 and first[0] == '*' and len(second) == 0:
		return False

	# If the first string contains '?', or current characters
	# of both strings match
	if (len(first) > 1 and first[0] == '?') or (len(first) != 0
		and len(second) !=0 and first[0] == second[0]):
		return match(first[1:],second[1:]);

	# If there is *, then there are two possibilities
	# a) We consider current character of second string
	# b) We ignore current character of second string.
	if len(first) !=0 and first[0] == '*':
		return match(first[1:],second) or match(first,second[1:])

	return False

def deleteCornerComponent( componentName, thisLayer ):
	indToDel = []
	count = 0
	for i, h in enumerate(thisLayer.hints):
		if h.isCorner:
			#help(h)
			if match(componentName, h.name):
				indToDel += [i]
	indToDel = list(reversed(indToDel))
	for i in indToDel:
		del thisLayer.hints[i]
		count += 1
	
	if count:
		print("  ❌ Removed %i corner component%s from layer: %s" % (
				count, 
				"" if count==1 else "s",
				thisLayer.name,
			))

class RemoveComponentfromSelectedGlyphs( object ):
	prefID = "com.mekkablue.RemoveComponents"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 250
		windowHeight = 135
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Remove Components", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.text1 = vanilla.TextBox( (inset, linePos, 115, 14), "Remove component", sizeStyle='small' )
		self.w.componentName  = vanilla.ComboBox(
				(inset+115, linePos-3, -30-inset, 19), 
				self.glyphList(), 
				sizeStyle='small' 
			)
		self.w.updateButton = vanilla.SquareButton( (-inset-20, linePos-2, -inset, 18), "↺", sizeStyle='small', callback=self.updateUI )
		
		linePos += lineHeight
		self.w.fromWhere = vanilla.RadioGroup(
				(inset, linePos, -inset, 40),
				("from all selected glyphs", "⚠️ from all glyphs in the font"),
				callback=self.SavePreferences,
				sizeStyle = 'small',
			)
		
		# Run Button:
		self.w.runButton = vanilla.Button((-100-inset, -20-inset, -inset, -inset), "Remove", sizeStyle='regular', callback=self.RemoveComponentfromSelectedGlyphsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Remove Component from Selected Glyphs' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def updateUI(self):
		glyphList = self.glyphList()
		if glyphList:
			self.w.componentName.setItems(glyphList)
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults[ self.domain("componentName") ] = self.w.componentName.get()
			Glyphs.defaults[ self.domain("fromWhere") ] = self.w.fromWhere.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault( self.domain("componentName"), "a")
			Glyphs.registerDefault( self.domain("fromWhere"), "0")
			self.w.componentName.set( self.pref("componentName") )
			self.w.fromWhere.set( self.pref("fromWhere") )
		except:
			return False
			
		return True
		
	def glyphList(self):
		thisFont = Glyphs.font
		if thisFont:
			return sorted([g.name for g in thisFont.glyphs])
		else:
			return []
	
	def removeComponentFromLayer(self, componentName, thisLayer):
		theseComponents = thisLayer.components
		numberOfComponents = len( theseComponents )
		removedComponents = []
		if numberOfComponents > 0:
			for i in range(numberOfComponents)[::-1]:
				thisComponent = theseComponents[i]
				if match(componentName, thisComponent.componentName):
					if Glyphs.versionNumber >= 3:
						index = thisLayer.shapes.index(thisComponent)
						del(thisLayer.shapes[index])
						removedComponents.append(thisComponent.componentName)
					else:
						thisLayer.removeComponent_( thisComponent )
		
		if removedComponents:
			print("  ❌ Removed %i component%s (%s) from layer: %s" % (
					len(removedComponents), 
					"" if len(removedComponents)==1 else "s",
					", ".join(set(removedComponents)), 
					thisLayer.name,
				))
			
		deleteCornerComponent(componentName, thisLayer)
		
	def removeComponentFromGlyph(self, componentName, thisGlyph):
		print("🔠 %s" % thisGlyph.name)
		for thisLayer in thisGlyph.layers:
			self.removeComponentFromLayer( componentName, thisLayer )

	def RemoveComponentfromSelectedGlyphsMain( self, sender ):
		# brings macro window to front and clears its log:
		Glyphs.clearLog()
		print( "Removing Components:" )
		
		try:
			thisFont = Glyphs.font # frontmost font
			listOfGlyphs = thisFont.glyphs 
			
			if self.pref("fromWhere") == 0:
				listOfGlyphs = [l.parent for l in thisFont.selectedLayers] # active layers of currently selected glyphs
				
			componentName = self.pref("componentName")
			for thisGlyph in listOfGlyphs:
				self.removeComponentFromGlyph( componentName, thisGlyph )
			
			if not self.SavePreferences( self ):
				print("Note: 'Remove Component from Selected Glyphs' could not write preferences.")
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Component from Selected Glyphs Error: %s" % e)

RemoveComponentfromSelectedGlyphs()