#MenuTitle: Short Segment Finder
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Goes through all interpolations and finds segments shorter than a user-specified threshold length.
"""

import vanilla
from Foundation import NSPoint

tempMarker = "###DELETEME###"
nodeMarker = u"👌🏻"

class ShortSegmentFinder( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 280
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Short Segment Finder", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.ShortSegmentFinder.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 30), u"Finds short segments in interpolations or masters, and opens a new tab with them", sizeStyle='small', selectable=True )
		linePos += lineHeight*2
		
		self.w.text_1 = vanilla.TextBox( (inset, linePos+2, 185, 14), "Acceptable min segment length:", sizeStyle='small' )
		self.w.minSegmentLength = vanilla.EditText( (inset+185, linePos-1, -inset, 19), "3", sizeStyle='small', callback=self.SavePreferences)
		self.w.minSegmentLength.getNSTextField().setToolTip_("Minimum length for every segment in all paths, measured in units.")
		linePos += lineHeight
		
		self.w.findShortSegmentsInMasters = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Look in masters instead (i.e., not in interpolations)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.findShortSegmentsInMasters.getNSButton().setToolTip_("If checked, will not calculate interpolations, but only measure segments in your master drawings, bracket and brace layers.")
		linePos += lineHeight
		
		self.w.allGlyphs = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Process all glyphs in font (i.e., ignore selection)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.allGlyphs.getNSButton().setToolTip_("If unchecked, will only process the currently selected glyph(s).")
		linePos += lineHeight
		
		self.w.exportingOnly = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Ignore non-exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.exportingOnly.getNSButton().setToolTip_("If checked, will skip glyphs that do not export. Always skips compounds.")
		linePos += lineHeight

		self.w.reportIncompatibilities = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Report incompatibilities and no paths in Macro Window", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reportIncompatibilities.getNSButton().setToolTip_("If checked, will warn about incompatibilities and if a glyph has no paths. Usually you want this off, because it will report all compounds.")
		linePos += lineHeight

		self.w.markSegments = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Mark segments in first layer", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.markSegments.getNSButton().setToolTip_("If checked, will mark affected segments with a warning emoji and the minimum segment length. Will mark the corresponding segment in the first layer if it finds a short segment in a calculated instance. Will use an annotation if the segment cannot be found (e.g. if the segment is in a corner component).")
		linePos += lineHeight

		self.w.bringMacroWindowToFront = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Bring Macro Window to front", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.bringMacroWindowToFront.getNSButton().setToolTip_("A detailed report is written to the Macro Window. Activate this check box, and the Macro Window will be brought to the front ever time you run this script.")
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Open Tab", sizeStyle='regular', callback=self.ShortSegmentFinderMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Short Segment Finder' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
		#
		self.adaptUItext(None)
	
	def adaptUItext( self, sender ):
		if Glyphs.defaults["com.mekkablue.ShortSegmentFinder.findShortSegmentsInMasters"]:
			self.w.markSegments.setTitle(u"Mark short segments 👌🏻")
		else:
			self.w.markSegments.setTitle(u"Mark short segments 👌🏻 in first layer")
		
		if Glyphs.defaults["com.mekkablue.ShortSegmentFinder.allGlyphs"]:
			self.w.runButton.setTitle("Open Tab")
		else:
			self.w.runButton.setTitle("Find Segments")
	
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.ShortSegmentFinder.minSegmentLength"] = self.w.minSegmentLength.get()
			Glyphs.defaults["com.mekkablue.ShortSegmentFinder.findShortSegmentsInMasters"] = self.w.findShortSegmentsInMasters.get()
			Glyphs.defaults["com.mekkablue.ShortSegmentFinder.allGlyphs"] = self.w.allGlyphs.get()
			Glyphs.defaults["com.mekkablue.ShortSegmentFinder.exportingOnly"] = self.w.exportingOnly.get()
			Glyphs.defaults["com.mekkablue.ShortSegmentFinder.reportIncompatibilities"] = self.w.reportIncompatibilities.get()
			Glyphs.defaults["com.mekkablue.ShortSegmentFinder.markSegments"] = self.w.markSegments.get()
			Glyphs.defaults["com.mekkablue.ShortSegmentFinder.bringMacroWindowToFront"] = self.w.bringMacroWindowToFront.get()
			self.adaptUItext(sender)
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.ShortSegmentFinder.minSegmentLength", 10.0)
			Glyphs.registerDefault("com.mekkablue.ShortSegmentFinder.findShortSegmentsInMasters", 0)
			Glyphs.registerDefault("com.mekkablue.ShortSegmentFinder.allGlyphs", 0)
			Glyphs.registerDefault("com.mekkablue.ShortSegmentFinder.exportingOnly", 1)
			Glyphs.registerDefault("com.mekkablue.ShortSegmentFinder.reportIncompatibilities", 0)
			Glyphs.registerDefault("com.mekkablue.ShortSegmentFinder.markSegments", 1)
			Glyphs.registerDefault("com.mekkablue.ShortSegmentFinder.bringMacroWindowToFront", 1)
			self.w.minSegmentLength.set( Glyphs.defaults["com.mekkablue.ShortSegmentFinder.minSegmentLength"] )
			self.w.findShortSegmentsInMasters.set( Glyphs.defaults["com.mekkablue.ShortSegmentFinder.findShortSegmentsInMasters"] )
			self.w.allGlyphs.set( Glyphs.defaults["com.mekkablue.ShortSegmentFinder.allGlyphs"] )
			self.w.exportingOnly.set( Glyphs.defaults["com.mekkablue.ShortSegmentFinder.exportingOnly"] )
			self.w.reportIncompatibilities.set( Glyphs.defaults["com.mekkablue.ShortSegmentFinder.reportIncompatibilities"] )
			self.w.markSegments.set( Glyphs.defaults["com.mekkablue.ShortSegmentFinder.markSegments"] )
			self.w.bringMacroWindowToFront.set( Glyphs.defaults["com.mekkablue.ShortSegmentFinder.bringMacroWindowToFront"] )
			self.adaptUItext(sender)
		except:
			return False
			
		return True
	
	def approxLengthOfSegment(self, segment):
		try:
			if len(segment) == 2:
				p0,p1 = [p.pointValue() for p in segment]
				return ( (p1.x-p0.x)**2 + (p1.y-p0.y)**2 )**0.5
			elif len(segment) == 4:
				p0,p1,p2,p3 = [p.pointValue() for p in segment]
				chord = distance(p0,p3)
				cont_net = distance(p0,p1) + distance(p1,p2) + distance(p2,p3)
				return (cont_net + chord) * 0.5 * 0.996767352316
			else:
				return u"Segment has unexpected point constellation (note: TT is not supported):\n    %s" % repr(segment)
		except Exception as e:
			print("SEGMENT:", segment)
			try:
				print("SEGMENT LENGTH:", len(segment))
			except:
				pass
			import traceback
			print(traceback.format_exc())
			return u"Possible single-node path."
	
	def bezier( self, p1, p2, p3, p4, t ):
		x1, y1 = p1.x, p1.y
		x2, y2 = p2.x, p2.y
		x3, y3 = p3.x, p3.y
		x4, y4 = p4.x, p4.y
		x = x1*(1-t)**3 + x2*3*t*(1-t)**2 + x3*3*t**2*(1-t) + x4*t**3
		y = y1*(1-t)**3 + y2*3*t*(1-t)**2 + y3*3*t**2*(1-t) + y4*t**3
		return NSPoint(x, y)
	
	def segmentMiddle(self, segment):
		if len(segment) == 2:
			p0,p1 = segment
			return NSPoint( (p0.x+p1.x)*0.5, (p0.y+p1.y)*0.5 )
		elif len(segment) == 4:
			p0,p1,p2,p3 = segment
			return self.bezier(p0,p1,p2,p3,0.5)
		else:
			print("Segment has unexpected length:\n" + segment)
			return None
	
	def segmentsInLayerShorterThan( self, thisLayer, minLength=10.0 ):
		shortSegments = []
		for thisPath in thisLayer.paths:
			nodeCount = len(thisPath.nodes)
			if not nodeCount>2:
				print(u"⚠️ WARNING: path with only %i point%s in %s (layer: %s). Skipping." % (
					nodeCount,
					"" if nodeCount==1 else "s",
					thisLayer.parent.name, 
					thisLayer.name,
					))
			else:
				for thisSegment in thisPath.segments:
					segmentLength = self.approxLengthOfSegment(thisSegment)
					if type(segmentLength) is unicode:
						print(u"😬 ERROR in %s (layer: %s): %s" % (thisLayer.parent.name, thisLayer.name, segmentLength))
					elif segmentLength < minLength:
						shortSegments.append(thisSegment)
		return shortSegments
	
	def glyphInterpolation( self, thisGlyphName, thisInstance ):
		"""
		Yields a layer.
		"""
		try:
			# calculate interpolation:
			interpolatedFont = thisInstance.pyobjc_instanceMethods.interpolatedFont()
			interpolatedLayer = interpolatedFont.glyphForName_(thisGlyphName).layers[0]
		
			# round to grid if necessary:
			if interpolatedLayer.paths:
				if interpolatedFont.gridLength == 1.0:
					interpolatedLayer.roundCoordinates()
				return interpolatedLayer
			else:
				return None
		except:
			import traceback
			print(traceback.format_exc())
			return None
	
	def addAnnotationTextAtPosition( self, layer, position, text ):
		annotationText = GSAnnotation()
		annotationText.type = TEXT
		annotationText.position = position
		annotationText.text = text
		layer.annotations.append(annotationText)
	
	def cleanNodeNamesInGlyph(self, glyph, nodeMarker):
		for thisLayer in glyph.layers:
			# reset node names:
			for thisPath in thisLayer.paths:
				for thisNode in thisPath.nodes:
					if thisNode.name:
						if nodeMarker in thisNode.name:
							thisNode.name = None
			
			# delete possible annotation circles:
			annotations = thisLayer.annotations
			if annotations:
				for i in range(len(annotations))[::-1]:
					thisAnnotation = annotations[i]
					if thisAnnotation.text and nodeMarker in thisAnnotation.text:
						del thisLayer.annotations[i]

	def ShortSegmentFinderMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Short Segment Finder' could not write preferences.")
			
			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			if Glyphs.defaults["com.mekkablue.ShortSegmentFinder.bringMacroWindowToFront"]:
				Glyphs.showMacroWindow()
				
			thisFont = Glyphs.font # frontmost font
			print("Short Segments Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			
			# query user settings:
			thisFont = Glyphs.font
			minLength = float(Glyphs.defaults["com.mekkablue.ShortSegmentFinder.minSegmentLength"])
			if Glyphs.defaults["com.mekkablue.ShortSegmentFinder.allGlyphs"]:
				glyphsToProbe = thisFont.glyphs
			else:
				glyphsToProbe = [l.parent for l in thisFont.selectedLayers]
			
			# lists for collecting affected and skipped glyphs:
			shortSegmentGlyphNames = []
			shortSegmentLayers = []
			skippedGlyphNames = []
			numOfGlyphs = len(glyphsToProbe)
			for index,thisGlyph in enumerate(glyphsToProbe):

				# update progress bar:
				self.w.progress.set( int(100*(float(index)/numOfGlyphs)) )
				if thisGlyph.export or not Glyphs.defaults["com.mekkablue.ShortSegmentFinder.exportingOnly"]:
					
					# clean node markers if necessary:
					if Glyphs.defaults["com.mekkablue.ShortSegmentFinder.markSegments"]:
						self.cleanNodeNamesInGlyph(thisGlyph, nodeMarker)
					
					# find segments in masters:
					if Glyphs.defaults["com.mekkablue.ShortSegmentFinder.findShortSegmentsInMasters"]:
						for currentLayer in thisGlyph.layers:
							
							# avoid potential troubles, just in case:
							if currentLayer is None:
								break
								
							# check if it is a master or special layer, otherwise ignore:
							if currentLayer.associatedMasterId == currentLayer.layerId or currentLayer.isSpecialLayer:
								shortSegments = self.segmentsInLayerShorterThan( currentLayer, minLength )
								if shortSegments:
									print(u"❌ %i short segment%s in %s, layer '%s'" % (
										len(shortSegments),
										"" if len(shortSegments) == 1 else "s",
										thisGlyph.name,
										currentLayer.name,
									))
									# collect name:
									shortSegmentGlyphNames.append(thisGlyph.name)
									# mark in canvas if required:
									if Glyphs.defaults["com.mekkablue.ShortSegmentFinder.markSegments"]:
										for shortSegment in shortSegments:
											middleOfSegment = self.segmentMiddle(shortSegment)
											if not middleOfSegment:
												print(u"⛔️ ERROR in %s, layer '%s'. Could not calculate center of segment:\n  %s" % (thisGlyph.name, currentLayer.name, repr(shortSegment)))
											else:
												annotationText = u"↙︎%s %.1fu" % ( nodeMarker, self.approxLengthOfSegment(shortSegment) )
												self.addAnnotationTextAtPosition( currentLayer, middleOfSegment, annotationText )
					
					# find segments in interpolations:
					else:
						for thisInstance in thisFont.instances:
							# define instance name
							instanceName = thisInstance.name.strip()
							familyName = thisInstance.customParameters["familyName"]
							if familyName:
								instanceName = "%s %s" % ( familyName, instanceName )
								
							# interpolate glyph for this instance:
							interpolatedLayer = self.glyphInterpolation( thisGlyph.name, thisInstance )
							if not interpolatedLayer:
								if Glyphs.defaults["com.mekkablue.ShortSegmentFinder.reportIncompatibilities"]:
									print(u"⚠️ %s: No paths in '%s'." % (thisGlyph.name, instanceName))
							else:
								interpolatedLayer.removeOverlap()
								shortSegments = self.segmentsInLayerShorterThan( interpolatedLayer, minLength )
							
								if shortSegments:
									print(u"❌ %i short segment%s in %s, instance '%s'" % (
										len(shortSegments),
										"" if len(shortSegments) == 1 else "s",
										thisGlyph.name,
										instanceName,
									))
								
									# collect name:
									shortSegmentGlyphNames.append(thisGlyph.name)
									# mark in canvas if required:
									if Glyphs.defaults["com.mekkablue.ShortSegmentFinder.markSegments"]:
										for shortSegment in shortSegments:
											middleOfSegment = self.segmentMiddle(shortSegment)
											if not middleOfSegment:
												print(u"⛔️ ERROR in %s, layer '%s'. Could not calculate center of segment:\n  %s" % (thisGlyph.name, currentLayer.name, repr(shortSegment)))
											else:
												annotationText = "%s %.0f (%s)" % ( nodeMarker, self.approxLengthOfSegment(shortSegment), instanceName )
												self.addAnnotationTextAtPosition( thisGlyph.layers[0], middleOfSegment, annotationText )
							
				else:
					skippedGlyphNames.append(thisGlyph.name)
			
			# report skipped glyphs:
			if skippedGlyphNames:
				print("\nSkipped %i glyphs:\n%s" % ( len(skippedGlyphNames), ", ".join(skippedGlyphNames) ))
			
			# turn on View > Show Annotations:
			if Glyphs.defaults["com.mekkablue.ShortSegmentFinder.markSegments"]:
				Glyphs.defaults["showAnnotations"] = 1
			
			# report affected glyphs:
			
			# found short segments in master layers > open these layers:
			if shortSegmentLayers:
				if Glyphs.defaults["com.mekkablue.ShortSegmentFinder.allGlyphs"]:
					shortSegmentTab = thisFont.newTab()
					shortSegmentTab.layers = shortSegmentLayers
				else:
					Message(
						title=u"⚠️ Short Segments Found", 
						message=u"Found segments shorter than %.1f units in %i layer%s in the selected glyph%s. Detailed report in Macro Window." % (
							minLength, 
							len(shortSegmentLayers),
							"" if len(shortSegmentLayers)==1 else "s",
							"" if len(glyphsToProbe)==1 else "s",
						), 
						OKButton=u"😲 OMG!"
					)
					
			# found short segments in interpolations > open the glyphs:
			elif shortSegmentGlyphNames:
				if Glyphs.defaults["com.mekkablue.ShortSegmentFinder.allGlyphs"]:
					tabText = "/"+"/".join( set(shortSegmentGlyphNames) )
					thisFont.newTab(tabText)
				else:
					Message(
						title=u"⚠️ Short Segments Found", 
						message=u"Found segments shorter than %.1f units in %i selected glyph%s." % (
							minLength, 
							len(shortSegmentGlyphNames),
							"" if len(shortSegmentGlyphNames)==1 else "s",
						), 
						OKButton=u"😲 OMG!"
					)
			else:
				Message(
					title=u"No Short Segments Found",
					message=u"Could not find any segments smaller than %.1f units in %s of %s. Congratulations." % (
						minLength, 
						"master layers" if Glyphs.defaults["com.mekkablue.ShortSegmentFinder.findShortSegmentsInMasters"] else "interpolations",
						thisFont.familyName,
						),
					OKButton=None,
				)
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Short Segments Finder Error: %s" % e)
			import traceback
			print(traceback.format_exc())

ShortSegmentFinder()