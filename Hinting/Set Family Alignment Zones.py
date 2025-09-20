# MenuTitle: Set Family Alignment Zones
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Inserts Family Alignment Zones parameter with values based on an instance. Needs properly set up and compatible alignment zones in Font Info > Masters.
"""
from copy import deepcopy
import vanilla
from AppKit import NSFont
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton


class SetFamilyAlignmentZones(mekkaObject):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 124
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Set Family Alignment Zones",  # window title
			minSize=(windowWidth, windowHeight + 19),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize + 19),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, lineHeight * 2), "Choose an instance (typically the Regular), and insert its zones as PostScript Family Alignment Zones.", sizeStyle='small', selectable=True)
		linePos += lineHeight * 2

		self.w.instanceText = vanilla.TextBox((inset, linePos + 2, inset + 55, 14), "Instance", sizeStyle='small')

		self.w.instancePicker = vanilla.PopUpButton((inset + 51, linePos, -inset - 22, 19), (), sizeStyle='small')
		self.w.instancePicker.getNSPopUpButton().setToolTip_("Choose the instance that will likely be used most (probably the Regular or Book). Its interpolated zones will be used as Family Alignment Zones. Inactive instances are marked with ‘inactive’.")

		# set font to tabular figures:
		popUpFont = NSFont.monospacedDigitSystemFontOfSize_weight_(NSFont.smallSystemFontSize(), 0.0)
		self.w.instancePicker.getNSPopUpButton().setFont_(popUpFont)

		self.w.updateButton = UpdateButton((-inset - 18, linePos - 1, -inset, 18), callback=self.updateInstancePicker)
		self.w.updateButton.getNSButton().setToolTip_("Click to update the menu with the instances of the currently frontmost font.")
		linePos += lineHeight

		# Help Button:
		self.w.helpTutorial = vanilla.HelpButton((inset, -20 - inset, 22, 22), callback=self.openURL)
		self.w.helpTutorial.getNSButton().setToolTip_("Will open the glyphsapp.com tutorial about PS Hinting, at the section that explains Family Alignment Zones.")

		# Run Button:
		self.w.runButton = vanilla.Button((-110 - inset, -20 - inset, -inset, -inset), "Insert FAZ", callback=self.SetFamilyAlignmentZonesMain)
		self.w.setDefaultButton(self.w.runButton)

		# Open window and focus on it:
		self.updateInstancePicker()
		self.w.open()
		self.w.makeKey()

	def openURL(self, sender):
		URL = None
		if sender == self.w.helpTutorial:
			URL = "https://glyphsapp.com/learn/hinting-postscript-autohinting#g-__family-alignment-zones"
		if URL:
			import webbrowser
			webbrowser.open(URL)

	def updateInstancePicker(self, sender=None):
		thisFont = Glyphs.font
		if thisFont and thisFont.instances:
			listOfInstances = []
			regularIndexes = []

			if Glyphs.versionNumber >= 3:
				# GLYPHS 3
				instances = [i for i in thisFont.instances if i.type == 0]  # exclude OTVar settings
			else:
				# GLYPHS 2
				instances = thisFont.instances

			for i, thisInstance in enumerate(instances):
				if Glyphs.buildNumber > 3198:
					instanceIsExporting = thisInstance.exports
				else:
					instanceIsExporting = thisInstance.active
				familyName = thisInstance.familyName
				if not familyName:
					familyName = thisFont.familyName

				instanceString = "%02i: %s %s%s" % (
					i,
					familyName,
					thisInstance.name,
					" (inactive)" if not instanceIsExporting else "",
				)
				listOfInstances.append(instanceString)
				if thisInstance.name in ("Regular", "Italic", "Regular Italic"):
					if not instanceIsExporting:
						regularIndexes.append(i)
					else:
						regularIndexes.insert(0, i)
			if listOfInstances:
				self.w.instancePicker.setItems(listOfInstances)
				if regularIndexes:
					self.w.instancePicker.set(regularIndexes[0])

	def SetFamilyAlignmentZonesMain(self, sender):
		try:
			Glyphs.clearLog()  # clears macro window log

			thisFont = Glyphs.font  # frontmost font
			print(f"Set Family Alignment Zones Report for {thisFont.familyName}")
			print(thisFont.filepath)
			print()

			instanceName = self.w.instancePicker.getItem()
			instanceIndex = int(instanceName[:instanceName.find(":")])
			thisInstance = [i for i in thisFont.instances if i.type == 0][instanceIndex]
			print("⚠️", thisInstance.name, instanceName)
			if thisInstance.name in instanceName:
				if Glyphs.versionNumber >= 3:
					# GLYPHS 3 code:
					instanceZones = deepcopy(thisInstance.interpolatedFont.masters[0].alignmentZones)
				else:
					# GLYPHS 2 code:
					instanceZones = thisInstance.interpolatedFont.masters[0].alignmentZones.__copy__()
				thisFont.customParameters["Family Alignment Zones"] = instanceZones
				print(f"✅ Set family alignment zones to instance {instanceName}")
				thisFont.parent.windowController().showFontInfoWindowWithTabSelected_(0) # font tab
			else:
				Message(
					title="Family Zones Error",
					message=f"Seems like the instance you picked ({instanceName}) is not in the frontmost font. Please click the update button and choose again.",
					OKButton=None,
				)
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Set Family Alignment Zones Error: {e}")
			import traceback
			print(traceback.format_exc())


SetFamilyAlignmentZones()
