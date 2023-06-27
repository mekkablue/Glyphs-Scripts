#MenuTitle: Rename Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Takes a list of oldglyphname=newglyphname pairs and renames glyphs in the font accordingly, much like the Rename Glyphs parameter.
"""

import vanilla, uuid
from AppKit import NSFont

class RenameGlyphs(object):
	prefID = "com.mekkablue.RenameGlyphs"
	prefDict = {
		# "prefName": defaultValue,
		"renameList": "oldname=newname",
		"allFonts": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 250
		windowHeight = 200
		windowWidthResize = 800 # user can resize width by this value
		windowHeightResize = 800 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Rename Glyphs", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName="com.mekkablue.RenameGlyphs.mainwindow" # stores last window position and size
			)

		# UI elements:
		self.w.text_1 = vanilla.TextBox((10, 12 + 2, -10, 14), "Add lines like oldname=newname:", sizeStyle='small')
		self.w.renameList = vanilla.TextEditor((1, 40, -1, -40), "oldname=newname", callback=self.SavePreferences)
		self.w.renameList.getNSTextView().setFont_(NSFont.userFixedPitchFontOfSize_(-1.0))
		self.w.renameList.getNSTextView().turnOffLigatures_(1)
		self.w.renameList.getNSTextView().useStandardLigatures_(0)
		self.w.renameList.selectAll()

		self.w.allFonts = vanilla.CheckBox((10, -35, 100, 20), "⚠️ ALL Fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		
		# Run Button:
		self.w.runButton = vanilla.Button((-100, -35, -15, -15), "Rename", sizeStyle='regular', callback=self.RenameGlyphsMain)
		#self.w.setDefaultButton( self.w.runButton )

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Rename Glyphs' could not load preferences. Will resort to defaults")

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

	def RenameGlyphsMain(self, sender):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Rename Glyphs’ could not write preferences.")
			
			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(sys.modules[__name__], prefName, self.pref(prefName))
				except:
					fallbackValue = self.prefDict[prefName]
					print(f"⚠️ Could not set pref ‘{prefName}’, resorting to default value: ‘{fallbackValue}’.")
					setattr(sys.modules[__name__], prefName, fallbackValue)

			if allFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = [Glyphs.font,]
				
			for thisFont in theseFonts:
				for thisLine in renameList.splitlines():
					if thisLine.strip():
						glyphNameLeft = thisLine.split("=")[0].strip()
						glyphNameRight = thisLine.split("=")[1].strip()
						glyphLeft = thisFont.glyphs[glyphNameLeft]
						glyphRight = thisFont.glyphs[glyphNameRight]
						if glyphLeft:
							if glyphRight:
								uniqueSuffix = ".%s" % uuid.uuid4().hex
								glyphLeft.name = glyphNameRight + uniqueSuffix
								glyphRight.name = glyphNameLeft
								glyphLeft.name = glyphNameRight

								# swap export status:
								glyphLeftExport = glyphLeft.export
								glyphLeft.export = glyphRight.export
								glyphRight.export = glyphLeftExport
							else:
								glyphLeft.name = glyphNameRight
						else:
							print(f"Warning: {glyphNameLeft} not in font.")

			if not self.SavePreferences(self):
				print("Note: 'Rename Glyphs' could not write preferences.")

			self.w.close() # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Rename Glyphs Error: {e}")
			import traceback
			print(traceback.format_exc())

RenameGlyphs()
