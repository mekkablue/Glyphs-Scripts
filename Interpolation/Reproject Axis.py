# MenuTitle: Reproject Axis
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Rescale (reproject) all design-space values of an axis to a new min/max range. Recalculates master and instance coordinates, brace (intermediate) and bracket (alternate) layer coordinates, Virtual Master locations, and the axis values in condition feature code.
"""

import re
import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton


def formatValue(value, forceInt=False):
	"""Return a clean string for a number: integer if whole (or forced), otherwise trimmed decimal."""
	rounded = round(value, 4)
	if forceInt or abs(rounded - round(rounded)) < 1e-9:
		return "%i" % round(rounded)
	return ("%f" % rounded).rstrip("0").rstrip(".")


def cleanNumber(value, forceInt=False):
	"""Return an int if the number is whole (or forced), otherwise a rounded float."""
	rounded = round(value, 4)
	if forceInt or abs(rounded - round(rounded)) < 1e-9:
		return int(round(rounded))
	return rounded


class ReprojectAxis(mekkaObject):
	prefDict = {
		"axisPopup": 0,
		"newMin": 0,
		"newMax": 1000,
		"roundValues": True,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 340
		windowHeight = 170
		windowWidthResize = 0  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Reproject Axis",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow"),  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 24

		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Rescale all design values of an axis onto a new range:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.axisLabel = vanilla.TextBox((inset, linePos + 2, 28, 14), "Axis", sizeStyle="small")
		self.w.axisPopup = vanilla.PopUpButton((inset + 32, linePos, -inset - 22, 17), self.axisMenuItems(), callback=self.axisChanged, sizeStyle="small")
		self.w.axisPopup.setToolTip("Pick the axis of the frontmost font whose values you want to reproject. Defaults to the first axis.")
		self.w.axisReset = UpdateButton((-inset - 18, linePos - 1, -inset, 18), callback=self.resetAxisMenu)
		self.w.axisReset.setToolTip("Reset the axis menu to the axes of the frontmost font, and reset the value fields to the current axis extremes.")
		linePos += lineHeight + 4

		# min → [ ] [ ] ← max
		self.w.minLabel = vanilla.TextBox((inset, linePos + 2, 26, 14), "Min", sizeStyle="small")
		self.w.minLabel.setToolTip("The current minimum (lowest master value) of the chosen axis.")
		self.w.currentMin = vanilla.TextBox((inset + 26, linePos + 2, 44, 14), "0", sizeStyle="small", selectable=True, alignment="right")
		self.w.currentMin.setToolTip("The current minimum (lowest master value) of the chosen axis.")
		self.w.arrowRight = vanilla.TextBox((inset + 72, linePos + 2, 14, 14), "→", sizeStyle="small")
		self.w.newMin = vanilla.EditText((inset + 88, linePos - 1, 52, 19), "0", callback=self.SavePreferences, sizeStyle="small")
		self.w.newMin.setToolTip("The new minimum for the chosen axis. All values on the axis are rescaled so that the current min lands here.")
		self.w.newMax = vanilla.EditText((inset + 148, linePos - 1, 52, 19), "1000", callback=self.SavePreferences, sizeStyle="small")
		self.w.newMax.setToolTip("The new maximum for the chosen axis. All values on the axis are rescaled so that the current max lands here.")
		self.w.arrowLeft = vanilla.TextBox((inset + 204, linePos + 2, 14, 14), "←", sizeStyle="small")
		self.w.currentMax = vanilla.TextBox((inset + 222, linePos + 2, 44, 14), "1000", sizeStyle="small", selectable=True)
		self.w.currentMax.setToolTip("The current maximum (highest master value) of the chosen axis.")
		self.w.maxLabel = vanilla.TextBox((inset + 268, linePos + 2, 30, 14), "Max", sizeStyle="small")
		self.w.maxLabel.setToolTip("The current maximum (highest master value) of the chosen axis.")
		linePos += lineHeight

		self.w.roundValues = vanilla.CheckBox((inset, linePos, -inset, 20), "Round reprojected values to full coordinates", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.roundValues.setToolTip("If enabled, all reprojected values (masters, instances, brace and bracket layers, Virtual Masters, and feature code) are rounded to whole numbers. Otherwise, fractional values are kept (rounded to 4 decimal places).")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-110 - inset, -20 - inset, -inset, -inset), "Reproject", callback=self.ReprojectAxisMain)
		self.w.runButton.setToolTip("Rescale masters, instances, brace and bracket layers, Virtual Masters, and condition feature code of the chosen axis from the current onto the new range.")
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def axisMenuItems(self, sender=None):
		items = []
		font = Glyphs.font
		if font and font.axes:
			for axis in font.axes:
				items.append("%s (%s)" % (axis.name, axis.axisTag))
		if not items:
			items = ["⚠️ No axes in frontmost font"]
		return items

	def selectedAxis(self):
		font = Glyphs.font
		if not font or not font.axes:
			return None
		index = self.prefInt("axisPopup")
		if index < 0 or index >= len(font.axes):
			index = 0
		return font.axes[index]

	def currentExtremes(self):
		"""Return (min, max) native master values for the selected axis, or None."""
		font = Glyphs.font
		axis = self.selectedAxis()
		if not font or axis is None or not font.masters:
			return None
		low, high = None, None
		for master in font.masters:
			value = master.axisValueValueForId_(axis.axisId)
			if value is None:
				continue
			if low is None or value < low:
				low = value
			if high is None or value > high:
				high = value
		if low is None or high is None:
			return None
		return low, high

	def resetAxisMenu(self, sender=None):
		self.w.axisPopup.setItems(self.axisMenuItems())
		self.w.axisPopup.set(0)
		self.setPref("axisPopup", 0)
		self.resetValueFields()
		self.SavePreferences()

	def axisChanged(self, sender=None):
		self.SavePreferences()
		self.resetValueFields()
		self.SavePreferences()

	def resetValueFields(self, sender=None):
		extremes = self.currentExtremes()
		if extremes:
			low, high = extremes
			self.w.newMin.set(formatValue(low))
			self.w.newMax.set(formatValue(high))

	def updateUI(self, sender=None):
		extremes = self.currentExtremes()
		if extremes:
			low, high = extremes
			self.w.currentMin.set(formatValue(low))
			self.w.currentMax.set(formatValue(high))
			self.w.runButton.enable(low != high)
		else:
			self.w.currentMin.set("–")
			self.w.currentMax.set("–")
			self.w.runButton.enable(False)

	def reprojectFeatureConditions(self, font, axisTag, reproject, roundValues):
		"""Rescale axis values inside condition statements of feature code. Returns number of edited condition segments."""
		numberPattern = re.compile(r"-?\d+(?:\.\d+)?")
		tagPattern = re.compile(r"\b%s\b" % re.escape(axisTag))
		conditionPattern = re.compile(r"(condition\b)([^;]*)(;)", re.IGNORECASE)
		editCount = [0]

		def rewriteNumbers(segment):
			return numberPattern.sub(lambda m: formatValue(reproject(float(m.group(0))), forceInt=roundValues), segment)

		def rewriteCondition(match):
			head, body, tail = match.group(1), match.group(2), match.group(3)
			segments = body.split(",")
			for i, segment in enumerate(segments):
				if tagPattern.search(segment):
					newSegment = rewriteNumbers(segment)
					if newSegment != segment:
						segments[i] = newSegment
						editCount[0] += 1
			return head + ",".join(segments) + tail

		codeContainers = list(font.features) + list(font.featurePrefixes)
		for container in codeContainers:
			code = container.code
			if code and "condition" in code:
				newCode = conditionPattern.sub(rewriteCondition, code)
				if newCode != code:
					container.code = newCode
					print("\t🔤 Updated condition code in ‘%s’" % container.name)
		return editCount[0]

	def reprojectVirtualMasters(self, font, axisName, reproject, roundValues):
		"""Rescale Locations in 'Virtual Master' custom parameters that reference the chosen axis (by full name). Returns number of edited entries."""
		count = 0
		for parameter in font.customParameters:
			if parameter.name != "Virtual Master":
				continue
			changed = False
			newCoordinates = []
			for coord in parameter.value:
				coordDict = dict(coord)
				if coordDict.get("Axis") == axisName:
					coordDict["Location"] = cleanNumber(reproject(float(coordDict["Location"])), forceInt=roundValues)
					changed = True
					count += 1
				newCoordinates.append(coordDict)
			if changed:
				parameter.value = newCoordinates
		return count

	def ReprojectAxisMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			font = Glyphs.font  # frontmost font
			if font is None:
				Message(title="No Font Open", message="Reproject Axis requires a font. Open a font and run the script again.", OKButton=None)
				return

			axis = self.selectedAxis()
			if axis is None:
				Message(title="No Axis Found", message="The frontmost font has no axes to reproject.", OKButton=None)
				return

			extremes = self.currentExtremes()
			if extremes is None:
				Message(title="No Master Values", message="Could not determine the current range of the axis from the masters.", OKButton=None)
				return
			oldMin, oldMax = extremes

			if oldMax == oldMin:
				Message(title="Zero-Width Axis", message="The current axis range is zero (min equals max), so it cannot be reprojected.", OKButton=None)
				return

			try:
				newMin = float(self.pref("newMin"))
				newMax = float(self.pref("newMax"))
			except ValueError:
				Message(title="Invalid Values", message="The new min and max must be numbers.", OKButton=None)
				return

			if newMax == newMin:
				Message(title="Zero-Width Target", message="The new min and max are identical, which would collapse the axis. Enter two different values.", OKButton=None)
				return

			axisID = axis.axisId
			axisTag = axis.axisTag
			axisName = axis.name
			roundValues = self.prefBool("roundValues")

			def reproject(value):
				return newMin + (float(value) - oldMin) * (newMax - newMin) / (oldMax - oldMin)

			print("Reproject Axis Report for %s" % font.familyName)
			if font.filepath:
				print(font.filepath)
			else:
				print("⚠️ The font file has not been saved yet.")
			print()
			print("↔️ Reprojecting axis ‘%s’ (%s): %s→%s ⇒ %s→%s\n" % (
				axisName, axisTag,
				formatValue(oldMin), formatValue(oldMax),
				formatValue(newMin), formatValue(newMax),
			))

			font.disableUpdateInterface()  # suppresses UI updates in Font View
			try:
				# masters:
				masterCount = 0
				for master in font.masters:
					value = master.axisValueValueForId_(axisID)
					if value is not None:
						master.setAxisValueValue_forId_(cleanNumber(reproject(value), forceInt=roundValues), axisID)
						masterCount += 1
				print("Ⓜ️ Reprojected %i master%s." % (masterCount, "" if masterCount == 1 else "s"))

				# instances:
				instanceCount = 0
				for instance in font.instances:
					value = instance.axisValueValueForId_(axisID)
					if value is not None:
						instance.setAxisValueValue_forId_(cleanNumber(reproject(value), forceInt=roundValues), axisID)
						instanceCount += 1
				print("ℹ️ Reprojected %i instance%s." % (instanceCount, "" if instanceCount == 1 else "s"))

				# brace (intermediate) and bracket (alternate) layers:
				braceCount = 0
				bracketCount = 0
				for glyph in font.glyphs:
					for layer in glyph.layers:
						if not (layer.isSpecialLayer and layer.attributes):
							continue
						# brace / intermediate layers:
						coordinates = layer.attributes["coordinates"]
						if coordinates and axisID in coordinates.keys():
							coordinates[axisID] = cleanNumber(reproject(float(coordinates[axisID])), forceInt=roundValues)
							braceCount += 1
						# bracket / alternate layers:
						axisRules = layer.attributes["axisRules"]
						if axisRules and axisID in axisRules.keys():
							axisLimits = dict(axisRules[axisID])
							changed = False
							for border in ("min", "max"):
								if border in axisLimits.keys() and axisLimits[border] not in (None, ""):
									axisLimits[border] = cleanNumber(reproject(float(axisLimits[border])), forceInt=roundValues)
									changed = True
							if changed:
								axisRules[axisID] = axisLimits
								bracketCount += 1
				print("🔲 Reprojected %i brace layer coordinate%s." % (braceCount, "" if braceCount == 1 else "s"))
				print("🔳 Reprojected %i bracket layer rule%s." % (bracketCount, "" if bracketCount == 1 else "s"))

				# Virtual Masters:
				virtualMasterCount = self.reprojectVirtualMasters(font, axisName, reproject, roundValues)
				print("🧬 Reprojected %i Virtual Master location%s." % (virtualMasterCount, "" if virtualMasterCount == 1 else "s"))

				# condition feature code:
				conditionCount = self.reprojectFeatureConditions(font, axisTag, reproject, roundValues)
				print("🔤 Reprojected %i condition segment%s in feature code." % (conditionCount, "" if conditionCount == 1 else "s"))
			except Exception as e:
				raise e
			finally:
				font.enableUpdateInterface()  # re-enables UI updates in Font View

			# refresh displayed extremes:
			self.updateUI()

			message = "Reprojected axis ‘%s’ onto %s–%s. Details in Macro Window." % (axisName, formatValue(newMin), formatValue(newMax))
			print("\n%s" % message)
			Glyphs.showNotification("%s: Reproject Axis Done" % font.familyName, message)
			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Reproject Axis Error: %s" % e)
			import traceback
			print(traceback.format_exc())


if Glyphs.versionNumber >= 3:
	# GLYPHS 3
	ReprojectAxis()
else:
	# GLYPHS 2
	Message(title="Reproject Axis Error", message="This script requires Glyphs 3 or later, because it relies on the Glyphs 3 axis API.", OKButton=None)
