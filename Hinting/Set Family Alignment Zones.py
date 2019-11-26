from __future__ import print_function
#MenuTitle: Set Family Alignment Zones
# -*- coding: utf-8 -*-
__doc__="""
Inserts Family Alignment Zones parameter with values based on an instance. Needs properly set up and compatible alignment zones in Font Info > Masters.
"""

import vanilla
from AppKit import NSFont

class SetFamilyAlignmentZones( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 140
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Set Family Alignment Zones", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.SetFamilyAlignmentZones.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, lineHeight*2), u"Choose an instance (typically the Regular), and insert its zones as PostScript Family Alignment Zones.", sizeStyle='small', selectable=True )
		linePos += lineHeight*2
		
		self.w.instanceText = vanilla.TextBox( (inset, linePos+2, inset+55, 14), u"Instance:", sizeStyle='small', selectable=True )
		
		self.w.instancePicker = vanilla.PopUpButton( (inset+55, linePos, -inset-25, 17), (), sizeStyle='small' )
		self.w.instancePicker.getNSPopUpButton().setToolTip_("Inactive instances are marked.")
		# set font to tabular figures:
		popUpFont = NSFont.monospacedDigitSystemFontOfSize_weight_(NSFont.smallSystemFontSize(), 0.0)
		self.w.instancePicker.getNSPopUpButton().setFont_(popUpFont)
		
		self.w.updateButton = vanilla.SquareButton( (-inset-20, linePos, -inset, 18), u"↺", sizeStyle='small', callback=self.updateInstancePicker )
		self.w.updateButton.getNSButton().setToolTip_("Click to update the menu with the instances of the current font.")
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-110-inset, -20-inset, -inset, -inset), "Insert FAZ", sizeStyle='regular', callback=self.SetFamilyAlignmentZonesMain )
		self.w.setDefaultButton( self.w.runButton )
		
		
		# Open window and focus on it:
		self.updateInstancePicker()
		self.w.open()
		self.w.makeKey()
	
	def updateInstancePicker(self, sender=None):
		thisFont = Glyphs.font
		if thisFont and thisFont.instances:
			listOfInstances = []
			regularIndexes = []
			for i,thisInstance in enumerate(thisFont.instances):
				instanceString = u"%02i: %s %s%s" % (
					i,
					thisInstance.familyName,
					thisInstance.name,
					" (inactive)" if not thisInstance.active else "",
				)
				listOfInstances.append(instanceString)
				if thisInstance.name in ("Regular", "Italic", "Regular Italic"):
					if not thisInstance.active:
						regularIndexes.append(i)
					else:
						regularIndexes.insert(0,i)
			if listOfInstances:
				self.w.instancePicker.setItems(listOfInstances)
				if regularIndexes:
					self.w.instancePicker.set(regularIndexes[0])
		

	def SetFamilyAlignmentZonesMain( self, sender ):
		try:
			Glyphs.clearLog() # clears macro window log
			
			thisFont = Glyphs.font # frontmost font
			print("Set Family Alignment Zones Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			
			instanceName = self.w.instancePicker.getItem()
			instanceIndex = int(instanceName[:instanceName.find(":")])
			thisInstance = thisFont.instances[instanceIndex]
			if thisInstance.name in instanceName:
				instanceZones = thisInstance.font.masters[0].alignmentZones
				thisFont.customParameters["Family Alignment Zones"] = instanceZones
				print(u"✅ Set family alignment zones to instance %s" % instanceName)
			else:
				Message(
					title="Family Zones Error", 
					message="Seems like the instance you picked (%s) is not in the frontmost font. Please click the update button and choose again." % instanceName, 
					OKButton=None,
				)
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Set Family Alignment Zones Error: %s" % e)
			import traceback
			print(traceback.format_exc())

SetFamilyAlignmentZones()