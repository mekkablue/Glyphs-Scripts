#MenuTitle: Manage Version, Date and Time
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Batch-set version numbers, date and time for all open fonts.
"""

import vanilla, datetime

class ManageVersionDateAndTime( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 130
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Manage Version, Date and Time", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.ManageVersionDateAndTime.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.setDate = vanilla.CheckBox( (inset, linePos-1, 100, 20), u"Date and time:", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.datePicker = vanilla.DatePicker( (inset+100, linePos-3, -inset-70, 22), date=NSDate.alloc().init(), minDate=None, maxDate=None, showStepper=True, mode='text', timeDisplay='hourMinuteSecond', dateDisplay='yearMonthDay', callback=None, sizeStyle='small' )
		self.w.noonButton = vanilla.SquareButton( (-inset-60, linePos, -inset, 18), u"🕛 Noon", sizeStyle='small', callback=self.setNoon )
		linePos += lineHeight
		
		self.w.setVersion = vanilla.CheckBox( (inset, linePos-1, 100, 20), u"Version:", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.versionMajor = vanilla.EditText( (inset+100, linePos, 50, 19), "1", callback=self.SavePreferences, sizeStyle='small' )
		self.w.versionDot = vanilla.TextBox( (inset+151, linePos+2, 8, 18), u".", sizeStyle='regular', selectable=True )
		self.w.versionMinor = vanilla.EditText( (inset+160, linePos, -inset-70, 19), "005", callback=self.SavePreferences, sizeStyle='small' )
		self.w.minVersionButton = vanilla.SquareButton( (-inset-60, linePos, -inset, 18), u"⟳ 1.005", sizeStyle='small', callback=self.setVersion1005 )
		linePos += lineHeight
		
		self.w.allOpenFonts = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"⚠️ Apply to all open fonts", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-100-inset, -20-inset, -inset, -inset), "Apply", sizeStyle='regular', callback=self.ManageVersionDateAndTimeMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Manage Version, Date and Time' could not load preferences. Will resort to defaults")
		
		self.setNoon()
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def updateUI(self, sender=None):
		dateEnabled = self.w.setDate.get()
		self.w.datePicker.enable(dateEnabled)
		self.w.noonButton.enable(dateEnabled)
		
		versionEnabled = self.w.setVersion.get()
		self.w.versionMajor.enable(versionEnabled)
		self.w.versionMinor.enable(versionEnabled)
		
		self.w.runButton.enable(dateEnabled or versionEnabled)
		
	
	def setNoon(self, sender=None):
		# Get current date:
		currentDate = datetime.datetime.now()
		newDate = datetime.datetime(
			currentDate.year,
			currentDate.month,
			currentDate.day,
			12, #d.hour,
			00, #d.minute,
			00, #d.second,
			00, #d.microsecond,
			currentDate.tzinfo,
			)
		self.w.datePicker.set(newDate)
	
	def setVersion1005(self, sender=None):
		self.w.versionMajor.set("1")
		self.w.versionMinor.set("005")
		
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.setDate"] = self.w.setDate.get()
			Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.setVersion"] = self.w.setVersion.get()
			Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.versionMinor"] = "%03i" % int(self.w.versionMinor.get())
			Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.versionMajor"] = self.w.versionMajor.get()
			Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.allOpenFonts"] = self.w.allOpenFonts.get()

			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.ManageVersionDateAndTime.setDate", 1)
			Glyphs.registerDefault("com.mekkablue.ManageVersionDateAndTime.setVersion", 1)
			Glyphs.registerDefault("com.mekkablue.ManageVersionDateAndTime.versionMinor", "005")
			Glyphs.registerDefault("com.mekkablue.ManageVersionDateAndTime.versionMajor", "1")
			Glyphs.registerDefault("com.mekkablue.ManageVersionDateAndTime.allOpenFonts", 1)
			
			# load previously written prefs:
			self.w.setDate.set( Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.setDate"] )
			self.w.setVersion.set( Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.setVersion"] )
			self.w.versionMinor.set( "%03i" % int(Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.versionMinor"]) )
			self.w.versionMajor.set( Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.versionMajor"] )
			self.w.allOpenFonts.set( Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.allOpenFonts"] )
			
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def ManageVersionDateAndTimeMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Manage Version, Date and Time' could not write preferences.")
			
			setDate = Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.setDate"]
			setVersion = Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.setVersion"]
			versionMinor = int(Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.versionMinor"])
			versionMajor = int(Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.versionMajor"])
			allOpenFonts = Glyphs.defaults["com.mekkablue.ManageVersionDateAndTime.allOpenFonts"]
			dateInDatePicker = self.w.datePicker.get()
			
			if allOpenFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font,) # tuple with frontmost font only
			
			print("Manage Version, Date and Time Report:")
			
			if not theseFonts or theseFonts[0] is None:
				Message(title="No Font Open", message="The script requires at list one font open. Open a font and run the script again.", OKButton=None)
			else:
				for i,thisFont in enumerate(theseFonts):
					print("\n\n%i. %s:\n" % (i+1, thisFont.familyName))
					if thisFont.filepath:
						print("📄 %s" % thisFont.filepath)
					else:
						print("⚠️ The font file has not been saved yet.")
					
					if setVersion:
						thisFont.versionMajor = versionMajor
						thisFont.versionMinor = versionMinor
						print("✅ 🔢 version set: %i.%03i" % (versionMajor,versionMinor))
					
					if setDate:
						thisFont.date = dateInDatePicker
						print("✅ 📆 date set: %s" % dateInDatePicker)

			# Final report:
			Glyphs.showNotification( 
				u"Script finished",
				u"Version, date and time have been set for %i font%s. Details in Macro Window." % (
					len(theseFonts),
					"" if len(theseFonts)==1 else "s",
				),
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Manage Version, Date and Time Error: %s" % e)
			import traceback
			print(traceback.format_exc())

ManageVersionDateAndTime()