# MenuTitle: BBox Bumper
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Like Auto Bumper, but with the bounding box of a group of glyphs, and the kerning inserted as GPOS feature code in Font Info > Features > kern. Useful if you want to do group kerning with classes that are different from the kerning groups.
"""

import vanilla
import math
from Foundation import NSRect, NSUnionRect, NSIsEmptyRect, NSInsetRect, NSStringFromRect, NSAffineTransform, NSAffineTransformStruct
from kernanalysis import stringToListOfGlyphsForFont, minDistanceBetweenTwoLayers
from GlyphsApp import Glyphs, GSFeature, GSLayer, GSPath, Message
from mekkablue import mekkaObject, UpdateButton


def updatedCode(oldCode, beginSig, endSig, newCode):
	"""Replaces text in oldCode with newCode, but only between beginSig and endSig."""
	beginOffset = oldCode.find(beginSig)
	endOffset = oldCode.find(endSig) + len(endSig)
	newCode = oldCode[:beginOffset] + beginSig + newCode + "\n" + endSig + oldCode[endOffset:]
	return newCode


def createOTFeature(featureName="calt", featureCode="# empty feature code", targetFont=Glyphs.font, codeSig="CUSTOM-CONTEXTUAL-ALTERNATES", prefix=""):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	featureName: name of the feature (str),
	featureCode: the AFDKO feature code (str),
	targetFont: the GSFont object receiving the feature,
	codeSig: the code signature (str) used as delimiters.
	"""

	beginSig = "# BEGIN " + codeSig + "\n"
	endSig = "# END " + codeSig + "\n"

	if featureName in [f.name for f in targetFont.features]:
		# feature already exists:
		targetFeature = targetFont.features[featureName]

		if prefix and not targetFeature.code.strip().startswith(prefix.strip()):
			targetFeature.code = prefix + "\n" + targetFeature.code

		if beginSig in targetFeature.code:
			# replace old code with new code:
			targetFeature.code = updatedCode(targetFeature.code, beginSig, endSig, featureCode)
		else:
			# append new code:
			targetFeature.code += "\n\n" + beginSig + featureCode + "\n" + endSig

		return "Updated existing OT feature ‘%s’." % featureName
	else:
		# create feature with new code:
		newFeature = GSFeature()
		newFeature.name = featureName
		newFeature.code = beginSig + featureCode + "\n" + endSig
		if prefix:
			newFeature.code = prefix + "\n\n" + newFeature.code
		targetFont.features.append(newFeature)
		return "Created new OT feature ‘%s’" % featureName


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
		windowWidth = 570
		windowHeight = 312
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"BBox Bumper Kerning as Feature Code",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		shift = 90

		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Bump the bbox of an OT Class (defined by a token) with other glyphs, and insert kern feature:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.tokenText = vanilla.TextBox((0, linePos + 2, inset + shift - 5, 14), "▪️BBox token:", sizeStyle=’small’, selectable=True)
		self.w.tokenText.getNSTextField().setAlignment_(2)
		self.w.token = vanilla.ComboBox((inset + shift, linePos - 2, -inset - 230, 21), self.tokens, callback=self.SavePreferences)
		self.w.token.getNSComboBox(
		).setToolTip_("Describe a glyph class predicate for defining an OT class, for which the class bbox is calculated and bumped against other glyphs.")
		self.w.helpToken = vanilla.HelpButton((-inset - 230, linePos - 2, -inset - 200, 21), callback=self.openURL)
		self.w.helpToken.setToolTip("Opens the ‘Tokens’ tutorial in a web browser. Look for ‘glyph class predicates’.")
		self.w.otClassNameText = vanilla.TextBox((-inset - 200, linePos + 2, shift - 5, 14), "OT classname:", sizeStyle=’small’, selectable=True)
		self.w.otClassNameText.getNSTextField().setAlignment_(2)
		self.w.otClassName = vanilla.ComboBox((-inset - 200 + shift, linePos - 2, -inset - 22, 21), self.classNames, callback=self.SavePreferences)
		self.w.otClassName.setToolTip("Name of the OT class. Make sure it is unique for all the fonts.")
		self.w.otClassNameUpdate = UpdateButton((-inset - 20, linePos - 3, -inset, 20), callback=self.updateClassName)
		self.w.otClassNameUpdate.setToolTip("Auto-fill classname for the current token.")
		linePos += lineHeight + 2

		self.w.minDistanceText = vanilla.TextBox((0, linePos + 3, inset + shift - 5, 14), "Min distance:", sizeStyle='small', selectable=True)
		self.w.minDistanceText.getNSTextField().setAlignment_(2)
		self.w.minDistance = vanilla.EditText((inset + shift, linePos, shift // 2.2, 19), "40", callback=self.SavePreferences, sizeStyle='small')
		self.w.minDistance.setToolTip("Minimum distance between other glyphs and the class bbox. Setting a value here will create positive kerning.")
		self.w.maxDistanceText = vanilla.TextBox((inset + shift * 1.5 - 5, linePos + 3, shift, 14), "Max distance:", sizeStyle='small', selectable=True)
		self.w.maxDistanceText.getNSTextField().setAlignment_(2)
		self.w.maxDistance = vanilla.EditText((inset + shift * 2.5, linePos, shift // 2.2, 19), "100", callback=self.SavePreferences, sizeStyle='small')
		self.w.maxDistance.setToolTip("Maximum distance between other glyphs and the class bbox. Setting a value here will create negative kerning.")
		self.w.bboxBubbleExtensionText = vanilla.TextBox((inset + shift * 3 - 5, linePos + 3, shift, 14), "Extend bbox:", sizeStyle='small', selectable=True)
		self.w.bboxBubbleExtensionText.getNSTextField().setAlignment_(2)
		self.w.bboxBubbleExtension = vanilla.EditText((inset + shift * 4, linePos, shift // 2.2, 19), "5", callback=self.SavePreferences, sizeStyle='small')
		self.w.bboxBubbleExtension.setToolTip("Extend the class bbox by this amount in units.")
		self.w.thresholdKerningText = vanilla.TextBox((inset + shift * 4.5 - 5, linePos + 3, shift, 14), "Kern threshold:", sizeStyle='small', selectable=True)
		self.w.thresholdKerningText.getNSTextField().setAlignment_(2)
		self.w.thresholdKerning = vanilla.EditText((inset + shift * 5.5, linePos, shift // 2.2, 19), "15", callback=self.SavePreferences, sizeStyle='small')
		self.w.thresholdKerning.setToolTip("Will insert the calculated (positive or negative) kerning only if it is at least this amount.")
		linePos += lineHeight

		self.w.roundByText = vanilla.TextBox((inset + shift * 3 - 5, linePos + 3, shift, 14), "Round by:", sizeStyle='small', selectable=True)
		self.w.roundByText.getNSTextField().setAlignment_(2)
		self.w.roundBy = vanilla.EditText((inset + shift * 4, linePos, shift // 2.2, 19), "5", callback=self.SavePreferences, sizeStyle='small')
		self.w.roundBy.setToolTip("All kerning values will be rounded by this value. Insert 1 for no rounding.")
		self.w.thresholdWidthText = vanilla.TextBox((inset + shift * 4.5 - 5, linePos + 3, shift, 14), "Overkern %:", sizeStyle='small', selectable=True)
		self.w.thresholdWidthText.getNSTextField().setAlignment_(2)
		self.w.thresholdWidth = vanilla.EditText((inset + shift * 5.5, linePos, shift // 2.2, 19), "40", callback=self.SavePreferences, sizeStyle='small')
		self.w.thresholdWidth.setToolTip("Overkern protection. Makes sure that no glyph (in the bbox class) is kerned more than this percentage of its width. Keep below 50.	")
		linePos += int(lineHeight * 1.5)

		self.w.otherGlyphsText = vanilla.TextBox((0, linePos + 2, inset + shift - 5, 14), "🔠 Bump with:", sizeStyle='small', selectable=True)
		self.w.otherGlyphsText.getNSTextField().setAlignment_(2)
		self.w.otherGlyphs = vanilla.ComboBox((inset + shift, linePos - 1, -inset, 19), self.otherGlyphsSuggestions, sizeStyle='small', callback=self.SavePreferences)
		self.w.otherGlyphs.setToolTip("The glyphs against which the class bbox is bumped for determining kerning.")
		linePos += int(lineHeight + 1.2)
		self.w.otherGlyphsOnLeftSide = vanilla.CheckBox((inset + shift, linePos - 1, -inset, 20), "Bump-kern with these glyphs to the LEFT of BBox: 🔠▪️", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.otherGlyphsOnLeftSide.setToolTip("If enabled, will create kerning with the bump glyphs on the left side, and the class bbox on the right side.")
		linePos += lineHeight
		self.w.otherGlyphsOnRightSide = vanilla.CheckBox((inset + shift, linePos - 1, -inset, 20), "Bump-kern with these glyphs to the RIGHT of BBox: ▪️🔠", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.otherGlyphsOnRightSide.setToolTip("If enabled, will create kerning with class bbox on the left side, and the the bump glyphs on the right side.")
		linePos += lineHeight
		self.w.allowKerningExceptions = vanilla.CheckBox((inset + shift, linePos - 1, -inset, 20), "Allow kerning exception if no kerning group is set", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allowKerningExceptions.setToolTip("If one of the bump glyphs does not have a kerning group, you can allow a kerning exception, i.e., kerning with just the bump glyph. If disabled, only group kerning and no kerning exceptions will be created.")
		linePos += int(lineHeight * 1.5)

		self.w.scopeText = vanilla.TextBox((inset, linePos + 2, shift - 5, 14), "Measure in:", sizeStyle='small', selectable=True)
		self.w.scopeText.getNSTextField().setAlignment_(2)
		self.w.scope = vanilla.PopUpButton((inset + shift, linePos, 250, 17), self.scope, sizeStyle='small', callback=self.SavePreferences)
		self.w.scope.setToolTip("Kern feature will be created per font, same for all masters. Here you can define which masters should be measured for determining the kerning pairs.")
		linePos += lineHeight

		# Progress bar:
		self.w.bar = vanilla.ProgressBar((inset, linePos + 2, -inset, 16))
		linePos += lineHeight

		# Run Button:
		self.w.status = vanilla.TextBox((inset, -20 - inset, -130 - inset, 14), "", sizeStyle="small")
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Bump BBox", callback=self.BBoxBumperKerningMain)
		self.w.setDefaultButton(self.w.runButton)

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
			self.w.status.set("Processing…")

			otClassName = self.pref("otClassName")
			token = self.pref("token")
			bboxBubbleExtension = self.prefFloat("bboxBubbleExtension")
			otherGlyphsString = self.pref("otherGlyphs")
			otherGlyphsOnLeftSide = self.pref("otherGlyphsOnLeftSide")
			otherGlyphsOnRightSide = self.pref("otherGlyphsOnRightSide")
			allowKerningExceptions = self.pref("allowKerningExceptions")
			minDistance = self.prefFloat("minDistance")
			maxDistance = self.prefFloat("maxDistance")
			thresholdKerning = self.prefFloat("thresholdKerning")
			thresholdWidth = self.prefFloat("thresholdWidth")
			# roundBy = self.prefFloat("roundBy")
			scope = self.pref("scope")

			if Glyphs.font is None:
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
							self.w.status.set("Measuring %s…" % otherGlyph.name)
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
					for leftKey in distanceDict.keys():
						for rightKey in distanceDict[leftKey].keys():
							dist = round(distanceDict[leftKey][rightKey])
							if dist < minDistance and abs(roundedBy(minDistance - dist, 5)) >= thresholdKerning:
								kernValue = roundedBy(minDistance - dist, 5)
							elif dist > maxDistance and abs(roundedBy(maxDistance - dist, 5)) >= thresholdKerning:
								kernValue = roundedBy(max(maxNegativeKern, maxDistance - dist), 5)  # prevent overkern
							else:
								continue
							otCode += "pos %s %s %i;\n" % (leftKey, rightKey, kernValue)

					featureStatus = createOTFeature(
						featureName="kern",
						featureCode=otCode.strip(),
						targetFont=thisFont,
						codeSig="Kerning %s" % otClassName,
						prefix="# Automatic Code",
					)
					print("🏗 %s" % featureStatus)
					print("🫱🏾‍🫲🏻 Recompiling features...")
					thisFont.compileFeatures()

			self.w.bar.set(100)
			self.w.status.set("Done.")

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
			self.w.status.set("Error.")
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("BBox Bumper Kerning as Feature Code Error: %s" % e)
			import traceback
			print(traceback.format_exc())


BBoxBumperKerning()
