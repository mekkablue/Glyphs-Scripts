#MenuTitle: Position Clicker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Finds all combinations of positional shapes that do not click well. Clicking means sharing two point coordinates when overlapping.
"""

import vanilla
from AppKit import NSPoint, NSFont
from GlyphsApp import OFFCURVE

def layerMissesPointsAtCoordinates(thisLayer, coordinates):
	tickOff = list(coordinates)
	for thisPath in thisLayer.paths:
		if tickOff:
			for thisNode in thisPath.nodes:
				while thisNode.position in tickOff:
					tickOff.remove(thisNode.position)
	return tickOff

def isPositional(glyphName):
	for suffix in ("medi", "init", "fina"):
		if suffix in glyphName.split("."):
			return True
	return False
	
def doTheyClick(rightLayer, leftLayer, requiredClicks=2):
	leftWidth = leftLayer.width
	rightCoordinates = []
	for p in rightLayer.copyDecomposedLayer().paths:
		for n in p.nodes:
			if n.type != OFFCURVE:
				coord = n.position
				coord.x += leftWidth
				rightCoordinates.append(coord)
	clickCount = 0
	for p in leftLayer.copyDecomposedLayer().paths:
		for n in p.nodes:
			if n.position in rightCoordinates:
				clickCount += 1
	if clickCount < requiredClicks:
		print("❌ %s does not click with a following %s (%s)."%(rightLayer.parent.name, leftLayer.parent.name, leftLayer.name))
		return False
	else:
		print("✅ OK: %s ⟺ %s" % (rightLayer.parent.name, leftLayer.parent.name))
		return True

class PositionClicker( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 170
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Position Clicker", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.PositionClicker.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight, indent = 12, 15, 22, 100

		self.w.descriptionText = vanilla.TextBox( (inset, linePos, -inset, 14), "Report positional combos that do not click:", sizeStyle='small', selectable=True )
		self.w.descriptionText.getNSTextField().setToolTip_("Clicking means that when two matching positional shapes follow each other (e.g. initial and final), they ‘click’, i.e., they share at least 2 point coordinates. Or whatever number is set in the minimal node count setting below.")
		linePos += lineHeight
		
		tooltip = "Reference glyph. Pick a medial glyph with paths for clicking. We recommend behDotless-ar.medi."
		self.w.referenceText = vanilla.TextBox( (inset, linePos+2, indent, 14), "Click with glyph", sizeStyle='small', selectable=True )
		self.w.referenceText.getNSTextField().setToolTip_(tooltip)
		
		self.w.referenceGlyphName = vanilla.ComboBox( (inset+indent, linePos-4, -inset-23, 25), self.getAllMediGlyphNames(), callback=self.SavePreferences, sizeStyle='regular' )
		self.w.referenceGlyphName.getNSComboBox().setFont_(NSFont.userFixedPitchFontOfSize_(11))
		self.w.referenceGlyphName.getNSComboBox().setToolTip_(tooltip)
		
		self.w.updateButton = vanilla.SquareButton( (-inset-20, linePos-1, -inset, 18), "↺", sizeStyle='small', callback=self.updateReferenceGlyphs )
		self.w.updateButton.getNSButton().setToolTip_("Update the list in the combo box with all .medi glyphs in the frontmost font.")
		linePos += lineHeight
		
		tooltip = "The amount of point coordinates that must be shared between two consecutive positional forms. E.g., if set to 2, an initial and a final shape must have two or more nodes exactly on top of each other when they follow each other."
		self.w.clickCountText = vanilla.TextBox( (inset, linePos+2, indent, 14), "Minimal node count", sizeStyle='small', selectable=True )
		self.w.clickCount = vanilla.EditText( (inset+indent, linePos-1, -inset, 19), "2", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.includeNonExporting = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeNonExporting.getNSButton().setToolTip_("Will also measure glyphs that are set to not export.")
		linePos += lineHeight
		
		self.w.reuseTab = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Reuse current tab", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reuseTab.getNSButton().setToolTip_("Will use the current tab for output. Will open a new tab only if there is no Edit tab open already.")
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-100-inset, -20-inset, -inset, -inset), "Open Tab", sizeStyle='regular', callback=self.PositionClickerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Position Clicker' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def updateReferenceGlyphs(self, sender=None):
		self.w.referenceGlyphName.setItems( self.getAllMediGlyphNames() )
	
	def updateUI(self, sender=None):
		glyphSelected = self.w.referenceGlyphName.get()
		try:
			atLeastOneClick = int(self.w.clickCount.get())>0
		except:
			# invalid entry for conversion to int
			atLeastOneClick = False
		self.w.runButton.enable(glyphSelected and atLeastOneClick)
	
	def getAllMediGlyphNames(self, sender=None):
		font = Glyphs.font
		fallback = "behDotless-ar.medi"
		if not font:
			return [fallback]
		else:
			glyphNames=[]
			for g in font.glyphs:
				if ".medi" in g.name:
					glyphNames.append(g.name)
			if fallback in glyphNames:
				glyphNames.remove(fallback)
				glyphNames.insert(0, fallback)
			return glyphNames
		
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.PositionClicker.referenceGlyphName"] = self.w.referenceGlyphName.get()
			Glyphs.defaults["com.mekkablue.PositionClicker.includeNonExporting"] = self.w.includeNonExporting.get()
			Glyphs.defaults["com.mekkablue.PositionClicker.reuseTab"] = self.w.reuseTab.get()
			Glyphs.defaults["com.mekkablue.PositionClicker.clickCount"] = self.w.clickCount.get()
			
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.PositionClicker.referenceGlyphName", "behDotless-ar.medi")
			Glyphs.registerDefault("com.mekkablue.PositionClicker.includeNonExporting", False)
			Glyphs.registerDefault("com.mekkablue.PositionClicker.reuseTab", False)
			Glyphs.registerDefault("com.mekkablue.PositionClicker.clickCount", 2)
			
			# load previously written prefs:
			self.w.reuseTab.set( Glyphs.defaults["com.mekkablue.PositionClicker.reuseTab"] )
			self.w.referenceGlyphName.set( Glyphs.defaults["com.mekkablue.PositionClicker.referenceGlyphName"] )
			self.w.includeNonExporting.set( Glyphs.defaults["com.mekkablue.PositionClicker.includeNonExporting"] )
			self.w.clickCount.set( Glyphs.defaults["com.mekkablue.PositionClicker.clickCount"] )
			
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def PositionClickerMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Position Clicker' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Position Clicker Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
			
				referenceGlyphName = Glyphs.defaults["com.mekkablue.PositionClicker.referenceGlyphName"]
				includeNonExporting = Glyphs.defaults["com.mekkablue.PositionClicker.includeNonExporting"]
				reuseTab = Glyphs.defaults["com.mekkablue.PositionClicker.reuseTab"]
				clickCount = int(Glyphs.defaults["com.mekkablue.PositionClicker.clickCount"])
				
				try:
					spaceLayer = thisFont.glyphs["space"].layers[0]
				except:
					spaceLayer = GSControlLayer.newline() 

				referenceGlyph = thisFont.glyphs[referenceGlyphName]
				try:
					# GLYPHS 3
					isRTL = referenceGlyph.direction==2 # 0=LTR, 1=BiDi, 2=RTL
				except:
					# GLYPHS 2
					isRTL = True
				
				tabLayers = []
				count = 0
				comboCount = 0
				for thisGlyph in thisFont.glyphs:
					glyphName = thisGlyph.name
					if isPositional(glyphName):
						comesFirst = (".medi" in glyphName or ".init" in glyphName)
						comesLater = (".medi" in glyphName or ".fina" in glyphName)
						if thisGlyph.export or includeNonExporting:
							for thisLayer in thisGlyph.layers:
								if thisLayer.paths and (thisLayer.isMasterLayer or thisLayer.isSpecialLayer):
									comboCount += 1
									referenceLayer = referenceGlyph.layers[thisLayer.master.id]
									
									if (comesFirst and isRTL) or (comesLater and not isRTL):
										if not doTheyClick(thisLayer, referenceLayer, clickCount):
											tabLayers.append(referenceLayer)
											tabLayers.append(thisLayer)
											tabLayers.append(spaceLayer)
											count += 1
									if (comesLater and isRTL) or (comesFirst and not isRTL):
										if not doTheyClick(referenceLayer, thisLayer, clickCount):
											tabLayers.append(thisLayer)
											tabLayers.append(referenceLayer)
											tabLayers.append(spaceLayer)
											count += 1

				if tabLayers:
					Glyphs.showNotification( 
						"%s: Position Clicker" % (thisFont.familyName),
						"Found %i imprecise connections. Details in Macro Window." % count,
						)
					if not reuseTab or not thisFont.currentTab:
						# opens new Edit tab:
						tab = thisFont.newTab()
					else:
						tab = thisFont.currentTab
					tab.layers = tabLayers
					tab.direction=0 # LTR!
				else:
					Message(
						title="Position Clicker found no problems 😃", 
						message="✅ Checked %i combinations: all positional glyphs with paths click on %i points or more. Good job!\nDetailed report in Macro Window." % (
							comboCount,
							clickCount,
						), 
						OKButton="🥂Cool",
						)
				
			
				self.w.close() # delete if you want window to stay open


			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Position Clicker Error: %s" % e)
			import traceback
			print(traceback.format_exc())

PositionClicker()

