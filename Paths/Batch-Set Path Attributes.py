# MenuTitle: Batch-Set Path Attributes
__doc__ = """
Set path attributes of all paths in selected glyphs, the master, the font, etc.
"""

import objc
import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)
from Foundation import NSNumberFormatter


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def intOrNone(value):
	value = str(value)
	if "." in value:
		value = value[:value.find(".")]
	newValue = ""
	for letter in value:
		if letter in "0123456789":
			newValue += letter
	if newValue:
		return newValue
	return None


allAttributeNames = (
	"lineCapStart",
	"lineCapEnd",
	"lineJoin",
	"strokeWidth",
	"strokeHeight",
	"strokePos",
)

strokePositions = {
	"center": None,
	"inside (left of path)": 1,
	"outside (right of path)": 0,
}
sortedStrokePositionNames = sorted(strokePositions.keys(), key=lambda thisListItem: "cio".find(thisListItem[0]))

lineCapsNames = (
	"straight cutoff",
	"round (wide)",
	"round (tight)",
	"square",
	"orthogonal",
)

lineJoinNames = (
	"miter",
	"round",
	"bevel",
)

scopeMaster = (
	"current master",
	"all masters",
)

scopeGlyphs = (
	"selected glyphs",
	"exporting glyphs",
	"all glyphs",
)


class BatchSetPathAttributes(mekkaObject):
	prefDict = {
		"scopeGlyphs": 0,
		"scopeMaster": 0,
		"lineCaps": 2,
		"lineCapsCheck": False,
		"lineJoin": 1,
		"lineJoinCheck": False,
		"strokeWidth": 20,
		"strokeWidthCheck": True,
		"strokeHeight": "",
		"strokeHeightCheck": False,
		"strokePos": 0,
		"strokePosCheck": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Batch-Set Path Attributes",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Attributes in", sizeStyle="small")
		self.w.scopeGlyphs = vanilla.PopUpButton("auto", scopeGlyphs, sizeStyle="small", callback=self.SavePreferences)
		self.w.scopeMasterText = vanilla.TextBox("auto", "for paths on", sizeStyle="small")
		self.w.scopeMaster = vanilla.PopUpButton("auto", scopeMaster, sizeStyle="small", callback=self.SavePreferences)

		tooltip = "Width of the path in units."
		self.w.strokeWidthCheck = vanilla.CheckBox("auto", "Stroke Width", sizeStyle="small", callback=self.SavePreferences)
		self.w.strokeWidthCheck.setToolTip(tooltip)
		strokeWidthFormatter = NSNumberFormatter.alloc().init()
		strokeWidthFormatter.setAllowsFloats_(False)
		strokeWidthFormatter.setMinimum_(0)
		self.w.strokeWidth = SteppingEditText("auto", "20", callback=self.SavePreferences, sizeStyle="small", formatter=strokeWidthFormatter)
		self.w.strokeWidth.setToolTip(tooltip)

		tooltip = "Height of the path in units. Leave empty for monoline (width=height)."
		self.w.strokeHeightCheck = vanilla.CheckBox("auto", "Stroke Height", sizeStyle="small", callback=self.SavePreferences)
		self.w.strokeHeightCheck.setToolTip(tooltip)
		self.w.strokeHeight = vanilla.EditText("auto", "20", callback=self.SavePreferences, sizeStyle="small")
		self.w.strokeHeight.setToolTip(tooltip)

		tooltip = "0: right\n1: left\nempty: center (default)"
		self.w.strokePosCheck = vanilla.CheckBox("auto", "Position", sizeStyle="small", callback=self.SavePreferences)
		self.w.strokePosCheck.setToolTip(tooltip)
		self.w.strokePos = vanilla.PopUpButton("auto", sortedStrokePositionNames, sizeStyle="small", callback=self.SavePreferences)
		self.w.strokePos.setToolTip(tooltip)

		tooltip = "Cap style applied to both the start and end of open paths."
		self.w.lineCapsCheck = vanilla.CheckBox("auto", "Line Caps", sizeStyle="small", callback=self.SavePreferences)
		self.w.lineCapsCheck.setToolTip(tooltip)
		self.w.lineCaps = vanilla.PopUpButton("auto", lineCapsNames, sizeStyle="small", callback=self.SavePreferences)
		self.w.lineCaps.setToolTip(tooltip)

		tooltip = "Join style applied at corners of open and closed paths."
		self.w.lineJoinCheck = vanilla.CheckBox("auto", "Line Join", sizeStyle="small", callback=self.SavePreferences)
		self.w.lineJoinCheck.setToolTip(tooltip)
		self.w.lineJoin = vanilla.PopUpButton("auto", lineJoinNames, sizeStyle="small", callback=self.SavePreferences)
		self.w.lineJoin.setToolTip(tooltip)

		# Buttons at the bottom:
		self.w.extractButton = vanilla.Button("auto", "Extract", callback=self.extractAttributes)
		self.w.extractButton.setToolTip("Extract attributes from currently selected path, or (if none are selected) from the first path in the current glyph.")

		self.w.removeButton = vanilla.Button("auto", "Remove", callback=self.removeAttributes)
		self.w.removeButton.setToolTip("Clears all path attributes for selection above.")

		self.w.runButton = vanilla.Button("auto", "Apply", callback=self.BatchSetPathAttributesMain)
		self.w.setDefaultButton(self.w.runButton)

		# the first column (labels and checkboxes) shares one width, the text labels are right-aligned:
		textLabels = (self.w.descriptionText, self.w.scopeMasterText)
		checkLabels = (self.w.strokeWidthCheck, self.w.strokeHeightCheck, self.w.strokePosCheck, self.w.lineCapsCheck, self.w.lineJoinCheck)
		for label in textLabels:
			label.getNSTextField().setAlignment_(NSTextAlignmentRight)
		columnViews = [label.getNSTextField() for label in textLabels] + [label.getNSButton() for label in checkLabels]
		for nsLabel in columnViews:
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		widestLabel = self.w.strokeHeightCheck
		rules = [
			"H:|-inset-[descriptionText]-gap-[scopeGlyphs]-inset-|",
			"H:|-inset-[scopeMasterText]-gap-[scopeMaster]-inset-|",
			"H:|-inset-[strokeWidthCheck]-gap-[strokeWidth]-inset-|",
			"H:|-inset-[strokeHeightCheck]-gap-[strokeHeight]-inset-|",
			"H:|-inset-[strokePosCheck]-gap-[strokePos]-inset-|",
			"H:|-inset-[lineCapsCheck]-gap-[lineCaps]-inset-|",
			"H:|-inset-[lineJoinCheck]-gap-[lineJoin]-inset-|",
			"H:|-inset-[extractButton(>=70)]-gap-[removeButton(>=70)]-(>=gap)-[runButton(>=70)]-inset-|",
			"V:|-inset-[scopeGlyphs]-row-[scopeMaster]-section-[strokeWidth]-row-[strokeHeight]-row-[strokePos]-row-[lineCaps]-row-[lineJoin]-inset-[runButton]-inset-|",
			"V:[extractButton]-inset-|",
			"V:[removeButton]-inset-|",
		]
		for label in textLabels + checkLabels:
			if label is not widestLabel:
				rules.append({"view1": label, "attribute1": "width", "view2": widestLabel, "attribute2": "width"})
		for label, field in (
			(self.w.descriptionText, self.w.scopeGlyphs),
			(self.w.scopeMasterText, self.w.scopeMaster),
			(self.w.strokeWidthCheck, self.w.strokeWidth),
			(self.w.strokeHeightCheck, self.w.strokeHeight),
			(self.w.strokePosCheck, self.w.strokePos),
			(self.w.lineCapsCheck, self.w.lineCaps),
			(self.w.lineJoinCheck, self.w.lineJoin),
		):
			rules.append({"view1": label, "attribute1": "centerY", "view2": field, "attribute2": "centerY"})
		self.w.addAutoPosSizeRules(rules, metrics={"inset": inset, "gap": 8, "row": 6, "section": 12})

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def glyphScopeErrorMsg(self, sender=None):
		Message(title="Glyph Scope Error", message="No applicable glyphs found. Please select the glyph scope and run the script again.", OKButton=None)

	def noFontOpenErrorMsg(self, sender=None):
		Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)

	def glyphsForCurrentScope(self, thisFont):
		scopeGlyphs = self.pref("scopeGlyphs")

		if scopeGlyphs == 0:
			# selected glyphs
			return [layer.parent for layer in thisFont.selectedLayers]
		elif scopeGlyphs == 1:
			# exporting glyphs
			return [g for g in thisFont.glyphs if g.export]
		elif scopeGlyphs == 2:
			# all glyphs
			return thisFont.glyphs

		return ()

	def extractAttributes(self, sender=None):
		try:
			thisFont = Glyphs.font
			if thisFont and thisFont.selectedLayers:
				currentLayer = thisFont.selectedLayers[0]

				currentPaths = [p for p in currentLayer.paths if p.selected]
				currentPath = None
				if currentPaths:
					currentPath = currentPaths[0]
				elif currentLayer.paths:
					currentPath = currentLayer.paths[0]
				else:
					Message(
						title="⚠️ No path selected",
						message="No path found for extracting attributes. Open a layer containing paths, select a specific path, and try again.",
						OKButton=None
					)

				if currentPath:
					lineCapStart = currentPath.attributeForKey_("lineCapStart")
					if lineCapStart is not None:
						self.setPref("lineCaps", int(lineCapStart))

					lineJoin = currentPath.attributeForKey_("lineJoin")
					if lineJoin is not None:
						self.setPref("lineJoin", int(lineJoin))

					strokeWidth = currentPath.attributeForKey_("strokeWidth")
					self.setPref("strokeWidth", strokeWidth)

					strokeHeight = currentPath.attributeForKey_("strokeHeight")
					self.setPref("strokeHeight", strokeHeight)

					strokePos = currentPath.attributeForKey_("strokePos")
					strokePosPrefValue = None
					for key in strokePositions.keys():
						value = strokePositions[key]
						if strokePos == value:
							strokePosPrefValue = sortedStrokePositionNames.index(key)
					self.setPref("strokePos", strokePosPrefValue)

			self.LoadPreferences()
		except Exception as e:  # noqa: F841
			# brings macro window to front and clears its log:
			Glyphs.showMacroWindow()
			print("\n⚠️ The 'Batch-Set Path Attributes' script encountered an error:\n")
			import traceback
			print(traceback.format_exc())

	def removeAttributes(self, sender=None):
		# clear macro window log:
		Glyphs.clearLog()

		# update settings to the latest user input:
		self.SavePreferences()

		thisFont = Glyphs.font  # frontmost font
		if thisFont is None:
			self.noFontOpenErrorMsg()
			return

		print("Batch-Set Path Attributes Report for %s" % thisFont.familyName)
		if thisFont.filepath:
			print(thisFont.filepath)
		else:
			print("⚠️ The font file has not been saved yet.")
		print()

		scopeMaster = self.pref("scopeMaster")

		glyphs = self.glyphsForCurrentScope(thisFont)
		currentFontMasterID = thisFont.selectedFontMaster.id
		print("🔠 Clearing attributes in %i glyph%s...\n" % (
			len(glyphs),
			"" if len(glyphs) == 1 else "s",
		))

		if not glyphs:
			self.glyphScopeErrorMsg()
		else:
			for thisGlyph in glyphs:
				print("🙅‍♂️ Deleting attributes for: %s" % thisGlyph.name)
				for thisLayer in thisGlyph.layers:
					# scopeMaster: 0 = current master, 1 = all masters
					if scopeMaster == 1 or (scopeMaster == 0 and thisLayer.associatedMasterId == currentFontMasterID):
						if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
							for thisPath in thisLayer.paths:
								for attribute in allAttributeNames:
									thisPath.removeAttributeForKey_(attribute)

		# Final report:
		Glyphs.showNotification(
			"%s: Done" % (thisFont.familyName),
			"Finished removing path attributes. Details in Macro Window",
		)
		print("\nDone.")

	def BatchSetPathAttributesMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				self.noFontOpenErrorMsg()
				return

			print("Batch-Set Path Attributes Report for %s" % thisFont.familyName)
			if thisFont.filepath:
				print(thisFont.filepath)
			else:
				print("⚠️ The font file has not been saved yet.")
			print()

			scopeMaster = self.pref("scopeMaster")
			lineCapsValue = str(self.prefInt("lineCaps"))
			lineCaps = (lineCapsValue, lineCapsValue)
			lineCapsCheck = self.prefBool("lineCapsCheck")
			lineJoin = str(self.prefInt("lineJoin"))
			lineJoinCheck = self.prefBool("lineJoinCheck")
			strokeWidth = self.prefInt("strokeWidth")
			strokeWidthCheck = self.prefBool("strokeWidthCheck")
			strokeHeight = self.pref("strokeHeight")
			strokeHeightCheck = self.prefBool("strokeHeightCheck")
			strokePos = self.pref("strokePos")
			strokePosCheck = self.prefBool("strokePosCheck")
			try:
				strokePosKey = sortedStrokePositionNames[strokePos]
				strokePos = strokePositions[strokePosKey]
			except:
				strokePos = None

			glyphs = self.glyphsForCurrentScope(thisFont)
			currentFontMasterID = thisFont.selectedFontMaster.id
			print("🔠 Setting attributes for %i glyph%s...\n" % (
				len(glyphs),
				"" if len(glyphs) == 1 else "s",
			))

			if not glyphs:
				self.glyphScopeErrorMsg()
				return
			for thisGlyph in glyphs:
				print("💁‍♀️ Setting attributes for: %s" % thisGlyph.name)
				for thisLayer in thisGlyph.layers:
					# scopeMaster: 0 = current master, 1 = all masters
					if scopeMaster == 1 or (scopeMaster == 0 and thisLayer.associatedMasterId == currentFontMasterID):
						if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
							for thisPath in thisLayer.paths:
								# line caps for start and end:
								if lineCapsCheck:
									for capValue, startOrEnd in zip(lineCaps, ("lineCapStart", "lineCapEnd")):
										thisPath.setAttribute_forKey_(capValue, startOrEnd)

								if lineJoinCheck:
									thisPath.setAttribute_forKey_(lineJoin, "lineJoin")

								if strokeWidthCheck:
									# stroke width, height, pos:
									thisPath.setAttribute_forKey_(strokeWidth, "strokeWidth")

								if strokeHeightCheck:
									if strokeHeight:  # default is None
										thisPath.setAttribute_forKey_(strokeHeight, "strokeHeight")
									else:
										thisPath.removeAttributeForKey_("strokeHeight")

								if strokePosCheck:
									if strokePos is None:  # default is None
										thisPath.removeAttributeForKey_("strokePos")
									else:
										thisPath.setAttribute_forKey_(strokePos, "strokePos")

			# Final report:
			Glyphs.showNotification(
				"%s: Done" % (thisFont.familyName),
				"Batch-Set Path Attributes is finished. Details in Macro Window",
			)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Batch-Set Path Attributes Error: %s" % e)
			import traceback
			print(traceback.format_exc())


BatchSetPathAttributes()
