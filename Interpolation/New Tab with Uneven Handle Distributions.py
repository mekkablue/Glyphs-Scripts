# MenuTitle: New Tab with Uneven Handle Distributions
__doc__ = """
Finds glyphs where handle distributions change too much (e.g., from balanced to harmonised).
"""

import vanilla
from mekkablue import mekkaObject, SteppingEditText, decimalFormatter
from mekkablue.geometry import intersectionLineLinePoints, bezierWithPoints
from GlyphsApp import Glyphs, CURVE, Message, distance
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityWindowSizeStayPut,
)


class NewTabWithUnevenHandleDistributions(mekkaObject):
	prefDict = {
		"factorChange": 0,
		"factorChangeEntry": 2.5,
		"anyMaxToNotMax": 1,
		"markInFirstMaster": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"New Tab with Uneven Handle Distributions",  # window title
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Finds compatible glyphs with curve segments in which the handle distribution changes too much:", sizeStyle='small', selectable=True)
		# the description wraps: it takes the width it is given instead of demanding one long line
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		formatter = decimalFormatter(0, fractionDigits=3)
		self.w.factorChange = vanilla.CheckBox("auto", "Tolerated change factor (BCP1÷BCP2):", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.factorChangeEntry = SteppingEditText("auto", "2.5", callback=self.SavePreferences, sizeStyle='small', formatter=formatter)
		factorChangeTooltipText = "Calculates length ratios of handles in a curve segment in every master. If the ratio differs by more than the given factor in one or more masters, glyph will be reported."
		self.w.factorChange.setToolTip(factorChangeTooltipText)
		self.w.factorChangeEntry.setToolTip(factorChangeTooltipText)

		self.w.anyMaxToNotMax = vanilla.CheckBox("auto", "Any handle that changes from 100% to non-100%", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.anyMaxToNotMax.setToolTip("Finds BCPs that are maximized (100%) in one master, but not in other masters.")

		self.w.markInFirstMaster = vanilla.CheckBox("auto", "Mark affected curve segments in first master", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.markInFirstMaster.enable(False)
		self.w.markInFirstMaster.setToolTip("Not implemented yet. Sorry.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Open Tab", callback=self.NewTabWithUnevenHandleDistributionsMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[factorChange]-gap-[factorChangeEntry(60)]-(>=inset)-|",
				"H:|-inset-[anyMaxToNotMax]-(>=inset)-|",
				"H:|-inset-[markInFirstMaster]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=100)]-inset-|",
				# the first checkbox has a field behind it, so the whole stack gets the wider gap:
				"V:|-gap-[descriptionText(28)]-headlineGap-[factorChange]-stackRow-[anyMaxToNotMax]-stackRow-[markInFirstMaster]-inset-[runButton]-inset-|",
				{"view1": self.w.factorChangeEntry, "attribute1": "centerY", "view2": self.w.factorChange, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "stackRow": 8, "headlineGap": 10},
		)

		# older versions stored the factor as text, but the stepping field needs a number:
		storedFactor = self.pref("factorChangeEntry")
		if isinstance(storedFactor, str):
			try:
				self.setPref("factorChangeEntry", float(storedFactor.replace(",", ".")))
			except ValueError:
				self.setPref("factorChangeEntry", self.prefDict["factorChangeEntry"])

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def factor(self, A, B, C, D, intersection):
		"""
		Returns the ratio of the two handle percentages, or None if it cannot be
		calculated (retracted handle, or intersection on top of an on-curve node).
		"""
		maxLength1 = distance(A.position, intersection)
		maxLength2 = distance(D.position, intersection)
		if not maxLength1 or not maxLength2:
			return None
		handlePercentage1 = distance(A.position, B.position) / maxLength1
		handlePercentage2 = distance(D.position, C.position) / maxLength2
		if not handlePercentage1 or not handlePercentage2:
			return None
		return handlePercentage1 / handlePercentage2

	def factorChangeIsTooBig(self, maxFactorChange, firstFactor, pathIndex, indexA, indexB, indexC, indexD, otherLayers):
		for otherLayer in otherLayers:
			otherPath = otherLayer.paths[pathIndex]
			A = otherPath.nodes[indexA]
			B = otherPath.nodes[indexB]
			C = otherPath.nodes[indexC]
			D = otherPath.nodes[indexD]
			intersection = intersectionLineLinePoints(A.position, B.position, C.position, D.position)
			if intersection:
				otherFactor = self.factor(A, B, C, D, intersection)
				if otherFactor is None:
					continue
				factorChange = otherFactor / firstFactor
				if factorChange > maxFactorChange or factorChange < 1 / maxFactorChange:
					return True
		return False

	def isMaxTheSameEverywhere(self, firstBCPsMaxed, pathIndex, indexA, indexB, indexC, indexD, otherLayers):
		for otherLayer in otherLayers:
			otherPath = otherLayer.paths[pathIndex]
			A = otherPath.nodes[indexA]
			B = otherPath.nodes[indexB]
			C = otherPath.nodes[indexC]
			D = otherPath.nodes[indexD]
			intersection = intersectionLineLinePoints(A.position, B.position, C.position, D.position)
			if intersection:
				BCPsMaxed = (B.position == intersection, C.position == intersection)
				if BCPsMaxed != firstBCPsMaxed:
					return False
		return True

	def insertMark(self, firstLayer, centerPoint):
		pass

	def NewTabWithUnevenHandleDistributionsMain(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font

			if not thisFont or not len(thisFont.masters) > 1:
				Message(
					title="Uneven Handle Distribution Error",
					message="This script requires a multiple-master font, because it measures the difference between BCP distributions of a curve segment in one master to the same curve in other masters.",
					OKButton="Oops, OK"
				)
			else:
				Glyphs.clearLog()
				print("New Tab with Uneven Handle Distributions\nReport for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(f"📄 {thisFont.filepath}")
				else:
					print(f"📄 {thisFont.familyName} (unsaved)")
				print()

				# query user options:
				maxFactorChange = self.prefFloat("factorChangeEntry")
				# a factor of 0 (or an empty field) cannot be tolerated, there is nothing to compare against:
				shouldCheckFactorChange = self.pref("factorChange") and maxFactorChange > 0
				shouldCheckAnyMaxToNotMax = self.pref("anyMaxToNotMax")
				markInFirstMaster = self.pref("markInFirstMaster")

				glyphs = [g for g in thisFont.glyphs if g.mastersCompatible]
				print("Found %i compatible glyph%s." % (
					len(glyphs),
					"" if len(glyphs) == 1 else "s",
				))

				affectedGlyphs = []
				for thisGlyph in glyphs:
					firstLayer = thisGlyph.layers[0]
					if firstLayer.paths:
						otherLayers = [
							layer for layer in thisGlyph.layers if layer != firstLayer and (layer.isMasterLayer or layer.isSpecialLayer) and thisGlyph.mastersCompatibleForLayers_((layer, firstLayer))
						]
						for i, firstPath in enumerate(firstLayer.paths):
							if thisGlyph.name not in affectedGlyphs and not markInFirstMaster:
								for j, firstNode in enumerate(firstPath.nodes):
									if firstNode.type == CURVE:
										indexPrevNode = (j - 3) % len(firstPath.nodes)
										indexBCP1 = (j - 2) % len(firstPath.nodes)
										indexBCP2 = (j - 1) % len(firstPath.nodes)

										firstPrevNode = firstPath.nodes[indexPrevNode]
										firstBCP1 = firstPath.nodes[indexBCP1]
										firstBCP2 = firstPath.nodes[indexBCP2]

										firstIntersection = intersectionLineLinePoints(firstPrevNode, firstBCP1, firstBCP2, firstNode, includeMidBcp=True)
										if firstIntersection:
											if shouldCheckFactorChange:
												firstFactor = self.factor(firstPrevNode, firstBCP1, firstBCP2, firstNode, firstIntersection)
												if firstFactor is not None and self.factorChangeIsTooBig(maxFactorChange, firstFactor, i, indexPrevNode, indexBCP1, indexBCP2, j, otherLayers):
													if thisGlyph.name not in affectedGlyphs:
														affectedGlyphs.append(thisGlyph.name)
													if markInFirstMaster:
														centerPoint = bezierWithPoints(firstPrevNode, firstBCP1, firstBCP2, firstNode, 0.5)
														self.insertMark(firstLayer, centerPoint)
													else:
														break
											if shouldCheckAnyMaxToNotMax:
												firstBCPsMaxed = (firstBCP1.position == firstIntersection, firstBCP2.position == firstIntersection)
												if not self.isMaxTheSameEverywhere(firstBCPsMaxed, i, indexPrevNode, indexBCP1, indexBCP2, j, otherLayers):
													if thisGlyph.name not in affectedGlyphs:
														affectedGlyphs.append(thisGlyph.name)
													if markInFirstMaster:
														centerPoint = bezierWithPoints(firstPrevNode, firstBCP1, firstBCP2, firstNode, 0.5)
														self.insertMark(firstLayer, centerPoint)
													else:
														break
				if affectedGlyphs:
					tabString = "/" + "/".join(affectedGlyphs)
					# opens new Edit tab:
					thisFont.newTab(tabString)
					print("Affected glyphs:\n%s" % tabString)
				else:
					# Floating notification:
					Glyphs.showNotification(
						"Handle Distribution %s" % (thisFont.familyName),
						"Found no uneven BCP distributions in the font.",
					)

				self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("New Tab with Uneven Handle Distributions Error: %s" % e)
			import traceback
			print(traceback.format_exc())


NewTabWithUnevenHandleDistributions()
