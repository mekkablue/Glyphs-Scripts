#MenuTitle: Offset Pixel Rows
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Offsets each row of pixels by a percentage. Rhythm of 2 = every other line offset by half of a pixel’s width; rhythm of 3 = every second line by a third, every third line by two thirds; and so on. Useful for offsetting hexagon-shaped pixels, etc.
"""

import vanilla, sys
from mekkablue import mekkaObject, UpdateButton, match


class OffsetPixelRows(mekkaObject):
	prefID = "com.mekkablue.OffsetPixelRows"
	prefDict = {
		# "prefName": defaultValue,
		"allMasters": True,
		"allGlyphs": False,
		"pixelWidth": 100,
		"pixelName": "*pix*",
		"rhythm": 2,
		"shouldResetGrid": True,
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 230
		windowHeight = 200
		windowWidthResize  = 0 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Offset Pixel Rows", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight, tab = 12, 15, 22, 72
		self.w.rhythmText = vanilla.TextBox((inset, linePos+2, tab, 14), "Line rhythm", sizeStyle="small", selectable=True)
		self.w.rhythm = vanilla.EditText((inset+tab, linePos, -inset, 19), "2", callback=self.SavePreferences, sizeStyle="small")
		self.w.rhythm.getNSTextField().setToolTip_("Will increasingly offset every n lines, first line not at all, each following line by 1/n pixel more. Use negative number for moving to the left.")
		linePos += lineHeight
		
		self.w.pixelNameText = vanilla.TextBox((inset, linePos+2, tab, 14), "Pixel name", sizeStyle="small", selectable=True)
		self.w.pixelName = vanilla.EditText((inset+tab, linePos, -inset, 19), "*pix*", callback=self.SavePreferences, sizeStyle="small")
		self.w.pixelName.getNSTextField().setToolTip_("Only components matching this name will be moved. You can use ? and * as wildcards. Leave empty for all components.")
		linePos += lineHeight
		
		self.w.pixelWidthText = vanilla.TextBox((inset, linePos+2, tab, 14), "Pixel width", sizeStyle="small", selectable=True)
		self.w.pixelWidth = vanilla.EditText((inset+tab, linePos, -inset-15, 19), "100", callback=self.SavePreferences, sizeStyle="small")
		self.w.pixelWidthUpdate = UpdateButton((-inset-12, linePos-2, -inset+6, 18), callback=self.updateUI)
		self.w.pixelWidth.getNSTextField().setToolTip_("Pixel size. All offsets are calculated based on this")
		linePos += lineHeight
		
		self.w.allGlyphs = vanilla.CheckBox((inset, linePos-1, -inset, 20), "All glyphs (ignore selection)", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.allMasters = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Include all masters", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.shouldResetGrid = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Reset grid to pixel width ÷ rhythm", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Offset", sizeStyle="regular", callback=self.OffsetPixelRowsMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Offset Pixel Rows’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()


	def updateUI(self, sender=None):
		font = Glyphs.font
		if not font:
			return

		if sender is self.w.pixelWidthUpdate:
			self.setPref("pixelWidth", int(font.gridLength))
			self.LoadPreferences()


	def OffsetPixelRowsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Offset Pixel Rows’ could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Offset Pixel Rows Report for {reportName}")
				print()
			
				allMasters = self.pref("allMasters")
				allGlyphs = self.pref("allGlyphs")
				pixelWidth = int(self.pref("pixelWidth"))
				pixelName = self.pref("pixelName")
				rhythm = int(self.pref("rhythm"))
				shouldResetGrid = self.pref("shouldResetGrid")
				currentMasterID = thisFont.selectedFontMaster.id

				if shouldResetGrid:
					thisFont.grid = abs(int(pixelWidth))
					thisFont.gridSubDivisions = abs(int(rhythm))
					
				if allGlyphs:
					glyphs = thisFont.glyphs
				else:
					glyphs = [l.parent for l in thisFont.selectedLayers]

				for glyph in glyphs:
					print(f"🔤 {glyph.name}")
					for layer in glyph.layers:
						if not layer.components:
							continue

						if not layer.isMasterLayer or layer.isSpecialLayer:
							continue

						if not (allMasters or layer.associatedMasterId == currentMasterID):
							continue

						for component in layer.components:
							if pixelName and not match(pixelName, component.componentName):
								continue

							verticalPosition = component.y
							offsetFactor = int(verticalPosition/pixelWidth) % rhythm
							if offsetFactor:
								component.x += (rhythm/abs(rhythm)) * offsetFactor * pixelWidth / rhythm

				if thisFont.currentTab:
					thisFont.currentTab.redraw()
				else:
					thisFont.fontView.redraw()
	
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Offset Pixel Rows Error: {e}")
			import traceback
			print(traceback.format_exc())

OffsetPixelRows()