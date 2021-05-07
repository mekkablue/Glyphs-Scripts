#MenuTitle: Remove Kerning Exceptions
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Removes all kernings glyph-glyph, group-glyph, and glyph-group; only keeps group-group kerning.
"""

import vanilla

class RemoveKerningExceptions( object ):
	prefDomain = "com.mekkablue.RemoveKerningExceptions"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 160
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Remove Kerning Exceptions", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "%s.mainwindow"%self.prefDomain # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.glyphGlyph = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Remove 🅰️🅰️ glyph-to-glyph pairs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		self.w.glyphGroup = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Remove 🅰️🔠 glyph-to-group pairs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		self.w.groupGlyph = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Remove 🔠🅰️ group-to-glyph pairs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.removeOnMastersText = vanilla.TextBox( (inset, linePos+2, 70, 14), "Remove on:", sizeStyle='small', selectable=True )
		self.w.removeOnMasters = vanilla.PopUpButton( (inset+70, linePos, -inset, 17), ("current master", "⚠️ all masters of current font", "⚠️ all masters of ⚠️ all open fonts"), sizeStyle='small', callback=self.SavePreferences )
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-100-inset, -20-inset, -inset, -inset), "Remove", sizeStyle='regular', callback=self.RemoveKerningExceptionsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Remove Kerning Exceptions' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def updateGUI(self, sender=None):
		anyOptionIsSelected = self.w.glyphGlyph.get() or self.w.glyphGroup.get() or self.w.groupGlyph.get()
		self.w.runButton.enable(anyOptionIsSelected)
	
	def domain(self, key):
		return "%s.%s" % (self.prefDomain, key)

	def preference(self, key):
		domain = self.domain(key)
		return Glyphs.defaults[domain]
	
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults[self.domain("glyphGlyph")] = self.w.glyphGlyph.get()
			Glyphs.defaults[self.domain("glyphGroup")] = self.w.glyphGroup.get()
			Glyphs.defaults[self.domain("groupGlyph")] = self.w.groupGlyph.get()
			Glyphs.defaults[self.domain("removeOnMasters")] = self.w.removeOnMasters.get()
			
			self.updateGUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False
	
	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault(self.domain("glyphGlyph"), 1)
			Glyphs.registerDefault(self.domain("glyphGroup"), 1)
			Glyphs.registerDefault(self.domain("groupGlyph"), 1)
			Glyphs.registerDefault(self.domain("removeOnMasters"), 0)
			
			# load previously written prefs:
			self.w.glyphGlyph.set( self.preference("glyphGlyph") )
			self.w.glyphGroup.set( self.preference("glyphGroup") )
			self.w.groupGlyph.set( self.preference("groupGlyph") )
			self.w.removeOnMasters.set( self.preference("removeOnMasters") )
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def RemoveKerningExceptionsMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Remove Kerning Exceptions' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires at least one font. Open a font and run the script again.", OKButton=None)
			else:
				glyphGlyph = self.preference("glyphGlyph")
				glyphGroup = self.preference("glyphGroup")
				groupGlyph = self.preference("groupGlyph")
				removeOnMasters = self.preference("removeOnMasters")
				
				if removeOnMasters==2:
					fonts = Glyphs.fonts
					allMasters = True
				else:
					fonts = (thisFont,)
					if removeOnMasters==0:
						allMasters = False
					else:
						allMasters = True
				
				for thisFont in fonts:
					print("\nRemoving kerning exceptions in: %s" % thisFont.familyName)
					if thisFont.filepath:
						print("📄 %s" % thisFont.filepath)
					else:
						print("⚠️ The font file has not been saved yet.")
					
					totalCount = 0
					for thisMaster in thisFont.masters:
						if allMasters or thisMaster==thisFont.selectedFontMaster:
							pairsToBeRemoved = []
							for leftSide in thisFont.kerning[thisMaster.id].keys():
								leftSideIsGlyph = not leftSide.startswith("@")
								for rightSide in thisFont.kerning[thisMaster.id][leftSide].keys():
									rightSideIsGlyph = not rightSide.startswith("@")
									removeGlyphGlyph = leftSideIsGlyph and rightSideIsGlyph and glyphGlyph
									removeGlyphGroup = leftSideIsGlyph and not rightSideIsGlyph and glyphGroup
									removeGroupGlyph = not leftSideIsGlyph and rightSideIsGlyph and groupGlyph
									if removeGroupGlyph or removeGlyphGroup or removeGlyphGlyph:
										pairsToBeRemoved.append( (leftSide, rightSide) )
							countOfDeletions = len(pairsToBeRemoved)
							totalCount += countOfDeletions
							print("🚫 Removing %i pairs in master ‘%s’..." % ( countOfDeletions, thisMaster.name))
							for pair in pairsToBeRemoved:
								left, right = pair
								if not left.startswith("@"):
									left = thisFont.glyphForId_(left).name
								if not right.startswith("@"):
									right = thisFont.glyphForId_(right).name
								thisFont.removeKerningForPair(thisMaster.id, left, right)
			
			# Final report:
			Glyphs.showNotification( 
				"Removed %i Exceptions" % (totalCount),
				"Processed %i font%s. Details in Macro Window" % (
					len(fonts),
					"" if len(fonts)!=1 else "s",
				),
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Kerning Exceptions Error: %s" % e)
			import traceback
			print(traceback.format_exc())

RemoveKerningExceptions()