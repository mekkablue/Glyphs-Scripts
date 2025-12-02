#MenuTitle: Duplexer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Duplexes all masters according to one master you pick, so all widths are synced across all masters. Great for preparing your font for the Sync Metrics with First Master parameter.
"""

import vanilla, sys
from copy import copy
from AppKit import NSPoint, NSMidX, NSMidY, NSAffineTransform, NSAffineTransformStruct
from GlyphsApp import Glyphs, GSLayer, GSCustomParameter, Message
from mekkablue import mekkaObject, UpdateButton

def mixedGlyphDatabase(glyphs):
	mixedDict = {}
	for glyph in glyphs:
		if not isMixed(glyph):
			continue
		mixedDict[glyph.name] = {}
		for layer in glyph.layers:
			if not layer.isMasterLayer and not layer.isSpecialLayer:
				continue
			mixedDict[glyph.name][layer.layerId] = [layer.width, layer.LSB]
			for shape in layer.shapes:
				center = NSMidX(shape.bounds)
				mixedDict[glyph.name][layer.layerId].append(center)
	return mixedDict

def fixMixedGlyphs(glyphs, mixedDict):
	for glyph in glyphs:
		if glyph.name in mixedDict.keys():
			fixMixedGlyph(glyph, mixedDict[glyph.name])

def fixMixedGlyph(glyph, layerInfos):
	for layer in glyph.layers:
		if layer.layerId in layerInfos.keys():
			fixMixedLayer(layer, layerInfos[layer.layerId])

def fixMixedLayer(layer, layerInfo):
	originalWidth = layerInfo.pop(0)
	originalLSB = layerInfo.pop(0)
	duplexWidth = layer.width
	duplexShift = (duplexWidth - originalWidth) // 2
	for i, shape in enumerate(layer.shapes):
		currentCenter = NSMidX(shape.bounds)
		originalCenter = layerInfo[i]
		hShift = originalCenter - currentCenter + duplexShift
		if hShift != 0.0:
			hMove = NSAffineTransform.transform()
			hMove.translateXBy_yBy_(hShift, 0)
			shape.applyTransform(hMove.transformStruct())
	if abs(layer.LSB - (originalLSB + duplexShift)) > 1.0:
		print(f"❌ LSB shift: {layer.parent.name} {layer.name}")

def isMixed(glyph):
	for layer in glyph.layers:
		if not layer.isMasterLayer and not layer.isSpecialLayer:
			continue
		if len(layer.components) > 0 and len(layer.paths) > 0:
			return True
	return False

def duplexLayerWidth(layer, referenceLayer):
	change = referenceLayer.width - layer.width
	leftChange = int(change/2)
	layer.LSB += leftChange
	layer.width = referenceLayer.width
	return True

def duplexGlyph(glyph, referenceMasterID, fixMetricsKeys=False):
	referenceLayer = glyph.layers[referenceMasterID]
	if not referenceLayer:
		print(f"❌ no reference layer in {glyph.name}")
		return
	
	if fixMetricsKeys:
		# assign layer-specific metrics key:
		referenceLayer.leftMetricsKey = referenceLayer.leftMetricsKey or glyph.leftMetricsKey
		if referenceLayer.leftMetricsKey:
			referenceLayer.leftMetricsKey.replace("=", "==").replace("===", "==")

		referenceLayer.rightMetricsKey = referenceLayer.rightMetricsKey or glyph.rightMetricsKey
		if referenceLayer.rightMetricsKey:
			referenceLayer.rightMetricsKey.replace("=", "==").replace("===", "==")

		# get rid of all other metrics keys:
		glyph.leftMetricsKey = None
		glyph.rightMetricsKey = None
		for layer in glyph.layers:
			if layer is referenceLayer:
				continue
			layer.leftMetricsKey = None
			layer.rightMetricsKey = None
	
	changed = False
	for layer in glyph.layers:
		if layer is referenceLayer:
			print(f"  ← {layer.name} ({layer.width})")
			continue
		if not layer.isMasterLayer and not layer.isSpecialLayer:
			continue
		if layer.hasAlignedWidth():
			continue
		
		layerChanged = duplexLayerWidth(layer, referenceLayer)
		changed = changed or layerChanged
		print(f"  → width {layer.width} for {layer.name} ")

	return changed

class Duplexer(mekkaObject):
	prefID = "com.mekkaObject.Duplexer"
	prefDict = {
		# "prefName": defaultValue,
		"base": 0,
		"allGlyphs": 1,
		"excludeSpecialGlyphs": 1,
		"fixMetricsKeys": 1,
		"addSyncParameter": 0,
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 200
		windowWidthResize  = 600 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Duplexer", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Sync widths of all masters (‘duplex’)", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		self.w.baseText = vanilla.TextBox((inset, linePos+2, 60, 14), "Based on:", sizeStyle="small", selectable=True)
		self.w.base = vanilla.PopUpButton((inset+60, linePos, -inset-20, 17), [], sizeStyle="small", callback=self.SavePreferences)
		self.w.baseUpdate = UpdateButton((-inset-16, linePos-3, -inset, 18), callback=self.updateUI)
		linePos += lineHeight
		
		self.w.allGlyphs = vanilla.CheckBox((inset+3, linePos-1, -inset+3, 20), "Apply to ALL glyphs (otherwise selected only)", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.excludeSpecialGlyphs = vanilla.CheckBox((inset+3, linePos-1, -inset+3, 20), "Exclude special glyphs (_corner, _smart, etc.)", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.fixMetricsKeys = vanilla.CheckBox((inset+3, linePos-1, -inset+3, 20), "Keep metrics keys on base master only", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.addSyncParameter = vanilla.CheckBox((inset+3, linePos-1, -inset+3, 20), "Add ‘Link Metrics With Master’ parameter", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Duplex", sizeStyle="regular", callback=self.DuplexerMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Duplexer’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def masterList(self, sender=None):
		menu = []
		font = Glyphs.font
		if font:
			for i, master in enumerate(font.masters):
				masterText = f"{i+1}. {font.familyName} ‘{master.name}’ (ID: {master.id})"
				menu.append(masterText)
		return menu

	def updateUI(self, sender=None):
		currentSelection = max(0, self.pref("base"))
		menu = self.masterList()
		if self.w.base.getItems() != menu:
			self.w.base.setItems(menu)
		if currentSelection+1 > len(menu):
			self.w.base.set(0)
		else:
			self.w.base.set(currentSelection)

	def DuplexerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Duplexer’ could not write preferences.")

			font = Glyphs.font # frontmost font
			if font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = font.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}:\n\n📄 {filePath}"
				else:
					reportName = f"{font.familyName}:\n\n⚠️ The font file has not been saved yet."
				print(f"Duplexer Report for {reportName}")

				base = self.pref("base")
				if self.w.base.getItems() != self.masterList():
					menu = self.w.base.getItems()
					firstMaster = menu[0]
					firstMaster = firstMaster[firstMaster.find(".")+1:firstMaster.find("‘")].strip()
					masterCount = len(menu)
					Message(
						title="Font mismatch",
						message="The settings in the script appear to be for a different font ({firstMaster} with {masterCount} masters) than the current frontmost font ({font.familyName} with {len(font.masters)} masters).",
						OKButton=None,
						)
					return

				# determine duplex source master (‘base’):
				baseMaster = font.masters[base]
				masterID = baseMaster.id
				print(f"Ⓜ️ Duplexing based on master ‘{baseMaster.name}’ (ID: {masterID})")

				# determine glyph span:
				allGlyphs = self.pref("allGlyphs")
				if allGlyphs:
					glyphs = font.glyphs
				else:
					glyphs = [l.parent for l in font.selectedLayers if isinstance(l, GSLayer)]

				# Exclude special glyphs:
				excludeSpecialGlyphs = self.pref("excludeSpecialGlyphs")
				if excludeSpecialGlyphs:
					glyphs = [g for g in glyphs if not g.name.startswith("_")]

				# Collect data of mixed glyphs:
				mixedDict = mixedGlyphDatabase(glyphs)

				# Start processing:
				print(f"🔢 Processing {len(glyphs)} glyphs...\n")
				font.disableUpdateInterface()
				try:
					fixMetricsKeys = self.pref("fixMetricsKeys")
					count = 0
					tabText = ""
					for glyph in glyphs:
						if glyph.name in mixedDict.keys():
							tabText += f"/{glyph.name}"

						print(f"🔡 Duplexing: {glyph.name}")
						success = duplexGlyph(glyph, masterID, fixMetricsKeys=fixMetricsKeys)
						if success:
							count += 1
						else:
							print("  🥴 (no change)")

					# fix positions in mixed glyphs:
					if mixedDict:
						fixMixedGlyphs(glyphs, mixedDict)
					
					# Link Metrics With Master:
					parameterName = "Link Metrics With Master"
					if self.pref("addSyncParameter"):
						for master in font.masters:
							# remove preexisting parameters:
							while master.customParameterForKey_(parameterName):
								master.removeObjectFromCustomParametersForKey_(parameterName)
							
							# do not add to base master:
							if master.id == masterID:
								continue
							
							# add parameter:
							parameter = GSCustomParameter(parameterName, masterID)
							master.customParameters.append(parameter)
						
					# report mixed glyphs:
					currentTabText = ""
					if font.currentTab:
						for l in font.currentTab.layers:
							if isinstance(l, GSLayer):
								currentTabText += f"/{l.parent.name}"

					if tabText and tabText != currentTabText:
						font.newTab(tabText)
				except Exception as e:
					raise e
				finally:
					font.enableUpdateInterface()
					self.w.close()

				print(f"\n✅ Done. Duplexed {count} glyphs.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Duplexer Error: {e}")
			import traceback
			print(traceback.format_exc())

Duplexer()