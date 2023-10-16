#MenuTitle: Enhance Compatibility
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Takes the current layer of each selected glyph, and propagates node types, node connections, realigns handles in technically compatible layers of the same glyph. Useful for fixing compatibility of glyphs that are shown to be compatible but still do not export.
"""

import vanilla, sys
from AppKit import NSPoint

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
	
	realigned = 0
	for p in layer.paths:
		for n in p.nodes:
			if n.connection != GSSMOOTH:
				continue
			nn, pn = n.nextNode, n.prevNode
			oldCoords = (pn.position, n.position, nn.position)
			if all((nn.type == OFFCURVE, pn.type == OFFCURVE)):
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
					
			elif n.type != OFFCURVE and (nn.type, pn.type).count(OFFCURVE) == 1:
				# only one of the surrounding points is a BCP
				center = n
				if nn.type == OFFCURVE:
					smoothen = nn
					opposite = pn
				elif pn.type == OFFCURVE:
					smoothen = pn
					opposite = nn
				else:
					continue # should never occur
				p.setSmooth_withCenterNode_oppositeNode_(
					smoothen, center, opposite,
					)
					
			if oldCoords != (pn.position, n.position, nn.position):
				realigned += 1
	return realigned

class EnhanceCompatibility(object):
	prefID = "com.mekkablue.EnhanceCompatibility"
	prefDict = {
		# "prefName": defaultValue,
		"fixType": True,
		"fixConnection": False,
		"realignHandles": False,
		"backupCurrentState": False,
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 370
		windowHeight = 180
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Enhance Compatibility", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -1, 14), "In compatible layers of selected glyphs, sync with selected layer:", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		self.w.fixType = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Sync node types (oncurve vs. offcurve)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.fixType.getNSButton().setToolTip_("Will propagate the current layer’s node types (oncurve vs. offcurve) to other compatible layers. Useful in TT paths.")
		linePos += lineHeight
		
		self.w.fixConnection = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Sync node connection (corner vs. smooth)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.fixConnection.getNSButton().setToolTip_("Will propagate the current layer’s node connections (green vs. blue) to other compatible layers. Usually just cosmetic.")
		linePos += lineHeight
		
		self.w.realignHandles = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Realign smooth connections (prefer orthogonals)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.realignHandles.getNSButton().setToolTip_("Will realign handles (BCPs) next to a smooth connection (green node). Or, if applicable, move smooth oncurves (green nodes) on the line between its surrounding handles.")
		linePos += lineHeight
		
		self.w.backupCurrentState = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Backup layers in background", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.backupCurrentState.getNSButton().setToolTip_("Will make a backup of the current layers in their respective backgrounds. Careful: will overwrite existing layer backgrounds.")
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Sync", sizeStyle="regular", callback=self.EnhanceCompatibilityMain)
		self.w.runButton.getNSButton().setToolTip_("If the button is greyed out, turn on at least one of the options above.")
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Enhance Compatibility’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def checkGUI(self, sender=None):
		allPrefs = self.prefDict.keys()
		shouldEnable = any([self.pref(k) for k in allPrefs])
		self.w.runButton.enable(shouldEnable)
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
			self.checkGUI()
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
			self.checkGUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def EnhanceCompatibilityMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Enhance Compatibility’ could not write preferences.")
			
			# read prefs:
			backupCurrentState = self.pref("backupCurrentState")
			fixType = self.pref("fixType")
			fixConnection = self.pref("fixConnection")
			realignHandles = self.pref("realignHandles")
			
			thisFont = Glyphs.font # frontmost font
			if Glyphs.font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Enhance Compatibility Report for {reportName}")
				
				for l1 in thisFont.selectedLayers:
					g = l1.parent
					print(f"\n🔤 {g.name}\n")
					for l2 in g.layers:
						if l2 == l1:
							continue
		
						print(f" ➡️ Layer ‘{l2.name}’")
						if l1.compareString() != l2.compareString():
							print(" 🚫 Not compatible. Skipping.\n")
							continue

						if backupCurrentState:
							l2.contentToBackgroundCheckSelection_keepOldBackground_(False, False)
							print(" 💕 Backed up in background.")
	
						for pi, p1 in enumerate(l1.paths):
							p2 = l2.paths[pi]
							for ni, n1 in enumerate(p1.nodes):
								n2 = p2.nodes[ni]
								if fixType and n1.type != n2.type:
									print(f" ✅ TYPE p{pi} n{ni}: should be {n1.type}, but is {n2.type}")
									n2.type = n1.type
								if fixConnection and n1.connection != n2.connection:
									print(f" ✅ CONNECTION p{pi} n{ni}: should be {n1.connection}, but is {n2.connection}")
									n2.connection = n1.connection
	
						if realignHandles:
							countRealigned = straightenBCPs(l2)
							if countRealigned:
								print(f" ✅ Realigned {countRealigned} node{'' if countRealigned==1 else 's'}.")
			
						print(" 🆗\n")

			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Enhance Compatibility Error: {e}")
			import traceback
			print(traceback.format_exc())

EnhanceCompatibility()