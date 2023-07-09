#MenuTitle: Tabular Figure Maker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Takes existing .tf figures and spaces them tabularly, or creates them from existing default figures.
"""

import vanilla, sys

class TabularFigureSpacer(object):
	prefID = "com.mekkablue.TabularFigureSpacer"
	prefDict = {
		# "prefName": defaultValue,
		"target": "one.tf",
		"suffix": ".tf",
		"createFromDefaultFigs": False,
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 270
		windowHeight = 160
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Tabular Figure Spacer", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos+2, -inset, 14), "Fit default figures in tabular spaces:", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		self.w.targetText = vanilla.TextBox((inset, linePos+2, -inset, 14), "Reference glyph:", sizeStyle="small", selectable=True)
		self.w.target = vanilla.ComboBox((inset+95, linePos-1, -inset-25, 19), [], sizeStyle="small", callback=self.SavePreferences)
		self.w.updateButton = vanilla.SquareButton((-inset-20, linePos, -inset, 18), "↺", sizeStyle="small", callback=self.update)
		linePos += lineHeight
		
		self.w.suffixText = vanilla.TextBox((inset, linePos+2, -inset, 14), "Tabular suffix:", sizeStyle="small", selectable=True)
		self.w.suffix = vanilla.EditText((inset+95, linePos, -inset, 19), ".tf", callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.createFromDefaultFigs = vanilla.CheckBox((inset, linePos-1, -inset, 20), "⚠️ Create tab figures with default figures", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Tab", sizeStyle="regular", callback=self.TabularFigureSpacerMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Tabular Figure Spacer’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.update()
		self.w.open()
		self.w.makeKey()
	
	def update(self, sender=None):
		self.w.target.setItems([g.name for g in Glyphs.font.glyphs if ".tf" in g.name or ".tosf" in g.name])
		
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

	def TabularFigureSpacerMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Tabular Figure Spacer’ could not write preferences.")
			
			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(sys.modules[__name__], prefName, self.pref(prefName))
				except:
					fallbackValue = self.prefDict[prefName]
					print(f"⚠️ Could not set pref ‘{prefName}’, resorting to default value: ‘{fallbackValue}’.")
					setattr(sys.modules[__name__], prefName, fallbackValue)
			
			font = Glyphs.font # frontmost font
			if font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = font.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{font}\n⚠️ The font file has not been saved yet."
				print(f"Tabular Figure Spacer Report for {reportName}")
				print()
				
				if createFromDefaultFigs:
					figs = "0123456789"
					for fig in figs:
						niceName = Glyphs.niceGlyphName(fig)
						figName = f"{niceName}.{suffix.lstrip('.')}"
						if figName != target:
							newGlyph = GSGlyph(figName)
							font.glyphs.append(newGlyph)
							for layer in newGlyph.layers:
								layer.shapes.append(GSComponent(niceName))
				
				targetGlyph = font.glyphs[target]
				tabFigs = [g for g in font.glyphs if g.name.endswith(suffix)]
				for glyph in tabFigs:
					if targetGlyph and targetGlyph != glyph:
						for master in font.masters:
							mID = master.id
							targetLayer = targetGlyph.layers[mID]
							layer = glyph.layers[mID]
							for thisComponent in layer.components:
								thisComponent.setDisableAlignment_(True)
							widthDiff = targetLayer.width - layer.width
							leftPercentage = layer.LSB / (layer.LSB + layer.RSB)
							layer.LSB += round(widthDiff * leftPercentage)
							layer.width = targetLayer.width
						glyph.widthMetricsKey = f"={target}"

				names = [g.name for g in tabFigs]
				font.newTab("/"+"/".join(names))
	
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Tabular Figure Spacer Error: {e}")
			import traceback
			print(traceback.format_exc())

TabularFigureSpacer()