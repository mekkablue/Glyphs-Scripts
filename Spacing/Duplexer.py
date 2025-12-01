#MenuTitle: Duplexer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Duplexes all masters according to one master you pick, so all widths are synced across all masters. Great for preparing your font for the Sync Metrics with First Master parameter.
"""

import vanilla, sys
from copy import copy
from GlyphsApp import Glyphs, GSLayer, GSCustomParameter, Message
from mekkablue import mekkaObject, UpdateButton

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
		referenceLayer.leftMetricsKey = referenceLayer.leftMetricsKey or glyph.leftMetricsKey.replace("=", "==").replace("===", "==")
		referenceLayer.rightMetricsKey = referenceLayer.rightMetricsKey or glyph.rightMetricsKey.replace("=", "==").replace("===", "==")

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
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 180
		windowWidthResize  = 100 # user can resize width by this value
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
		
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Run", sizeStyle="regular", callback=self.DuplexerMain)
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
		currentSelection = self.w.base.get()
		menu = self.masterList()
		self.w.base.setItems(menu)
		if currentSelection+1 > len(menu):
			self.w.base.set(0)

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
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{font.familyName}\n⚠️ The font file has not been saved yet."
				print(f"📄 Duplexer Report for {reportName}")

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

				baseMaster = font.masters[base]
				masterID = baseMaster.id
				print(f"Ⓜ️ Duplexing based on master ‘{baseMaster.name}’ (ID: {masterID})")

				allGlyphs = self.pref("allGlyphs")
				if allGlyphs:
					glyphs = font.glyphs
				else:
					glyphs = [l.parent for l in font.selectedLayers if isinstance(l, GSLayer)]

				excludeSpecialGlyphs = self.pref("excludeSpecialGlyphs")
				if excludeSpecialGlyphs:
					glyphs = [g for g in glyphs if not g.name.startswith("_")]

				print(f"Processing {len(glyphs)} glyphs...")

				font.disableUpdateInterface()
				try:
					fixMetricsKeys = self.pref("fixMetricsKeys")
					count = 0
					for glyph in glyphs:
						success = duplexGlyph(glyph, masterID, fixMetricsKeys=fixMetricsKeys)
						if success:
							print(f"🔡 Duplexed: {glyph.name}")
							count += 1
						else:
							print(f"🥴 No change: {glyph.name}")
				except Exception as e:
					raise e
				finally:
					font.enableUpdateInterface()

				self.w.close() # delete if you want window to stay open

				print(f"\n✅ Done. Duplexed {count} glyphs.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Duplexer Error: {e}")
			import traceback
			print(traceback.format_exc())

Duplexer()