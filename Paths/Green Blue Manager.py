#MenuTitle: Green Blue Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
if Glyphs.versionNumber >= 3:
	from GlyphsApp import GlyphsPathPlugin
__doc__ = """
Define an angle above which a node will be set to blue, below which it will be set to green.
"""

import vanilla, sys
from math import degrees, atan2
from Foundation import NSPoint, NSMutableArray, NSNumber

def angle(firstPoint, secondPoint):
	"""
	Returns the angle (in degrees) of the straight line between firstPoint and secondPoint,
	0 degrees being the second point to the right of first point.
	firstPoint, secondPoint: must be NSPoint or GSNode
	"""
	xDiff = secondPoint.x - firstPoint.x
	yDiff = secondPoint.y - firstPoint.y
	return degrees(atan2(yDiff, xDiff))

class GreenBlueManager(object):
	prefID = "com.mekkablue.GreenBlueManager"
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
		"reuseTab": 1,
	}

	def __init__(self):
		self.Tool = GlyphsPathPlugin.alloc().init()

		# Window 'self.w':
		windowWidth = 300
		windowHeight = 285
		windowWidthResize = 300 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Green Blue Manager", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName="com.mekkablue.GreenBlueManager.mainwindow" # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 5, 15, 22
		self.w.descriptionText = vanilla.TextBox(
			(inset, linePos + 2, -inset, lineHeight * 2),
			"Validates the connection state of nodes, green vs. blue, according to the angle between them. Optionally corrects green/blue state and handles.",
			sizeStyle='small',
			selectable=True
			)
		linePos += lineHeight * 2.5

		self.w.thresholdAngleText = vanilla.TextBox((inset, linePos, 110, 14), "Threshold Angle:", sizeStyle='small', selectable=True)
		self.w.thresholdAngle = vanilla.EditText((inset + 110, linePos - 3, -inset, 19), "11", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.fixGreenBlue = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Fix green vs. blue connection for on-curves", value=True, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.fixGreenBlue.getNSButton().setToolTip_(
			"Sets the green/blue state of an on-curve node according to the connection angle. Any connection below the threshold angle will be green, otherwise blue. Deselect both Fix and Realign options for a new tab with all glyphs that have nodes with wrong connections according to the threshold angle."
			)
		linePos += lineHeight

		self.w.realignHandles = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Realign handles attached to green nodes", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.realignHandles.getNSButton().setToolTip_(
			"If a BCP (grey handle) follows a green node, it will be aligned to the previous two points. Deselect both Fix and Realign options for a new tab with all glyphs that have nodes with wrong connections according to the threshold angle."
			)
		linePos += lineHeight
		
		self.w.allMasters = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Process ⚠️ ALL masters of selected glyphs", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allMasters.getNSButton().setToolTip_("If checked, will go through all master layers and special layers of selected glyphs. If unchecked, will only process the currently visible layer.")
		linePos += lineHeight

		self.w.completeFont = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Process ⚠️ ALL glyphs in font", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.completeFont.getNSButton().setToolTip_(
			"If checked, will go through all active (i.e., master, brace and bracket) layers of all glyphs. If unchecked, will only go through selected layers. Careful: can take a minute."
			)
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
		self.w.progress.set(0) # set progress indicator to zero
		linePos += lineHeight

		self.w.processingText = vanilla.TextBox((inset, linePos + 2, -120 - inset, 14), "", sizeStyle='small', selectable=True)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Treat Points", sizeStyle='regular', callback=self.GreenBlueManagerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Green Blue Manager' could not load preferences. Will resort to defaults")

		self.checkGUI()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]

	def checkGUI(self, sender=None):
		if not self.w.realignHandles.get() and not self.w.fixGreenBlue.get():
			self.w.runButton.setTitle("Open Tab")
		else:
			self.w.runButton.setTitle("Treat Nodes")

		self.w.reportInMacroWindowVerbose.enable(self.w.reportInMacroWindow.get())

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

	def realignLayer(self, thisLayer, shouldRealign=False, shouldReport=False, shouldVerbose=False):
		moveForward = NSPoint(1, 0)
		moveBackward = NSPoint(-1, 0)
		noModifier = NSNumber.numberWithUnsignedInteger_(0)
		layerCount = 0

		if thisLayer:
			for thisPath in thisLayer.paths:
				oldPathCoordinates = [n.position for n in thisPath.nodes]
				for i, thisNode in enumerate(thisPath.nodes):
					if thisNode.type == GSOFFCURVE:
						# oldPosition = NSPoint(thisNode.position.x, thisNode.position.y)
						oncurve = None
						if thisNode.prevNode.type != GSOFFCURVE:
							oncurve = thisNode.prevNode
							opposingPoint = oncurve.prevNode
						elif thisNode.nextNode.type != GSOFFCURVE:
							oncurve = thisNode.nextNode
							opposingPoint = oncurve.nextNode

						handleStraight = (oncurve.x - thisNode.x) * (oncurve.y - thisNode.y) == 0.0
						if oncurve and oncurve.smooth and not handleStraight:
							# thisNode = angled handle, straighten it
							thisPath.setSmooth_withCenterPoint_oppositePoint_(
								thisNode,
								oncurve.position,
								opposingPoint.position,
								)
						elif oncurve and opposingPoint and oncurve.smooth and handleStraight and opposingPoint.type == GSOFFCURVE:
							# thisNode = straight handle: align opposite handle
							thisPath.setSmooth_withCenterPoint_oppositePoint_(
								opposingPoint,
								oncurve.position,
								thisNode.position,
								)
						else:
							selectedNode = NSMutableArray.arrayWithObject_(thisNode)
							thisLayer.setSelection_(selectedNode)
							self.Tool.moveSelectionLayer_shadowLayer_withPoint_withModifier_(thisLayer, thisLayer, moveForward, noModifier)
							self.Tool.moveSelectionLayer_shadowLayer_withPoint_withModifier_(thisLayer, thisLayer, moveBackward, noModifier)
							# TODO:
							# recode with GSPath.setSmooth_withCenterNode_oppositeNode_()

				for i, coordinate in enumerate(oldPathCoordinates):
					if thisPath.nodes[i].position != coordinate:
						layerCount += 1

						# put handle back if not desired by user:
						if not shouldRealign:
							thisPath.nodes[i].position = coordinate
		thisLayer.setSelection_(())

		if shouldReport and shouldVerbose:
			if layerCount:
				if shouldRealign:
					print(f'   ⚠️ Realigned {layerCount} handle{"" if layerCount == 1 else "s"}.')
				else:
					print(f'   ❌ {layerCount} handle{"" if layerCount == 1 else "s"} are unaligned.')
			else:
				print("   ✅ All BCPs OK.")

		return layerCount

	def fixConnectionsOnLayer(self, thisLayer, shouldFix=False, shouldReport=False, shouldVerbose=False):
		thresholdAngle = float(self.pref("thresholdAngle"))
		shouldMark = bool(self.pref("shouldMark"))
		layerCount = 0
		for thisPath in thisLayer.paths:
			for i, thisNode in enumerate(thisPath.nodes):
				if thisNode.type == OFFCURVE:
					hotNode = None
					if thisNode.prevNode.type != OFFCURVE:
						hotNode = thisNode.prevNode
					elif thisNode.nextNode.type != OFFCURVE:
						hotNode = thisNode.nextNode
					if not hotNode is None:
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

			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
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

				# determine which layers to process:
				layersToBeProcessed, glyphsToBeProcessed = [], []
				if self.pref("completeFont"):
					mID = thisFont.selectedFontMaster.id
					for thisGlyph in thisFont.glyphs:
						if self.pref("allMasters"):
							for thisLayer in thisGlyph.layers:
								if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
									layersToBeProcessed.append(thisLayer)
						else:
							thisLayer = thisGlyph.layers[mID]
							layersToBeProcessed.append(thisLayer)
				else:
					if self.pref("allMasters"):
						glyphsToBeProcessed = [l.parent for l in thisFont.selectedLayers if l.parent and not type(l)==GSControlLayer]
						for g in glyphsToBeProcessed:
							for l in g.layers:
								if l.isSpecialLayer or l.isMasterLayer:
									layersToBeProcessed.append(l)
					else:
						layersToBeProcessed = thisFont.selectedLayers

				if not layersToBeProcessed:
					Message(
						title="Green Blue Manager Error: No Selection",
						message="No glyphs selected for processing. Either select some glyphs or select the option ‘Process complete font’.",
						OKButton=None
						)
				else:
					numberOfLayers = len(layersToBeProcessed)
					affectedLayersFixedConnections = []
					affectedLayersRealignedHandles = []

					# process layers:
					for i, thisLayer in enumerate(layersToBeProcessed):
						if type(thisLayer) != GSControlLayer:
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
					onlyReport = not shouldFix and not shouldRealign

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
							# Floating notification:
							# Glyphs.showNotification(
							# 	"%s in %s:" % (
							# 		"Found Problems" if onlyReport else "Fixed Problems",
							# 		thisGlyph.name,
							# 		),
							# 	message,
							# 	)

							return

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

							# Floating notification:
							# Glyphs.showNotification(
							# 	"Green Blue Manager: %s" % (thisFont.familyName),
							# 	"• %s: %i layers\n• %s: %i layers" % (titles[0], len(affectedLayersFixedConnections), titles[1], len(affectedLayersRealignedHandles)),
							# 	)

							return
					# Floating notification:
					# Glyphs.showNotification(
					# 	"All OK in %s!" % thisGlyph.name,
					# 	"No unaligned handles or wrong connectifon types found in glyph %{e}"hisGlyph.name,
					# 	)

					return

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"\nGreen Blue Manager Error: {e}")
			import traceback
			print(traceback.format_exc())
			print()

GreenBlueManager()
