# MenuTitle: Add Grade

__doc__ = """
Add Grade axis and/or Grade master, based on your Weight and Width axes.
"""

import vanilla
from AppKit import NSAffineTransform, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSColor, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSPoint, NSTextAlignmentRight
from copy import copy
from GlyphsApp import Glyphs, GSInstance, GSUppercase, GSSmallcaps, GSSMOOTH, GSOFFCURVE, GSAxis, GSCustomParameter, Message
from mekkablue import mekkaObject, UpdateButton, reportFontName, makeWindowResizable


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


def anisotropicAdjust(font, master, originMaster, scope=(), setStatus=None):
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
		if setStatus:
			setStatus(f"🔠 {glyph.name} ({master.name})")
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


def wdthAdjust(font, gradeMaster, baseMaster, scope=(), setStatus=None):
	wdthAxisIndex = axisIdForTag(font, "wdth")
	if wdthAxisIndex is None:
		print("⚠️ No wdth axis found. Widths not fitted.")
		Message(
			title="No Width Axis",
			message=f"Advance widths could not be fitted to those of master ‘{baseMaster.name}’ because there is no wdth axis. Remove the graded master ‘{gradeMaster.name}’ and try again.",
			OKButton=None,
		)
		return

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
		return

	refWdthValue = wdthValues[0]
	refInstance = GSInstance()
	refInstance.font = font
	refInstance.axes = copy(gradeMaster.axes)
	refInstance.axes[wdthAxisIndex] = refWdthValue
	refFont = refInstance.interpolatedFont

	for glyph in font.glyphs:
		if glyph.name not in scope:
			continue
		if setStatus:
			setStatus(f"🔠 {glyph.name} ({gradeMaster.name})")
		gradeLayer = glyph.layers[gradeMaster.id]
		baseLayer = glyph.layers[baseMaster.id]
		if gradeLayer.width == baseLayer.width:
			# skip if width is OK already
			continue

		refLayer = refFont.glyphs[glyph.name].layers[0]
		if refLayer.width == gradeLayer.width or not gradeLayer.shapes:
			# width cannot be interpolated, so just fix SBs:
			fitSidebearings(gradeLayer, targetWidth=baseLayer.width)
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
		windowWidth = 470
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Add Grade",  # window title
			autosaveName=self.domain("mainwindow"),  # stores last window position and width
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Add Grade master (and if necessary Grade axis)", sizeStyle="small", selectable=True)

		self.w.baseMasterText = vanilla.TextBox("auto", "Based on master", sizeStyle="small", selectable=True)
		tooltipText = "The master that the new Grade master is derived from."
		self.w.baseMaster = vanilla.PopUpButton("auto", self.mastersOfCurrentFont(), sizeStyle="small", callback=self.SavePreferences)
		self.w.baseMaster.setToolTip(tooltipText)
		self.w.updateBaseMaster = UpdateButton("auto", callback=self.updateFromButton)
		self.w.baseMasterText.setToolTip(tooltipText)
		self.w.updateBaseMaster.setToolTip("Updates the list of masters from the frontmost font.")

		self.w.weightText = vanilla.TextBox("auto", "Use coordinate", sizeStyle="small", selectable=True)
		tooltipText = "Comma-separated axis coordinates (tag=value) at which the grade glyphs are interpolated, e.g. wght=100, wdth=100."
		self.w.weight = vanilla.ComboBox("auto", self.weightValuesForCurrentFont(), sizeStyle="small", callback=self.SavePreferences)
		self.w.weight.setToolTip(tooltipText)
		self.w.updateWeight = UpdateButton("auto", callback=self.updateFromButton)
		self.w.weightText.setToolTip(tooltipText)
		self.w.updateWeight.setToolTip("Fills in the axis coordinates of the chosen base master.")

		self.w.gradeText = vanilla.TextBox("auto", "… for grade", sizeStyle="small", selectable=True)
		tooltipText = "The value of the grade axis for the new master, e.g. -50, 0 or 50."
		self.w.grade = vanilla.ComboBox("auto", ("-50", "0", "50"), sizeStyle="small", callback=self.SavePreferences)
		self.w.grade.setToolTip(tooltipText)
		self.w.gradeText.setToolTip(tooltipText)
		self.w.axisTagText = vanilla.TextBox("auto", "Axis tag & name", sizeStyle="small", selectable=True)
		tooltipText = "Four-letter tag and name of the grade axis, used if the font has no such axis yet."
		self.w.axisTag = vanilla.EditText("auto", "GRAD", callback=self.SavePreferences, sizeStyle="small")
		self.w.axisTag.setToolTip(tooltipText)
		self.w.axisName = vanilla.EditText("auto", "Grade", callback=self.SavePreferences, sizeStyle="small")
		self.w.axisName.setToolTip(tooltipText)
		self.w.axisTagText.setToolTip(tooltipText)
		self.w.axisReset = UpdateButton("auto", callback=self.updateFromButton)
		self.w.axisReset.setToolTip("Resets axis tag and name to GRAD and Grade.")

		self.w.fittingMethodText = vanilla.TextBox("auto", "Fitting", sizeStyle="small", selectable=True)
		tooltipText = "How the glyph shapes are refitted into the metrics after the grade change."
		self.w.fittingMethod = vanilla.PopUpButton("auto", self.refittingMethods, sizeStyle="small", callback=self.SavePreferences)
		self.w.fittingMethod.setToolTip(tooltipText)
		self.w.fittingMethodText.setToolTip(tooltipText)

		self.w.addSyncMetricCustomParameter = vanilla.CheckBox("auto", "Add custom parameter ‘Link Metrics With Master’ (recommended)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.addSyncMetricCustomParameter.setToolTip("Adds the custom parameter ‘Link Metrics With Master’ to the new master, so that its metrics stay in sync with the base master.")

		self.w.limitToSelectedGlyphs = vanilla.CheckBox("auto", "Limit to selected glyphs", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.limitToSelectedGlyphs.setToolTip("If checked, only the selected glyphs are processed; other glyphs are left as they are.")

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")
		self.w.status.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Add Master", callback=self.AddGradeMain)
		self.w.runButton.setToolTip("Adds the Grade master (and the Grade axis if needed) to the frontmost font.")
		self.w.setDefaultButton(self.w.runButton)
		self.w.runButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.runButton.getNSButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# labels: right-aligned, one shared width per column
		for labelName in ("baseMasterText", "weightText", "gradeText", "fittingMethodText", "axisTagText"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes and square buttons stretch vertically by default; with everything
		# hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		def sameAttribute(attribute, viewName, referenceName):
			return {"view1": getattr(self.w, viewName), "attribute1": attribute, "view2": getattr(self.w, referenceName), "attribute2": attribute}

		rules = [
			"H:|-inset-[descriptionText]-inset-|",
			"H:|-inset-[baseMasterText]-gap-[baseMaster]-gap-[updateBaseMaster(24)]-inset-|",
			"H:|-inset-[weightText]-gap-[weight]-gap-[updateWeight(24)]-inset-|",
			"H:|-inset-[gradeText]-gap-[grade(60)]-gap-[axisTagText]-gap-[axisTag(45)]-gap-[axisName]-gap-[axisReset(24)]-inset-|",
			"H:|-inset-[fittingMethodText]-gap-[fittingMethod]-inset-|",
			"H:[addSyncMetricCustomParameter]-(>=inset)-|",
			"H:|-inset-[limitToSelectedGlyphs]-(>=inset)-|",
			"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
			"V:|-inset-[descriptionText]-row-[baseMaster]-row-[weight]-row-[grade]-section-[fittingMethod]-checkRow-[addSyncMetricCustomParameter]-checkRow-[limitToSelectedGlyphs]-inset-[runButton]-inset-|",
			sameAttribute("left", "addSyncMetricCustomParameter", "fittingMethod"),
			sameAttribute("width", "weightText", "baseMasterText"),
			sameAttribute("width", "gradeText", "baseMasterText"),
			sameAttribute("width", "fittingMethodText", "baseMasterText"),
			sameAttribute("centerY", "baseMasterText", "baseMaster"),
			sameAttribute("centerY", "updateBaseMaster", "baseMaster"),
			sameAttribute("centerY", "weightText", "weight"),
			sameAttribute("centerY", "updateWeight", "weight"),
			sameAttribute("centerY", "gradeText", "grade"),
			sameAttribute("centerY", "axisTagText", "grade"),
			sameAttribute("centerY", "axisTag", "grade"),
			sameAttribute("centerY", "axisName", "grade"),
			sameAttribute("centerY", "axisReset", "grade"),
			sameAttribute("centerY", "fittingMethodText", "fittingMethod"),
			sameAttribute("centerY", "status", "runButton"),
		]
		self.w.addAutoPosSizeRules(rules, metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5, "section": 12})

		makeWindowResizable(self.w)  # resizable horizontally only

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
				for m in (*font.masters, *font.instances):
					value = f"wght={m.axisValueValueForId_(axisID)}"
					if value not in weightValues:
						weightValues.append(value)
			for m in (*font.masters, *font.instances):
				value = self.masterAxesString(m)
				if value not in weightValues:
					weightValues.append(value)
		return sorted(weightValues)

	def masterAxesString(self, master):
		font = master.font
		return ", ".join([f"{a.axisTag}={master.axes[i]}" for i, a in enumerate(font.axes)])

	def updateFromButton(self, sender=None):
		font = Glyphs.font
		if font is None and sender == self.w.updateWeight:
			return
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
		glyphNameForStatus = "start"
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			self.setStatus("🛠️ Processing …")
			fittingMethod = self.prefInt("fittingMethod")
			limitToSelectedGlyphs = self.prefBool("limitToSelectedGlyphs")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				self.setStatus("⚠️ No font open.")
				Message(
					title="No Font Open",
					message="The script requires a font with a weight axis. Open a font and run the script again.",
					OKButton=None,
				)
			else:
				if limitToSelectedGlyphs:
					glyphNames = [layer.parent.name for layer in thisFont.selectedLayers]
				else:
					glyphNames = [g.name for g in thisFont.glyphs]

				self.setStatus(f"🛠️ Processing {len(glyphNames)} glyphs …")
				reportName = reportFontName(thisFont)
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
					glyphNameForStatus = glyphName
					self.setStatus(f"🔠 {glyphName} ({gradeMaster.name})")
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
					anisotropicAdjust(thisFont, gradeMaster, baseMaster, scope=glyphNames, setStatus=self.setStatus)
				elif fittingMethod == 3:
					# adjust width with wdth axis:
					print(
						f"↔️ Fitting {len(glyphNames)} glyph{'' if len(glyphNames) == 1 else 's'} through the width axis..."
					)
					wdthAdjust(thisFont, gradeMaster, baseMaster, scope=glyphNames, setStatus=self.setStatus)

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

				self.setStatus(f"✅ Added master ‘{gradeMaster.name}’ with {len(glyphNames)} glyphs.")
				self.w.close()  # delete if you want window to stay open

			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			self.setStatus(f"❌ Error at {glyphNameForStatus}. Details in Macro Window.")
			print(f"Add Grade Error: {e}")
			import traceback

			print(traceback.format_exc())


AddGrade()
