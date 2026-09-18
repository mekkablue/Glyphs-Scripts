# MenuTitle: Add Alignment Zones for Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Creates fitting zones for the selected glyphs, on every master.
"""

import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityWindowSizeStayPut,
)
from Foundation import NSMaxY, NSMinY

if Glyphs.versionNumber >= 4:
	from GlyphsApp import GSMetricStore
elif Glyphs.versionNumber == 3:
	from GlyphsApp import GSMetricValue as GSMetricStore
else:
	from GlyphsApp import GSAlignmentZone


def setMetricValueInMaster(master, metricID, position, overshoot):
	"""
	Stores position and overshoot for the metric with metricID in the master.
	Returns True if the value could be stored, False otherwise.
	"""

	metricValue = GSMetricStore()
	metricValue.position = position
	metricValue.overshoot = overshoot

	if metricValue is None or not metricID:
		return False
	if hasattr(master, "setMetricValue_forId_"):
		try:
			master.setMetricValue_forId_(metricValue, metricID)
			return True
		except Exception:
			pass
	try:
		master.metrics[metricID] = metricValue
		return True
	except Exception:
		return False


class CreateAlignmentZonesforSelectedGlyphs(mekkaObject):
	prefDict = {
		"createTopZones": 1,
		"createBottomZones": 1,
		"dontExceedExistingZones": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 290
		windowHeight = 1  # Auto Layout grows the window to the required size
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Alignment Zones for Selected Glyphs",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", u"Create alignment zones for selected glyphs. Detailed report in Macro Window.", sizeStyle='small', selectable=True)

		self.w.createTopZones = vanilla.CheckBox("auto", u"Create top zones for selected glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.createTopZones.setToolTip(u"If enabled, will create top zones that match the currently selected glyphs, for every master. The height of the lowest selected glyph will be the zone position, the difference to the highest glyph will be the size of the zone.")

		self.w.createBottomZones = vanilla.CheckBox("auto", u"Create bottom zones for selected glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.createBottomZones.setToolTip(u"If enabled, will create bottom zones that match the currently selected glyphs, for every master. The highest bottom edge is the zone position, the difference to the lowest bottom edge will be the zone size.")

		self.w.dontExceedExistingZones = vanilla.CheckBox("auto", u"Prevent zone sizes bigger than current zones", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.dontExceedExistingZones.setToolTip(u"Recommended. If enabled, will make sure that no zone will be added that is larger than existing zones in the master.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Create Zones", callback=self.CreateAlignmentZonesforSelectedGlyphsMain)
		self.w.setDefaultButton(self.w.runButton)

		# The description wraps at this window width, so let it take the available
		# horizontal space instead of demanding its single-line intrinsic width.
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(
			NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal
		)

		# Checkboxes do not resist vertical stretching by default. With every control
		# hugging vertically, Auto Layout determines the window's exact content height.
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[createTopZones]-(>=inset)-|",
				"H:|-inset-[createBottomZones]-(>=inset)-|",
				"H:|-inset-[dontExceedExistingZones]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=90)]-inset-|",
				"V:|-gap-[descriptionText(30)]-line-[createTopZones]-line-[createBottomZones]-line-[dontExceedExistingZones]-inset-[runButton]-inset-|",
			],
			metrics={"inset": inset, "gap": 8, "line": 8},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def zoneIsOverlappingWithExistingOne(self, zonePosition, zoneSize, master, blueFuzz=0):
		requiredDistance = 1 + 2 * blueFuzz
		zoneLow, zoneHigh = sorted((zonePosition, zonePosition + zoneSize))
		for zone in master.alignmentZones:
			lowEnd, highEnd = sorted((zone.position, zone.position + zone.size))
			for zoneBorder in (zoneLow, zoneHigh):
				if lowEnd - requiredDistance < zoneBorder < highEnd + requiredDistance:
					return True
		return False

	def addZoneToMaster(self, zonePosition, zoneSize, master, blueFuzz=0, isTop=True, masterIndex=0):
		if self.zoneIsOverlappingWithExistingOne(zonePosition, zoneSize, master, blueFuzz=0):
			print("❌ Zone p:%i s:%i cannot be added to master ‘%s’: existing zone in the way." % (zonePosition, zoneSize, master.name))
			return 0
		else:
			if Glyphs.versionNumber >= 3:
				# GLYPHS 3 and 4 code:
				name = "New Top" if isTop else "New Bottom"

				metric = master.setMetricPosition_overshoot_type_name_filter_(zonePosition, zoneSize, 0, name, None)
				zoneWasAdded = bool(metric)

				if not zoneWasAdded:
					print("❌ Zone p:%i s:%i cannot be added to master ‘%s’: no way to store metric values in this app version." % (zonePosition, zoneSize, master.name))
					return 0
				print("✅ Zone ‘%s’ p:%i s:%i added to master ‘%s’." % ("mekkablue_zone", zonePosition, zoneSize, master.name))

			else:
				# GLYPHS 2 code:
				if GSAlignmentZone is None:
					print("❌ Zone p:%i s:%i cannot be added to master ‘%s’: GSAlignmentZone unavailable." % (zonePosition, zoneSize, master.name))
					return 0
				z = GSAlignmentZone()
				z.size = zoneSize
				z.position = zonePosition
				master.alignmentZones.append(z)
				print("✅ Zone p:%i s:%i added to master ‘%s’." % (zonePosition, zoneSize, master.name))
			return 1

	def CreateAlignmentZonesforSelectedGlyphsMain(self, sender):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Alignment Zones for Selected Glyphs Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				top = self.pref("createTopZones")
				bottom = self.pref("createBottomZones")
				dontExceed = self.pref("dontExceedExistingZones")

				try:
					# GLYPHS 3
					selectedGlyphs = [layer.parent for layer in thisFont.selectedLayers if layer.shapes]
				except:
					# GLYPHS 2
					selectedGlyphs = [layer.parent for layer in thisFont.selectedLayers if layer.paths or layer.components]

				addedZoneCount = 0

				blueFuzz = 0  # fallback
				blueFuzzParameter = thisFont.customParameters["blueFuzz"]
				if blueFuzzParameter is not None:
					try:
						blueFuzz = int(blueFuzzParameter)
					except:
						pass  # stay with fallback if parameter is invalid

				for i, master in enumerate(thisFont.masters):

					print("\nFont Master %i: %s" % (i + 1, master.name))
					if master.alignmentZones:
						largestSize = max([abs(z.size) for z in master.alignmentZones])
					else:
						largestSize = 100  # unrealistic high value to allow any size if there are no existing zones

					if top:
						allHeights = []
						for g in selectedGlyphs:
							layer = g.layers[master.id]
							allHeights.append(NSMaxY(layer.bounds))

						minHeight = min(allHeights)
						maxHeight = max(allHeights)
						size = maxHeight - minHeight

						if not dontExceed or size <= largestSize:
							zoneSize = max(1, size)
							zonePosition = minHeight
							addedZoneCount += self.addZoneToMaster(zonePosition, zoneSize, master, blueFuzz, isTop=True, masterIndex=i)

					if bottom:
						allDepths = []
						for g in selectedGlyphs:
							layer = g.layers[master.id]
							allDepths.append(NSMinY(layer.bounds))

						maxDepth = min(allDepths)
						minDepth = max(allDepths)
						size = maxDepth - minDepth

						if not dontExceed or abs(size) <= largestSize:
							zonePosition = minDepth
							zoneSize = min(-1, size)
							addedZoneCount += self.addZoneToMaster(zonePosition, zoneSize, master, blueFuzz, isTop=False, masterIndex=i)

					if Glyphs.versionNumber >= 3:
						# GLYPHS 3
						pass
					else:
						# GLYPHS 2
						master.sortAlignmentZones()
						master.setAlignmentZones_(master.alignmentZones)  # triggers UI redraw in Font Info > Masters

					# Floating notification:
					Glyphs.showNotification(
						"%s: Done." % (thisFont.familyName),
						"Added %i zone%s based on %i selected glyph%s. Detailed report in Macro Window." % (
							addedZoneCount,
							"" if addedZoneCount == 1 else "s",
							len(selectedGlyphs),
							"" if len(selectedGlyphs) == 1 else "s",
						),
					)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Create Alignment Zones for Selected Glyphs Error: %s" % e)
			import traceback
			print(traceback.format_exc())


CreateAlignmentZonesforSelectedGlyphs()
