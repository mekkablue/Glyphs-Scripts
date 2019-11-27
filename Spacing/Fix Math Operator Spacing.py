#MenuTitle: Fix Math Operator Spacing
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__="""
Syncs widths and centers glyphs for +−×÷=≠±≈¬, optionally also Less/greater symbols and asciicircum/asciitilde.
"""

import vanilla

mathOperators = u"+−×÷=≠±≈¬"
lessGreater = u"><≥≤"
asciiOperators = u"~^"

class FixMathOperatorSpacing( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 290
		windowHeight = 390
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Fix Math Operator Spacing", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.FixMathOperatorSpacing.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 23
		
		self.w.decriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), "Sync widths between math operators:", sizeStyle='small', selectable=True )
		linePos += lineHeight



		# MATH OPERATORS:
		
		self.w.suffixText = vanilla.TextBox( (inset, linePos+2, 100, 14), u"With suffix:", sizeStyle='small', selectable=True )
		self.w.suffix = vanilla.EditText( (inset+100, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		self.w.suffix.getNSTextField().setToolTip_(u"Script only applies operators and reference glyphs that have this dot suffix. Enter with or without dot. Leave blank for default operators.")
		linePos += lineHeight
		
		self.w.referenceOperatorText = vanilla.TextBox( (inset, linePos+2, 100, 14), "Width reference:", sizeStyle='small', selectable=True )
		self.w.referenceOperator = vanilla.PopUpButton( (inset+100, linePos, -inset, 17), [u"%s %s"%(c,Glyphs.niceGlyphName(c)) for c in mathOperators+lessGreater+asciiOperators], sizeStyle='small', callback=self.SavePreferences )
		self.w.referenceOperator.getNSPopUpButton().setToolTip_(u"The glyph that is used for the reference width and for the metrics keys.")
		linePos += lineHeight
		
		self.w.SyncWidths = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Sync widths of: %s"%mathOperators, value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.SyncWidths.getNSButton().setToolTip_(u"Syncs the width of the math operators with the reference glyph.")
		linePos += lineHeight
		
		self.w.centerMathOperators = vanilla.CheckBox( (inset*2+3, linePos-1, -inset, 20), u"Center shapes for: %s"%mathOperators, value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.centerMathOperators.getNSButton().setToolTip_(u"Centers the shape of the operator glyph in its width.")
		linePos += lineHeight
		
		self.w.metricKeysForMathOperators = vanilla.CheckBox( (inset*2+3, linePos-1, -inset, 20), u"Set width metrics key", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.metricKeysForMathOperators.getNSButton().setToolTip_(u"Also applies metrics keys for the width, so you can update later with Glyph > Update Metrics.")
		linePos += lineHeight
		
		
		
		# LESS AND GREATER:
		
		self.w.syncWidthsLessGreater = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Sync widths of: %s"%lessGreater, value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.syncWidthsLessGreater.getNSButton().setToolTip_(u"Also syncs widths of less, greater, lessequal and greaterequal.")
		linePos += lineHeight
		
		radioOptions = ( 
			u"Same options as above", 
			u"Same options as above, but no centering", 
			u"Metrics keys based on:",
			)
		self.w.lessGreaterRadioButtons = vanilla.RadioGroup( (inset*2, linePos, -inset, lineHeight*len(radioOptions) ), radioOptions, callback=self.SavePreferences, sizeStyle = 'small' )
		self.w.lessGreaterRadioButtons.set( 0 )
		linePos += lineHeight*(len(radioOptions)-1)
		
		self.w.lessGreaterMetricReference = vanilla.PopUpButton( (inset+160, linePos+2, -inset, 17), [u"%s %s"%(c,Glyphs.niceGlyphName(c)) for c in lessGreater+mathOperators+asciiOperators], sizeStyle='small', callback=self.SavePreferences )
		self.w.lessGreaterMetricReference.getNSPopUpButton().setToolTip_(u"Override the reference glyph for <>≤≥. Useful if you do not want to center <>≤≥.")
		linePos += lineHeight

		self.w.syncWidthOfLessGreaterReference = vanilla.CheckBox( (inset*3.5, linePos-1, -inset, 20), u"Sync width of this reference glyph", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		
		# ASCII OPERATORS:
		self.w.SyncWidthsAscii = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Sync widths of: %s"%asciiOperators, value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.SyncWidthsAscii.getNSButton().setToolTip_(u"Syncs widths of asciicircum and asciitilde, with the same options as for the main math operators.")
		linePos += lineHeight
		
		self.w.ignoreAutoAligned = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Ignore auto-aligned compounds", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.ignoreAutoAligned.getNSButton().setToolTip_(u"Skips centering and metrics keys for layers that are built from components and are auto-aligned.")
		linePos += lineHeight
		
		self.w.deleteLayerMetricsKeys = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Reset layer metrics keys", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.deleteLayerMetricsKeys.getNSButton().setToolTip_(u"In glyphs that receive new metric keys, delete all layer-specific metric keys (e.g., ‘==100’).")
		linePos += lineHeight
		
		
		# Buttons:
		self.w.tabButton = vanilla.Button( (-200-inset, -20-inset, -90-inset, -inset), "Open Tab", sizeStyle='regular', callback=self.OpenTab )
		self.w.tabButton.getNSButton().setToolTip_(u"Opens a new Edit tab with +−×÷=≠±≈¬ <>≤≥ ^~")
		
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Sync", sizeStyle='regular', callback=self.FixMathOperatorSpacingMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print(u"⚠️ Note: 'Fix Math Operator Spacing' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def updateTextsInUI(self):
		enteredSuffix = self.suffixWithDot( self.w.suffix.get().strip() )
			
		referenceOperator = self.w.referenceOperator.getTitle().split()[-1]
		title = u"Set metrics key for width: ‘=%s’" % (referenceOperator+enteredSuffix)
		self.w.metricKeysForMathOperators.setTitle(title)
		
		lessGreaterReferenceOperator = self.w.lessGreaterMetricReference.getTitle().split()[-1]
		title = u"Set width key for %s: ‘=%s’" % (lessGreaterReferenceOperator+enteredSuffix, referenceOperator+enteredSuffix)
		self.w.syncWidthOfLessGreaterReference.setTitle(title)
		
		onOff = self.w.SyncWidths.get()
		self.w.centerMathOperators.enable(onOff)
		self.w.metricKeysForMathOperators.enable(onOff)
		
		onOff = self.w.syncWidthsLessGreater.get()
		self.w.lessGreaterRadioButtons.enable(onOff)
		self.w.lessGreaterMetricReference.enable(onOff)
		self.w.syncWidthOfLessGreaterReference.enable(onOff)
		
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.referenceOperator"] = self.w.referenceOperator.get()
			Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.suffix"] = self.w.suffix.get()
			Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.SyncWidths"] = self.w.SyncWidths.get()
			Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.centerMathOperators"] = self.w.centerMathOperators.get()
			Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.metricKeysForMathOperators"] = self.w.metricKeysForMathOperators.get()
			Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.syncWidthsLessGreater"] = self.w.syncWidthsLessGreater.get()
			Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.SyncWidthsAscii"] = self.w.SyncWidthsAscii.get()
			Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.lessGreaterRadioButtons"] = self.w.lessGreaterRadioButtons.get()
			Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.lessGreaterMetricReference"] = self.w.lessGreaterMetricReference.get()
			Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.syncWidthOfLessGreaterReference"] = self.w.syncWidthOfLessGreaterReference.get()
			Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.ignoreAutoAligned"] = self.w.ignoreAutoAligned.get()
			Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.deleteLayerMetricsKeys"] = self.w.deleteLayerMetricsKeys.get()
			
			self.updateTextsInUI()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.FixMathOperatorSpacing.referenceOperator", 0)
			Glyphs.registerDefault("com.mekkablue.FixMathOperatorSpacing.suffix", "")
			Glyphs.registerDefault("com.mekkablue.FixMathOperatorSpacing.SyncWidths", 0)
			Glyphs.registerDefault("com.mekkablue.FixMathOperatorSpacing.centerMathOperators", 0)
			Glyphs.registerDefault("com.mekkablue.FixMathOperatorSpacing.metricKeysForMathOperators", 0)
			Glyphs.registerDefault("com.mekkablue.FixMathOperatorSpacing.syncWidthsLessGreater", 0)
			Glyphs.registerDefault("com.mekkablue.FixMathOperatorSpacing.SyncWidthsAscii", 0)
			Glyphs.registerDefault("com.mekkablue.FixMathOperatorSpacing.lessGreaterRadioButtons", 0)
			Glyphs.registerDefault("com.mekkablue.FixMathOperatorSpacing.lessGreaterMetricReference", 0)
			Glyphs.registerDefault("com.mekkablue.FixMathOperatorSpacing.syncWidthOfLessGreaterReference", 0)
			Glyphs.registerDefault("com.mekkablue.FixMathOperatorSpacing.ignoreAutoAligned", 0)
			Glyphs.registerDefault("com.mekkablue.FixMathOperatorSpacing.deleteLayerMetricsKeys", 0)
			
			self.w.referenceOperator.set( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.referenceOperator"] )
			self.w.suffix.set( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.suffix"] )
			self.w.SyncWidths.set( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.SyncWidths"] )
			self.w.centerMathOperators.set( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.centerMathOperators"] )
			self.w.metricKeysForMathOperators.set( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.metricKeysForMathOperators"] )
			self.w.syncWidthsLessGreater.set( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.syncWidthsLessGreater"] )
			self.w.SyncWidthsAscii.set( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.SyncWidthsAscii"] )
			self.w.lessGreaterRadioButtons.set( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.lessGreaterRadioButtons"] )
			self.w.lessGreaterMetricReference.set( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.lessGreaterMetricReference"] )
			self.w.syncWidthOfLessGreaterReference.set( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.syncWidthOfLessGreaterReference"] )
			self.w.ignoreAutoAligned.set( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.ignoreAutoAligned"] )
			self.w.deleteLayerMetricsKeys.set( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.deleteLayerMetricsKeys"] )
			
			self.updateTextsInUI()
		except:
			return False
			
		return True
	
	def OpenTab(self, sender):
		# update prefs:
		self.SavePreferences(sender)
		
		# all operators
		tabText = u"+−×÷=≠±≈¬\n<>≤≥\n^~"
		suffix = self.suffixWithDot( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.suffix"] )
		
		# opens new Edit tab:
		thisFont = Glyphs.font
		if thisFont:
			if suffix:
				escapedTabText=""
				for tabLine in tabText.splitlines():
					for char in tabLine:
						escapedTabText += "/%s%s" % ( Glyphs.niceGlyphName(char), suffix )
					escapedTabText += "\n"
				tabText = escapedTabText[:-1]
			thisFont.newTab( tabText )
		else:
			Message(title="No Font Error", message="Could not determine a frontmost font. Open a font and try again.", OKButton="😬 Oops")
	
	def suffixWithDot(self, suffix):
		if suffix:
			suffix = suffix.strip()
			if suffix and suffix[0]!=".":
				suffix = ".%s"%suffix
		else:
			suffix = ""
		return suffix
	
	def centerLayerInWidth(self, layer):
		oldWidth = layer.width
		newSB = (layer.LSB+layer.RSB)/2
		layer.LSB = round(newSB)
		layer.width = oldWidth
		print(u"   ✅ Centered shape on layer: %s" % layer.name)
	
	def updateMetricKeys(self, layer):
		if Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.deleteLayerMetricsKeys"]:
			layer.leftMetricsKey = None
			layer.rightMetricsKey = None
			layer.widthMetricsKey = None
		layer.updateMetrics()
		layer.syncMetrics()
	
	def warnAboutMissingGlyph(self, glyphName):
		print(u"❌ Warning: glyph %s is missing." % glyphName)
		# brings macro window to front:
		Glyphs.showMacroWindow()
	
	def warnAboutAutoAlignedLayer(self, layer):
		print(u"   ℹ️ Layer ‘%s’ is auto-aligned compound: skipping" % layer.name)
	
	def reportProcessing(self, glyphName):
		print(u"🔣 %s" % glyphName)

	def FixMathOperatorSpacingMain( self, sender ):
		try:
			self.SavePreferences(None) # get the current UI state (in case two windows are open)
			
			suffix = self.suffixWithDot( Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.suffix"] )
			
			syncWidths = Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.SyncWidths"]
			syncWidthsLessGreater = Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.syncWidthsLessGreater"]
			syncWidthsAscii = Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.SyncWidthsAscii"]

			centerMathOperators = Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.centerMathOperators"]
			metricKeysForMathOperators = Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.metricKeysForMathOperators"]
			lessGreaterRadioButtons = int(Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.lessGreaterRadioButtons"])
			lessGreaterMetricReferenceName = "%s%s" % ( self.w.lessGreaterMetricReference.getTitle().split()[-1], suffix )
			syncWidthOfLessGreaterReference = Glyphs.defaults["com.mekkablue.FixMathOperatorSpacing.syncWidthOfLessGreaterReference"]
			
			Glyphs.clearLog()
			thisFont = Glyphs.font # frontmost font
			print("Fixing Math Operator Spacing for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			
			referenceOperatorName = "%s%s" % ( self.w.referenceOperator.getTitle().split()[-1], suffix )
			referenceOperatorGlyph = thisFont.glyphs[referenceOperatorName]
			
			# SYNC MATH AND ASCII OPERATORS
			charsToProcess = u""
			if syncWidthsAscii:
				charsToProcess += asciiOperators
			if syncWidths:
				charsToProcess += mathOperators
			if syncWidthOfLessGreaterReference and lessGreaterRadioButtons == 2 and syncWidthsLessGreater:
				charsToProcess += self.w.lessGreaterMetricReference.getTitle().split()[0]
			if charsToProcess:
				for mathOperatorChar in charsToProcess:
					mathOperatorGlyphName = "%s%s" % ( Glyphs.niceGlyphName(mathOperatorChar), suffix )
					mathOperatorGlyph = thisFont.glyphs[mathOperatorGlyphName]
					if not mathOperatorGlyph:
						self.warnAboutMissingGlyph(mathOperatorGlyphName)
					else:
						self.reportProcessing(mathOperatorGlyphName)
						
						# add metrics keys if necessary
						if metricKeysForMathOperators:
							widthKey = "=%s" % referenceOperatorName
							mathOperatorGlyph.widthMetricsKey = widthKey
							mathOperatorGlyph.leftMetricsKey = None
							mathOperatorGlyph.rightMetricsKey = None
							print(u"   ✅ Set width metrics key: %s" % widthKey)
						
						for layer in mathOperatorGlyph.layers:
							if layer.isAligned:
								self.warnAboutAutoAlignedLayer(layer)
							else:
								# check if layer is relevant in the first place:
								master = layer.associatedFontMaster()
								isMasterLayer = layer.layerId == master.id
								isBracketLayer = "[" in layer.name and "]" in layer.name
								isBraceLayer = "{" in layer.name and "}" in layer.name
								if isMasterLayer or isBraceLayer or isBracketLayer:
									referenceLayer = referenceOperatorGlyph.layers[master.id]

									# sync width with reference glyph (only for other glyphs):
									if mathOperatorGlyph != referenceOperatorGlyph:
								
										# update width
										layer.width = referenceLayer.width
								
										# update metrics keys if necessary
										if metricKeysForMathOperators:
											self.updateMetricKeys(layer)
							
									# center shape (also for reference glyph):
									if centerMathOperators and mathOperatorGlyphName != lessGreaterMetricReferenceName:
										self.centerLayerInWidth(layer)
										# add metricskey if necessary:
										# if metricKeysForMathOperators:
										# 	mathOperatorGlyph.rightMetricsKey = "=|"
											# update metrics: 
											# layer.updateMetrics()
											# layer.syncMetrics()
							
				
			# SYNC LESS/GREATER:
			if syncWidthsLessGreater:

				# overwrite options:
				if lessGreaterRadioButtons > 0:
					centerMathOperators = False
				if lessGreaterRadioButtons == 2:
					referenceOperatorName = lessGreaterMetricReferenceName
					referenceOperatorGlyph = thisFont.glyphs[referenceOperatorName]
				
				if not referenceOperatorGlyph:
					self.warnAboutMissingGlyph(referenceOperatorName)
				else:
					for lessGreaterChar in lessGreater:
						lessGreaterGlyphName = "%s%s" % ( Glyphs.niceGlyphName(lessGreaterChar), suffix )
						lessGreaterGlyph = thisFont.glyphs[lessGreaterGlyphName]
						if not lessGreaterGlyph:
							self.warnAboutMissingGlyph(lessGreaterGlyphName)
						else:
							# do not process reference glyph twice:
							lessGreaterReferenceAlreadyProcessed = syncWidthOfLessGreaterReference and lessGreaterRadioButtons == 2 and syncWidthsLessGreater
							if not (lessGreaterGlyphName == referenceOperatorName and lessGreaterReferenceAlreadyProcessed):
								self.reportProcessing(lessGreaterGlyphName)
								
								# add metrics keys if necessary
								if metricKeysForMathOperators:
									widthKey = "=%s" % referenceOperatorName
									sbKey = widthKey
						
									notBothLess = "less" in referenceOperatorName and not "less" in lessGreaterGlyphName
									notBothGreater = "great" in referenceOperatorName and not "great" in lessGreaterGlyphName
									if notBothLess or notBothGreater:
										sbKey = "=|%s" % referenceOperatorName
									lessGreaterGlyph.widthMetricsKey = widthKey
									lessGreaterGlyph.leftMetricsKey = sbKey
									lessGreaterGlyph.rightMetricsKey = None
									print(u"   ✅ Set keys for width: %s, LSB: %s" % (widthKey, sbKey))
								
								for layer in lessGreaterGlyph.layers:
									if layer.isAligned:
										self.warnAboutAutoAlignedLayer(layer)
									else:
										# check if layer is relevant in the first place:
										master = layer.associatedFontMaster()
										isMasterLayer = layer.layerId == master.id
										isBracketLayer = "[" in layer.name and "]" in layer.name
										isBraceLayer = "{" in layer.name and "}" in layer.name
										if isMasterLayer or isBraceLayer or isBracketLayer:
											referenceLayer = referenceOperatorGlyph.layers[master.id]

											# sync width with reference glyph (only for other glyphs):
											if lessGreaterGlyph != referenceOperatorGlyph:
								
												# update width
												layer.width = referenceLayer.width
								
												# update metrics keys if necessary
												if metricKeysForMathOperators:
													self.updateMetricKeys(layer)
							
											# center shape (also for reference glyph):
											if centerMathOperators:
												self.centerLayerInWidth(layer)
								
												# add metricskey if necessary:
												# if metricKeysForMathOperators:
												# 	mathOperatorGlyph.rightMetricsKey = "=|"
													# update metrics: 
													# layer.updateMetrics()
													# layer.syncMetrics()
			
			if not self.SavePreferences( self ):
				print(u"⚠️ Note: 'Fix Math Operator Spacing' could not write preferences.")
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Fix Math Operator Spacing Error: %s" % e)
			import traceback
			print(traceback.format_exc())

FixMathOperatorSpacing()