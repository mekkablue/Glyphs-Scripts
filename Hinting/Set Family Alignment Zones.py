# MenuTitle: Set Family Alignment Zones
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Inserts Family Alignment Zones parameter with values based on an instance. Needs properly set up and compatible alignment zones in Font Info > Masters.
"""

import vanilla
from AppKit import NSFont
from copy import deepcopy, copy
from GlyphsApp import Glyphs, Message, TTF, PLAIN, INSTANCETYPEVARIABLE
from mekkablue import mekkaObject, UpdateButton
from ttfautohintoptions import parameterName, valuelessOptions, availableOptionsDict, availableOptions, removeFromAutohintOptions, dictToParameterValue, ttfAutohintDict, glyphInterpolation, idotlessMeasure, writeOptionsToInstance
# from ttfautohintoptions import *


class SetFamilyAlignmentZones(mekkaObject):
	prefDict = {
		"addTTReference": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 134
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

		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, lineHeight * 2), "Choose an instance (typically the Regular), and insert its zones as PostScript Family Alignment Zones.", sizeStyle='small', selectable=True)
		linePos += int(lineHeight * 1.7)

		self.w.instanceText = vanilla.TextBox((inset, linePos + 2, inset + 55, 14), "Instance", sizeStyle='small')
		self.w.instancePicker = vanilla.PopUpButton((inset + 51, linePos, -inset - 22, 19), (), sizeStyle='small')
		self.w.instancePicker.getNSPopUpButton().setToolTip_("Choose the instance that will likely be used most (probably the Regular or Book). Its interpolated zones will be used as Family Alignment Zones. Inactive instances are marked with ‘inactive’.")

		# set font to tabular figures:
		popUpFont = NSFont.monospacedDigitSystemFontOfSize_weight_(NSFont.smallSystemFontSize(), 0.0)
		self.w.instancePicker.getNSPopUpButton().setFont_(popUpFont)

		self.w.updateButton = UpdateButton((-inset - 18, linePos - 1, -inset, 18), callback=self.updateInstancePicker)
		self.w.updateButton.getNSButton().setToolTip_("Click to update the menu with the instances of the currently frontmost font.")
		linePos += lineHeight
		
		self.w.addTTReference = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Also add as reference TTF to ttfautohint options", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.addTTReference.getNSButton().setToolTip_("Will write a TTF of the same instance into /Users/Shared/ttf/ and a --reference option to all existing ‘TTF Autohint Options’ parameters in Font Info > Exports.")

		# Help Buttons:
		self.w.helpTutorialPS = vanilla.HelpButton((inset, -20 - inset, 22, 22), callback=self.openURL)
		self.w.helpTutorialPS.getNSButton().setToolTip_("Will open the glyphsapp.com tutorial about PS Hinting, at the section that explains Family Alignment Zones.")

		# Run Button:
		self.w.runButton = vanilla.Button((-110 - inset, -20 - inset, -inset, -inset), "Insert FAZ", callback=self.SetFamilyAlignmentZonesMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Open window and focus on it:
		self.LoadPreferences()
		self.updateInstancePicker()
		self.w.open()
		self.w.makeKey()


	def openURL(self, sender):
		URL = None
		if sender == self.w.helpTutorialPS:
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


	def removeOption(self, sender, optionName="reference", parameterName="TTFAutohint options"):
		for thisInstance in Glyphs.font.instances:
			if thisInstance.customParameters[parameterName]:
				removeFromAutohintOptions(thisInstance, optionName)
				print(f"Removing ttfautohint {optionName} from instance '{thisInstance.name}'.")


	def addInstanceAsReferenceFontToAllTTFautohintOptions(self, thisInstance, destinationFolder="/Users/Shared/.ttf", parameterName="TTFAutohint options", reference="reference"):
		font = thisInstance.font
		if not font:
			Message(
				title="TT Reference Error",
				message=f"Could not determine the font for instance {thisInstance.name}. No ttfautohint reference established.",
				OKButton=None,
				)
			return
		
		# create instance & generate font
		fileName = font.familyName.strip().replace(" ", "").lower()
		fullPath = os.path.join(destinationFolder, fileName + ".ttf")
		referenceInstance = copy(thisInstance)
		referenceInstance.font = font
		referenceInstance.customParameters["fileName"] = fileName
		referenceInstance.generate(TTF, destinationFolder, False, True, False, True, [PLAIN], True)
		print(f"  📄 --reference={fullPath}")

		for instance in font.instances:
			if instance.type == INSTANCETYPEVARIABLE:
				continue

			# remove any previous --reference options
			removeFromAutohintOptions(instance, reference)

			# add the new reference
			if instance.customParameters[parameterName] is not None:
				optionDict = ttfAutohintDict(instance.customParameters[parameterName])
				optionDict[reference] = fullPath
				writeOptionsToInstance(optionDict, instance)
				print(f"  ☑️ Set {reference} in ‘{parameterName}’ parameter in instance '{instance.name}'.")
			else:
				print(f"  🙅‍♂️ No ‘{parameterName}’ parameter in instance '{instance.name}'; skipping.")


	def SetFamilyAlignmentZonesMain(self, sender):
		try:
			Glyphs.clearLog()  # clears macro window log
			self.SavePreferences()
			thisFont = Glyphs.font  # frontmost font
			print(f"👾 Family Alignment Zones Report for {thisFont.familyName}")
			if thisFont.filepath:
				print(f"📄 {thisFont.filepath}")

			instanceName = self.w.instancePicker.getItem()
			instanceIndex = int(instanceName[:instanceName.find(":")])
			thisInstance = [i for i in thisFont.instances if i.type == 0][instanceIndex]
			
			print(f"\n🤖 Adding PS family alignment zones...")
			if thisInstance.name in instanceName:
				# POSTSCRIPT FAMILY ZONES
				if Glyphs.versionNumber >= 3:
					# GLYPHS 3 code:
					instanceZones = deepcopy(thisInstance.interpolatedFont.masters[0].alignmentZones)
				else:
					# GLYPHS 2 code:
					instanceZones = thisInstance.interpolatedFont.masters[0].alignmentZones.__copy__()
				thisFont.customParameters["Family Alignment Zones"] = instanceZones
				print(f"  ☑️ Set family alignment zones to instance {instanceName}")
				thisFont.parent.windowController().showFontInfoWindowWithTabSelected_(0) # font tab
				
				# TRUETYPE REFERENCE FONT
				if self.pref("addTTReference"):
					print("\n🤖 Adding TT reference font...")
					self.addInstanceAsReferenceFontToAllTTFautohintOptions(thisInstance)
			else:
				Message(
					title="Family Zones Error",
					message=f"Seems like the instance you picked ({instanceName}) is not in the frontmost font. Please click the update button and choose again.",
					OKButton=None,
				)
				print(f"\n❌ ERROR: ‘{instanceName}’ not in frontmost font ‘{thisFont.familyName}’.")

			print("\n✅ Done.")
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Set Family Alignment Zones Error: {e}")
			import traceback
			print(traceback.format_exc())


SetFamilyAlignmentZones()
