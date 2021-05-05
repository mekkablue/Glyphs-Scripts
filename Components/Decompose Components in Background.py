#MenuTitle: Decompose Components in Background
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from GlyphsApp import GSLayer
import vanilla as vl
__doc__="""
Decomposes components in the Background.
"""

warning_text_allfonts_allmasters = u"""❗️⚠️⚠️❗️WARNING ❗️⚠️⚠️❗️

Option "All glyphs in all fonts in all masters" is selected

Which means, that script will affect a lot of things with one click.
Make sure that you want to do it and it is advised to make 
a backup copy of your all opened fonts.

It is also important to make sure that you've opened 
only those fonts that you want to edit with this script.
"""

warning_text_allGlyphs = u"""❗️⚠️❗️WARNING ❗️⚠️❗️

Option "All glyphs" is selected

Which means, that script will affect a lot of things with one click.
Make sure that you want to do it and it is advised to make 
a backup copy of your currently edited font.
"""

class Decompose_Components_in_Background(object):
	key = "com.mekkablue.Decompose_Components_in_Background"
	baseH = 226
	padding = (10,10,10)
	btnH = 20
	txtH = 14
	sizeStyle = 'small'
	glyphsOptions = ["Selected glyphs in current font", u"⚠️All glyphs in current font",u"⚠️⚠️ All glyphs in all fonts in all masters"]
	masterOptions = ["Current master only", "All masters"]
	def __init__(self):
		x,y,p = self.padding
		
		self.w = vl.Window((370, self.baseH), "Decompose Components in Background")
		
		### Master Options
		self.w.glyphsOptionsRadioGroup = vl.RadioGroup(
			(x, y, -p, self.btnH * len(self.glyphsOptions)),
			self.glyphsOptions, sizeStyle=self.sizeStyle , callback=self.glyphsOptionsCallback)
		

		y += self.btnH * len(self.glyphsOptions)
		self.w.div_glyphsOptions = vl.HorizontalLine((x, y, -p, self.txtH))
		y += self.txtH + p 

		### Master Options
		self.w.masterOptionsRadioGroup = vl.RadioGroup(
			(x, y, -p, self.btnH * len(self.masterOptions)),
			self.masterOptions, sizeStyle=self.sizeStyle)

		y += self.btnH * len(self.masterOptions) 
		self.w.div_masterOptions = vl.HorizontalLine((x, y, -p, self.txtH))
		y += self.txtH + p 
		
		### backup glyphs in the background before decomposition
		self.w.storeInBackground = vl.CheckBox((x+3, y, -p, self.txtH), "make background copy of glyphs before decomposition", sizeStyle=self.sizeStyle)
		y += self.txtH
		self.w.div_storeInBackground = vl.HorizontalLine((x, y, -p, self.txtH))
		y += self.txtH + p 
		

		### worning text box
		self.w.warningText = vl.TextBox((x,y,-p,-self.btnH-p-p),"",sizeStyle=self.sizeStyle)

		### action button
		self.w.decomposeButton = vl.Button(
				(x, -self.btnH-p, -p, self.btnH), 
				"Decompose Components in Background",sizeStyle=self.sizeStyle,
				callback=self.decomposeButtonCallback
			)
		y += self.btnH + p
		

		self.w.bind('close', self.closeWindowEvent)
		self.w.open()
		self.LoadPreferences()

	###
	## CALLBACKS
	###
	
	def glyphsOptionsCallback(self, sender):
		enable = True
		warningText = None
		if self.glyphsOptions[sender.get()] == u"⚠️⚠️ All glyphs in all fonts in all masters":
			enable = False
			warningText = warning_text_allfonts_allmasters
		if self.glyphsOptions[sender.get()] == u"⚠️All glyphs in current font":
			warningText = warning_text_allGlyphs
			
		self.w.masterOptionsRadioGroup.enable(enable)
		x,y,w,h = self.w.getPosSize()
		if warningText is not None:
			txth = len(warningText.split("\n")) * self.txtH
			self.w.setPosSize((x,y,w,self.baseH+txth))
			self.w.warningText.set(warningText)
		else:
			self.w.setPosSize((x,y,w,self.baseH))
			self.w.warningText.set("")
		
	def decomposeButtonCallback(self, sender):
		
		# determine affected fonts
		if self.glyphsOptions[self.w.glyphsOptionsRadioGroup.get()] == u"⚠️⚠️ All glyphs in all fonts in all masters":
			selectedFonts = Glyphs.fonts
		else:
			selectedFonts = [Glyphs.font]


		
		for thisFont in selectedFonts:
			# determine affected glyphs
			if self.glyphsOptions[self.w.glyphsOptionsRadioGroup.get()] != "Selected glyphs in current font":
				selectedGlyphs = thisFont.glyphs
			else:
				selectedGlyphs = [thisLayer.parent for thisLayer in thisFont.selectedLayers]

			# determine affected masters
			if self.masterOptions[self.w.masterOptionsRadioGroup.get()] == "All masters":
				selectedMasterIDs = [master.id for master in thisFont.masters]
			else:
				selectedMasterIDs = [Glyphs.font.selectedLayers[0].associatedMasterId]

			thisFont.disableUpdateInterface() # suppresses UI updates in Font View
			try:
				for thisGlyph in selectedGlyphs:
					
					####print("Processing", thisGlyph.name)
					thisGlyph.beginUndo() # begin undo grouping
					for thisMasterID in selectedMasterIDs:
						thisLayer = thisGlyph.layers[thisMasterID]
			
						if thisLayer is not None:
							self.process( thisLayer )
					thisGlyph.endUndo()   # end undo grouping

			except Exception as e:
				Glyphs.showMacroWindow()
				print("\n⚠️ Script Error:\n")
				import traceback
				print(traceback.format_exc())
				print()
				raise e
				
			finally:
				thisFont.enableUpdateInterface() # re-enables UI updates in Font View
	
	def process(self, thisLayer ):
		
		if thisLayer.components:
			if self.w.storeInBackground.get() == 1:
				thisLayer.setBackground_(thisLayer)	
				print("  Storing '%s - %s' foreground in the background." % (thisLayer.name, thisLayer.parent.name))
		background = None
		if thisLayer.isKindOfClass_(GSBackgroundLayer):
			background = thisLayer
		else:
			background = thisLayer.background
		
		if not background:
			print("  Could not access background layer '%s'." % thisLayer.name)
		elif background.components:			
			compCount = len(background.components)
			print("  Decomposed %i component%s in background." % (
				compCount,
				"" if compCount==1 else "s",
				))
			background.decomposeComponents()	

	### preferences handling:
	def SavePreferences( self ):
		try:
			Glyphs.defaults[self.key+"storeInBackground"] = self.w.storeInBackground.get()

			Glyphs.defaults[self.key+"masterOptionsRadioGroup"] = self.w.masterOptionsRadioGroup.get()

			Glyphs.defaults[self.key+"glyphsOptionsRadioGroup"] = self.w.glyphsOptionsRadioGroup.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault(self.key+"storeInBackground", "0")
			self.w.storeInBackground.set( Glyphs.defaults[self.key+"storeInBackground"] )

			Glyphs.registerDefault(self.key+"masterOptionsRadioGroup", "0")
			self.w.masterOptionsRadioGroup.set( Glyphs.defaults[self.key+"masterOptionsRadioGroup"] )

			Glyphs.registerDefault(self.key+"glyphsOptionsRadioGroup", "0")
			self.w.glyphsOptionsRadioGroup.set( Glyphs.defaults[self.key+"glyphsOptionsRadioGroup"] )
		except:
			return False
		
		self.glyphsOptionsCallback(self.w.glyphsOptionsRadioGroup)
		return True
	###
	## EVENTS
	###

	def closeWindowEvent(self, window):
	   self.SavePreferences()
def run():
	Decompose_Components_in_Background()


run()