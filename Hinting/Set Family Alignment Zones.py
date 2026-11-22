# MenuTitle: Set Family Alignment Zones
__doc__ = """
Inserts Family Alignment Zones parameter with values based on an instance. Needs properly set up and compatible alignment zones in Font Info > Masters.
"""

import os
from copy import deepcopy

import vanilla
from AppKit import NSFont, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message, TTF, PLAIN, INSTANCETYPEVARIABLE
from mekkablue import mekkaObject, UpdateButton, makeWindowResizable
from ttfautohintoptions import parameterName, valuelessOptions, availableOptionsDict, availableOptions, removeFromAutohintOptions, dictToParameterValue, ttfAutohintDict, glyphInterpolation, idotlessMeasure, writeOptionsToInstance
# from ttfautohintoptions import *


class SetFamilyAlignmentZones(mekkaObject):
	prefDict = {
		"addTTReference": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Set Family Alignment Zones",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Choose an instance (typically the Regular), and insert its zones as PostScript Family Alignment Zones.", sizeStyle='small', selectable=True)
		# a text block that wraps takes the width it is given, instead of demanding one long line:
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		instanceTooltip = "Choose the instance that will likely be used most (probably the Regular or Book). Its interpolated zones will be used as Family Alignment Zones. Inactive instances are marked with ‘inactive’."
		self.w.instanceText = vanilla.TextBox("auto", "Instance", sizeStyle='small')
		self.w.instanceText.setToolTip(instanceTooltip)
		self.w.instancePicker = vanilla.PopUpButton("auto", (), sizeStyle='small')
		self.w.instancePicker.setToolTip(instanceTooltip)

		# set font to tabular figures:
		popUpFont = NSFont.monospacedDigitSystemFontOfSize_weight_(NSFont.smallSystemFontSize(), 0.0)
		self.w.instancePicker.getNSPopUpButton().setFont_(popUpFont)

		self.w.updateButton = UpdateButton("auto", callback=self.updateInstancePicker)
		self.w.updateButton.setToolTip("Click to update the menu with the instances of the currently frontmost font.")

		self.w.addTTReference = vanilla.CheckBox("auto", "Also add as reference TTF to ttfautohint options", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.addTTReference.setToolTip("Will write a TTF of the same instance into /Users/Shared/.ttf/ and a --reference option to all existing ‘TTF Autohint Options’ parameters in Font Info > Exports.")

		# Help Buttons:
		self.w.helpTutorialPS = vanilla.HelpButton("auto", callback=self.openURL)
		self.w.helpTutorialPS.setToolTip("Will open the glyphsapp.com tutorial about PS Hinting, at the section that explains Family Alignment Zones.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Insert FAZ", callback=self.SetFamilyAlignmentZonesMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.instanceText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[instanceText]-gap-[instancePicker]-gap-[updateButton]-inset-|",
				"H:|-inset-[addTTReference]-(>=inset)-|",
				"H:|-inset-[helpTutorialPS]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText(28)]-row-[instancePicker]-row-[addTTReference]-inset-[runButton]-inset-|",
				"V:[helpTutorialPS]-inset-|",
				{"view1": self.w.instanceText, "attribute1": "centerY", "view2": self.w.instancePicker, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.instancePicker, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

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
		referenceInstance = thisInstance.copy()
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
			if not thisFont:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			print(f"👾 Family Alignment Zones Report for {thisFont.familyName}")
			print(f"📄 {thisFont.filepath}" if thisFont.filepath else f"📄 {thisFont.familyName} (unsaved)")

			instanceName = self.w.instancePicker.getItem()
			instanceIndex = int(instanceName[:instanceName.find(":")])
			thisInstance = [i for i in thisFont.instances if i.type == 0][instanceIndex]
			
			print("\n🤖 Adding PS family alignment zones...")
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
