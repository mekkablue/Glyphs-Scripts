#MenuTitle: Auto Bumper
# -*- coding: utf-8 -*-
__doc__="""
Specify a minimum distance, left and right glyphs, and Auto Bumper will add the minimum necessary kerning for the current master.
"""

import vanilla
from timeit import default_timer as timer
from kernanalysis import *

defaultStrings = u"""
iíĭǐîïịìỉīįĩjĵ
ÍǏÎÏİÌỈĪĨ # UPPERCASE
/iacute.sc/icaron.sc/icircumflex.sc/idieresis.sc/idotaccent.sc/igrave.sc/ihookabove.sc/imacron.sc/itilde.sc
FTKVWY # TOP RIGHT
f
/lslash
bhlkþ
rtkvwxyz

abcdefghijklmnopqrstuvwxyzßð
ABCDEFGHIJKLMNOPQRSTUVWXYZẞÞ
/a.sc/b.sc/c.sc/d.sc/e.sc/f.sc/g.sc/h.sc/i.sc/j.sc/k.sc/l.sc/m.sc/n.sc/o.sc/p.sc/q.sc/r.sc/s.sc/t.sc/u.sc/v.sc/w.sc/x.sc/y.sc/z.sc/germandbls.sc/thorn.sc

/Ohorn/Uhorn #VIETNAMESE
/ohorn/uhorn #VIETNAMESE
/ohorn.sc/uhorn.sc #VIETNAMESE
/i/iacute/idotbelow/igrave/ihookabove/itilde #VIETNAMESE
/i.sc/iacute.sc/idotbelow.sc/igrave.sc/ihookabove.sc/itilde.sc #VIETNAMESE

({[„“”
„“”]})
/parenleft.sc/braceleft.sc/bracketleft.sc
/parenright.sc/braceright.sc/bracketright.sc

/quotesinglbase/quotedblbase/quotedblleft/quotedblright/quoteleft/quoteright/quotedbl/quotesingle


/a.sc/aogonek.sc/ae.sc/b.sc/c.sc/d.sc/e.sc/f.sc/g.sc/h.sc/i.sc/j.sc/k.sc/l.sc/m.sc/n.sc/eng.sc/o.sc/oe.sc/p.sc/thorn.sc/q.sc/r.sc/s.sc/germandbls.sc/t.sc/u.sc/v.sc/w.sc/x.sc/y.sc/z.sc
/slash
/iacute.sc/icaron.sc/icircumflex.sc/idieresis.sc/idotaccent.sc/igrave.sc/imacron.sc/iogonek.sc/itilde.sc/icaron.sc

ĄĘĮ # OGONEK
gjpy # DESCENDER

AKLRXZ # BOTTOM RIGHT
sxz # BOTTOM LEFT
"""

def reportTimeInNaturalLanguage( seconds ):
	if seconds > 60.0:
		timereport = "%i:%02i minutes" % ( seconds//60, seconds%60 )
	elif seconds < 1.0:
		timereport = "%.2f seconds" % seconds
	elif seconds < 20.0:
		timereport = "%.1f seconds" % seconds
	else:
		timereport = "%i seconds" % seconds
	return timereport

class Bumper( object ):
	def __init__( self ):
		# register prefs if run for the first time:
		if not Glyphs.defaults["com.mekkablue.Bumper.kernStrings"]:
			self.RegisterPreferences()
		
		# Window 'self.w':
		windowWidth  = 500
		windowHeight = 365
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 500 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Auto Bumper", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.Bumper.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		inset, lineHeight, currentHeight = 14, 24, -10
		currentHeight+=lineHeight
		
		self.w.text_1 = vanilla.TextBox( (inset, currentHeight, -inset, 14), "Add supplementary kerning for specified glyphs in the current master:", sizeStyle='small' )
		currentHeight+=lineHeight
		
		self.w.swapButton = vanilla.SquareButton( (-inset-20, currentHeight, -inset, 42), u"↰\n↲", sizeStyle='regular', callback=self.swap )
		
		self.w.text_left = vanilla.TextBox( (inset, currentHeight+3, 80, 14), "Left glyphs:", sizeStyle='small' )
		self.w.leftGlyphs = vanilla.ComboBox( (inset+80, currentHeight, -inset-102, 18), self.kernStringList(self), callback=self.SavePreferences, sizeStyle='small' )
		self.w.leftGlyphs.getNSComboBox().setToolTip_(u"Measures the specified glyphs from their right side to the following glyph. You can type the character ‘é’ or the slash-escaped glyph name ‘/eacute’. Or specify a category after an at sign ‘@Letter’, add a subcategory after a colon ‘@Letter:Lowercase’.\nAdd default strings in the text box at the bottom of the window. Expand the window at the bottom to access it.")
		self.w.leftIsGroups = vanilla.CheckBox((-inset-94, currentHeight+1, -inset-22, 17), u"As groups", value=True, sizeStyle='small', callback=self.SavePreferences )
		self.w.leftIsGroups.getNSButton().setToolTip_(u"If on, will measure only the specified glyph, but set the calculated kerning for the whole right group of the glyph (i.e., add group kerning). If off, will set the kerning for the glyph only (i.e., add an exception).")
		currentHeight+=lineHeight
		
		self.w.text_right = vanilla.TextBox( (inset, currentHeight+3, 80, 14), "Right glyphs:", sizeStyle='small' )
		self.w.rightGlyphs = vanilla.ComboBox( (inset+80, currentHeight, -inset-102, 18), self.kernStringList(self), callback=self.SavePreferences, sizeStyle='small' )
		self.w.rightGlyphs.getNSComboBox().setToolTip_(u"Measures from the previous glyphs to the specified glyphs to their left side. You can type the character ‘é’ or the slash-escaped glyph name ‘/eacute’. Or specify a category after an at sign ‘@Letter’, add a subcategory after a colon ‘@Letter:Lowercase’.\nAdd default strings in the text box at the bottom of the window. Expand the window at the bottom to access it.")
		self.w.rightIsGroups = vanilla.CheckBox((-inset-94, currentHeight+1, -inset-22, 17), u"As groups", value=True, sizeStyle='small', callback=self.SavePreferences )
		self.w.rightIsGroups.getNSButton().setToolTip_(u"If on, will measure only the specified glyph, but set the calculated kerning for the whole left group of the glyph (i.e., add group kerning). If off, will set the kerning for the glyph only (i.e., add an exception).")
		currentHeight+=lineHeight
		
		self.w.suffixText = vanilla.TextBox( (inset, currentHeight+3, 80, 14), u"Add suffix:", sizeStyle='small', selectable=True )
		self.w.suffix = vanilla.EditText( (inset+80, currentHeight, 150, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		self.w.suffix.getNSTextField().setToolTip_("Looks for the suffixed version of the listed glyphs, with this suffix added to the name. Useful with .sc for smallcaps. Enter WITH the leading dot for dot suffixes. Can also be used with 'superior' for figures.")
		currentHeight+=lineHeight
		
		self.w.text_21 = vanilla.TextBox( (inset, currentHeight+3, 80, 14), "Min distance:", sizeStyle='small' )
		self.w.minDistance = vanilla.EditText( (inset+80, currentHeight, 60, 19), "50", sizeStyle='small', callback=self.SavePreferences)
		self.w.minDistance.getNSTextField().setPlaceholderString_("50")
		self.w.minDistance.getNSTextField().setToolTip_(u"Adds kerning if the shortest distance between two glyphs is shorter than specified value. Leave blank or set to zero to ignore.")
		self.w.text_22 = vanilla.TextBox( (inset+80*2, currentHeight+3, 80, 14), "Max distance:", sizeStyle='small' )
		self.w.maxDistance = vanilla.EditText( (inset+80*3, currentHeight, 60, 19), "200", sizeStyle='small', callback=self.SavePreferences)
		self.w.maxDistance.getNSTextField().setPlaceholderString_("200")
		self.w.maxDistance.getNSTextField().setToolTip_(u"Adds kerning if the shortest distance between two glyphs is larger than specified value. Leave blank or set to zero to ignore.")
		self.w.text_23 = vanilla.TextBox( (inset+80*4, currentHeight+3, 80, 14), "Round by:", sizeStyle='small' )
		self.w.roundFactor = vanilla.EditText( (inset+80*5, currentHeight, -inset, 19), "10", sizeStyle='small', callback=self.SavePreferences)
		self.w.roundFactor.getNSTextField().setPlaceholderString_("10")
		self.w.roundFactor.getNSTextField().setToolTip_(u"Rounds calculated kerning. Leave blank or set to zero to ignore.")
		currentHeight+=lineHeight
				
		self.w.text_speed = vanilla.TextBox( (inset, currentHeight+3, 42, 14), "Speed:", sizeStyle='small' )
		self.w.speedPopup = vanilla.PopUpButton( (inset+42, currentHeight+1, 80, 17), ["very slow","slow","medium","fast","very fast"], callback=self.SavePreferences, sizeStyle='small' )
		self.w.speedPopup.getNSPopUpButton().setToolTip_(u"Specifies the number of measurements. Measuring is processor-intensive and can take a while. Slow: many measurements, fast: few measurements.")
		intervalIndex = Glyphs.defaults["com.mekkablue.Bumper.speedPopup"]
		if intervalIndex is None:
			intervalIndex = 0
		self.w.text_speedExplanation = vanilla.TextBox( (inset+42+90, currentHeight+3, -15, 14), "Measuring every %i units."%intervalList[intervalIndex], sizeStyle='small' )
		currentHeight+=lineHeight

		self.w.text_6 = vanilla.TextBox( (inset, currentHeight+3, 130, 14), "Ignore height intervals:", sizeStyle='small' )
		self.w.ignoreIntervals = vanilla.EditText( (inset+130, currentHeight, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.ignoreIntervals.getNSTextField().setPlaceholderString_("200:300, 400:370, -200:-150")
		self.w.ignoreIntervals.getNSTextField().setToolTip_(u"Does not measure on y coordinates in intervals specified as y1:y2. Separate multiple intervals with commas.")
		currentHeight+=lineHeight
		
		self.w.keepExistingKerning = vanilla.CheckBox((inset+5, currentHeight, -inset, 17), u"Keep (don’t overwrite) existing kerning", value=True, sizeStyle='small', callback=self.SavePreferences )
		self.w.keepExistingKerning.getNSButton().setToolTip_(u"If the kern pair already exists in the font, it will not be overwritten.")
		currentHeight+=lineHeight
		
		self.w.excludeNonExporting = vanilla.CheckBox((inset+5, currentHeight, 200, 17), u"Exclude non-exporting glyphs", value=True, sizeStyle='small', callback=self.SavePreferences )
		self.w.excludeNonExporting.getNSButton().setToolTip_(u"If one of the specified glyphs is not set to export, Auto Bumper will skip it.")
		self.w.avoidZeroKerning = vanilla.CheckBox((inset+200, currentHeight, -inset, 17), u"Avoid zero kerns", value=True, sizeStyle='small', callback=self.SavePreferences )
		self.w.avoidZeroKerning.getNSButton().setToolTip_(u"If the calculated (and rounded) kerning value is 0, it will not be added to the font.")
		currentHeight+=lineHeight
		
		self.w.reportInMacroWindow = vanilla.CheckBox((inset+5, currentHeight, -inset, 17), u"Also report in Macro Window (a few seconds slower)", value=False, sizeStyle='small', callback=self.SavePreferences )
		self.w.reportInMacroWindow.getNSButton().setToolTip_(u"Outputs a detailed report in the Macro Window, and opens it.")
		currentHeight+=lineHeight

		self.w.openNewTabWithKernPairs = vanilla.CheckBox((inset+5, currentHeight, -inset, 17), u"Open new Edit tab with new kern pairs", value=False, sizeStyle='small', callback=self.SavePreferences )
		self.w.openNewTabWithKernPairs.getNSButton().setToolTip_(u"If kern pairs were added, opens them in a new Edit tab, for inspection.")
		currentHeight+=lineHeight
		
		# Progress Bar:
		self.w.bar = vanilla.ProgressBar((inset, currentHeight, -inset, 16))
		currentHeight+=lineHeight
		
		# (Hidden) Preferences Kern Strings:
		self.w.kernStrings = vanilla.TextEditor((1, currentHeight, -1, -45), callback=self.SavePreferences)
		self.w.kernStrings.getNSTextView().setToolTip_("Add your default kern strings here. They will show up in the left/right dropdowns at the top. Everything after a hashtag (#) is ignored. Use blank lines for structuring.")
		
		self.w.text_kernStrings = vanilla.TextBox( (inset, -14-inset, -100-inset, -inset), "Expand window below to access default strings.", sizeStyle='small' )
		self.w.text_kernStrings.getNSTextField().setTextColor_( NSColor.colorWithRed_green_blue_alpha_(0,0,0, 0.2) )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-100-inset, -20-inset, -inset, -inset), "Kern", sizeStyle='regular', callback=self.BumperMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: Auto Bumper could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def kernStringList( self, sender ):
		kernStrings = Glyphs.defaults["com.mekkablue.Bumper.kernStrings"].splitlines()
		if kernStrings:
			return kernStrings
		else:
			return defaultStrings
			
	def swap(self, sender=None):
		rightEntry = self.w.rightGlyphs.get()
		rightGroupEntry = self.w.rightIsGroups.get()
		leftEntry = self.w.leftGlyphs.get()
		leftGroupEntry = self.w.leftIsGroups.get()

		self.w.rightGlyphs.set( leftEntry )
		self.w.rightIsGroups.set( leftGroupEntry )
		self.w.leftGlyphs.set( rightEntry )
		self.w.leftIsGroups.set( rightGroupEntry )
		
		self.SavePreferences(sender)
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.Bumper.leftGlyphs"] = self.w.leftGlyphs.get()
			Glyphs.defaults["com.mekkablue.Bumper.leftIsGroups"] = self.w.leftIsGroups.get()
			Glyphs.defaults["com.mekkablue.Bumper.rightGlyphs"] = self.w.rightGlyphs.get()
			Glyphs.defaults["com.mekkablue.Bumper.rightIsGroups"] = self.w.rightIsGroups.get()
			
			Glyphs.defaults["com.mekkablue.Bumper.minDistance"] = self.w.minDistance.get()
			Glyphs.defaults["com.mekkablue.Bumper.maxDistance"] = self.w.maxDistance.get()
			Glyphs.defaults["com.mekkablue.Bumper.roundFactor"] = self.w.roundFactor.get()
			Glyphs.defaults["com.mekkablue.Bumper.speedPopup"] = self.w.speedPopup.get()
			Glyphs.defaults["com.mekkablue.Bumper.ignoreIntervals"] = self.w.ignoreIntervals.get()
			Glyphs.defaults["com.mekkablue.Bumper.keepExistingKerning"] = self.w.keepExistingKerning.get()
			Glyphs.defaults["com.mekkablue.Bumper.excludeNonExporting"] = self.w.excludeNonExporting.get()
			Glyphs.defaults["com.mekkablue.Bumper.reportInMacroWindow"] = self.w.reportInMacroWindow.get()
			Glyphs.defaults["com.mekkablue.Bumper.openNewTabWithKernPairs"] = self.w.openNewTabWithKernPairs.get()
			Glyphs.defaults["com.mekkablue.Bumper.avoidZeroKerning"] = self.w.avoidZeroKerning.get()
			Glyphs.defaults["com.mekkablue.Bumper.suffix"] = self.w.suffix.get()

			Glyphs.defaults["com.mekkablue.Bumper.kernStrings"] = self.w.kernStrings.get()
			
			if sender == self.w.kernStrings:
				kernStrings = Glyphs.defaults["com.mekkablue.Bumper.kernStrings"].splitlines()
				if kernStrings:
					self.w.leftGlyphs.setItems(kernStrings)
					self.w.rightGlyphs.setItems(kernStrings)
			elif sender in (self.w.leftGlyphs, self.w.rightGlyphs):
				kernStrings = Glyphs.defaults["com.mekkablue.Bumper.kernStrings"].splitlines()
				for thisItem in sender.getItems():
					if not thisItem in kernStrings:
						Glyphs.defaults["com.mekkablue.Bumper.kernStrings"] += "\n%s"%thisItem
		except:
			return False
		
		# update speed explanation:
		if sender == self.w.speedPopup:
			intervalIndex = Glyphs.defaults["com.mekkablue.Bumper.speedPopup"]
			if intervalIndex is None:
				intervalIndex = 0
			self.w.text_speedExplanation.set( "Measuring every %i units." % intervalList[intervalIndex] )
		
		return True

	def RegisterPreferences( self ):
		Glyphs.registerDefault("com.mekkablue.Bumper.leftGlyphs", u"TVWY")
		Glyphs.registerDefault("com.mekkablue.Bumper.leftIsGroups", 1)
		Glyphs.registerDefault("com.mekkablue.Bumper.rightGlyphs", u"iíĭǐîïịìỉīįĩjĵ")
		Glyphs.registerDefault("com.mekkablue.Bumper.rightIsGroups", 0)
		
		Glyphs.registerDefault("com.mekkablue.Bumper.minDistance", 50)
		Glyphs.registerDefault("com.mekkablue.Bumper.maxDistance", 200)
		Glyphs.registerDefault("com.mekkablue.Bumper.roundFactor", 10)
		Glyphs.registerDefault("com.mekkablue.Bumper.speedPopup", 2)
		Glyphs.registerDefault("com.mekkablue.Bumper.ignoreIntervals", "")
		Glyphs.registerDefault("com.mekkablue.Bumper.keepExistingKerning", 1)
		Glyphs.registerDefault("com.mekkablue.Bumper.excludeNonExporting", 1)
		Glyphs.registerDefault("com.mekkablue.Bumper.reportInMacroWindow", 1)
		Glyphs.registerDefault("com.mekkablue.Bumper.openNewTabWithKernPairs", 1)
		Glyphs.registerDefault("com.mekkablue.Bumper.avoidZeroKerning", 1)
		Glyphs.registerDefault("com.mekkablue.Bumper.suffix", "")
		
		Glyphs.registerDefault("com.mekkablue.Bumper.kernStrings", defaultStrings)
		
		
	def LoadPreferences( self ):
		try:
			self.w.leftGlyphs.set( Glyphs.defaults["com.mekkablue.Bumper.leftGlyphs"] )
			self.w.leftIsGroups.set( Glyphs.defaults["com.mekkablue.Bumper.leftIsGroups"] )
			self.w.rightGlyphs.set( Glyphs.defaults["com.mekkablue.Bumper.rightGlyphs"] )
			self.w.rightIsGroups.set( Glyphs.defaults["com.mekkablue.Bumper.rightIsGroups"] )
			
			self.w.minDistance.set( Glyphs.defaults["com.mekkablue.Bumper.minDistance"] )
			self.w.maxDistance.set( Glyphs.defaults["com.mekkablue.Bumper.maxDistance"] )
			self.w.roundFactor.set( Glyphs.defaults["com.mekkablue.Bumper.roundFactor"] )
			self.w.speedPopup.set( Glyphs.defaults["com.mekkablue.Bumper.speedPopup"] )
			self.w.ignoreIntervals.set( Glyphs.defaults["com.mekkablue.Bumper.ignoreIntervals"] )
			self.w.keepExistingKerning.set( Glyphs.defaults["com.mekkablue.Bumper.keepExistingKerning"] )
			self.w.excludeNonExporting.set( Glyphs.defaults["com.mekkablue.Bumper.excludeNonExporting"] )
			self.w.reportInMacroWindow.set( Glyphs.defaults["com.mekkablue.Bumper.reportInMacroWindow"] )
			self.w.openNewTabWithKernPairs.set( Glyphs.defaults["com.mekkablue.Bumper.openNewTabWithKernPairs"] )
			self.w.suffix.set( Glyphs.defaults["com.mekkablue.Bumper.suffix"] )
			
			self.w.kernStrings.set( Glyphs.defaults["com.mekkablue.Bumper.kernStrings"] )
		except Exception as e:
			print e
			import traceback
			print traceback.format_exc()
			return False
			
		return True
		
	def addMissingKerning( self, thisFont, thisMasterID, leftSide, rightSide, minMaxDistance, distanceBetweenShapes ):
		# query user settings:
		shouldKeepExistingKerning = bool(Glyphs.defaults["com.mekkablue.Bumper.keepExistingKerning"])
		try:
			roundValue = float(Glyphs.defaults["com.mekkablue.Bumper.roundFactor"])
		except:
			roundValue = 1.0
		roundValue = max(roundValue,1.0)
		
		# check for existing kerning:
		existingKerning = thisFont.kerningForPair( thisMasterID, leftSide, rightSide )
		kerningExists = existingKerning < 1000000
		if not kerningExists:
			existingKerning = 0
		newKernValue = round( (minMaxDistance-distanceBetweenShapes+existingKerning) / roundValue, 0 ) * roundValue
		
		# add only if it is OK:
		if newKernValue == 0.0 and Glyphs.defaults["com.mekkablue.Bumper.avoidZeroKerning"]:
			if Glyphs.defaults["com.mekkablue.Bumper.reportInMacroWindow"]:
				print "- %s %s: zero kerning, not added." % (leftSide, rightSide)
			return False # do not increase kern count
		else:
			if kerningExists and shouldKeepExistingKerning:
				if Glyphs.defaults["com.mekkablue.Bumper.reportInMacroWindow"]:
					print "- %s %s: keeps existing %i (instead of new %i)." % (leftSide, rightSide, existingKerning, newKernValue)
				return False # do not increase kern count
			else:
				thisFont.setKerningForPair(thisMasterID, leftSide, rightSide, newKernValue)
				if Glyphs.defaults["com.mekkablue.Bumper.reportInMacroWindow"]:
					print "- %s %s: %i" % ( leftSide, rightSide, newKernValue )
				return True # increase kern count

	def BumperMain( self, sender ):
		try:
			# save prefs
			if self.SavePreferences(None):
				if Glyphs.defaults["com.mekkablue.Bumper.reportInMacroWindow"]:
					print "Note: Auto Bumper could not write preferences.\n"
			
			# query frontmost fontmaster:
			thisFont = Glyphs.font
			thisMaster = thisFont.selectedFontMaster
			thisMasterID = thisMaster.id
			
			# start reporting to macro window:
			if Glyphs.defaults["com.mekkablue.Bumper.reportInMacroWindow"]:
				Glyphs.clearLog()
				print "Auto Bumper Report for %s, master %s:\n" % (thisFont.familyName, thisMaster.name)

			# reset progress bar:
			self.w.bar.set(0)
			# start taking time:
			start = timer()
			
			
			
			# COLLECTING THE DATA WE NEED:
			
			# query user input:
			step = intervalList[ Glyphs.defaults["com.mekkablue.Bumper.speedPopup"] ]
			ignoreIntervals = sortedIntervalsFromString( Glyphs.defaults["com.mekkablue.Bumper.ignoreIntervals"] )
			shouldExcludeNonExporting = bool( Glyphs.defaults["com.mekkablue.Bumper.excludeNonExporting"] )
			
			minDistance = Glyphs.defaults["com.mekkablue.Bumper.minDistance"]
			try:
				minDistance = float(minDistance)
			except:
				minDistance = None
				self.w.minDistance.set("")
				self.SavePreferences(None)
				
			maxDistance = Glyphs.defaults["com.mekkablue.Bumper.maxDistance"]
			try:
				maxDistance = float(maxDistance)
			except:
				maxDistance = None
				self.w.maxDistance.set("")
				self.SavePreferences(None)
			
			roundFactor = Glyphs.defaults["com.mekkablue.Bumper.roundFactor"]
			try:
				roundFactor = float(roundFactor)
			except:
				roundFactor = None
				self.w.roundFactor.set("")
				self.SavePreferences(None)
			
			suffix = Glyphs.defaults["com.mekkablue.Bumper.suffix"].strip()
			cleanedSuffix=""
			for letter in suffix:
				if letter in u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-":
					cleanedSuffix += letter
			if cleanedSuffix != suffix:
				Message(
					title="Invalid Suffix Error", 
					message="The suffix you entered ('%s') is invalid. The script suggests '%s' instead. Please verify and try again." % (suffix, cleanedSuffix), 
					OKButton=None)
				self.w.suffix.set(cleanedSuffix)
				self.SavePreferences(None)
			else:
				# find list of glyph names:
				firstGlyphList = stringToListOfGlyphsForFont(
					Glyphs.defaults["com.mekkablue.Bumper.leftGlyphs"],
					thisFont,
					report=Glyphs.defaults["com.mekkablue.Bumper.reportInMacroWindow"],
					excludeNonExporting=shouldExcludeNonExporting,
					suffix=suffix,
				)
				secondGlyphList = stringToListOfGlyphsForFont(
					Glyphs.defaults["com.mekkablue.Bumper.rightGlyphs"],
					thisFont,
					report=Glyphs.defaults["com.mekkablue.Bumper.reportInMacroWindow"],
					excludeNonExporting=shouldExcludeNonExporting,
					suffix=suffix,
				)
			
				# report key values for kerning:
				if Glyphs.defaults["com.mekkablue.Bumper.reportInMacroWindow"]:
					print
					if not minDistance is None:
						print "Minimum Distance: %i" % minDistance
					if not maxDistance is None:
						print "Maximum Distance: %i" % maxDistance
					if not roundFactor is None:
						print "Rounding: %i" % roundFactor
				
					print
					print "Left glyphs:\n%s\n" % ", ".join([g.name for g in firstGlyphList])
					print "Right glyphs:\n%s\n" % ", ".join([g.name for g in secondGlyphList])
			
			
			
				# CREATE KERNING DATA:
			
				tabString = ""
				kernCount = 0
				numOfGlyphs = len(firstGlyphList)
				for index in range(numOfGlyphs):
					# update progress bar:
					self.w.bar.set( int(100*(float(index)/numOfGlyphs)) )
					# determine left glyph:
					leftGlyph = firstGlyphList[index]
					leftLayer = leftGlyph.layers[thisMasterID]
					leftGroup = leftGlyph.rightKerningGroup
					if Glyphs.defaults["com.mekkablue.Bumper.leftIsGroups"]:
						if leftGroup:
							leftSide = "@MMK_L_%s" % leftGroup
						else:
							Glyphs.showMacroWindow()
							print "Error: Left glyph %s has no kerning group. Cannot apply group kerning." % leftGlyph.name
							leftSide = None
					else:
						leftSide = leftGlyph.name
				
					# only continue if we could establish a left side:
					if leftSide:
						# cycle through right glyphs:
						for rightGlyph in secondGlyphList:
							rightLayer = rightGlyph.layers[thisMasterID]
							rightGroup = rightGlyph.leftKerningGroup
							if Glyphs.defaults["com.mekkablue.Bumper.rightIsGroups"]:
								if rightGroup:
									rightSide = "@MMK_R_%s" % rightGroup
								else:
									Glyphs.showMacroWindow()
									print "Error: Right glyph %s has no kerning group. Cannot apply group kerning." % rightGlyph.name
									rightSide = None
							else:
								rightSide = rightGlyph.name
						
							# only continue if we could establish a right side:
							if rightSide:
								kerning = effectiveKerning( leftGlyph.name, rightGlyph.name, thisFont, thisMasterID )
								distanceBetweenShapes = minDistanceBetweenTwoLayers( leftLayer, rightLayer, interval=step, kerning=kerning, report=False, ignoreIntervals=ignoreIntervals )
					
								# positive kerning (if desired):
								if minDistance and (not distanceBetweenShapes is None) and (distanceBetweenShapes < minDistance):
									if self.addMissingKerning( thisFont, thisMasterID, leftSide, rightSide, minDistance, distanceBetweenShapes ):
										kernCount += 1
										tabString += "/%s/%s " % (leftGlyph.name, rightGlyph.name)
								
								# negative kerning (if desired):
								if maxDistance and (not distanceBetweenShapes is None) and (distanceBetweenShapes > maxDistance):
									if self.addMissingKerning( thisFont, thisMasterID, leftSide, rightSide, maxDistance, distanceBetweenShapes ):
										kernCount += 1
										tabString += "/%s/%s " % (leftGlyph.name, rightGlyph.name)
					
					tabString += "\n"
			
			
			
				# FINISH UP AND REPORT: 
			
				# update progress bar:
				self.w.bar.set( 100 )
				# take time:
				timereport = reportTimeInNaturalLanguage( timer() - start )

				# clean up the tab string:
				tabString = tabString.strip()
				while "\n\n" in tabString:
					tabString = tabString.replace("\n\n", "\n")
			
				# Report number of new kern pairs:
				if kernCount:
					report = 'Added %i kern pairs. Time elapsed: %s.' % (kernCount, timereport)
				# or report that nothing was found:
				else:
					report = 'No kerning added. Time elapsed: %s. Congrats!' % timereport
			
				# Floating notification:
				notificationTitle = "Bumper: %s (%s)" % (thisFont.familyName, thisMaster.name)
				Glyphs.showNotification( notificationTitle, report )
			
				# Open new tab:
				if Glyphs.defaults["com.mekkablue.Bumper.openNewTabWithKernPairs"]:
					thisFont.newTab( tabString )

				# Report in Macro Window:
				if Glyphs.defaults["com.mekkablue.Bumper.reportInMacroWindow"]:
					print
					print report
					Glyphs.showMacroWindow()
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Auto Bumper Error: %s" % e
			import traceback
			print traceback.format_exc()

Bumper()