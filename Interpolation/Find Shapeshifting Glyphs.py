#MenuTitle: Find Shapeshifting Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Finds glyphs that change the number of paths while interpolating. Opens a new tab and reports to Macro Window.
"""

import vanilla

tempMarker = "###DELETEME###"

def glyphInterpolation( thisGlyphName, thisInstance ):
	"""
	Yields a layer.
	"""
	try:
		# calculate interpolation:
		# interpolatedFont = thisInstance.interpolatedFont # too slow still
		interpolatedFont = thisInstance.pyobjc_instanceMethods.interpolatedFont()
		interpolatedLayer = interpolatedFont.glyphForName_(thisGlyphName).layers[0]
		
		# if interpolatedLayer.components:
		# 	interpolatedLayer.decomposeComponents()
		
		# round to grid if necessary:
		if interpolatedLayer.paths:
			if interpolatedFont.gridLength == 1.0:
				interpolatedLayer.roundCoordinates()
			return interpolatedLayer
		else:
			return interpolatedLayer
		
	except:
		import traceback
		print traceback.format_exc()
		return None

class FindShapeshiftingGlyphs( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 290
		windowHeight = 250
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Find Shapeshifting Glyphs", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.FindShapeshiftingGlyphs.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 28), u"Reports glyphs that change number of cw/ccw paths (‘shapeshift’) in interpolation.", sizeStyle='small', selectable=True )
		linePos += lineHeight*1.7
		
		self.w.text_1 = vanilla.TextBox( (inset, linePos+2, 85, 14), "Count paths in", sizeStyle='small' )
		self.w.checkInstances = vanilla.PopUpButton( (inset+85, linePos, -inset, 17), ("constructed instances midway between masters", "all active instances in font", "all active and inactive instances in font"), callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.alsoCheckMasters = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Add masters as instances", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.onlyCheckSelection = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Limit to selected glyphs (otherwise all glyphs)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.ignoreGlyphsWithoutPaths = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Ignore glyphs without paths", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.ignoreNonexportingGlyphs = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Ignore glyphs that do not export", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.openTab = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Open found shapeshifters in a new tab", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Find", sizeStyle='regular', callback=self.FindShapeshiftingGlyphsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Find Shapeshifting Glyphs' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.checkInstances"] = self.w.checkInstances.get()
			Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.alsoCheckMasters"] = self.w.alsoCheckMasters.get()
			Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.onlyCheckSelection"] = self.w.onlyCheckSelection.get()
			Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.ignoreGlyphsWithoutPaths"] = self.w.ignoreGlyphsWithoutPaths.get()
			Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.ignoreNonexportingGlyphs"] = self.w.ignoreNonexportingGlyphs.get()
			Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.openTab"] = self.w.openTab.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.FindShapeshiftingGlyphs.checkInstances", 0)
			Glyphs.registerDefault("com.mekkablue.FindShapeshiftingGlyphs.alsoCheckMasters", 0)
			Glyphs.registerDefault("com.mekkablue.FindShapeshiftingGlyphs.onlyCheckSelection", 0)
			Glyphs.registerDefault("com.mekkablue.FindShapeshiftingGlyphs.ignoreGlyphsWithoutPaths", 0)
			Glyphs.registerDefault("com.mekkablue.FindShapeshiftingGlyphs.ignoreNonexportingGlyphs", 0)
			Glyphs.registerDefault("com.mekkablue.FindShapeshiftingGlyphs.openTab", 0)
			self.w.checkInstances.set( Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.checkInstances"] )
			self.w.alsoCheckMasters.set( Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.alsoCheckMasters"] )
			self.w.onlyCheckSelection.set( Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.onlyCheckSelection"] )
			self.w.ignoreGlyphsWithoutPaths.set( Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.ignoreGlyphsWithoutPaths"] )
			self.w.ignoreNonexportingGlyphs.set( Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.ignoreNonexportingGlyphs"] )
			self.w.openTab.set( Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.openTab"] )
		except:
			return False
			
		return True
	
	def generateTestInstance(self, thisFont, indexMasterDict):
		numOfMasters = len(indexMasterDict)
		significance = 1.0/numOfMasters
		interpolationDict = {}
		sortedIndexes = sorted(indexMasterDict.keys())
		for i in sortedIndexes:
			master = indexMasterDict[i]
			interpolationDict[master.id] = significance
			
		testInstance = GSInstance()
		testInstance.active = False
		testInstance.name = "%s-%s" % ("-".join([str(i) for i in sortedIndexes]),tempMarker)
		testInstance.setManualInterpolation_(1)
		testInstance.setInstanceInterpolations_(interpolationDict)
		
		disabledMasters = []
		for m in range(len(thisFont.masters)):
			if not m in sortedIndexes:
				disabledMasters.append(thisFont.masters[m].name)
		if disabledMasters:
			disabledMasters = tuple(disabledMasters)
			testInstance.customParameters["Disable Masters"] = disabledMasters

		testInstance.setFont_(thisFont)
		return testInstance
		
	
	def addMasterInstances(self, thisFont, keepExisting=False):
		for i,master in enumerate(thisFont.masters):
			testInstance = self.generateTestInstance( thisFont, { i: master } )
			self.instances.append(testInstance)
	
	def addHalfWayInstances(self, thisFont, keepExisting=False):
		numOfMasters = len(thisFont.masters)
		r = range(numOfMasters)
		for i in r[:-1]:
			for j in r[i+1:]:
				master1 = thisFont.masters[i]
				master2 = thisFont.masters[j]
				testInstance = self.generateTestInstance( thisFont, { i: master1, j: master2 } )
				self.instances.append(testInstance)
		
		
	def FindShapeshiftingGlyphsMain( self, sender ):
		try:
			# query settings:
			thisFont = Glyphs.font
			checkInstances = Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.checkInstances"]
			alsoCheckMasters = Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.alsoCheckMasters"]
			onlyCheckSelection = Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.onlyCheckSelection"]
			ignoreGlyphsWithoutPaths = Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.ignoreGlyphsWithoutPaths"]
			ignoreNonexportingGlyphs = Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.ignoreNonexportingGlyphs"]
			openTab = Glyphs.defaults["com.mekkablue.FindShapeshiftingGlyphs.openTab"]

			# Clear macro window log:
			Glyphs.clearLog()
			print "Find Shapeshifters in %s" % thisFont.familyName
			print "Path: %s" % thisFont.filepath
			print
			
			# determine glyphs to be checked:
			if onlyCheckSelection:
				glyphs = [l.glyph() for l in thisFont.selectedLayers if l.glyph()]
			else:
				glyphs = thisFont.glyphs
			glyphNamesToBeChecked = [
				g.name for g in glyphs 
				if (g.export or not ignoreNonexportingGlyphs)
				and (len(g.layers[0].paths)>0 or not ignoreGlyphsWithoutPaths)
				]
			print "Checking %i glyph%s:\n%s\n" % ( 
				len(glyphNamesToBeChecked), 
				"" if len(glyphNamesToBeChecked)==1 else "s",
				", ".join(glyphNamesToBeChecked),
				)
			
			# determine the instances to calculate:
			self.instances = []
			# 0: constructed midway instances
			if checkInstances == 0:
				self.addHalfWayInstances( thisFont )
			# 1: all active instances in font
			elif checkInstances == 1:
				self.instances = [i for i in thisFont.instances if i.active]
			# 2: all active and inactive instances in font
			else:
				self.instances = thisFont.instances
			# add masters as instances if required:
			if alsoCheckMasters:
				self.addMasterInstances( thisFont )
			# report:
			print "Calculating %i instance interpolations.\n" % len(self.instances)
			for i in self.instances:
				print "- %s:" % i.name
				for key in i.instanceInterpolations:
					print "  %s: %.3f" % (thisFont.masters[key].name, i.instanceInterpolations[key])
			print
			
			# iterate through glyphs:
			affectedGlyphNames = []
			numOfGlyphs = len(glyphNamesToBeChecked)
			for i,thisGlyphName in enumerate(glyphNamesToBeChecked):
				# tick the progress bar:
				self.w.progress.set( int(100*(float(i)/numOfGlyphs)) )
				
				# collect number of paths for every instance:
				pathCounts = []
				for thisInstance in self.instances:
					interpolation = glyphInterpolation( thisGlyphName, thisInstance )
					if interpolation:
						# only decompose and remove overlap when necessary, should speed things up:
						if interpolation.components:
							interpolation.decomposeComponents()
						if len(interpolation.paths) > 1:
							interpolation.removeOverlap()
						countOfCWPaths = len([p for p in interpolation.paths if p.direction == 1])
						countOfCCWPaths = len(interpolation.paths) - countOfCWPaths
						pathCounts.append( (countOfCWPaths,countOfCCWPaths), )
					else:
						print "ERROR: %s has no interpolation for '%s'." % (thisGlyphName, thisInstance.name)
				
				# see if path counts changed:
				pathCounts = set(pathCounts)
				if len(pathCounts) > 1:
					sortedPathCounts = [u"%i⟳+%i⟲"%(pair[0],pair[1]) for pair in sorted(pathCounts, key=lambda count: count[0])]
					print u"%s: changing between %s paths." % ( thisGlyphName, u", ".join(sortedPathCounts) )
					affectedGlyphNames.append(thisGlyphName)
			
			# report:
			if affectedGlyphNames:
				if openTab:
					tabString = "/"+"/".join(affectedGlyphNames)
					thisFont.newTab(tabString)
				else:
					# brings macro window to front:
					Glyphs.showMacroWindow()
			else:
				Message(
					title="No Shapeshifting Glyphs", 
					message="Among the specified glyphs and interpolations, no changes of path numbers could be found.", 
					OKButton=u"🍻Cheers!",
				)
			
			if not self.SavePreferences( self ):
				print "Note: 'Find Shapeshifting Glyphs' could not write preferences."
			
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Find Shapeshifting Glyphs Error: %s" % e
			import traceback
			print traceback.format_exc()

FindShapeshiftingGlyphs()