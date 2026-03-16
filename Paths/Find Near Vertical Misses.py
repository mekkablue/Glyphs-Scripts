# MenuTitle: Find Near Vertical Misses
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds on-curve nodes that are close but not exactly on any of the layer's vertical metrics.
Always checks on-curve points only, never removes overlap, always includes non-exporting glyphs,
never includes composites. Uses each layer's individual metrics (supports per-layer overrides).
"""

import vanilla
from GlyphsApp import Glyphs, GSAnnotation, TEXT, GSOFFCURVE, Message
from mekkablue import mekkaObject


class FindNearVerticalMisses(mekkaObject):
	marker = "❌"

	prefDict = {
		"deviance": "1",
		"tolerateIfNextNodeIsOn": True,
		"tolerateIfExtremum": True,
		"markNodes": False,
		"limitToLetters": False,
		"exclude": "",
		"openTab": True,
		"reuseTab": True,
	}

	def __init__(self):
		windowWidth = 320
		windowHeight = 282
		windowWidthResize = 300
		windowHeightResize = 0
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Find Near Vertical Misses",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),
			autosaveName=self.domain("mainwindow"),
		)

		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Search for on-curve nodes not exactly on metrics:", sizeStyle="small", selectable=True)
		self.w.descriptionText.getNSTextField().setToolTip_("Searches for on-curve nodes that are close but not exactly on any vertical metric of their layer.")
		linePos += lineHeight

		self.w.devianceText = vanilla.TextBox((inset, linePos + 3, 130, 14), "Find nodes off by up to", sizeStyle="small", selectable=True)
		self.w.devianceText.getNSTextField().setToolTip_("Finds nodes that are not equal to any metric value, but off by up to this many units. Minimum: 1 unit.")
		self.w.deviance = vanilla.EditText((inset + 130, linePos, 35, 19), "1", callback=self.SavePreferences, sizeStyle="small")
		self.w.deviance.getNSTextField().setAlignment_(2)  # NSTextAlignmentRight
		self.w.deviance.getNSTextField().setToolTip_("Finds nodes that are not equal to any metric value, but off by up to this many units. Minimum: 1 unit.")
		self.w.devianceUnitsText = vanilla.TextBox((inset + 170, linePos + 3, 50, 14), "units", sizeStyle="small", selectable=True)
		self.w.devianceUnitsText.getNSTextField().setToolTip_("Finds nodes that are not equal to any metric value, but off by up to this many units. Minimum: 1 unit.")
		linePos += lineHeight

		linePos += int(lineHeight * 0.5)

		self.w.tolerateIfNextNodeIsOn = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Tolerate near miss if next node is on", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.tolerateIfNextNodeIsOn.getNSButton().setToolTip_("Will skip the just-off node if the next or previous on-curve node is EXACTLY on the metric line. Useful if you have very thin serifs or short segments near the metric lines.")
		linePos += lineHeight

		self.w.tolerateIfExtremum = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Tolerate near miss for left/right curve extremum", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.tolerateIfExtremum.getNSButton().setToolTip_("Will skip the just-off node if the next and previous nodes are VERTICAL OFF-CURVES. Recommended for avoiding false positives.")
		linePos += lineHeight

		self.w.markNodes = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), f"Mark affected nodes with {self.marker}", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.markNodes.getNSButton().setToolTip_("Sets the name of affected nodes to this emoji so you can easily find them. Enable View > Show Node Names to see the markers.")
		linePos += lineHeight

		self.w.limitToLetters = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Limit to letters", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.limitToLetters.getNSButton().setToolTip_("Only checks glyphs with category 'Letter'. Skips figures, punctuation, symbols, etc.")
		linePos += lineHeight

		self.w.excludeText = vanilla.TextBox((inset, linePos + 3, 150, 14), "Exclude glyphs containing:", sizeStyle="small", selectable=True)
		self.w.excludeText.getNSTextField().setToolTip_("Comma-separated substrings. Any glyph whose name contains one of these will be skipped.")
		self.w.exclude = vanilla.EditText((inset + 150, linePos, -inset, 19), ".ornm, .notdef, comb", callback=self.SavePreferences, sizeStyle="small")
		self.w.exclude.getNSTextField().setToolTip_("Comma-separated substrings. Any glyph whose name contains one of these will be skipped.")
		linePos += lineHeight
		linePos += 2  # extra breathing room before tab options

		self.w.openTab = vanilla.CheckBox((inset + 2, linePos - 1, 80, 20), "Open tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.openTab.getNSButton().setToolTip_("If near misses are found, opens a tab with the affected layers.")
		self.w.reuseTab = vanilla.CheckBox((inset + 2 + 80 + 4, linePos - 1, -inset, 20), "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.reuseTab.getNSButton().setToolTip_("Reuses the frontmost open tab instead of opening a new one.")
		linePos += lineHeight

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)

		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Find", callback=self.FindNearVerticalMissesMain)
		self.w.setDefaultButton(self.w.runButton)

		self.w.status = vanilla.TextBox((inset, -18 - inset, -80 - inset, 14), "🤖 Ready.", sizeStyle="small", selectable=True)

		self.LoadPreferences()
		self.w.open()
		currentWidth, currentHeight = self.w.getPosSize()[2:]
		currentHeight += 19
		
		windowWithinConstraints = (
			windowWidth <= currentWidth <= windowWidth + windowWidthResize
			and windowHeight <= currentHeight <= windowHeight + windowHeightResize
			)
		if not windowWithinConstraints:
			self.w.resize(windowWidth, windowHeight-19)
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.reuseTab.enable(self.w.openTab.get())

	def getMetricValues(self, layer):
		"""Returns a set of effective metric y-values for the given layer."""
		values = set()
		font = layer.parent.parent
		try:
			fontMetrics = font.metrics
			masterMetrics = layer.master.metrics
			layerMetrics = layer.metrics
			for i in range(len(fontMetrics)):
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
			thisNode.name = None

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

					metricValues = self.getMetricValues(thisLayer)
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
					message=f"Congratulations! No nodes found missing any metric and off by up to {self.pref('deviance')} u.",
					OKButton="🥂Cheers!"
				)

		except Exception as e:
			Glyphs.showMacroWindow()
			print(f"Find Near Vertical Misses Error: {e}")
			import traceback
			print(traceback.format_exc())


FindNearVerticalMisses()
