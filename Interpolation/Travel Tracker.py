#MenuTitle: Travel Tracker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Finds interpolations in which points travel more than they should, i.e., can find wrongly hooked-up asterisks and slashes.
"""

import vanilla

class TravelTracker( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 430
		windowHeight = 190
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Travel Tracker", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.TravelTracker.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 28), u"Finds master-compatible glyphs with nodes that travel more than they should because they interpolate with a wrong node in the other master(s).", sizeStyle='small', selectable=True )
		linePos += lineHeight*1.8
		
		self.w.travelPercentageText = vanilla.TextBox( (inset, linePos+2.5, 190, 14), u"Acceptable travel ratio in percent:", sizeStyle='small', selectable=True )
		self.w.travelPercentage = vanilla.EditText( (inset+190, linePos, -inset, 19), "50", callback=self.SavePreferences, sizeStyle='small' )
		self.w.travelPercentage.getNSTextField().setToolTip_(u"Anything above 50% is suspicious in a weight interpolation, and above 70% in a width interpolation. (100% is the diagonal of the bounding box of the path the node belongs to.)")
		linePos += lineHeight
		
		self.w.includeNonExporting = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include non-exporting glyphs (recommended)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeNonExporting.getNSButton().setToolTip_(u"Important if you are using non-exporting glyphs as components inside others, e.g., the slash in the oslash.")
		linePos += lineHeight

		self.w.normalizePathPosition = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Normalize path origin (recommended)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.normalizePathPosition.getNSButton().setToolTip_(u"Calculates node travel distances as if every path’s origin point were x=0, y=0.")
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Find", sizeStyle='regular', callback=self.TravelTrackerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Travel Tracker' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.TravelTracker.travelPercentage"] = self.w.travelPercentage.get()
			Glyphs.defaults["com.mekkablue.TravelTracker.includeNonExporting"] = self.w.includeNonExporting.get()
			Glyphs.defaults["com.mekkablue.TravelTracker.normalizePathPosition"] = self.w.normalizePathPosition.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.TravelTracker.travelPercentage", "50")
			Glyphs.registerDefault("com.mekkablue.TravelTracker.includeNonExporting", 1)
			Glyphs.registerDefault("com.mekkablue.TravelTracker.normalizePathPosition", 1)
			self.w.travelPercentage.set( Glyphs.defaults["com.mekkablue.TravelTracker.travelPercentage"] )
			self.w.includeNonExporting.set( Glyphs.defaults["com.mekkablue.TravelTracker.includeNonExporting"] )
			self.w.normalizePathPosition.set( Glyphs.defaults["com.mekkablue.TravelTracker.normalizePathPosition"] )
		except:
			return False
			
		return True
	
	def maxBoundsOfPaths(self, p1, p2):
		w = max(p1.bounds.size.width, p2.bounds.size.width)
		h = max(p1.bounds.size.height, p2.bounds.size.height)
		#print "\n   path size: %i %i" % (w,h)
		return w, h
	
	def diagonalOfMaxPathBounds(self, p1, p2):
		w, h = self.maxBoundsOfPaths(p1, p2)
		boundsHypothenuse = (w**2+h**2)**0.5
		#print "   diagonal: %i" % boundsHypothenuse
		return boundsHypothenuse
	
	def maxNodeTravelRatioForLayers( self, layer, otherLayer ):
		maxTravelRatio = 0.0
		for pi,p1 in enumerate(layer.paths):
			maxNodeTravel=0.0
			p2 = otherLayer.paths[pi]
			p1offset = p1.bounds.origin
			p2offset = p2.bounds.origin
			maxPossibleTravel = self.diagonalOfMaxPathBounds(p1,p2)
			if maxPossibleTravel > 0.0:
				for ni,n1 in enumerate(p1.nodes):
					n2 = p2.nodes[ni]
					if Glyphs.defaults["com.mekkablue.TravelTracker.normalizePathPosition"]:
						n1pos = subtractPoints(n1.position,p1offset)
						n2pos = subtractPoints(n2.position,p2offset)
					else:
						n1pos = n1.position
						n2pos = n2.position
					nodeDistance = distance(n1pos,n2pos)
					maxNodeTravel = max( maxNodeTravel, nodeDistance )
					# print "   path %i, node %i: %i,%i > %i,%i = %.1f" % (pi, ni, n1pos.x, n1pos.y, n2pos.x, n2pos.y, nodeDistance)
				thisPathTravelRatio = maxNodeTravel/maxPossibleTravel
				maxTravelRatio = max( maxTravelRatio, thisPathTravelRatio )
		return maxTravelRatio

	def relevantLayersOfGlyph(self, glyph):
		relevantLayers = [
			l for l in glyph.layers 
			if (l.layerId==l.associatedMasterId or l.isSpecialLayer)
			and l.paths
		]
		return relevantLayers
		
	def hasInterpolatingPaths(self, glyph):
		relevantLayers = self.relevantLayersOfGlyph(glyph)
		if len(relevantLayers) < 2:
			return False
		else:
			return True
			
	def maxNodeTravelRatioForGlyph(self, relevantGlyph):
		maxTravelRatio = 0.0
		relevantLayers = self.relevantLayersOfGlyph(relevantGlyph)
		numOfLayers = len(relevantLayers)
		for i in range(numOfLayers-1):
			firstLayer = relevantLayers[i]
			for j in range(i+1,numOfLayers):
				secondLayer = relevantLayers[j]
				if relevantGlyph.mastersCompatibleForLayers_((firstLayer, secondLayer)):
					thisTravelRatio = self.maxNodeTravelRatioForLayers(firstLayer, secondLayer)
					maxTravelRatio = max( maxTravelRatio, thisTravelRatio )
		return maxTravelRatio

	def TravelTrackerMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Travel Tracker' could not write preferences.")
			
			travelPercentage = float(Glyphs.defaults["com.mekkablue.TravelTracker.travelPercentage"])
			acceptableTravelRatio = travelPercentage/100.0
			includeNonExporting = bool(Glyphs.defaults["com.mekkablue.TravelTracker.includeNonExporting"])
			
			thisFont = Glyphs.font # frontmost font
			
			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			print("Travel Tracker Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			
			relevantGlyphs = [
				g for g in thisFont.glyphs 
				if (g.mastersCompatible and self.hasInterpolatingPaths(g))
				and (includeNonExporting or g.export)
			]
			
			numOfGlyphs = float(len(relevantGlyphs)) # float for calculating the progress indicator below
			print("Examining %i interpolating glyphs..." % numOfGlyphs)
			print()
			
			affectedGlyphInfos = []
			for i,relevantGlyph in enumerate(relevantGlyphs):
				# push progress bar 1 tick further:
				self.w.progress.set(int(i/numOfGlyphs*100.0))
				
				travelRatioInThisGlyph = self.maxNodeTravelRatioForGlyph(relevantGlyph)
				if not travelRatioInThisGlyph > acceptableTravelRatio:
					print(u"✅ Max node travel % 3i%% in: %s" % ( int(travelRatioInThisGlyph*100), relevantGlyph.name ))
				else:
					print(u"❌ Node traveling % 3i%% in: %s" % ( int(travelRatioInThisGlyph*100), relevantGlyph.name ))
					affectedGlyphInfos.append( (relevantGlyph.name,travelRatioInThisGlyph), )
			
			# last one finished, progress bar = 100:
			self.w.progress.set(100)
			
			if not affectedGlyphInfos:
				Message(
					title="No affected glyph found",
					message="No glyph found where a node travels more than %i%% of its path bounds diagonal. Congratulations!" % travelPercentage, 
					OKButton=u"🥂 Cheers!")
			else:
				# report in macro window
				Glyphs.showMacroWindow()
				sortedGlyphInfos = sorted( affectedGlyphInfos, key = lambda thisListItem: -thisListItem[1] )
				print()
				print("Affected glyphs:")
				for glyphInfo in sortedGlyphInfos:
					percentage = glyphInfo[1]*100
					glyphName = glyphInfo[0]
					print(u"   % 3i%% %s" % (percentage, glyphName))
				
				# open tab:
				affectedGlyphNames = [gi[0] for gi in sortedGlyphInfos]
				tabText = "/"+"/".join(affectedGlyphNames)
				thisFont.newTab(tabText)
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(u"Travel Tracker Error: %s" % e)
			import traceback
			print(traceback.format_exc())

TravelTracker()