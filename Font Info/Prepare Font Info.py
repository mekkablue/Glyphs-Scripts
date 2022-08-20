#MenuTitle: Prepare Font Info
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Prepare open fonts for a modern font production and git workflow.
"""

import vanilla

class PrepareFontforGit( object ):
	prefID = "com.mekkablue.PrepareFontforGit"
	prefs = (
		"preventDisplayStrings",
		"preventTimeStamps",
		"preventMacName",
		"fileFormat",
		"removeGlyphOrder",
	)
	parameterDict = {
		"preventDisplayStrings": ("Write DisplayStrings", 0),
		"preventTimeStamps": ("Write lastChange", 0),
		"preventMacName": ("Export Mac Name Table Entries", 0),
	}
	
	removeParameters = (
		"glyphOrder",
	)
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 360
		windowHeight = 200
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Prepare File", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), "Make the font git-ready with these custom parameters:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.preventDisplayStrings = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Prevent storing of tab contents (Write DisplayStrings = OFF)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.preventTimeStamps = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Prevent storing of time stamps (Write lastChange = OFF)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.preventMacName = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Prevent export of Mac entries in name table", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.fileFormat = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Set File Format to Glyphs version 3", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.removeGlyphOrder = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Remove glyphOrder", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		# Apply Scope:
		self.w.applyToFontsText = vanilla.TextBox( (inset, -18-inset+2, 60, 14), "Apply to:", sizeStyle='small', selectable=True )
		self.w.applyToFonts = vanilla.PopUpButton( (inset+60, -18-inset, -120-inset, 17), ("frontmost font only", "⚠️ ALL open fonts"), sizeStyle='small', callback=self.SavePreferences )
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-100-inset, -20-inset, -inset, -inset), "Apply", sizeStyle='regular', callback=self.PrepareFontforGitMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Prepare Font Info' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def updateGUI(self, sender=None):
		onOff = any( [self.pref(prefName) for prefName in self.prefs] )
		self.w.applyToFonts.enable(onOff)
		self.w.runButton.enable(onOff)
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			for prefName in self.prefs:
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
				
			self.updateGUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			for prefName in self.prefs:
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), prefName.startswith("include") or prefName.startswith("reuse"))
				# load previously written prefs:
				getattr(self.w, prefName).set( self.pref(prefName) )
			
			self.updateGUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def setParameterForFont(self, font, parameterName, parameterValue=0, remove=False):
		while font.customParameters[parameterName]:
			del font.customParameters[parameterName]
			
		if remove:
			print("🚫 Font Info > Font > Custom Parameters > %s" % parameterName)
		else:
			font.customParameters[parameterName] = parameterValue
			print("✅ Font Info > Font > Custom Parameters > %s = %i" % (parameterName, parameterValue))
	
	def PrepareFontforGitMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Prepare Font Info' could not write preferences.")
			
			if len(Glyphs.fonts)==0:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				applyToFonts = self.pref("applyToFonts")
				
				if applyToFonts==1:
					theseFonts = Glyphs.fonts
				else:
					theseFonts = (Glyphs.font,)
			
				for thisFont in theseFonts:
					print("🧑🏽‍💻 Prepare Font for Git: %s" % thisFont.familyName)
					if thisFont.filepath:
						print("📄 %s" % thisFont.filepath)
					else:
						print("⚠️ The font file has not been saved yet.")
					
					# set parameters:
					for optionKey in self.parameterDict.keys():
						if bool(self.pref(optionKey)):
							parameterName, parameterValue = self.parameterDict[optionKey]
							self.setParameterForFont(thisFont, parameterName, parameterValue)
					
					# remove parameters:
					for optionKey in [prefName for prefName in self.prefs if prefName.startswith("remove")]:
						parameterName = optionKey[6].lower() + optionKey[7:]
						self.setParameterForFont(thisFont, parameterName, remove=True)
					
					# set file format:
					if self.pref("fileFormat"):
						if thisFont.formatVersion != 3:
							thisFont.formatVersion = 3
							print("✅ Font Info > Other > File Format: 3")
						else:
							print("😮‍💨 Font Info > Other > File Format was already 3")
					
					print()
			
			self.w.close() # delete if you want window to stay open

			# Final report:
			Glyphs.showNotification( 
				"%s: Done" % (thisFont.familyName),
				"‘Prepare Font Info’ is finished. Details in Macro Window",
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Prepare Font Info Error: %s" % e)
			import traceback
			print(traceback.format_exc())

PrepareFontforGit()