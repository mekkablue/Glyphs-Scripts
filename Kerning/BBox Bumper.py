# MenuTitle: BBox Bumper
__doc__ = """
Like Auto Bumper, but with the bounding box of a group of glyphs, and the kerning inserted as GPOS feature code in Font Info > Features > kern. Useful if you want to do group kerning with classes that are different from the kerning groups.
"""

import vanilla
import math
from AppKit import NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSRect, NSUnionRect, NSIsEmptyRect, NSInsetRect, NSStringFromRect, NSAffineTransform, NSAffineTransformStruct
from kernanalysis import stringToListOfGlyphsForFont, minDistanceBetweenTwoLayers
from GlyphsApp import Glyphs, GSFeature, GSLayer, GSPath, Message
from mekkablue import mekkaObject, UpdateButton, SteppingEditText, integerFormatter, createOTFeature, makeWindowResizable


def straightenedLayer(layer):
	disposableLayer = layer.copyDecomposedLayer()
	if layer.italicAngle != 0:
		skewStruct = NSAffineTransformStruct()
		skewStruct.m11 = 1.0
		skewStruct.m22 = 1.0
		skewStruct.m21 = math.tan(math.radians(-layer.italicAngle))
		skewTransform = NSAffineTransform.transform()
		skewTransform.setTransformStruct_(skewStruct)
		disposableLayer.decomposeSmartOutlines()
		disposableLayer.decomposeCorners()
		disposableLayer.applyTransform(skewTransform.transformStruct())
	return disposableLayer


def kerningKeysForOTKey(otKey, font):
	"""
	Returns all keys under which otKey can show up in font.kerning:
	group keys stay as they are, glyph names are complemented by their glyph IDs.
	"""
	if otKey.startswith("@"):
		return (otKey, )
	keys = [otKey]
	glyph = font.glyphs[otKey]
	if glyph and glyph.id:
		keys.append(glyph.id)
	return tuple(keys)


def nameForKerningKey(kerningKey, font):
	"""Turns a glyph ID used in font.kerning into a glyph name; group keys are returned unchanged."""
	if kerningKey.startswith("@"):
		return kerningKey
	glyph = font.glyphForId_(kerningKey)
	if glyph:
		return glyph.name
	return kerningKey


def bboxKerningKeys(bboxGlyphs, isLeftSide):
	"""
	Returns the set of font.kerning keys that represent the token glyphs
	on the left (isLeftSide=True) or right (isLeftSide=False) side of a pair.
	"""
	keys = set()
	for glyph in bboxGlyphs:
		if not glyph:
			continue
		if glyph.id:
			keys.add(glyph.id)
		keys.add(glyph.name)
		group = glyph.rightKerningGroup if isLeftSide else glyph.leftKerningGroup
		if group:
			keys.add("@MMK_%s_%s" % ("L" if isLeftSide else "R", group))
	return keys


def roundedBy(value, base):
	return base * round(value / base)


def addRects(rects):
	completeRect = NSRect()
	for r in rects:
		completeRect = NSUnionRect(r, completeRect)
	return completeRect


def unionRectForLayers(layers):
	if Glyphs.versionNumber >= 3.2:
		allRects = [layer.fastBounds() for layer in layers]
	else:
		allRects = [layer.bounds for layer in layers]
	unionRect = addRects(allRects)
	return unionRect


def removeRegularKerningForPairs(font, bboxGlyphs, emittedLeftKeys, emittedRightKeys):
	"""
	Deletes those pairs from font.kerning (in all masters) for which the bbox bumper
	has just inserted a feature-code pair. Pairs in which BOTH sides belong to the
	bbox token (or to the kerning groups of its glyphs) are preserved.
	Returns the number of removed pairs.
	"""
	bboxLeftKeys = bboxKerningKeys(bboxGlyphs, isLeftSide=True)
	bboxRightKeys = bboxKerningKeys(bboxGlyphs, isLeftSide=False)

	removeLeftKeys = set()
	for otKey in emittedLeftKeys:
		removeLeftKeys.update(kerningKeysForOTKey(otKey, font))
	removeRightKeys = set()
	for otKey in emittedRightKeys:
		removeRightKeys.update(kerningKeysForOTKey(otKey, font))

	removedCount = 0
	for master in font.masters:
		masterKerning = font.kerning.get(master.id, None)
		if not masterKerning:
			continue
		for leftKey in tuple(masterKerning.keys()):
			for rightKey in tuple(masterKerning[leftKey].keys()):
				# never touch kerning inside the bbox class:
				if leftKey in bboxLeftKeys and rightKey in bboxRightKeys:
					continue
				shouldRemove = (rightKey in bboxRightKeys and leftKey in removeLeftKeys) or (leftKey in bboxLeftKeys and rightKey in removeRightKeys)
				if shouldRemove:
					font.removeKerningForPair(master.id, nameForKerningKey(leftKey, font), nameForKerningKey(rightKey, font))
					removedCount += 1
					print("   ⌫ %s: %s %s" % (master.name, leftKey, rightKey))
	return removedCount


class BBoxBumperKerning(mekkaObject):
	prefDict = {
		"token": "name like '*superior'",
		"otClassName": "superior",
		"minDistance": 40,
		"maxDistance": 100,
		"bboxBubbleExtension": 5,
		"thresholdKerning": 15,
		"roundBy": 5,
		"thresholdWidth": 45,
		"otherGlyphs": "ABCDEFGHIJKLMNOPQRSẞTUVWXYZabcdďðefghijklmnopqrsßtuvwxyz()[]{}:;,.„“”",
		"otherGlyphsOnRightSide": True,
		"otherGlyphsOnLeftSide": True,
		"allowKerningExceptions": False,
		"removeRegularKerning": False,
		"scope": 2,
	}

	scope = (
		"Current master of frontmost font",
		"⚠️ ALL masters of frontmost font",
		"⚠️ ALL masters of ⚠️ ALL open fonts",
	)

	tokens = (
		"name like '*superior'",
		"name like '*inferior'",
		"name like '*.sc'",
	)

	classNames = (
		"superior",
		"inferior",
		"smallcaps",
	)

	otherGlyphsSuggestions = (
		"ABCDEFGHIJKLMNOPQRSẞTUVWXYZabcdďðefghijklmnopqrsßtuvwxyz0123456789()[]{}:;,.„“”",
		"ABCDEFGHIJKLMNOPQRSẞTUVWXYZ",
		"abcdďðefghijklmnopqrsßtuvwxyz",
		"()[]{}:;,.„“”",
		"0123456789",
	)

	def __init__(self):
		# Window 'self.w':
		windowWidth = 640
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"BBox Bumper Kerning as Feature Code",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		formatter = integerFormatter()
		thresholdFormatter = integerFormatter(0)
		roundFormatter = integerFormatter(1)
		percentFormatter = integerFormatter(0, 100)

		self.w.descriptionText = vanilla.TextBox("auto", "Bump the bbox of an OT Class (defined by a token) with other glyphs, and insert kern feature:", sizeStyle='small', selectable=True)

		self.w.tokenText = vanilla.TextBox("auto", "▪️BBox token:", sizeStyle='small', selectable=True)
		self.w.token = vanilla.ComboBox("auto", self.tokens, callback=self.SavePreferences)
		tooltipText = "Describe a glyph class predicate for defining an OT class, for which the class bbox is calculated and bumped against other glyphs."
		self.w.tokenText.setToolTip(tooltipText)
		self.w.token.getNSComboBox().setToolTip_(tooltipText)
		self.w.helpToken = vanilla.HelpButton("auto", callback=self.openURL)
		self.w.helpToken.setToolTip("Opens the 'Tokens' tutorial in a web browser. Look for 'glyph class predicates'.")
		self.w.otClassNameText = vanilla.TextBox("auto", "OT classname:", sizeStyle='small', selectable=True)
		self.w.otClassName = vanilla.ComboBox("auto", self.classNames, callback=self.SavePreferences)
		tooltipText = "Name of the OT class. Make sure it is unique for all the fonts."
		self.w.otClassNameText.setToolTip(tooltipText)
		self.w.otClassName.setToolTip(tooltipText)
		self.w.otClassNameUpdate = UpdateButton("auto", callback=self.updateClassName)
		self.w.otClassNameUpdate.setToolTip("Auto-fill classname for the current token.")

		self.w.minDistanceText = vanilla.TextBox("auto", "Min distance:", sizeStyle='small', selectable=True)
		self.w.minDistance = SteppingEditText("auto", "40", callback=self.SavePreferences, sizeStyle='small', formatter=formatter)
		tooltipText = "Minimum distance between other glyphs and the class bbox. Setting a value here will create positive kerning."
		self.w.minDistanceText.setToolTip(tooltipText)
		self.w.minDistance.setToolTip(tooltipText)
		self.w.maxDistanceText = vanilla.TextBox("auto", "Max distance:", sizeStyle='small', selectable=True)
		self.w.maxDistance = SteppingEditText("auto", "100", callback=self.SavePreferences, sizeStyle='small', formatter=formatter)
		tooltipText = "Maximum distance between other glyphs and the class bbox. Setting a value here will create negative kerning."
		self.w.maxDistanceText.setToolTip(tooltipText)
		self.w.maxDistance.setToolTip(tooltipText)
		self.w.bboxBubbleExtensionText = vanilla.TextBox("auto", "Extend bbox:", sizeStyle='small', selectable=True)
		self.w.bboxBubbleExtension = SteppingEditText("auto", "5", callback=self.SavePreferences, sizeStyle='small', formatter=formatter)
		tooltipText = "Extend the class bbox by this amount in units."
		self.w.bboxBubbleExtensionText.setToolTip(tooltipText)
		self.w.bboxBubbleExtension.setToolTip(tooltipText)
		self.w.thresholdKerningText = vanilla.TextBox("auto", "Kern threshold:", sizeStyle='small', selectable=True)
		self.w.thresholdKerning = SteppingEditText("auto", "15", callback=self.SavePreferences, sizeStyle='small', formatter=thresholdFormatter)
		tooltipText = "Will insert the calculated (positive or negative) kerning only if it is at least this amount."
		self.w.thresholdKerningText.setToolTip(tooltipText)
		self.w.thresholdKerning.setToolTip(tooltipText)

		self.w.roundByText = vanilla.TextBox("auto", "Round by:", sizeStyle='small', selectable=True)
		self.w.roundBy = SteppingEditText("auto", "5", callback=self.SavePreferences, sizeStyle='small', formatter=roundFormatter)
		tooltipText = "All kerning values will be rounded by this value. Insert 1 for no rounding."
		self.w.roundByText.setToolTip(tooltipText)
		self.w.roundBy.setToolTip(tooltipText)
		self.w.thresholdWidthText = vanilla.TextBox("auto", "Overkern %:", sizeStyle='small', selectable=True)
		self.w.thresholdWidth = SteppingEditText("auto", "40", callback=self.SavePreferences, sizeStyle='small', formatter=percentFormatter)
		tooltipText = "Overkern protection. Makes sure that no glyph (in the bbox class) is kerned more than this percentage of its width. Keep below 50."
		self.w.thresholdWidthText.setToolTip(tooltipText)
		self.w.thresholdWidth.setToolTip(tooltipText)

		self.w.otherGlyphsText = vanilla.TextBox("auto", "🔠 Bump with:", sizeStyle='small', selectable=True)
		self.w.otherGlyphs = vanilla.ComboBox("auto", self.otherGlyphsSuggestions, sizeStyle='small', callback=self.SavePreferences)
		tooltipText = "The glyphs against which the class bbox is bumped for determining kerning."
		self.w.otherGlyphsText.setToolTip(tooltipText)
		self.w.otherGlyphs.setToolTip(tooltipText)
		self.w.otherGlyphsOnLeftSide = vanilla.CheckBox("auto", "Bump-kern with these glyphs to the LEFT of BBox: 🔠▪️", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.otherGlyphsOnLeftSide.setToolTip("If enabled, will create kerning with the bump glyphs on the left side, and the class bbox on the right side.")
		self.w.otherGlyphsOnRightSide = vanilla.CheckBox("auto", "Bump-kern with these glyphs to the RIGHT of BBox: ▪️🔠", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.otherGlyphsOnRightSide.setToolTip("If enabled, will create kerning with class bbox on the left side, and the the bump glyphs on the right side.")
		self.w.allowKerningExceptions = vanilla.CheckBox("auto", "Allow kerning exception if no kerning group is set", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allowKerningExceptions.setToolTip("If one of the bump glyphs does not have a kerning group, you can allow a kerning exception, i.e., kerning with just the bump glyph. If disabled, only group kerning and no kerning exceptions will be created.")
		self.w.removeRegularKerning = vanilla.CheckBox("auto", "Remove respective pairs from regular kerning", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeRegularKerning.setToolTip("For every pair inserted into the kern feature code, delete the corresponding pair from the font’s regular kerning (in all masters), so the feature code is not overridden. Kerning between the glyphs of the bbox token (and their kerning group members) is preserved.")

		self.w.scopeText = vanilla.TextBox("auto", "Measure in:", sizeStyle='small', selectable=True)
		self.w.scope = vanilla.PopUpButton("auto", self.scope, sizeStyle='small', callback=self.SavePreferences)
		tooltipText = "Kern feature will be created per font, same for all masters. Here you can define which masters should be measured for determining the kerning pairs."
		self.w.scopeText.setToolTip(tooltipText)
		self.w.scope.setToolTip(tooltipText)

		# Progress bar:
		self.w.bar = vanilla.ProgressBar("auto")

		# Status line and buttons:
		self.w.status = vanilla.TextBox("auto", "🤖 Ready. 💬 See tooltips for help.", sizeStyle="small")
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.openFeaturesButton = vanilla.Button("auto", "Open Features", callback=self.openFeatures)
		self.w.openFeaturesButton.setToolTip("Opens Font Info > Features so you can inspect the inserted kern feature code.")
		self.w.runButton = vanilla.Button("auto", "Bump BBox", callback=self.BBoxBumperKerningMain)
		self.w.runButton.setToolTip("Calculates the kerning between the class bbox and the other glyphs and inserts it as kern feature code.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned and hug their text; the labels in the first column share one width,
		# and so do the labels in the other columns:
		firstColumnLabels = ("tokenText", "minDistanceText", "roundByText", "otherGlyphsText", "scopeText")
		otherColumnLabels = ("otClassNameText", "maxDistanceText", "bboxBubbleExtensionText", "thresholdKerningText", "thresholdWidthText")
		for labelName in firstColumnLabels + otherColumnLabels:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		widthRules = [{
			"view1": getattr(self.w, labelName),
			"attribute1": "width",
			"view2": self.w.otherGlyphsText,
			"attribute2": "width",
		} for labelName in firstColumnLabels if labelName != "otherGlyphsText"]
		widthRules += [{
			"view1": getattr(self.w, labelName),
			"attribute1": "width",
			"view2": self.w.thresholdKerningText,
			"attribute2": "width",
		} for labelName in otherColumnLabels if labelName != "thresholdKerningText"]
		# the numeric fields share one width:
		numericFields = ("minDistance", "maxDistance", "bboxBubbleExtension", "thresholdKerning", "roundBy", "thresholdWidth")
		widthRules += [{
			"view1": getattr(self.w, fieldName),
			"attribute1": "width",
			"view2": self.w.minDistance,
			"attribute2": "width",
		} for fieldName in numericFields[1:]]

		centerRules = []
		for labelName, fieldName in (
			("tokenText", "token"),
			("helpToken", "token"),
			("otClassNameText", "token"),
			("otClassName", "token"),
			("otClassNameUpdate", "token"),
			("minDistanceText", "minDistance"),
			("maxDistanceText", "minDistance"),
			("maxDistance", "minDistance"),
			("bboxBubbleExtensionText", "minDistance"),
			("bboxBubbleExtension", "minDistance"),
			("thresholdKerningText", "minDistance"),
			("thresholdKerning", "minDistance"),
			("roundByText", "roundBy"),
			("thresholdWidthText", "roundBy"),
			("thresholdWidth", "roundBy"),
			("otherGlyphsText", "otherGlyphs"),
			("scopeText", "scope"),
			("status", "runButton"),
			("openFeaturesButton", "runButton"),
		):
			centerRules.append({"view1": getattr(self.w, labelName), "attribute1": "centerY", "view2": getattr(self.w, fieldName), "attribute2": "centerY"})

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[tokenText]-gap-[token(>=150)]-gap-[helpToken]-gap-[otClassNameText]-gap-[otClassName(>=110)]-gap-[otClassNameUpdate]-inset-|",
				"H:|-inset-[minDistanceText]-gap-[minDistance(>=40)]-gap-[maxDistanceText]-gap-[maxDistance]-gap-[bboxBubbleExtensionText]-gap-[bboxBubbleExtension]-gap-[thresholdKerningText]-gap-[thresholdKerning]-(>=inset)-|",
				"H:|-inset-[roundByText]-gap-[roundBy]-gap-[thresholdWidthText]-gap-[thresholdWidth]-(>=inset)-|",
				"H:|-inset-[otherGlyphsText]-gap-[otherGlyphs]-inset-|",
				"H:|-inset-[otherGlyphsText]-gap-[otherGlyphsOnLeftSide]-(>=inset)-|",
				"H:|-inset-[otherGlyphsText]-gap-[otherGlyphsOnRightSide]-(>=inset)-|",
				"H:|-inset-[otherGlyphsText]-gap-[allowKerningExceptions]-(>=inset)-|",
				"H:|-inset-[otherGlyphsText]-gap-[removeRegularKerning]-(>=inset)-|",
				"H:|-inset-[scopeText]-gap-[scope(>=250)]-(>=inset)-|",
				"H:|-inset-[bar]-inset-|",
				"H:|-inset-[status]-(>=gap)-[openFeaturesButton(>=70)]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-headlineGap-[token]-row-[minDistance]-row-[roundBy]-sectionGap-[otherGlyphs]-sectionRow-[otherGlyphsOnLeftSide]-checkRow-[otherGlyphsOnRightSide]-checkRow-[allowKerningExceptions]-checkRow-[removeRegularKerning]-sectionGap-[scope]-row-[bar(16)]-inset-[runButton]-inset-|",
			] + centerRules + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 6, "headlineGap": 12, "sectionGap": 14, "sectionRow": 8, "checkRow": 5},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def openURL(self, sender=None):
		URL = None
		if sender == self.w.helpToken:
			URL = "https://www.glyphsapp.com/learn/tokens"
		if URL:
			import webbrowser
			webbrowser.open(URL)

	def openFeatures(self, sender=None):
		thisFont = Glyphs.font
		if thisFont is None:
			Message(title="No Font Open", message="The script requires at least one font. Open a font and run the script again.", OKButton=None)
			return
		# opens Font Info at the Features tab (4th tab, index 3):
		thisFont.parent.windowController().showFontInfoWindowWithTabSelected_(3)

	def updateClassName(self, sender=None):
		token = self.pref("token")
		for t, cn in zip(self.tokens, self.classNames):
			if token == t:
				self.w.otClassName.set(cn)
				self.SavePreferences()
				return

	def BBoxBumperKerningMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			print("BBox Bumper Report")

			# update settings to the latest user input:
			self.SavePreferences()
			self.w.bar.set(0)
			self.w.status.set("🛠️ Processing…")

			otClassName = self.pref("otClassName")
			token = self.pref("token")
			bboxBubbleExtension = self.prefFloat("bboxBubbleExtension")
			otherGlyphsString = self.pref("otherGlyphs")
			otherGlyphsOnLeftSide = self.pref("otherGlyphsOnLeftSide")
			otherGlyphsOnRightSide = self.pref("otherGlyphsOnRightSide")
			allowKerningExceptions = self.pref("allowKerningExceptions")
			removeRegularKerning = self.prefBool("removeRegularKerning")
			minDistance = self.prefFloat("minDistance")
			maxDistance = self.prefFloat("maxDistance")
			thresholdKerning = self.prefFloat("thresholdKerning")
			thresholdWidth = self.prefFloat("thresholdWidth")
			roundBy = self.prefInt("roundBy") or 1
			scope = self.pref("scope")

			if Glyphs.font is None:
				self.w.status.set("❌ No font open.")
				Message(title="No Font Open", message="The script requires at least one font. Open a font and run the script again.", OKButton=None)
			else:
				if scope == 2:
					theseFonts = Glyphs.fonts
				else:
					theseFonts = (Glyphs.font, )
				for thisFont in theseFonts:
					fontIndicator = thisFont.familyName
					if thisFont.filepath:
						fontIndicator = thisFont.filepath.lastPathComponent()
					print("\n🔠 Font: %s" % fontIndicator)

					# determine other glyphs:
					otherGlyphs = stringToListOfGlyphsForFont(otherGlyphsString, thisFont, report=False)
					if not otherGlyphs:
						print("❌ None of the other glyphs in font and exporting.\nSkipping font.\n")
						continue
					print("✅ %i other glyph%s found exporting in the font." % (
						len(otherGlyphs),
						"" if len(otherGlyphs) == 1 else "s",
					))

					# process token to determine bbox glyphs:
					evaluatedToken = GSFeature.evaluatePredicateToken_font_contextLabel_error_(token, thisFont, "", None)
					if not evaluatedToken:
						print("❌ Token evaluates to nothing: %s\nSkipping font.\n" % token)
						continue
					print("✅ Token → %s" % evaluatedToken)
					bboxGlyphs = [thisFont.glyphs[name] for name in evaluatedToken.strip().split(" ")]

					# prepare otCode
					otCode = "# %s\n@%s=[ $[%s] ];\n" % (evaluatedToken, otClassName, token)

					# prepare nested dict for distances between glyphs
					distanceDict = {}

					def addToDistanceDict(leftKey, rightKey, value):
						if value is None:
							return
						if leftKey not in distanceDict.keys():
							distanceDict[leftKey] = {
								rightKey: value
							}
						else:
							if rightKey not in distanceDict[leftKey].keys():
								distanceDict[leftKey][rightKey] = value
							else:
								# take the smallest possible distance (if measured across multiple masters)
								if value is not None and value < distanceDict[leftKey][rightKey]:
									distanceDict[leftKey][rightKey] = value

					# step through all masters the user wants us to step through:
					if scope == 0:
						theseMasters = (thisFont.selectedFontMaster, )
					else:
						theseMasters = thisFont.masters
					totalSteps = max(1, len(theseMasters) * len(otherGlyphs))
					processedSteps = 0
					for thisMaster in theseMasters:
						print("\nⓂ️ Master: %s" % thisMaster.name)
						bboxLayers = [straightenedLayer(thisFont.glyphs[name].layers[thisMaster.id]) for name in evaluatedToken.strip().split(" ")]
						maxNegativeKern = round(min([layer.width for layer in bboxLayers]) * thresholdWidth / 100) * -1
						smallestLSB = min([layer.LSB for layer in bboxLayers])
						smallestRSB = min([layer.RSB for layer in bboxLayers])
						collectiveBounds = unionRectForLayers(bboxLayers)
						if NSIsEmptyRect(collectiveBounds):
							print("⚠️ Bounds empty for: %s\nSkipping master.\n" % evaluatedToken)
							continue
						print("  ✅ Class bbox: %s" % NSStringFromRect(collectiveBounds))

						collectiveBounds = NSInsetRect(collectiveBounds, -bboxBubbleExtension, -bboxBubbleExtension)
						bboxLayer = GSLayer()
						bboxLayer.shapes.append(GSPath.rectWithRect_(collectiveBounds))
						bboxLayer.setAssociatedMasterId_(thisMaster.id)
						bboxLayer.LSB = smallestLSB - bboxBubbleExtension
						bboxLayer.RSB = smallestRSB - bboxBubbleExtension
						bboxKey = "@%s" % otClassName

						print("  📐 Measuring distances with %i other glyphs..." % len(otherGlyphs))
						for otherGlyph in otherGlyphs:
							processedSteps += 1
							self.w.bar.set(100 * processedSteps // totalSteps)
							self.w.status.set("🔠 %s" % otherGlyph.name)
							otherLayerStraightened = straightenedLayer(otherGlyph.layers[thisMaster.id])
							if otherGlyphsOnLeftSide:
								otherKey = None
								dist = minDistanceBetweenTwoLayers(
									otherLayerStraightened,
									bboxLayer,
									interval=2,
								)
								if otherGlyph.rightKerningGroup:
									otherKey = "@MMK_L_%s" % otherGlyph.rightKerningGroup
								elif allowKerningExceptions:
									otherKey = otherGlyph.name
								if otherKey:
									addToDistanceDict(otherKey, bboxKey, dist)

							if otherGlyphsOnRightSide:
								otherKey = None
								dist = minDistanceBetweenTwoLayers(
									bboxLayer,
									otherLayerStraightened,
									interval=2,
								)
								if otherGlyph.leftKerningGroup:
									otherKey = "@MMK_R_%s" % otherGlyph.leftKerningGroup
								elif allowKerningExceptions:
									otherKey = otherGlyph.name
								if otherKey:
									addToDistanceDict(bboxKey, otherKey, dist)

					print("\n👷🏻‍♂️ Building feature code...")
					emittedLeftKeys = set()  # bump glyphs to the LEFT of the bbox class
					emittedRightKeys = set()  # bump glyphs to the RIGHT of the bbox class
					for leftKey in distanceDict.keys():
						for rightKey in distanceDict[leftKey].keys():
							dist = round(distanceDict[leftKey][rightKey])
							if dist < minDistance and abs(roundedBy(minDistance - dist, roundBy)) >= thresholdKerning:
								kernValue = roundedBy(minDistance - dist, roundBy)
							elif dist > maxDistance and abs(roundedBy(maxDistance - dist, roundBy)) >= thresholdKerning:
								kernValue = roundedBy(max(maxNegativeKern, maxDistance - dist), roundBy)  # prevent overkern
							else:
								continue
							otCode += "pos %s %s %i;\n" % (leftKey, rightKey, kernValue)
							if rightKey == "@%s" % otClassName:
								emittedLeftKeys.add(leftKey)
							else:
								emittedRightKeys.add(rightKey)

					if removeRegularKerning:
						removedCount = removeRegularKerningForPairs(thisFont, bboxGlyphs, emittedLeftKeys, emittedRightKeys)
						print("🗑 Removed %i regular kerning pair%s (all masters)." % (
							removedCount,
							"" if removedCount == 1 else "s",
						))

					print("🫱🏾‍🫲🏻 Adding feature code and recompiling features...")
					featureStatus = createOTFeature(
						featureName="kern",
						featureCode=otCode.strip(),
						targetFont=thisFont,
						codeSig="Kerning %s" % otClassName,
						prefix="# Automatic Code",
					)
					print("🏗 %s" % featureStatus)

			if Glyphs.font is not None:
				self.w.bar.set(100)
				self.w.status.set("✅ Bumped %i font%s." % (len(theseFonts), "" if len(theseFonts) == 1 else "s"))

				# Final report:
				Glyphs.showNotification(
					"BBox Bumper: done",
					"Bumped %s in %i font%s. Details in Macro Window" % (
						otClassName,
						len(theseFonts),
						"" if len(theseFonts) == 1 else "s",
					),
				)
				print("\nDone.")

		except Exception as e:
			self.w.status.set("❌ Error. Details in Macro Window.")
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("BBox Bumper Kerning as Feature Code Error: %s" % e)
			import traceback
			print(traceback.format_exc())


BBoxBumperKerning()
