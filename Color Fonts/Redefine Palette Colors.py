#MenuTitle: Redefine Palette Colors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Reassign palette colors (in CPAL/COLR fonts).
"""

from mekkablue import mekkaObject, UpdateButton
import vanilla, sys

class RedefinePaletteColors(mekkaObject):
	prefID = "com.mekkablue.RedefinePaletteColors"
	prefDict = {
		# "prefName": defaultValue,
		"colorSource": 1,
		"colorTarget": 0,
		"allGlyphs": True,
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 215
		windowHeight = 115
		windowWidthResize  = 0 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Redefine Palette Colors", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.text1 = vanilla.TextBox((inset, linePos+2, 55, 14), "Reassign", sizeStyle="small", selectable=True)
		self.w.colorSource = vanilla.ComboBox((inset+55, linePos-1, 40, 19), [], sizeStyle="small", callback=self.SavePreferences)
		self.w.colorSource.setToolTip("The palette index you want to replace. If you click the update button, the combo box will be populated with all palette indexes currently present in the glyphs of the frontmost font.")
		
		self.w.text2 = vanilla.TextBox((inset+101, linePos+2, 15, 14), "→", sizeStyle="small", selectable=True)
		self.w.colorTarget = vanilla.ComboBox((inset+119, linePos-1, 40, 19), [], sizeStyle="small", callback=self.SavePreferences)
		self.w.colorTarget.setToolTip("The palette index you want to convert to. If you click the update button, the combo box will be populated with all palette indexes in the color palette of the current font.")

		self.w.colorUpdate = UpdateButton((-inset-16, linePos-3, -inset, 18), callback=self.update)
		linePos += lineHeight
		
		self.w.allGlyphs = vanilla.CheckBox((inset+5, linePos-1, -inset, 20), "⚠️ Apply to ALL glyphs", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allGlyphs.setToolTip("If unchecked, it will only process selected glyphs.")
		linePos += lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button((inset, -20-inset, -inset, -inset), "Reassign", sizeStyle="regular", callback=self.RedefinePaletteColorsMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Redefine Palette Colors’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def update(self, sender):
		font = Glyphs.font
		if not font:
			return

		parameter = font.customParameters["Color Palettes"]
		if parameter is None:
			Message(
				title="No Palette Found",
				message=f"The frontmost font ({font.familyName}) does not appear to have a Color Palette parameter set up in Font Info → Font → Custom Parameters. Cannot update the UI.",
				OKButton=None,
				)
			return
		paletteIndexes = list(range(len(parameter[0])))
		self.w.colorTarget.setItems(paletteIndexes)
		
		existingIndexes = []
		for g in font.glyphs:
			for l in g.layers:
				paletteIndex = l.attributes["colorPalette"]
				if paletteIndex is not None and paletteIndex not in existingIndexes:
					existingIndexes.append(paletteIndex)
		existingIndexes = sorted(existingIndexes)
		self.w.colorSource.setItems(existingIndexes)


	def RedefinePaletteColorsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Redefine Palette Colors’ could not write preferences.")
			
			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(sys.modules[__name__], prefName, self.pref(prefName))
				except:
					fallbackValue = self.prefDict[prefName]
					print(f"⚠️ Could not set pref ‘{prefName}’, resorting to default value: ‘{fallbackValue}’.")
					setattr(sys.modules[__name__], prefName, fallbackValue)
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Redefine Palette Colors Report for {reportName}")
			
				if self.pref("allGlyphs"):
					glyphs = thisFont.glyphs
				else:
					glyphs = set([l.parent for l in thisFont.selectedLayers if isinstance(l, GSLayer)])
				
				colorSource = int(self.pref("colorSource"))
				colorTarget = int(self.pref("colorTarget"))
				print(f"🎨 Change palette indexes: {colorSource} → {colorTarget}\n")
				
				for g in glyphs:
					print(f"🔡 {g.name}")
					layerCount = 0
					for l in g.layers:
						paletteIndex = l.attributes["colorPalette"]
						if paletteIndex is None:
							continue
						if paletteIndex == colorSource:
							l.attributes["colorPalette"] = colorTarget
							layerCount += 1
					if layerCount:
						print(f"  {layerCount} color layers converted")
				
				self.w.close() # delete if you want window to stay open

			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Redefine Palette Colors Error: {e}")
			import traceback
			print(traceback.format_exc())

RedefinePaletteColors()