#MenuTitle: Font Info Batch Setter
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Batch-apply settings in Font Info > Font to open fonts: designer, designer URL, manufacturer, manufacturer URL, copyright, version number, date and time. Useful for syncing Font Info settings across many fonts.
"""
from AppKit import NSDate
import vanilla, datetime

class FontInfoBatchSetter( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 300
		windowWidthResize  = 1000 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Font Info Batch Setter", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.FontInfoBatchSetter.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		column = 100
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Batch-set Font Info > Font of open fonts with these values:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		# DESIGNER
		self.w.setDesigner = vanilla.CheckBox( (inset, linePos-1, column, 20), u"Designer:", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.designer = vanilla.EditText( (inset+column, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		self.w.setDesignerURL = vanilla.CheckBox( (inset, linePos-1, column, 20), u"Designer URL:", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.designerURL = vanilla.EditText( (inset+column, linePos, -inset, 19), "https://", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		# MANUFACTURER
		self.w.setManufacturer = vanilla.CheckBox( (inset, linePos-1, column, 20), u"Manufacturer:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.manufacturer = vanilla.EditText( (inset+column, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		self.w.setManufacturerURL = vanilla.CheckBox( (inset, linePos-1, column, 20), u"Manufact.URL:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.manufacturerURL = vanilla.EditText( (inset+column, linePos, -inset, 19), "https://", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		# COPYRIGHT
		self.w.setCopyright = vanilla.CheckBox( (inset, linePos-1, column, 20), u"Copyright:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.copyright = vanilla.EditText( (inset+column, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		# VERSION NUMBER
		self.w.setVersion = vanilla.CheckBox( (inset, linePos-1, column, 20), u"Version:", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.versionMajor = vanilla.EditText( (inset+column, linePos, 50, 19), "1", callback=self.SavePreferences, sizeStyle='small' )
		self.w.versionDot = vanilla.TextBox( (inset+151, linePos+2, 8, 18), u".", sizeStyle='regular', selectable=True )
		self.w.versionMinor = vanilla.EditText( (inset+160, linePos, -inset-113, 19), "005", callback=self.SavePreferences, sizeStyle='small' )
		self.w.versionMinorDecrease = vanilla.SquareButton( (-inset-110, linePos, -inset-90, 19), u"−", sizeStyle='small', callback=self.changeMinVersion )
		self.w.versionMinorDecrease.getNSButton().setToolTip_("Decrease the version number by 0.001.")
		self.w.versionMinorIncrease = vanilla.SquareButton( (-inset-91, linePos, -inset-71, 19), u"+", sizeStyle='small', callback=self.changeMinVersion )
		self.w.versionMinorIncrease.getNSButton().setToolTip_("Increase the version number by 0.001.")
		self.w.minVersionButton = vanilla.SquareButton( (-inset-60, linePos, -inset, 18), u"⟳ 1.005", sizeStyle='small', callback=self.setVersion1005 )
		self.w.minVersionButton.getNSButton().setToolTip_(u"Resets the version to 1.005. Some (old?) Microsoft apps may consider fonts with smaller versions as unfinished and not display them in their font menu.")
		linePos += lineHeight
		
		# DATE AND TIME
		self.w.setDate = vanilla.CheckBox( (inset, linePos-1, column, 20), u"Date and time:", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.datePicker = vanilla.DatePicker( (inset+column, linePos-3, -inset-70, 22), date=NSDate.alloc().init(), minDate=None, maxDate=None, showStepper=True, mode='text', timeDisplay='hourMinuteSecond', dateDisplay='yearMonthDay', callback=None, sizeStyle='small' )
		self.w.noonButton = vanilla.SquareButton( (-inset-60, linePos, -inset, 18), u"🕛 Today", sizeStyle='small', callback=self.setNoon )
		self.w.noonButton.getNSButton().setToolTip_(u"Resets the date to today 12:00 noon.")
		linePos += lineHeight
		
		# SEPARATOR
		self.w.separator = vanilla.HorizontalLine((inset, linePos+int(lineHeight*0.5)-1, -inset, 1))
		linePos += lineHeight
				
		# APPLY TO FONTS
		self.w.finger = vanilla.TextBox( (inset-5, linePos, 22, 22), u"👉 ", sizeStyle='regular', selectable=True )
		self.w.applyText = vanilla.TextBox( (inset+17, linePos+2, 70, 14), u"Apply to", sizeStyle='small', selectable=True )
		self.w.applyPopup = vanilla.PopUpButton( (inset+70, linePos, 150, 17), (u"ALL open fonts", u"open fonts containing"), sizeStyle='small', callback=self.SavePreferences )
		self.w.applyContaining = vanilla.EditText( (inset+70+150+10, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small', placeholder="enter part of family name here" )
		self.w.applyContaining.getNSTextField().setToolTip_(u"Only applies the settings to fonts that contain this in Font Info > Font > Family Name.")
		linePos += lineHeight
		
		# Buttons:
		self.w.extractButton = vanilla.Button( (-270-inset, -20-inset, -130-inset, -inset), "Extract from Font", sizeStyle='regular', callback=self.ExtractFontInfoFromFrontmostFont )
		self.w.extractButton.getNSButton().setToolTip_(u"Extracts the settings from the frontmost font and fills the UI with it.")
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Apply to Fonts", sizeStyle='regular', callback=self.FontInfoBatchSetterMain )
		self.w.runButton.getNSButton().setToolTip_(u"Applies the checked settings above to all fonts indicated in the ‘Apply to’ option.")
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Font Info Batch Setter' could not load preferences. Will resort to defaults")
		
		self.setNoon()
		self.updateUI()
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def changeMinVersion(self, sender=None):
		valueField = self.w.versionMinor
		currentValue = int(valueField.get())
		if sender == self.w.versionMinorDecrease:
			currentValue -= 1
			if currentValue < 0:
				currentValue = 0
		if sender == self.w.versionMinorIncrease:
			currentValue += 1
			if currentValue > 999:
				currentValue = 999
		valueField.set("%03i"%currentValue)
		self.SavePreferences()
	
	def updateUI(self, sender=None):
		self.w.designer.enable(self.w.setDesigner.get())
		self.w.designerURL.enable(self.w.setDesignerURL.get())
		self.w.manufacturer.enable(self.w.setManufacturer.get())
		self.w.manufacturerURL.enable(self.w.setManufacturerURL.get())
		self.w.copyright.enable(self.w.setCopyright.get())

		dateEnabled = self.w.setDate.get()
		self.w.datePicker.enable(dateEnabled)
		self.w.noonButton.enable(dateEnabled)
		
		versionEnabled = self.w.setVersion.get()
		self.w.versionMajor.enable(versionEnabled)
		self.w.versionMinor.enable(versionEnabled)
		self.w.minVersionButton.enable(versionEnabled)
		
		self.w.applyContaining.show(self.w.applyPopup.get()) # 0=all fonts, 1=fonts containing, here repurposed as bool
		applySettingsEnable = self.w.applyPopup.get() == 0 or len(self.w.applyContaining.get().strip()) > 0

		self.w.runButton.enable(
			(
				# ANY of the checboxes must be on:
				dateEnabled or
				versionEnabled or
				self.w.setDesigner.get() or
				self.w.setDesignerURL.get() or
				self.w.setManufacturer.get() or
				self.w.setManufacturerURL.get() or
				self.w.setCopyright.get()
			) and applySettingsEnable
		)
	
	def updateTooltips(self, sender=None):
		self.w.designer.getNSTextField().setToolTip_(self.w.designer.get())
		self.w.designerURL.getNSTextField().setToolTip_(self.w.designerURL.get())
		self.w.manufacturer.getNSTextField().setToolTip_(self.w.manufacturer.get())
		self.w.manufacturerURL.getNSTextField().setToolTip_(self.w.manufacturerURL.get())
		self.w.copyright.getNSTextField().setToolTip_(self.w.copyright.get())
	
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
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.applyContaining"] = self.w.applyContaining.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.applyPopup"] = self.w.applyPopup.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.copyright"] = self.w.copyright.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.designer"] = self.w.designer.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.designerURL"] = self.w.designerURL.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.manufacturer"] = self.w.manufacturer.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.manufacturerURL"] = self.w.manufacturerURL.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setCopyright"] = self.w.setCopyright.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setDate"] = self.w.setDate.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setDesigner"] = self.w.setDesigner.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setDesignerURL"] = self.w.setDesignerURL.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setManufacturer"] = self.w.setManufacturer.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setManufacturerURL"] = self.w.setManufacturerURL.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setVersion"] = self.w.setVersion.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.versionMajor"] = self.w.versionMajor.get()
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.versionMinor"] = "%03i" % int(self.w.versionMinor.get())
			
			self.updateTooltips()
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.applyContaining", "")
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.applyPopup", 0)
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.copyright", "")
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.designer", "")
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.designerURL", "")
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.manufacturer", "")
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.manufacturerURL", "")
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.setCopyright", False)
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.setDate", True)
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.setDesigner", False)
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.setDesignerURL", False)
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.setManufacturer", False)
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.setManufacturerURL", False)
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.setVersion", True)
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.versionMajor", "1")
			Glyphs.registerDefault("com.mekkablue.FontInfoBatchSetter.versionMinor", "005")
			
			# load previously written prefs:
			self.w.applyContaining.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.applyContaining"] )
			self.w.applyPopup.set( int(Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.applyPopup"]) )
			self.w.copyright.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.copyright"] )
			self.w.designer.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.designer"] )
			self.w.designerURL.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.designerURL"] )
			self.w.manufacturer.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.manufacturer"] )
			self.w.manufacturerURL.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.manufacturerURL"] )
			self.w.setCopyright.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setCopyright"] )
			self.w.setDate.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setDate"] )
			self.w.setDesigner.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setDesigner"] )
			self.w.setDesignerURL.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setDesignerURL"] )
			self.w.setManufacturer.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setManufacturer"] )
			self.w.setManufacturerURL.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setManufacturerURL"] )
			self.w.setVersion.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setVersion"] )
			self.w.versionMajor.set( Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.versionMajor"] )
			self.w.versionMinor.set( "%03i" % int(Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.versionMinor"]) )
			
			self.updateTooltips()
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False
	
	def ExtractFontInfoFromFrontmostFont(self, sender=None):
		# clear macro window log:
		Glyphs.clearLog()
		thisFont = Glyphs.font
		if not thisFont:
			self.complainAboutNoFonts()
		else:
			print("Extracting font info from: %s" % thisFont.familyName)
			self.reportFilePath( thisFont )
		
			# update prefs:
			self.w.datePicker.set(thisFont.date)
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.versionMinor"] = thisFont.versionMinor
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.versionMajor"] = thisFont.versionMajor
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.copyright"] = thisFont.copyright
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.designer"] = thisFont.designer
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.designerURL"] = thisFont.designerURL
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.manufacturer"] = thisFont.manufacturer
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.manufacturerURL"] = thisFont.manufacturerURL

			# update checkboxes:
			# Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setDate"] = True
			# Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setVersion"] = True
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setCopyright"] = bool(thisFont.copyright)
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setDesigner"] = bool(thisFont.designer)
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setDesignerURL"] = bool(thisFont.designerURL)
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setManufacturer"] = bool(thisFont.manufacturer)
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setManufacturerURL"] = bool(thisFont.manufacturerURL)
			
			# "containing" text box:
			name = thisFont.familyName.strip()
			words = name.split(" ")
			if len(words) > 1:
				potentialFoundryPrefix = len(words)==2 and len(words[0])<4 # e.g. "GT Flexa"
				if not potentialFoundryPrefix:
					# get rid of last word in family name (e.g. "Sans"):
					name = " ".join(words[:-1])
			Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.applyContaining"] = name
			
			print()
			print("👨‍🎨 Designer: %s" % thisFont.designer)
			print("👨‍🎨 DesignerURL: %s" % thisFont.designerURL)
			print("👸‍ Manufacturer: %s" % thisFont.manufacturer)
			print("👸‍ ManufacturerURL: %s" % thisFont.manufacturerURL)
			print("📝 Copyright: %s" % thisFont.copyright)
			print("🔢 Version: %i.%03i" % (thisFont.versionMajor, thisFont.versionMinor))
			print("📆 Date: %s" % thisFont.date)
			print("\nDone.")
			
			# update UI to the settings stored above:
			self.LoadPreferences()
	
	def FontInfoBatchSetterMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Font Info Batch Setter' could not write preferences.")
			
			setDate = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setDate"]
			setVersion = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setVersion"]
			versionMinor = int(Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.versionMinor"])
			versionMajor = int(Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.versionMajor"])
			allOpenFonts = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.allOpenFonts"]
			dateInDatePicker = self.w.datePicker.get()
			
			applyPopup = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.applyPopup"]
			applyContaining = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.applyContaining"]
			copyright = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.copyright"]
			setCopyright = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setCopyright"]
			manufacturerURL = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.manufacturerURL"]
			setManufacturerURL = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setManufacturerURL"]
			manufacturer = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.manufacturer"]
			setManufacturer = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setManufacturer"]
			designerURL = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.designerURL"]
			setDesignerURL = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setDesignerURL"]
			designer = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.designer"]
			setDesigner = Glyphs.defaults["com.mekkablue.FontInfoBatchSetter.setDesigner"]
			
			if applyPopup == 0:
				# ALL OPEN FONTS
				theseFonts = Glyphs.fonts
			elif applyPopup == 1:
				# ALL FONTS CONTAINING
				theseFonts = [f for f in Glyphs.fonts if applyContaining in f.familyName]
				
			print("Font Info Batch Setter Report:")
			
			changeCount = 0
			changedFontsCount = 0

			if not theseFonts or theseFonts[0] is None:
				self.complainAboutNoFonts()
			else:
				
				for i,thisFont in enumerate(theseFonts):
					print("\n\n%i. %s:" % (i+1, thisFont.familyName))
					self.reportFilePath( thisFont )
					print()
					
					currentChangeCount = changeCount
					
					if setVersion:
						if thisFont.versionMajor == versionMajor and thisFont.versionMinor == versionMinor:
							print("🆗 🔢 Font already has desired Version. No change.")
						else:
							thisFont.versionMajor = versionMajor
							thisFont.versionMinor = versionMinor
							print("✅ 🔢 Version set: %i.%03i" % (versionMajor,versionMinor))
							changeCount += 1
					
					if setDate:
						if thisFont.date == dateInDatePicker:
							print("🆗 📆 Font already has desired Date. No change.")
						else:
							thisFont.date = dateInDatePicker
							print("✅ 📆 Date set: %s" % dateInDatePicker)
							changeCount += 1
					
					if setCopyright:
						if thisFont.copyright == copyright:
							print("🆗 📝 Font already has desired Copyright. No change.")
						else:
							thisFont.copyright = copyright
							print("✅ 📝 Copyright set: %s" % copyright)
							changeCount += 1
							
					if setManufacturerURL:
						if thisFont.manufacturerURL == manufacturerURL:
							print("🆗 👸 Font already has desired ManufacturerURL. No change.")
						else:
							thisFont.manufacturerURL = manufacturerURL
							print("✅ 👸 ManufacturerURL set: %s" % manufacturerURL)
							changeCount += 1
							
					if setManufacturer:
						if thisFont.manufacturer == manufacturer:
							print("🆗 👸 Font already has desired Manufacturer. No change.")
						else:
							thisFont.manufacturer = manufacturer
							print("✅ 👸 Manufacturer set: %s" % manufacturer)
							changeCount += 1
							
					if setDesignerURL:
						if thisFont.designerURL == designerURL:
							print("🆗 👨‍🎨 Font already has desired DesignerURL. No change.")
						else:
							thisFont.designerURL = designerURL
							print("✅ 👨‍🎨 DesignerURL set: %s" % designerURL)
							changeCount += 1
							
					if setDesigner:
						if thisFont.designer == designer:
							print("🆗 👨‍🎨 Font already has desired Designer. No change.")
						else:
							thisFont.designer = designer
							print("✅ 👨‍🎨 Designer set: %s" % designer)
							changeCount += 1
					
					if changeCount > currentChangeCount:
						changedFontsCount += 1

			# Final report:
			Glyphs.showNotification( 
				u"Font Info Batch Setter: Done",
				u"Went through %i open font%s. Changed %i value%s in %i font%s. Details in Macro Window." % (
					len(theseFonts),
					"" if len(theseFonts)==1 else "s",
					changeCount,
					"" if changeCount==1 else "s",
					changedFontsCount,
					"" if changedFontsCount==1 else "s",
				),
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Font Info Batch Setter Error: %s" % e)
			import traceback
			print(traceback.format_exc())

	def complainAboutNoFonts(self, sender=None):
		Message(title="No Font Open", message="The script requires at least one font open. Open a font and run the script again.", OKButton=None)
		print("🤷‍♂️ No open fonts found.")
	
	def reportFilePath(self, thisFont):
		if thisFont.filepath:
			print("📄 %s" % thisFont.filepath)
		else:
			print("⚠️ The font file has not been saved yet.")


FontInfoBatchSetter()