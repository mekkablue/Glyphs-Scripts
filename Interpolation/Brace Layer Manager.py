# MenuTitle: Brace and Bracket Manager
__doc__ = """
Find and replace brace and bracket layer coordinates.
"""

import objc
import vanilla
from AppKit import NSColor, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSNotificationCenter, NSTextAlignmentRight
from Foundation import NSNumberFormatter
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


class BraceLayerManager(mekkaObject):
	prefDict = {
		"layerType": 0,
		"scope": 0,
		"oldCoordinate": 100,
		"newCoordinate": 200,
		"axisIndex": 0,
		"currentMasterOnly": 0,
	}
	layerTypes = (
		"{ } brace (intermediate) layers",
		"[ ] bracket (alternate) layers",
	)

	scopes = (
		"in selected glyphs",
		"⚠️ in ALL glyphs of current font",
		"⚠️ in ALL glyphs of ⚠️ ALL open fonts",
	)

	def __init__(self):
		# Window 'self.w':
		windowWidth = 380
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Brace and Bracket Manager",  # window title
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "In", sizeStyle="small")
		self.w.layerType = vanilla.PopUpButton("auto", self.layerTypes, sizeStyle="small", callback=self.SavePreferences)

		self.w.replaceText = vanilla.TextBox("auto", "replace", sizeStyle="small")
		self.w.oldCoordinate = vanilla.ComboBox("auto", self.allBraceAndBracketLayerCoordinatesInFrontmostFont(), sizeStyle="small", callback=self.SavePreferences)
		self.w.oldCoordinateUpdate = UpdateButton("auto", callback=self.update)
		tooltipText = "Leave empty for disabling the brace layer or deleting the bracket layer condition."
		self.w.withText = vanilla.TextBox("auto", "with", sizeStyle="small")
		self.w.withText.setToolTip(tooltipText)
		self.w.newCoordinate = vanilla.EditText("auto", "100", callback=self.SavePreferences, sizeStyle="small")
		self.w.newCoordinate.setToolTip(tooltipText)

		self.w.axisText = vanilla.TextBox("auto", "for axis at index", sizeStyle="small")
		axisIndexFormatter = NSNumberFormatter.alloc().init()
		axisIndexFormatter.setAllowsFloats_(False)
		axisIndexFormatter.setMinimum_(0)
		self.w.axisIndex = SteppingEditText("auto", "0", callback=self.SavePreferences, sizeStyle="small", formatter=axisIndexFormatter)
		self.w.axisTextAfter = vanilla.TextBox("auto", "(first axis = 0)", sizeStyle="small")
		self.w.axisTextAfter.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())

		self.w.scope = vanilla.VerticalRadioGroup("auto", self.scopes, callback=self.SavePreferences, sizeStyle="small")
		self.w.scope.set(0)

		self.w.currentMasterOnly = vanilla.CheckBox("auto", "Restrict to currently selected master(s) only", value=False, callback=self.SavePreferences, sizeStyle="small")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Change", callback=self.BraceLayerManagerMain)
		self.w.setDefaultButton(self.w.runButton)

		# labels: right-aligned, all with the width of the widest one
		labelNames = ("descriptionText", "replaceText", "axisText")
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes and square buttons stretch vertically by default; with everything
		# hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		def sameAttribute(attribute, viewName, referenceName):
			return {"view1": getattr(self.w, viewName), "attribute1": attribute, "view2": getattr(self.w, referenceName), "attribute2": attribute}

		rules = [
			"H:|-inset-[descriptionText]-gap-[layerType]-inset-|",
			"H:|-inset-[replaceText]-gap-[oldCoordinate(70)]-gap-[oldCoordinateUpdate(24)]-gap-[withText]-gap-[newCoordinate(>=60)]-inset-|",
			"H:|-inset-[axisText]-gap-[axisIndex(50)]-gap-[axisTextAfter]-(>=inset)-|",
			"H:|-inset-[scope]-(>=inset)-|",
			"H:|-inset-[currentMasterOnly]-(>=inset)-|",
			"H:|-(>=inset)-[runButton(>=70)]-inset-|",
			"V:|-inset-[layerType]-row-[oldCoordinate]-row-[axisIndex]-row-[scope(radioHeight)]-checkRow-[currentMasterOnly]-inset-[runButton]-inset-|",
			sameAttribute("width", "replaceText", "descriptionText"),
			sameAttribute("width", "axisText", "descriptionText"),
			sameAttribute("centerY", "descriptionText", "layerType"),
			sameAttribute("centerY", "replaceText", "oldCoordinate"),
			sameAttribute("centerY", "oldCoordinateUpdate", "oldCoordinate"),
			sameAttribute("centerY", "withText", "oldCoordinate"),
			sameAttribute("centerY", "newCoordinate", "oldCoordinate"),
			sameAttribute("centerY", "axisText", "axisIndex"),
			sameAttribute("centerY", "axisTextAfter", "axisIndex"),
		]
		self.w.addAutoPosSizeRules(
			rules,
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5, "radioHeight": self.w.scope.getFittingHeight()},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def update(self, sender=None):
		if sender == self.w.oldCoordinateUpdate:
			allCoordinates = self.allBraceAndBracketLayerCoordinatesInFrontmostFont()
			self.w.oldCoordinate.setItems(allCoordinates)

	def allBraceAndBracketLayerCoordinatesInFrontmostFont(self, sender=None):
		allCoordinates = []
		axisIndex = 0
		currentFont = Glyphs.font
		isBraceLayer = self.pref("layerType") == 0
		try:
			axisIndex = self.prefInt("axisIndex")
		except:
			print("Warning: could not retrieve preference for axis index, will default to 0.")

		if currentFont and len(currentFont.axes) > axisIndex:
			axisID = currentFont.axes[axisIndex].axisId
			for thisGlyph in currentFont.glyphs:
				for thisLayer in thisGlyph.layers:
					if thisLayer.isSpecialLayer and thisLayer.attributes:
						if isBraceLayer and "coordinates" in thisLayer.attributes.keys():
							currentCoord = thisLayer.attributes["coordinates"].get(str(axisID))
							if currentCoord:
								allCoordinates.append(currentCoord)
						if not isBraceLayer and "axisRules" in thisLayer.attributes:
							axisRules = thisLayer.attributes["axisRules"]
							if axisRules and axisID in axisRules.keys():
								axisLimits = axisRules[axisID]
								for border in ("min", "max"):
									if border in axisLimits.keys():
										borderLimit = axisLimits[border]
										allCoordinates.append(borderLimit)

			allCoordinates = sorted(set(allCoordinates), key=lambda coordinate: float(coordinate))

		return allCoordinates

	def BraceLayerManagerMain(self, sender=None):
		# clear macro window log:
		Glyphs.clearLog()

		# update settings to the latest user input:
		self.SavePreferences()

		isBraceLayer = self.pref("layerType") == 0
		scope = self.pref("scope")
		if scope < 2:
			fonts = (Glyphs.font, )
		else:
			fonts = Glyphs.fonts

		count = 0

		for thisFont in fonts:
			if thisFont is None:
				Message(
					title="No Font Open",
					message="The script requires a font. Open a font and run the script again.",
					OKButton=None,
				)
				return
			else:
				thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
				try:
					count = self.processFont(thisFont, isBraceLayer, scope, count)
				except Exception as e:
					# brings macro window to front and reports error:
					Glyphs.showMacroWindow()
					print(f"💔 Brace and Bracket Manager Error\nFont: {thisFont.familyName}\n{e}")
					import traceback
					print(traceback.format_exc())
				finally:
					thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
					if thisFont.currentTab and Glyphs.versionNumber >= 3:
						NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisFont.currentTab)
					if thisFont.currentTab:
						thisFont.currentTab.reflow()
			print()

		# Final report:
		reportMsg = "Changed %i %s layer%s" % (
			count,
			"brace" if isBraceLayer else "bracket",
			"" if count == 1 else "s",
		)
		if len(fonts) > 1:
			reportMsg += " in %i fonts"
		Glyphs.showNotification(
			"Brace & Bracket Layer Update Done",
			"%s. Details in Macro Window" % reportMsg,
		)
		print("%s.\nDone." % reportMsg)

	def processFont(self, thisFont, isBraceLayer, scope, count):
		print("Brace and Bracket Manager Report for %s" % thisFont.familyName)
		if thisFont.filepath:
			print(thisFont.filepath)
		else:
			print("⚠️ The font file has not been saved yet.")
		print()

		searchFor = self.prefFloat("oldCoordinate")
		replaceWith = self.pref("newCoordinate").strip()
		if replaceWith == "":
			replaceWith = None
		else:
			replaceWith = float(replaceWith)
		currentMasterOnly = self.prefBool("currentMasterOnly")
		currentMasterID = thisFont.selectedFontMaster.id
		axisIndex = self.prefInt("axisIndex")
		axis = thisFont.axes[axisIndex]
		axisID = axis.axisId
		axisName = axis.name

		if replaceWith is None:
			print(f"🚫 Disabling {axisName}: {searchFor}")
		else:
			print(f"🔢 Attempting {axisName}: {searchFor} → {replaceWith}")

		if scope == 0:
			glyphs = [layer.parent for layer in thisFont.selectedLayers]
		else:
			glyphs = thisFont.glyphs

		for glyph in glyphs:
			# print(f"  Processing {glyph.name}...")
			for layer in glyph.layers:
				if currentMasterOnly and layer.associatedMasterId != currentMasterID:
					continue
				if layer.isSpecialLayer and layer.attributes:
					if isBraceLayer:
						result, count = self.processBraceLayer(layer, count, searchFor, replaceWith, axisID)
					else:
						result, count = self.processBracketLayer(layer, count, searchFor, replaceWith, axisID, axisIndex)
					if not result:
						break
		return count

	def processBraceLayer(self, layer, count, searchFor, replaceWith, axisID):
		if "coordinates" not in layer.attributes.keys():
			return True, count

		currentPos = float(layer.attributes["coordinates"][axisID])
		if currentPos == float(searchFor):
			if replaceWith is not None:
				try:
					layer.attributes["coordinates"][axisID] = replaceWith
				except Exception as e:
					print(f"⚠️ Error in {layer.parent.name}, ‘{layer.name}’: {e}")
			else:
				del layer.attributes["coordinates"][axisID]
				if not layer.attributes["coordinates"]:
					del layer.attributes["coordinates"]
			count += 1
			print(f"  🔠 {count}. {layer.parent.name}")
		return True, count

	def processBracketLayer(self, layer, count, searchFor, replaceWith, axisID, axisIndex):
		axisRules = layer.attributes["axisRules"]
		if not axisRules:
			return True, count
		if axisID not in axisRules.keys():
			print(f"⚠️ Could not find bracket layers for axis ‘{layer.font.axisForId_(axisID).name}’ (index {axisIndex}) in {layer.parent.name}. Did you select the correct axis?")
			Glyphs.showMacroWindow()
			return False

		axisLimits = dict(axisRules[axisID])  # issues with native NSDictionary
		if not axisLimits:
			return

		for border in ("min", "max"):
			if border in axisLimits.keys():
				borderLimit = float(axisLimits[border])
				if borderLimit == float(searchFor):
					if replaceWith is not None:
						axisLimits[border] = replaceWith
						axisRules[axisID] = axisLimits
					else:
						del axisLimits[border]
						if not axisLimits:  # empty dict
							del layer.attributes["axisRules"][axisID]
						else:
							layer.attributes["axisRules"][axisID] = axisLimits
						if not layer.attributes["axisRules"]:
							del layer.attributes["axisRules"]
					count += 1
					print(f"  🔠 {count}. {layer.parent.name} ({border})")
		return True, count


if Glyphs.versionNumber >= 3:
	# GLYPHS 3
	BraceLayerManager()
else:
	# GLYPHS 2
	Message(
		title="Version Error",
		message="This script requires Glyphs 3 or later.",
		OKButton=None,
	)
