#MenuTitle: New Tab with Transformed Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Opens a new edit tab with components that are rotated, scaled or flipped, i.e., any transformation beyond mere shifts.
"""

import vanilla

def containsTransformedComponents( thisGlyph ):
	for thisLayer in thisGlyph.layers:
		for thisComponent in thisLayer.components:
			if thisComponent.transform[:4] != (1.0,0.0,0.0,1.0):
				return True
	return False

def hasScaledComponents(thisLayer, unproportional=False):
	for thisComponent in thisLayer.components:
		if thisComponent.rotation == 0.0:
			hScale, vScale = thisComponent.scale
			scaled = (hScale*vScale > 0.0) and (abs(hScale)!=1.0 or abs(vScale)!=1.0)
			if scaled:
				if unproportional:
					unproportionallyScaled = abs(hScale) != abs(vScale)
					if unproportionallyScaled:
						return True
				else:
					return True
	return False
	
def hasRotatedComponents(thisLayer):
	for thisComponent in thisLayer.components:
		if thisComponent.rotation:
			return True
	return False

def hasMirroredComponents(thisLayer):
	for thisComponent in thisLayer.components:
		hScale, vScale = thisComponent.scale
		if hScale * vScale < 0:
			return True
	return False
	
def hasMerelyShiftedComponents(thisLayer):
	for thisComponent in thisLayer.components:
		hScale, vScale = thisComponent.scale
		degrees = thisComponent.rotation
		if hScale==1.0 and vScale==1.0 and degrees == 0.0:
			x, y = thisComponent.position
			if x!=0 or y!=0:
				return True
	return False

class NewTabWithTransformedComponents( object ):
	prefID = "com.mekkablue.NewTabWithTransformedComponents"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 280
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"New Tab with Transformed Components", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Finds and displays components that are transformed:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.findScaled = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Find scaled components", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.findUnproportionallyScaled = vanilla.CheckBox( (inset*2, linePos-1, -inset, 20), u"Only unproportionally scaled (h≠v)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.findRotated = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Find rotated components", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight

		self.w.findMirrored = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Find flipped components", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.findShifted = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Find shifted (otherwise untransformed) components", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.includeNonexporting = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.includeInactiveLayers = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include inactive backup layers", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.showAllLayers = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Show all affected layers (otherwise just glyphs)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.reuseTab = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-110-inset, -20-inset, -inset, -inset), "Open Tab", sizeStyle='regular', callback=self.NewTabWithTransformedComponentsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'New Tab with Transformed Components' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		self.updateUI()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def updateUI(self, sender=None):
		self.w.findUnproportionallyScaled.enable( self.w.findScaled.get() )
		self.w.runButton.enable(
			self.w.findScaled.get() or
			self.w.findRotated.get() or
			self.w.findMirrored.get() or
			self.w.findShifted.get()
		)
		
		
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults[self.domain("findScaled")] = self.w.findScaled.get()
			Glyphs.defaults[self.domain("findUnproportionallyScaled")] = self.w.findUnproportionallyScaled.get()
			Glyphs.defaults[self.domain("findRotated")] = self.w.findRotated.get()
			Glyphs.defaults[self.domain("findMirrored")] = self.w.findMirrored.get()
			Glyphs.defaults[self.domain("findShifted")] = self.w.findShifted.get()
			Glyphs.defaults[self.domain("includeNonexporting")] = self.w.includeNonexporting.get()
			Glyphs.defaults[self.domain("includeInactiveLayers")] = self.w.includeInactiveLayers.get()
			Glyphs.defaults[self.domain("reuseTab")] = self.w.reuseTab.get()
			Glyphs.defaults[self.domain("showAllLayers")] = self.w.showAllLayers.get()
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault(self.domain("findScaled"), 1)
			Glyphs.registerDefault(self.domain("findUnproportionallyScaled"), 1)
			Glyphs.registerDefault(self.domain("findRotated"), 0)
			Glyphs.registerDefault(self.domain("findMirrored"), 0)
			Glyphs.registerDefault(self.domain("findShifted"), 0)
			Glyphs.registerDefault(self.domain("includeNonexporting"), 0)
			Glyphs.registerDefault(self.domain("includeInactiveLayers"), 0)
			Glyphs.registerDefault(self.domain("reuseTab"), 1)
			Glyphs.registerDefault(self.domain("showAllLayers"), 0)
			
			# load previously written prefs:
			self.w.findScaled.set( self.pref("findScaled") )
			self.w.findUnproportionallyScaled.set( self.pref("findUnproportionallyScaled") )
			self.w.findRotated.set( self.pref("findRotated") )
			self.w.findMirrored.set( self.pref("findMirrored") )
			self.w.findShifted.set( self.pref("findShifted") )
			self.w.includeNonexporting.set( self.pref("includeNonexporting") )
			self.w.includeInactiveLayers.set( self.pref("includeInactiveLayers") )
			self.w.reuseTab.set( self.pref("reuseTab") )
			self.w.showAllLayers.set( self.pref("showAllLayers") )
			
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def NewTabWithTransformedComponentsMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'New Tab with Transformed Components' could not write preferences.")
			
			findScaled = self.pref("findScaled")
			findUnproportionallyScaled = self.pref("findUnproportionallyScaled")
			findRotated = self.pref("findRotated")
			findMirrored = self.pref("findMirrored")
			findShifted = self.pref("findShifted")
			includeNonexporting = self.pref("includeNonexporting")
			includeInactiveLayers = self.pref("includeInactiveLayers")
			reuseTab = self.pref("reuseTab")
			showAllLayers = self.pref("showAllLayers")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton="Oooops")
			else:
				print("New Tab with Transformed Components Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
				
				layersWithScaledComponents = []
				layersWithRotatedComponents = []
				layersWithMirroredComponents = []
				layersWithShiftedComponents = []
				
				glyphCount = len(thisFont.glyphs)
				affectedGlyphCount = 0
				for i, thisGlyph in enumerate(thisFont.glyphs):
					self.w.progress.set(i/glyphCount*100)
					if thisGlyph.export or includeNonexporting:
						isAffected = False
						for thisLayer in thisGlyph.layers:
							if thisLayer.components:
								if Glyphs.versionNumber >= 3:
									layerCheck = thisLayer.isMasterLayer or thisLayer.isSpecialLayer or thisLayer.isAnyColorLayer() or includeInactiveLayers
								else: 
									layerCheck = thisLayer.isMasterLayer or thisLayer.isSpecialLayer or thisLayer.isColorLayer or includeInactiveLayers
								if layerCheck:
									# scale
									if findScaled and hasScaledComponents(thisLayer, unproportional=findUnproportionallyScaled):
										layersWithScaledComponents.append(thisLayer)
										print("↕️ %s: layer ‘%s’ contains scaled component" % (thisGlyph.name, thisLayer.name))
										isAffected = True
									
									# rotated
									if findRotated and hasRotatedComponents(thisLayer):
										layersWithRotatedComponents.append(thisLayer)
										print("🔄 %s: layer ‘%s’ contains rotated component" % (thisGlyph.name, thisLayer.name))
										isAffected = True
								
									# mirrored
									if findMirrored and hasMirroredComponents(thisLayer):
										layersWithMirroredComponents.append(thisLayer)
										print("🔀 %s: layer ‘%s’ contains mirrored component" % (thisGlyph.name, thisLayer.name))
										isAffected = True
									
									# shifted
									if findShifted and hasMerelyShiftedComponents(thisLayer):
										layersWithShiftedComponents.append(thisLayer)
										print("↗️ %s: layer ‘%s’ contains shifted component" % (thisGlyph.name, thisLayer.name))
										isAffected = True
						
						if isAffected:
							affectedGlyphCount += 1
							print()
			
				allLayers = []
				allAffectedGlyphs = []
				allText = ""
				for foundLayers in (layersWithScaledComponents, layersWithRotatedComponents, layersWithMirroredComponents, layersWithShiftedComponents):
					if foundLayers:
						allLayers.extend( foundLayers )
						for i in range(2):
							allLayers.append( GSControlLayer.newline() )

						foundGlyphs = []
						for l in foundLayers:
							if not l.parent.name in foundGlyphs:
								foundGlyphs.append(l.parent.name)
						allAffectedGlyphs.extend(foundGlyphs)
						allText += "/"+"/".join(foundGlyphs)+"\n\n"
				if len(allLayers) > 0:
					# opens new Edit tab:
					if reuseTab and thisFont.currentTab:
						newTab = thisFont.currentTab
					else:
						newTab = thisFont.newTab()
					
					if showAllLayers:
						newTab.layers = allLayers
					else:
						newTab.text = allText

			self.w.progress.set(100)
			
			# Final report:
			try:
				affectedGlyphCount = len(set(allAffectedGlyphs))
				Glyphs.showNotification( 
					u"%s: found %i glyph%s" % (
						thisFont.familyName,
						affectedGlyphCount,
						"" if affectedGlyphCount==1 else "s",
						),
					u"Layers found: %s components in %i glyph%s. Details in Macro Window." % (
						("%s%s%s%s" % (
							"%i scaled, " % len(layersWithScaledComponents), # if layersWithScaledComponents else "",
							"%i rotated, " % len(layersWithRotatedComponents), # if layersWithRotatedComponents else "",
							"%i mirrored, " % len(layersWithMirroredComponents), # if layersWithMirroredComponents else "",
							"%i shifted, " % len(layersWithShiftedComponents), # if layersWithShiftedComponents else "",
						))[:-2],
						affectedGlyphCount,
						"" if affectedGlyphCount==1 else "s",
					),
				
					)
			except:
				# Floating notification:
				Glyphs.showNotification( 
					u"%s: nothing found" % (thisFont.familyName),
					u"Script finished with no results. Details in Macro Window.",
					)
				
			print("\nDone. Processed %i glyphs."%glyphCount)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("New Tab with Transformed Components Error: %s" % e)
			import traceback
			print(traceback.format_exc())

NewTabWithTransformedComponents()
