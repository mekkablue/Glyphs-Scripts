# MenuTitle: Find Near Vertical Misses
__doc__ = """
Finds on-curve nodes that are close but not exactly on any of the layer's vertical metrics.
Always checks on-curve points only, never removes overlap, always includes non-exporting glyphs,
never includes composites. Uses each layer's individual metrics (supports per-layer overrides).
"""

import vanilla
from AppKit import NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, GSAnnotation, TEXT, GSOFFCURVE, GSUppercase, GSLowercase, GSMetricsTypexHeight, GSMetricsTypeCapHeight, Message
from mekkablue import mekkaObject, SteppingEditText, decimalFormatter


class FindNearVerticalMisses(mekkaObject):
	marker = "❌"

	prefDict = {
		"deviance": 1,
		"tolerateIfNextNodeIsOn": True,
		"tolerateIfExtremum": True,
		"markNodes": False,
		"limitToLetters": False,
		"exclude": ".ornm, .notdef, comb",
		"openTab": True,
		"reuseTab": True,
	}

	def __init__(self):
		windowWidth = 370
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Find Near Vertical Misses",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Search for on-curve nodes not exactly on metrics:", sizeStyle="small", selectable=True)
		self.w.descriptionText.setToolTip("Searches for on-curve nodes that are close but not exactly on any vertical metric of their layer. Automatically skips xHeight for uppercase glyphs, and capHeight for lowercase glyphs, to avoid false positives.")

		tooltipText = "Finds nodes that are not equal to any metric value, but off by up to this many units. Minimum: 1 unit."
		formatter = decimalFormatter(1)
		self.w.devianceText = vanilla.TextBox("auto", "Find nodes off by up to", sizeStyle="small", selectable=True)
		self.w.devianceText.setToolTip(tooltipText)
		self.w.deviance = SteppingEditText("auto", "1", callback=self.SavePreferences, sizeStyle="small", formatter=formatter)
		self.w.deviance.getNSTextField().setAlignment_(NSTextAlignmentRight)
		self.w.deviance.setToolTip(tooltipText)
		self.w.devianceUnitsText = vanilla.TextBox("auto", "units", sizeStyle="small", selectable=True)
		self.w.devianceUnitsText.setToolTip(tooltipText)

		self.w.tolerateIfNextNodeIsOn = vanilla.CheckBox("auto", "Tolerate near miss if next node is on", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.tolerateIfNextNodeIsOn.setToolTip("Skips a near-miss node if the nearest on-curve neighbor (in either direction along the path) sits exactly on the same metric line. Useful for very thin serifs or short segments near metric lines.")

		self.w.tolerateIfExtremum = vanilla.CheckBox("auto", "Tolerate near miss for left/right curve extremum", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.tolerateIfExtremum.setToolTip("Skips a near-miss node when both its neighbor nodes are vertical off-curves (i.e. the node is a left or right curve extremum). Strongly recommended to avoid false positives on rounded shapes.")

		self.w.markNodes = vanilla.CheckBox("auto", f"Mark affected nodes with {self.marker}", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.markNodes.setToolTip(f"Assigns the name '{self.marker}' to each offending node so it appears as a node label. Enable View > Show Node Names to see the markers in the canvas.")

		self.w.limitToLetters = vanilla.CheckBox("auto", "Limit to letters", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.limitToLetters.setToolTip("Restricts the search to glyphs with category 'Letter'. All other categories (figures, punctuation, symbols, etc.) are skipped.")

		tooltipText = "Comma-separated list of substrings. Any glyph whose name contains at least one of these substrings is skipped entirely."
		self.w.excludeText = vanilla.TextBox("auto", "Exclude glyphs containing:", sizeStyle="small", selectable=True)
		self.w.excludeText.setToolTip(tooltipText)
		self.w.exclude = vanilla.EditText("auto", ".ornm, .notdef, comb", callback=self.SavePreferences, sizeStyle="small")
		self.w.exclude.setToolTip(tooltipText)

		self.w.openTab = vanilla.CheckBox("auto", "Open tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.openTab.setToolTip("Opens an edit tab showing all layers that contain at least one near-miss node.")
		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.reuseTab.setToolTip("Replaces the contents of the currently active tab instead of opening a new one.")

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)

		self.w.runButton = vanilla.Button("auto", "Find", callback=self.FindNearVerticalMissesMain)
		self.w.setDefaultButton(self.w.runButton)

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small", selectable=True)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, the field behind it takes the leftover width:
		nsLabel = self.w.excludeText.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[devianceText]-gap-[deviance(40)]-gap-[devianceUnitsText]-(>=inset)-|",
				"H:|-inset-[tolerateIfNextNodeIsOn]-(>=inset)-|",
				"H:|-inset-[tolerateIfExtremum]-(>=inset)-|",
				"H:|-inset-[markNodes]-(>=inset)-|",
				"H:|-inset-[limitToLetters]-(>=inset)-|",
				"H:|-inset-[excludeText]-gap-[exclude]-inset-|",
				"H:|-inset-[openTab]-gap-[reuseTab]-(>=inset)-|",
				"H:|-inset-[progress]-inset-|",
				"H:|-inset-[status]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-row-[deviance]-section-[tolerateIfNextNodeIsOn]-stackRow-[tolerateIfExtremum]-stackRow-[markNodes]-stackRow-[limitToLetters]-stackRow-[exclude]-section-[openTab]-section-[progress(16)]-inset-[runButton]-inset-|",
				{"view1": self.w.devianceText, "attribute1": "centerY", "view2": self.w.deviance, "attribute2": "centerY"},
				{"view1": self.w.devianceUnitsText, "attribute1": "centerY", "view2": self.w.deviance, "attribute2": "centerY"},
				{"view1": self.w.excludeText, "attribute1": "centerY", "view2": self.w.exclude, "attribute2": "centerY"},
				{"view1": self.w.reuseTab, "attribute1": "centerY", "view2": self.w.openTab, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8, "stackRow": 8, "section": 12},
		)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.reuseTab.enable(self.w.openTab.get())
		if self.w.markNodes.get():
			Glyphs.defaults["showNodeNames"] = 1

	def getMetricValues(self, layer, glyph=None):
		"""Returns a set of effective metric y-values for the given layer.

		Skips xHeight metrics for uppercase glyphs and capHeight metrics for
		lowercase glyphs to avoid false positives from cross-case metric proximity.
		"""
		values = set()
		font = layer.parent.parent
		glyphCase = glyph.case if glyph is not None else None
		try:
			fontMetrics = font.metrics
			masterMetrics = layer.master.metrics
			layerMetrics = layer.metrics
			for i in range(len(fontMetrics)):
				try:
					metricType = fontMetrics[i].type
					if glyphCase == GSUppercase and metricType == GSMetricsTypexHeight:
						continue
					if glyphCase == GSLowercase and metricType == GSMetricsTypeCapHeight:
						continue
				except (AttributeError, IndexError):
					pass
				val = None
				try:
					if i < len(layerMetrics) and layerMetrics[i]:
						val = layerMetrics[i].position
				except (KeyError, IndexError):
					pass
				if val is None:
					try:
						if i < len(masterMetrics) and masterMetrics[i]:
							val = masterMetrics[i].position
					except (KeyError, IndexError):
						pass
				if val is not None:
					values.add(val)
		except (AttributeError, TypeError, IndexError):
			# Fallback for Glyphs 2 or unexpected API changes
			master = layer.master
			if master:
				for attrName in ("ascender", "capHeight", "xHeight", "descender"):
					if glyphCase == GSUppercase and attrName == "xHeight":
						continue
					if glyphCase == GSLowercase and attrName == "capHeight":
						continue
					try:
						v = getattr(master, attrName)
						if v is not None:
							values.add(float(v))
					except AttributeError:
						pass
				values.add(0.0)  # baseline
		return values

	def isNodeSlightlyOff(self, nodePosition, metricValues, deviance, prevY, nextY):
		y = nodePosition.y
		prevAndNextDontCount = prevY is None or nextY is None
		for metricY in metricValues:
			if y != metricY:
				if metricY - deviance <= y <= metricY + deviance:
					if prevAndNextDontCount or (prevY != metricY and nextY != metricY):
						return True
					else:
						# Neighbor is exactly on this metric — tolerate the near miss
						return False
		return False

	def doubleCheckNodeName(self, thisNode):
		if thisNode.name == self.marker:
			thisNode.setName_(None)

	def doubleCheckAnnotations(self, thisLayer):
		for i in range(len(thisLayer.annotations))[::-1]:
			if thisLayer.annotations[i].text == self.marker:
				del thisLayer.annotations[i]

	def addAnnotation(self, layer, position, text):
		annotation = GSAnnotation()
		annotation.type = TEXT
		annotation.position = position
		annotation.text = text
		annotation.width = min(max(50.0, 7 * len(text)), 600.0)
		layer.annotations.append(annotation)

	def FindNearVerticalMissesMain(self, sender):
		try:
			Glyphs.clearLog()
			self.w.progress.set(0)
			self.SavePreferences()
			self.updateUI()

			thisFont = Glyphs.font
			if not thisFont:
				Message(title="No Font Open", message="Please open a font first.", OKButton=None)
				return

			print(f"Find Near Vertical Misses Report for {thisFont.familyName}")
			print(thisFont.filepath)
			print()

			deviance = self.prefFloat("deviance")
			limitToLetters = self.prefBool("limitToLetters")
			excludeString = self.pref("exclude").strip()
			excludes = [x.strip() for x in excludeString.split(",")] if excludeString else None

			skippedGlyphs = []
			affectedLayers = []
			totalNumberOfGlyphs = len(thisFont.glyphs)

			for i, thisGlyph in enumerate(thisFont.glyphs):
				self.w.progress.set(100 * i // totalNumberOfGlyphs)

				glyphIsExcluded = False
				if limitToLetters and thisGlyph.category != "Letter":
					glyphIsExcluded = True
				if not glyphIsExcluded and excludes:
					for excludedText in excludes:
						if excludedText in thisGlyph.name:
							skippedGlyphs.append(thisGlyph.name)
							glyphIsExcluded = True
							break

				if glyphIsExcluded:
					continue

				self.w.status.set(f"🔠 {thisGlyph.name}")

				for thisLayer in thisGlyph.layers:
					self.doubleCheckAnnotations(thisLayer)
					layerCounts = thisLayer.isMasterLayer or thisLayer.isSpecialLayer
					# Never include composites: only layers that have paths
					if not layerCounts or len(thisLayer.paths) == 0:
						continue

					metricValues = self.getMetricValues(thisLayer, thisGlyph)
					if not metricValues:
						continue

					for thisPath in thisLayer.paths:
						for thisNode in thisPath.nodes:
							# Always exclude off-curve points
							if thisNode.type == GSOFFCURVE:
								self.doubleCheckNodeName(thisNode)
								continue

							if self.prefBool("tolerateIfExtremum"):
								if thisNode.prevNode:
									if thisNode.prevNode.type == GSOFFCURVE and thisNode.nextNode.type == GSOFFCURVE:
										vertical = thisNode.x == thisNode.prevNode.x == thisNode.nextNode.x
										linedUp = (thisNode.y - thisNode.prevNode.y) * (thisNode.nextNode.y - thisNode.y) > 0.0
										if vertical and linedUp:
											continue
								else:
									print(f"⚠️ Potential open path in {thisGlyph.name}")

							previousY = None
							nextY = None
							if self.prefBool("tolerateIfNextNodeIsOn"):
								previousOnCurve = thisNode.prevNode
								if previousOnCurve:
									while previousOnCurve.type == GSOFFCURVE:
										previousOnCurve = previousOnCurve.prevNode
									previousY = previousOnCurve.y
									nextOnCurve = thisNode.nextNode
									while nextOnCurve.type == GSOFFCURVE:
										nextOnCurve = nextOnCurve.nextNode
									nextY = nextOnCurve.y
								else:
									print(f"⚠️ Potential open path in {thisGlyph.name}")

							if self.isNodeSlightlyOff(thisNode.position, metricValues, deviance, previousY, nextY):
								if thisLayer not in affectedLayers:
									affectedLayers.append(thisLayer)
								thisNode.selected = True
								print("%s /%s '%s': %.1f %.1f" % (
									self.marker,
									thisGlyph.name,
									thisLayer.name,
									thisNode.x,
									thisNode.y,
								))
								if self.prefBool("markNodes"):
									thisNode.name = self.marker
								else:
									self.doubleCheckNodeName(thisNode)
							else:
								self.doubleCheckNodeName(thisNode)

			if self.prefBool("markNodes"):
				Glyphs.defaults["showNodeNames"] = 1

			self.w.progress.set(100)
			self.w.status.set("✅ Done.")

			if skippedGlyphs:
				print()
				print(f"Skipped glyphs:\n{', '.join(skippedGlyphs)}")

			print()
			print("Done.")

			if affectedLayers:
				if self.prefBool("openTab"):
					resultTab = thisFont.currentTab
					if resultTab and self.prefBool("reuseTab"):
						resultTab.layers = ()
					else:
						resultTab = thisFont.newTab()
					resultTab.layers = affectedLayers
				else:
					Glyphs.showMacroWindow()
			else:
				Message(
					title="No Deviant Nodes",
					message=f"Congratulations! No nodes found missing any metric and off by up to {deviance:g} u.",
					OKButton="🥂Cheers!"
				)

		except Exception as e:
			Glyphs.showMacroWindow()
			print(f"Find Near Vertical Misses Error: {e}")
			import traceback
			print(traceback.format_exc())


FindNearVerticalMisses()
