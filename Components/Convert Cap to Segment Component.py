# MenuTitle: Convert Cap to Segment Component
__doc__ = """
Converts a _cap.xxx glyph into a _segment.xxx glyph. Rotates and repositions
the cap paths so the connection points (node1/node2 anchors, or path endpoints)
land on the baseline, then places start/end anchors there. Optionally updates
all glyphs in the font that reference the cap to use the new segment instead.
"""

import math
import re

import vanilla
from AppKit import NSAffineTransform, NSPoint, NSTextAlignmentRight, NSWindowStyleMaskResizable, NSSize, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import CAP, SEGMENT, GSAnchor, GSHint, GSLayer, Glyphs, Message
from mekkablue import UpdateButton, mekkaObject, newGlyphWithName, clearGuides


def sanitizeSuffix(text):
	"""Keep only characters allowed in glyph name suffixes: A-Z, a-z, 0-9, hyphen, period, underscore."""
	return re.sub(r'[^A-Za-z0-9\-._]', '', text)


def plural(count, noun):
	return f"{count} {noun}{'' if count == 1 else 's'}"


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
		# state for the one Undo step (None as long as there is nothing to undo)
		self.undoState = None

		windowWidth = 390
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Convert Cap to Segment Component",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		inset = 15

		# cap combo box + update button
		tooltipText = "The _cap.xxx glyph to convert into a _segment component."
		self.w.capLabel = vanilla.TextBox("auto", "Convert cap", sizeStyle="small")
		self.w.capLabel.setToolTip(tooltipText)
		self.w.capGlyphName = vanilla.ComboBox("auto", self.allCapGlyphs(), sizeStyle="small", callback=self.SavePreferences)
		self.w.capGlyphName.setToolTip(tooltipText)
		self.w.updateCapList = UpdateButton("auto", callback=self.updateCapList)
		self.w.updateCapList.setToolTip("Refreshes the list of _cap.xxx glyphs from the frontmost font.")

		# rename suffix
		tooltipText = "Suffix of the new _segment glyph. Empty keeps the suffix of the cap. Allowed: A–Z, a–z, 0–9, hyphen, period, underscore; other characters are removed."
		self.w.renameLabel = vanilla.TextBox("auto", "Rename to _segment.", sizeStyle="small")
		self.w.renameLabel.setToolTip(tooltipText)
		self.w.renameTo = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		self.w.renameTo.setToolTip(tooltipText)
		self.w.renameTo.getNSTextField().setPlaceholderString_("Leave empty for keeping cap suffix")

		# options
		self.w.updateAffectedGlyphs = vanilla.CheckBox("auto", "Update all affected glyphs", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.updateAffectedGlyphs.setToolTip("Creates the segment, switches all glyphs using the cap to it (in all layers, including backups), and deletes the cap. If off, only creates the segment.")
		self.w.decomposeBackup = vanilla.CheckBox("auto", "Decomposed backup in background", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.decomposeBackup.setToolTip("Before converting, copies the decomposed outlines of each affected master and special layer into its background.")
		self.w.openTab = vanilla.CheckBox("auto", "Open tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.openTab.setToolTip("Opens a tab with the new segment and all updated glyphs.")
		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.reuseTab.setToolTip("Replaces the text of the current tab instead of opening a new one. Needs ‘Open tab’.")

		# Status line (bottom, left of run button)
		self.w.statusText = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.statusText.setToolTip("Progress and result of the last run.")
		self.w.statusText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Undo button
		self.w.undoButton = vanilla.Button("auto", "Undo", callback=self.undo)
		self.w.undoButton.setToolTip("Restores the glyphs as they were before the last conversion. Available only after a conversion.")
		self.w.undoButton.enable(False)

		# Run button
		self.w.runButton = vanilla.Button("auto", "Convert", callback=self.run)
		self.w.runButton.setToolTip("Converts the cap into a segment with the settings above.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels: right-aligned, same width, hugging their text
		labelNames = ("capLabel", "renameLabel")
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[capLabel]-gap-[capGlyphName]-gap-[updateCapList]-inset-|",
				"H:|-inset-[renameLabel]-gap-[renameTo]-inset-|",
				"H:|-inset-[updateAffectedGlyphs]-(>=inset)-|",
				"H:|-inset-[decomposeBackup]-(>=inset)-|",
				"H:|-inset-[openTab]-gap-[reuseTab]-(>=inset)-|",
				"H:|-inset-[statusText]-inset-|",
				"H:|-inset-[undoButton(>=80)]-(>=gap)-[runButton(>=80)]-inset-|",
				"V:|-inset-[capGlyphName]-row-[renameTo]-checkGap-[updateAffectedGlyphs]-checkRow-[decomposeBackup]-checkRow-[openTab]-inset-[statusText]-gap-[runButton]-inset-|",
				{"view1": self.w.capLabel, "attribute1": "centerY", "view2": self.w.capGlyphName, "attribute2": "centerY"},
				{"view1": self.w.updateCapList, "attribute1": "centerY", "view2": self.w.capGlyphName, "attribute2": "centerY"},
				{"view1": self.w.renameLabel, "attribute1": "centerY", "view2": self.w.renameTo, "attribute2": "centerY"},
				{"view1": self.w.undoButton, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.reuseTab, "attribute1": "centerY", "view2": self.w.openTab, "attribute2": "centerY"},
				{"view1": self.w.capLabel, "attribute1": "width", "view2": self.w.renameLabel, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkGap": 10, "checkRow": 5},
		)

		self.LoadPreferences()
		self.updateCapList()  # reset to first cap if stored name is no longer valid
		self.w.open()
		self.w.makeKey()

		# make the window horizontally resizable, but keep the height that Auto Layout determined.
		# (Content sizes set directly on the NSWindow, so the title bar is not counted twice.)
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()
		contentSize = nsWindow.contentView().frame().size
		nsWindow.setContentMinSize_(NSSize(round(contentSize.width * 0.75), contentSize.height))  # 25% narrower than the initial width
		nsWindow.setContentMaxSize_(NSSize(contentSize.width + 1000, contentSize.height))

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
		self.w.reuseTab.enable(self.prefBool("openTab"))

	def setStatus(self, text):
		"""Sets the status line and redraws it right away, so it shows while the script is busy."""
		self.w.statusText.set(text)
		self.w.statusText.getNSTextField().display()

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

		segmentGlyph = newGlyphWithName(segmentGlyphName)
		segmentGlyph.category = "Corner"
		segmentGlyph.export = False
		segmentGlyph.leftMetricsKey = "=100"
		segmentGlyph.rightMetricsKey = "=100"
		font.glyphs.append(segmentGlyph)

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
				segmentLayer.shapes.append(path.copy())

			# Apply the aligning transform: move startPos to origin, rotate to baseline
			t = self.buildAlignTransform(startPos, endPos)
			segmentLayer.applyTransform(t.transformStruct())

			# Clear guides and anchors before setting sidebearings
			clearGuides(segmentLayer)
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
	# Undo
	# -------------------------------------------------------------------------

	def undo(self, sender=None):
		"""Restores the glyphs of the last conversion (one step): removes the new segment and puts back the stored copies."""
		state = self.undoState
		if state is None:
			return
		font = state["font"]
		if font not in Glyphs.fonts:
			self.undoState = None
			self.w.undoButton.enable(False)
			self.setStatus("⚠️ The font was closed, nothing to undo.")
			return

		font.disableUpdateInterface()
		try:
			# the new segment goes away, a segment of the same name that existed before comes back:
			segmentGlyphName = state["segmentGlyphName"]
			if font.glyphs[segmentGlyphName]:
				del font.glyphs[segmentGlyphName]
			if state["previousSegment"] is not None:
				font.glyphs.append(state["previousSegment"])

			# the affected glyphs and the cap come back in their previous state:
			for glyphName, glyphCopy in state["glyphs"]:
				if font.glyphs[glyphName]:
					del font.glyphs[glyphName]
				font.glyphs.append(glyphCopy)
		finally:
			font.enableUpdateInterface()

		print(f"↩️ Undo: restored {plural(len(state['glyphs']), 'glyph')}, removed {segmentGlyphName}.")
		self.undoState = None
		self.w.undoButton.enable(False)
		self.setStatus("↩️ Conversion undone.")

	# -------------------------------------------------------------------------
	# Main action
	# -------------------------------------------------------------------------

	def run(self, sender=None):
		try:
			self.SavePreferences()
			font = Glyphs.font
			if not font:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			capGlyphName = self.pref("capGlyphName").strip()
			if not capGlyphName or not capGlyphName.startswith("_cap."):
				Message(title="No Cap Selected", message=f"Please select a _cap.xxx glyph. Got: ‘{capGlyphName}’", OKButton=None)
				return

			capGlyph = font.glyphs[capGlyphName]
			if capGlyph is None:
				Message(title="Cap Not Found", message=f"Could not find ‘{capGlyphName}’ in the frontmost font.", OKButton=None)
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
			print("Convert Cap to Segment Component Report\n")
			print(f"\t{capGlyphName} → {segmentGlyphName}\n")

			# remember the state before any change, for Undo (names and copies of the affected glyphs, and of the cap):
			affectedGlyphs = self.findAffectedGlyphs(font, capGlyphName) if updateAffectedGlyphs else []
			namesToRemember = affectedGlyphs + ([capGlyphName] if updateAffectedGlyphs else [])
			previousSegment = font.glyphs[segmentGlyphName]
			self.undoState = {
				"font": font,
				"segmentGlyphName": segmentGlyphName,
				"previousSegment": previousSegment.copy() if previousSegment else None,
				"glyphs": [(name, font.glyphs[name].copy()) for name in namesToRemember if font.glyphs[name]],
			}
			self.w.undoButton.enable(True)

			# Step 1: create the _segment glyph
			self.setStatus(f"🔧 Creating {segmentGlyphName}…")
			font.disableUpdateInterface()
			try:
				self.createSegmentGlyph(font, capGlyph, segmentGlyphName)
			finally:
				font.enableUpdateInterface()

			tabGlyphs = [segmentGlyphName]
			updatedCount = 0

			if updateAffectedGlyphs:
				print(f"\tFound {plural(len(affectedGlyphs), 'glyph')} referencing {capGlyphName}\n")

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
				statusMsg = f"✅ Updated {plural(updatedCount, 'glyph')} to use {segmentGlyphName}."
				print(f"\n{statusMsg}")
				Glyphs.showNotification("Convert Cap to Segment", f"Updated {plural(updatedCount, 'glyph')}. {capGlyphName} → {segmentGlyphName}")
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
