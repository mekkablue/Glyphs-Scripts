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

def wghtIndex(font):
	for i, a in enumerate(font.axes):
		if a.axisTag == "wght":
			return i
	return None

def hScaleLayer(layer, hFactor=1.0):
	xScale = NSAffineTransform.transform()
	xScale.scaleXBy_yBy_(hFactor, 1.0)
	layer.applyTransform(xScale.transformStruct())

def anisotropicAdjust(font, layers):
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

	def wghtIndex(font):
		for i, a in enumerate(font.axes):
			if a.axisTag == "wght":
				return i
		return None

	def hScaleLayer(layer, hFactor=1.0):
		xScale = NSAffineTransform.transform()
		xScale.scaleXBy_yBy_(hFactor, 1.0)
		layer.applyTransform(xScale.transformStruct())
	
	def anisotropicAdjust(font, master, layers):
		font = Glyphs.font
		layer = font.selectedLayers[0]
		glyph = layer.parent
		referenceGlyph = "idotless"
		if glyph.case == GSUppercase:
			referenceGlyph = "I"
		elif glyph.case == GSSmallcaps:
			referenceGlyph = "i.sc"

		hScale = 1.5
		wghtScale = 1/hScale
		wghtAxisIndex = wghtIndex(font)
		wghtInstanceAxes = list(layer.master.axes)

		currentWght = layer.master.axes[wghtAxisIndex]
		currentWghtInstance = GSInstance()
		currentWghtInstance.font = font
		currentWghtInstance.axes = wghtInstanceAxes
		currentWghtFont = currentWghtInstance.interpolatedFont
		currentRealWght = realWeight(currentWghtFont)
		currentRealWghtUC = realWeight(currentWghtFont, referenceGlyph="I")

		refWght = currentWght * wghtScale
		wghtInstanceAxes[wghtAxisIndex] = refWght
		refWghtInstance = GSInstance()
		refWghtInstance.font = font
		refWghtInstance.axes = wghtInstanceAxes
		refWghtFont = refWghtInstance.interpolatedFont
		refRealWght = realWeight(refWghtFont)
		refRealWghtUC = realWeight(refWghtFont, referenceGlyph="I")
	
		# ANY CASE
		wghtCorrection = currentRealWght / refRealWght
		wghtCorrected = currentWght + (refWght-currentWght) * wghtCorrection
		wghtInstanceAxes[wghtAxisIndex] = wghtCorrected
		wghtInstance = GSInstance()
		wghtInstance.font = font
		wghtInstance.axes = wghtInstanceAxes
		wghtFont = wghtInstance.interpolatedFont
	
		# UPPERCASE
		wghtCorrection = currentRealWghtUC / refRealWghtUC
		wghtCorrected = currentWght + (refWght-currentWght) * wghtCorrection
		wghtInstanceAxes[wghtAxisIndex] = wghtCorrected
		wghtInstanceUC = GSInstance()
		wghtInstanceUC.font = font
		wghtInstanceUC.axes = wghtInstanceAxes
		wghtFontUC = wghtInstanceUC.interpolatedFont

		wghtLayer = wghtInstance.interpolatedFont.glyphs[glyph.name].layers[0]
		for i, path in enumerate(wghtLayer.paths):
			for j, node in enumerate(path.nodes):
				originalNode = layer.paths[i].nodes[j]
				node.y = originalNode.y

		hScaleLayer(wghtLayer, hScale)
		layer.shapes = copy(wghtLayer.shapes)
		layer.width *= hScale
	

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
		"useWdthAxis": 1,
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 220
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
		
		self.w.baseMasterText = vanilla.TextBox((inset, linePos+2, 100, 14), "Based on master:", sizeStyle="small", selectable=True)
		self.w.baseMaster = vanilla.PopUpButton((inset+100, linePos, -inset, 17), self.mastersOfCurrentFont(), sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight
		
		indent = 70
		
		self.w.weightText = vanilla.TextBox((inset, linePos+2, indent, 14), "Use weight:", sizeStyle="small", selectable=True)
		self.w.weight = vanilla.ComboBox((inset+indent, linePos-1, -inset, 19), self.weightValuesForCurrentFont(), sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight
		
		self.w.gradeText = vanilla.TextBox((inset, linePos+2, indent, 14), "…as grade:", sizeStyle="small", selectable=True)
		self.w.grade = vanilla.ComboBox((inset+indent, linePos-1, -inset, 19), ("-50", "0", "50"), sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight
		
		indent = 92
		
		self.w.axisTagText = vanilla.TextBox((inset, linePos+2, indent, 14), "Grade axis:   Tag", sizeStyle="small", selectable=True)
		self.w.axisTag = vanilla.EditText((inset+indent, linePos, 50, 19), "GRAD", callback=self.SavePreferences, sizeStyle="small")
		self.w.axisNameText = vanilla.TextBox((inset+indent+60, linePos+2, 35, 14), "Name", sizeStyle="small", selectable=True)
		self.w.axisName = vanilla.EditText((inset+indent+95, linePos, -inset, 19), "Grade", callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.addSyncMetricCustomParameter = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Add custom parameter ‘Link Metrics With Master’ (recommended)", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		
		self.w.useWdthAxis = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Use Width axis for fitting grade layer width", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.useWdthAxis.enable(False)
		
		
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Add", sizeStyle="regular", callback=self.AddGradeMain)
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
		if font:
			for i, master in enumerate(font.masters):
				masterMenu.append(f"{i+1}. {master.name} (ID: {master.id})")
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
					if targetWidth != weightedWidth:
						diff = targetWidth - weightedWidth
						if weightedLayer.LSB + weightedLayer.RSB:
							lsbPercentage = weightedLayer.LSB / (weightedLayer.LSB + weightedLayer.RSB)
						else:
							lsbPercentage = 0.5
						diff *= lsbPercentage
						weightedLayer.LSB += diff
					gradeLayer.shapes = copy(weightedLayer.shapes)
					gradeLayer.anchors = copy(weightedLayer.anchors)
				
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
				
				# self.w.close() # delete if you want window to stay open

			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Add Grade Error: {e}")
			import traceback
			print(traceback.format_exc())

AddGrade()