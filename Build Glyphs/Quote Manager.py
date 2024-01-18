# MenuTitle: Quote Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Build double quotes from single quotes, and insert #exit and #entry anchors in the single quotes for auto-alignment.
"""

import vanilla
from Foundation import NSPoint
from AppKit import NSNotificationCenter
from GlyphsApp import Glyphs, GSAnchor, GSComponent
from mekkaCore import mekkaObject

names = {
	"quotesinglbase": "quotedblbase",
	"quoteleft": "quotedblleft",
	"quoteright": "quotedblright",
	"quotesingle": "quotedbl",
}


class QuoteManager(mekkaObject):
	prefDict = {
		"defaultQuote": 0,
		"syncWithDefaultQuote": 0,
		"suffix": "",
		"excludeDumbQuotes": 0,
		"openTabWithAffectedGlyphs": 0,
		"reuseTab": 1,
		"keepCopyInBackground": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 480
		windowHeight = 295
		windowWidthResize = 400  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Quote Manager: build and align quotes",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 24

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Syncs single and double quotes with cursive attachment. Reports in Macro Window.", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.defaultQuoteText = vanilla.TextBox((inset, linePos + 2, 90, 14), "Default quotes:", sizeStyle='small', selectable=True)
		self.w.defaultQuote = vanilla.PopUpButton((inset + 90, linePos, -inset, 17), ["%s/%s" % (name, names[name]) for name in names], sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.syncWithDefaultQuote = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Sync all quotes with default quotes (metrics keys, anchor placement)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.syncWithDefaultQuote.getNSButton().setToolTip_("If enabled, the default quotes will be taken as reference for metrics keys and distance between #exit and #entry anchors.")
		linePos += lineHeight

		self.w.excludeDumbQuotes = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Ignore straight dumb quotes (quotesingle, quotedbl)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.excludeDumbQuotes.getNSButton().setToolTip_("For most actions, tthis option allows you to ignore the (straight) dumb quotes. The Kerning Group button will ignore this setting and always set the groups for the straight quote.")
		linePos += lineHeight

		self.w.suffixText = vanilla.TextBox((inset, linePos + 2, 270, 14), "Suffix for all quotes involved (leave blank if none):", sizeStyle='small', selectable=True)
		self.w.suffix = vanilla.EditText((inset + 270, linePos - 1, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.suffix.getNSTextField().setToolTip_(u"E.g., ‘case’ for .case variants. Entry with or without the leading period. Leave blank for the default quotes (without dot suffixes).")
		linePos += lineHeight

		self.w.openTabWithAffectedGlyphs = vanilla.CheckBox((inset, linePos - 1, 200, 20), "Open tab with affected glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.openTabWithAffectedGlyphs.getNSButton().setToolTip_("Whatever action you take, this option makes sure a new tab will be opened with all the glyphs affected.")
		self.w.reuseTab = vanilla.CheckBox((inset + 200, linePos - 1, -inset, 20), u"Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.getNSButton().setToolTip_(u"Instead of opening a new tab, will reuse the current tab. Highly recommended.")
		linePos += lineHeight

		self.w.buildDoublesButton = vanilla.Button((inset, linePos, 130, 18), "Add Components", sizeStyle='small', callback=self.buildDoublesMain)
		self.w.buildDoublesText = vanilla.TextBox((inset + 135, linePos + 2, -inset, 14), "Insert single quotes as components in double quotes", sizeStyle='small', selectable=True)
		tooltip = "Do this first. Then adjust the position of the second component in the default double quote. Inserting anchors (the next button) will take the distance between the components into account. Or follow the instructions in the tooltip of the next button. Then press the Insert Anchors button."
		self.w.buildDoublesButton.getNSButton().setToolTip_(tooltip)
		self.w.buildDoublesText.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.keepCopyInBackground = vanilla.CheckBox((inset + 135, linePos - 1, -inset, 20), "Backup current quotes in the background", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.keepCopyInBackground.getNSButton().setToolTip_("Copies the current shapes in the background and decomposes them to paths there. Useful to see if anything shifted.")
		linePos += lineHeight

		self.w.insertAnchorsButton = vanilla.Button((inset, linePos, 130, 18), "Insert Anchors", sizeStyle='small', callback=self.insertAnchorsMain)
		self.w.insertAnchorsText = vanilla.TextBox((inset + 135, linePos + 2, -inset, 14), "Insert #exit and #entry anchors in single quotes", sizeStyle='small', selectable=True)
		tooltip = "Hint: After you have done the previous steps, FIRST press button to insert the anchors, THEN adjust the width between the anchors in your default quote, THEN press this button again to sync all other #exit and #entry anchors with the default quotes."
		self.w.insertAnchorsButton.getNSButton().setToolTip_(tooltip)
		self.w.insertAnchorsText.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.metricKeyButton = vanilla.Button((inset, linePos, 130, 18), "Add Keys", sizeStyle='small', callback=self.metricKeyMain)
		self.w.metricKeyText = vanilla.TextBox((inset + 135, linePos + 2, -inset, 14), "Apply metrics keys to single quotes", sizeStyle='small', selectable=True)
		tooltip = "Adds Metrics Keys to single quotes, so your quotes are all in sync and have the same width. Double quotes should use automatic alignment by now."
		self.w.metricKeyButton.getNSButton().setToolTip_(tooltip)
		self.w.metricKeyText.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.kernGroupButton = vanilla.Button((inset, linePos, 130, 18), "Set Groups", sizeStyle='small', callback=self.kernGroupMain)
		self.w.kernGroupText = vanilla.TextBox((inset + 135, linePos + 2, -inset, 14), "Set kern groups (based on singles)", sizeStyle='small', selectable=True)
		tooltip = "Sync kern groups between double and single quotes."
		self.w.kernGroupButton.getNSButton().setToolTip_(tooltip)
		self.w.kernGroupText.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Build and align quotes' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.reuseTab.enable(self.w.openTabWithAffectedGlyphs.get())

	def getDotSuffix(self):
		dotSuffix = self.pref("suffix").strip().lstrip(".")

		# clean up:
		if dotSuffix:
			dotSuffix = ".%s" % dotSuffix

		return dotSuffix

	def openTabIfRequested(self):
		if self.pref("openTabWithAffectedGlyphs"):
			Font = Glyphs.font
			suffix = self.getDotSuffix()
			tabString = ""
			for name in names:
				for singleOrDoubleName in (name, names[name]):
					suffixedName = singleOrDoubleName + suffix
					if Font.glyphs[suffixedName]:
						tabString += "/%s" % suffixedName
			if tabString:
				if Font.currentTab and self.pref("reuseTab"):
					Font.currentTab.text = tabString
				else:
					Font.newTab(tabString)
			else:
				print(u"⚠️ WARNING: None of the required glyphs in the font. No new tab opened.")

	def reportFont(self):
		Font = Glyphs.font
		print("Font: %s" % Font.familyName)
		print("Path: %s\n" % Font.filepath)

	def reportMissingGlyph(self, glyphName):
		print(u"⚠️ WARNING: %s not in font. Skipping." % glyphName)

	def reportMetricKeys(self, glyphName):
		print(u"✅ Updated Metrics Keys for: %s" % glyphName)

	def defaultQuotes(self, dotSuffix=""):
		if self.pref("syncWithDefaultQuote"):
			defaultSingle = self.w.defaultQuote.getItem()
			defaultSingle = defaultSingle[:defaultSingle.find("/")]
			defaultDouble = names[defaultSingle]

			if dotSuffix:
				defaultSingle += dotSuffix
				defaultDouble += dotSuffix

			print("\nReference quotes: %s/%s" % (defaultSingle, defaultDouble))
		else:
			defaultSingle = None
			defaultDouble = None

		return defaultSingle, defaultDouble

	def kernGroupMain(self, sender):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences(self):
				print("Note: 'Quote Manager' could not write preferences.")

			Glyphs.clearLog()
			Font = Glyphs.font  # frontmost font
			dotSuffix = self.getDotSuffix()

			# report:
			self.reportFont()

			for keyGlyphName in names:
				singleQuoteName = "%s%s" % (keyGlyphName, dotSuffix)
				singleQuote = Font.glyphs[singleQuoteName]
				doubleQuoteName = "%s%s" % (names[keyGlyphName], dotSuffix)
				doubleQuote = Font.glyphs[doubleQuoteName]

				print("\nSetting kern groups for: %s, %s" % (singleQuoteName, doubleQuoteName))

				if not singleQuote:
					self.reportMissingGlyph(singleQuoteName)
				elif not doubleQuote:
					self.reportMissingGlyph(doubleQuoteName)
				else:
					for glyph in (singleQuote, doubleQuote):
						glyph.leftKerningGroup = singleQuoteName
						glyph.rightKerningGroup = singleQuoteName
					print(u"✅ Successfully set kerning groups to: '%s'" % singleQuoteName)

			self.openTabIfRequested()
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Quote Manager Error: %s" % e)
			import traceback
			print(traceback.format_exc())

	def insertAnchorsMain(self, sender):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences(self):
				print("Note: 'Quote Manager' could not write preferences.")

			Glyphs.clearLog()
			Font = Glyphs.font  # frontmost font

			# query suffix
			dotSuffix = self.getDotSuffix()

			# report:
			self.reportFont()
			print("Inserting cursive attachment anchors in single quotes, and auto-aligning double quotes%s." % (" with suffix '%s'" % dotSuffix if dotSuffix else ""))

			defaultSingle, defaultDouble = self.defaultQuotes(dotSuffix)

			if defaultSingle and not Font.glyphs[defaultSingle]:
				self.reportMissingGlyph(defaultSingle)
			elif defaultDouble and not Font.glyphs[defaultDouble]:
				self.reportMissingGlyph(defaultDouble)
			else:
				for singleName in names:
					doubleName = names[singleName]
					if dotSuffix:
						doubleName += dotSuffix
						singleName += dotSuffix

					if singleName == "quotesingle" and self.pref("excludeDumbQuotes"):
						print(u"\n⚠️ Skipping %s/%s" % (singleName, doubleName))
					else:
						print("\n%s/%s:" % (singleName, doubleName))

						g = Font.glyphs[singleName]  # single quote glyph
						gg = Font.glyphs[doubleName]  # double quote glyph

						if not g:
							self.reportMissingGlyph(singleName)
						elif not gg:
							self.reportMissingGlyph(doubleName)
						else:
							for master in Font.masters:
								mID = master.id
								gl = g.layers[mID]  # single quote layer
								ggl = gg.layers[mID]  # double quote layer

								# check if a default quote has been determined by the user:
								if defaultSingle:
									referenceGlyph = Font.glyphs[defaultDouble]
									referenceLayer = referenceGlyph.layers[mID]
								else:
									referenceGlyph = gg
									referenceLayer = ggl  # layer for measuring, depends on user input

								# measure referenceLayer:
								xPos = [c.position.x for c in referenceLayer.components]
								if xPos and len(xPos) == 2:

									# add anchors in single quote:
									print(xPos[1] - xPos[0], master.name)
									dist = abs(xPos[1] - xPos[0])
									for aName in ("entry", "exit"):
										if aName == "exit":
											x = dist
										else:
											x = 0
										newAnchor = GSAnchor("#%s" % aName, NSPoint(x, 0))
										gl.anchors.append(newAnchor)
									print(u"    ✅ %s: Added #exit and #entry anchors." % g.name)

									# auto align components
									for comp in ggl.components:
										comp.automaticAlignment = True

									# update metrics:
									ggl.updateMetrics()
									ggl.syncMetrics()

									print(u"    ✅ %s: Auto-aligned components." % gg.name)
								else:
									print(u"    ⚠️ WARNING: No components in %s, layer '%s'. Cannot add anchors." % (referenceLayer.parent.name, referenceLayer.name))

			self.openTabIfRequested()
			self.updateFontTab(Font)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Quote Manager Error: %s" % e)
			import traceback
			print(traceback.format_exc())

	def updateFontTab(self, Font):
		if Font.currentTab:
			if Glyphs.versionNumber >= 3:
				NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", Font.currentTab)
			Font.currentTab.redraw()

	def metricKeyMain(self, sender):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences(self):
				print("Note: 'Quote Manager' could not write preferences.")

			# brings macro window to front and clears its log:
			Glyphs.clearLog()

			Font = Glyphs.font  # frontmost font

			# query suffix
			dotSuffix = self.getDotSuffix()

			# report:
			self.reportFont()
			print("Inserting metric keys in single quotes%s." % (" with suffix '%s'" % dotSuffix if dotSuffix else ""))

			quotesinglbaseName = "quotesinglbase" + dotSuffix
			quotesinglbase = Font.glyphs[quotesinglbaseName]
			quoteleftName = "quoteleft" + dotSuffix
			quoteleft = Font.glyphs[quoteleftName]
			quoterightName = "quoteright" + dotSuffix
			quoteright = Font.glyphs[quoterightName]
			quotesingleName = "quotesingle" + dotSuffix
			quotesingle = Font.glyphs[quotesingleName]

			defaultSingle, defaultDouble = self.defaultQuotes(dotSuffix)
			equals = "=%s" % defaultSingle
			reverse = "=|%s" % defaultSingle

			if quotesingle:
				if defaultSingle == quotesingleName:
					# dumb quote, all the same:
					quotesinglbase.leftMetricsKey = equals
					quotesinglbase.rightMetricsKey = equals
					quoteleft.leftMetricsKey = equals
					quoteleft.rightMetricsKey = equals
					quoteright.leftMetricsKey = equals
					quoteright.rightMetricsKey = equals
					print(u"✅ Updated Metrics Keys for: %s, %s, %s" % (quotesinglbaseName, quoteleftName, quoterightName))
				elif not self.pref("excludeDumbQuotes"):
					# set dumb quote metric keys:
					quotesingle.leftMetricsKey = equals
					quotesingle.rightMetricsKey = "=|"
					print(u"✅ Updated Metrics Keys for: %s" % (quotesingleName))
				else:
					print(u"\n⚠️ Skipping %s" % (quotesingleName))
			else:
				self.reportMissingGlyph(quotesingleName)

			if quotesinglbase and defaultSingle == quotesinglbaseName:
				if quoteleft:
					quoteleft.leftMetricsKey = reverse
					quoteleft.rightMetricsKey = reverse
					self.reportMetricKeys(quoteleftName)
				else:
					self.reportMissingGlyph(quoteleftName)

				if quoteright:
					quoteright.leftMetricsKey = equals
					quoteright.rightMetricsKey = equals
					self.reportMetricKeys(quoterightName)
				else:
					self.reportMissingGlyph(quoterightName)

			if quoteleft and defaultSingle == quoteleftName:
				if quotesinglbase:
					quotesinglbase.leftMetricsKey = reverse
					quotesinglbase.rightMetricsKey = reverse
					self.reportMetricKeys(quotesinglbaseName)
				else:
					self.reportMissingGlyph(quotesinglbaseName)

				if quoteright:
					quoteright.leftMetricsKey = reverse
					quoteright.rightMetricsKey = reverse
					self.reportMetricKeys(quoterightName)
				else:
					self.reportMissingGlyph(quoterightName)

			if quoteright and defaultSingle == quoterightName:
				if quotesinglbase:
					quotesinglbase.leftMetricsKey = equals
					quotesinglbase.rightMetricsKey = equals
					self.reportMetricKeys(quotesinglbaseName)
				else:
					self.reportMissingGlyph(quotesinglbaseName)

				if quoteleft:
					quoteleft.leftMetricsKey = reverse
					quoteleft.rightMetricsKey = reverse
					self.reportMetricKeys(quoteleftName)
				else:
					self.reportMissingGlyph(quoteleftName)

			# update metrics:
			for thisGlyph in (quotesinglbase, quoteleft, quoteright, quotesingle):
				if thisGlyph:
					for thisLayer in thisGlyph.layers:
						thisLayer.updateMetrics()
						thisLayer.syncMetrics()

			self.openTabIfRequested()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Quote Manager Error: %s" % e)
			import traceback
			print(traceback.format_exc())

	def buildDoublesMain(self, sender):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences(self):
				print("Note: 'Quote Manager' could not write preferences.")

			# brings macro window to front and clears its log:
			Glyphs.clearLog()

			Font = Glyphs.font  # frontmost font

			# query suffix
			dotSuffix = self.getDotSuffix()
			keepCopyInBackground = self.pref("keepCopyInBackground")

			# report:
			self.reportFont()
			print("Inserting single quote components in double quotes%s." % (" with suffix '%s'" % dotSuffix if dotSuffix else ""))

			for singleName in names:
				doubleName = names[singleName]
				if dotSuffix:
					doubleName += dotSuffix
					singleName += dotSuffix

				if singleName == "quotesingle" and self.pref("excludeDumbQuotes"):
					print(u"\n⚠️ Skipping %s/%s" % (singleName, doubleName))
				else:
					print("\n%s/%s:" % (singleName, doubleName))

					if not Font.glyphs[singleName]:
						self.reportMissingGlyph(singleName)
					elif not Font.glyphs[doubleName]:
						self.reportMissingGlyph(doubleName)
					else:
						g = Font.glyphs[singleName]  # single quote glyph
						gg = Font.glyphs[doubleName]  # double quote glyph
						for master in Font.masters:
							mID = master.id
							gl = g.layers[mID]  # single quote layer
							ggl = gg.layers[mID]  # double quote layer

							# backup and clear layer:
							if keepCopyInBackground:
								ggl.swapForegroundWithBackground()
								ggl.background.decomposeComponents()
							ggl.clear()

							# add components:
							for i in range(2):
								newComponent = GSComponent(singleName)
								try:
									ggl.shapes.append(newComponent)
								except:
									ggl.components.append(newComponent)
								newComponent.automaticAlignment = True

							print(u"✅ %s: Added 2 %s components." % (doubleName, singleName))

			self.openTabIfRequested()
			self.updateFontTab(Font)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Quote Manager Error: %s" % e)
			import traceback
			print(traceback.format_exc())


QuoteManager()
