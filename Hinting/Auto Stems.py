#MenuTitle: Auto Stems
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Derive one H and one V stem value for all your masters by measuring certain shapes in your font.
"""

import vanilla, sys
from AppKit import NSPoint

whichMeasure = (
	"bounds",
	"diameter",
	)

whichShape = (
	"first shape",
	"smallest shape",
	"largest shape",
	)

class AutoStems(object):
	prefID = "com.mekkablue.AutoStems"
	prefDict = {
		# "prefName": defaultValue,
		"hMeasure": 0,
		"hShape": 1,
		"hStemGlyph": "f",
		"vMeasure": 1,
		"vShape": 0,
		"vStemGlyph": "idotaccent",
		"overwriteExisting": 1,
		"allFonts": 0,
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 420
		windowHeight = 160
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Auto Stems", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Measure shapes in the font and derive stem entries:", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		self.w.hText1 = vanilla.TextBox((inset, linePos+2, 48, 14), "H Stem:", sizeStyle="small", selectable=True)
		self.w.hMeasure = vanilla.PopUpButton((inset+48, linePos, 82, 17), whichMeasure, sizeStyle="small", callback=self.SavePreferences)
		self.w.hText2 = vanilla.TextBox((inset+133, linePos+2, 17, 14), "of", sizeStyle="small", selectable=True)
		self.w.hShape = vanilla.PopUpButton((inset+150, linePos, 110, 17), whichShape, sizeStyle="small", callback=self.SavePreferences)
		self.w.hText3 = vanilla.TextBox((inset+263, linePos+2, 17, 14), "of", sizeStyle="small", selectable=True)
		self.w.hStemGlyph = vanilla.ComboBox((inset+280, linePos-1, -inset-25, 19), [g.name for g in Glyphs.font.glyphs], sizeStyle="small", callback=self.SavePreferences)
		self.w.hReset = vanilla.SquareButton((-inset-20, linePos, -inset, 18), "↺", sizeStyle="small", callback=self.update)
		linePos += lineHeight
		
		self.w.vText1 = vanilla.TextBox((inset, linePos+2, 48, 14), "V Stem:", sizeStyle="small", selectable=True)
		self.w.vMeasure = vanilla.PopUpButton((inset+48, linePos, 82, 17), whichMeasure, sizeStyle="small", callback=self.SavePreferences)
		self.w.vText2 = vanilla.TextBox((inset+133, linePos+2, 17, 14), "of", sizeStyle="small", selectable=True)
		self.w.vShape = vanilla.PopUpButton((inset+150, linePos, 110, 17), whichShape, sizeStyle="small", callback=self.SavePreferences)
		self.w.vText3 = vanilla.TextBox((inset+263, linePos+2, 17, 14), "of", sizeStyle="small", selectable=True)
		self.w.vStemGlyph = vanilla.ComboBox((inset+280, linePos-1, -inset-25, 19), [g.name for g in Glyphs.font.glyphs], sizeStyle="small", callback=self.SavePreferences)
		self.w.vReset = vanilla.SquareButton((-inset-20, linePos, -inset, 18), "↺", sizeStyle="small", callback=self.update)
		linePos += lineHeight
		
		self.w.overwriteExisting = vanilla.CheckBox((inset, linePos-1, -inset, 20), "⚠️ Overwrite existing stems", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.allFonts = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Process ⚠️ ALL open fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button((-120-inset, -20-inset, -inset, -inset), "Add Stems", sizeStyle="regular", callback=self.AutoStemsMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Auto Stems’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def update(self, sender=None):
		if sender in (self.w.hReset, self.w.vReset):
			sender.setItems([g.name for g in Glyphs.font.glyphs])
		
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

	def LoadPreferences(self):
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

	def measureLayer(self, layer, measure, shape, v=True):
		l = layer.copyDecomposedLayer()
		l.parent = layer.parent
		
		if shape==0: # first
			s = l.shapes[0]
		elif shape==1: # smallest
			s = sorted(l.shapes, key=lambda thisShape: thisShape.bounds.size.height * thisShape.bounds.size.width)[0]
		elif shape==2: # largest
			s = sorted(l.shapes, key=lambda thisShape: thisShape.bounds.size.height * thisShape.bounds.size.width * -1)[0]

		# reduce layer to just the shape we want to measure
		# l.setShapes_([s])
		for i in range(len(l.shapes)-1,-1,-1):
			if l.shapes[i] != s:
				del l.shapes[i]

		if v:
			if measure==0: # bounds
				return l.bounds.size.width
			elif measure==1: # diameter 
				midY = l.bounds.origin.y + 0.5 * l.bounds.size.height
				x1 = l.bounds.origin.x - 50
				x2 = l.bounds.origin.x + l.bounds.size.width + 50
				cuts = l.intersectionsBetweenPoints(
					NSPoint(x1, midY), 
					NSPoint(x2, midY), 
					components=True)
				stemMeasurement = float(round(cuts[-2].x-cuts[1].x))
				return abs(stemMeasurement)
		else: # h
			if measure==0: # bounds
				return l.bounds.size.height
			elif measure==1: # diameter
				midX = l.bounds.origin.x + 0.5 * l.bounds.size.width
				y1 = l.bounds.origin.y - 50
				y2 = l.bounds.origin.y + l.bounds.size.height + 50
				cuts = l.intersectionsBetweenPoints(
					NSPoint(midX, y1), 
					NSPoint(midX, y2), 
					components=True)
				stemMeasurement = float(round(cuts[-1].y-cuts[1].y))
				return abs(stemMeasurement)

	def AutoStemsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Auto Stems’ could not write preferences.")

			# read prefs:
			hMeasure = self.pref("hMeasure")
			hShape = self.pref("hShape")
			hStemGlyph = self.pref("hStemGlyph")
			vMeasure = self.pref("vMeasure")
			vShape = self.pref("vShape")
			vStemGlyph = self.pref("vStemGlyph")
			overwriteExisting = self.pref("overwriteExisting")
			allFonts = self.pref("allFonts")

			if allFonts:
				fonts = Glyphs.fonts
			else:
				fonts = (Glyphs.font,)

			if not fonts:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			for f in fonts:
				filePath = f.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{f.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Auto Stems Report for {reportName}")
				print()

				if overwriteExisting:
					f.setStems_(())

				stem = GSMetric()
				stem.name = "V"
				stem.horizontal = False
				stem.type = 0
				f.stems.append(stem)
				vID = stem.id

				stem = GSMetric()
				stem.name = "H"
				stem.horizontal = True
				stem.type = 0
				f.stems.append(stem)
				hID = stem.id

				vGlyph = f.glyphs[vStemGlyph] # idotless
				hGlyph = f.glyphs[hStemGlyph] # f
				
				for m in f.masters:
					mID = m.id

					# measure idotless
					vStem = self.measureLayer(vGlyph.layers[m.id], vMeasure, vShape, v=True)

					# measure f
					hStem = self.measureLayer(hGlyph.layers[m.id], hMeasure, hShape, v=False)

					# set stems:
					print(f"V {vStem} H {hStem}: {m.name}")
					vInfo = GSInfoValue.alloc().initWithValue_(vStem)
					hInfo = GSInfoValue.alloc().initWithValue_(hStem)
					m.setStemValue_forId_(vInfo, vID)
					m.setStemValue_forId_(hInfo, hID)

				print()

			self.w.close() # delete if you want window to stay open
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Auto Stems Error: {e}")
			import traceback
			print(traceback.format_exc())

AutoStems()