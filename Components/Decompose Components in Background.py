#MenuTitle: Decompose Components in Background
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from GlyphsApp import GSLayer, GSBackgroundLayer
import vanilla as vl
__doc__="""
Will backup foregrounds into backgrounds, and decompose backgrounds. Useful for keeping original designs of composites for reference.
"""

class Decompose_Components_in_Background(object):
	key = "com.mekkablue.Decompose_Components_in_Background"
	windowHeight = 216
	padding = (10,10,12)
	buttonHeight = 20
	textHeight = 14
	sizeStyle = 'small'
	glyphsOptions = (
		"Backgrounds of selected glyphs in frontmost font", 
		"⚠️ All glyph backgrounds in current font",
		"⚠️ All glyph backgrounds in all masters of ⚠️ all open fonts",
		)
	masterOptions = (
		"On currently selected master only", 
		"On all masters",
		)
	
	def __init__(self):
		x,y,p = self.padding
		
		self.w = vl.FloatingWindow((370, self.windowHeight), "Decompose Backgrounds")
		
		### Description text
		self.w.descriptionText = vl.TextBox( (x, y, -p, self.textHeight), "Decompose components in glyph backgrounds:", sizeStyle='small', selectable=True )
		y += self.textHeight + p
		
		### Option to backup glyphs in the background before decomposition
		self.w.copyToBackgroundFirst = vl.CheckBox((x+3, y, -p, self.textHeight), "Create backups in background first", sizeStyle=self.sizeStyle, callback=self.SavePreferences)
		self.w.copyToBackgroundFirst.getNSButton().setToolTip_("If selected, will copy current foregrounds into backgrounds, overwriting existing background content.")
		y += self.textHeight
		
		### Divider
		self.w.div_copyToBackgroundFirst = vl.HorizontalLine((x, y, -p, self.textHeight))
		y += self.textHeight
		
		### Which glyphs in which fonts
		self.w.whichGlyphsInWhichFonts = vl.RadioGroup(
			(x, y, -p, self.buttonHeight * len(self.glyphsOptions)),
			self.glyphsOptions, sizeStyle=self.sizeStyle , callback=self.glyphsOptionsCallback)
		
		self.w.whichGlyphsInWhichFonts.getNSMatrix().setToolTip_("Which glyphs are affected in which fonts.\n\n⚠️ Careful with the bigger scopes: they affect many glyph backgrounds in one click. Consider saving your .glyphs file first (so you can revert in the worst case).")
		y += self.buttonHeight * len(self.glyphsOptions)
		
		### Divider
		self.w.div_glyphsOptions = vl.HorizontalLine((x, y, -p, self.textHeight))
		y += self.textHeight

		### Which masters
		self.w.whichMasters = vl.RadioGroup(
			(x, y, -p, self.buttonHeight * len(self.masterOptions)),
			self.masterOptions,
			sizeStyle=self.sizeStyle,
			callback=self.SavePreferences,
			)
		self.w.whichMasters.getNSMatrix().setToolTip_("Choose which font masters shall be affected.")

		y += self.buttonHeight * len(self.masterOptions) 
		
		### Action button
		self.w.decomposeButton = vl.Button(
				(-p-120, -self.buttonHeight-p, -p, self.buttonHeight), 
				"Decompose",
				sizeStyle="regular",
				callback=self.decomposeButtonCallback
			)
		
		self.w.setDefaultButton( self.w.decomposeButton )

		if not self.LoadPreferences():
			print("Note: 'Decompose Backgrounds' could not load preferences. Will resort to defaults")
		
		self.w.open()
		self.w.makeKey()

	def glyphsOptionsCallback(self, sender):
		allFontsSelected = sender.get()==2
		self.w.whichMasters.enable(not allFontsSelected)
		self.SavePreferences()
		
	def decomposeButtonCallback(self, sender):
		# collect user settings:
		copyToBackgroundFirst = bool(Glyphs.defaults[self.key+"copyToBackgroundFirst"])
		workOnAllFonts = Glyphs.defaults[self.key+"whichGlyphsInWhichFonts"] == 2
		workOnAllGlyphs = workOnAllFonts or Glyphs.defaults[self.key+"whichMasters"] != 0
		
		# determine affected fonts
		if workOnAllFonts:
			selectedFonts = Glyphs.fonts
		else:
			selectedFonts = (Glyphs.font,)
		
		for thisFont in selectedFonts:
			# determine affected glyphs
			if workOnAllGlyphs:
				selectedGlyphs = thisFont.glyphs
			else:
				selectedGlyphs = [thisLayer.parent for thisLayer in thisFont.selectedLayers]

			# determine affected masters
			workOnAllMasters = workOnAllFonts or self.w.whichMasters.get() == 1
			if workOnAllMasters:
				selectedMasterIDs = [master.id for master in thisFont.masters]
			else:
				selectedMasterIDs = thisFont.selectedFontMaster.id

			thisFont.disableUpdateInterface() # suppresses UI updates in Font View
			try:
				for thisGlyph in selectedGlyphs:
					####print("Processing", thisGlyph.name)
					thisGlyph.beginUndo() # begin undo grouping
					for thisLayer in thisGlyph.layers:
						if thisLayer is not None and (thisLayer.isMasterLayer or thisLayer.isSpecialLayer) and thisLayer.associatedMasterId in selectedMasterIDs:
							self.process( thisLayer, copyToBackgroundFirst=copyToBackgroundFirst )
					thisGlyph.endUndo()   # end undo grouping

			except Exception as e:
				Glyphs.showMacroWindow()
				print("\n⚠️ Script Error:\n")
				import traceback
				print(traceback.format_exc())
				print("\n%s"%e)
				# raise e
				
			finally:
				thisFont.enableUpdateInterface() # re-enables UI updates in Font View
	
	def process( self, thisLayer, copyToBackgroundFirst=False ):
		# Determine foreground and background:
		if thisLayer.isKindOfClass_(GSBackgroundLayer):
			background = thisLayer
			foreground = thisLayer.foreground()
		else:
			background = thisLayer.background
			foreground = thisLayer
		
		# make backup if user asked for it:
		if copyToBackgroundFirst:
			thisLayer.contentToBackgroundCheckSelection_keepOldBackground_(False,False)
		
		# decompose background:
		if background and background.components:			
			compCount = len(background.components)
			print("🔠 %s: decomposed %i component%s in background." % (
				foreground.parent.name,
				compCount,
				"" if compCount==1 else "s",
				))
			background.decomposeComponents()	

	def SavePreferences( self, sender=None ):
		try:
			Glyphs.defaults[self.key+"copyToBackgroundFirst"] = self.w.copyToBackgroundFirst.get()
			Glyphs.defaults[self.key+"whichMasters"] = self.w.whichMasters.get()
			Glyphs.defaults[self.key+"whichGlyphsInWhichFonts"] = self.w.whichGlyphsInWhichFonts.get()
		except:
			return False
			
		return True

	def LoadPreferences( self, sender=None ):
		try:
			Glyphs.registerDefault(self.key+"copyToBackgroundFirst", "0")
			self.w.copyToBackgroundFirst.set( Glyphs.defaults[self.key+"copyToBackgroundFirst"] )

			Glyphs.registerDefault(self.key+"whichMasters", "0")
			self.w.whichMasters.set( Glyphs.defaults[self.key+"whichMasters"] )

			Glyphs.registerDefault(self.key+"whichGlyphsInWhichFonts", "0")
			self.w.whichGlyphsInWhichFonts.set( Glyphs.defaults[self.key+"whichGlyphsInWhichFonts"] )
		except:
			return False
		
		return True

def run():
	Decompose_Components_in_Background()

run()