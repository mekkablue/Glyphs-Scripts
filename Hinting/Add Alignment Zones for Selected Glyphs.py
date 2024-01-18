# MenuTitle: Add Alignment Zones for Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Creates fitting zones for the selected glyphs, on every master.
"""

import vanilla
from Foundation import NSMaxY, NSMinY
from GlyphsApp import Glyphs, GSMetric, GSMetricValue, GSAlignmentZone, Message
from mekkaCore import mekkaObject


# function for adding Metrics to master in Glyphs3
def addNamedHorizontalMetricToMaster(master, name, typeName, position, overshoot):
	metricTypes = {
		"ascender": 1,
		"cap height": 2,
		"x-height": 4,
		"bodyHeight": 6,
		"descender": 7,
		"baseline": 8,
		"italic angle": 9,
	}
	typeName = metricTypes.get(typeName, 0)
	font = master.font
	# metric_dict = dict(name=name,typeName=None,horizontal=True)
	metric = GSMetric()  # .initWithDict_format_(metric_dict, 2)
	metric.name = name
	metric.horizontal = True
	metric.type = typeName

	font.addMetric_(metric)
	metricValue = GSMetricValue.alloc().initWithPosition_overshoot_(position, overshoot)
	master.setMetricValue_forId_(metricValue, metric.id)
	return metric.id


class CreateAlignmentZonesforSelectedGlyphs(mekkaObject):
	prefDict = {
		"createTopZones": 1,
		"createBottomZones": 1,
		"dontExceedExistingZones": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 290
		windowHeight = 170
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Alignment Zones for Selected Glyphs",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 8, 12, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, int(lineHeight * 1.5)), u"Create alignment zones for selected glyphs. Detailed report in Macro Window.", sizeStyle='small', selectable=True)
		linePos += int(lineHeight * 1.7)

		self.w.createTopZones = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Create top zones for selected glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.createTopZones.getNSButton().setToolTip_(u"If enabled, will create top zones that match the currently selected glyphs, for every master. The height of the lowest selected glyph will be the zone position, the difference to the highest glyph will be the size of the zone.")
		linePos += lineHeight

		self.w.createBottomZones = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Create bottom zones for selected glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.createBottomZones.getNSButton().setToolTip_(u"If enabled, will create bottom zones that match the currently selected glyphs, for every master. The highest bottom edge is the zone position, the difference to the lowest bottom edge will be the zone size.")
		linePos += lineHeight

		self.w.dontExceedExistingZones = vanilla.CheckBox((inset, linePos - 1, -inset, 20), u"Prevent zone sizes bigger than current zones", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.dontExceedExistingZones.getNSButton().setToolTip_(u"Recommended. If enabled, will make sure that no zone will be added that is larger than existing zones in the master.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Create Zones", sizeStyle='regular', callback=self.CreateAlignmentZonesforSelectedGlyphsMain)
		self.w.setDefaultButton(self.w.runButton)

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
				# GLYPHS 3 code:
				name = None
				if masterIndex == 0:
					self.current_metric_id = addNamedHorizontalMetricToMaster(master, name, None, zonePosition, zoneSize)
				else:
					metricValue = GSMetricValue.alloc().initWithPosition_overshoot_(zonePosition, zoneSize)
					master.setMetricValue_forId_(metricValue, self.current_metric_id)
				print("✅ Zone ‘%s’ p:%i s:%i added to master ‘%s’." % ("mekkablue_zone", zonePosition, zoneSize, master.name))

			else:
				# GLYPHS 2 code:
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
