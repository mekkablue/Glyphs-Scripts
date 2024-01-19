# MenuTitle: Add Grade
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__ = """
Add Grade axis and/or Grade master, based on your Weight and Width axes.
"""

import vanilla
from AppKit import NSAffineTransform, NSPoint
from copy import copy
from GlyphsApp import Glyphs, GSInstance, GSUppercase, GSSmallcaps, GSSMOOTH, GSOFFCURVE, GSAxis, GSCustomParameter, Message
from mekkablue import mekkaObject


def axisIdForTag(font, tag="wght"):
	for i, a in enumerate(font.axes):
		if a.axisTag == tag:
			return i
	return None


def realWeight(font, referenceGlyph="idotless", masterIndex=0):
	glyph = font.glyphs[referenceGlyph]
	if not glyph:
		return None

	layer = glyph.layers[masterIndex]
	midY = layer.bounds.origin.y + layer.bounds.size.height / 2
	intersections = layer.intersectionsBetweenPoints(
		NSPoint(layer.bounds.origin.x - 100, midY),
		NSPoint(layer.bounds.origin.x + layer.bounds.size.width + 100, midY),
	)
	p1 = intersections[1]
	p2 = intersections[-2]
	actualWidth = p2.x - p1.x
	return actualWidth


def hScaleLayer(layer, hFactor=1.0):
	xScale = NSAffineTransform.transform()
	xScale.scaleXBy_yBy_(hFactor, 1.0)
	layer.applyTransform(xScale.transformStruct())


def anisotropicAdjust(font, master, originMaster, scope=[]):
	font = Glyphs.font

	wghtAxisIndex = axisIdForTag(font, "wght")
	wghtInstanceAxes = list(master.axes)

	# current master weight
	currentWght = master.axes[wghtAxisIndex]
	currentWghtInstance = GSInstance()
	currentWghtInstance.font = font
	currentWghtInstance.axes = wghtInstanceAxes
	currentWghtFont = currentWghtInstance.interpolatedFont
	currentRealWght = realWeight(currentWghtFont)
	currentRealWghtUC = realWeight(currentWghtFont, referenceGlyph="I")
	currentRealWghtSC = realWeight(currentWghtFont, referenceGlyph="i.sc")

	for glyph in font.glyphs:
		if glyph.name not in scope:
			continue
		layer = glyph.layers[master.id]
		originLayer = glyph.layers[originMaster.id]

		# skip glyphs where we do not make adjustments
		if layer.width == 0 or originLayer.width == 0 or layer.width == originLayer.width:
			continue

		# reference weight for measuring the span of an axis
		hScale = originLayer.width / layer.width
		wghtScale = 1 / hScale
		refWght = currentWght * wghtScale
		wghtInstanceAxes[wghtAxisIndex] = refWght
		refWghtInstance = GSInstance()
		refWghtInstance.font = font
		refWghtInstance.axes = wghtInstanceAxes
		refWghtFont = refWghtInstance.interpolatedFont

		# CASE
		if glyph.case == GSUppercase:
			wghtCorrection = currentRealWghtUC / realWeight(refWghtFont, referenceGlyph="I")
		elif glyph.case == GSSmallcaps:
			wghtCorrection = currentRealWghtSC / realWeight(refWghtFont, referenceGlyph="i.sc")
		else:
			wghtCorrection = currentRealWght / realWeight(refWghtFont)

		wghtCorrected = currentWght + (refWght - currentWght) * wghtCorrection
		wghtInstanceAxes[wghtAxisIndex] = wghtCorrected
		wghtInstance = GSInstance()
		wghtInstance.font = font
		wghtInstance.axes = wghtInstanceAxes
		wghtFont = wghtInstance.interpolatedFont

		wghtLayer = wghtFont.glyphs[glyph.name].layers[0]
		for i, path in enumerate(wghtLayer.paths):
			for j, node in enumerate(path.nodes):
				originalNode = layer.paths[i].nodes[j]
				node.y = originalNode.y

		hScaleLayer(wghtLayer, hScale)
		layer.shapes = copy(wghtLayer.shapes)
		layer.width *= hScale

		# realign handles
		straightenBCPs(layer)


def fitSidebearings(layer, targetWidth, left=0.5):
	if not layer.shapes:
		layer.width = targetWidth
	else:
		diff = targetWidth - layer.width
		diff *= left
		layer.LSB += diff
		layer.width = targetWidth


def wdthAdjust(font, gradeMaster, baseMaster, scope=[]):
	wdthAxisIndex = axisIdForTag(font, "wdth")
	if wdthAxisIndex is None:
		print("⚠️ No wdth axis found. Widths not fitted.")
		Message(
			title="No Width Axis",
			message=f"Advance widths could not be fitted to those of master ‘{baseMaster.name}’ because there is no wdth axis. Remove the graded master ‘{gradeMaster.name}’ and try again.",
			OKButton=None,
		)

	baseWdthValue = baseMaster.axes[wdthAxisIndex]
	gradeWdthValue = gradeMaster.axes[wdthAxisIndex]
	wdthValues = sorted(
		set([m.axes[wdthAxisIndex] for m in font.masters if m.axes[wdthAxisIndex] != baseWdthValue])
	)
	if not wdthValues:
		print("⚠️ No wdth interpolation found. Widths not fitted.")
		Message(
			title="No Width Interpolation",
			message=f"Advance widths could not be fitted to those of master ‘{baseMaster.name}’ because there is no interpolation along the wdth axis. Remove the graded master ‘{gradeMaster.name}’ and try again.",
			OKButton=None,
		)

	refWdthValue = wdthValues[0]
	refInstance = GSInstance()
	refInstance.font = font
	refInstance.axes = copy(gradeMaster.axes)
	refInstance.axes[wdthAxisIndex] = refWdthValue
	refFont = refInstance.interpolatedFont

	for glyph in font.glyphs:
		if glyph.name not in scope:
			continue
		gradeLayer = glyph.layers[gradeMaster.id]
		baseLayer = glyph.layers[baseMaster.id]
		if gradeLayer.width == baseLayer.width:
			# skip if width is OK already
			continue

		refLayer = refFont.glyphs[glyph.name].layers[0]
		if refLayer.width == gradeLayer.width or not gradeLayer.shapes:
			# width cannot be interpolated, so just fix SBs:
			fitSidebearings(gradeLayer, targetWidth=baseLayer)
			print(f"⚠️ could not interpolate wdth, just fitted SBs: {glyph.name}")
			continue

		# calculate and interpolate wdth variation
		wdthFactor = (baseLayer.width - refLayer.width) / (gradeLayer.width - refLayer.width)
		wdthValue = refWdthValue + wdthFactor * (gradeWdthValue - refWdthValue)
		print(wdthValue, glyph.name)
		wdthInstance = GSInstance()
		wdthInstance.font = font
		wdthInstance.axes = copy(gradeMaster.axes)
		wdthInstance.axes[wdthAxisIndex] = wdthValue
		wdthFont = wdthInstance.interpolatedFont
		wdthLayer = wdthFont.glyphs[glyph.name].layers[0]

		# copy it back to the target layer
		gradeLayer.shapes = copy(wdthLayer.shapes)
		gradeLayer.anchors = copy(wdthLayer.anchors)
		gradeLayer.hints = copy(wdthLayer.hints)
		gradeLayer.width = wdthLayer.width

		# realign handles
		straightenBCPs(gradeLayer)


def straightenBCPs(layer):
	def closestPointOnLine(P, A, B):
		# vector of line AB
		AB = NSPoint(B.x - A.x, B.y - A.y)
		# vector from point A to point P
		AP = NSPoint(P.x - A.x, P.y - A.y)
		# dot product of AB and AP
		dotProduct = AB.x * AP.x + AB.y * AP.y
		ABsquared = AB.x**2 + AB.y**2
		t = dotProduct / ABsquared
		x = A.x + t * AB.x
		y = A.y + t * AB.y
		return NSPoint(x, y)

	def ortho(n1, n2):
		xDiff = n1.x - n2.x
		yDiff = n1.y - n2.y
		# must not have the same coordinates,
		# and either vertical or horizontal:
		if xDiff != yDiff and xDiff * yDiff == 0.0:
			return True
		return False

	for p in layer.paths:
		for n in p.nodes:
			if n.connection != GSSMOOTH:
				continue
			nn, pn = n.nextNode, n.prevNode
			if all((nn.type == GSOFFCURVE, pn.type == GSOFFCURVE)):
				# surrounding points are BCPs
				smoothen, center, opposite = None, None, None
				for handle in (nn, pn):
					if ortho(handle, n):
						center = n
						opposite = handle
						smoothen = nn if nn != handle else pn
						p.setSmooth_withCenterNode_oppositeNode_(
							smoothen, center, opposite,
						)
						break
				if smoothen is None and center is None and opposite is None:
					n.position = closestPointOnLine(
						n.position, nn, pn,
					)
			elif n.type != GSOFFCURVE and (nn.type, pn.type).count(GSOFFCURVE) == 1:
				# only one of the surrounding points is a BCP
				center = n
				if nn.type == GSOFFCURVE:
					smoothen = nn
					opposite = pn
				elif pn.type == GSOFFCURVE:
					smoothen = pn
					opposite = nn
				else:
					continue  # should never occur
				p.setSmooth_withCenterNode_oppositeNode_(
					smoothen, center, opposite,
				)


class AddGrade(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"baseMaster": 0,
		"axisName": "Grade",
		"axisTag": "GRAD",
		"grade": 50,
		"weight": 100,
		"addSyncMetricCustomParameter": 1,
		"fittingMethod": 0,
		"limitToSelectedGlyphs": 0,
	}

	refittingMethods = (
		"Adjust advance width: LSB 50%, RSB 50%",
		"Adjust advance width: keep current SB proportions",
		"Anisotropic wght interpolation (slow, requires I and idotless)",
		"Isotropic wdth interpolation (slow, requires wdth axis)",
	)

	def __init__(self):
		# Window 'self.w':
		windowWidth = 440
		windowHeight = 230
		windowWidthResize = 200  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Add Grade",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow"),  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		indent = 100

		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Add Grade master (and if necessary Grade axis):", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.baseMasterText = vanilla.TextBox((inset, linePos + 3, indent, 14), "Based on master:", sizeStyle="small", selectable=True)
		self.w.baseMaster = vanilla.PopUpButton((inset + indent, linePos, -inset - 25, 17), self.mastersOfCurrentFont(), sizeStyle="small", callback=self.SavePreferences)
		self.w.updateBaseMaster = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle="small", callback=self.updateUI)
		linePos += lineHeight

		self.w.weightText = vanilla.TextBox((inset, linePos + 3, indent, 14), "Use coordinate:", sizeStyle="small", selectable=True)
		self.w.weight = vanilla.ComboBox((inset + indent, linePos - 1, -inset - 25, 19), self.weightValuesForCurrentFont(), sizeStyle="small", callback=self.SavePreferences)
		self.w.updateWeight = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle="small", callback=self.updateUI)
		linePos += lineHeight

		self.w.gradeText = vanilla.TextBox((inset, linePos + 3, indent, 14), "… for grade:", sizeStyle="small", selectable=True)
		self.w.grade = vanilla.ComboBox((inset + indent, linePos - 1, 55, 19), ("-50", "0", "50"), sizeStyle="small", callback=self.SavePreferences)
		self.w.axisTagText = vanilla.TextBox((inset + indent + 65, linePos + 3, indent, 14), "Axis tag & name:", sizeStyle="small", selectable=True)
		self.w.axisTag = vanilla.EditText((inset + indent * 2 + 60, linePos, 45, 19), "GRAD", callback=self.SavePreferences, sizeStyle="small")
		self.w.axisName = vanilla.EditText((inset + indent * 2 + 110, linePos, -inset - 25, 19), "Grade", callback=self.SavePreferences, sizeStyle="small")
		self.w.axisReset = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle="small", callback=self.updateUI)
		linePos += lineHeight + 10

		indent = 45
		self.w.fittingMethodText = vanilla.TextBox((inset, linePos + 3, indent, 14), "Fitting:", sizeStyle="small", selectable=True)
		self.w.fittingMethod = vanilla.PopUpButton((inset + indent, linePos + 1, -inset, 17), self.refittingMethods, sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight

		self.w.addSyncMetricCustomParameter = vanilla.CheckBox((inset + indent, linePos - 1, -inset, 20), "Add custom parameter ‘Link Metrics With Master’ (recommended)", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight + 5

		self.w.limitToSelectedGlyphs = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Limit to selected glyphs", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		# self.w.useWdthAxis = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Use Width axis for fitting grade layer width", value=False, callback=self.SavePreferences, sizeStyle="small")
		# linePos += lineHeight
		#
		# self.w.useWdthAxis.enable(False)

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Add Master", sizeStyle="regular", callback=self.AddGradeMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def mastersOfCurrentFont(self, sender=None):
		masterMenu = []
		font = Glyphs.font
		if font:
			for i, master in enumerate(font.masters):
				masterMenu.append(f"{i + 1}. {master.name}: {self.masterAxesString(master)}")
		return masterMenu

	def weightValuesForCurrentFont(self, sender=None):
		# presets for the combo box
		weightValues = []
		font = Glyphs.font
		if font:
			wghtAxis = font.axisForTag_("wght")
			if wghtAxis:
				axisID = wghtAxis.id
				for m in font.masters + font.instances:
					value = f"wght={m.axisValueValueForId_(axisID)}"
					if value not in weightValues:
						weightValues.append(value)
			for m in font.masters + font.instances:
				value = self.masterAxesString(m)
				if value not in weightValues:
					weightValues.append(value)
		return sorted(weightValues)

	def masterAxesString(self, master):
		font = master.font
		return ", ".join([f"{a.axisTag}={master.axes[i]}" for i, a in enumerate(font.axes)])

	def updateUI(self, sender=None):
		font = Glyphs.font
		if sender == self.w.updateWeight:
			# get current master:
			masterIndex = self.w.baseMaster.get()
			master = font.masters[masterIndex]
			self.w.weight.set(self.masterAxesString(master))
		elif sender == self.w.updateBaseMaster:
			self.w.baseMaster.setItems(self.mastersOfCurrentFont())
		elif sender == self.w.axisReset:
			self.w.axisTag.set("GRAD")
			self.w.axisName.set("Grade")
		self.SavePreferences()

	def AddGradeMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			fittingMethod = self.prefInt("fittingMethod")
			limitToSelectedGlyphs = self.prefBool("limitToSelectedGlyphs")

			thisFont = Glyphs.font  # frontmost font
			if limitToSelectedGlyphs:
				glyphNames = [layer.parent.name for layer in thisFont.selectedLayers]
			else:
				glyphNames = [g.name for g in thisFont.glyphs]

			if thisFont is None:
				Message(
					title="No Font Open",
					message="The script requires a font with a weight axis. Open a font and run the script again.",
					OKButton=None,
				)
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Add Grade Report for {reportName}")
				print()

				axisName = self.pref("axisName").strip()
				axisTag = f'{self.pref("axisTag").strip()[:4]:4}'
				existingAxisTags = [a.axisTag for a in thisFont.axes]
				if axisTag not in existingAxisTags:
					print(f"Adding axis ‘{axisName}’ ({axisTag})")
					gradeAxis = GSAxis()
					gradeAxis.name = axisName
					gradeAxis.axisTag = axisTag
					gradeAxis.hidden = False
					thisFont.axes.append(gradeAxis)
					thisFont.didChangeValueForKey_("axes")
				else:
					gradeAxis = thisFont.axisForTag_(axisTag)
					if gradeAxis.name != axisName:
						print(f"Updating {axisTag} axis name: {gradeAxis.name} → {axisName}")
						gradeAxis.name = axisName

				baseMaster = thisFont.masters[self.pref("baseMaster")]
				grade = self.prefInt("grade")
				gradeMaster = copy(baseMaster)
				gradeMaster.name = f"{baseMaster.name} Grade {grade}"
				gradeMaster.font = thisFont
				gradeMaster.setAxisValueValue_forId_(grade, gradeAxis.id)

				# work font = font without graded master,
				# because it influences interpolation otherwise
				workFont = copy(thisFont)
				for m in workFont.masters[::-1]:
					if m.axes == gradeMaster.axes:
						workFont.removeFontMaster_(m)

				if self.pref("addSyncMetricCustomParameter"):
					linkMasterParameter = GSCustomParameter(
						"Link Metrics With Master", baseMaster.id
					)
					gradeMaster.customParameters.append(linkMasterParameter)

				# use existing master if there is one, and
				# discard the gradeMaster we started building above:
				existingMaster = False
				for m in thisFont.masters[::-1]:
					if m.axes == gradeMaster.axes:
						if existingMaster or not limitToSelectedGlyphs:
							# remove preexisting graded masters if there are any
							print(f"❌ Removing preexisting graded master ‘{m.name}’")
							thisFont.removeFontMaster_(m)
						else:
							# keep master if we only reinterpolate some glyphs
							m.name = gradeMaster.name
							gradeMaster = m
							existingMaster = True

				# otherwise add the one we built above:
				if not existingMaster:
					print(f"Ⓜ️ Adding master: ‘{gradeMaster.name}’")
					thisFont.masters.append(gradeMaster)
					thisFont.didChangeValueForKey_("fontMasters")

				# make grade interpolation in workFont
				gradeInstance = GSInstance()
				gradeInstance.font = workFont  # the font that does not have the graded master yet
				gradeInstance.name = "###DELETEME###"
				gradeInstance.axes = baseMaster.axes

				# parse user input for graded designspace coordinate:
				for valuePair in self.pref("weight").strip().split(","):
					tag, axisValue = valuePair.split("=")
					tag = tag.strip()
					axisValue = float(axisValue.strip())
					axisID = axisIdForTag(workFont, tag)
					gradeInstance.axes[axisID] = axisValue
				print(f"🛠️ Interpolating grade: {self.masterAxesString(gradeInstance)}")

				# interpolate the grade:
				gradeFont = gradeInstance.interpolatedFont
				for glyphName in glyphNames:
					weightedGlyph = gradeFont.glyphs[glyphName]
					weightedLayer = weightedGlyph.layers[0]
					weightedWidth = weightedLayer.width

					baseGlyph = thisFont.glyphs[glyphName]
					baseLayer = baseGlyph.layers[baseMaster.id]
					baseWidth = baseLayer.width

					# adjust width by methods 0 and 1:
					if weightedWidth != baseWidth and fittingMethod < 2:
						if fittingMethod == 1 and (weightedLayer.LSB + weightedLayer.RSB != 0):
							lsbPercentage = weightedLayer.LSB / (
								weightedLayer.LSB + weightedLayer.RSB
							)
						else:
							lsbPercentage = 0.5
						fitSidebearings(weightedLayer, targetWidth=baseWidth, left=lsbPercentage)

					# bring the interpolated shapes back into the open font:
					gradeLayer = baseGlyph.layers[gradeMaster.id]
					gradeLayer.width = weightedLayer.width
					gradeLayer.shapes = copy(weightedLayer.shapes)
					gradeLayer.anchors = copy(weightedLayer.anchors)
					gradeLayer.hints = copy(weightedLayer.hints)

				# adjust widths by methods 2 and 3:
				if fittingMethod == 2:
					# adjust width anisotropically:
					print(
						f"↔️ Fitting {len(glyphNames)} glyph{'' if len(glyphNames) == 1 else 's'} anisotropically..."
					)
					anisotropicAdjust(thisFont, gradeMaster, baseMaster, scope=glyphNames)
				elif fittingMethod == 3:
					# adjust width with wdth axis:
					print(
						f"↔️ Fitting {len(glyphNames)} glyph{'' if len(glyphNames) == 1 else 's'} through the width axis..."
					)
					wdthAdjust(thisFont, gradeMaster, baseMaster, scope=glyphNames)

				# add missing axis locations if base master has axis locations:
				if Glyphs.versionNumber < 4:
					print("📐 Updating Axis Locations in masters...")
					for thisMaster in thisFont.masters:
						axLoc = thisMaster.customParameters["Axis Location"]
						if axLoc and len(axLoc) < len(thisFont.axes):
							axLoc.append(
								{
									"Axis": self.pref("axisName"),
									"Location": thisMaster.axisValueValueForId_(gradeAxis.id),
								}
							)
							thisMaster.customParameters["Axis Location"] = axLoc

					print("📐 Updating Axis Locations in instances...")
					for thisInstance in thisFont.instances:
						axLoc = thisInstance.customParameters["Axis Location"]
						if axLoc and len(axLoc) < len(thisFont.axes):
							axLoc = list(axLoc)
							axLoc.append(
								{
									"Axis": self.pref("axisName"),
									"Location": thisInstance.axisValueValueForId_(gradeAxis.id),
								}
							)
							thisInstance.customParameters["Axis Location"] = axLoc
						# Glyphs 4:
						# thisMaster.setExternAxisValueValue_forId_(thisMaster.axisValueValueForId_(gradeID), gradeID)
						# thisMaster.externalAxesValues[gradeID] = thisMaster.internalAxesValues[gradeID]

					# update Axis Locations in Virtual Masters if there are any:
					for parameter in thisFont.customParameters:
						if parameter.name == "Virtual Master":
							print("Updating Virtual Master...")
							axLoc = parameter.value
							if len(axLoc) < len(thisFont.axes):
								axLoc.append(
									{
										"Axis": self.pref("axisName"),
										"Location": 0,
									}
								)
							parameter.value = axLoc

				self.w.close()  # delete if you want window to stay open

			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Add Grade Error: {e}")
			import traceback

			print(traceback.format_exc())


AddGrade()
