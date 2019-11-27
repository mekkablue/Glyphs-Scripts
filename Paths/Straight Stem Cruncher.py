#MenuTitle: Straight Stem Cruncher
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__="""
Measures in centers of straight segments, and reports deviations in stem thicknesses.
"""

import vanilla
from Foundation import NSPoint

def pointDistance(p1, p2):
	stemThickness = ( (p2.x-p1.x)**2.0 + (p2.y-p1.y)**2.0 ) **0.5
	return stemThickness

def middleBetweenTwoPoints(p1, p2):
	x = (p1.x+p2.x)*0.5
	y = (p1.y+p2.y)*0.5
	return NSPoint(x,y)

class StraightStemCruncher( object ):
	defaultExcludeList = ".sc, .c2sc, .smcp, .sups, .subs, .sinf, superior, inferior, .numr, .dnom"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 355
		windowHeight = 345
		windowWidthResize  = 600 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Straight Stem Cruncher", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.StraightStemCruncher.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"In current master, looks for stems close but not exactly at:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.stemsText = vanilla.TextBox( (inset, linePos+3, 80, 14), u"Stem Widths:", sizeStyle='small', selectable=True )
		self.w.stems = vanilla.EditText( (inset+80, linePos, -inset-25, 19), "20, 30, 40", callback=self.SavePreferences, sizeStyle='small' )
		self.w.stems.getNSTextField().setToolTip_("Comma-separated list of stem sizes to look for. If the script finds stems deviating from these sizes, within the given min/max deviations, it will report them.")
		self.w.stemUpdate = vanilla.SquareButton( (-inset-20, linePos, -inset, 19), u"↺", sizeStyle='small', callback=self.update )
		self.w.stemUpdate.getNSButton().setToolTip_("Populate the stems with the stems of the current master.")
		linePos += lineHeight
		
		self.w.stemFindText = vanilla.TextBox( (inset, linePos+3, 175, 14), u"Find deviating stems, min/max:", sizeStyle='small', selectable=True )
		self.w.deviationMin = vanilla.EditText( (inset+175, linePos, 45, 19), "0.4", callback=self.SavePreferences, sizeStyle='small' )
		self.w.deviationMin.getNSTextField().setToolTip_("Deviations up to this value will be tolerated. Half a unit is a good idea to avoid false positives from rounding errors.")
		self.w.deviationMax = vanilla.EditText( (inset+175+55, linePos, 45, 19), "3.1", callback=self.SavePreferences, sizeStyle='small' )
		self.w.deviationMax.getNSTextField().setToolTip_("Deviations up to this value will be reported. Do not exaggerate value, otherwise you get false positives from cases where the opposing segment is not the other side of the stem.")
		linePos += lineHeight
		
		self.w.minimumSegmentLengthText = vanilla.TextBox( (inset, linePos+2, 145, 14), u"Minimum segment length:", sizeStyle='small', selectable=True )
		self.w.minimumSegmentLength = vanilla.EditText( (inset+145, linePos, -inset-25, 19), "200", callback=self.SavePreferences, sizeStyle='small' )
		self.w.minimumSegmentLength.getNSTextField().setToolTip_("Looks for straight-line segments with at least this length and measures from their center to the opposing segment. Half x-height is a good idea.")
		self.w.segmentLengthUpdate = vanilla.SquareButton( (-inset-20, linePos, -inset, 19), u"↺", sizeStyle='small', callback=self.update )
		self.w.segmentLengthUpdate.getNSButton().setToolTip_("Reset to 40% of x-height.")
		linePos += lineHeight
		
		self.w.ignoreDiagonals = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Ignore diagonal stems", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.ignoreDiagonals.getNSButton().setToolTip_("If activated, only measures completely horizontal and completely vertical segments.")
		linePos += lineHeight
		
		self.w.checkSpecialLayers = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Also check bracket layers", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.checkSpecialLayers.getNSButton().setToolTip_("If checked, also measures on bracket ayers. Otherwise only on master layers.")
		linePos += lineHeight
		
		self.w.selectedGlyphsOnly = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Measure selected glyphs only (otherwise all glyphs in font)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.selectedGlyphsOnly.getNSButton().setToolTip_("Uncheck for measuring complete font.")
		linePos += lineHeight
		
		self.w.includeNonExporting = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeNonExporting.getNSButton().setToolTip_("Usually not necessary because the algorithm decomposes and removes overlap first.")
		linePos += lineHeight
		
		self.w.includeCompounds = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Include components", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeCompounds.getNSButton().setToolTip_("If checked, also measures components (after decomposition and removing overlap). If unchecked, only measures outlines.")
		linePos += lineHeight
		
		self.w.excludeGlyphs = vanilla.CheckBox( (inset, linePos, 165, 20), u"Exclude glyphs containing:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.excludeGlyphNames = vanilla.EditText( (inset+165, linePos, -inset-25, 19), self.defaultExcludeList, callback=self.SavePreferences, sizeStyle='small' )
		self.w.excludeGlyphNames.getNSTextField().setToolTip_("Comma-separated list of glyph name parts (e.g., suffixes). Glyphs containing these will not be measured if checkbox is enabled.")
		self.w.excludeGlyphNamesReset = vanilla.SquareButton( (-inset-20, linePos, -inset, 19), u"↺", sizeStyle='small', callback=self.update )
		self.w.excludeGlyphNamesReset.getNSButton().setToolTip_("Reset to: %s." % self.defaultExcludeList)
		linePos += lineHeight
		
		self.w.reportNonMeasurements = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Report layers without measurements", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reportNonMeasurements.getNSButton().setToolTip_("In Macro Window, report if a layer does not have any measurements. Most likely causes: no straight stems in the paths, or wrong path direction.")
		linePos += lineHeight
		
		self.w.openTab = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Open tab with affected glyphs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.openTab.getNSButton().setToolTip_("If unchecked, will bring macro window with detailed report to front.")
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Measure", sizeStyle='regular', callback=self.StraightStemCruncherMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Straight Stem Cruncher' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def update( self, sender=None ):
		if sender == self.w.segmentLengthUpdate:
			xHeight = Glyphs.font.selectedFontMaster.xHeight
			self.w.minimumSegmentLength.set("%i" % round(xHeight/2.1,-1))
			
		elif sender == self.w.stemUpdate:
			stems = [s for s in Glyphs.font.selectedFontMaster.horizontalStems+Glyphs.font.selectedFontMaster.verticalStems]
			stems = sorted(set(stems))
			stemString = ", ".join( [str(s) for s in stems] )
			if stemString:
				self.w.stems.set(stemString)
			else:
				Message(title="Stem Error", message="No standard stems defined in the current master. Please add some in Font Info > Masters.", OKButton=None)
		
		elif sender == self.w.excludeGlyphNamesReset:
			self.w.excludeGlyphNames.set(self.defaultExcludeList)
		
		self.SavePreferences()
				
	def SavePreferences( self, sender=None ):
		try:
			Glyphs.defaults["com.mekkablue.StraightStemCruncher.stems"] = self.w.stems.get()
			Glyphs.defaults["com.mekkablue.StraightStemCruncher.deviationMin"] = self.w.deviationMin.get()
			Glyphs.defaults["com.mekkablue.StraightStemCruncher.deviationMax"] = self.w.deviationMax.get()
			Glyphs.defaults["com.mekkablue.StraightStemCruncher.checkSpecialLayers"] = self.w.checkSpecialLayers.get()
			Glyphs.defaults["com.mekkablue.StraightStemCruncher.selectedGlyphsOnly"] = self.w.selectedGlyphsOnly.get()
			Glyphs.defaults["com.mekkablue.StraightStemCruncher.includeNonExporting"] = self.w.includeNonExporting.get()
			Glyphs.defaults["com.mekkablue.StraightStemCruncher.openTab"] = self.w.openTab.get()
			Glyphs.defaults["com.mekkablue.StraightStemCruncher.includeCompounds"] = self.w.includeCompounds.get()
			Glyphs.defaults["com.mekkablue.StraightStemCruncher.minimumSegmentLength"] = self.w.minimumSegmentLength.get()
			Glyphs.defaults["com.mekkablue.StraightStemCruncher.reportNonMeasurements"] = self.w.reportNonMeasurements.get()
			Glyphs.defaults["com.mekkablue.StraightStemCruncher.excludeGlyphs"] = self.w.excludeGlyphs.get()
			Glyphs.defaults["com.mekkablue.StraightStemCruncher.excludeGlyphNames"] = self.w.excludeGlyphNames.get()
			Glyphs.defaults["com.mekkablue.StraightStemCruncher.ignoreDiagonals"] = self.w.ignoreDiagonals.get()
			
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.StraightStemCruncher.stems", "80, 100")
			Glyphs.registerDefault("com.mekkablue.StraightStemCruncher.deviationMin", 0.6)
			Glyphs.registerDefault("com.mekkablue.StraightStemCruncher.deviationMax", 4.0)
			Glyphs.registerDefault("com.mekkablue.StraightStemCruncher.checkSpecialLayers", 1)
			Glyphs.registerDefault("com.mekkablue.StraightStemCruncher.selectedGlyphsOnly", 0)
			Glyphs.registerDefault("com.mekkablue.StraightStemCruncher.includeNonExporting", 0)
			Glyphs.registerDefault("com.mekkablue.StraightStemCruncher.openTab", 1)
			Glyphs.registerDefault("com.mekkablue.StraightStemCruncher.includeCompounds", 0)
			Glyphs.registerDefault("com.mekkablue.StraightStemCruncher.minimumSegmentLength", 200)
			Glyphs.registerDefault("com.mekkablue.StraightStemCruncher.reportNonMeasurements", 0)
			Glyphs.registerDefault("com.mekkablue.StraightStemCruncher.excludeGlyphs", 0)
			Glyphs.registerDefault("com.mekkablue.StraightStemCruncher.excludeGlyphNames", self.defaultExcludeList)
			Glyphs.registerDefault("com.mekkablue.StraightStemCruncher.ignoreDiagonals", 0)
			

			self.w.stems.set( Glyphs.defaults["com.mekkablue.StraightStemCruncher.stems"] )
			self.w.deviationMin.set( Glyphs.defaults["com.mekkablue.StraightStemCruncher.deviationMin"] )
			self.w.deviationMax.set( Glyphs.defaults["com.mekkablue.StraightStemCruncher.deviationMax"] )
			self.w.checkSpecialLayers.set( Glyphs.defaults["com.mekkablue.StraightStemCruncher.checkSpecialLayers"] )
			self.w.selectedGlyphsOnly.set( Glyphs.defaults["com.mekkablue.StraightStemCruncher.selectedGlyphsOnly"] )
			self.w.includeNonExporting.set( Glyphs.defaults["com.mekkablue.StraightStemCruncher.includeNonExporting"] )
			self.w.openTab.set( Glyphs.defaults["com.mekkablue.StraightStemCruncher.openTab"] )
			self.w.includeCompounds.set( Glyphs.defaults["com.mekkablue.StraightStemCruncher.includeCompounds"] )
			self.w.minimumSegmentLength.set( Glyphs.defaults["com.mekkablue.StraightStemCruncher.minimumSegmentLength"] )
			self.w.reportNonMeasurements.set( Glyphs.defaults["com.mekkablue.StraightStemCruncher.reportNonMeasurements"] )
			self.w.excludeGlyphs.set( Glyphs.defaults["com.mekkablue.StraightStemCruncher.excludeGlyphs"] )
			self.w.excludeGlyphNames.set( Glyphs.defaults["com.mekkablue.StraightStemCruncher.excludeGlyphNames"] )
			self.w.ignoreDiagonals.set( Glyphs.defaults["com.mekkablue.StraightStemCruncher.ignoreDiagonals"] )
			
		except:
			return False
			
		return True

	def stemThicknessAtLine(self, layer, p1, p2, measureLength=100.0):
		h = p2.x-p1.x
		v = p2.y-p1.y
		l = (h**2+v**2)**0.5
	
		hUnit = h/l
		vUnit = v/l
	
		h = hUnit * measureLength
		v = vUnit * measureLength
	
		measurePoint1 = middleBetweenTwoPoints(p1,p2)
		#	print "  middle:", measurePoint1, hUnit, vUnit
		# 	measurePoint1.x += vUnit*2
		# 	measurePoint1.y -= hUnit*2
	
		measurePoint2 = NSPoint(measurePoint1.x-v,measurePoint1.y+h)
		intersections = layer.intersectionsBetweenPoints(measurePoint1,measurePoint2)
	
		if measurePoint1 != intersections[0].pointValue():
			intersections = intersections[::-1]
	
		if len(intersections) > 2:
			stemWidth = pointDistance(intersections[1],intersections[2])
			return stemWidth
		else:
			return None

	def measureStraighStemsInLayer(self, layer, glyphName=""):
		try:
			minLength=int( Glyphs.defaults["com.mekkablue.StraightStemCruncher.minimumSegmentLength"] )
		except:
			self.update(self.w.segmentLengthUpdate)
			minLength=int( Glyphs.defaults["com.mekkablue.StraightStemCruncher.minimumSegmentLength"] )
			
		measurements = []
		measureLayer = layer.copyDecomposedLayer()
		measureLayer.removeOverlap()
		for thisPath in measureLayer.paths:
			nodeCount = len(thisPath.nodes)
			if nodeCount>2:
				for thisSegment in thisPath.segments:
					if len(thisSegment)==2:
						p1 = thisSegment[0].pointValue()
						p2 = thisSegment[1].pointValue()
						if p1.x==p2.x or p1.y==p2.y or not Glyphs.defaults["com.mekkablue.StraightStemCruncher.ignoreDiagonals"]:
							if pointDistance(p1,p2) >= minLength:
								measurement = self.stemThicknessAtLine( measureLayer, p1, p2, measureLength=max(100.0,measureLayer.bounds.size.width+measureLayer.bounds.size.height) )
								measurements.append(measurement)
			else:
				print(u"⚠️ Found path with only %i point%s%s." % ( 
					nodeCount,
					"" if nodeCount==1 else "s",
					" in %s" % glyphName if glyphName else "",
					))
		return measurements

	def StraightStemCruncherMain( self, sender ):
		try:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Straight Stem Cruncher' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			print("Straight Stem Cruncher Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			
			self.w.progress.set(0)
			if Glyphs.defaults["com.mekkablue.StraightStemCruncher.selectedGlyphsOnly"]:
				glyphsToCheck = [l.parent for l in thisFont.selectedLayers]
			else:
				glyphsToCheck = thisFont.glyphs
			
			excludedGlyphNameParts = []
			if Glyphs.defaults["com.mekkablue.StraightStemCruncher.excludeGlyphs"]:
				enteredParts = [ x.strip() for x in Glyphs.defaults["com.mekkablue.StraightStemCruncher.excludeGlyphNames"].split(",") ]
				if enteredParts:
					excludedGlyphNameParts.extend( set(enteredParts) )
			
			stems = Glyphs.defaults["com.mekkablue.StraightStemCruncher.stems"] # "80, 100"
			stems = [int(s.strip()) for s in stems.split(",")]
			
			deviationMin = float( Glyphs.defaults["com.mekkablue.StraightStemCruncher.deviationMin"] ) # 0.6
			deviationMax = float( Glyphs.defaults["com.mekkablue.StraightStemCruncher.deviationMax"] ) # 4.0
			
			affectedLayers = []
			for glyphIndex, thisGlyph in enumerate(glyphsToCheck):
				self.w.progress.set(100*glyphIndex/len(thisFont.glyphs))
				
				# see if any exclusion applies:
				
				glyphNameIsExcluded = False
				for particle in excludedGlyphNameParts:
					if particle in thisGlyph.name:
						glyphNameIsExcluded = True
						break
				
				glyphExportsOrNonExportingIncluded = thisGlyph.export or Glyphs.defaults["com.mekkablue.StraightStemCruncher.includeNonExporting"]
				
				if glyphExportsOrNonExportingIncluded and not glyphNameIsExcluded:
					for thisLayer in thisGlyph.layers:
						if thisLayer.master == thisFont.selectedFontMaster:
							if thisLayer.isMasterLayer or (thisLayer.isSpecialLayer and Glyphs.defaults["com.mekkablue.StraightStemCruncher.checkSpecialLayers"]):
								if Glyphs.defaults["com.mekkablue.StraightStemCruncher.includeCompounds"]:
									checkLayer = thisLayer.copyDecomposedLayer()
								else:
									checkLayer = thisLayer.copy()
									checkLayer.components = None
								
								if checkLayer.paths:
									checkLayer.removeOverlap()
									measurements = self.measureStraighStemsInLayer(checkLayer, glyphName=thisGlyph.name)
									if not measurements:
										if Glyphs.defaults["com.mekkablue.StraightStemCruncher.reportNonMeasurements"]:
											print(u"⚠️ %s, layer '%s': no stem measurements. Wrong path direction or no line segments?" % (
												thisGlyph.name,
												thisLayer.name,
											))
									else:
										deviatingStems = []
										for measurement in measurements:
											if not measurement in stems:
												for stem in stems:
													if stem-deviationMax < measurement < stem-deviationMin or stem+deviationMin < measurement < stem+deviationMax:
														deviatingStems.append(measurement)
										if deviatingStems:
											print(u"❌ %s, layer '%s': found %i stem%s off: %s." % ( 
												thisGlyph.name, thisLayer.name, 
												len( deviatingStems ),
												"" if len(deviatingStems) == 1 else "s",
												", ".join( ["%.1f"%s for s in deviatingStems] ),
											))
											if not thisLayer in affectedLayers:
												affectedLayers.append(thisLayer)
									
			self.w.progress.set(100)
			
			if not affectedLayers:
				Message(title="No Deviances Found", message="No point distances deviating from supplied stem widths within the given limits.", OKButton=None)
			elif Glyphs.defaults["com.mekkablue.StraightStemCruncher.openTab"]:
				tab = thisFont.newTab()
				tab.layers = affectedLayers
			else:
				# brings macro window to front:
				Glyphs.showMacroWindow()
			
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Straight Stem Cruncher Error: %s" % e)
			import traceback
			print(traceback.format_exc())

StraightStemCruncher()