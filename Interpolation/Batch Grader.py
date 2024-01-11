#MenuTitle: Batch Grader
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Btach-add graded masters to a multiple-master setup.
"""

import vanilla, sys
from copy import copy

def axisIdForTag(font, tag="wght"):
	for i, a in enumerate(font.axes):
		if a.axisTag == tag:
			return i
	return None

def fitSidebearings(layer, targetWidth, left=0.5):
	if not layer.shapes:
		layer.width = targetWidth
	else:
		diff = targetWidth - layer.width
		diff *= left
		layer.LSB += diff
		layer.width = targetWidth

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
			if any((nn.type == OFFCURVE, pn.type == OFFCURVE)):
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
				if smoothen == center == opposite == None:
					n.position = closestPointOnLine(
						n.position, nn, pn,
						)
			# elif n.type != OFFCURVE and (nn.type, pn.type).count(OFFCURVE) == 1:
			# 	# only one of the surrounding points is a BCP
			# 	center = n
			# 	if nn.type == OFFCURVE:
			# 		smoothen = nn
			# 		opposite = pn
			# 	elif pn.type == OFFCURVE:
			# 		smoothen = pn
			# 		opposite = nn
			# 	else:
			# 		continue # should never occur
			# 	p.setSmooth_withCenterNode_oppositeNode_(
			# 		smoothen, center, opposite,
			# 		)


class BatchGrader(object):
	prefID = "com.mekkablue.BatchGrader"
	prefDict = {
		# "prefName": defaultValue,
		"graderCode": "# mastername: wght+=100, wdth=100 ",
		"axisName": "Grade",
		"axisTag": "GRAD",
		"grade": 100,
		"searchFor": "GD0",
		"replaceWith": "GD100",
		"excludeFromInterpolation": "Grade, GD100",
		"addSyncMetricCustomParameter": True,
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 380
		windowHeight = 260
		windowWidthResize  = 1000 # user can resize width by this value
		windowHeightResize = 1000 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Batch Grader", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		indent = 65
		self.w.gradeText = vanilla.TextBox((inset, linePos+3, indent, 14), "Add grade:", sizeStyle="small", selectable=True)
		self.w.grade = vanilla.ComboBox((inset+indent, linePos-1, 55, 19), ("-100", "-50", "50", "100"), sizeStyle="small", callback=self.SavePreferences)
		self.w.axisTagText = vanilla.TextBox((inset+indent+65, linePos+3, 100, 14), "Axis tag & name:", sizeStyle="small", selectable=True)
		self.w.axisTag = vanilla.EditText((inset+indent+100+60, linePos, 45, 19), "GRAD", callback=self.SavePreferences, sizeStyle="small")
		self.w.axisName = vanilla.EditText((inset+indent+100+110, linePos, -inset-25, 19), "Grade", callback=self.SavePreferences, sizeStyle="small")
		self.w.axisReset = vanilla.SquareButton((-inset-20, linePos, -inset, 18), "↺", sizeStyle="small", callback=self.updateUI)
		linePos += lineHeight
		
		indent = 110
		self.w.searchForText = vanilla.TextBox((inset, linePos+2, indent, 14), "In name, search for:", sizeStyle="small", selectable=True)
		self.w.searchFor = vanilla.EditText((inset+indent, linePos, 60, 19), self.pref("searchFor"), callback=self.SavePreferences, sizeStyle="small")
		self.w.replaceWithText = vanilla.TextBox((inset+indent+65, linePos+2, 100, 14), "and replace with:", sizeStyle="small", selectable=True)
		self.w.replaceWith = vanilla.EditText((inset+indent+165, linePos, -inset, 19), self.pref("replaceWith"), callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		indent = 155
		self.w.excludeFromInterpolationText = vanilla.TextBox((inset, linePos+3, -inset, 14), "Ignore masters containing:", sizeStyle="small", selectable=True)
		self.w.excludeFromInterpolation = vanilla.EditText((inset+indent, linePos, -inset, 19), self.prefDict["excludeFromInterpolation"], callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.addSyncMetricCustomParameter = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Add custom parameter ‘Link Metrics With Master’ (recommended)", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight + 5



		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Recipe for new graded masters:", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		self.w.graderCode = vanilla.TextEditor((1, linePos, -1, -inset * 3), text=self.prefDict["graderCode"], callback=self.SavePreferences, checksSpelling=False)
		self.w.graderCode.getNSTextView().setToolTip_(
			"- Prefix comments with hashtag (#)\n- Empty line are ignored\n- Recipe syntax: MASTERNAME: AXISTAG+=100, AXISTAG=400, AXISTAG-=10"
			)
		self.w.graderCode.getNSScrollView().setHasVerticalScroller_(1)
		self.w.graderCode.getNSScrollView().setHasHorizontalScroller_(1)
		self.w.graderCode.getNSScrollView().setRulersVisible_(0)
		textView = self.w.graderCode.getNSTextView()
		try:
			legibleFont = NSFont.userFixedPitchFontOfSize_(NSFont.systemFontSize())
			textView.setFont_(legibleFont)
		except Exception as e:
			print(e)
		
		
		
		
		# Buttons:
		self.w.resetButton = vanilla.Button((inset, -20-inset, 80, -inset), "Reset", sizeStyle="regular", callback=self.ResetGraderCode)
		
		self.w.runButton = vanilla.Button((-120-inset, -20-inset, -inset, -inset), "Add Grades", sizeStyle="regular", callback=self.BatchGraderMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Batch Grader’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def updateUI(self, sender=None):
		pass
		
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
	
	def ResetGraderCode(self, sender=None):
		thisFont = Glyphs.font
		text = "# mastername: wght+=100, wdth=100\n"
		gradeValue = int(self.pref("grade").strip())
		wghtCode = f"wght+={gradeValue}".replace("+=-", "-=")
		for m in thisFont.masters:
			if self.shouldExcludeMaster(m):
				continue
			text += f"{m.name}: {wghtCode}\n"
		self.w.graderCode.set(text)
	
	def shouldExcludeMaster(self, master):
		excludedParticles = self.pref("excludeFromInterpolation")
		excludedParticles = [p.strip() for p in excludedParticles.split(",") if p]
		for particle in excludedParticles:
			if particle in master.name:
				return True # yes, exclude
		return False # no, don't exclude

	def masterAxesString(self, master):
		font = master.font
		return ", ".join([f"{a.axisTag}={master.axes[i]}" for i, a in enumerate(font.axes)])

	def cleanInterpolationDict(self, instance):
		font = instance.font
		interpolationDict = instance.instanceInterpolations
		newInterpolationDict = {}
		total = 0.0
		for k in interpolationDict.keys():
			m = font.masters[k]
			if not m or self.shouldExcludeMaster(m):
				continue
			newInterpolationDict[k] = interpolationDict[k]
			total += newInterpolationDict[k]
		if not newInterpolationDict:
			print(f"⚠️ Exclusion rules would make interpolation impossible. Leaving as is.")
		else:
			if total != 1.0:
				factor = 1.0 / total
				for k in newInterpolationDict.keys():
					newInterpolationDict[k] *= factor
			instance.manualInterpolation = True
			instance.instanceInterpolations = newInterpolationDict
	
	def BatchGraderMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Batch Grader’ could not write preferences.")
			
			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(self, prefName, self.pref(prefName))
				except:
					fallbackValue = self.prefDict[prefName]
					print(f"⚠️ Could not set pref ‘{prefName}’, resorting to default value: ‘{fallbackValue}’.")
					setattr(self, prefName, fallbackValue)
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Batch Grader Report for {reportName}")
				print()
				
				# add or update Grade axis if necessary:
				grade = int(self.pref("grade").strip())
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
					thisFont.didChangeValueForKey_("axes")
				else:
					gradeAxis = thisFont.axisForTag_(axisTag)
					if gradeAxis.name != axisName:
						print(f"Updating {axisTag} axis name: {gradeAxis.name} → {axisName}")
						gradeAxis.name = axisName
				gradeAxisID = axisIdForTag(thisFont, axisTag)
				
				# parse code and step through masters:
				searchFor = self.pref("searchFor")
				replaceWith = self.pref("replaceWith")
				graderCode = self.pref("graderCode").strip()
				for codeLine in graderCode.splitlines():
					if "#" in codeLine:
						codeLine = codeLine[:codeLine.find("#")]
					codeLine = codeLine.strip()
					if not codeLine:
						continue
					
					masterName, axes = codeLine.split(":")
					masterName = masterName.strip()
					master = thisFont.fontMasterForName_(masterName)
					if not master:
						print(f"⚠️ No master called ‘{masterName}’")
						continue
					
					if self.shouldExcludeMaster(master):
						continue
					
					print(master)
					weightedAxes = master.axes[:]
					axisCodes = [a.strip() for a in axes.split(",") if "=" in a]
					for axisCode in axisCodes:
						if "+=" in axisCode:
							axisTag, value = axisCode.split("+=")
							valueFactor = 1
						elif "-=" in axisCode:
							axisTag, value = axisCode.split("-=")
							valueFactor = -1
						else:
							axisTag, value = axisCode.split("=")
							valueFactor = 0
						axisID = axisIdForTag(thisFont, tag=axisTag.strip())
						value = int(value.strip())
						
						if valueFactor==0:
							weightedAxes[axisID] = value
						else:
							weightedAxes[axisID] = weightedAxes[axisID] + value * valueFactor
						
					print("\t", weightedAxes)
					
					# weighted instance/font: the shapes
					weightedInstance = GSInstance()
					weightedInstance.font = thisFont
					weightedInstance.name = "###DELETEME###"
					weightedInstance.axes = weightedAxes
					self.cleanInterpolationDict(weightedInstance)
					weightedFont = weightedInstance.interpolatedFont
					print(f"🛠️ Interpolating grade: {self.masterAxesString(weightedInstance)}")
					
					# add the graded master
					gradeMaster = copy(master)
					if searchFor and replaceWith:
						gradeMaster.name = master.name.replace(searchFor, replaceWith)
					elif replaceWith:
						gradeMaster.name = master.name + replaceWith
					else:
						gradeMaster.name = f"{master.name} Grade {grade}"
					gradeMaster.font = thisFont
					gradeAxes = list(master.axes)
					gradeAxes[gradeAxisID] = grade
					gradeMaster.axes = gradeAxes
					if self.pref("addSyncMetricCustomParameter"):
						gradeMaster.customParameters.append(
							GSCustomParameter(
								"Link Metrics With Master", 
								master.id,
								)
							)
					
					for m in thisFont.masters[::-1]:
						if m.axes == gradeMaster.axes:
							# remove preexisting graded masters if there are any
							print(f"❌ Removing preexisting graded master ‘{m.name}’")
							thisFont.removeFontMaster_(m)
				
					# otherwise add the one we built above:
					print(f"Ⓜ️ Adding master: ‘{gradeMaster.name}’")
					thisFont.masters.append(gradeMaster)
					glyphNames = [g.name for g in thisFont.glyphs]
					for glyphName in glyphNames:
						weightedGlyph = weightedFont.glyphs[glyphName]
						weightedLayer = weightedGlyph.layers[0]
						straightenBCPs(weightedLayer)
						weightedWidth = weightedLayer.width
					
						baseGlyph = thisFont.glyphs[glyphName]
						baseLayer = baseGlyph.layers[master.id]
						baseWidth = baseLayer.width
					
						if weightedWidth != baseWidth:
							fitSidebearings(weightedLayer, targetWidth=baseWidth, left=0.5)
					
						# bring the interpolated shapes back into the open font:
						gradeLayer = baseGlyph.layers[gradeMaster.id]
						gradeLayer.width = weightedLayer.width
						gradeLayer.shapes = copy(weightedLayer.shapes)
						gradeLayer.anchors = copy(weightedLayer.anchors)
						gradeLayer.hints = copy(weightedLayer.hints)
				
				
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
				
				thisFont.didChangeValueForKey_("fontMasters")
				
				self.w.close() # delete if you want window to stay open

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Batch Grader Error: {e}")
			import traceback
			print(traceback.format_exc())

BatchGrader()