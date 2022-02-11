#MenuTitle: New Tab with Nested Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Opens a new tab with all nested components.
"""

import vanilla

def layerContainsNestedComponents(thisLayer):
	if thisLayer.components:
		for thisComponent in thisLayer.components:
			originalLayer = thisComponent.componentLayer
			if originalLayer.components:
				return True
	return False

def glyphContainsNestedComponents(thisGlyph):
	for thisLayer in thisGlyph.layers:
		if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
			if layerContainsNestedComponents(thisLayer):
				return True
	return False


class NewTabwithNestedComponents( object ):
	prefID = "com.mekkablue.NewTabwithNestedComponents"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 260
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"New Tab with Nested Components", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), "Find nested components in frontmost fonts", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.includeNonExporting = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Find", sizeStyle='regular', callback=self.NewTabwithNestedComponentsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'New Tab with Nested Components' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults[self.domain("popup_1")] = self.w.popup_1.get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault(self.domain("popup_1"), 0)
			
			# load previously written prefs:
			self.w.popup_1.set( self.pref("popup_1") )
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def NewTabwithNestedComponentsMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'New Tab with Nested Components' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			affectedNames = []
			
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("New Tab with Nested Components Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
			
				includeNonExporting = self.pref("includeNonExporting")

				for thisGlyph in thisFont.glyphs:
					if thisGlyph.export or includeNonExporting:
						if glyphContainsNestedComponents(thisGlyph):
							affectedNames.append(thisGlyph.name)
							print("⚠️ nested component in %s" % thisGlyph.name)

				print(", ".join(affectedNames))
				thisFont.currentTab.text = "/"+"/".join(affectedNames)
				self.w.close() # delete if you want window to stay open

			# Final report:
			Glyphs.showNotification( 
				"%s: Done" % (thisFont.familyName),
				"%i nested component%s found. Details in Macro Window" % (
					len(affectedNames),
					"" if len(affectedNames)==1 else "s",
					),
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("New Tab with Nested Components Error: %s" % e)
			import traceback
			print(traceback.format_exc())

NewTabwithNestedComponents()