#MenuTitle: sbix Spacer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Batch-set sbix positions and glyph widths.
"""

import vanilla
from AppKit import NSRect, NSPoint, NSSize, NSAffineTransform

class sbixSpacer( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 340
		windowHeight = 200
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"sbix Spacer", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.sbixSpacer.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.insertMarkers = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Reset master layer and insert markers for sbix bounds", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.resetWidths = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Reset sidebearings to image widths", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.preferredSizeForWidthText = vanilla.TextBox( (inset, linePos, 235, 14), " Preferred iColor size for width reference:", sizeStyle='small', selectable=True )
		self.w.preferredSizeForWidth = vanilla.EditText( (inset+235, linePos-3, -inset, 19), "128", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.verticalShift = vanilla.CheckBox( (inset, linePos-1, 120, 20), "Vertical sbix shift:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.verticalShiftValue = vanilla.EditText( (inset+120, linePos-1, -inset, 19), "-100", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.allGlyphs = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Include all iColor glyphs in font (ignore glyph selection)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.allMasters = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Include all masters (otherwise only current master)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		# Buttons:
		self.w.help   = vanilla.HelpButton((inset, -20-inset, 20, 20), callback=self.openURL )
		
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Apply", sizeStyle='regular', callback=self.sbixSpacerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'sbix Spacer' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def openURL(self, sender=None):
		URL = "https://glyphsapp.com/tutorials/creating-an-apple-color-font"
		import webbrowser
		webbrowser.open( URL )
	
	def updateUI(self, sender=None):
		self.w.preferredSizeForWidth.enable( self.w.resetWidths.get() or self.w.insertMarkers.get() )
		self.w.verticalShiftValue.enable( self.w.verticalShift.get() )
		self.w.runButton.enable( self.w.insertMarkers.get() or self.w.verticalShift.get() or self.w.resetWidths.get() )
		
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.sbixSpacer.allGlyphs"] = self.w.allGlyphs.get()
			Glyphs.defaults["com.mekkablue.sbixSpacer.allMasters"] = self.w.allMasters.get()
			Glyphs.defaults["com.mekkablue.sbixSpacer.insertMarkers"] = self.w.insertMarkers.get()
			Glyphs.defaults["com.mekkablue.sbixSpacer.verticalShift"] = self.w.verticalShift.get()
			Glyphs.defaults["com.mekkablue.sbixSpacer.verticalShiftValue"] = self.w.verticalShiftValue.get()
			Glyphs.defaults["com.mekkablue.sbixSpacer.resetWidths"] = self.w.resetWidths.get()
			Glyphs.defaults["com.mekkablue.sbixSpacer.preferredSizeForWidth"] = self.w.preferredSizeForWidth.get()
			
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault( "com.mekkablue.sbixSpacer.allGlyphs", 0 )
			Glyphs.registerDefault( "com.mekkablue.sbixSpacer.allMasters", 0 )
			Glyphs.registerDefault( "com.mekkablue.sbixSpacer.insertMarkers", 1 )
			Glyphs.registerDefault( "com.mekkablue.sbixSpacer.verticalShift", 0 )
			Glyphs.registerDefault( "com.mekkablue.sbixSpacer.verticalShiftValue", -100 )
			Glyphs.registerDefault( "com.mekkablue.sbixSpacer.resetWidths", 0 )
			Glyphs.registerDefault( "com.mekkablue.sbixSpacer.preferredSizeForWidth", 128 )
			
			# load previously written prefs:
			self.w.allGlyphs.set( Glyphs.defaults["com.mekkablue.sbixSpacer.allGlyphs"] )
			self.w.allMasters.set( Glyphs.defaults["com.mekkablue.sbixSpacer.allMasters"] )
			self.w.insertMarkers.set( Glyphs.defaults["com.mekkablue.sbixSpacer.insertMarkers"] )
			self.w.verticalShift.set( Glyphs.defaults["com.mekkablue.sbixSpacer.verticalShift"] )
			self.w.verticalShiftValue.set( Glyphs.defaults["com.mekkablue.sbixSpacer.verticalShiftValue"] )
			self.w.resetWidths.set( Glyphs.defaults["com.mekkablue.sbixSpacer.resetWidths"] )
			self.w.preferredSizeForWidth.set( Glyphs.defaults["com.mekkablue.sbixSpacer.preferredSizeForWidth"] )
			
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False
	
	def addMarkers(self, layer=None, bounds=None):
		if layer and bounds:
			markerPositions = (
				bounds.origin,
				NSPoint( bounds.origin.x+bounds.size.width, bounds.origin.y+bounds.size.height ),
				)
			factors = (1,-1)
			for position, factor in zip(markerPositions,factors):
				# draw rectangle:
				pen = layer.getPen()
				pen.moveTo( position )
				pen.lineTo( (position.x+factor, position.y) )
				pen.lineTo( (position.x, position.y+factor) )
				pen.closePath()
				pen.endPath()
			
	def sbixSpacerMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'sbix Spacer' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("sbix Spacer Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
				
				# query user settings:
				insertMarkers = Glyphs.defaults["com.mekkablue.sbixSpacer.insertMarkers"]
				verticalShift = Glyphs.defaults["com.mekkablue.sbixSpacer.verticalShift"]
				verticalShiftValue = int(Glyphs.defaults["com.mekkablue.sbixSpacer.verticalShiftValue"])
				resetWidths = Glyphs.defaults["com.mekkablue.sbixSpacer.resetWidths"]
				preferredSizeForWidth = int(Glyphs.defaults["com.mekkablue.sbixSpacer.preferredSizeForWidth"])
				allGlyphs = Glyphs.defaults["com.mekkablue.sbixSpacer.allGlyphs"]
				allMasters = Glyphs.defaults["com.mekkablue.sbixSpacer.allMasters"]
				
				if allGlyphs:
					glyphs = thisFont.glyphs
				else:
					glyphs = [l.parent for l in thisFont.selectedLayers]
					
				if allMasters:
					masters = thisFont.masters
				else:
					masters = (thisFont.selectedFontMaster,)
					
				for glyph in glyphs:
					for master in masters:
						masterLayer = glyph.layers[master.id]
						layers = [l for l in glyph.layers if l.master == master and l!=masterLayer]
						isSbixGlyph = False
						for layer in layers:
							if layer.name.startswith("iColor "):
								isSbixGlyph = True
								break
						
						if isSbixGlyph:
							print("🔠 %s"%glyph.name)
							if resetWidths or insertMarkers:
								preferredLayerName = "iColor %i" % preferredSizeForWidth
								preferredLayer = None
								for layer in layers:
									if layer.name == preferredLayerName or (layer.name.startswith("iColor ") and preferredLayer is None):
										preferredLayer = layer
								if preferredLayer:
									if preferredLayer.backgroundImage:
										origin = preferredLayer.backgroundImage.position
										size = preferredLayer.backgroundImage.image.size()
										if size and size.width>1 and size.height>1:
											preferredLayerSize = int(preferredLayer.name.split(" ")[1])
											scaledSize = NSSize(thisFont.upm*size.width/preferredLayerSize, thisFont.upm*size.height/preferredLayerSize)
											if insertMarkers:
												print("  Inserting markers")
												masterLayer.clear()
												bounds = NSRect(origin, scaledSize)
												self.addMarkers(masterLayer, bounds)
											if resetWidths:
												print("  Resetting width to %i"%size.width)
												masterLayer.width = scaledSize.width
						
							if verticalShift:
								print("  Shifting master layer %s units"%verticalShiftValue)
								shiftTransform = NSAffineTransform.transform()
								shiftTransform.translateXBy_yBy_(0,verticalShiftValue)
								shiftMatrix = shiftTransform.transformStruct() # returns the 6-float tuple
								masterLayer.applyTransform(shiftMatrix)

			# Final report:
			Glyphs.showNotification( 
				"%s: Done" % (thisFont.familyName),
				"sbix Spacer is finished. Details in Macro Window",
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("sbix Spacer Error: %s" % e)
			import traceback
			print(traceback.format_exc())

sbixSpacer()