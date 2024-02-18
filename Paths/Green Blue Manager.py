# MenuTitle: Green Blue Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Define an angle above which a node will be set to blue, below which it will be set to green.
"""

import vanilla
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSControlLayer, GSOFFCURVE, GSSMOOTH, GSSHARP, Message
from mekkablue import mekkaObject
from mekkablue.geometry import angle

if Glyphs.versionNumber >= 3:
	from GlyphsApp import GlyphsPathPlugin


class GreenBlueManager(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"thresholdAngle": 11,
		"completeFont": 1,
		"fixGreenBlue": 1,
		"realignHandles": 1,
		"reportInMacroWindow": 1,
		"reportInMacroWindowVerbose": 0,
		"shouldMark": 0,
		"allMasters": 0,
		"scope": 0,
		"reuseTab": 1,
		"exclude": ".ornm, BlackIndex, Heart, apple",
	}

	def __init__(self):
		self.Tool = GlyphsPathPlugin.alloc().init()

		# Window 'self.w':
		windowWidth = 300
		windowHeight = 310
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Green Blue Manager",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 5, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, lineHeight * 2), "Validates the connection state of nodes, green vs. blue, according to the angle between them. Optionally corrects green/blue state and handles.", sizeStyle='small', selectable=True)
		linePos += lineHeight * 2.5

		self.w.thresholdAngleText = vanilla.TextBox((inset, linePos, 110, 14), "Threshold Angle:", sizeStyle='small', selectable=True)
		self.w.thresholdAngle = vanilla.EditText((inset + 110, linePos - 3, -inset, 19), "11", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.fixGreenBlue = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Fix green vs. blue connection for on-curves", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.fixGreenBlue.getNSButton().setToolTip_("Sets the green/blue state of an on-curve node according to the connection angle. Any connection below the threshold angle will be green, otherwise blue. Deselect both Fix and Realign options for a new tab with all glyphs that have nodes with wrong connections according to the threshold angle.")
		linePos += lineHeight

		self.w.realignHandles = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Realign handles attached to green nodes", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.realignHandles.getNSButton().setToolTip_("If a BCP (grey handle) follows a green node, it will be aligned to the previous two points. Deselect both Fix and Realign options for a new tab with all glyphs that have nodes with wrong connections according to the threshold angle.")
		linePos += lineHeight

		self.w.allMasters = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Process ⚠️ ALL masters of selected glyphs", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allMasters.getNSButton().setToolTip_("If checked, will go through all master layers and special layers of selected glyphs. If unchecked, will only process the currently visible layer.")
		linePos += lineHeight

		self.w.completeFont = vanilla.CheckBox((inset, linePos - 1, 155, 20), "Process ⚠️ ALL glyphs in", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.completeFont.getNSButton().setToolTip_("If checked, will go through all active (i.e., master, brace and bracket) layers of all glyphs. If unchecked, will only go through selected layers. Careful: can take a minute.")
		self.w.scope = vanilla.PopUpButton((inset + 155, linePos, -inset, 17), ("frontmost font", "⚠️ ALL open fonts"), sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight

		self.w.excludeText = vanilla.TextBox((inset, linePos, 115, 14), "Exclude glyphs with:", sizeStyle="small", selectable=True)
		self.w.exclude = vanilla.EditText((inset + 115, linePos - 3, -inset, 19), ".ornm, BlackIndex, Heart, apple", callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.reportInMacroWindow = vanilla.CheckBox((inset, linePos - 1, 160, 20), "Report in Macro window", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportInMacroWindowVerbose = vanilla.CheckBox((inset + 160, linePos - 1, -inset, 20), "Verbose", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportInMacroWindow.getNSButton().setToolTip_("If enabled, will output a report in Window > Macro Panel.")
		self.w.reportInMacroWindowVerbose.getNSButton().setToolTip_("If enabled, will output a verbose (detailed) report in Window > Macro Panel.")
		linePos += lineHeight

		self.w.shouldMark = vanilla.CheckBox((inset, linePos - 1, 160, 20), "Mark affected nodes", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.shouldMark.getNSButton().setToolTip_("If enabled, will mark (intended) node type changes as follows: 💚=SMOOTH 🔷=CORNER.")
		self.w.reuseTab = vanilla.CheckBox((inset + 160, linePos - 1, -inset, 20), "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.getNSButton().setToolTip_("If enabled, will use the current tab for output, and only open a new tab if there is none open.")
		linePos += lineHeight

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)  # set progress indicator to zero
		linePos += lineHeight

		self.w.processingText = vanilla.TextBox((inset, linePos + 2, -120 - inset, 14), "", sizeStyle='small', selectable=True)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Treat Points", callback=self.GreenBlueManagerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		self.updateUI()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		if not self.w.realignHandles.get() and not self.w.fixGreenBlue.get():
			self.w.runButton.setTitle("Open Tab")
		else:
			self.w.runButton.setTitle("Treat Nodes")

		self.w.reportInMacroWindowVerbose.enable(self.w.reportInMacroWindow.get())
		self.w.scope.enable(self.w.completeFont.get())

	def realignLayer(self, layer, shouldRealign=False, shouldReport=False, shouldVerbose=False):

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

		def triplet(n1, n2, n3):
			return (n1.position, n2.position, n3.position)

		handleCount = 0
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
							oldPos = triplet(smoothen, center, opposite)
							p.setSmooth_withCenterNode_oppositeNode_(
								smoothen, center, opposite,
							)
							if oldPos != triplet(smoothen, center, opposite):
								handleCount += 1
							if not shouldRealign:
								smoothen.position, center.position, opposite.position = oldPos
							break
					if smoothen == center == opposite is None:
						oldPos = triplet(n, nn, pn)
						n.position = closestPointOnLine(
							n.position, nn, pn,
						)
						if oldPos != triplet(n, nn, pn):
							handleCount += 1
						if not shouldRealign:
							n.position, nn.position, pn.position = oldPos

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
					oldPos = triplet(smoothen, center, opposite)
					p.setSmooth_withCenterNode_oppositeNode_(
						smoothen, center, opposite,
					)
					if oldPos != triplet(smoothen, center, opposite):
						handleCount += 1
					if not shouldRealign:
						smoothen.position, center.position, opposite.position = oldPos

		if shouldReport and shouldVerbose:
			if handleCount:
				if shouldRealign:
					print(f'   ⚠️ Realigned {handleCount} handle{"" if handleCount == 1 else "s"}.')
				else:
					print(f'   ❌ {handleCount} handle{"" if handleCount == 1 else "s"} are unaligned.')
			else:
				print("   ✅ All BCPs OK.")

		return handleCount

	def fixConnectionsOnLayer(self, thisLayer, shouldFix=False, shouldReport=False, shouldVerbose=False):
		thresholdAngle = self.prefFloat("thresholdAngle")
		shouldMark = self.prefBool("shouldMark")
		layerCount = 0
		for thisPath in thisLayer.paths:
			for i, thisNode in enumerate(thisPath.nodes):
				if thisNode.type == GSOFFCURVE:
					hotNode = None
					if thisNode.prevNode.type != GSOFFCURVE:
						hotNode = thisNode.prevNode
					elif thisNode.nextNode.type != GSOFFCURVE:
						hotNode = thisNode.nextNode
					if hotNode is not None:
						if hotNode.prevNode and hotNode.nextNode:
							angleDiff = abs(angle(hotNode.prevNode, hotNode) - angle(hotNode, hotNode.nextNode)) % 360
							if (angleDiff <= thresholdAngle or angleDiff >= 360 - thresholdAngle) and hotNode.connection != GSSMOOTH:
								layerCount += 1
								if shouldFix:
									hotNode.connection = GSSMOOTH
								if shouldMark:
									hotNode.name = "💚"
							elif (thresholdAngle < angleDiff < 360 - thresholdAngle) and hotNode.connection != GSSHARP:
								layerCount += 1
								if shouldFix:
									hotNode.connection = GSSHARP
								if shouldMark:
									hotNode.name = "🔷"

		if shouldReport and shouldVerbose:
			print(f"{thisLayer.parent.name}, layer '{thisLayer.name}'")
			if layerCount:
				if shouldFix:
					print(f'   ⚠️ Fixed {layerCount} connection{"" if layerCount == 1 else "s"}')
				else:
					print(f'   ❌ {layerCount} wrong connection{"" if layerCount == 1 else "s"}')
			else:
				print("   ✅ All connections OK.")

		return layerCount

	def GreenBlueManagerMain(self, sender):
		try:
			shouldReport = self.pref("reportInMacroWindow")
			if shouldReport:
				Glyphs.clearLog()

			scope = self.pref("scope")
			if not Glyphs.font:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			elif scope == 1:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )

			for thisFont in theseFonts:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."

				print(f"GreenBlueManager Report for {reportName}")
				print()

				shouldRealign = self.pref("realignHandles")
				shouldVerbose = self.pref("reportInMacroWindowVerbose")
				shouldFix = self.pref("fixGreenBlue")
				reuseTab = self.pref("reuseTab")
				exclude = [x.strip() for x in self.pref("exclude").split(",")]

				# determine which layers to process:
				layersToBeProcessed, glyphsToBeProcessed = [], []
				if self.pref("completeFont"):
					mID = thisFont.selectedFontMaster.id
					for thisGlyph in thisFont.glyphs:
						if any([x in thisGlyph.name for x in exclude]):
							print(f"Skipping {thisGlyph.name}: excluded as requested.")
							continue
						if self.pref("allMasters"):
							for thisLayer in thisGlyph.layers:
								if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
									layersToBeProcessed.append(thisLayer)
						else:
							thisLayer = thisGlyph.layers[mID]
							layersToBeProcessed.append(thisLayer)
				else:
					if self.pref("allMasters"):
						glyphsToBeProcessed = [layer.parent for layer in thisFont.selectedLayers if layer.parent and not isinstance(layer, GSControlLayer)]
						for g in glyphsToBeProcessed:
							for layer in g.layers:
								if layer.isSpecialLayer or layer.isMasterLayer:
									layersToBeProcessed.append(layer)
					else:
						layersToBeProcessed = thisFont.selectedLayers

				if not layersToBeProcessed:
					print(
						"❌ Green Blue Manager Error: No Selection",
						"\n⚠️ No glyphs selected for processing. Either select some glyphs or select the option ‘Process ALL glyphs’.",
					)
				else:
					numberOfLayers = len(layersToBeProcessed)
					affectedLayersFixedConnections = []
					affectedLayersRealignedHandles = []

					# process layers:
					for i, thisLayer in enumerate(layersToBeProcessed):
						if isinstance(thisLayer, GSControlLayer):
							thisGlyph = thisLayer.parent
							statusMessage = f"Processing: {thisGlyph.name}"
							if shouldReport and shouldVerbose:
								print(statusMessage)
							self.w.processingText.set(statusMessage)
							self.w.progress.set(100.0 / numberOfLayers * i)

							numberOfFixes = self.fixConnectionsOnLayer(thisLayer, shouldFix=shouldFix)
							if numberOfFixes:
								affectedLayersFixedConnections.append(thisLayer)

							numberOfAligns = self.realignLayer(thisLayer, shouldRealign, shouldReport, shouldVerbose)
							if numberOfAligns:
								affectedLayersRealignedHandles.append(thisLayer)

					self.w.progress.set(100)
					statusMessage = "Processed %i layer%s." % (
						numberOfLayers,
						"" if numberOfLayers == 1 else "s",
					)
					self.w.processingText.set(statusMessage)

					titles = []
					if shouldFix:
						titles.append("Fixed green-blue status")
					else:
						titles.append("Wrong green-blue status")
					if shouldRealign:
						titles.append("Aligned BCPs")
					else:
						titles.append("Unaligned BCPs")
					# onlyReport = not shouldFix and not shouldRealign

					if shouldReport:
						if affectedLayersFixedConnections:
							print(f"\n{titles[0]} in following layers:")
							for fixedLayer in affectedLayersFixedConnections:
								print(f"   {fixedLayer.parent.name}, layer '{fixedLayer.name}'")
						if affectedLayersRealignedHandles:
							print(f"\n{titles[1]} in following layers:")
							for fixedLayer in affectedLayersRealignedHandles:
								print(f"   {fixedLayer.parent.name}, layer '{fixedLayer.name}'")
						print(f"\nDone. {statusMessage}")
						# Glyphs.showMacroWindow()

					if numberOfLayers == 1 and len(glyphsToBeProcessed) != 1 and thisFont.currentTab:
						# if only one layer was processed, do not open new tab:
						thisFont.currentTab.forceRedraw()
						if affectedLayersFixedConnections or affectedLayersRealignedHandles:
							message = ""
							if affectedLayersFixedConnections:
								message += f"• {titles[0]}\n"
							if affectedLayersRealignedHandles:
								message += f"• {titles[1]}\n"
							print(message)
							continue

					else:
						# opens new Edit tab:
						if affectedLayersFixedConnections or affectedLayersRealignedHandles:
							if reuseTab and thisFont.currentTab:
								outputTab = thisFont.currentTab
								outputTab.text = "\n"
							else:
								outputTab = thisFont.newTab()

							if affectedLayersFixedConnections:
								outputTab.text += f"{titles[0]}:\n"
								for affectedLayer in affectedLayersFixedConnections:
									outputTab.layers.append(affectedLayer)
							if affectedLayersFixedConnections and affectedLayersRealignedHandles:
								outputTab.text += "\n\n"
							if affectedLayersRealignedHandles:
								outputTab.text += f"{titles[1]}:\n"
								for affectedLayer in affectedLayersRealignedHandles:
									outputTab.layers.append(affectedLayer)
							continue
					continue

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"\nGreen Blue Manager Error: {e}")
			import traceback
			print(traceback.format_exc())
			print()


GreenBlueManager()
