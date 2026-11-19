# MenuTitle: Green Blue Manager
__doc__ = """
Define an angle above which a node will be set to blue, below which it will be set to green. In Glyphs 4, green nodes between two curves can also be turned into star nodes and back.
"""

import objc
import vanilla
from AppKit import NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSWindowStyleMaskResizable
from Foundation import NSPoint, NSSize
from GlyphsApp import Glyphs, GSControlLayer, GSOFFCURVE, GSSMOOTH, GSSHARP, Message
from mekkablue import mekkaObject, reportFontName, SteppingEditText, decimalFormatter, UpdateButton
from mekkablue.geometry import angle

GlyphsPathPlugin = objc.lookUpClass("GlyphsPathPlugin")

starNodeConnection = 102  # value of node.connection for star nodes (Glyphs 4); green nodes are GSSMOOTH (100)


class GreenBlueManager(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"thresholdAngle": 11,
		"fixGreenBlue": 1,
		"realignHandles": 1,
		"openTab": 1,
		"reportInMacroWindow": 1,
		"reportInMacroWindowVerbose": 0,
		"shouldMark": 0,
		"layerScope": 0,  # 0 = selected layers, 1 = all masters of selected glyphs, 2 = all glyphs on current master, 3 = all glyphs in font, 4 = all glyphs in all open fonts
		"reuseTab": 1,
		"exclude": ".ornm, BlackIndex, Heart, apple",
	}

	def __init__(self):
		self.Tool = GlyphsPathPlugin.new()

		# star nodes exist in Glyphs 4 and later only:
		self.hasStarNodes = Glyphs.versionNumber >= 4.0
		if self.hasStarNodes:
			self.prefDict = {**self.prefDict, "starNodes": 0, "starNodesAction": 0}

		# Window 'self.w':
		windowWidth = 440
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Green Blue Manager",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Validates the connection state of nodes, green vs. blue, according to the angle between them. Optionally corrects green/blue state and handles.", sizeStyle='small', selectable=True)
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		formatter = decimalFormatter(0, 180)
		self.w.thresholdAngleText = vanilla.TextBox("auto", "Threshold angle:", sizeStyle='small', selectable=True)
		self.w.thresholdAngle = SteppingEditText("auto", self.prefDict["thresholdAngle"], callback=self.SavePreferences, sizeStyle='small', formatter=formatter)
		thresholdTooltip = "Connection angles up to this value (in degrees) become green, larger ones blue."
		self.w.thresholdAngleText.setToolTip(thresholdTooltip)
		self.w.thresholdAngle.setToolTip(thresholdTooltip)

		self.w.fixGreenBlue = vanilla.CheckBox("auto", "Fix green vs. blue connection for on-curves", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.fixGreenBlue.setToolTip("Sets on-curve nodes green or blue according to the threshold angle. With all treatments off, only opens a tab with the affected layers.")

		self.w.realignHandles = vanilla.CheckBox("auto", "Realign handles attached to green nodes", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.realignHandles.setToolTip("Aligns the handles next to green nodes. With all treatments off, only opens a tab with the affected layers.")

		if self.hasStarNodes:
			self.w.starNodes = vanilla.CheckBox("auto", "Star nodes", value=False, callback=self.SavePreferences, sizeStyle='small')
			starNodesTooltip = "Converts between green and star nodes. Only affects nodes between two curves. Raises the file format version to 4 if needed."
			self.w.starNodes.setToolTip(starNodesTooltip)
			self.w.starNodesAction = vanilla.PopUpButton(
				"auto",
				("turn green nodes between curves into star nodes", "turn star nodes back into green nodes"),
				sizeStyle="small",
				callback=self.SavePreferences,
			)
			self.w.starNodesAction.setToolTip(starNodesTooltip)

		self.w.separator = vanilla.HorizontalLine("auto")

		scopeTooltip = "Which layers to process. The ⚠️ options cover all glyphs and can take a while. They include all master and special (brace, bracket) layers, except the current-master option."
		self.w.scopeText = vanilla.TextBox("auto", "Process:", sizeStyle="small", selectable=True)
		self.w.scopeText.setToolTip(scopeTooltip)
		self.w.layerScope = vanilla.PopUpButton(
			"auto",
			("currently selected layers only", "all masters of selected glyphs", "⚠️ all glyphs, but current master only", "⚠️ all glyphs in font", "⚠️ all glyphs in all open fonts"),
			sizeStyle="small",
			callback=self.SavePreferences,
		)
		self.w.layerScope.setToolTip(scopeTooltip)

		self.w.excludeText = vanilla.TextBox("auto", "Exclude glyphs with:", sizeStyle="small", selectable=True)
		self.w.exclude = vanilla.EditText("auto", ".ornm, BlackIndex, Heart, apple", callback=self.SavePreferences, sizeStyle="small")
		self.w.resetButton = UpdateButton("auto", callback=self.resetToDefaults)
		excludeTooltip = "Skips glyphs whose names contain any of these comma-separated strings. Only applies to the ⚠️ ‘all glyphs’ options."
		self.w.excludeText.setToolTip(excludeTooltip)
		self.w.exclude.setToolTip(excludeTooltip)
		self.w.resetButton.setToolTip("Resets all settings of this window to their defaults.")

		self.w.openTab = vanilla.CheckBox("auto", "Open tab with result", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.openTab.setToolTip("Opens a tab with the affected layers.")
		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.setToolTip("Shows the result in the current tab instead of opening a new one.")

		self.w.shouldMark = vanilla.CheckBox("auto", "Mark affected nodes", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.shouldMark.setToolTip("Names changed nodes: 💚 for green, 🔷 for blue.")

		self.w.reportInMacroWindow = vanilla.CheckBox("auto", "Report in Macro Window", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportInMacroWindow.setToolTip("Writes a report to the Macro Panel.")
		self.w.reportInMacroWindowVerbose = vanilla.CheckBox("auto", "Verbose", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportInMacroWindowVerbose.setToolTip("Reports every layer, not just the ones with changes.")

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero
		self.w.progress.setToolTip("Progress of the run.")

		self.w.processingText = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle='small', selectable=True)
		self.w.processingText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Treat Nodes", callback=self.GreenBlueManagerMain)
		self.w.runButton.setToolTip("Runs the enabled treatments on the chosen layers. Without any treatment enabled, opens a tab with the affected layers.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned and share the width of the widest one:
		labelNames = ("thresholdAngleText", "scopeText", "excludeText")
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		rules = [
			"H:|-inset-[descriptionText]-inset-|",
			"H:|-inset-[thresholdAngleText]-gap-[thresholdAngle(55)]-(>=inset)-|",
			"H:|-inset-[fixGreenBlue]-(>=inset)-|",
			"H:|-inset-[realignHandles]-(>=inset)-|",
			"H:|-inset-[separator]-inset-|",
			"H:|-inset-[scopeText]-gap-[layerScope]-inset-|",
			"H:|-inset-[excludeText]-gap-[exclude]-gap-[resetButton]-inset-|",
			"H:|-inset-[openTab]-gap-[reuseTab]-(>=inset)-|",
			"H:|-inset-[shouldMark]-(>=inset)-|",
			"H:|-inset-[reportInMacroWindow]-gap-[reportInMacroWindowVerbose]-(>=inset)-|",
			"H:|-inset-[progress]-inset-|",
			"H:|-inset-[processingText]-(>=gap)-[runButton(>=100)]-inset-|",
			{"view1": self.w.thresholdAngleText, "attribute1": "centerY", "view2": self.w.thresholdAngle, "attribute2": "centerY"},
			{"view1": self.w.scopeText, "attribute1": "centerY", "view2": self.w.layerScope, "attribute2": "centerY"},
			{"view1": self.w.excludeText, "attribute1": "centerY", "view2": self.w.exclude, "attribute2": "centerY"},
			{"view1": self.w.resetButton, "attribute1": "centerY", "view2": self.w.exclude, "attribute2": "centerY"},
			{"view1": self.w.reportInMacroWindowVerbose, "attribute1": "centerY", "view2": self.w.reportInMacroWindow, "attribute2": "centerY"},
			{"view1": self.w.reuseTab, "attribute1": "centerY", "view2": self.w.openTab, "attribute2": "centerY"},
			{"view1": self.w.reportInMacroWindow, "attribute1": "width", "view2": self.w.openTab, "attribute2": "width"},
			{"view1": self.w.thresholdAngleText, "attribute1": "width", "view2": self.w.excludeText, "attribute2": "width"},
			{"view1": self.w.scopeText, "attribute1": "width", "view2": self.w.excludeText, "attribute2": "width"},
			{"view1": self.w.processingText, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
		]
		verticalRule = "V:|-inset-[descriptionText(42)]-row-[thresholdAngle]-row-[fixGreenBlue]-stackRow-[realignHandles]"

		if self.hasStarNodes:
			# the checkbox hugs its title, the popup behind it takes the leftover width:
			self.w.starNodes.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsStarNodesAction = self.w.starNodesAction.getNSPopUpButton()
			nsStarNodesAction.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
			nsStarNodesAction.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
			rules.append("H:|-inset-[starNodes]-gap-[starNodesAction]-inset-|")
			rules.append({"view1": self.w.starNodesAction, "attribute1": "centerY", "view2": self.w.starNodes, "attribute2": "centerY"})
			verticalRule += "-stackRow-[starNodes]"

		verticalRule += "-row-[separator(1)]-row-[layerScope]-row-[exclude]-stackRow-[openTab]-stackRow-[shouldMark]-stackRow-[reportInMacroWindow]-barGap-[progress(16)]-inset-[runButton]-inset-|"
		rules.append(verticalRule)

		self.w.addAutoPosSizeRules(rules, metrics={"inset": inset, "gap": 8, "row": 8, "stackRow": 8, "barGap": 12})

		# Load Settings:
		self.LoadPreferences()

		self.updateUI()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# make the window horizontally resizable, but keep the height that Auto Layout determined.
		# (Content sizes set directly on the NSWindow, so the title bar is not counted twice.)
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()  # make sure the content has its final size before we read it
		contentSize = nsWindow.contentView().frame().size
		nsWindow.setContentMinSize_(NSSize(contentSize.width, contentSize.height))
		nsWindow.setContentMaxSize_(NSSize(contentSize.width + 1000, contentSize.height))

	def resetToDefaults(self, sender=None):
		for prefName, defaultValue in self.prefDict.items():
			self.setPref(prefName, defaultValue)
		self.LoadPreferences()

	def updateUI(self, sender=None):
		shouldStar = self.hasStarNodes and self.w.starNodes.get()
		if not self.w.realignHandles.get() and not self.w.fixGreenBlue.get() and not shouldStar:
			self.w.runButton.setTitle("Open Tab")
		else:
			self.w.runButton.setTitle("Treat Nodes")

		if self.hasStarNodes:
			self.w.starNodesAction.enable(self.w.starNodes.get())
		self.w.reuseTab.enable(self.w.openTab.get())
		self.w.reportInMacroWindowVerbose.enable(self.w.reportInMacroWindow.get())

	def realignLayer(self, layer, shouldRealign=False, shouldReport=False, shouldVerbose=False):
		def closestPointOnLine(P, A, B):
			# vector of line AB
			AB = NSPoint(B.x - A.x, B.y - A.y)
			# vector from point A to point P
			AP = NSPoint(P.x - A.x, P.y - A.y)
			# dot product of AB and AP
			dotProduct = AB.x * AP.x + AB.y * AP.y
			ABsquared = AB.x**2 + AB.y**2
			if ABsquared == 0.0:
				return NSPoint(P.x, P.y)  # A and B coincide: no line to project onto
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
							if (angleDiff <= thresholdAngle or angleDiff >= 360 - thresholdAngle) and hotNode.connection not in (GSSMOOTH, starNodeConnection):
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

	def starNodesOnLayer(self, thisLayer, makeStars=True, shouldReport=False, shouldVerbose=False):
		layerCount = 0
		for thisPath in thisLayer.paths:
			for thisNode in thisPath.nodes:
				prevNode, nextNode = thisNode.prevNode, thisNode.nextNode
				if prevNode is None or nextNode is None:
					continue
				if not (prevNode.type == GSOFFCURVE and nextNode.type == GSOFFCURVE):
					continue  # only nodes between two curves
				if makeStars and thisNode.connection == GSSMOOTH:
					thisNode.selected = True
					thisNode.connection = starNodeConnection
					layerCount += 1
				elif not makeStars and thisNode.connection == starNodeConnection:
					thisNode.selected = False
					thisNode.connection = GSSMOOTH
					layerCount += 1

		if shouldReport and shouldVerbose:
			if layerCount:
				if makeStars:
					print(f'   ⚠️ Turned {layerCount} green node{"" if layerCount == 1 else "s"} into star node{"" if layerCount == 1 else "s"}.')
				else:
					print(f'   ⚠️ Turned {layerCount} star node{"" if layerCount == 1 else "s"} back into green.')
			else:
				print("   ✅ No nodes to convert.")

		return layerCount

	def GreenBlueManagerMain(self, sender):
		try:
			shouldReport = self.pref("reportInMacroWindow")
			if shouldReport:
				Glyphs.clearLog()

			scope = self.pref("layerScope")
			if not Glyphs.font:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			elif scope == 4:  # all glyphs in all open fonts
				theseFonts = Glyphs.fonts
			else:  # current font
				theseFonts = (Glyphs.font, )

			for thisFont in theseFonts:
				reportName = reportFontName(thisFont)

				print(f"Green Blue Manager Report for {reportName}")
				print()

				shouldRealign = self.pref("realignHandles")
				shouldVerbose = self.pref("reportInMacroWindowVerbose")
				shouldFix = self.pref("fixGreenBlue")
				shouldStar = self.hasStarNodes and self.pref("starNodes")
				makeStars = self.pref("starNodesAction") == 0
				openTab = self.pref("openTab")
				reuseTab = self.pref("reuseTab")
				exclude = [x.strip() for x in self.pref("exclude").split(",") if x.strip()]

				# determine which layers to process:
				layersToBeProcessed, glyphsToBeProcessed = [], []
				if scope >= 2:  # all glyphs
					for thisGlyph in thisFont.glyphs:
						if any([x in thisGlyph.name for x in exclude]):
							print(f"Skipping {thisGlyph.name}: excluded as requested.")
							continue
						if scope == 2:  # current master only
							layersToBeProcessed.append(thisGlyph.layers[thisFont.selectedFontMaster.id])
							continue
						for thisLayer in thisGlyph.layers:
							if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
								layersToBeProcessed.append(thisLayer)
				elif scope == 1:  # all masters of selected glyphs
					glyphsToBeProcessed = [layer.parent for layer in thisFont.selectedLayers if layer.parent and not isinstance(layer, GSControlLayer)]
					for g in glyphsToBeProcessed:
						for layer in g.layers:
							if layer.isSpecialLayer or layer.isMasterLayer:
								layersToBeProcessed.append(layer)
				else:  # currently selected layers only
					layersToBeProcessed = thisFont.selectedLayers

				if not layersToBeProcessed:
					print(
						"❌ Green Blue Manager Error: No Selection",
						"\n⚠️ No glyphs selected for processing. Either select some glyphs or choose one of the ‘all glyphs’ options in ‘Process’.",
					)
				else:
					numberOfLayers = len(layersToBeProcessed)
					affectedLayersFixedConnections = []
					affectedLayersRealignedHandles = []
					affectedLayersStarNodes = []

					# process layers:
					for i, thisLayer in enumerate(layersToBeProcessed):
						if isinstance(thisLayer, GSControlLayer):
							continue

						thisGlyph = thisLayer.parent
						statusMessage = f"🔠 {thisGlyph.name}"
						if shouldReport and shouldVerbose:
							print(statusMessage)
						self.w.processingText.set(statusMessage)
						self.w.progress.set(100.0 / numberOfLayers * i)

						numberOfFixes = self.fixConnectionsOnLayer(thisLayer, shouldFix=shouldFix, shouldReport=shouldReport, shouldVerbose=shouldVerbose)
						if numberOfFixes:
							affectedLayersFixedConnections.append(thisLayer)

						numberOfAligns = self.realignLayer(thisLayer, shouldRealign, shouldReport, shouldVerbose)
						if numberOfAligns:
							affectedLayersRealignedHandles.append(thisLayer)

						if shouldStar:
							numberOfStars = self.starNodesOnLayer(thisLayer, makeStars, shouldReport, shouldVerbose)
							if numberOfStars:
								affectedLayersStarNodes.append(thisLayer)

					if affectedLayersStarNodes and makeStars and thisFont.formatVersion < 4:
						print(f"☑️ Star nodes need file format version 4: setting it from {thisFont.formatVersion} to 4.")
						thisFont.formatVersion = max(4, thisFont.formatVersion)

					self.w.progress.set(100)
					statusMessage = "✅ Processed %i layer%s." % (
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
					if shouldStar:
						titles.append("Turned green nodes into star nodes" if makeStars else "Turned star nodes back into green nodes")
					affectedGroups = [(titles[0], affectedLayersFixedConnections), (titles[1], affectedLayersRealignedHandles)]
					if shouldStar:
						affectedGroups.append((titles[2], affectedLayersStarNodes))
					affectedGroups = [(title, layers) for title, layers in affectedGroups if layers]

					if shouldReport:
						for title, layers in affectedGroups:
							print(f"\n{title} in following layers:")
							for affectedLayer in layers:
								print(f"   {affectedLayer.parent.name}, layer '{affectedLayer.name}'")
						print(f"\nDone. {statusMessage}")
						# Glyphs.showMacroWindow()

					if numberOfLayers == 1 and len(glyphsToBeProcessed) != 1 and thisFont.currentTab:
						# if only one layer was processed, do not open new tab:
						if Glyphs.versionNumber >= 4.0:
							thisFont.currentTab.redraw()
						else:
							thisFont.currentTab.forceRedraw()
						thisFont.currentTab.reflow()
						if affectedGroups:
							message = "".join(f"• {title}\n" for title, layers in affectedGroups)
							print(message)
							continue

					else:
						# opens new Edit tab:
						if affectedGroups and openTab:
							if reuseTab and thisFont.currentTab:
								outputTab = thisFont.currentTab
								outputTab.text = "\n"
							else:
								outputTab = thisFont.newTab()

							for groupIndex, (title, layers) in enumerate(affectedGroups):
								if groupIndex:
									outputTab.text += "\n\n"
								outputTab.text += f"{title}:\n"
								for affectedLayer in layers:
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
