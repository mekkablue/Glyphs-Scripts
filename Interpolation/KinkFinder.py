#MenuTitle: Kink Finder
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds kinks in interpolation space, reports them in the Macro window and opens a new tab with affected glyphs.
"""

import vanilla
from Foundation import NSPoint
from math import hypot
tempMarker = "###DELETEME###"
nodeMarker = "⛔️"

def distanceBetweenPoints(node1, node2):
	return hypot(node1.x - node2.x, node1.y - node2.y)

def intersect(pointA, pointB, pointC, pointD):
	"""
	Returns an NSPoint of the intersection AB with CD,
	or None if there is no intersection.
	pointA, pointB: NSPoints representing the first line AB,
	pointC, pointD: NSPoints representing the second line CD.
	"""
	x1, y1 = pointA
	x2, y2 = pointB
	x3, y3 = pointC
	x4, y4 = pointD

	xtop = (x4 - x3) * (x2 * y1 - x1 * y2) - (x2 - x1) * (x4 * y3 - x3 * y4)
	ytop = (y1 - y2) * (x4 * y3 - x3 * y4) - (y3 - y4) * (x2 * y1 - x1 * y2)
	divisor = (y4 - y3) * (x2 - x1) - (y2 - y1) * (x4 - x3)

	x = xtop / divisor
	y = ytop / divisor

	return NSPoint(x, y)

def orthogonalDistance(pivot, A, B):
	try:
		x, y = subtractPoints(A, B)
		pivot2 = NSPoint(pivot.x + y, pivot.y - x)
		intersection = intersect(pivot, pivot2, A, B)
		return distanceBetweenPoints(intersection, pivot)
	except:
		import traceback
		print(traceback.format_exc())
		return 0

"""
g = Layer.parent
for i in range(0,105,5):
	inst = Font.instances[0]
	Font.instances[0].weightValue = 100.0+i
	l =	 glyphInterpolation( g.name, inst )
	p = l.paths[0]
	point = p.nodes[0]
	print i, orthogonalDistance(point.position, point.prevNode.position, point.nextNode.position)
"""

class KinkFinder(object):
	prefID = "com.mekkablue.KinkFinder"
	instances = None

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 265
		windowWidthResize = 100 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Kink Finder", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName="com.mekkablue.KinkFinder.mainwindow" # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox(
			(inset, linePos + 2, -inset, 30),
			"Find glyphs where kinks between triplets appear in interpolation, and the kink exceeds the given threshold size.",
			sizeStyle='small',
			selectable=True
			)
		linePos += lineHeight * 2

		self.w.text_1 = vanilla.TextBox((inset, linePos, 145, 14), "Acceptable max kink size:", sizeStyle='small')
		self.w.maxKinkSize = vanilla.EditText((inset + 145, linePos - 3, -inset, 19), "3", sizeStyle='small', callback=self.SavePreferences)
		self.w.maxKinkSize.getNSTextField().setToolTip_("Measured in units as the perpendicular distance between middle point and the line between first and third points.")
		linePos += lineHeight

		self.findKinksWhereOptions = (
			"between all masters (false positives with 6+ masters)",
			"between adjacent masters only (single axis, 3+ masters)",
			"in all current active instances",
			"in all current active and inactive instances",
			"in masters instead (not in interpolations)",
			)
		self.w.findKinksWhereText = vanilla.TextBox((inset, linePos + 2, 60, 14), "Find kinks", sizeStyle='small', selectable=True)
		self.w.findKinksWhere = vanilla.PopUpButton((inset + 60, linePos, -inset, 17), self.findKinksWhereOptions, sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		# self.w.betweenAdjacentMastersOnly.getNSButton().setToolTip_("If checked, will look for kinks between masters 0+1, 1+2, 1+3, but NOT between 0+2, 1+3 or 0+3. Makes sense if you have only one axis (e.g. weight) and more than two masters in interpolation order (lightest through boldest).")

		self.w.allGlyphs = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Process all glyphs in font (ignore selection)", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.allGlyphs.getNSButton().setToolTip_("If unchecked, will only process the current glyph(s).")
		linePos += lineHeight

		self.w.exportingOnly = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Ignore non-exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.exportingOnly.getNSButton().setToolTip_("If checked, will skip glyphs that do not export. Always skips compounds.")
		linePos += lineHeight

		self.w.markKinks = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Mark kinky nodes in first layer", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.markKinks.getNSButton().setToolTip_(
			"If checked, will mark affected nodes with a warning emoji and the maximum kink distance. Will mark the corresponding node in the first layer if it finds a kink in an instance. Will use an annotation if the node cannot be found (e.g. if the kink happens in a corner component)."
			)
		linePos += lineHeight

		self.w.reportIncompatibilities = vanilla.CheckBox(
			(inset, linePos - 1, 180, 20), "Also report incompatibilities", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.reportIncompatibilities.getNSButton(
		).setToolTip_("If checked, will warn about incompatibilities. Usually you want this off, especially when you have bracket layers.")

		self.w.bringMacroWindowToFront = vanilla.CheckBox(
			(inset + 180, linePos - 1, -inset, 20), "Macro Window to front", value=True, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.bringMacroWindowToFront.getNSButton().setToolTip_(
			"A detailed report is written to the Macro Window. Activate this check box, and the Macro Window will be brought to the front ever time you run this script."
			)
		linePos += lineHeight

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Open Tab", sizeStyle='regular', callback=self.KinkFinderMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ Warning: 'Kink Finder' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def adaptUItext(self, sender):
		# 0: between all masters (false positives with 6+ masters)
		# 1: between adjacent masters only (single axis, 3+ masters)
		# 2: in all current active instances
		# 3: in all current active and inactive instances
		# 4: in masters instead (not in interpolations)

		if self.pref("findKinksWhere") == 4:
			self.w.markKinks.setTitle("Mark kinky nodes")
		else:
			self.w.markKinks.setTitle("Mark kinky nodes in first layer")

		if Glyphs.defaults["com.mekkablue.KinkFinder.allGlyphs"]:
			self.w.runButton.setTitle("Open Tab")
		else:
			self.w.runButton.setTitle("Find Kinks")

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()

	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]

	def SavePreferences(self, sender=None):
		try:
			Glyphs.defaults[self.domain("maxKinkSize")] = self.w.maxKinkSize.get()
			Glyphs.defaults[self.domain("allGlyphs")] = self.w.allGlyphs.get()
			Glyphs.defaults[self.domain("exportingOnly")] = self.w.exportingOnly.get()
			Glyphs.defaults[self.domain("markKinks")] = self.w.markKinks.get()
			Glyphs.defaults[self.domain("findKinksWhere")] = self.w.findKinksWhere.get()
			Glyphs.defaults[self.domain("reportIncompatibilities")] = self.w.reportIncompatibilities.get()
			Glyphs.defaults[self.domain("bringMacroWindowToFront")] = self.w.bringMacroWindowToFront.get()
			Glyphs.defaults[self.domain("betweenAdjacentMastersOnly")] = self.w.betweenAdjacentMastersOnly.get()
			self.adaptUItext(sender)
		except:
			return False

		return True

	def LoadPreferences(self, sender=None):
		try:
			Glyphs.registerDefault(self.domain("maxKinkSize"), 0.9)
			Glyphs.registerDefault(self.domain("allGlyphs"), 0)
			Glyphs.registerDefault(self.domain("exportingOnly"), 1)
			Glyphs.registerDefault(self.domain("markKinks"), 0)
			Glyphs.registerDefault(self.domain("findKinksWhere"), 0)
			Glyphs.registerDefault(self.domain("reportIncompatibilities"), 0)
			Glyphs.registerDefault(self.domain("reportIncompatibilities"), 0)
			Glyphs.registerDefault(self.domain("reportIncompatibilities"), 0)
			self.w.maxKinkSize.set(self.pref("maxKinkSize"))
			self.w.allGlyphs.set(self.pref("allGlyphs"))
			self.w.exportingOnly.set(self.pref("exportingOnly"))
			self.w.markKinks.set(self.pref("markKinks"))
			self.w.findKinksWhere.set(self.pref("findKinksWhere"))
			self.w.reportIncompatibilities.set(self.pref("reportIncompatibilities"))
			self.w.bringMacroWindowToFront.set(self.pref("bringMacroWindowToFront"))
			self.w.betweenAdjacentMastersOnly.set(self.pref("betweenAdjacentMastersOnly"))

			# update UI:
			self.adaptUItext(sender)
		except:

			return False

		return True

	def kinkSizeForNode(self, kinkNode):
		#print "node nr.", kinkNode.index, "pos:", kinkNode.position, "handles:", kinkNode.prevNode.type, kinkNode.nextNode.type
		return orthogonalDistance(kinkNode.position, kinkNode.prevNode.position, kinkNode.nextNode.position)

	def glyphInterpolation(self, thisGlyphName, thisInstance):
		"""
		Yields a layer.
		"""
		try:
			# calculate interpolation:
			if Glyphs.versionNumber >= 3.2:
				interpolatedFont = thisInstance.interpolatedFontProxy
			else:
				interpolatedFont = thisInstance.interpolatedFontProxy()
			interpolatedLayer = interpolatedFont.glyphs[thisGlyphName].layers[0]

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

	def buildInstance(self, name, interpolationDict, font):
		instance = GSInstance()
		if Glyphs.buildNumber>3198:
			instance.exports = False
		else:
			instance.active = False
		instance.name = name
		instance.manualInterpolation = True
		instance.instanceInterpolations = interpolationDict
		if font:
			instance.setFont_(font)
		return instance

	def buildHalfWayInstances(self, thisFont):
		# 0: between all masters (false positives with 6+ masters)
		# 1: between adjacent masters only (single axis, 3+ masters)
		# 2: in all current active instances
		# 3: in all current active and inactive instances
		# 4: in masters instead (not in interpolations)
		self.instances = []
		findKinksWhere = self.pref("findKinksWhere")
		if findKinksWhere in (2, 3):
			for i, thisInstance in enumerate(thisFont.instances):
				if Glyphs.buildNumber>3198:
					instanceIsExporting = thisInstance.exports
				else:
					instanceIsExporting = thisInstance.active
				if instanceIsExporting or findKinksWhere == 3:
					interpolationDict = thisInstance.instanceInterpolations
					instanceName = "%03i-%s-%s" % (i, thisInstance.name, tempMarker)
					testInstance = self.buildInstance(instanceName, interpolationDict, thisFont)
					self.instances.append(testInstance)
		elif findKinksWhere == 4:
			for i, m in enumerate(thisFont.masters):
				interpolationDict = {
					m.id: 1.0
					}
				instanceName = "%03i-%s" % (i, tempMarker)
				testInstance = self.buildInstance(instanceName, interpolationDict, thisFont)
				if Glyphs.versionNumber >= 3: # GLYPHS 3
					testInstance.axes = m.axes
				self.instances.append(testInstance)
		else:
			betweenAdjacentMastersOnly = findKinksWhere == 1
			numOfMasters = len(thisFont.masters)
			r = range(numOfMasters)
			for i in r[:-1]:
				for j in r[i + 1:]:
					if abs(i - j) == 1 or not betweenAdjacentMastersOnly:
						master1 = thisFont.masters[i]
						master2 = thisFont.masters[j]
						interpolationDict = {
							master1.id: 0.5,
							master2.id: 0.5
							}
						instanceName = "%i-%i-%s" % (i, j, tempMarker)
						testInstance = self.buildInstance(instanceName, interpolationDict, thisFont)

						# disable other masters:
						disabledMasters = []
						for m in range(len(thisFont.masters)):
							if m != i and m != j:
								disabledMasters.append(thisFont.masters[m].name)
						if disabledMasters:
							disabledMasters = tuple(disabledMasters)
							testInstance.customParameters["Disable Masters"] = disabledMasters

						# collect the instance in self.instance:
						self.instances.append(testInstance)

		# report:
		print("Testing in %i instances:" % len(self.instances))
		for i in self.instances:
			print("- %s:" % i.name)
			for key in i.instanceInterpolations.keys():
				print("  %s: %.3f" % (
					thisFont.masters[key].name,
					i.instanceInterpolations[key],
					))
		print()

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

	def addAnnotationAtPosition(self, layer, position, width=25.0):
		circle = GSAnnotation()
		circle.type = CIRCLE
		circle.position = position
		circle.width = width
		circle.text = nodeMarker
		layer.annotations.append(circle)

	def markNodeAtPosition(self, layer, position, nodeName):
		# first all green (smooth) points, then all blue points:
		for considerOnlySmooth in (True, False):
			for thisPath in layer.paths:
				for thisNode in thisPath.nodes:
					if (thisNode.connection == GSSMOOTH and considerOnlySmooth) or (thisNode.connection != GSSMOOTH and not considerOnlySmooth):
						if thisNode.position == position:
							thisNode.name = nodeName
							return

		# no node found in paths, kinky node is likely in a corner component:
		self.addAnnotationAtPosition(layer, position)

	def KinkFinderMain(self, sender):
		try:
			if not self.SavePreferences(self):
				print("Note: 'Kink Finder' could not write preferences.")

			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			if self.pref("bringMacroWindowToFront"):
				Glyphs.showMacroWindow()

			# query user settings:
			thisFont = Glyphs.font
			maxKink = float(self.pref("maxKinkSize"))
			kinkyGlyphNames = []
			kinkyLayers = []
			if self.pref("allGlyphs"):
				glyphsToProbe = thisFont.glyphs
			else:
				glyphsToProbe = [l.parent for l in thisFont.selectedLayers]

			# prepare instances:
			findKinksInMastersInstead = self.pref("findKinksWhere") == 4
			if not findKinksInMastersInstead:
				self.buildHalfWayInstances(thisFont)

				# instance for first layer:
				firstInstanceInterpolationDict = {
					thisFont.masters[0].id: 1.0
					}
				firstInstanceName = "First Master-%s" % tempMarker
				firstInstance = self.buildInstance(firstInstanceName, firstInstanceInterpolationDict, thisFont)
			else:
				firstInstance = None

			skippedGlyphNames = []
			numOfGlyphs = len(glyphsToProbe)
			for index, thisGlyph in enumerate(glyphsToProbe):
				# update progress bar:
				self.w.progress.set(int(100 * (float(index) / numOfGlyphs)))
				if thisGlyph.export or not self.pref("exportingOnly"):

					# clean node markers if necessary:
					if self.pref("markKinks"):
						self.cleanNodeNamesInGlyph(thisGlyph, nodeMarker)

					# find kinks in masters:
					if findKinksInMastersInstead:
						for kinkLayer in thisGlyph.layers:

							# avoid potential troubles, just in case:
							if kinkLayer is None:
								break

							# check if it is a master or special layer, otherwise ignore:
							if kinkLayer.associatedMasterId == kinkLayer.layerId or kinkLayer.isSpecialLayer:
								for pathIndex, kinkPath in enumerate(kinkLayer.paths):
									if not kinkPath:
										print("❌ Could not determine same path in glyph %s, master %s." % (thisGlyph.name, thisMaster.name))
									else:
										for nodeIndex, kinkNode in enumerate(kinkPath.nodes):
											if kinkNode.connection == GSSMOOTH:
												thisKink = self.kinkSizeForNode(kinkNode)
												if thisKink > maxKink:
													if not kinkLayer in kinkyLayers:
														kinkyLayers.append(kinkLayer)
													# kinkyGlyphNames.append(thisGlyph.name)
													print(
														"%s Kink in %s on layer '%s', path %i, node %i: %.1f units" %
														(nodeMarker, thisGlyph.name, kinkLayer.name, pathIndex, nodeIndex, thisKink)
														)
													if self.pref("markKinks"):
														kinkNode.name = "%.1f %s" % (thisKink, nodeMarker)

					# TODO find kinks in interpolations (needs rewrite):
					else:
						if not thisGlyph.layers[0].paths:
							skippedGlyphNames.append(thisGlyph.name)
						else:
							firstLayer = self.glyphInterpolation(thisGlyph.name, firstInstance)
							if not firstLayer:
								print("⚠️ Could not determine primary layer of %s, most likely cause: no paths." % thisGlyph.name)
							else:
								for pathIndex in range(len(firstLayer.paths)):
									thisPath = firstLayer.paths[pathIndex]
									for nodeIndex in range(len(thisPath.nodes)):
										thisNode = thisPath.nodes[nodeIndex]
										if thisNode.connection == GSSMOOTH:
											thisNodeMaxKink = 0
											for thisInstance in self.instances:
												kinkLayer = self.glyphInterpolation(thisGlyph.name, thisInstance)
												if not kinkLayer:
													if self.pref("reportIncompatibilities"):
														print(
															"⚠️ ERROR: Could not calculate interpolation for: %s (%s)" %
															(thisGlyph.name, thisInstance.name.replace(tempMarker, ""))
															)
												elif not thisGlyph.mastersCompatibleForLayers_((firstLayer, kinkLayer)):
													if self.pref("reportIncompatibilities"):
														print(
															"⚠️ interpolation incompatible for glyph %s: %s (most likely cause: cap or corner components, bracket layers)" %
															(thisGlyph.name, thisInstance.name.replace(tempMarker, ""))
															)
														print(firstLayer, firstLayer.shapes, firstLayer.anchors)
														print(kinkLayer, kinkLayer.shapes, kinkLayer.anchors)
												else:
													kinkNode = kinkLayer.paths[pathIndex].nodes[nodeIndex]
													thisKink = self.kinkSizeForNode(kinkNode)

													# kink is found:
													if thisKink > maxKink:
														kinkyGlyphNames.append(thisGlyph.name)
														print(
															"%s Kink in %s between masters %s, path %i, node %i: %.1f units (%.1f, %.1f)" % (
																nodeMarker, thisGlyph.name, " and ".join(thisInstance.name.split("-")[:2]
																											), pathIndex, nodeIndex, thisKink, thisNode.x, thisNode.y
																)
															)

														if self.pref("markKinks"):
															if thisKink > thisNodeMaxKink:
																thisNodeMaxKink = thisKink
															nodeName = "%.1f %s" % (thisNodeMaxKink, nodeMarker)
															self.markNodeAtPosition(thisGlyph.layers[0], thisNode.position, nodeName)

										elif self.pref("markKinks"):
											thisNode.name = None
				else:
					skippedGlyphNames.append(thisGlyph.name)

			# Progress bar 100%
			self.w.progress.set(100.0)

			if skippedGlyphNames:
				print("\nSkipped %i glyphs:\n%s" % (len(skippedGlyphNames), ", ".join(skippedGlyphNames)))
			uniqueKinkyGlyphNames = set(kinkyGlyphNames)

			if kinkyLayers:
				kinkyTab = thisFont.newTab()
				kinkyTab.layers = kinkyLayers
			elif uniqueKinkyGlyphNames:
				tabText = "/" + "/".join(uniqueKinkyGlyphNames)
				thisFont.newTab(tabText)
			else:
				Message(
					title="No Kinks Found 🎉",
					message="Could not find any kinks larger than %.1f units in %s of %s. Congratulations!" % (
						maxKink,
						"master layers" if findKinksInMastersInstead else "interpolations",
						thisFont.familyName,
						),
					OKButton="🥂 Cheers!",
					)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Kink Finder Error: %s" % e)
			import traceback
			print(traceback.format_exc())

KinkFinder()
