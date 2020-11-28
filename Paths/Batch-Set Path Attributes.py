#MenuTitle: Batch-Set Path Attributes
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Set path attributes of all paths in selected glyphs, the master, the font, etc.
"""

import vanilla

scopeMaster = (
	"current master",
	"all masters",
)

scopeGlyphs = (
	"selected glyphs",
	"exporting glyphs",
	"all glyphs",
)

class BatchSetPathAttributes( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 200
		windowHeight = 190
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Batch-Set Path Attributes", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.BatchSetPathAttributes.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		indent = 70
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, indent, 14), "Attributes in", sizeStyle='small', selectable=True )
		self.w.scopeGlyphs = vanilla.PopUpButton( (inset+indent, linePos, -inset, 17), scopeGlyphs, sizeStyle='small', callback=self.SavePreferences )
		linePos += lineHeight
		self.w.scopeMasterText = vanilla.TextBox( (inset, linePos+2, indent, 14), "for paths on", sizeStyle='small', selectable=True )
		self.w.scopeMaster = vanilla.PopUpButton( (inset+indent, linePos, -inset, 17), scopeMaster, sizeStyle='small', callback=self.SavePreferences )
		linePos += lineHeight+5
		
		indent = 80
		
		tooltip = ""
		self.w.lineCapStartText = vanilla.TextBox( (inset*2, linePos+2, indent, 14), "lineCapStart", sizeStyle='small', selectable=True )
		self.w.lineCapStart = vanilla.EditText( (inset*2+indent, linePos, -inset, 19), "2", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		tooltip = " "
		self.w.lineCapEndText = vanilla.TextBox( (inset*2, linePos+2, indent, 14), "lineCapEnd", sizeStyle='small', selectable=True )
		self.w.lineCapEnd = vanilla.EditText( (inset*2+indent, linePos, -inset, 19), "2", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		tooltip = "Width of the path in units."
		self.w.strokeWidthText = vanilla.TextBox( (inset*2, linePos+2, indent, 14), "strokeWidth", sizeStyle='small', selectable=True )
		self.w.strokeWidth = vanilla.EditText( (inset*2+indent, linePos, -inset, 19), "20", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight

		# Buttons at the bottom:
		self.w.extractButton = vanilla.Button( (inset, -20-inset, 80, -inset), "Extract", sizeStyle='regular', callback=self.extractAttributes )
		self.w.extractButton.getNSButton().setToolTip_("Extract attributes from currently selected path.")
		
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Apply", sizeStyle='regular', callback=self.BatchSetPathAttributesMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Batch-Set Path Attributes' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def extractAttributes(self, sender=None):
		thisFont = Glyphs.font
		if thisFont and thisFont.selectedLayers:
			currentLayer = thisFont.selectedLayers[0]
			for thisPath in currentLayer.paths:
				if thisPath.selected:
					lineCapStart = thisPath.attributeForKey_("lineCapStart")
					if lineCapStart != None:
						Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.lineCapStart"] = lineCapStart
						
					lineCapEnd = thisPath.attributeForKey_("lineCapEnd")
					if lineCapEnd != None:
						Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.lineCapEnd"] = lineCapEnd
						
					strokeWidth = thisPath.attributeForKey_("strokeWidth")
					if strokeWidth != None:
						Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.strokeWidth"] = strokeWidth
		
		self.LoadPreferences()
		
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.scopeGlyphs"] = self.w.scopeGlyphs.get()
			Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.scopeMaster"] = self.w.scopeMaster.get()
			Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.lineCapStart"] = self.w.lineCapStart.get()
			Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.lineCapEnd"] = self.w.lineCapEnd.get()
			Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.strokeWidth"] = self.w.strokeWidth.get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.BatchSetPathAttributes.scopeGlyphs", 0)
			Glyphs.registerDefault("com.mekkablue.BatchSetPathAttributes.scopeMaster", 0)
			Glyphs.registerDefault("com.mekkablue.BatchSetPathAttributes.lineCapStart", 2)
			Glyphs.registerDefault("com.mekkablue.BatchSetPathAttributes.lineCapEnd", 2)
			Glyphs.registerDefault("com.mekkablue.BatchSetPathAttributes.strokeWidth", 20)
			
			# load previously written prefs:
			self.w.scopeGlyphs.set( Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.scopeGlyphs"] )
			self.w.scopeMaster.set( Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.scopeMaster"] )
			self.w.lineCapStart.set( Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.lineCapStart"] )
			self.w.lineCapEnd.set( Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.lineCapEnd"] )
			self.w.strokeWidth.set( Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.strokeWidth"] )
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def BatchSetPathAttributesMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Batch-Set Path Attributes' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Batch-Set Path Attributes Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
				
				scopeGlyphs = Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.scopeGlyphs"]
				scopeMaster = Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.scopeMaster"]
				lineCapStart = int(Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.lineCapStart"])
				lineCapEnd = int(Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.lineCapEnd"])
				strokeWidth = int(Glyphs.defaults["com.mekkablue.BatchSetPathAttributes.strokeWidth"])
				
				if scopeGlyphs==0:
					# selected glyphs
					glyphs = [l.parent for l in thisFont.selectedLayers]
				elif scopeGlyphs==1:
					# exporting glyphs
					glyphs = [g for g in thisFont.glyphs if g.export]
				elif scopeGlyphs==2:
					# all glyphs
					glyphs = thisFont.glyphs
				else:
					glyphs = ()
					
				currentFontMasterID = thisFont.selectedFontMaster.id
				print("🔠 Processing %i glyph%s...\n" % (
					len(glyphs),
					"" if len(glyphs)==1 else "s",
					))
				
				if not glyphs:
					Message(title="Glyph Scope Error", message="No applicable glyphs found. Please select the glyph scope and run the script again.", OKButton=None)
				else:
					for thisGlyph in glyphs:
						print("  %s"%thisGlyph.name)
						for thisLayer in thisGlyph.layers:
							# scopeMaster: 0 = current master, 1 = all masters
							if scopeMaster==1 or (scopeMaster==0 and thisLayer.associatedMasterId==currentFontMasterID):
								if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
									for thisPath in thisLayer.paths:
										thisPath.setAttribute_forKey_(lineCapStart, "lineCapStart")
										thisPath.setAttribute_forKey_(lineCapEnd, "lineCapEnd")
										thisPath.setAttribute_forKey_(strokeWidth, "strokeWidth")

			# Final report:
			Glyphs.showNotification( 
				"%s: Done" % (thisFont.familyName),
				"Batch-Set Path Attributes is finished. Details in Macro Window",
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Batch-Set Path Attributes Error: %s" % e)
			import traceback
			print(traceback.format_exc())

BatchSetPathAttributes()