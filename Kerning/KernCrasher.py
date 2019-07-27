#MenuTitle: KernCrasher
# -*- coding: utf-8 -*-
__doc__="""
Opens a new tab with Kerning Combos that crash in the current fontmaster.
"""

import vanilla
from timeit import default_timer as timer

intervalList = (1,3,5,10,20)
categoryList = (
	"Letter:Uppercase",
	"Letter:Lowercase",
	"Letter:Smallcaps",
	"Punctuation",
	"Symbol:Currency",
	"Symbol:Math",
	"Symbol:Other",
	"Symbol:Arrow",
	"Number:Decimal Digit",
	"Number:Small",
	"Number:Fraction",
)

class KernCrasher( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 290
		windowHeight = 270
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"KernCrasher", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.KernCrasher.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15-1, 12+2, -15, 14), "Open tab with kern collisions in current master:", sizeStyle='small' )

		self.w.text_21 = vanilla.TextBox( (15-1, 32+2, 42, 14), "Script:", sizeStyle='small' )
		self.w.popupScript = vanilla.PopUpButton( (15+42, 32, 80, 17), ["latin","cyrillic","greek"], callback=self.SavePreferences, sizeStyle='small' )
		
		self.w.text_22 = vanilla.TextBox( (140, 32+2, 150, 14), "Min distance:", sizeStyle='small' )
		self.w.minDistance = vanilla.EditText( (220, 32-1, -15, 19), "10", sizeStyle='small')
		
		self.w.text_speed = vanilla.TextBox( (15-1, 52+2, 42, 14), "Speed:", sizeStyle='small' )
		self.w.popupSpeed = vanilla.PopUpButton( (15+42, 52, 80, 17), ["very slow","slow","medium","fast","very fast"], callback=self.SavePreferences, sizeStyle='small' )
		intervalIndex = Glyphs.defaults["com.mekkablue.KernCrasher.popupSpeed"]
		if intervalIndex is None:
			intervalIndex = 0
		self.w.text_speedExplanation = vanilla.TextBox( (140, 52+2, -15, 14), "Measuring every %i units."%intervalList[intervalIndex], sizeStyle='small' )
		
		self.w.text_3 = vanilla.TextBox( (15-1, 20+52+2, 90, 14), "Left Category:", sizeStyle='small' )
		self.w.popupLeftCat = vanilla.PopUpButton( (15+90, 20+52, -15, 17), categoryList, callback=self.SavePreferences, sizeStyle='small' )

		self.w.text_4 = vanilla.TextBox( (15-1, 20+72+2, 90, 14), "Right Category:", sizeStyle='small' )
		self.w.popupRightCat = vanilla.PopUpButton( (15+90, 20+72, -15, 17), categoryList, callback=self.SavePreferences, sizeStyle='small' )
		
		self.w.text_5 = vanilla.TextBox( (15-1, 20+92+2, 160, 14), "Exclude glyphs containing:", sizeStyle='small' )
		self.w.excludeSuffixes = vanilla.EditText( (170, 20+92, -15, 19), ".locl, .alt, .sups, .sinf, .tf, .tosf, Ldot, ldot, Jacute, jacute", callback=self.SavePreferences, sizeStyle='small')

		self.w.text_6 = vanilla.TextBox( (15-1, 20+112+2, 160, 14), "Ignore height intervals:", sizeStyle='small' )
		self.w.ignoreIntervals = vanilla.EditText( (170, 20+112, -15, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.ignoreIntervals.getNSTextField().setPlaceholderString_("200:300, 400:370, -200:-150")

		self.w.excludeNonExporting = vanilla.CheckBox((15-1, 20+132+2, -15, 17), "Exclude non-exporting glyphs", value=True, sizeStyle='small', callback=self.SavePreferences )
		self.w.reportCrashesInMacroWindow = vanilla.CheckBox((15-1, 20+152+2, -15, 17), "Also report in Macro Window (a few seconds slower)", value=False, sizeStyle='small', callback=self.SavePreferences )
		
		# Percentage:
		self.w.bar = vanilla.ProgressBar((15-1, 20+172+2, -15, 16))
		
		#self.w.percentage = vanilla.TextBox( (15-1, -30, -100-15, -15), "", sizeStyle='small' )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-100-15, -20-15, -15, -15), "Open Tab", sizeStyle='regular', callback=self.KernCrasherMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'KernCrasher' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.KernCrasher.popupScript"] = self.w.popupScript.get()
			Glyphs.defaults["com.mekkablue.KernCrasher.popupSpeed"] = self.w.popupSpeed.get()
			Glyphs.defaults["com.mekkablue.KernCrasher.popupLeftCat"] = self.w.popupLeftCat.get()
			Glyphs.defaults["com.mekkablue.KernCrasher.popupRightCat"] = self.w.popupRightCat.get()
			Glyphs.defaults["com.mekkablue.KernCrasher.excludeSuffixes"] = self.w.excludeSuffixes.get()
			Glyphs.defaults["com.mekkablue.KernCrasher.excludeNonExporting"] = self.w.excludeNonExporting.get()
			Glyphs.defaults["com.mekkablue.KernCrasher.minDistance"] = self.w.minDistance.get()
			Glyphs.defaults["com.mekkablue.KernCrasher.reportCrashesInMacroWindow"] = self.w.reportCrashesInMacroWindow.get()
			Glyphs.defaults["com.mekkablue.KernCrasher.ignoreIntervals"] = self.w.ignoreIntervals.get()
		except Exception as e:
			return False
		
		# update speed explanation:
		if sender == self.w.popupSpeed:
			intervalIndex = Glyphs.defaults["com.mekkablue.KernCrasher.popupSpeed"]
			if intervalIndex is None:
				intervalIndex = 0
			self.w.text_speedExplanation.set( "Measuring every %i units." % intervalList[intervalIndex] )

		return True

	def LoadPreferences( self ):
		try:
			NSUserDefaults.standardUserDefaults().registerDefaults_(
				{
					"com.mekkablue.KernCrasher.minDistance": "0",
					"com.mekkablue.KernCrasher.popupScript": "0",
					"com.mekkablue.KernCrasher.popupSpeed": "0",
					"com.mekkablue.KernCrasher.popupLeftCat": "0",
					"com.mekkablue.KernCrasher.popupRightCat": "0",
					"com.mekkablue.KernCrasher.excludeSuffixes": ".locl, .alt, .sups, .sinf, .tf, .tosf, Ldot, ldot, Jacute, jacute",
					"com.mekkablue.KernCrasher.excludeNonExporting": "1",
					"com.mekkablue.KernCrasher.reportCrashesInMacroWindow": "0",
					"com.mekkablue.KernCrasher.ignoreIntervals": "",
				}
			)
			self.w.minDistance.set( Glyphs.defaults["com.mekkablue.KernCrasher.minDistance"] )
			self.w.popupScript.set( Glyphs.defaults["com.mekkablue.KernCrasher.popupScript"] )
			self.w.popupSpeed.set( Glyphs.defaults["com.mekkablue.KernCrasher.popupSpeed"] )
			self.w.popupLeftCat.set( Glyphs.defaults["com.mekkablue.KernCrasher.popupLeftCat"] )
			self.w.popupRightCat.set( Glyphs.defaults["com.mekkablue.KernCrasher.popupRightCat"] )
			self.w.excludeSuffixes.set( Glyphs.defaults["com.mekkablue.KernCrasher.excludeSuffixes"] )
			self.w.excludeNonExporting.set( Glyphs.defaults["com.mekkablue.KernCrasher.excludeNonExporting"] )
			self.w.reportCrashesInMacroWindow.set( Glyphs.defaults["com.mekkablue.KernCrasher.reportCrashesInMacroWindow"] )
			self.w.ignoreIntervals.set( Glyphs.defaults["com.mekkablue.KernCrasher.ignoreIntervals"] )
		except:
			return False
			
		return True
	
	def nameUntilFirstPeriod( self, glyphName ):
		if not "." in glyphName:
			return glyphName
		else:
			offset = glyphName.find(".")
			return glyphName[:offset]
	
	def effectiveKerning( self, leftGlyphName, rightGlyphName, thisFont, thisFontMasterID ):
		leftLayer = thisFont.glyphs[leftGlyphName].layers[thisFontMasterID]
		rightLayer = thisFont.glyphs[rightGlyphName].layers[thisFontMasterID]
		effectiveKerning = leftLayer.rightKerningForLayer_( rightLayer )
		if effectiveKerning < NSNotFound:
			return effectiveKerning
		else:
			return 0.0
	
	def listOfNamesForCategories( self, thisFont, requiredCategory, requiredSubCategory, requiredScript, excludedGlyphNameParts, excludeNonExporting ):
		nameList = []
		for thisGlyph in thisFont.glyphs:
			thisScript = thisGlyph.script
			glyphName = thisGlyph.name
			nameIsOK = True
			
			if excludedGlyphNameParts:
				for thisNamePart in excludedGlyphNameParts:
					nameIsOK = nameIsOK and not thisNamePart in glyphName
			
			if nameIsOK and (thisGlyph.export or not excludeNonExporting):
					if thisScript == None or thisScript == requiredScript:
						if thisGlyph.category == requiredCategory:
							if requiredSubCategory:
								if thisGlyph.subCategory == requiredSubCategory:
									nameList.append( glyphName )
							else:
								nameList.append( glyphName )
		return nameList
		
	def splitString( self, string, delimiter=":", minimum=2 ):
		# split string into a list:
		returnList = string.split(delimiter)
		
		# remove trailing spaces:
		for i in range(len(returnList)):
			returnList[i] = returnList[i].strip()
		
		# if necessary fill up with None:
		while len(returnList) < minimum:
			returnList.append(None)
		
		if returnList == [""]:
			return None
			
		return returnList
	
	def measureLayerAtHeightFromLeftOrRight( self, thisLayer, height, leftSide=True ):
		try:
			if leftSide:
				measurement = thisLayer.lsbAtHeight_(height)
			else:
				measurement = thisLayer.rsbAtHeight_(height)
			if measurement < NSNotFound:
				return measurement
			else:
				return None
		except:
			return None
	
	def isHeightInIntervals(self, height, ignoreIntervals):
		if ignoreIntervals:
			for interval in ignoreIntervals:
				if height <= interval[1] and height >= interval[0]:
					return True
		return False
	
	def minDistanceBetweenTwoLayers( self, leftLayer, rightLayer, interval=5.0, kerning=0.0, report=False, ignoreIntervals=[] ):
		# correction = leftLayer.RSB+rightLayer.LSB
		topY = min( leftLayer.bounds.origin.y+leftLayer.bounds.size.height, rightLayer.bounds.origin.y+rightLayer.bounds.size.height )
		bottomY = max( leftLayer.bounds.origin.y, rightLayer.bounds.origin.y )
		distance = topY - bottomY
		minDist = None
		for i in range(int(distance//interval)):
			height = bottomY + i * interval
			if not self.isHeightInIntervals(height, ignoreIntervals) or not ignoreIntervals:
				left = self.measureLayerAtHeightFromLeftOrRight( leftLayer, height, leftSide=False )
				right = self.measureLayerAtHeightFromLeftOrRight( rightLayer, height, leftSide=True )
				try: # avoid gaps like in i or j
					total = left+right+kerning # +correction
					if minDist == None or minDist > total:
						minDist = total
				except:
					pass
		return minDist
		
	def queryPrefs( self ):
		script = self.w.popupScript.getItems()[ Glyphs.defaults["com.mekkablue.KernCrasher.popupScript"] ]
		firstCategory, firstSubCategory   = self.splitString( self.w.popupLeftCat.getItems()[ Glyphs.defaults["com.mekkablue.KernCrasher.popupLeftCat"] ] )
		secondCategory, secondSubCategory = self.splitString( self.w.popupRightCat.getItems()[ Glyphs.defaults["com.mekkablue.KernCrasher.popupRightCat"] ] )
		return script, firstCategory, firstSubCategory, secondCategory, secondSubCategory
	
	def sortedIntervalsFromString(self, intervals=""):
		ignoreIntervals = []
		if intervals:
			for interval in intervals.split(","):
				if interval.find(":") != -1:
					interval = interval.strip()
					try:
						intervalTuple = tuple(sorted([
							int(interval.split(":")[0].strip()),
							int(interval.split(":")[1].strip()),
						]))
						ignoreIntervals.append(intervalTuple)
					except:
						print "Warning: could not convert '%s' into a number interval." % interval.strip()
						pass
				else:
					print "Warning: '%s' is not an interval (missing colon)" % interval.strip()

		return ignoreIntervals
	
	
	def KernCrasherMain( self, sender ):
		try:
			# query frontmost fontmaster:
			thisFont = Glyphs.font
			thisFontMaster = thisFont.selectedFontMaster
			thisFontMasterID = thisFontMaster.id
			
			# reset progress bar:
			self.w.bar.set(0)
			
			# start taking time:
			start = timer()

			# start reporting to macro window:
			if Glyphs.defaults["com.mekkablue.KernCrasher.reportCrashesInMacroWindow"]:
				Glyphs.clearLog()
				print "KernCrasher Report for %s, master %s:\n" % (thisFont.familyName, thisFontMaster.name)
			
			# query user input:
			script, firstCategory, firstSubCategory, secondCategory, secondSubCategory = self.queryPrefs()
			step = intervalList[ Glyphs.defaults["com.mekkablue.KernCrasher.popupSpeed"] ]
			excludedGlyphNameParts = self.splitString( Glyphs.defaults["com.mekkablue.KernCrasher.excludeSuffixes"], delimiter=",", minimum=0 )
			excludeNonExporting = bool( Glyphs.defaults["com.mekkablue.KernCrasher.excludeNonExporting"] )
			minDistance = 0.0
			ignoreIntervals = self.sortedIntervalsFromString( Glyphs.defaults["com.mekkablue.KernCrasher.ignoreIntervals"] )
			try:
				minDistance = float( Glyphs.defaults["com.mekkablue.KernCrasher.minDistance"] )
			except Exception as e:
				print "Warning: Could not read min distance entry. Will default to 0.\n%s" % e
				import traceback
				print traceback.format_exc()
				print

			# save prefs
			if not self.SavePreferences(None):
				print "Note: KernCrasher could not write preferences."
			
			# get list of glyph names:
			firstList = self.listOfNamesForCategories( thisFont, firstCategory, firstSubCategory, script, excludedGlyphNameParts, excludeNonExporting )
			secondList = self.listOfNamesForCategories( thisFont, secondCategory, secondSubCategory, script, excludedGlyphNameParts, excludeNonExporting )

			if Glyphs.defaults["com.mekkablue.KernCrasher.reportCrashesInMacroWindow"]:
				print "Minimum Distance: %i\n" % minDistance
				print "Left glyphs:\n%s\n" % ", ".join(firstList)
				print "Right glyphs:\n%s\n" % ", ".join(secondList)

			tabString = "\n"
			crashCount = 0
			numOfGlyphs = len(firstList)
			for index in range(numOfGlyphs):
				# update progress bar:
				self.w.bar.set( int(100*(float(index)/numOfGlyphs)) )
				# determine left glyph:
				firstGlyphName = firstList[index]
				leftLayer = thisFont.glyphs[firstGlyphName].layers[thisFontMasterID]
				
				# cycle through right glyphs:
				for secondGlyphName in secondList:
					rightLayer = thisFont.glyphs[secondGlyphName].layers[thisFontMasterID]
					kerning = self.effectiveKerning( firstGlyphName, secondGlyphName, thisFont, thisFontMasterID )
					distanceBetweenShapes = self.minDistanceBetweenTwoLayers( leftLayer, rightLayer, interval=step, kerning=kerning, report=False, ignoreIntervals=ignoreIntervals )
					if (not distanceBetweenShapes is None) and (distanceBetweenShapes < minDistance):
						crashCount += 1
						tabString += "/%s/%s/space" % ( firstGlyphName, secondGlyphName )
						if Glyphs.defaults["com.mekkablue.KernCrasher.reportCrashesInMacroWindow"]:
							print "- %s %s: %i" % ( firstGlyphName, secondGlyphName, distanceBetweenShapes )
				tabString += "\n"
				
			# clean up the tab string:
			tabString = tabString[:-6].replace("/space\n", "\n")
			while "\n\n" in tabString:
				tabString = tabString.replace("\n\n", "\n")
			tabString = tabString[1:]
			
			# update progress bar:
			self.w.bar.set( 100 )
			
			# take time:
			end = timer()
			seconds = end - start
			if seconds > 60.0:
				timereport = "%i:%02i minutes" % ( seconds//60, seconds%60 )
			elif seconds < 1.0:
				timereport = "%.2f seconds" % seconds
			elif seconds < 20.0:
				timereport = "%.1f seconds" % seconds
			else:
				timereport = "%i seconds" % seconds
			
			# open new Edit tab:
			if tabString:
				if len(tabString) > 40:
					# disable reporters (avoid slowdown)
					Glyphs.defaults["visibleReporters"] = None
				report = '%i kerning crashes have been found. Time elapsed: %s.' % (crashCount, timereport)
				thisFont.newTab( tabString )
			# or report that nothing was found:
			else:
				report = 'No collisions found. Time elapsed: %s. Congrats!' % timereport
			
			# Notification:
			notificationTitle = "KernCrasher: %s (%s)" % (thisFont.familyName, thisFontMaster.name)
			Glyphs.showNotification( notificationTitle, report )
			
			# Report in Macro Window:
			if Glyphs.defaults["com.mekkablue.KernCrasher.reportCrashesInMacroWindow"]:
				print report
				Glyphs.showMacroWindow()

		except Exception as e:
			print "KernCrasher Error: %s" % e
			import traceback
			print traceback.format_exc()

KernCrasher()
