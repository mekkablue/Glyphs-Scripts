#MenuTitle: Move Paths to Component
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Moves paths to a separate glyph and insert them as auto-aligned, anchored components in the source glyph. Perfect for making path+component mixtures into pure composites.
"""

import vanilla
from AppKit import NSNotificationCenter, NSPoint
from copy import copy as copy

class MovePathstoComponent( object ):
	prefID = "com.mekkablue.MovePathstoComponent"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 160
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Move Paths to Component", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), "Turn paths of selected glyph into component on all masters:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.nameText = vanilla.TextBox( (inset, linePos+2, 100, 14), "Component name:", sizeStyle='small', selectable=True )
		self.w.name = vanilla.EditText( (inset+100, linePos, -inset, 19), "_bar.dollar", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.anchorText = vanilla.TextBox( (inset, linePos+2, 100, 14), "Attach to anchor:", sizeStyle='small', selectable=True )
		self.w.anchor = vanilla.ComboBox( (inset+100, linePos-1, -inset-30, 19), self.allAnchorNames(), sizeStyle='small', callback=self.SavePreferences )
		self.w.anchorUpdateButton = vanilla.SquareButton( (-inset-20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.updateAnchors )
		linePos += lineHeight
		
		self.w.includeSpecialLayers = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Include special layers (recommended)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-140-inset, -20-inset, -inset, -inset), "Make Composite", sizeStyle='regular', callback=self.MovePathsToComponentMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Move Paths to Component' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults[self.domain("name")] = self.w.name.get()
			Glyphs.defaults[self.domain("anchor")] = self.w.anchor.get()
			Glyphs.defaults[self.domain("includeSpecialLayers")] = self.w.includeSpecialLayers.get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault(self.domain("name"), "_bar.dollar")
			Glyphs.registerDefault(self.domain("anchor"), "bottom")
			Glyphs.registerDefault(self.domain("includeSpecialLayers"), 0)

			# load previously written prefs:
			self.w.name.set( self.pref("name") )
			self.w.anchor.set( self.pref("anchor") )
			self.w.includeSpecialLayers.set( self.pref("includeSpecialLayers") )
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False
	
	def updateAnchors(self, sender=None):
		anchorNames = self.allAnchorNames()
		self.w.anchor.setItems(anchorNames)
		
	def allAnchorNames(self, sender=None):
		anchorNames = []
		thisFont = Glyphs.font
		if thisFont:
			if thisFont.selectedLayers:
				thisLayer = thisFont.selectedLayers[0]
				for thisAnchor in thisLayer.anchorsTraversingComponents():
					if not thisAnchor.name in anchorNames:
						anchorNames.append(thisAnchor.name)
		return anchorNames
	
	def MovePathsToComponentMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Move Paths to Component' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			glyphName = None
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("‘Move Paths to Component’ Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
				
				# determine current glyph:
				if not thisFont.selectedLayers:
					Message(title="Error: No Glyph", message="The script requires a selected glyph. Best to open a glyph in Edit view.", OKButton="Oops")
					print("🚫 No glyph selected. Aborting.\nDone.")
					return
					
				thisGlyph = thisFont.selectedLayers[0].parent
				glyphName = thisGlyph.name
				if not thisGlyph.layers[0].paths:
					Message(title="Error: No Paths in Glyph", message="The glyph ‘%s’ seems to have no paths. So the script has nothing to turn into a component."%glyphName, OKButton="Oops")
					print("🚫 No paths in first layer of %s. Aborting.\nDone." % glyphName)
					return
				
				print("⚒️ Processing %s..." % thisGlyph.name)
				
				# query prefs:
				newCompName = self.pref("name")
				category = self.pref("category")
				subCategory = self.pref("subCategory")
				attachToAnchor = str(self.pref("anchor"))
				includeSpecialLayers = self.pref("includeSpecialLayers")
				
				# determine the kind of comp glyph, and the name of the new anchor 
				category = "Letter"
				subCategory = None
				if attachToAnchor.endswith("entry"):
					insertAnchor = attachToAnchor.replace("entry","exit")
				elif attachToAnchor.endswith("exit"):
					insertAnchor = attachToAnchor.replace("exit","entry")
				elif attachToAnchor.startswith("_"):
					insertAnchor = attachToAnchor[1:]
				else:
					insertAnchor = "_"+attachToAnchor
					category = "Mark"
					subCategory = "Nonspacing"
				
				# create new comp glyph:
				print("🔠 Creating %s..." % newCompName)
				newGlyph = GSGlyph()
				newGlyph.name = newCompName
				newGlyph.export = False
				newGlyph.category = category
				if subCategory:
					newGlyph.subCategory = subCategory
				if Font.glyphs[newCompName]:
					# overwrite if it already exists
					del Font.glyphs[newCompName]
					print("⚠️ Overwrote existing %s" % newCompName)
				thisFont.glyphs.append(newGlyph)
				
				# step through current glyph and extract paths to new comp glyph:
				for l in thisGlyph.layers:
					# extract paths:
					if l.isMasterLayer or (l.isSpecialLayer and includeSpecialLayers):
						originalWidth = l.width
						newLayer = copy(l)
						
						# get rid of components, we just want paths:
						for i in range(len(newLayer.shapes)-1,-1,-1):
							thisShape = newLayer.shapes[i]
							if type(thisShape) == GSComponent:
								del newLayer.shapes[i]
						
						# insert connecting anchor:
						newAnchor = GSAnchor()
						newAnchor.name = insertAnchor
						newAnchor.position = NSPoint(0,0)
						for referralAnchor in l.anchorsTraversingComponents():
							if referralAnchor.name == attachToAnchor:
								newAnchor.position = referralAnchor.position
								break
						newLayer.anchors.append(newAnchor)
						
						# insert the new layer into the new comp glyph:
						if l.isMasterLayer:
							newGlyph.layers[l.associatedMasterId] = newLayer
						else:
							newGlyph.layers.append(newLayer)

						# in original glyph, insert component before or after:
						componentNames = None
						if "entry" in attachToAnchor or attachToAnchor.startswith("_"):
							componentNames = [newCompName]
							for c in l.components:
								componentNames.append(c.componentName)
						else:
							componentNames = []
							for c in l.components:
								componentNames.append(c.componentName)
							componentNames.append(newCompName)
						if componentNames:
							l.setComponentNames_(componentNames)
	
						# remove paths from original glyph, we just want to keep components:
						for i in range(len(l.shapes)-1,-1,-1):
							thisShape = l.shapes[i]
							if type(thisShape) == GSPath:
								del l.shapes[i]
						
						# autoalign all components and update metrics
						for c in l.components:
							c.setDisableAlignment_(False)
						l.alignComponents() # updates the width
						
						# insert correcting RSB adjustment (minimum 5):
						widthDifference = originalWidth-l.width
						if abs(widthDifference) > 4:
							metricsKey = "==%s%i" % (
								"-" if widthDifference<0 else "+",
								abs(widthDifference),
							)
							if attachToAnchor.endswith("exit"):
								l.leftMetricsKey = metricsKey
								leftOrRight = "left"
							else:
								l.rightMetricsKey = metricsKey
								leftOrRight = "right"
								
							l.updateMetrics()
							l.syncMetrics()
							
							print("↔️ Added %s metrics key ‘%s’ on layer ‘%s’" % (
								leftOrRight,
								l.rightMetricsKey,
								l.name,
							))
			
			# trigger UI update:
			if Glyphs.versionNumber>=3 and thisFont.currentTab:
				NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisFont.currentTab)

			# Final report:
			if glyphName:
				print("✅ Turned %s into a pure composite of %s." % (
					glyphName, 
					" and ".join(componentNames),
					))
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Move Paths to Component Error: %s" % e)
			import traceback
			print(traceback.format_exc())

MovePathstoComponent()