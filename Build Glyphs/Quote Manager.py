# MenuTitle: Quote Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Build and sync quotes: create single and double quotes with cursive attachment anchors, metrics keys, and kern groups.
"""

import vanilla
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSAnchor, GSComponent, GSGlyph, GSPath, GSNode, LINE, GSMetricsTypeCapHeight
from mekkablue import mekkaObject

# Maps single quote → double quote
SINGLE_TO_DOUBLE = {
	"quotesinglbase": "quotedblbase",
	"quoteleft": "quotedblleft",
	"quoteright": "quotedblright",
	"guilsinglleft": "guillemetleft",
	"guilsinglright": "guillemetright",
	"quotesingle": "quotedbl",
	"quotereversed": "quotedblrightreversed",
}

# Apostrophe composites: name → source single quote
APOSTROPHE_COMPOSITES = {
	"apostrophemod": "quoteright",
	"commareversedmod": "quotereversed",
	"commaturnedmod": "quoteleft",
}

DEFAULT_QUOTE_CHOICES = ["quotesinglbase", "quoteleft", "quoteright"]
DEFAULT_GUILLEMET_CHOICES = ["guilsinglleft", "guilsinglright"]

# (source, target) → (flipH, flipV)
QUOTE_BUILD_FLIP = {
	("quotesinglbase", "quoteright"): (False, False),
	("quotesinglbase", "quoteleft"): (True, True),   # base quotes are upside-down relative to raised quotes
	("quotesinglbase", "quotereversed"): (True, False),
	("quoteleft", "quoteright"): (True, False),
	("quoteleft", "quotesinglbase"): (False, False),
	("quoteleft", "quotereversed"): (False, False),
	("quoteright", "quoteleft"): (True, False),
	("quoteright", "quotesinglbase"): (False, False),
	("quoteright", "quotereversed"): (True, False),
	("guilsinglleft", "guilsinglright"): (True, False),
	("guilsinglright", "guilsinglleft"): (True, False),
}

BASE_QUOTES = {"quotesinglbase", "quotedblbase"}


class QuoteManager(mekkaObject):
	prefDict = {
		"doLeftGuillemets": 1,
		"doRightGuillemets": 1,
		"doDumbQuotes": 1,
		"doBaseQuotes": 1,
		"doLeftQuotes": 1,
		"doRightQuotes": 1,
		"doApostrophes": 1,
		"doReversedQuotes": 1,
		"useQuoteDefault": 1,
		"defaultQuote": 0,
		"useGuillemetsDefault": 1,
		"defaultGuillemet": 0,
		"preserveExisting": 1,
		"backupInBackground": 0,
		"openTab": 1,
		"reuseTab": 1,
	}

	def __init__(self):
		windowWidth = 360
		windowHeight = 320
		windowWidthResize = 100
		windowHeightResize = 0
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Quote Manager",
			minSize=(windowWidth - 30, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),
			autosaveName=self.domain("mainwindow"),
		)

		linePos, inset, lineHeight = 12, 15, 22
		col2 = inset + 165  # second column x offset

		self.w.titleText = vanilla.TextBox(
			(inset, linePos + 2, -inset, 14),
			"Create quotes with synced spacing and kern groups:",
			sizeStyle="small",
			selectable=True,
		)
		linePos += lineHeight

		# Row 1: Left guillemets | Left quotes
		self.w.doLeftGuillemets = vanilla.CheckBox(
			(inset, linePos, 165, 20), "Left guillemets", value=True, callback=self.SavePreferences, sizeStyle="small"
		)
		self.w.doLeftGuillemets.setToolTip("Create or update guilsinglleft, guillemetleft (‹ «)")
		self.w.doLeftQuotes = vanilla.CheckBox(
			(col2, linePos, -inset, 20), "Left quotes", value=True, callback=self.SavePreferences, sizeStyle="small"
		)
		self.w.doLeftQuotes.setToolTip("Create or update quoteleft, quotedblleft (\u2018 \u201c)")
		linePos += lineHeight

		# Row 2: Right guillemets | Right quotes
		self.w.doRightGuillemets = vanilla.CheckBox(
			(inset, linePos, 165, 20), "Right guillemets", value=True, callback=self.SavePreferences, sizeStyle="small"
		)
		self.w.doRightGuillemets.setToolTip("Create or update guilsinglright, guillemetright (› »)")
		self.w.doRightQuotes = vanilla.CheckBox(
			(col2, linePos, -inset, 20), "Right quotes", value=True, callback=self.SavePreferences, sizeStyle="small"
		)
		self.w.doRightQuotes.setToolTip("Create or update quoteright, quotedblright (\u2019 \u201d)")
		linePos += lineHeight

		# Row 3: Dumb quotes | Apostrophe
		self.w.doDumbQuotes = vanilla.CheckBox(
			(inset, linePos, 165, 20), "Dumb quotes", value=True, callback=self.SavePreferences, sizeStyle="small"
		)
		self.w.doDumbQuotes.setToolTip("Create or update quotesingle, quotedbl (' \")")
		self.w.doApostrophes = vanilla.CheckBox(
			(col2, linePos, -inset, 20), "Apostrophe", value=True, callback=self.SavePreferences, sizeStyle="small"
		)
		self.w.doApostrophes.setToolTip(
			"Create or update apostrophemod, commareversedmod, commaturnedmod (ʼ ʽ ʻ)"
		)
		linePos += lineHeight

		# Row 4: Base quotes | Reversed quotes
		self.w.doBaseQuotes = vanilla.CheckBox(
			(inset, linePos, 165, 20), "Base quotes", value=True, callback=self.SavePreferences, sizeStyle="small"
		)
		self.w.doBaseQuotes.setToolTip("Create or update quotesinglbase, quotedblbase (‚ „)")
		self.w.doReversedQuotes = vanilla.CheckBox(
			(col2, linePos, -inset, 20), "Reversed quotes", value=True, callback=self.SavePreferences, sizeStyle="small"
		)
		self.w.doReversedQuotes.setToolTip(
			"Create or update quotereversed, quotedblrightreversed (‛ ‟)"
		)
		linePos += lineHeight

		self.w.divider1 = vanilla.HorizontalLine((inset, linePos + 6, -inset, 1))
		linePos += lineHeight

		self.w.useQuoteDefault = vanilla.CheckBox(
			(inset, linePos, 140, 20), "Quotes based on", value=True, callback=self.SavePreferences, sizeStyle="small"
		)
		self.w.useQuoteDefault.setToolTip(
			"Use a specific single quote as the reference for metrics keys, anchor positions, and path building."
		)
		self.w.defaultQuote = vanilla.PopUpButton(
			(inset + 130, linePos + 1, -inset, 18),
			DEFAULT_QUOTE_CHOICES,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.defaultQuote.setToolTip(
			"The single quote all other quotes are derived from. Draw this glyph first, then click Build."
		)
		linePos += lineHeight

		self.w.useGuillemetsDefault = vanilla.CheckBox(
			(inset, linePos, 140, 20),
			"Guillemets based on",
			value=True,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.useGuillemetsDefault.setToolTip(
			"Use a specific guillemet as the reference for guillemet metrics keys, anchor positions, and path building."
		)
		self.w.defaultGuillemet = vanilla.PopUpButton(
			(inset + 130, linePos + 1, -inset, 18),
			DEFAULT_GUILLEMET_CHOICES,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.defaultGuillemet.setToolTip(
			"The single guillemet all other guillemets are derived from. The other guillemet will be a mirrored composite."
		)
		linePos += lineHeight

		self.w.preserveExisting = vanilla.CheckBox(
			(inset, linePos, -inset, 20),
			"Preserve existing quotes when building",
			value=True,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.preserveExisting.setToolTip(
			"When on, only empty layers are filled. When off, all quotes are rebuilt from scratch based on the default single quote/guillemet."
		)
		linePos += lineHeight

		self.w.backupInBackground = vanilla.CheckBox(
			(inset, linePos, -inset, 20),
			"Backup in background",
			value=False,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.backupInBackground.setToolTip("Decomposed copy of the current quotes")
		linePos += lineHeight

		self.w.openTab = vanilla.CheckBox(
			(inset, linePos, 120, 20), "Open tab", value=True, callback=self.SavePreferences, sizeStyle="small"
		)
		self.w.openTab.setToolTip("Open a tab showing all affected glyphs after the operation.")
		self.w.reuseTab = vanilla.CheckBox(
			(inset + 120, linePos, -inset, 20),
			"Reuse current tab",
			value=True,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.reuseTab.setToolTip("Replace the current tab's content instead of opening a new tab.")
		linePos += lineHeight

		self.w.editSinglesButton = vanilla.Button(
			(inset, -22 - inset, 100, -inset), "Edit Singles", callback=self.editSingles
		)
		self.w.editSinglesButton.setToolTip(
			"Open the default glyph(s) in a tab for editing. Creates them if they don't exist yet, and adds #entry/#exit anchors if missing."
		)
		self.w.updateButton = vanilla.Button(
			(-inset - 145, -22 - inset, 75, -inset), "Update", callback=self.update
		)
		self.w.updateButton.setToolTip(
			"Update metrics keys, anchors, and kern groups for all selected quote groups. Does not overwrite existing paths."
		)
		self.w.buildButton = vanilla.Button(
			(-inset - 65, -22 - inset, 65, -inset), "Build", callback=self.build
		)
		self.w.buildButton.setToolTip(
			"Build all selected quote glyphs: fills empty layers with mirrored paths, builds double quotes as composites, sets metrics keys, anchors, and kern groups."
		)
		self.w.setDefaultButton(self.w.buildButton)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.defaultQuote.enable(bool(self.w.useQuoteDefault.get()))
		self.w.defaultGuillemet.enable(bool(self.w.useGuillemetsDefault.get()))
		self.w.reuseTab.enable(bool(self.w.openTab.get()))

	# -----------------------------------------------------------------------
	# Helpers
	# -----------------------------------------------------------------------

	def getDefaultQuoteName(self):
		if self.prefBool("useQuoteDefault"):
			return DEFAULT_QUOTE_CHOICES[self.prefInt("defaultQuote")]
		return None

	def getDefaultGuillemetsName(self):
		if self.prefBool("useGuillemetsDefault"):
			return DEFAULT_GUILLEMET_CHOICES[self.prefInt("defaultGuillemet")]
		return None

	def getSelectedGroups(self):
		groups = set()
		if self.prefBool("doLeftGuillemets"):
			groups.add("leftGuillemets")
		if self.prefBool("doRightGuillemets"):
			groups.add("rightGuillemets")
		if self.prefBool("doDumbQuotes"):
			groups.add("dumbQuotes")
		if self.prefBool("doBaseQuotes"):
			groups.add("baseQuotes")
		if self.prefBool("doLeftQuotes"):
			groups.add("leftQuotes")
		if self.prefBool("doRightQuotes"):
			groups.add("rightQuotes")
		if self.prefBool("doApostrophes"):
			groups.add("apostrophes")
		if self.prefBool("doReversedQuotes"):
			groups.add("reversedQuotes")
		return groups

	def getSinglesForGroups(self, groups):
		"""Return list of single quote glyph names for the selected groups (no apostrophes, no doubles)."""
		singles = []
		if "leftGuillemets" in groups:
			singles.append("guilsinglleft")
		if "rightGuillemets" in groups:
			singles.append("guilsinglright")
		if "dumbQuotes" in groups:
			singles.append("quotesingle")
		if "baseQuotes" in groups:
			singles.append("quotesinglbase")
		if "leftQuotes" in groups:
			singles.append("quoteleft")
		if "rightQuotes" in groups:
			singles.append("quoteright")
		if "reversedQuotes" in groups:
			singles.append("quotereversed")
		return singles

	def getAllAffectedNames(self, groups):
		singles = self.getSinglesForGroups(groups)
		doubles = [SINGLE_TO_DOUBLE[s] for s in singles if s in SINGLE_TO_DOUBLE]
		apostrophes = list(APOSTROPHE_COMPOSITES.keys()) if "apostrophes" in groups else []
		return singles + doubles + apostrophes

	def openTabIfRequested(self, font, glyphNames):
		if not self.prefBool("openTab"):
			return
		tabString = "".join(f"/{n}" for n in glyphNames if font.glyphs[n])
		if not tabString:
			return
		if font.currentTab and self.prefBool("reuseTab"):
			font.currentTab.text = tabString
		else:
			font.newTab(tabString)

	def ensureGlyphExists(self, font, glyphName):
		if not font.glyphs[glyphName]:
			g = GSGlyph(glyphName)
			font.glyphs.append(g)
			print(f"\t➕ Created glyph: {glyphName}")
		return font.glyphs[glyphName]

	def backupLayer(self, layer):
		if self.prefBool("backupInBackground"):
			layer.swapForegroundWithBackground()
			layer.background.decomposeComponents()

	def setAnchors(self, layer, entryX=0, exitX=None):
		"""Place #entry at 0,0 and #exit at the same distance from 0 as exitX is from entryX."""
		if exitX is None:
			exitX = round(layer.width * 0.8)
		distance = exitX - entryX
		toRemove = [a for a in layer.anchors if a.name in ("#entry", "#exit")]
		for a in toRemove:
			layer.anchors.remove(a)
		layer.anchors.append(GSAnchor("#entry", NSPoint(0, 0)))
		layer.anchors.append(GSAnchor("#exit", NSPoint(distance, 0)))

	# -----------------------------------------------------------------------
	# Metrics keys
	# -----------------------------------------------------------------------

	def resetMetricsKeys(self, font, groups):
		"""Clear all glyph- and layer-level metrics keys on affected glyphs before setting new ones."""
		for name in self.getAllAffectedNames(groups):
			g = font.glyphs[name]
			if g:
				g.leftMetricsKey = None
				g.rightMetricsKey = None
				for layer in g.layers:
					layer.leftMetricsKey = None
					layer.rightMetricsKey = None

	def setMetricsKeys(self, font, groups, defaultQuote, defaultGuillemet):
		if defaultQuote:
			eq = f"={defaultQuote}"
			rev = f"=|{defaultQuote}"

			# For each quote, determine LSB/RSB relative to the default
			if defaultQuote == "quotesinglbase":
				metricsMap = {
					"quoteright": (eq, eq),
					"quoteleft": (rev, rev),
					"quotereversed": (rev, rev),
					"quotesingle": (eq, "=|"),
				}
			elif defaultQuote == "quoteleft":
				metricsMap = {
					"quotesinglbase": (rev, rev),
					"quoteright": (rev, rev),
					"quotereversed": (eq, eq),
					"quotesingle": (eq, "=|"),
				}
			else:  # quoteright
				metricsMap = {
					"quotesinglbase": (eq, eq),
					"quoteleft": (rev, rev),
					"quotereversed": (rev, rev),
					"quotesingle": (eq, "=|"),
				}

			groupFilter = {
				"quotesinglbase": "baseQuotes",
				"quoteleft": "leftQuotes",
				"quoteright": "rightQuotes",
				"quotereversed": "reversedQuotes",
				"quotesingle": "dumbQuotes",
			}

			for glyphName, (lsk, rsk) in metricsMap.items():
				if glyphName == defaultQuote:
					continue
				if groupFilter.get(glyphName) not in groups:
					continue
				g = font.glyphs[glyphName]
				if g:
					g.leftMetricsKey = lsk
					g.rightMetricsKey = rsk
					print(f"\t📐 Metrics keys for {glyphName}: LSB={lsk} RSB={rsk}")

		if defaultGuillemet:
			revG = f"=|{defaultGuillemet}"
			otherGuillemet = "guilsinglright" if defaultGuillemet == "guilsinglleft" else "guilsinglleft"
			otherGroup = "rightGuillemets" if otherGuillemet == "guilsinglright" else "leftGuillemets"
			if otherGroup in groups:
				g = font.glyphs[otherGuillemet]
				if g:
					g.leftMetricsKey = revG
					g.rightMetricsKey = revG
					print(f"\t📐 Metrics keys for {otherGuillemet}: LSB={revG} RSB={revG}")

	# -----------------------------------------------------------------------
	# Kern groups
	# -----------------------------------------------------------------------

	def setKernGroups(self, font, singles):
		for singleName in singles:
			g = font.glyphs[singleName]
			if g:
				g.leftKerningGroup = singleName
				g.rightKerningGroup = singleName
				print(f"\t🔗 Kern groups for {singleName}")

			doubleName = SINGLE_TO_DOUBLE.get(singleName)
			if doubleName:
				gg = font.glyphs[doubleName]
				if gg:
					gg.leftKerningGroup = singleName
					gg.rightKerningGroup = singleName
					print(f"\t🔗 Kern groups for {doubleName} → {singleName}")

		for apostropheName, sourceName in APOSTROPHE_COMPOSITES.items():
			g = font.glyphs[apostropheName]
			if g:
				g.leftKerningGroup = sourceName
				g.rightKerningGroup = sourceName
				print(f"\t🔗 Kern groups for {apostropheName} → {sourceName}")

	# -----------------------------------------------------------------------
	# Anchors
	# -----------------------------------------------------------------------

	def syncAnchorsFromDefault(self, font, singles, defaultQuote, defaultGuillemet):
		"""Copy #entry/#exit positions from the relevant default to each single."""
		for singleName in singles:
			isGuillemet = singleName in ("guilsinglleft", "guilsinglright")
			defaultName = defaultGuillemet if isGuillemet else defaultQuote
			if not defaultName or singleName == defaultName:
				continue
			# The non-default guillemet is a composite; anchors are inherited from the component
			if isGuillemet:
				continue

			defaultGlyph = font.glyphs[defaultName]
			targetGlyph = font.glyphs[singleName]
			if not defaultGlyph or not targetGlyph:
				continue

			for master in font.masters:
				mID = master.id
				defaultLayer = defaultGlyph.layers[mID]
				targetLayer = targetGlyph.layers[mID]
				entryAnchor = defaultLayer.anchors["#entry"]
				exitAnchor = defaultLayer.anchors["#exit"]

				if entryAnchor and exitAnchor:
					self.setAnchors(
						targetLayer,
						entryX=entryAnchor.position.x,
						exitX=exitAnchor.position.x,
					)
				else:
					self.setAnchors(targetLayer)
				print(f"\t⚓ Anchors synced: {singleName} / {master.name}")

	# -----------------------------------------------------------------------
	# Path building helpers
	# -----------------------------------------------------------------------

	def getCapHeightMetrics(self, font, master):
		"""Return (position, overshoot) for the cap height metric of the given master."""
		for metric in font.metrics:
			if metric.type == GSMetricsTypeCapHeight:
				metricValue = master.metrics[metric.id]
				return metricValue.position, metricValue.overshoot
		# Fallback: use master.capHeight if the metrics API is unavailable
		capH = master.capHeight if hasattr(master, "capHeight") else 700
		return capH, 0

	def _hasHorizontalTopEdge(self, layer):
		"""True if the top edge is a flat horizontal segment: exactly 2 consecutive LINE on-curves at maxY, no off-curves at maxY."""
		if not layer.paths:
			return False
		allNodes = [n for p in layer.paths for n in p.nodes]
		if not allNodes:
			return False
		maxY = max(n.position.y for n in allNodes)
		# Collect all nodes sitting at maxY across all paths
		topNodes = [(p, i, n) for p in layer.paths for i, n in enumerate(p.nodes) if n.position.y == maxY]
		# Must be exactly 2, both LINE type (not off-curve, not smooth curve)
		if len(topNodes) != 2:
			return False
		if any(n.type != LINE for _, _, n in topNodes):
			return False
		# Must be in the same path and consecutive (including wrap-around)
		p0, i0, _ = topNodes[0]
		p1, i1, _ = topNodes[1]
		if p0 is not p1:
			return False
		nodeCount = len(p0.nodes)
		return abs(i1 - i0) == 1 or {i0, i1} == {0, nodeCount - 1}

	def _repositionLayer(self, layer, isBase, capHeightPos, capHeightOvershoot):
		"""Move paths so they sit at the right vertical position."""
		bounds = layer.bounds
		if bounds.size.height == 0:
			return
		bboxY = bounds.origin.y
		bboxH = bounds.size.height

		if isBase:
			# Vertically center over baseline
			targetYMin = -bboxH / 2.0
		else:
			# Flat horizontal top edge: butt exactly against cap height, no overshoot
			if self._hasHorizontalTopEdge(layer):
				targetTop = capHeightPos
			else:
				targetTop = capHeightPos + 0.5 * capHeightOvershoot
			targetYMin = targetTop - bboxH

		dy = targetYMin - bboxY
		if dy != 0:
			layer.applyTransform((1, 0, 0, 1, 0, dy))

	def buildSingleFromDefault(self, font, singleName, defaultName, forceOverwrite=False):
		"""Copy and optionally H-mirror paths from defaultName to singleName; reposition vertically."""
		defaultGlyph = font.glyphs[defaultName]
		targetGlyph = font.glyphs[singleName]
		if not defaultGlyph or not targetGlyph:
			return

		flipH, flipV = QUOTE_BUILD_FLIP.get((defaultName, singleName), (False, False))
		isBase = singleName in BASE_QUOTES

		for master in font.masters:
			mID = master.id
			defaultLayer = defaultGlyph.layers[mID]
			targetLayer = targetGlyph.layers[mID]

			# Only fill empty layers (unless forced)
			if not forceOverwrite and (targetLayer.paths or targetLayer.components):
				continue

			if not defaultLayer.paths:
				print(f"\t⚠️ No paths in default {defaultName} / {master.name} — skipping {singleName}")
				continue

			capHeightPos, capHeightOvershoot = self.getCapHeightMetrics(font, master)

			self.backupLayer(targetLayer)
			targetLayer.clear()

			# Copy paths
			for path in defaultLayer.paths:
				newPath = path.copy()
				try:
					targetLayer.shapes.append(newPath)
				except Exception:
					targetLayer.paths.append(newPath)

			# H-mirror around bbox center X
			if flipH:
				bounds = targetLayer.bounds
				centerX = bounds.origin.x + bounds.size.width / 2.0
				targetLayer.applyTransform((-1, 0, 0, 1, 2 * centerX, 0))

			# V-mirror around bbox center Y
			if flipV:
				bounds = targetLayer.bounds
				centerY = bounds.origin.y + bounds.size.height / 2.0
				targetLayer.applyTransform((1, 0, 0, -1, 0, 2 * centerY))

			# Reposition vertically
			self._repositionLayer(targetLayer, isBase, capHeightPos, capHeightOvershoot)

			# Sync width
			targetLayer.width = defaultLayer.width

			flips = [label for flag, label in ((flipH, "H-mirrored"), (flipV, "V-mirrored")) if flag]
			suffix = f", {', '.join(flips)}" if flips else ""
			print(f"\t✏️ Paths built for {singleName} / {master.name} (from {defaultName}{suffix})")

	def buildDumbQuote(self, font, forceOverwrite=False):
		"""Build quotesingle as a trapezoid from the default single quote."""
		defaultQuote = self.getDefaultQuoteName()
		if not defaultQuote:
			return

		defaultGlyph = font.glyphs[defaultQuote]
		targetGlyph = font.glyphs["quotesingle"]
		if not defaultGlyph or not targetGlyph:
			return

		for master in font.masters:
			mID = master.id
			defaultLayer = defaultGlyph.layers[mID]
			targetLayer = targetGlyph.layers[mID]

			if not forceOverwrite and (targetLayer.paths or targetLayer.components):
				continue

			bounds = defaultLayer.bounds
			if bounds.size.height == 0:
				print(f"\t⚠️ Default {defaultQuote} is empty in {master.name} — skipping quotesingle")
				continue

			capHeightPos, _overshoot = self.getCapHeightMetrics(font, master)
			bboxW = bounds.size.width
			bboxH = bounds.size.height
			bboxX = bounds.origin.x

			topW = bboxW * 1.12
			bottomW = bboxW * 0.6
			centerX = bboxX + bboxW / 2.0

			# Butted against cap height: top at capHeightPos, no overshoot
			topY = capHeightPos
			bottomY = topY - bboxH

			self.backupLayer(targetLayer)
			targetLayer.clear()

			newPath = GSPath()
			for pt in (
				NSPoint(centerX - topW / 2.0, topY),
				NSPoint(centerX + topW / 2.0, topY),
				NSPoint(centerX + bottomW / 2.0, bottomY),
				NSPoint(centerX - bottomW / 2.0, bottomY),
			):
				node = GSNode(pt, type=LINE)
				newPath.nodes.append(node)
			newPath.closed = True

			try:
				targetLayer.shapes.append(newPath)
			except Exception:
				targetLayer.paths.append(newPath)

			targetLayer.width = defaultLayer.width
			print(f"\t✏️ Trapezoid built for quotesingle / {master.name}")

	def buildApostropheComposites(self, font, forceOverwrite=False):
		"""Build apostrophemod, commareversedmod, commaturnedmod as single composites."""
		for apostropheName, sourceName in APOSTROPHE_COMPOSITES.items():
			sourceGlyph = font.glyphs[sourceName]
			if not sourceGlyph:
				print(f"\t⚠️ Source {sourceName} not in font — skipping {apostropheName}")
				continue

			g = self.ensureGlyphExists(font, apostropheName)

			for master in font.masters:
				mID = master.id
				layer = g.layers[mID]
				sourceLayer = sourceGlyph.layers[mID]

				if not sourceLayer.paths and not sourceLayer.components:
					continue

				if not forceOverwrite and (layer.paths or layer.components):
					continue

				self.backupLayer(layer)
				layer.clear()

				comp = GSComponent(sourceName)
				comp.automaticAlignment = True
				try:
					layer.shapes.append(comp)
				except Exception:
					layer.components.append(comp)

				print(f"\t🔤 {apostropheName} ← composite of {sourceName} / {master.name}")

	def buildOtherGuillemet(self, font, defaultGuillemet, forceOverwrite=False):
		"""Build the non-default guillemet as an H-mirrored composite of the default."""
		otherGuillemet = "guilsinglright" if defaultGuillemet == "guilsinglleft" else "guilsinglleft"

		if not font.glyphs[defaultGuillemet]:
			print(f"\t⚠️ Default guillemet {defaultGuillemet} not in font")
			return

		g = self.ensureGlyphExists(font, otherGuillemet)

		for master in font.masters:
			mID = master.id
			layer = g.layers[mID]

			if not forceOverwrite and (layer.paths or layer.components):
				continue

			defaultLayer = font.glyphs[defaultGuillemet].layers[mID]
			self.backupLayer(layer)
			layer.clear()

			comp = GSComponent(defaultGuillemet)
			comp.automaticAlignment = True
			# Horizontal mirror (-100% scale on x); auto-alignment manages the translation
			comp.transform = (-1, 0, 0, 1, defaultLayer.width, 0)
			try:
				layer.shapes.append(comp)
			except Exception:
				layer.components.append(comp)

			layer.width = defaultLayer.width
			print(f"\t🔤 {otherGuillemet} ← mirrored composite of {defaultGuillemet} / {master.name}")

	def buildDoubleQuotes(self, font, singles, forceOverwrite=False):
		"""Build double quotes from two auto-aligned single quote components."""
		for singleName in singles:
			doubleName = SINGLE_TO_DOUBLE.get(singleName)
			if not doubleName:
				continue

			singleGlyph = font.glyphs[singleName]
			if not singleGlyph:
				print(f"\t⚠️ {singleName} not in font — skipping {doubleName}")
				continue

			gg = self.ensureGlyphExists(font, doubleName)

			for master in font.masters:
				mID = master.id
				ggl = gg.layers[mID]
				singleLayer = singleGlyph.layers[mID]

				if not singleLayer.paths and not singleLayer.components:
					continue

				if not forceOverwrite and (ggl.paths or ggl.components):
					continue

				self.backupLayer(ggl)
				ggl.clear()

				for _ in range(2):
					comp = GSComponent(singleName)
					comp.automaticAlignment = True
					try:
						ggl.shapes.append(comp)
					except Exception:
						ggl.components.append(comp)

				print(f"\t🔤 {doubleName} ← 2× {singleName} / {master.name}")

	def ensureAutoAlignedComponents(self, font, glyphNames):
		"""Set automaticAlignment=True on every component in the given glyphs (double quotes, apostrophes)."""
		for name in glyphNames:
			g = font.glyphs[name]
			if not g:
				continue
			for layer in g.layers:
				for c in layer.components:
					c.automaticAlignment = True

	# -----------------------------------------------------------------------
	# Validate default quote
	# -----------------------------------------------------------------------

	def validateDefault(self, font, defaultName):
		"""Return True if default quote exists, is not empty, and has anchors in all masters."""
		g = font.glyphs[defaultName]
		if not g:
			print(f"❌ Default quote '{defaultName}' not in font. Click 'Edit Defaults' to create it first.")
			return False
		ok = True
		for master in font.masters:
			layer = g.layers[master.id]
			if not layer.paths and not layer.components:
				print(f"⚠️ '{defaultName}' is empty in master '{master.name}'. Draw it first, then click Build.")
				ok = False
			elif not layer.anchors["#entry"] or not layer.anchors["#exit"]:
				self.setAnchors(layer)
				print(f"\t⚓ Auto-added anchors to '{defaultName}' / {master.name}")
		return ok

	# -----------------------------------------------------------------------
	# Edit Defaults
	# -----------------------------------------------------------------------

	def editSingles(self, sender):
		try:
			self.SavePreferences()
			font = Glyphs.font
			if not font:
				return
			Glyphs.clearLog()
			print("Quote Manager — Edit Singles\n")
			print(f"Font: {font.familyName}\n")

			glyphsToOpen = []

			for defaultName in filter(None, [self.getDefaultQuoteName(), self.getDefaultGuillemetsName()]):
				g = self.ensureGlyphExists(font, defaultName)
				glyphsToOpen.append(defaultName)
				for master in font.masters:
					layer = g.layers[master.id]
					if not layer.anchors["#entry"] or not layer.anchors["#exit"]:
						self.setAnchors(layer)
						print(f"\t⚓ Added anchors to {defaultName} / {master.name}")

			self.openTabIfRequested(font, glyphsToOpen)
			print("\nDone.")
		except Exception as e:
			Glyphs.showMacroWindow()
			print(f"Quote Manager Error: {e}")
			import traceback
			print(traceback.format_exc())

	# -----------------------------------------------------------------------
	# Update
	# -----------------------------------------------------------------------

	def update(self, sender):
		"""Update metrics keys, kern groups, and anchors. Does NOT overwrite existing paths."""
		try:
			self.SavePreferences()
			Glyphs.clearLog()
			font = Glyphs.font
			if not font:
				return
			print("Quote Manager — Update\n")
			print(f"Font: {font.familyName}\n")

			groups = self.getSelectedGroups()
			singles = self.getSinglesForGroups(groups)
			defaultQuote = self.getDefaultQuoteName()
			defaultGuillemet = self.getDefaultGuillemetsName()

			self.resetMetricsKeys(font, groups)
			self.setMetricsKeys(font, groups, defaultQuote, defaultGuillemet)
			self.syncAnchorsFromDefault(font, singles, defaultQuote, defaultGuillemet)
			self.setKernGroups(font, singles)

			mirrorGuillemet = (
				["guilsinglright" if defaultGuillemet == "guilsinglleft" else "guilsinglleft"]
				if defaultGuillemet and ("leftGuillemets" in groups or "rightGuillemets" in groups)
				else []
			)
			compositeGlyphs = (
				[SINGLE_TO_DOUBLE[s] for s in singles if s in SINGLE_TO_DOUBLE]
				+ (list(APOSTROPHE_COMPOSITES.keys()) if "apostrophes" in groups else [])
				+ mirrorGuillemet
			)
			self.ensureAutoAlignedComponents(font, compositeGlyphs)

			for name in self.getAllAffectedNames(groups):
				g = font.glyphs[name]
				if g:
					for layer in g.layers:
						layer.updateMetrics()
						layer.syncMetrics()

			self.openTabIfRequested(font, self.getAllAffectedNames(groups))
			print("\nDone.")
			Glyphs.showNotification("Quote Manager", "Updated metrics keys, anchors, and kern groups.")
		except Exception as e:
			Glyphs.showMacroWindow()
			print(f"Quote Manager Error: {e}")
			import traceback
			print(traceback.format_exc())

	# -----------------------------------------------------------------------
	# Build
	# -----------------------------------------------------------------------

	def build(self, sender):
		"""Full build: create glyphs, build paths (if empty), set metrics/anchors/groups, build doubles."""
		try:
			self.SavePreferences()
			Glyphs.clearLog()
			font = Glyphs.font
			if not font:
				return
			print("Quote Manager — Build\n")
			print(f"Font: {font.familyName}\n")

			groups = self.getSelectedGroups()
			defaultQuote = self.getDefaultQuoteName()
			defaultGuillemet = self.getDefaultGuillemetsName()

			# 1. Validate defaults
			if defaultQuote and not self.validateDefault(font, defaultQuote):
				Glyphs.showNotification("Quote Manager", "Default quote has issues — see Macro Window.")
				Glyphs.showMacroWindow()
				return

			singles = self.getSinglesForGroups(groups)
			forceOverwrite = not self.prefBool("preserveExisting")

			# 2. Ensure all single and double glyphs exist
			for singleName in singles:
				self.ensureGlyphExists(font, singleName)
				doubleName = SINGLE_TO_DOUBLE.get(singleName)
				if doubleName:
					self.ensureGlyphExists(font, doubleName)
			if "apostrophes" in groups:
				for name in APOSTROPHE_COMPOSITES:
					self.ensureGlyphExists(font, name)

			# 3. Build guillemet mirror composite
			if defaultGuillemet and ("leftGuillemets" in groups or "rightGuillemets" in groups):
				print("Building guillemet mirror composite:")
				self.buildOtherGuillemet(font, defaultGuillemet, forceOverwrite=forceOverwrite)

			# 4. Build single quote paths
			if defaultQuote:
				print(f"\nBuilding single quote paths ({'overwriting existing' if forceOverwrite else 'empty layers only'}):")
				for singleName in singles:
					if singleName in ("guilsinglleft", "guilsinglright"):
						continue  # handled above
					if singleName == defaultQuote:
						continue
					if singleName == "quotesingle" and "dumbQuotes" in groups:
						self.buildDumbQuote(font, forceOverwrite=forceOverwrite)
					else:
						self.buildSingleFromDefault(font, singleName, defaultQuote, forceOverwrite=forceOverwrite)

			# 5. Apostrophe composites (always overwrite if source is not empty)
			if "apostrophes" in groups:
				print("\nBuilding apostrophe composites:")
				self.buildApostropheComposites(font, forceOverwrite=True)

			# 6. Metrics keys
			print("\nResetting and setting metrics keys:")
			self.resetMetricsKeys(font, groups)
			self.setMetricsKeys(font, groups, defaultQuote, defaultGuillemet)

			# 7. Sync anchors from default
			print("\nSyncing anchors:")
			self.syncAnchorsFromDefault(font, singles, defaultQuote, defaultGuillemet)
			# Also set anchors on the default itself if missing
			if defaultQuote:
				g = font.glyphs[defaultQuote]
				if g:
					for master in font.masters:
						layer = g.layers[master.id]
						if not layer.anchors["#entry"] or not layer.anchors["#exit"]:
							self.setAnchors(layer)
							print(f"\t⚓ Added anchors to {defaultQuote} / {master.name}")

			# 8. Build double quotes (always overwrite if single is not empty)
			print("\nBuilding double quotes:")
			self.buildDoubleQuotes(font, singles, forceOverwrite=True)

			# 9. Kern groups
			print("\nSetting kern groups:")
			self.setKernGroups(font, singles)

			# 10. Ensure all composite components (double quotes, apostrophes) are auto-aligned
			mirrorGuillemet = (
				["guilsinglright" if defaultGuillemet == "guilsinglleft" else "guilsinglleft"]
				if defaultGuillemet and ("leftGuillemets" in groups or "rightGuillemets" in groups)
				else []
			)
			compositeGlyphs = (
				[SINGLE_TO_DOUBLE[s] for s in singles if s in SINGLE_TO_DOUBLE]
				+ (list(APOSTROPHE_COMPOSITES.keys()) if "apostrophes" in groups else [])
				+ mirrorGuillemet
			)
			self.ensureAutoAlignedComponents(font, compositeGlyphs)

			# 11. Refresh metrics
			for name in self.getAllAffectedNames(groups):
				g = font.glyphs[name]
				if g:
					for layer in g.layers:
						layer.updateMetrics()
						layer.syncMetrics()

			self.openTabIfRequested(font, self.getAllAffectedNames(groups))
			print("\nDone.")
			Glyphs.showNotification("Quote Manager", "Build complete. Details in Macro Window.")
		except Exception as e:
			Glyphs.showMacroWindow()
			print(f"Quote Manager Error: {e}")
			import traceback
			print(traceback.format_exc())


QuoteManager()
