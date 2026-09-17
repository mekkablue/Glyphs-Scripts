# MenuTitle: Add Alignment Zones for Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Creates fitting zones for the selected glyphs, on every master.
"""

import vanilla
from Foundation import NSMaxY, NSMinY
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, GSMetric, Message

try:
	# Glyphs 3:
	from GlyphsApp import GSMetricValue
except ImportError:
	# Glyphs 4 does not export the class in GlyphsApp anymore, so look it up in the runtime:
	GSMetricValue = None
	try:
		import objc
	except ImportError:
		objc = None
	if objc:
		for className in ("GSMetricValue", "GSMetricStore"):
			try:
				GSMetricValue = objc.lookUpClass(className)
				break
			except Exception:
				continue

try:
	# Glyphs 2 only:
	from GlyphsApp import GSAlignmentZone
except ImportError:
	GSAlignmentZone = None


def newMetricValue(position, overshoot):
	"""
	Returns a metric value object carrying position and overshoot, or None if it cannot
	be created. Glyphs 4 does not export GSMetricValue in GlyphsApp anymore, and the
	initialiser may be unavailable, so fall back to setting the properties separately.
	"""
	if GSMetricValue is None:
		return None
	try:
		return GSMetricValue.alloc().initWithPosition_overshoot_(position, overshoot)
	except AttributeError:
		pass
	try:
		metricValue = GSMetricValue.alloc().init()
		metricValue.position = position
		metricValue.overshoot = overshoot
		return metricValue
	except Exception:
		return None


def setMetricValueInMaster(master, metricID, position, overshoot):
	"""
	Stores position and overshoot for the metric with metricID in the master.
	Returns True if the value could be stored, False otherwise.
	"""
	metricValue = newMetricValue(position, overshoot)
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


# function for adding Metrics to master in Glyphs 3 and 4
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
	if not setMetricValueInMaster(master, metric.id, position, overshoot):
		return None
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

		self.w.createTopZones = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), u"Create top zones for selected glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.createTopZones.setToolTip(u"If enabled, will create top zones that match the currently selected glyphs, for every master. The height of the lowest selected glyph will be the zone position, the difference to the highest glyph will be the size of the zone.")
		linePos += lineHeight

		self.w.createBottomZones = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), u"Create bottom zones for selected glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.createBottomZones.setToolTip(u"If enabled, will create bottom zones that match the currently selected glyphs, for every master. The highest bottom edge is the zone position, the difference to the lowest bottom edge will be the zone size.")
		linePos += lineHeight

		self.w.dontExceedExistingZones = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), u"Prevent zone sizes bigger than current zones", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.dontExceedExistingZones.setToolTip(u"Recommended. If enabled, will make sure that no zone will be added that is larger than existing zones in the master.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Create Zones", callback=self.CreateAlignmentZonesforSelectedGlyphsMain)
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
				# GLYPHS 3 and 4 code:
				name = None
				if masterIndex == 0 or not getattr(self, "current_metric_id", None):
					# no metric yet, e.g. because it could not be added to the first master:
					self.current_metric_id = addNamedHorizontalMetricToMaster(master, name, None, zonePosition, zoneSize)
					zoneWasAdded = bool(self.current_metric_id)
				else:
					zoneWasAdded = setMetricValueInMaster(master, self.current_metric_id, zonePosition, zoneSize)
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
