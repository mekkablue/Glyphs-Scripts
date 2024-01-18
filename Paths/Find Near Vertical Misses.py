# MenuTitle: Find Near Vertical Misses
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds nodes that are close but not exactly on vertical metrics.
"""

import vanilla
from GlyphsApp import Glyphs, GSAnnotation, TEXT, GSOFFCURVE, GSUppercase, GSLowercase, GSSmallcaps, Message
from mekkaCore import mekkaObject


class FindNearVerticalMisses(mekkaObject):
	marker = "❌"
	heightsToCheck = []

	prefDict = {
		"deviance": "1",
		"tolerateIfNextNodeIsOn": True,
		"tolerateIfExtremum": True,
		"includeHandles": False,
		"removeOverlap": False,
		"markNodes": False,
		"includeNonExporting": False,
		"includeComposites": False,
		"exclude": False,
		"openTab": True,
		"reuseTab": True,
		"whereToCheck.ascender": True,
		"whereToCheck.capHeight": True,
		"whereToCheck.shoulderHeight": False,
		"whereToCheck.smallCapHeight": False,
		"whereToCheck.xHeight": True,
		"whereToCheck.baseline": True,
		"whereToCheck.descender": True,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 510
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Find Near Vertical Misses",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Find glyphs with nodes not exactly on vertical metrics:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.devianceText = vanilla.TextBox((inset, linePos + 3, inset + 135, 14), "Find nodes off by up to:", sizeStyle='small', selectable=True)
		self.w.deviance = vanilla.EditText((inset + 135, linePos, -inset, 19), "1", callback=self.SavePreferences, sizeStyle='small')
		self.w.deviance.getNSTextField().setToolTip_("Finds nodes that are not equal to the metric, but off up to this value in units. Minimum: 1 unit.")
		linePos += lineHeight

		# BOX
		linePos += int(lineHeight // 2)
		self.w.whereToCheck = vanilla.Box((inset, linePos, -inset, int(lineHeight * 7.6)))
		insetLinePos = int(inset * 0.2)

		self.w.whereToCheck.ascender = vanilla.CheckBox((int(0.5 * inset), insetLinePos - 1, -inset, 20), "Ascender (caps ignored)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.whereToCheck.ascender.getNSButton().setToolTip_("Checks if points are not exactly on, but just off the ascender of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight

		self.w.whereToCheck.capHeight = vanilla.CheckBox((int(0.5 * inset), insetLinePos - 1, -inset, 20), "Cap Height (lowercase ignored)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.whereToCheck.capHeight.getNSButton().setToolTip_("Checks if points are not exactly on, but just off the capHeight of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight

		self.w.whereToCheck.shoulderHeight = vanilla.CheckBox((int(0.5 * inset), insetLinePos - 1, -inset, 20), "shoulderHeight (UC, LC, SC ignored)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.whereToCheck.shoulderHeight.getNSButton().setToolTip_("Checks if points are not exactly on, but just off the shoulderHeight of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight

		self.w.whereToCheck.smallCapHeight = vanilla.CheckBox((int(0.5 * inset), insetLinePos - 1, -inset, 20), "smallCapHeight (only considers smallcaps)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.whereToCheck.smallCapHeight.getNSButton().setToolTip_("Checks if points are not exactly on, but just off the smallCapHeight of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight

		self.w.whereToCheck.xHeight = vanilla.CheckBox((int(0.5 * inset), insetLinePos - 1, -inset, 20), "x-height (caps ignored)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.whereToCheck.xHeight.getNSButton().setToolTip_("Checks if points are not exactly on, but just off the xHeight of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight

		self.w.whereToCheck.baseline = vanilla.CheckBox((int(0.5 * inset), insetLinePos - 1, -inset, 20), "Baseline", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.whereToCheck.baseline.getNSButton().setToolTip_("Checks if points are not exactly on, but just off the baseline of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight

		self.w.whereToCheck.descender = vanilla.CheckBox((int(0.5 * inset), insetLinePos - 1, -inset, 20), "Descender", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.whereToCheck.descender.getNSButton().setToolTip_("Checks if points are not exactly on, but just off the descender of the corresponding master.")
		linePos += lineHeight
		insetLinePos += lineHeight

		linePos += lineHeight
		# BOX END

		self.w.tolerateIfNextNodeIsOn = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Tolerate near miss if next node is on", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.tolerateIfNextNodeIsOn.getNSButton().setToolTip_("Will skip the just-off node if the next or previous on-curve node is EXACTLY on the metric line. Useful if you have very thin serifs or short segments near the metric lines.")
		linePos += lineHeight

		self.w.tolerateIfExtremum = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Tolerate near miss for left/right curve extremum", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.tolerateIfExtremum.getNSButton().setToolTip_("Will skip the just-off node if the next and previous nodes are VERTICAL OFF-CURVES. Recommended for avoiding false positives.")
		linePos += lineHeight

		self.w.includeHandles = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Include off-curve points", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeHandles.getNSButton().setToolTip_("Also checks BCPs (Bézier control points), vulgo ‘handles’. Otherwise only considers on-curve nodes")
		linePos += lineHeight

		self.w.removeOverlap = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Check outlines after Remove Overlap (slower)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeOverlap.getNSButton().setToolTip_("Only checks outlines after overlap removal. That way, ignores triangular overlaps (‘opened corners’). Use this option if you have too many false positives.")
		linePos += lineHeight

		self.w.markNodes = vanilla.CheckBox((inset, linePos - 1, -inset, 20), f"Mark affected nodes with {self.marker}", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.markNodes.getNSButton().setToolTip_("Sets the name of affected nodes to this emoji, so you can easily find it. ATTENTION: If Remove Overlap option is on, will use the emoji as an annotation instead.")
		linePos += lineHeight

		self.w.includeNonExporting = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.getNSButton().setToolTip_("Also check for near misses in glyphs that are set to not export. Useful if you are using non-exporting parts as components in other glyphs.")
		linePos += lineHeight

		self.w.includeComposites = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Include composites", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeComposites.getNSButton().setToolTip_("If unchecked, will only go through glyphs that have paths in them. Recommended to leave off, because it usually reports a lot of false positives.")
		linePos += lineHeight

		self.w.excludeText = vanilla.TextBox((inset, linePos + 3, 150, 14), "Exclude glyphs containing:", sizeStyle='small', selectable=True)
		self.w.exclude = vanilla.EditText((inset + 150, linePos, -inset, 19), ".ornm, .notdef, comb", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.openTab = vanilla.CheckBox((inset, linePos - 1, 190, 20), "Open tab with affected layers", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.openTab.getNSButton().setToolTip_("If it finds nodes just off the indicated metrics, will open a new tab with the layers if found the deviating nodes on. Otherwise please check the detailed report in Macro Window.")
		self.w.reuseTab = vanilla.CheckBox((inset + 190, linePos - 1, -inset, 20), "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.getNSButton().setToolTip_("If a tab is open already, will use that one, rather than opening a new tab. Recommended, keeps tab clutter low.")
		linePos += lineHeight

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)  # set progress indicator to zero
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Find", sizeStyle='regular', callback=self.FindNearVerticalMissesMain)
		self.w.setDefaultButton(self.w.runButton)

		# Status Message:
		self.w.status = vanilla.TextBox((inset, -18 - inset, -80 - inset, 14), "🤖 Ready.", sizeStyle='small', selectable=True)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def uodateUI(self, sender=None):
		# At least one vertical metrics must be on, otherwise disable button:
		enableButton = False
		boxDict = self.w.whereToCheck.__dict__
		for itemName in boxDict:
			checkbox = boxDict[itemName]
			if isinstance(checkbox, vanilla.vanillaCheckBox.CheckBox):
				if checkbox.get():
					enableButton = True
					break
		self.w.runButton.enable(onOff=enableButton)

		# disable Reuse Tab button if Open Tab is off:
		self.w.reuseTab.enable(self.w.openTab.get())

	def isNodeSlightlyOff(self, nodePosition, master, deviance, prevY, nextY, glyphType=None, glyphSuffix=None):
		y = nodePosition.y
		prevAndNextDontCount = prevY is None or nextY is None

		if self.pref("descender"):
			if y != master.descender:
				if master.descender - deviance <= y <= master.descender + deviance:
					if prevAndNextDontCount or (prevY != master.descender and nextY != master.descender):
						return True
					else:
						# prev or next node or exactly on metric line, so do not count as off:
						return False

		if self.pref("baseline"):
			if y != 0.0:
				if 0.0 - deviance <= y <= 0.0 + deviance:
					if prevAndNextDontCount or (prevY != 0.0 and nextY != 0.0):
						return True
					else:
						# prev or next node or exactly on metric line, so do not count as off:
						return False

		if self.pref("xHeight"):
			if glyphType is None or glyphType not in ("Uppercase", "Smallcaps"):
				if y != master.xHeight:
					if master.xHeight - deviance <= y <= master.xHeight + deviance:
						if prevAndNextDontCount or (prevY != master.xHeight and nextY != master.xHeight):
							return True
						else:
							# prev or next node or exactly on metric line, so do not count as off:
							return False

		if self.pref("smallCapHeight"):
			suffixIsSC = False
			if glyphSuffix:
				suffixes = glyphSuffix.split(".")  # could be multiple suffixes
				for suffix in ("sc", "smcp", "c2sc"):
					if suffix in suffixes:
						suffixIsSC = True

			if suffixIsSC or glyphType == "Smallcaps":  # is smallcap
				smallCapHeight = master.customParameters["smallCapHeight"]
				if smallCapHeight:
					smallCapHeight = float(smallCapHeight)
					if y != smallCapHeight:
						if smallCapHeight - deviance <= y <= smallCapHeight + deviance:
							if prevAndNextDontCount or (prevY != smallCapHeight and nextY != smallCapHeight):
								return True
							else:
								# prev or next node or exactly on metric line, so do not count as off:
								return False

		if self.pref("shoulderHeight"):
			if glyphType is None or glyphType not in ("Lowercase", "Uppercase", "Smallcaps"):
				shoulderHeight = master.customParameters["shoulderHeight"]
				if shoulderHeight:
					shoulderHeight = float(shoulderHeight)
					if y != shoulderHeight:
						if shoulderHeight - deviance <= y <= shoulderHeight + deviance:
							if prevAndNextDontCount or (prevY != shoulderHeight and nextY != shoulderHeight):
								return True
							else:
								# prev or next node or exactly on metric line, so do not count as off:
								return False

		if self.pref("capHeight"):
			if glyphType is None or glyphType not in ("Lowercase", "Smallcaps"):
				if y != master.capHeight:
					if master.capHeight - deviance <= y <= master.capHeight + deviance:
						if prevAndNextDontCount or (prevY != master.capHeight and nextY != master.capHeight):
							return True
						else:
							# prev or next node or exactly on metric line, so do not count as off:
							return False

		if self.pref("ascender"):
			if glyphType is None or glyphType not in ("Uppercase", "Smallcaps"):
				if y != master.ascender:
					if master.ascender - deviance <= y <= master.ascender + deviance:
						if prevAndNextDontCount or (prevY != master.ascender and nextY != master.ascender):
							return True
						else:
							# prev or next node or exactly on metric line, so do not count as off:
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
		marker = GSAnnotation()
		marker.type = TEXT
		marker.position = position
		marker.text = text
		marker.width = min(max(50.0, 7 * len(text)), 600.0)  # min=50, max=600
		layer.annotations.append(marker)

	def FindNearVerticalMissesMain(self, sender):
		try:
			# clears macro window log:
			Glyphs.clearLog()
			self.w.progress.set(0)

			# update settings to the latest user input:
			self.SavePreferences()

			self.checkGUI()

			thisFont = Glyphs.font  # frontmost font
			print(f"Find Near Vertical Misses Report for {thisFont.familyName}")
			print(thisFont.filepath)
			print()

			includeComposites = self.pref("includeComposites")
			includeNonExporting = self.pref("includeNonExporting")

			deviance = self.prefFloat("deviance")
			excludes = [x.strip() for x in self.pref("exclude").split(",")]
			skippedGlyphs = []

			affectedLayers = []
			totalNumberOfGlyphs = len(thisFont.glyphs)
			for i, thisGlyph in enumerate(thisFont.glyphs):
				self.w.progress.set(100 * i // totalNumberOfGlyphs)

				glyphIsExcluded = not (thisGlyph.export or includeNonExporting)
				if not glyphIsExcluded:
					for excludedText in excludes:
						if excludedText in thisGlyph.name:
							skippedGlyphs.append(thisGlyph.name)
							glyphIsExcluded = True
							break

				if not glyphIsExcluded:
					self.w.status.set(f"🔠 {thisGlyph.name}")
					suffix = None
					if "." in thisGlyph.name:
						offset = thisGlyph.name.find(".")
						suffix = thisGlyph.name[offset:]

					for thisLayer in thisGlyph.layers:
						# get rid of debris from previous iterations:
						self.doubleCheckAnnotations(thisLayer)
						layerCounts = thisLayer.isMasterLayer or thisLayer.isSpecialLayer
						layerShouldBeChecked = len(thisLayer.paths) > 0 or includeComposites

						if layerCounts and layerShouldBeChecked:

							# overlap removal if requested:
							if self.pref("removeOverlap"):
								checkLayer = thisLayer.copyDecomposedLayer()
								checkLayer.removeOverlap()
							else:
								checkLayer = thisLayer

							# step through nodes:
							for thisPath in checkLayer.paths:
								for thisNode in thisPath.nodes:
									nodeIsOncurve = thisNode.type != GSOFFCURVE
									if nodeIsOncurve or self.pref("includeHandles"):

										skipThisNode = False
										if self.pref("tolerateIfExtremum"):
											if thisNode.prevNode:
												if thisNode.prevNode.type == GSOFFCURVE and thisNode.nextNode.type == GSOFFCURVE:
													vertical = thisNode.x == thisNode.prevNode.x == thisNode.nextNode.x
													linedUp = (thisNode.y - thisNode.prevNode.y) * (thisNode.nextNode.y - thisNode.y) > 0.0
													if vertical and linedUp:
														skipThisNode = True
											else:
												print(f"⚠️ Potential open path in {thisGlyph.name}")

										if not skipThisNode:
											if self.pref("tolerateIfNextNodeIsOn"):
												# determine previous oncurve point
												previousOnCurve = thisNode.prevNode
												if previousOnCurve:
													while previousOnCurve.type == GSOFFCURVE:
														previousOnCurve = previousOnCurve.prevNode
													previousY = previousOnCurve.y
													# determine next oncurve point
													nextOnCurve = thisNode.nextNode
													while nextOnCurve.type == GSOFFCURVE:
														nextOnCurve = nextOnCurve.nextNode
													nextY = nextOnCurve.y
												else:
													print(f"⚠️ Potential open path in {thisGlyph.name}")
											else:
												previousY = None
												nextY = None

											glyphType = None
											if Glyphs.versionNumber >= 3:
												# GLYPHS 3
												if thisGlyph.case == GSUppercase:
													glyphType = "Uppercase"
												elif thisGlyph.case == GSLowercase:
													glyphType = "Lowercase"
												elif thisGlyph.case == GSSmallcaps:
													glyphType = "Smallcaps"
											else:
												glyphType = thisGlyph.subCategory

											if self.isNodeSlightlyOff(thisNode.position, thisLayer.master, deviance, previousY, nextY, glyphType, suffix):
												# collect layer:
												if thisLayer not in affectedLayers:
													affectedLayers.append(thisLayer)
												thisNode.selected = True

												# report:
												print("%s /%s ‘%s’: %.1f %.1f" % (
													self.marker,
													thisGlyph.name,
													thisLayer.name,
													thisNode.x,
													thisNode.y,
												))

												# node name:
												if self.pref("markNodes"):
													if self.pref("removeOverlap"):
														self.addAnnotation(thisLayer, thisNode.position, self.marker)
													else:
														thisNode.name = self.marker
												else:
													self.doubleCheckNodeName(thisNode)
											else:
												self.doubleCheckNodeName(thisNode)
									else:
										self.doubleCheckNodeName(thisNode)

			# make sure View options are on:
			if self.pref("markNodes"):
				if self.pref("removeOverlap"):
					Glyphs.defaults["showAnnotations"] = 1
				else:
					Glyphs.defaults["showNodeNames"] = 1

			# Done. Set Progress Bar to max and report:
			self.w.progress.set(100)
			self.w.status.set("✅ Done.")

			if skippedGlyphs:
				print()
				print(f"Skipped glyphs:\n{', '.join(skippedGlyphs)}")

			print()
			print("Done.")

			if affectedLayers:
				if self.pref("openTab"):
					# try to reuse current tab:
					resultTab = thisFont.currentTab
					if resultTab and self.pref("reuseTab"):
						resultTab.layers = ()
					else:
						# open new tab:
						resultTab = thisFont.newTab()
					resultTab.layers = affectedLayers
				else:
					# brings macro window to front:
					Glyphs.showMacroWindow()
			else:
				Message(
					title="No Deviant Nodes",
					message="Congratulations! No nodes found missing the indicated metrics and off by up to {self.pref('deviance')} u.",
					OKButton="🥂Cheers!"
				)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Find Near Vertical Misses Error: {e}")
			import traceback
			print(traceback.format_exc())


FindNearVerticalMisses()
