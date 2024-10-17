# MenuTitle: Short Segment Finder
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Goes through all interpolations and finds segments shorter than a user-specified threshold length.
"""

import vanilla
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSAnnotation, TEXT, Message, distance
from mekkablue import mekkaObject

tempMarker = "###DELETEME###"
nodeMarker = "👌🏻"


class ShortSegmentFinder(mekkaObject):
	prefDict = {
		"minSegmentLength": 10.0,
		"findShortSegmentsInMasters": 0,
		"allGlyphs": 0,
		"exportingOnly": 1,
		"reportIncompatibilities": 0,
		"markSegments": 1,
		"bringMacroWindowToFront": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 280
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Short Segment Finder",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 30), "Finds short segments in interpolations or masters, and opens a new tab with them", sizeStyle='small', selectable=True)
		linePos += lineHeight * 2

		self.w.text_1 = vanilla.TextBox((inset, linePos + 2, 185, 14), "Acceptable min segment length:", sizeStyle='small')
		self.w.minSegmentLength = vanilla.EditText((inset + 185, linePos - 1, -inset, 19), "3", sizeStyle='small', callback=self.SavePreferences)
		self.w.minSegmentLength.getNSTextField().setToolTip_("Minimum length for every segment in all paths, measured in units.")
		linePos += lineHeight

		self.w.findShortSegmentsInMasters = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Look in masters instead (i.e., not in interpolations)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.findShortSegmentsInMasters.getNSButton().setToolTip_("If checked, will not calculate interpolations, but only measure segments in your master drawings, bracket and brace layers.")
		linePos += lineHeight

		self.w.allGlyphs = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Process all glyphs in font (i.e., ignore selection)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allGlyphs.getNSButton().setToolTip_("If unchecked, will only process the currently selected glyph(s).")
		linePos += lineHeight

		self.w.exportingOnly = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Ignore non-exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.exportingOnly.getNSButton().setToolTip_("If checked, will skip glyphs that do not export. Always skips compounds.")
		linePos += lineHeight

		self.w.reportIncompatibilities = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Report incompatibilities and no paths in Macro Window", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportIncompatibilities.getNSButton().setToolTip_("If checked, will warn about incompatibilities and if a glyph has no paths. Usually you want this off, because it will report all compounds.")
		linePos += lineHeight

		self.w.markSegments = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Mark segments in first layer", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.markSegments.getNSButton().setToolTip_("If checked, will mark affected segments with a warning emoji and the minimum segment length. Will mark the corresponding segment in the first layer if it finds a short segment in a calculated instance. Will use an annotation if the segment cannot be found (e.g. if the segment is in a corner component).")
		linePos += lineHeight

		self.w.bringMacroWindowToFront = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Bring Macro Window to front", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.bringMacroWindowToFront.getNSButton().setToolTip_("A detailed report is written to the Macro Window. Activate this check box, and the Macro Window will be brought to the front ever time you run this script.")
		linePos += lineHeight

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)  # set progress indicator to zero
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Open Tab", callback=self.ShortSegmentFinderMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		#
		self.updateUI(None)

	def updateUI(self, sender):
		if self.pref("findShortSegmentsInMasters"):
			self.w.markSegments.setTitle("Mark short segments 👌🏻")
		else:
			self.w.markSegments.setTitle("Mark short segments 👌🏻 in first layer")

		if self.pref("allGlyphs"):
			self.w.runButton.setTitle("Open Tab")
		else:
			self.w.runButton.setTitle("Find Segments")

	def approxLengthOfSegment(self, segment):
		try:
			if len(segment) == 2:
				if Glyphs.versionNumber >= 3:
					# Glyphs 3 code
					p0, p1 = [p for p in segment]
				else:
					# Glyphs 2 code
					p0, p1 = [p.pointValue() for p in segment]
				return ((p1.x - p0.x)**2 + (p1.y - p0.y)**2)**0.5
			elif len(segment) == 4:
				if Glyphs.versionNumber >= 3:
					# Glyphs 3 code
					p0, p1, p2, p3 = [p for p in segment]
				else:
					# Glyphs 2 code
					p0, p1, p2, p3 = [p.pointValue() for p in segment]
				chord = distance(p0, p3)
				cont_net = distance(p0, p1) + distance(p1, p2) + distance(p2, p3)
				return (cont_net + chord) * 0.5 * 0.996767352316
			else:
				return "Segment has unexpected point constellation (note: TT is not supported):\n    %s" % repr(segment)
		except Exception as e:  # noqa: F841
			print("SEGMENT:", segment)
			try:
				print("SEGMENT LENGTH:", len(segment))
			except:
				pass
			import traceback
			print(traceback.format_exc())
			return "Possible single-node path."

	def bezier(self, p1, p2, p3, p4, t):
		x1, y1 = p1.x, p1.y
		x2, y2 = p2.x, p2.y
		x3, y3 = p3.x, p3.y
		x4, y4 = p4.x, p4.y
		x = x1 * (1 - t)**3 + x2 * 3 * t * (1 - t)**2 + x3 * 3 * t**2 * (1 - t) + x4 * t**3
		y = y1 * (1 - t)**3 + y2 * 3 * t * (1 - t)**2 + y3 * 3 * t**2 * (1 - t) + y4 * t**3
		return NSPoint(x, y)

	def segmentMiddle(self, segment):
		if len(segment) == 2:
			p0, p1 = segment
			return NSPoint((p0.x + p1.x) * 0.5, (p0.y + p1.y) * 0.5)
		elif len(segment) == 4:
			p0, p1, p2, p3 = segment
			return self.bezier(p0, p1, p2, p3, 0.5)
		else:
			print("Segment has unexpected length:\n" + segment)
			return None

	def segmentsInLayerShorterThan(self, thisLayer, minLength=10.0):
		shortSegments = []
		for thisPath in thisLayer.paths:
			nodeCount = len(thisPath.nodes)
			if not nodeCount > 2:
				print("⚠️ WARNING: path with only %i point%s in %s (layer: %s). Skipping." % (
					nodeCount,
					"" if nodeCount == 1 else "s",
					thisLayer.parent.name,
					thisLayer.name,
				))
			else:
				for thisSegment in thisPath.segments:
					segmentLength = self.approxLengthOfSegment(thisSegment)
					if isinstance(segmentLength, (int, float)):
						if segmentLength < minLength:
							shortSegments.append(thisSegment)
					else:
						print("😬 ERROR in %s (layer: %s): %s" % (thisLayer.parent.name, thisLayer.name, segmentLength))
		return shortSegments

	def glyphInterpolation(self, thisGlyphName, thisInstance):
		"""
		Yields a layer.
		"""
		try:
			# calculate interpolation:
			interpolatedFont = thisInstance.pyobjc_instanceMethods.interpolatedFont()
			interpolatedLayer = interpolatedFont.glyphForName_(thisGlyphName).layers[0]

			# round to grid if necessary:
			if interpolatedLayer.paths:
				if interpolatedFont.gridLength == 1.0:
					interpolatedLayer.roundCoordinates()
				return interpolatedLayer
			else:
				return None
		except:
			import traceback
			print(traceback.format_exc())
			return None

	def addAnnotationTextAtPosition(self, layer, position, text):
		annotationText = GSAnnotation()
		annotationText.type = TEXT
		annotationText.position = position
		annotationText.text = text
		layer.annotations.append(annotationText)

	def cleanNodeNamesInGlyph(self, glyph, nodeMarker):
		for thisLayer in glyph.layers:
			# reset node names:
			for thisPath in thisLayer.paths:
				for thisNode in thisPath.nodes:
					if thisNode.name:
						if nodeMarker in thisNode.name:
							thisNode.name = None

			# delete possible annotation circles:
			annotations = thisLayer.annotations
			if annotations:
				for i in range(len(annotations))[::-1]:
					thisAnnotation = annotations[i]
					if thisAnnotation.text and nodeMarker in thisAnnotation.text:
						del thisLayer.annotations[i]

	def ShortSegmentFinderMain(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()
			# print(">> DEBUG CHECKPOINT 0")###DEBUG-DELETE LATER

			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			if self.pref("bringMacroWindowToFront"):
				Glyphs.showMacroWindow()
			# print(">> DEBUG CHECKPOINT 1")###DEBUG-DELETE LATER

			thisFont = Glyphs.font  # frontmost font
			print("Short Segments Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			# print(">> DEBUG CHECKPOINT 2")###DEBUG-DELETE LATER

			# query user settings:
			thisFont = Glyphs.font
			minLength = self.prefFloat("minSegmentLength")
			if self.pref("allGlyphs"):
				glyphsToProbe = thisFont.glyphs
			else:
				glyphsToProbe = [layer.parent for layer in thisFont.selectedLayers]
			# print(">> DEBUG CHECKPOINT 3")###DEBUG-DELETE LATER
			# lists for collecting affected and skipped glyphs:
			shortSegmentGlyphNames = []
			shortSegmentLayers = []
			skippedGlyphNames = []
			# numOfGlyphs = len(glyphsToProbe)
			for index, thisGlyph in enumerate(glyphsToProbe):
				print("i >", index)  # ##Delete
				# update progress bar:
				# print(">> DEBUG CHECKPOINT 4")  ###DEBUG-DELETE LATER
				# self.w.progress.set(int(100 * (float(index) / numOfGlyphs)))  ###UNHIDE?
				if thisGlyph.export or not self.pref("exportingOnly"):
					# print(">> DEBUG CHECKPOINT 5")###DEBUG-DELETE LATER
					# clean node markers if necessary:
					if self.pref("markSegments"):
						self.cleanNodeNamesInGlyph(thisGlyph, nodeMarker)
					# print(">> DEBUG CHECKPOINT 6")###DEBUG-DELETE LATER
					# find segments in masters:
					if self.pref("findShortSegmentsInMasters"):
						# print(">> DEBUG CHECKPOINT 7")###DEBUG-DELETE LATER
						for currentLayer in thisGlyph.layers:
							# print(">> DEBUG CHECKPOINT 8")###DEBUG-DELETE LATER
							# avoid potential troubles, just in case:
							if currentLayer is None:
								# print(">> DEBUG CHECKPOINT 9")###DEBUG-DELETE LATER
								break

							# check if it is a master or special layer, otherwise ignore:
							if currentLayer.associatedMasterId == currentLayer.layerId or currentLayer.isSpecialLayer:
								# print(">> DEBUG CHECKPOINT 10")###DEBUG-DELETE LATER
								shortSegments = self.segmentsInLayerShorterThan(currentLayer, minLength)
								if shortSegments:
									# print(">> DEBUG CHECKPOINT 11")###DEBUG-DELETE LATER
									print(
										"❌ %i short segment%s in %s, layer '%s'" % (
											len(shortSegments),
											"" if len(shortSegments) == 1 else "s",
											thisGlyph.name,
											currentLayer.name,
										)
									)
									# collect name:
									shortSegmentGlyphNames.append(thisGlyph.name)
									# print(">> DEBUG CHECKPOINT 12")###DEBUG-DELETE LATER
									# mark in canvas if required:
									if self.pref("markSegments"):
										# print(">> DEBUG CHECKPOINT 13")###DEBUG-DELETE LATER
										for shortSegment in shortSegments:
											# print(">> DEBUG CHECKPOINT 14")###DEBUG-DELETE LATER
											middleOfSegment = self.segmentMiddle(shortSegment)
											if not middleOfSegment:
												print(
													"⛔️ ERROR in %s, layer '%s'. Could not calculate center of segment:\n  %s" %
													(thisGlyph.name, currentLayer.name, repr(shortSegment))
												)
											else:
												annotationText = "↙︎%s %.1f" % (nodeMarker, self.approxLengthOfSegment(shortSegment))
												self.addAnnotationTextAtPosition(currentLayer, middleOfSegment, annotationText)

					# find segments in interpolations:
					else:
						for thisInstance in thisFont.instances:
							# print(">> DEBUG CHECKPOINT 15")###DEBUG-DELETE LATER
							# define instance name
							instanceName = thisInstance.name.strip()
							familyName = thisInstance.customParameters["familyName"]
							if familyName:
								# print(">> DEBUG CHECKPOINT 16")###DEBUG-DELETE LATER
								instanceName = "%s %s" % (familyName, instanceName)

							# interpolate glyph for this instance:
							interpolatedLayer = self.glyphInterpolation(thisGlyph.name, thisInstance)
							if not interpolatedLayer:
								# print(">> DEBUG CHECKPOINT 17")###DEBUG-DELETE LATER
								if self.pref("reportIncompatibilities"):
									# print(">> DEBUG CHECKPOINT 18")###DEBUG-DELETE LATER
									print("⚠️ %s: No paths in '%s'." % (thisGlyph.name, instanceName))
							else:
								interpolatedLayer.removeOverlap()
								# print(">> DEBUG CHECKPOINT 19")###DEBUG-DELETE LATER
								shortSegments = self.segmentsInLayerShorterThan(interpolatedLayer, minLength)
								# print(">> DEBUG CHECKPOINT 20")###DEBUG-DELETE LATER

								if shortSegments:
									# print(">> DEBUG CHECKPOINT 21")###DEBUG-DELETE LATER
									print(
										"❌ %i short segment%s in %s, instance '%s'" % (
											len(shortSegments),
											"" if len(shortSegments) == 1 else "s",
											thisGlyph.name,
											instanceName,
										)
									)

									# collect name:
									shortSegmentGlyphNames.append(thisGlyph.name)
									# mark in canvas if required:
									if self.pref("markSegments"):
										# print(">> DEBUG CHECKPOINT 22")###DEBUG-DELETE LATER
										for shortSegment in shortSegments:
											# print(">> DEBUG CHECKPOINT 23")###DEBUG-DELETE LATER
											middleOfSegment = self.segmentMiddle(shortSegment)
											if not middleOfSegment:
												print(
													"⛔️ ERROR in %s, layer '%s'. Could not calculate center of segment:\n  %s" %
													(thisGlyph.name, currentLayer.name, repr(shortSegment))
												)
											else:
												annotationText = "%s %.0f (%s)" % (nodeMarker, self.approxLengthOfSegment(shortSegment), instanceName)
												self.addAnnotationTextAtPosition(thisGlyph.layers[0], middleOfSegment, annotationText)

				else:
					# print(">> DEBUG CHECKPOINT 24")###DEBUG-DELETE LATER
					skippedGlyphNames.append(thisGlyph.name)

			# report skipped glyphs:
			if skippedGlyphNames:
				print("\nSkipped %i glyphs:\n%s" % (len(skippedGlyphNames), ", ".join(skippedGlyphNames)))

			# turn on View > Show Annotations:
			if self.pref("markSegments"):
				Glyphs.defaults["showAnnotations"] = 1

			# report affected glyphs:

			# found short segments in master layers > open these layers:
			if shortSegmentLayers:
				if self.pref("allGlyphs"):
					shortSegmentTab = thisFont.newTab()
					shortSegmentTab.layers = shortSegmentLayers
				else:
					Message(
						title="⚠️ Short Segments Found",
						message="Found segments shorter than %.1f units in %i layer%s in the selected glyph%s. Detailed report in Macro Window." % (
							minLength,
							len(shortSegmentLayers),
							"" if len(shortSegmentLayers) == 1 else "s",
							"" if len(glyphsToProbe) == 1 else "s",
						),
						OKButton="😲 OMG!"
					)

			# found short segments in interpolations > open the glyphs:
			elif shortSegmentGlyphNames:
				if self.pref("allGlyphs"):
					tabText = "/" + "/".join(set(shortSegmentGlyphNames))
					thisFont.newTab(tabText)
				else:
					Message(
						title="⚠️ Short Segments Found",
						message="Found segments shorter than %.1f units in %i selected glyph%s." % (
							minLength,
							len(shortSegmentGlyphNames),
							"" if len(shortSegmentGlyphNames) == 1 else "s",
						),
						OKButton="😲 OMG!"
					)
			else:
				Message(
					title="No Short Segments Found",
					message="Could not find any segments smaller than %.1f units in %s of %s. Congratulations." % (
						minLength,
						"master layers" if self.pref("findShortSegmentsInMasters") else "interpolations",
						thisFont.familyName,
					),
					OKButton=None,
				)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Short Segments Finder Error: %s" % e)
			import traceback
			print(traceback.format_exc())


ShortSegmentFinder()
