#MenuTitle: Add Alignment Zones for Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Creates fitting zones for the selected glyphs, on every master.
"""

import vanilla

class CreateAlignmentZonesforSelectedGlyphs( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 290
		windowHeight = 170	
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Alignment Zones for Selected Glyphs", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.CreateAlignmentZonesforSelectedGlyphs.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 8, 12, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, int(lineHeight*1.5)), u"Create alignment zones for selected glyphs. Detailed report in Macro Window.", sizeStyle='small', selectable=True )
		linePos += int(lineHeight*1.7)
		
		self.w.createTopZones = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Create top zones for selected glyphs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.createTopZones.getNSButton().setToolTip_(u"If enabled, will create top zones that match the currently selected glyphs, for every master. The height of the lowest selected glyph will be the zone position, the difference to the highest glyph will be the size of the zone.")
		linePos += lineHeight
		
		self.w.createBottomZones = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Create bottom zones for selected glyphs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.createBottomZones.getNSButton().setToolTip_(u"If enabled, will create bottom zones that match the currently selected glyphs, for every master. The highest bottom edge is the zone position, the difference to the lowest bottom edge will be the zone size.")
		linePos += lineHeight
		
		self.w.dontExceedExistingZones = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Prevent zone sizes bigger than current zones", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.dontExceedExistingZones.getNSButton().setToolTip_(u"Recommended. If enabled, will make sure that no zone will be added that is larger than existing zones in the master.")
		linePos += lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Create Zones", sizeStyle='regular', callback=self.CreateAlignmentZonesforSelectedGlyphsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Create Alignment Zones for Selected Glyphs' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.CreateAlignmentZonesforSelectedGlyphs.createTopZones"] = self.w.createTopZones.get()
			Glyphs.defaults["com.mekkablue.CreateAlignmentZonesforSelectedGlyphs.createBottomZones"] = self.w.createBottomZones.get()
			Glyphs.defaults["com.mekkablue.CreateAlignmentZonesforSelectedGlyphs.dontExceedExistingZones"] = self.w.dontExceedExistingZones.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.CreateAlignmentZonesforSelectedGlyphs.createTopZones", 1)
			Glyphs.registerDefault("com.mekkablue.CreateAlignmentZonesforSelectedGlyphs.createBottomZones", 1)
			Glyphs.registerDefault("com.mekkablue.CreateAlignmentZonesforSelectedGlyphs.dontExceedExistingZones", 1)
			self.w.createTopZones.set( Glyphs.defaults["com.mekkablue.CreateAlignmentZonesforSelectedGlyphs.createTopZones"] )
			self.w.createBottomZones.set( Glyphs.defaults["com.mekkablue.CreateAlignmentZonesforSelectedGlyphs.createBottomZones"] )
			self.w.dontExceedExistingZones.set( Glyphs.defaults["com.mekkablue.CreateAlignmentZonesforSelectedGlyphs.dontExceedExistingZones"] )
		except:
			return False
			
		return True

	def CreateAlignmentZonesforSelectedGlyphsMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Create Alignment Zones for Selected Glyphs' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			print("Create Alignment Zones for Selected Glyphs Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			
			top = Glyphs.defaults["com.mekkablue.CreateAlignmentZonesforSelectedGlyphs.createTopZones"]
			bottom = Glyphs.defaults["com.mekkablue.CreateAlignmentZonesforSelectedGlyphs.createBottomZones"]
			dontExceed = Glyphs.defaults["com.mekkablue.CreateAlignmentZonesforSelectedGlyphs.dontExceedExistingZones"]
			
			selectedGlyphs = [l.parent for in thisFont.selectedLayers]
			
			for i,master in enumerate(thisFont.masters):
				print("\nFont Master %i: %s" % (i+1,master.name))
				largestSize = max([abs(z.size) for z in master.alignmentZones])
				
				if top:
					allHeights = []
					for g in selectedGlyphs:
						l = g.layers[master.id]
						allHeights.append( l.bounds.origin.y+l.bounds.size.height )
	
					minHeight = min(allHeights)
					maxHeight = max(allHeights)
					size = maxHeight-minHeight
					print( "- position: %i, size: %i" % (minHeight, size) )
	
					if not dontExceed or size <= largestSize:
						z = GSAlignmentZone()
						z.size = max(1,size)
						z.position = minHeight
						master.alignmentZones.append(z)
			
				if bottom:
					allDepths = []
					for g in selectedGlyphs:
						l = g.layers[master.id]
						allDepths.append( l.bounds.origin.y )
	
					maxDepth = min(allDepths)
					minDepth = max(allDepths)
					size = maxDepth-minDepth
					print( "- position: %i, size: %i" % (minDepth, size) )
	
					if not dontExceed or abs(size) <= largestSize:
						z = GSAlignmentZone()
						z.size = min(-1,size)
						z.position = minDepth
						master.alignmentZones.append(z)
					
				master.sortAlignmentZones()
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Create Alignment Zones for Selected Glyphs Error: %s" % e)
			import traceback
			print(traceback.format_exc())

CreateAlignmentZonesforSelectedGlyphs()