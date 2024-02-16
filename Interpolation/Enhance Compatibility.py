# MenuTitle: Enhance Compatibility
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Takes the current layer of each selected glyph, and propagates node types, node connections, realigns handles in technically compatible layers of the same glyph. Useful for fixing compatibility of glyphs that are shown to be compatible but still do not export.
"""

import vanilla
from AppKit import NSPoint
from GlyphsApp import Glyphs, GSSMOOTH, GSOFFCURVE, GSShapeTypePath, Message
from mekkablue import mekkaObject


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
				if smoothen == center == opposite is None:
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

			if oldCoords != (pn.position, n.position, nn.position):
				realigned += 1
	return realigned


class EnhanceCompatibility(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"fixType": True,
		"fixConnection": False,
		"removeEmptyPaths": True,
		"realignHandles": False,
		"backupCurrentState": False,
		"otherFont": False,
		"sourceFont": 0,
		"sourceMaster": 0,
	}
	currentFonts = []

	def __init__(self):
		# Window 'self.w':
		windowWidth = 380
		windowHeight = 220
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Enhance Compatibility",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -1, 14), "In compatible layers of selected glyphs, sync with selected layer:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.fixType = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Sync node types (oncurve vs. offcurve)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.fixType.getNSButton().setToolTip_("Will propagate the current layer’s node types (oncurve vs. offcurve) to other compatible layers. Useful in TT paths.")
		linePos += lineHeight

		self.w.fixConnection = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Sync node connection (corner vs. smooth)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.fixConnection.getNSButton().setToolTip_("Will propagate the current layer’s node connections (green vs. blue) to other compatible layers. Usually just cosmetic.")
		linePos += lineHeight

		self.w.removeEmptyPaths = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Remove empty paths", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.removeEmptyPaths.getNSButton().setToolTip_("Sometimes an invisible empty path (a path with no nodes) is blocking compatibility. This will remove those empty shapes.")
		linePos += lineHeight

		indent = 85
		self.w.otherFont = vanilla.CheckBox((inset, linePos - 1, indent, 20), "Source from", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.sourceFont = vanilla.PopUpButton((inset + indent, linePos, 160, 17), (), sizeStyle="small", callback=self.SavePreferences)
		self.w.sourceMaster = vanilla.PopUpButton((inset + indent + 165, linePos, -inset - 25, 17), (), sizeStyle="small", callback=self.SavePreferences)
		self.w.updateButton = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle="small", callback=self.updateCurrentFonts)
		tooltip = "As source glyph to sync node types and connections with, take glyph(s) with same name in this font, rather than the current font."
		self.w.updateButton.getNSButton().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.realignHandles = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Realign smooth connections (prefer orthogonals)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.realignHandles.getNSButton().setToolTip_("Will realign handles (BCPs) next to a smooth connection (green node). Or, if applicable, move smooth oncurves (green nodes) on the line between its surrounding handles.")
		linePos += lineHeight

		self.w.backupCurrentState = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Backup layers in background", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.backupCurrentState.getNSButton().setToolTip_("Will make a backup of the current layers in their respective backgrounds. Careful: will overwrite existing layer backgrounds.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Sync", sizeStyle="regular", callback=self.EnhanceCompatibilityMain)
		self.w.runButton.getNSButton().setToolTip_("If the button is greyed out, turn on at least one of the options above.")
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		self.updateCurrentFonts()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		excludeKeys = ("otherFont", "sourceFont", "sourceMaster")
		allPrefs = [k for k in self.prefDict.keys() if k not in excludeKeys]
		shouldEnable = any([self.pref(k) for k in allPrefs])
		self.w.runButton.enable(shouldEnable)

		shouldEnable = self.w.otherFont.get()
		for popup in (self.w.sourceFont, self.w.sourceMaster):
			popup.enable(shouldEnable)

	def updateCurrentFonts(self, sender=None):
		self.currentFonts = [f for f in Glyphs.fonts if f != Glyphs.font]  # all except frontmost font
		self.w.sourceFont.setItems([f"{f.familyName}, {len(f.glyphs)} glyphs ({f.filepath.lastPathComponent() if f.filepath else 'unsaved'})" for f in self.currentFonts])
		if len(self.currentFonts) <= self.pref("sourceFont"):
			self.w.sourceFont.set(0)
		else:
			self.w.sourceFont.set(self.pref("sourceFont"))
		self.updateCurrentMaster()
		self.SavePreferences()

	def updateCurrentMaster(self, sender=None):
		fontIndex = self.w.sourceFont.get()
		print("fontIndex", fontIndex)
		if len(self.currentFonts) > max(fontIndex, 0):
			font = self.currentFonts[fontIndex]
			masters = font.masters
			self.w.sourceMaster.setItems([m.name for m in masters])
		self.w.sourceMaster.set(0)

	def EnhanceCompatibilityMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			# read prefs:
			backupCurrentState = self.pref("backupCurrentState")
			fixType = self.pref("fixType")
			fixConnection = self.pref("fixConnection")
			removeEmptyPaths = self.pref("removeEmptyPaths")
			realignHandles = self.pref("realignHandles")
			otherFont = self.pref("otherFont")
			sourceFont = self.pref("sourceFont")
			sourceMaster = self.pref("sourceMaster")

			thisFont = Glyphs.font  # frontmost font
			if Glyphs.font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Enhance Compatibility Report for {reportName}")

				for selectedLayer in thisFont.selectedLayers:
					g = selectedLayer.parent
					print(f"\n🔤 {g.name}\n")

					if otherFont:
						sourceFont = self.currentFonts[self.prefInt("sourceFont")]
						sourceMaster = sourceFont.masters[self.prefInt("sourceMaster")]
						l1 = sourceFont.glyphs[g.name].layers[sourceMaster.id]
					else:
						l1 = selectedLayer

					# remove empty shapes first:
					for l2 in g.layers:
						if removeEmptyPaths:
							for s in l2.shapes:
								if s.shapeType == GSShapeTypePath and not s.nodes:
									l2.removeShape_(s)
									print(f" 🫙 Removed empty path on {l2.name}")

					# second run, check for compatibility:
					for l2 in g.layers:
						if l2 == l1:
							continue

						print(f" ➡️ Layer ‘{l2.name}’")
						if len(l1.compareString()) != len(l2.compareString()):
							print(" 🚫 Not compatible due to different point or shape number. Skipping.\n")
							continue

						if backupCurrentState:
							l2.contentToBackgroundCheckSelection_keepOldBackground_(False, False)
							print(" 💕 Backed up in background.")

						for pi, p1 in enumerate(l1.paths):
							p2 = l2.paths[pi]
							if len(p1.nodes) != len(p2.nodes):
								continue
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
								print(f" ✅ Realigned {countRealigned} node{'' if countRealigned == 1 else 's'}.")

						print(" 🆗\n")

			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Enhance Compatibility Error: {e}")
			import traceback
			print(traceback.format_exc())


EnhanceCompatibility()
