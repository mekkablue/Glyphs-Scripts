#MenuTitle: New Tabs with Glyphs Not Reaching Into Zones
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Opens a new tab with all glyphs that do NOT reach into any top or bottom alignment zone. Only counts glyphs that contain paths in the current master. Ignores empty glyphs and compounds.
"""

import vanilla

class NewTabsWithGlyphsNotReachingIntoZones( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 175
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"New Tabs with Glyphs Not Reaching Into Zones", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 12, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Open tab with glyphs that are not reaching into zones.", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.allMastersInSeparateTabs = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include All Masters (in Separate Tabs)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.includeSpecialLayers = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include Special Layers", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.ignoreGlyphsText = vanilla.TextBox( (inset, linePos+2, 140, 14), u"Ignore glyphs containing:", sizeStyle='small', selectable=True )
		self.w.ignoreGlyphs = vanilla.EditText( (inset+140, linePos-1, -inset, 19), ".sups, .subs, superior, inferior, Arrow", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.includeText = vanilla.TextBox( (inset, linePos+2, 60, 14), u"Include:", sizeStyle='small', selectable=True )
		self.w.includeMarks = vanilla.CheckBox( (inset+50, linePos-1, -inset, 20), u"Marks", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeSymbols = vanilla.CheckBox( (inset+110, linePos-1, -inset, 20), u"Symbols", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includePunctuation = vanilla.CheckBox( (inset+60*3, linePos-1, -inset, 20), u"Punctuation", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Open Tabs", sizeStyle='regular', callback=self.NewTabsWithGlyphsNotReachingIntoZonesMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'New Tabs with Glyphs Not Reaching Into Zones' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.allMastersInSeparateTabs"] = self.w.allMastersInSeparateTabs.get()
			Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includeSpecialLayers"] = self.w.includeSpecialLayers.get()
			Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.ignoreGlyphs"] = self.w.ignoreGlyphs.get()
			Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includeMarks"] = self.w.includeMarks.get()
			Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includeSymbols"] = self.w.includeSymbols.get()
			Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includePunctuation"] = self.w.includePunctuation.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.allMastersInSeparateTabs", 0)
			Glyphs.registerDefault("com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includeSpecialLayers", 1)
			Glyphs.registerDefault("com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.ignoreGlyphs", ".sups, .subs, superior, inferior, Arrow")
			Glyphs.registerDefault("com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includeMarks", 0)
			Glyphs.registerDefault("com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includeSymbols", 0)
			Glyphs.registerDefault("com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includePunctuation", 0)
			self.w.allMastersInSeparateTabs.set( Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.allMastersInSeparateTabs"] )
			self.w.includeSpecialLayers.set( Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includeSpecialLayers"] )
			self.w.ignoreGlyphs.set( Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.ignoreGlyphs"] )
			self.w.includeMarks.set( Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includeMarks"] )
			self.w.includeSymbols.set( Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includeSymbols"] )
			self.w.includePunctuation.set( Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includePunctuation"] )
		except:
			return False
			
		return True

	def NewTabsWithGlyphsNotReachingIntoZonesMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'New Tabs with Glyphs Not Reaching Into Zones' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			print("New Tabs with Glyphs Not Reaching Into Zones Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			
			allMastersInSeparateTabs = Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.allMastersInSeparateTabs"]
			includeSpecialLayers = Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includeSpecialLayers"]
			ignoreGlyphs = Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.ignoreGlyphs"]
			includeMarks = Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includeMarks"]
			includeSymbols = Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includeSymbols"]
			includePunctuation = Glyphs.defaults["com.mekkablue.NewTabsWithGlyphsNotReachingIntoZones.includePunctuation"]
			
			if allMastersInSeparateTabs:
				masters = thisFont.masters
			else:
				masters = (thisFont.selectedFontMaster,)
			
			for thisFontMaster in masters:
				bottomZones = sorted( [z for z in thisFontMaster.alignmentZones if z.size < 0.0], key = lambda thisZone: -thisZone.position )
				topZones    = sorted( [z for z in thisFontMaster.alignmentZones if z.size > 0.0], key = lambda thisZone: thisZone.position )
				exportingGlyphs = [g for g in thisFont.glyphs if g.export and len(g.layers[thisFontMaster.id].paths)>0 ]
				
				# opens new Edit tab:
				masterTab = thisFont.newTab()
				
				# set the master for the tab:
				i = -1
				for i,m in enumerate(thisFont.masters):
					if m is thisFontMaster:
						mIndex = i
				if i >= 0:
					masterTab.masterIndex = mIndex
				
				masterTab.text += "Master: %s" % thisFontMaster.name

				for zoneGroupInfo in ( (bottomZones,False), (topZones, True) ):
					zones = zoneGroupInfo[0]
					isTopZone = zoneGroupInfo[1]
					if isTopZone:
						zoneType = "top"
					else:
						zoneType = "bottom"
					
					# parse exrta text in tab as layers because otherwise 
					# previously inserted layers would be converted to mere tabtext
					# and special layers would get lost:
					extraTabText = "\n\nNo %s zone:\n" % zoneType
					for char in extraTabText:
						if char == "\n":
							masterTab.layers.append( GSControlLayer.newline() )
						else:
							glyphName = Glyphs.niceGlyphName(char)
							if glyphName and thisFont.glyphs[glyphName]:
								layer = thisFont.glyphs[glyphName].layers[thisFontMaster.id]
								if layer:
									masterTab.layers.append( layer )
					

					for thisGlyph in exportingGlyphs:
						passMarksTest = includeMarks or thisGlyph.category != "Mark"
						passSymbolsTest = includeSymbols or thisGlyph.category != "Symbol"
						passPunctuationTest = includePunctuation or thisGlyph.category != "Punctuation"
						passNameTest = True
						for namePart in [n.strip() for n in ignoreGlyphs.split(",")]:
							if namePart in thisGlyph.name:
								passNameTest = False
					
						if passMarksTest and passSymbolsTest and passPunctuationTest and passNameTest:
							if includeSpecialLayers:
								theseLayers = [l for l in thisGlyph.layers if (l.isSpecialLayer or l.isMasterLayer) and l.associatedMasterId==thisFontMaster.id]
							else:
								theseLayers = (thisGlyph.layers[thisFontMaster.id],)
							
							for thisLayer in theseLayers:
								
								# exclude diacritic compounds:
								isDiacriticCompound = (
									thisGlyph.category == "Letter"
									and len(thisLayer.paths)==0
									and len(thisLayer.components)>0 
									# and thisLayer.components[0].component.category=="Letter"
								)
			
								if thisLayer.bounds.size.height and not isDiacriticCompound:
									doesNotReachZone = True
									if isTopZone:
										topEdge = thisLayer.bounds.origin.y + thisLayer.bounds.size.height
										for thisZone in zones:
											if topEdge >= thisZone.position and topEdge <= (thisZone.position+thisZone.size):
												doesNotReachZone = False
									else:
										bottomEdge = thisLayer.bounds.origin.y
										for thisZone in zones:
											if bottomEdge <= thisZone.position and bottomEdge >= (thisZone.position+thisZone.size):
												doesNotReachZone = False
									if doesNotReachZone:
										masterTab.layers.append(thisLayer) # += "/%s" % thisGlyph.name
			
			self.w.close() # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("New Tabs with Glyphs Not Reaching Into Zones Error: %s" % e)
			import traceback
			print(traceback.format_exc())

NewTabsWithGlyphsNotReachingIntoZones()