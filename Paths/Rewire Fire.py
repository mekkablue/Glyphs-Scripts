from __future__ import print_function
#MenuTitle: Rewire Fire
# -*- coding: utf-8 -*-
__doc__="""
Finds, selects and marks duplicate coordinates. Two nodes on the same position typically can be rewired with Reconnect Nodes.
"""

import vanilla
from Foundation import NSPoint

class RewireFire( object ):
	nodeMarker = u"🔥"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 180
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			u"🔥 Rewire Fire 🔥", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.RewireFire.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Finds candidates for rewiring with Reconnect Nodes.", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.includeNonExporting = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include non-exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeNonExporting.getNSButton().setToolTip_("Also check in glyphs that are not set to export. Recommended if you have modular components in the font.")
		linePos += lineHeight
		
		self.w.markWithCircle = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Circle duplicate coordinates with annotation ⭕️", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.markWithCircle.getNSButton().setToolTip_("Circle annotations remain after reconnecting the nodes.")
		linePos += lineHeight
		
		self.w.setFireToNode = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Mark nodes with fire emoji 🔥", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.setFireToNode.getNSButton().setToolTip_("Emoji will be added as a node name. Node names may disappear after reconnection and path cleanup.")
		linePos += lineHeight
		
		self.w.openTabWithAffectedLayers = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"New tab with affected layers (otherwise report only)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.openTabWithAffectedLayers.getNSButton().setToolTip_("If checked, will open a new tab with all layers that contain duplicate coordinates. Otherwise, will report in Macro Window only.")
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Fire", sizeStyle='regular', callback=self.RewireFireMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Rewire Fire' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.RewireFire.openTabWithAffectedLayers"] = self.w.openTabWithAffectedLayers.get()
			Glyphs.defaults["com.mekkablue.RewireFire.setFireToNode"] = self.w.setFireToNode.get()
			Glyphs.defaults["com.mekkablue.RewireFire.markWithCircle"] = self.w.markWithCircle.get()
			Glyphs.defaults["com.mekkablue.RewireFire.includeNonExporting"] = self.w.includeNonExporting.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.RewireFire.openTabWithAffectedLayers", 0)
			Glyphs.registerDefault("com.mekkablue.RewireFire.setFireToNode", 1)
			Glyphs.registerDefault("com.mekkablue.RewireFire.markWithCircle", 0)
			Glyphs.registerDefault("com.mekkablue.RewireFire.includeNonExporting", 1)
			self.w.openTabWithAffectedLayers.set( Glyphs.defaults["com.mekkablue.RewireFire.openTabWithAffectedLayers"] )
			self.w.setFireToNode.set( Glyphs.defaults["com.mekkablue.RewireFire.setFireToNode"] )
			self.w.markWithCircle.set( Glyphs.defaults["com.mekkablue.RewireFire.markWithCircle"] )
			self.w.includeNonExporting.set( Glyphs.defaults["com.mekkablue.RewireFire.includeNonExporting"] )
		except:
			return False
			
		return True
	
	def circleInLayerAtPosition( self, layer, position, width=25.0 ):
		circle = GSAnnotation()
		circle.type = CIRCLE
		circle.position = position
		circle.width = width
		layer.annotations.append(circle)

	def RewireFireMain( self, sender ):
		try:
			Glyphs.clearLog()
				
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Rewire Fire' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			print("Rewire Fire Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			
			duplicateCount = 0
			affectedLayers = []
			for thisGlyph in thisFont.glyphs:
				if thisGlyph.export or Glyphs.defaults["com.mekkablue.RewireFire.includeNonExporting"]:
					for thisLayer in thisGlyph.layers:
						if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
							thisLayer.selection = None
							allCoordinates = []
							duplicateCoordinates = []
						
							for thisPath in thisLayer.paths:
								for thisNode in thisPath.nodes:
									if thisNode.type != OFFCURVE:
										if thisNode.position in allCoordinates:
											thisNode.selected = True
											duplicateCoordinates.append(thisNode.position)
											duplicateCount += 1
											if Glyphs.defaults["com.mekkablue.RewireFire.setFireToNode"]:
												thisNode.name = self.nodeMarker
										else:
											allCoordinates.append(thisNode.position)
											if thisNode.name == self.nodeMarker:
												thisNode.name = None
											
							if duplicateCoordinates:
								print()
								print(u"%s, layer: '%s'" % (thisGlyph.name, thisLayer.name))
								for dupe in duplicateCoordinates:
									print(u"   %s x %.1f, y %.1f" % (self.nodeMarker, dupe.x, dupe.y))
							
								if Glyphs.defaults["com.mekkablue.RewireFire.markWithCircle"]:
									coords = set([(p.x,p.y) for p in duplicateCoordinates])
									for dupeCoord in coords:
										x,y = dupeCoord
										self.circleInLayerAtPosition( thisLayer, NSPoint(x,y) )
							
								affectedLayers.append(thisLayer)
			
			
			print("\nFound a total of %i duplicate coordinates. (Triplets count as two.)" % duplicateCount)
			
			if not affectedLayers:
				Message(title="No Duplicates Found", message=u"Could not find any duplicate coordinates in %s."%thisFont.familyName, OKButton=u"😇 Cool")
			elif Glyphs.defaults["com.mekkablue.RewireFire.openTabWithAffectedLayers"]:
				# opens new Edit tab:
				newTab = thisFont.newTab()
				newTab.layers = affectedLayers
			else:
				Glyphs.showMacroWindow()
				
			self.w.close() # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Rewire Fire Error: %s" % e)
			import traceback
			print(traceback.format_exc())

RewireFire()