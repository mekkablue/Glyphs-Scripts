# MenuTitle: Rewire Fire
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds, selects and marks duplicate coordinates. Two nodes on the same position typically can be rewired with Reconnect Nodes.
"""

import vanilla
from Foundation import NSPoint, NSIntersectsRect
from GlyphsApp import Glyphs, GSAnnotation, GSOFFCURVE, CIRCLE, Message, distance
from mekkablue import mekkaObject


def isOnLine(p1, p2, p3, threshold=2.01**0.5):
	"""
	Returns True if p3 is on and within p1-p2.
	And not off more than threshold.
	"""
	x1, y1 = p1.x, p1.y
	x2, y2 = p2.x, p2.y
	x3, y3 = p3.x, p3.y

	dx = x2 - x1
	dy = y2 - y1
	d2 = dx**2 + dy**2
	nx = ((x3 - x1) * dx + (y3 - y1) * dy) / d2
	offset = distance(p3, NSPoint(dx * nx + x1, dy * nx + y1))
	if offset < threshold:
		if 0.0 < nx < 1.0:
			return True

	return False


class RewireFire(mekkaObject):
	prefDict = {
		"setFireToNode": 1,
		"dynamiteForOnSegment": 1,
		"tolerateZeroSegments": 0,
		"includeNonExporting": 1,
		"shouldSelect": 1,
		"reuseTab": 1,
		"allFonts": 0,
	}

	duplicateMarker = "🔥"
	onSegmentMarker = "🧨"

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 240
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			f"{self.duplicateMarker} Rewire Fire {self.onSegmentMarker}",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Finds candidates for rewiring with Reconnect Nodes.", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.setFireToNode = vanilla.CheckBox((inset, linePos - 1, -inset, 20), f"Mark duplicate nodes with fire emoji {self.duplicateMarker}", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.setFireToNode.getNSButton().setToolTip_("Finds different on-curve nodes that share the same coordinates. Emoji will be added as a node name. Node names may disappear after reconnection and path cleanup.")
		linePos += lineHeight

		self.w.tolerateZeroSegments = vanilla.CheckBox((inset * 2, linePos - 1, -inset * 2, 20), "Tolerate duplicate if it is neighboring node (OTVar)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.tolerateZeroSegments.getNSButton().setToolTip_("If node coordinates within the same segment share the same coordinates, they will not be marked with a fire emoji. Makes sense in variable fonts, where segments need to disappear in a point in one master.")
		linePos += lineHeight

		# DISABLED
		# self.w.markWithCircle = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Circle duplicate coordinates with annotation ⭕️", value=False, callback=self.SavePreferences, sizeStyle='small' )
		# self.w.markWithCircle.getNSButton().setToolTip_("Circle annotations remain after reconnecting the nodes.")
		# linePos += lineHeight

		self.w.dynamiteForOnSegment = vanilla.CheckBox((inset, linePos - 1, -inset, 20), f"Mark nodes on top of line segments with dynamite emoji {self.onSegmentMarker}", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.dynamiteForOnSegment.getNSButton().setToolTip_("Finds on-curve nodes that are located on line segments between (other) two on-curve nodes. Emoji will be added as a node name. Node names may disappear after reconnection and path cleanup.")
		linePos += lineHeight

		self.w.shouldSelect = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Select nodes for rewiring on affected glyph layers", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.shouldSelect.getNSButton().setToolTip_("If nodes are found, will reset the layer selection and select only the affected nodes. In the best case, you should be able to right-click, hold down the Opt (Alt) key, and choose Reconnect Nodes on All Masters from the context menu.")
		linePos += lineHeight

		self.w.includeNonExporting = vanilla.CheckBox((inset, linePos - 1, 200, 20), "Include non-exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.getNSButton().setToolTip_("Also check in glyphs that are not set to export. Recommended if you have modular components in the font.")
		self.w.reuseTab = vanilla.CheckBox((inset + 200, linePos - 1, -inset, 20), "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.getNSButton().setToolTip_("If enabled, will only open a new tab if there is none open yet. Otherwise will always open a new tab.")
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "⚠️ Work through ALL open fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allFonts.getNSButton().setToolTip_("If enabled, will look in all currently opened fonts.")
		linePos += lineHeight

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)  # set progress indicator to zero
		linePos += lineHeight

		self.w.statusText = vanilla.TextBox((inset, -20 - inset, -80 - inset, -inset), "🤖 Ready.", sizeStyle='small', selectable=True)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Fire", sizeStyle='regular', callback=self.RewireFireMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		anyOptionSelected = self.w.setFireToNode.get() or self.w.dynamiteForOnSegment.get()
		self.w.runButton.enable(anyOptionSelected)
		self.w.reuseTab.enable(self.w.openTabWithAffectedLayers.get())
		self.w.tolerateZeroSegments.enable(self.w.setFireToNode.get())

	def circleInLayerAtPosition(self, layer, position, width=25.0):
		circle = GSAnnotation()
		circle.type = CIRCLE
		circle.position = position
		circle.width = width
		layer.annotations.append(circle)

	def findNodesOnLines(self, layer, dynamiteForOnSegment=True, shouldSelect=True):
		affectedNodes = []

		# find line segments:
		for p in layer.paths:
			if p.closed:
				firstPathBounds = p.bounds
				for n1 in p.nodes:
					n2 = n1.nextNode
					if n2 and n1.type != GSOFFCURVE and n2.type != GSOFFCURVE:
						p1 = n1.position
						p2 = n2.position

						# make sure it is not a zero-lenth segment:
						if p1 != p2:

							# find other nodes that are exactly on the line segment:
							for pp in layer.paths:
								secondPathBounds = pp.bounds
								if pp.closed and NSIntersectsRect(firstPathBounds, secondPathBounds):
									for n3 in pp.nodes:
										if n3 != n1 and n3 != n2 and n3.type != GSOFFCURVE:
											p3 = n3.position
											# find projection with threshold:
											if isOnLine(p1, p2, p3):
												affectedNodes.append(n3)

		if affectedNodes:
			thisGlyph = layer.parent
			print()
			print(f"🔠 {thisGlyph.name}, layer ‘{layer.name}’: {len(affectedNodes)} nodes on line segments")
			for node in affectedNodes:
				print(f"   {self.onSegmentMarker} x {node.x}, y {node.y}")

			for n3 in affectedNodes:
				if dynamiteForOnSegment:
					n3.name = self.onSegmentMarker
				if shouldSelect:
					layer.selection.append(n3)
			return True
		else:
			return False

	def findDuplicates(self, thisLayer, setFireToNode=True, markWithCircle=False, shouldSelect=True, tolerateZeroSegments=False):
		allCoordinates = []
		duplicateCoordinates = []
		for thisPath in thisLayer.paths:
			for thisNode in thisPath.nodes:
				if thisNode.type != GSOFFCURVE:
					if thisNode.position in allCoordinates:
						if not tolerateZeroSegments or thisNode.position not in (thisNode.nextNode.position, thisNode.prevNode.position):
							# select node:
							if shouldSelect and thisNode not in thisLayer.selection:
								thisLayer.selection.append(thisNode)
							duplicateCoordinates.append(thisNode.position)
							if setFireToNode:
								thisNode.name = self.duplicateMarker
					else:
						allCoordinates.append(thisNode.position)
						if thisNode.name == self.duplicateMarker:
							thisNode.name = None

		if duplicateCoordinates:
			thisGlyph = thisLayer.parent
			print()
			print(f"🔠 {thisGlyph.name}, layer ‘{thisLayer.name}’: {len(duplicateCoordinates)} duplicates")
			for dupe in duplicateCoordinates:
				print(f"   {self.duplicateMarker} x {dupe.x}, y {dupe.y}")

			# if markWithCircle:
			# 	coords = set([(p.x,p.y) for p in duplicateCoordinates])
			# 	for dupeCoord in coords:
			# 		x,y = dupeCoord
			# 		self.circleInLayerAtPosition( thisLayer, NSPoint(x,y) )

			return True

		else:
			return False

	def RewireFireMain(self, sender):
		try:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			includeNonExporting = self.pref("includeNonExporting")
			setFireToNode = self.pref("setFireToNode")
			shouldSelect = self.pref("shouldSelect")
			dynamiteForOnSegment = self.pref("dynamiteForOnSegment")
			tolerateZeroSegments = self.pref("tolerateZeroSegments")
			# markWithCircle = self.pref("markWithCircle")

			if len(Glyphs.fonts) == 0:
				Message(
					title="No font open",
					message="This script requires at least one font open.",
					OKButton="Meh",
				)
				return

			if self.pref("allFonts"):
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )

			totalCountAffectedLayers = 0
			totalCountExaminedGlyphs = 0
			for fontIndex, thisFont in enumerate(theseFonts):
				print(f"🌟 Rewire Fire Report for {thisFont.familyName}")
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ Warning: file has not been saved yet.")

				affectedLayers = []
				numGlyphs = float(len(thisFont.glyphs))

				for i, thisGlyph in enumerate(thisFont.glyphs):
					fontSector = 100 / len(theseFonts)
					self.w.progress.set(int(fontIndex * fontSector + i / numGlyphs * fontSector))
					self.w.statusText.set(f"📄 {fontIndex + 1} 🔠 {thisGlyph.name}")

					if thisGlyph.export or includeNonExporting:
						for thisLayer in thisGlyph.layers:
							if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
								# reset selection if necessary:
								if shouldSelect:
									thisLayer.selection = None

								# mark and select duplicate nodes:
								if setFireToNode and self.findDuplicates(thisLayer, shouldSelect=shouldSelect, tolerateZeroSegments=tolerateZeroSegments):
									affectedLayers.append(thisLayer)

								# mark and select nodes on line segments:
								if dynamiteForOnSegment and self.findNodesOnLines(thisLayer, shouldSelect=shouldSelect):
									if thisLayer not in affectedLayers:
										affectedLayers.append(thisLayer)

				if affectedLayers:
					# opens new Edit tab:
					if thisFont.currentTab and self.pref("reuseTab"):
						thisFont.currentTab.layers = affectedLayers
					else:
						newTab = thisFont.newTab()
						newTab.layers = affectedLayers

				totalCountAffectedLayers += len(affectedLayers)
				totalCountExaminedGlyphs += len(thisFont.glyphs)

			if totalCountAffectedLayers == 0:
				Message(
					title="Rewire Fire: All Good",
					message=f"Could not find any nodes for rewiring in a total of {totalCountExaminedGlyphs} glyphs in {len(theseFonts)} font{'s' if len(theseFonts) > 1 else ''} examined.",
					OKButton="😇 Cool",
				)
			else:
				Message(
					title="Rewire Fire found issues",
					message=f"Found issues on {totalCountAffectedLayers} layers in a total of {totalCountExaminedGlyphs} glyphs in {len(theseFonts)} font{'s' if len(theseFonts) > 1 else ''} examined.",
					OKButton=None,
				)

			self.w.progress.set(0)
			self.w.statusText.set("✅ Done.")

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Rewire Fire Error: {e}")
			import traceback
			print(traceback.format_exc())


RewireFire()
