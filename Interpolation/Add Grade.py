#MenuTitle: Add Grade
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Add Grade axis and/or Grade master, based on your Weight and Width axes.
"""

import vanilla, sys
from AppKit import NSAffineTransform, NSAffineTransformStruct, NSPoint
from copy import copy

def realWeight(font, referenceGlyph="idotless", masterIndex=0):
	glyph = font.glyphs[referenceGlyph]
	layer = glyph.layers[masterIndex]
	midY = layer.bounds.origin.y + layer.bounds.size.height / 2
	intersections = layer.intersectionsBetweenPoints(
		NSPoint(layer.bounds.origin.x-100, midY),
		NSPoint(layer.bounds.origin.x + layer.bounds.size.width + 100, midY),
		)
	p1 = intersections[1]
	p2 = intersections[-2]
	actualWidth = p2.x - p1.x
	return actualWidth

def axisIdForTag(font, tag="wght"):
	for i, a in enumerate(font.axes):
		if a.axisTag == tag:
			return i
	return None

def hScaleLayer(layer, hFactor=1.0):
	xScale = NSAffineTransform.transform()
	xScale.scaleXBy_yBy_(hFactor, 1.0)
	layer.applyTransform(xScale.transformStruct())

def realWeight(font, referenceGlyph="idotless", masterIndex=0):
	glyph = font.glyphs[referenceGlyph]
	if not glyph:
		return None

	layer = glyph.layers[masterIndex]
	midY = layer.bounds.origin.y + layer.bounds.size.height / 2
	intersections = layer.intersectionsBetweenPoints(
		NSPoint(layer.bounds.origin.x-100, midY),
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

def anisotropicAdjust(font, master, originMaster):
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
		layer = glyph.layers[master.id]
		originLayer = glyph.layers[originMaster.id]
		
		# skip glyphs where we do not make adjustments
		if layer.width == 0 or originLayer.width == 0 or layer.width == originLayer.width:
			continue
		
		# reference weight for measuring the span of an axis
		hScale = originLayer.width/layer.width
		wghtScale = 1/hScale
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
		
		wghtCorrected = currentWght + (refWght-currentWght) * wghtCorrection
		wghtInstanceAxes[wghtAxisIndex] = wghtCorrected
		wghtInstance = GSInstance()
		wghtInstance.font = font
		wghtInstance.axes = wghtInstanceAxes
		wghtFont = wghtInstance.interpolatedFont

		wghtLayer = wghtInstance.interpolatedFont.glyphs[glyph.name].layers[0]
		for i, path in enumerate(wghtLayer.paths):
			for j, node in enumerate(path.nodes):
				originalNode = layer.paths[i].nodes[j]
				node.y = originalNode.y

		hScaleLayer(wghtLayer, hScale)
		layer.shapes = copy(wghtLayer.shapes)
		layer.width *= hScale

def fitSidebearings(layer, targetWidth, left=0.5):
	if not layer.shapes:
		layer.width = targetWidth
	else:
		diff = targetWidth - layer.width
		diff *= left
		layer.LSB += diff
		layer.width = targetWidth
	
def wdthAdjust(font, gradeMaster, baseMaster):
	wdthAxisIndex = axisIdForTag(font, "wdth")
	if wdthAxisIndex == None:
		print("⚠️ No wdth axis found. Widths not fitted.")
		Message(
			title="No Width Axis",
			message=f"Advance widths could not be fitted to those of master ‘{baseMaster.name}’ because there is no wdth axis. Remove the graded master ‘{gradeMaster.name}’ and try again.",
			OKButton=None,
			)
	
	baseWdthValue = baseMaster.axes[wdthAxisIndex]
	gradeWdthValue = gradeMaster.axes[wdthAxisIndex]
	wdthValues = sorted(set([m.axes[wdthAxisIndex] for m in font.masters if m.axes[wdthAxisIndex] != baseWdthValue]))
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
		
		wdthFactor = baseLayer.width / gradeLayer.width
		wdthValue = gradeWdthValue + wdthFactor * (baseWdthValue - gradeWdthValue)
		wdthInstance = GSInstance()
		wdthInstance.font = font
		wdthInstance.axes = copy(gradeMaster.axes)
		wdthInstance.axes[wdthAxisIndex] = wdthValue
		wdthFont = wdthInstance.interpolatedFont
		wdthLayer = wdthFont.glyphs[glyph.name].layers[0]
		gradeLayer.shapes = copy(wdthLayer.shapes)
		gradeLayer.anchors = copy(wdthLayer.anchors)
		gradeLayer.width = baseLayer.width

class AddGrade(object):
	prefID = "com.mekkablue.AddGrade"
	prefDict = {
		# "prefName": defaultValue,
		"baseMaster": 0,
		"axisName": "Grade",
		"axisTag": "GRAD",
		"grade": 50,
		"weight": 100,
		"addSyncMetricCustomParameter": 1,
		"fittingMethod": 0,
	}
	
	refittingMethods = (
		"Adjust advance width: LSB 50%, RSB 50%",
		"Adjust advance width: SBs by current proportions",
		"Anisotropic wght interpolation (requires I and idotless)",
		"Isotropic wdth interpolation (requires wdth axis)",
	)
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 225
		windowWidthResize  = 200 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Add Grade", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos+2, -inset, 14), "Add Grade master (and if necessary Grade axis):", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		self.w.baseMasterText = vanilla.TextBox((inset, linePos+3, 100, 14), "Based on master:", sizeStyle="small", selectable=True)
		self.w.baseMaster = vanilla.PopUpButton((inset+100, linePos, -inset, 17), self.mastersOfCurrentFont(), sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight
		
		indent = 70
		
		self.w.weightText = vanilla.TextBox((inset, linePos+3, indent, 14), "Use weight:", sizeStyle="small", selectable=True)
		self.w.weight = vanilla.ComboBox((inset+indent, linePos-1, -inset, 19), self.weightValuesForCurrentFont(), sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight
		
		self.w.gradeText = vanilla.TextBox((inset, linePos+3, indent, 14), "…as grade:", sizeStyle="small", selectable=True)
		self.w.grade = vanilla.ComboBox((inset+indent, linePos-1, -inset, 19), ("-50", "0", "50"), sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight
		
		indent = 92
		
		self.w.axisTagText = vanilla.TextBox((inset, linePos+3, indent, 14), "Grade axis:   Tag", sizeStyle="small", selectable=True)
		self.w.axisTag = vanilla.EditText((inset+indent, linePos, 50, 19), "GRAD", callback=self.SavePreferences, sizeStyle="small")
		self.w.axisNameText = vanilla.TextBox((inset+indent+60, linePos+3, 35, 14), "Name", sizeStyle="small", selectable=True)
		self.w.axisName = vanilla.EditText((inset+indent+95, linePos, -inset, 19), "Grade", callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.addSyncMetricCustomParameter = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Add custom parameter ‘Link Metrics With Master’ (recommended)", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.fittingMethodText = vanilla.TextBox((inset, linePos+3, 90, 14), "Fitting method:", sizeStyle="small", selectable=True)
		self.w.fittingMethod = vanilla.PopUpButton((inset+90, linePos+1, -inset, 17), self.refittingMethods, sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight
		
		# self.w.useWdthAxis = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Use Width axis for fitting grade layer width", value=False, callback=self.SavePreferences, sizeStyle="small")
		# linePos += lineHeight
		#
		# self.w.useWdthAxis.enable(False)
		
		# Run Button:
		self.w.runButton = vanilla.Button((-120-inset, -20-inset, -inset, -inset), "Add Master", sizeStyle="regular", callback=self.AddGradeMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Add Grade’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def mastersOfCurrentFont(self, sender=None):
		masterMenu = []
		font = Glyphs.font
		wghtID = font.axisForTag_("wght").id
		if font:
			for i, master in enumerate(font.masters):
				masterMenu.append(f"{i+1}. {master.name}, wght={master.axes[wghtID]} (ID: {master.id})")
		return masterMenu
	
	def weightValuesForCurrentFont(self, sender=None):
		weightValues = []
		font = Glyphs.font
		if font:
			axisID = font.axisForTag_("wght").id
			for m in font.masters:
				value = m.axisValueValueForId_(axisID)
				if not value in weightValues:
					weightValues.append(value)
			for i in font.instances:
				value = i.axisValueValueForId_(axisID)
				if not value in weightValues:
					weightValues.append(value)
		return sorted(weightValues)
			
	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				getattr(self.w, prefName).set(self.pref(prefName))
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def AddGradeMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Add Grade’ could not write preferences.")
			
			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(sys.modules[__name__], prefName, self.pref(prefName))
				except:
					fallbackValue = self.prefDict[prefName]
					print(f"⚠️ Could not set pref ‘{prefName}’, resorting to default value: ‘{fallbackValue}’.")
					setattr(sys.modules[__name__], prefName, fallbackValue)

			fittingMethod = int(self.pref("fittingMethod"))
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
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
				if not axisTag in existingAxisTags:
					print(f"Adding axis ‘{axisName}’ ({axisTag})")
					gradeAxis = GSAxis()
					gradeAxis.name = axisName
					gradeAxis.axisTag = axisTag
					gradeAxis.hidden = False
					thisFont.axes.append(gradeAxis)
				else:
					gradeAxis = thisFont.axisForTag_(axisTag)
					if gradeAxis.name != axisName:
						print(f"Updating {axisTag} axis name: {gradeAxis.name} → {axisName}")
						gradeAxis.name = axisName
				
				baseMaster = thisFont.masters[self.pref("baseMaster")]
				grade = int(self.pref("grade"))
				gradeMaster = copy(baseMaster)
				gradeMaster.name = f"{baseMaster.name} Grade {self.pref('grade')}"
				print(f"Adding master: {gradeMaster.name}")
				gradeMaster.setAxisValueValue_forId_(grade, gradeAxis.id)
				if self.pref("addSyncMetricCustomParameter"):
					linkMasterParameter = GSCustomParameter("Link Metrics With Master", baseMaster.id)
					gradeMaster.customParameters.append(linkMasterParameter)
				thisFont.masters.append(gradeMaster)
				
				gradeInstance = GSInstance()
				gradeInstance.font = thisFont
				gradeInstance.name = "###DELETEME###"
				gradeInstance.axes = baseMaster.axes
				weightValue = float(self.pref("weight").strip())
				for i, a in enumerate(thisFont.axes):
					if a.axisTag == "wght" or a.name == "Weight": # weight axis
						gradeInstance.axes[i] = weightValue
						break
				gradeFont = gradeInstance.interpolatedFont
				for weightedGlyph in gradeFont.glyphs:
					weightedLayer = weightedGlyph.layers[0]
					weightedWidth = weightedLayer.width
					targetGlyph = thisFont.glyphs[weightedGlyph.name]
					gradeLayer = targetGlyph.layers[gradeMaster.id]
					baseLayer = targetGlyph.layers[baseMaster.id]
					targetWidth = baseLayer.width
					
					# adjust width by methods 0 and 1:
					if targetWidth != weightedWidth and fittingMethod < 2:
						if fittingMethod == 1 and (weightedLayer.LSB + weightedLayer.RSB != 0):
							lsbPercentage = weightedLayer.LSB / (weightedLayer.LSB + weightedLayer.RSB)
						else:
							lsbPercentage = 0.5
						fitSidebearings(weightedLayer, targetWidth=targetWidth, left=lsbPercentage)
						
					gradeLayer.shapes = copy(weightedLayer.shapes)
					gradeLayer.anchors = copy(weightedLayer.anchors)
				
				if fittingMethod == 2:
					# adjust width anisotropically:
					anisotropicAdjust(thisFont, gradeMaster, baseMaster)
				elif fittingMethod == 3:
					# adjust width with wdth axis:
					wdthAdjust(thisFont, gradeMaster, baseMaster)
					
				# add missing axis locations if base master has axis locations:
				if Glyphs.versionNumber < 4:
					print("Updating Axis Locations in masters...")
					for thisMaster in thisFont.masters:
						axLoc = thisMaster.customParameters["Axis Location"]
						if axLoc and len(axLoc) < len(thisFont.axes):
							axLoc.append(
								{
									"Axis": "Grade",
									"Location": thisMaster.axisValueValueForId_(gradeAxis.id),
								}
							)
							thisMaster.customParameters["Axis Location"] = axLoc
							
					print("Updating Axis Locations in instances...")
					for thisInstance in thisFont.instances:
						axLoc = thisInstance.customParameters["Axis Location"]
						if axLoc and len(axLoc) < len(thisFont.axes):
							axLoc.append(
								{
									"Axis": "Grade",
									"Location": thisInstance.axisValueValueForId_(gradeAxis.id),
								}
							)
							thisInstance.customParameters["Axis Location"] = axLoc
						# thisMaster.setExternAxisValueValue_forId_(thisMaster.axisValueValueForId_(gradeID), gradeID)
						# thisMaster.externalAxesValues[gradeID] = thisMaster.internalAxesValues[gradeID]
						
					for parameter in thisFont.customParameters:
						if parameter.name == "Virtual Master":
							print("Updating Virtual Master...")
							axLoc = parameter.value
							if len(axLoc) < len(thisFont.axes):
								axLoc.append(
									{
										"Axis": "Grade",
										"Location": 0,
									}
								)
							parameter.value = axLoc
				
				self.w.close() # delete if you want window to stay open

			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Add Grade Error: {e}")
			import traceback
			print(traceback.format_exc())

AddGrade()