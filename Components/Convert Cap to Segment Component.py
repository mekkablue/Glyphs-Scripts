# MenuTitle: Convert Cap to Segment Component
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Converts a _cap.xxx glyph into a _segment.xxx glyph. Rotates and repositions
the cap paths so the connection points (node1/node2 anchors, or path endpoints)
land on the baseline, then places start/end anchors there. Optionally updates
all glyphs in the font that reference the cap to use the new segment instead.
"""

import math
import re

import vanilla
from AppKit import NSAffineTransform, NSPoint
from GlyphsApp import CAP, SEGMENT, GSAnchor, GSGlyph, GSHint, GSLayer, Glyphs, Message
from mekkablue import UpdateButton, mekkaObject


def sanitizeSuffix(text):
	"""Keep only characters allowed in glyph name suffixes: A-Z, a-z, 0-9, hyphen, period, underscore."""
	return re.sub(r'[^A-Za-z0-9\-._]', '', text)


class ConvertCapToSegmentComponent(mekkaObject):
	prefDict = {
		"capGlyphName": "",
		"renameTo": "",
		"updateAffectedGlyphs": 1,
		"decomposeBackup": 1,
		"openTab": 1,
		"reuseTab": 1,
	}

	def __init__(self):
		windowWidth = 390
		windowHeight = 185
		windowWidthResize = 400
		windowHeightResize = 0
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Convert Cap to Segment Component",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),
			autosaveName=self.domain("mainwindow"),
		)

		linePos, inset, lineHeight = 12, 15, 22

		# Line 1: cap combo box + update button
		self.w.capLabel = vanilla.TextBox((inset, linePos + 2, 75, 14), "Convert cap:", sizeStyle="small")
		self.w.capGlyphName = vanilla.ComboBox((inset + 75, linePos - 1, -inset - 26, 18), self.allCapGlyphs(), sizeStyle="small", callback=self.SavePreferences)
		self.w.capGlyphName.getNSComboBox().setToolTip_("Select the _cap.xxx glyph to convert to a _segment component.")
		self.w.updateCapList = UpdateButton((-inset - 19, linePos - 3, -inset, 18), callback=self.updateCapList)
		self.w.updateCapList.getNSButton().setToolTip_("Update the list of _cap.xxx glyphs from the frontmost font.")
		linePos += lineHeight

		# Line 2: rename suffix
		self.w.renameLabel = vanilla.TextBox((inset, linePos + 2, 122, 14), "Rename to: _segment.", sizeStyle="small")
		self.w.renameTo = vanilla.EditText((inset + 122, linePos - 1, -inset, 19), "", callback=self.SavePreferences, sizeStyle="small")
		self.w.renameTo.getNSTextField().setToolTip_(
			"Suffix for the new _segment glyph name. Leave empty to keep the same suffix as the selected _cap glyph. "
			"Allowed characters: A–Z, a–z, 0–9, hyphen (-), period (.), underscore (_). Spaces and other characters are removed."
		)
		self.w.renameTo.getNSTextField().setPlaceholderString_("Leave empty for keeping cap suffix")
		linePos += lineHeight

		# Line 3: update all affected glyphs
		self.w.updateAffectedGlyphs = vanilla.CheckBox((inset, linePos, -inset, 20), "Update all affected glyphs", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.updateAffectedGlyphs.getNSButton().setToolTip_(
			"If enabled: create the _segment glyph, delete the _cap glyph, and update all cap component references "
			"in all glyph layers (including backups) to use the new segment. "
			"If disabled: only create the _segment glyph without removing the _cap or modifying other glyphs."
		)
		linePos += lineHeight

		# Line 4: decomposed backup in background
		self.w.decomposeBackup = vanilla.CheckBox((inset, linePos, -inset, 20), "Decomposed backup in background", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.decomposeBackup.getNSButton().setToolTip_(
			"Before converting, copy the current layer content into the background of each master/special layer "
			"in affected glyphs, then decompose regular components there. Gives you a backup of the original state."
		)
		linePos += lineHeight

		# Line 5: open tab + reuse tab
		self.w.openTab = vanilla.CheckBox((inset, linePos, 90, 20), "Open tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.openTab.getNSButton().setToolTip_("After conversion, open a tab showing the new _segment glyph and all updated glyphs.")
		self.w.reuseTab = vanilla.CheckBox((inset + 90, linePos, -inset, 20), "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.reuseTab.getNSButton().setToolTip_("If 'Open tab' is active: replace the content of the current tab instead of opening a new one.")
		linePos += lineHeight

		# Status line (bottom, left of run button)
		self.w.statusText = vanilla.TextBox((inset, -20 - inset + 3, -inset - 96, 14), "🤖 Ready.", sizeStyle="small")

		# Run button
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Convert", callback=self.run)
		self.w.setDefaultButton(self.w.runButton)

		self.LoadPreferences()
		self.updateCapList()  # reset to first cap if stored name is no longer valid
		self.w.open()
		self.w.makeKey()

	def allCapGlyphs(self):
		font = Glyphs.font
		if not font:
			return []
		return [g.name for g in font.glyphs if g.name.startswith("_cap.")]

	def updateCapList(self, sender=None):
		currentName = self.pref("capGlyphName")
		capGlyphs = self.allCapGlyphs()
		self.w.capGlyphName.setItems(capGlyphs)
		if currentName in capGlyphs:
			self.w.capGlyphName.set(currentName)
		elif capGlyphs:
			self.w.capGlyphName.set(capGlyphs[0])
			self.SavePreferences()

	def updateUI(self, sender=None):
		openTab = self.prefBool("openTab")
		self.w.reuseTab.enable(openTab)

	def setStatus(self, text):
		self.w.statusText.set(text)

	# -------------------------------------------------------------------------
	# Geometry helpers
	# -------------------------------------------------------------------------

	def getCapConnectionPoints(self, layer):
		"""Return (startPos, endPos) from the first path's first and last nodes."""
		if not layer.paths:
			return None, None
		firstPath = layer.paths[0]
		if not firstPath.nodes:
			return None, None
		n0 = firstPath.nodes[0]
		n1 = firstPath.nodes[-1]
		return NSPoint(n0.position.x, n0.position.y), NSPoint(n1.position.x, n1.position.y)

	def buildAlignTransform(self, node1Pos, node2Pos):
		"""
		Build an NSAffineTransform that:
		  1. Translates so node1 moves to the origin (0, 0).
		  2. Rotates so the node1→node2 direction aligns with the positive x-axis (baseline).
		Uses appendTransform_ so operations are applied in the order listed.
		"""
		dx = (node2Pos.x - node1Pos.x) if node2Pos else 0.0
		dy = (node2Pos.y - node1Pos.y) if node2Pos else 0.0
		angleDeg = math.degrees(math.atan2(dy, dx))

		t1 = NSAffineTransform.transform()
		t1.translateXBy_yBy_(-node1Pos.x, -node1Pos.y)

		t2 = NSAffineTransform.transform()
		t2.rotateByDegrees_(-angleDeg)

		t = NSAffineTransform.transform()
		t.appendTransform_(t1)  # applied first: move node1 to origin
		t.appendTransform_(t2)  # applied second: rotate to baseline
		return t

	# -------------------------------------------------------------------------
	# Segment creation
	# -------------------------------------------------------------------------

	def createSegmentGlyph(self, font, capGlyph, segmentGlyphName):
		"""Create a _segment glyph from the cap's paths, rotated to the baseline."""
		if font.glyphs[segmentGlyphName]:
			del font.glyphs[segmentGlyphName]

		segmentGlyph = GSGlyph(segmentGlyphName)
		segmentGlyph.category = "Corner"
		segmentGlyph.export = False
		segmentGlyph.leftMetricsKey = "=100"
		segmentGlyph.rightMetricsKey = "=100"
		font.glyphs.append(segmentGlyph)

		font.disableUpdateInterface()
		try:
			for capLayer in capGlyph.layers:
				startPos, endPos = self.getCapConnectionPoints(capLayer)
				if startPos is None:
					continue  # no geometry in this layer

				# Find or create the corresponding layer in the segment glyph
				segmentLayer = segmentGlyph.layers[capLayer.layerId]
				if segmentLayer is None:
					segmentLayer = GSLayer()
					segmentLayer.layerId = capLayer.layerId
					segmentLayer.name = capLayer.name
					if hasattr(capLayer, 'associatedMasterId'):
						segmentLayer.associatedMasterId = capLayer.associatedMasterId
					segmentGlyph.layers.append(segmentLayer)

				# Copy paths only (no guides, no anchors yet)
				for path in capLayer.paths:
					segmentLayer.paths.append(path.copy())

				# Apply the aligning transform: move startPos to origin, rotate to baseline
				t = self.buildAlignTransform(startPos, endPos)
				segmentLayer.applyTransform(t.transformStruct())

				# Clear guides and anchors before setting sidebearings
				segmentLayer.guides = []
				segmentLayer.anchors = []

				# Set sidebearings — Glyphs shifts the paths to achieve these values;
				# read node positions afterwards so anchors land on the actual nodes
				segmentLayer.LSB = 100
				segmentLayer.RSB = 100

				firstPath = segmentLayer.paths[0]
				actualStart = firstPath.nodes[0].position
				actualEnd = firstPath.nodes[-1].position

				startAnchor = GSAnchor()
				startAnchor.name = "start"
				startAnchor.position = NSPoint(actualStart.x, actualStart.y)
				segmentLayer.anchors.append(startAnchor)

				endAnchor = GSAnchor()
				endAnchor.name = "end"
				endAnchor.position = NSPoint(actualEnd.x, actualEnd.y)
				segmentLayer.anchors.append(endAnchor)

				segmentLayer.updateHints()
		finally:
			font.enableUpdateInterface()

		print(f"\t☑️ Created {segmentGlyphName}")
		return segmentGlyph

	# -------------------------------------------------------------------------
	# Affected glyph helpers
	# -------------------------------------------------------------------------

	def findAffectedGlyphs(self, font, capGlyphName):
		"""Return a list of glyph names that reference capGlyphName as a CAP hint in any layer."""
		affected = []
		for glyph in font.glyphs:
			for layer in glyph.layers:
				if any(h.type == CAP and h.name == capGlyphName for h in layer.hints):
					affected.append(glyph.name)
					break
		return affected

	def createDecomposeBackup(self, glyph):
		"""Store fully decomposed shapes (including caps/corners) in the background of each master/special layer."""
		for layer in glyph.layers:
			if layer.isMasterLayer or layer.isSpecialLayer:
				layer.background.clear()
				layer.background.shapes = layer.copyDecomposedLayer().shapes

	def updateGlyphCapToSegment(self, glyph, capGlyphName, segmentGlyphName):
		"""Change every CAP hint named capGlyphName to a SEGMENT hint in all layers of glyph."""
		for layer in glyph.layers:
			changed = False
			for hint in layer.hints:
				if hint.type == CAP and hint.name == capGlyphName:
					originNode = hint.originNode
					nextNode = originNode.nextNode if originNode is not None else None
					hint.type = SEGMENT
					hint.name = segmentGlyphName
					if nextNode is not None:
						hint.originNode = nextNode
					changed = True
			if changed:
				layer.updateHints()

	# -------------------------------------------------------------------------
	# Main action
	# -------------------------------------------------------------------------

	def run(self, sender=None):
		try:
			self.SavePreferences()
			font = Glyphs.font
			if not font:
				Message("No font open", "Please open a font and try again.", OKButton=None)
				return

			capGlyphName = self.pref("capGlyphName").strip()
			if not capGlyphName or not capGlyphName.startswith("_cap."):
				Message("No cap selected", f"Please select a _cap.xxx glyph. Got: '{capGlyphName}'", OKButton=None)
				return

			capGlyph = font.glyphs[capGlyphName]
			if capGlyph is None:
				Message("Cap not found", f"Could not find '{capGlyphName}' in the current font.", OKButton=None)
				return

			capSuffix = capGlyphName[len("_cap."):]
			renameTo = sanitizeSuffix(self.pref("renameTo").strip())
			segmentSuffix = renameTo if renameTo else capSuffix
			segmentGlyphName = "_segment." + segmentSuffix

			updateAffectedGlyphs = self.prefBool("updateAffectedGlyphs")
			doDecomposeBackup = self.prefBool("decomposeBackup")
			openTab = self.prefBool("openTab")
			reuseTab = self.prefBool("reuseTab")

			Glyphs.clearLog()
			print(f"Convert Cap to Segment Component\n")
			print(f"\t{capGlyphName} → {segmentGlyphName}\n")

			# Step 1: create the _segment glyph
			self.setStatus(f"🔧 Creating {segmentGlyphName}…")
			font.disableUpdateInterface()
			try:
				segmentGlyph = self.createSegmentGlyph(font, capGlyph, segmentGlyphName)
			finally:
				font.enableUpdateInterface()

			if segmentGlyph is None:
				self.setStatus("❌ Aborted.")
				return

			tabGlyphs = [segmentGlyphName]
			updatedCount = 0

			if updateAffectedGlyphs:
				affectedGlyphs = self.findAffectedGlyphs(font, capGlyphName)
				print(f"\tFound {len(affectedGlyphs)} glyph{'' if len(affectedGlyphs)==1 else 's'} referencing {capGlyphName}\n")

				font.disableUpdateInterface()
				try:
					# Step 2: optional decomposed backup
					if doDecomposeBackup:
						self.setStatus("💾 Creating decomposed backups…")
						for glyphName in affectedGlyphs:
							glyph = font.glyphs[glyphName]
							if glyph:
								self.createDecomposeBackup(glyph)

					# Step 3: convert CAP hints to SEGMENT hints
					for glyphName in affectedGlyphs:
						self.setStatus(f"🔡 {glyphName}")
						glyph = font.glyphs[glyphName]
						if glyph:
							self.updateGlyphCapToSegment(glyph, capGlyphName, segmentGlyphName)
							tabGlyphs.append(glyphName)
							updatedCount += 1
							print(f"\t✅ {glyphName}")

					# Step 4: delete the _cap glyph
					self.setStatus(f"🗑️ Removing {capGlyphName}…")
					del font.glyphs[capGlyphName]
					print(f"\n\t🗑️ Deleted {capGlyphName}")

				finally:
					font.enableUpdateInterface()

			# Step 5: open tab
			if openTab and tabGlyphs:
				tabString = "/" + "/".join(tabGlyphs)
				if reuseTab and font.currentTab:
					font.currentTab.text = tabString
				else:
					font.newTab(tabString)

			if updateAffectedGlyphs:
				statusMsg = f"✅ Updated {updatedCount} glyph{'' if updatedCount==1 else 's'} to use {segmentGlyphName}."
				print(f"\n{statusMsg}")
				Glyphs.showNotification("Convert Cap to Segment", f"Updated {updatedCount} glyph{'' if updatedCount==1 else 's'}. {capGlyphName} → {segmentGlyphName}")
			else:
				statusMsg = f"✅ Created {segmentGlyphName}."
				print(f"\n{statusMsg}")
				Glyphs.showNotification("Convert Cap to Segment", f"Created {segmentGlyphName}.")

			self.setStatus(statusMsg)

		except Exception as e:
			import traceback
			Glyphs.showMacroWindow()
			print(f"❌ Error: {e}\n{traceback.format_exc()}")
			self.setStatus("❌ Error — see Macro Window.")


ConvertCapToSegmentComponent()
