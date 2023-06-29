#MenuTitle: Merge CPAL Layers into Master Layer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Takes all CPAL/COLR layers and puts copies of their shapes into the master layer.
"""

import vanilla, sys

allOptions = (
	"selected CPAL/COLR glyphs in current font",
	"⚠️ ALL CPAL/COLR glyphs in current font",
	"⚠️ ALL CPAL/COLR glyphs in ⚠️ ALL fonts",
)

class MergeCPALLayersIntoMasterLayer(object):
	prefID = "com.mekkablue.MergeCPALLayersIntoMasterLayer"
	prefDict = {
		# "prefName": defaultValue,
		"overwrite": 1,
		"all": 0,
		"verbose": 0,
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 320
		windowHeight = 155
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Merge CPAL Layers into Master Layer", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos+2, -inset, 14), "Merge CPAL/COLR shapes into master layers", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		self.w.allText = vanilla.TextBox((inset, linePos+2, 30, 14), "for:", sizeStyle="small", selectable=True)
		self.w.all = vanilla.PopUpButton((inset+30, linePos, -inset, 17), allOptions, sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight
		
		self.w.overwrite = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Overwrite existing master layers", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.verbose = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Verbose reporting in Macro window", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button((-90-inset, -20-inset, -inset, -inset), "Merge", sizeStyle="regular", callback=self.MergeCPALLayersIntoMasterLayerMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Merge CPAL Layers into Master Layer’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				getattr(self.w, prefName).set(self.pref(prefName))
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def MergeCPALLayersIntoMasterLayerMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Merge CPAL Layers into Master Layer’ could not write preferences.")
			
			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(sys.modules[__name__], prefName, self.pref(prefName))
				except:
					fallbackValue = self.prefDict[prefName]
					print(f"⚠️ Could not set pref ‘{prefName}’, resorting to default value: ‘{fallbackValue}’.")
					setattr(sys.modules[__name__], prefName, fallbackValue)
			
			if not Glyphs.font:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				countGlyphs = 0
				if all > 1:
					theseFonts = Glyphs.fonts
				else:
					theseFonts = (Glyphs.font,)
			
				for thisFont in theseFonts:
					filePath = thisFont.filepath
					if filePath:
						reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
					else:
						reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
					print(f"Merge CPAL Layers into Master Layer Report for {reportName}")
					print()
				
					if all==0:
						theseGlyphs = [l.parent for l in thisFont.selectedLayers]
					else:
						theseGlyphs = thisFont.glyphs
					
					for thisGlyph in theseGlyphs:
						for m in thisFont.masters:
							masterLayer = thisGlyph.layers[m.id]
							collectedShapes = []
							for colorLayer in thisGlyph.layers:
								if colorLayer.isSpecialLayer and colorLayer.attributeForKey_("colorPalette")!=None:
									for shape in colorLayer.shapes:
										collectedShapes.append(shape.copy())
							if collectedShapes:
								if overwrite:
									masterLayer.shapes = None
								for shape in collectedShapes:
									masterLayer.shapes.append(shape)
								print(f"🌈 {thisGlyph.name}: merged color shapes into Ⓜ️ {m.name}")
								countGlyphs += 1
							elif verbose:
								print(f"🚫 {thisGlyph.name} Ⓜ️ {m.name}: no color layers, skipping.")
					print()
	
				print(f"✅ Done. Merged {countGlyphs} glyph{'' if countGlyphs==1 else 's'} in {len(theseFonts)} font{'' if len(theseFonts)==1 else 's'}.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Merge CPAL Layers into Master Layer Error: {e}")
			import traceback
			print(traceback.format_exc())

MergeCPALLayersIntoMasterLayer()