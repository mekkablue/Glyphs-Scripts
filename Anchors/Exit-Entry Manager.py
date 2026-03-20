# MenuTitle: Exit-Entry Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Toolbox for managing exit/entry and #exit/#entry anchors used for cursive attachment.
Insert anchors at sidebearings, at selected nodes, or for positional glyphs;
add or remove the # prefix; swap or delete anchors — all from one place.
"""

import vanilla
from mekkablue import mekkaObject
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSAnchor, GSPath, GSNode, GSOFFCURVE, GSLTR, GSRTL


class ExitEntryManager(mekkaObject):
	prefDict = {
		"useHashtag": True,
		"overwriteExisting": False,
		"allLayers": True,
		"applyFontWide": False,
	}

	def __init__(self):
		windowWidth = 380
		windowHeight = 330
		windowWidthResize = 100
		windowHeightResize = 0
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Exit-Entry Manager",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),
			autosaveName=self.domain("mainwindow"),
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		buttonWidth = 90
		buttonX = -(inset + buttonWidth)

		# ── Insert section ──────────────────────────────────────────────────────
		self.w.insertSideText = vanilla.TextBox((inset, linePos + 2, buttonX - 5, 14), "Insert at sidebearings (LTR: entry@LSB, exit@RSB; RTL: vice versa):", sizeStyle="small", selectable=True)
		self.w.insertSideButton = vanilla.Button((buttonX, linePos, -inset, 20), "Insert", callback=self.insertAtSidebearings, sizeStyle="small")
		self.w.insertSideText.setToolTip("LTR glyphs: entry at x=0 (LSB), exit at x=width (RSB). RTL glyphs: exit at x=0, entry at x=width. Respects '# prefix' and 'Overwrite' checkboxes.")
		self.w.insertSideButton.setToolTip("Insert entry/exit anchors at sidebearings, direction-aware.")
		linePos += lineHeight

		self.w.insertNodeText = vanilla.TextBox((inset, linePos + 2, buttonX - 5, 14), "Insert at outermost selected nodes (y=0, direction-aware):", sizeStyle="small", selectable=True)
		self.w.insertNodeButton = vanilla.Button((buttonX, linePos, -inset, 20), "Insert", callback=self.insertAtSelectedNodes, sizeStyle="small")
		self.w.insertNodeText.setToolTip("Uses x of outermost selected nodes to place entry/exit at y=0. LTR: entry left, exit right. RTL: exit left, entry right. Always uses the current selection; ignores 'Apply to ALL glyphs'.")
		self.w.insertNodeButton.setToolTip("Place entry/exit anchors at x of outermost selected nodes, y=0, direction-aware.")
		linePos += lineHeight

		self.w.insertPositionalText = vanilla.TextBox((inset, linePos + 2, buttonX - 5, 14), "Insert for positional glyphs (.init/.medi/.fina, direction-aware):", sizeStyle="small", selectable=True)
		self.w.insertPositionalButton = vanilla.Button((buttonX, linePos, -inset, 20), "Insert", callback=self.insertForPositionalGlyphs, sizeStyle="small")
		self.w.insertPositionalText.setToolTip("RTL (.init/.medi): exit at x=0; (.medi/.fina): entry at rightmost oncurve. LTR (.init/.medi): exit at rightmost oncurve; (.medi/.fina): entry at leftmost oncurve. Skips non-positional glyphs.")
		self.w.insertPositionalButton.setToolTip("Insert exit/entry anchors for positional glyphs (.init/.medi/.fina), direction-aware.")
		linePos += lineHeight + 4

		self.w.separator1 = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 10

		# ── Prefix section ──────────────────────────────────────────────────────
		self.w.addHashText = vanilla.TextBox((inset, linePos + 2, buttonX - 5, 14), "Add # prefix: exit → #exit, entry → #entry:", sizeStyle="small", selectable=True)
		self.w.addHashButton = vanilla.Button((buttonX, linePos, -inset, 20), "Add #", callback=self.addHashPrefix, sizeStyle="small")
		self.w.addHashText.setToolTip("Renames 'exit' to '#exit' and 'entry' to '#entry' in selected (or all) glyphs. The '#' prefix disables automatic curs feature generation by Glyphs.")
		self.w.addHashButton.setToolTip("Add # prefix to all exit/entry anchors (disables curs feature generation).")
		linePos += lineHeight

		self.w.removeHashText = vanilla.TextBox((inset, linePos + 2, buttonX - 5, 14), "Remove # prefix: #exit → exit, #entry → entry:", sizeStyle="small", selectable=True)
		self.w.removeHashButton = vanilla.Button((buttonX, linePos, -inset, 20), "Remove #", callback=self.removeHashPrefix, sizeStyle="small")
		self.w.removeHashText.setToolTip("Renames '#exit' to 'exit' and '#entry' to 'entry' in selected (or all) glyphs. This re-enables automatic curs feature generation.")
		self.w.removeHashButton.setToolTip("Remove # prefix from all #exit/#entry anchors (enables curs feature generation).")
		linePos += lineHeight + 4

		self.w.separator2 = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 10

		# ── Utility section ─────────────────────────────────────────────────────
		self.w.swapText = vanilla.TextBox((inset, linePos + 2, buttonX - 5, 14), "Swap exit ↔ entry anchor positions:", sizeStyle="small", selectable=True)
		self.w.swapButton = vanilla.Button((buttonX, linePos, -inset, 20), "Swap", callback=self.swapExitEntry, sizeStyle="small")
		self.w.swapText.setToolTip("Exchanges the x/y positions of exit and entry anchors (both with and without # prefix). Useful when converting between LTR and RTL layouts.")
		self.w.swapButton.setToolTip("Swap positions of exit and entry anchors in selected (or all) glyphs.")
		linePos += lineHeight

		self.w.removeAnchorText = vanilla.TextBox((inset, linePos + 2, buttonX - 5, 14), "Remove all exit/entry anchors (with and without #):", sizeStyle="small", selectable=True)
		self.w.removeAnchorButton = vanilla.Button((buttonX, linePos, -inset, 20), "Remove", callback=self.removeAnchors, sizeStyle="small")
		self.w.removeAnchorText.setToolTip("Deletes all exit, entry, #exit, and #entry anchors from selected (or all) glyphs, in all processed layers.")
		self.w.removeAnchorButton.setToolTip("Delete all exit/entry anchors (with or without # prefix) from selected glyphs.")
		linePos += lineHeight + 4

		self.w.separator3 = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 10

		# ── Options ─────────────────────────────────────────────────────────────
		self.w.useHashtag = vanilla.CheckBox((inset, linePos, -inset, 20), "Use # prefix for insert operations (#exit, #entry)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.useHashtag.setToolTip("When inserting anchors, use '#exit'/'#entry' (checked) or 'exit'/'entry' (unchecked). Applies to all three Insert operations above.")
		linePos += lineHeight

		self.w.overwriteExisting = vanilla.CheckBox((inset, linePos, -inset, 20), "Overwrite existing exit/entry anchors", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.overwriteExisting.setToolTip("If checked, existing exit/entry anchors are replaced. If unchecked, existing anchors are kept and only missing ones are added.")
		linePos += lineHeight

		self.w.allLayers = vanilla.CheckBox((inset, linePos, -inset, 20), "All masters and special layers (otherwise current master only)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.allLayers.setToolTip("Process all master layers and special layers (brace/bracket layers). Unchecked: only layers associated with the currently active master.")
		linePos += lineHeight

		self.w.applyFontWide = vanilla.CheckBox((inset, linePos, -inset, 20), "⚠️ Apply to ALL glyphs (otherwise selected glyphs only)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.applyFontWide.setToolTip("Process every glyph in the font. Unchecked: only the currently selected glyphs.")
		linePos += lineHeight + 5

		self.w.status = vanilla.TextBox((inset, linePos, -inset, 14), "", sizeStyle="small")
		linePos += lineHeight

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	# ── Helpers ─────────────────────────────────────────────────────────────────

	def anchorName(self, baseName):
		"""Returns anchor name with or without # prefix based on the useHashtag setting."""
		prefix = "#" if self.prefBool("useHashtag") else ""
		return "%s%s" % (prefix, baseName)

	def getGlyphsToProcess(self):
		font = Glyphs.font
		if not font:
			return []
		if self.prefBool("applyFontWide"):
			return list(font.glyphs)
		return [layer.parent for layer in font.selectedLayers if layer.parent]

	def getLayersFromGlyph(self, glyph):
		font = Glyphs.font
		if self.prefBool("allLayers"):
			return [l for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer]
		else:
			currentMasterId = font.selectedFontMaster.id
			return [l for l in glyph.layers if l.associatedMasterId == currentMasterId and l.isMasterLayer]

	def _getPaths(self, layer):
		try:
			return [p for p in layer.shapes if isinstance(p, GSPath)]
		except Exception:
			return layer.paths

	def rightmostOncurve(self, layer):
		"""Returns the rightmost oncurve node in the layer, or None."""
		result = None
		for path in self._getPaths(layer):
			for node in path.nodes:
				if node.type != GSOFFCURVE:
					if result is None or node.x > result.x:
						result = node
		return result

	def leftmostOncurve(self, layer):
		"""Returns the leftmost oncurve node in the layer, or None."""
		result = None
		for path in self._getPaths(layer):
			for node in path.nodes:
				if node.type != GSOFFCURVE:
					if result is None or node.x < result.x:
						result = node
		return result

	def updateUI(self, sender=None):
		# "Insert at selected nodes" only works with an active selection, not font-wide
		self.w.insertNodeButton.enable(not self.prefBool("applyFontWide"))

	def setStatus(self, msg):
		self.w.status.set(msg)

	# ── Insert operations ────────────────────────────────────────────────────────

	def insertAtSidebearings(self, sender=None):
		font = Glyphs.font
		if not font:
			return
		glyphs = self.getGlyphsToProcess()
		if not glyphs:
			self.setStatus("No glyphs to process.")
			return

		overwrite = self.prefBool("overwriteExisting")
		exitName = self.anchorName("exit")
		entryName = self.anchorName("entry")
		count = 0

		font.disableUpdateInterface()
		try:
			for glyph in glyphs:
				isLTR = glyph.direction == GSLTR
				for layer in self.getLayersFromGlyph(glyph):
					xEntry = 0.0 if isLTR else layer.width
					xExit = layer.width if isLTR else 0.0
					for anchorName, x in ((entryName, xEntry), (exitName, xExit)):
						if not layer.anchors[anchorName] or overwrite:
							newAnchor = GSAnchor()
							newAnchor.name = anchorName
							newAnchor.position = NSPoint(x, 0.0)
							layer.anchors.append(newAnchor)
							count += 1
		finally:
			font.enableUpdateInterface()
		self.setStatus("Inserted %i anchor%s in %i glyph%s." % (count, "" if count == 1 else "s", len(glyphs), "" if len(glyphs) == 1 else "s"))

	def insertAtSelectedNodes(self, sender=None):
		font = Glyphs.font
		if not font:
			return

		overwrite = self.prefBool("overwriteExisting")
		exitName = self.anchorName("exit")
		entryName = self.anchorName("entry")
		count = 0
		glyphsProcessed = 0

		font.disableUpdateInterface()
		try:
			for activeLayer in font.selectedLayers:
				glyph = activeLayer.parent
				if not glyph:
					continue

				isLTR = glyph.direction == GSLTR
				selectedNodes = sorted(
					[item for item in activeLayer.selection if isinstance(item, GSNode)],
					key=lambda n: n.x,
				)
				if not selectedNodes:
					continue

				bounds = activeLayer.bounds
				if bounds.size.width == 0:
					continue
				threshold = bounds.origin.x + bounds.size.width / 2

				xEntry = None
				xExit = None
				if isLTR:
					# LTR: entry on the left, exit on the right
					if selectedNodes[0].x <= threshold:
						xEntry = selectedNodes[0].x
					if selectedNodes[-1].x >= threshold:
						xExit = selectedNodes[-1].x
				else:
					# RTL: exit on the left, entry on the right
					if selectedNodes[0].x <= threshold:
						xExit = selectedNodes[0].x
					if selectedNodes[-1].x >= threshold:
						xEntry = selectedNodes[-1].x

				glyphsProcessed += 1
				for layer in self.getLayersFromGlyph(glyph):
					if xEntry is not None and (not layer.anchors[entryName] or overwrite):
						layer.anchors.append(GSAnchor(entryName, NSPoint(xEntry, 0.0)))
						count += 1
					if xExit is not None and (not layer.anchors[exitName] or overwrite):
						layer.anchors.append(GSAnchor(exitName, NSPoint(xExit, 0.0)))
						count += 1
		finally:
			font.enableUpdateInterface()
		self.setStatus("Inserted %i anchor%s in %i glyph%s." % (count, "" if count == 1 else "s", glyphsProcessed, "" if glyphsProcessed == 1 else "s"))

	def insertForPositionalGlyphs(self, sender=None):
		font = Glyphs.font
		if not font:
			return
		glyphs = self.getGlyphsToProcess()
		if not glyphs:
			self.setStatus("No glyphs to process.")
			return

		overwrite = self.prefBool("overwriteExisting")
		exitName = self.anchorName("exit")
		entryName = self.anchorName("entry")
		count = 0
		skipped = 0

		font.disableUpdateInterface()
		try:
			for glyph in glyphs:
				glyphName = glyph.name
				isInit = ".init" in glyphName
				isMedi = ".medi" in glyphName
				isFina = ".fina" in glyphName
				if not (isInit or isMedi or isFina):
					skipped += 1
					continue
				isLTR = glyph.direction == GSLTR
				for layer in self.getLayersFromGlyph(glyph):
					hasPaths = bool(self._getPaths(layer))
					if not hasPaths:
						continue
					if isLTR:
						# LTR cursive: exit connects to the right, entry connects from the left
						if isInit or isMedi:
							node = self.rightmostOncurve(layer)
							if node and (not layer.anchors[exitName] or overwrite):
								layer.anchors.append(GSAnchor(exitName, NSPoint(node.x, node.y)))
								count += 1
						if isMedi or isFina:
							node = self.leftmostOncurve(layer)
							if node and (not layer.anchors[entryName] or overwrite):
								layer.anchors.append(GSAnchor(entryName, NSPoint(node.x, node.y)))
								count += 1
					else:
						# RTL cursive (Arabic): exit connects to the left (x=0), entry from the right
						if isInit or isMedi:
							if not layer.anchors[exitName] or overwrite:
								layer.anchors.append(GSAnchor(exitName, NSPoint(0.0, 0.0)))
								count += 1
						if isMedi or isFina:
							node = self.rightmostOncurve(layer)
							if node and (not layer.anchors[entryName] or overwrite):
								layer.anchors.append(GSAnchor(entryName, NSPoint(node.x, node.y)))
								count += 1
		finally:
			font.enableUpdateInterface()
		msg = "Inserted %i anchor%s." % (count, "" if count == 1 else "s")
		if skipped:
			msg += " Skipped %i non-positional glyph%s." % (skipped, "" if skipped == 1 else "s")
		self.setStatus(msg)

	# ── Prefix operations ────────────────────────────────────────────────────────

	def addHashPrefix(self, sender=None):
		font = Glyphs.font
		if not font:
			return
		glyphs = self.getGlyphsToProcess()
		if not glyphs:
			self.setStatus("No glyphs to process.")
			return

		count = 0
		font.disableUpdateInterface()
		try:
			for glyph in glyphs:
				for layer in self.getLayersFromGlyph(glyph):
					for anchor in layer.anchors:
						if anchor.name in ("exit", "entry"):
							anchor.name = "#" + anchor.name
							count += 1
		finally:
			font.enableUpdateInterface()
		self.setStatus("Added # prefix to %i anchor%s." % (count, "" if count == 1 else "s"))

	def removeHashPrefix(self, sender=None):
		font = Glyphs.font
		if not font:
			return
		glyphs = self.getGlyphsToProcess()
		if not glyphs:
			self.setStatus("No glyphs to process.")
			return

		count = 0
		font.disableUpdateInterface()
		try:
			for glyph in glyphs:
				for layer in self.getLayersFromGlyph(glyph):
					for anchor in layer.anchors:
						if anchor.name in ("#exit", "#entry"):
							anchor.name = anchor.name[1:]
							count += 1
		finally:
			font.enableUpdateInterface()
		self.setStatus("Removed # prefix from %i anchor%s." % (count, "" if count == 1 else "s"))

	# ── Utility operations ───────────────────────────────────────────────────────

	def swapExitEntry(self, sender=None):
		font = Glyphs.font
		if not font:
			return
		glyphs = self.getGlyphsToProcess()
		if not glyphs:
			self.setStatus("No glyphs to process.")
			return

		count = 0
		font.disableUpdateInterface()
		try:
			for glyph in glyphs:
				for layer in self.getLayersFromGlyph(glyph):
					for prefix in ("", "#"):
						exitAnchor = layer.anchors["%sexit" % prefix]
						entryAnchor = layer.anchors["%sentry" % prefix]
						if exitAnchor and entryAnchor:
							exitPos = NSPoint(exitAnchor.position.x, exitAnchor.position.y)
							exitAnchor.position = NSPoint(entryAnchor.position.x, entryAnchor.position.y)
							entryAnchor.position = exitPos
							count += 2
						elif exitAnchor and not entryAnchor:
							exitAnchor.name = "%sentry" % prefix
							count += 1
						elif entryAnchor and not exitAnchor:
							entryAnchor.name = "%sexit" % prefix
							count += 1
		finally:
			font.enableUpdateInterface()
		self.setStatus("Swapped/renamed %i anchor%s." % (count, "" if count == 1 else "s"))

	def removeAnchors(self, sender=None):
		font = Glyphs.font
		if not font:
			return
		glyphs = self.getGlyphsToProcess()
		if not glyphs:
			self.setStatus("No glyphs to process.")
			return

		targetNames = {"exit", "entry", "#exit", "#entry"}
		count = 0
		font.disableUpdateInterface()
		try:
			for glyph in glyphs:
				for layer in self.getLayersFromGlyph(glyph):
					toRemove = [a for a in layer.anchors if a.name in targetNames]
					for anchor in toRemove:
						layer.anchors.remove(anchor)
						count += 1
		finally:
			font.enableUpdateInterface()
		self.setStatus("Removed %i anchor%s." % (count, "" if count == 1 else "s"))


ExitEntryManager()
