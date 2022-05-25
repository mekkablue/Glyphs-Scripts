#MenuTitle: Brace and Bracket Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Find and replace brace and bracket layer coordinates.
"""

import vanilla
from AppKit import NSNotificationCenter

class BraceLayerManager( object ):
	prefID = "com.mekkablue.BraceLayerManager"
	
	layerTypes = (
		"{ } brace (intermediate) layers",
		"[ ] bracket (alternate) layers",
	)
	
	scopes = (
		"in selected glyphs",
		"⚠️ in ALL glyphs of current font",
		"⚠️ in ALL glyphs of ⚠️ ALL open fonts",
	)
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 250
		windowHeight = 205
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Brace and Bracket Manager", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 12, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, 20, 14), "In", sizeStyle='small', selectable=True )
		self.w.layerType = vanilla.PopUpButton( (inset+20, linePos, -inset, 17), self.layerTypes, sizeStyle='small', callback=self.SavePreferences )
			
		linePos += lineHeight
		self.w.replaceText = vanilla.TextBox( (inset, linePos+2, 45, 14), "replace", sizeStyle='small', selectable=True )
		self.w.oldCoordinate = vanilla.ComboBox( (inset+45, linePos-1, 55, 19), self.allBraceAndBracketLayerCoordinatesInFrontmostFont(), sizeStyle='small', callback=self.SavePreferences )
		self.w.oldCoordinateUpdate = vanilla.SquareButton( (inset+105, linePos, 20, 18), "↺", sizeStyle='small', callback=self.update )
		self.w.withText = vanilla.TextBox( (inset+130, linePos+2, 30, 14), "with", sizeStyle='small', selectable=True )
		self.w.newCoordinate = vanilla.EditText( (inset+160, linePos-1, -inset, 19), "100", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.axisText = vanilla.TextBox( (inset, linePos+2, 95, 14), "for axis at index", sizeStyle='small', selectable=True )
		self.w.axisIndex = vanilla.EditText( (inset+90, linePos-1, -inset-80, 19), "0", callback=self.SavePreferences, sizeStyle='small' )
		self.w.axisTextAfter = vanilla.TextBox( (-inset-78, linePos+2, -inset, 14), "(first axis = 0)", sizeStyle='small', selectable=True )
		linePos += lineHeight

		self.w.scope = vanilla.RadioGroup( (inset, linePos, -inset, lineHeight*len(self.scopes) ), self.scopes, callback=self.SavePreferences, sizeStyle = 'small' )
		self.w.scope.set( 0 )
		linePos += lineHeight*len(self.scopes)
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-90-inset, -20-inset, -inset, -inset), "Change", sizeStyle='regular', callback=self.BraceLayerManagerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Brace Layer Manager' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def update(self, sender=None):
		if sender==self.w.oldCoordinateUpdate:
			allCoordinates = self.allBraceAndBracketLayerCoordinatesInFrontmostFont()
			self.w.oldCoordinate.setItems(allCoordinates)
	
	def allBraceAndBracketLayerCoordinatesInFrontmostFont(self, sender=None):
		allCoordinates = []
		axisIndex = 0
		currentFont = Glyphs.font
		isBraceLayer = self.pref("layerType") == 0
		try:
			axisIndex = int(self.pref("axisIndex"))
		except:
			print("Warning: could not retrieve preference for axis index, will default to 0.")
			
		if currentFont and len(currentFont.axes)>axisIndex:
			axisID = currentFont.axes[axisIndex].axisId
			for thisGlyph in currentFont.glyphs:
				for thisLayer in thisGlyph.layers:
					if thisLayer.isSpecialLayer and thisLayer.attributes:
						if isBraceLayer and "coordinates" in thisLayer.attributes.keys():
							currentCoord = thisLayer.attributes["coordinates"][axisID]
							allCoordinates.append(currentCoord)
						if not isBraceLayer and "axisRules" in thisLayer.attributes:
							axisRules = thisLayer.attributes["axisRules"]
							if axisRules and axisID in axisRules.keys():
								axisLimits = axisRules[axisID]
								for border in ("min","max"):
									if border in axisLimits.keys():
										borderLimit = axisLimits[border]
										allCoordinates.append(borderLimit)
							
			allCoordinates = sorted(set(allCoordinates), key=lambda coordinate: int(coordinate))
		
		return allCoordinates
	
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults[self.domain("layerType")] = self.w.layerType.get()
			Glyphs.defaults[self.domain("scope")] = self.w.scope.get()
			Glyphs.defaults[self.domain("oldCoordinate")] = self.w.oldCoordinate.get()
			Glyphs.defaults[self.domain("newCoordinate")] = self.w.newCoordinate.get()
			Glyphs.defaults[self.domain("axisIndex")] = self.w.axisIndex.get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault(self.domain("layerType"), 0)
			Glyphs.registerDefault(self.domain("scope"), 0)
			Glyphs.registerDefault(self.domain("oldCoordinate"), 100)
			Glyphs.registerDefault(self.domain("newCoordinate"), 200)
			Glyphs.registerDefault(self.domain("axisIndex"), 0)
			
			# load previously written prefs:
			self.w.layerType.set( self.pref("layerType") )
			self.w.scope.set( self.pref("scope") )
			self.w.oldCoordinate.set( self.pref("oldCoordinate") )
			self.w.newCoordinate.set( self.pref("newCoordinate") )
			self.w.axisIndex.set( self.pref("axisIndex") )
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def BraceLayerManagerMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Brace Layer Manager' could not write preferences.")
			
			isBraceLayer = self.pref("layerType") == 0
			scope = self.pref("scope")
			if scope<2:
				fonts = (Glyphs.font,)
			else:
				fonts = Glyphs.fonts
			
			count = 0
			
			for thisFont in fonts:
				if thisFont is None:
					Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
					return
				else:
					print("Brace and Bracket Manager Report for %s" % thisFont.familyName)
					if thisFont.filepath:
						print(thisFont.filepath)
					else:
						print("⚠️ The font file has not been saved yet.")
					print()
					
					searchFor = int(self.pref("oldCoordinate"))
					replaceWith = int(self.pref("newCoordinate"))
					axis = thisFont.axes[ int(self.pref("axisIndex")) ]
					axisID = axis.axisId
					axisName = axis.name
					
					print("🔢 Attempting %s: %i → %i" % (axisName, searchFor, replaceWith))
					
					if scope == 0:
						glyphs = [l.parent for l in thisFont.selectedLayers]
					else:
						glyphs = thisFont.glyphs
					
					for glyph in glyphs:
						for layer in glyph.layers:
							if layer.isSpecialLayer and layer.attributes:
								if isBraceLayer:
									if "coordinates" in layer.attributes.keys():
										currentPos = layer.attributes["coordinates"][axisID]
										if currentPos == searchFor:
											layer.attributes["coordinates"][axisID] = replaceWith
											count += 1
											print("  🔠 %i. %s" % (count, glyph.name))
								else:
									axisRules = layer.attributes["axisRules"]
									if axisRules:
										axisLimits = axisRules[axisID]
										if axisLimits:
											for border in ("min","max"):
												if border in axisLimits.keys():
													borderLimit = int(axisLimits[border])
													if borderLimit == searchFor:
														axisLimits[border] = replaceWith
														count += 1
														print("  🔠 %i. %s" % (count, glyph.name))
					
					if thisFont.currentTab:
						NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisFont.currentTab)
					
				print()
				
			# Final report:
			reportMsg = "Changed %i %s layer%s" % ( 
				count, 
				"brace" if isBraceLayer else "bracket",
				"" if count==1 else "s",
				)
			if len(fonts) > 1:
				reportMsg += " in %i fonts"
			Glyphs.showNotification( 
				"Brace & Bracket Layer Update Done",
				"%s. Details in Macro Window" % reportMsg,
				)
			print("%s.\nDone." % reportMsg)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Brace and Bracket Manager Error: %s" % e)
			import traceback
			print(traceback.format_exc())

if Glyphs.versionNumber >= 3:
	# GLYPHS 3
	BraceLayerManager()	
else:
	# GLYPHS 2
	Message(title="Version Error", message="This script requires Glyphs 3 or later.", OKButton=None)

