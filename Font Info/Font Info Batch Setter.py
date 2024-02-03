# MenuTitle: Font Info Batch Setter
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Batch-apply settings in Font Info > Font to open fonts: designer, designer URL, manufacturer, manufacturer URL, copyright, version number, date and time. Useful for syncing Font Info settings across many fonts.
"""
import vanilla
import datetime
import AppKit
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


def addPropertyToFont(font, key, value):
	while font.propertyForName_(key):
		font.removeObjectFromProperties_(font.propertyForName_(key))
	font.setProperty_value_languageTag_(key, value, None)


class FontInfoBatchSetter(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"applyContaining": "",
		"applyPopup": 0,
		
		"copyright": "",
		"trademark": "",
		"vendorID": "",
		"designer": "",
		"designerURL": "",
		"manufacturer": "",
		"manufacturerURL": "",
		"license": "",
		"licenseURL": "",
		"fontDescription": "",
		
		"setCopyright": False,
		"setTrademark": False,
		"setVendorID": False,
		"setDesigner": False,
		"setDesignerURL": False,
		"setManufacturer": False,
		"setManufacturerURL": False,
		"setLicense": False,
		"setLicenseURL": False,
		"setFontDescription": False,
		
		"setDate": True,

		"setVersion": True,
		"versionMajor": "1",
		"versionMinor": "005",
	}
	placeholderFamilyName = "###familyName###"

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 400
		windowWidthResize = 1000  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Font Info Batch Setter",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		column = 100

		self.w.explanatoryText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Batch-set Font Info > Font of open fonts with these values:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		# DESIGNER
		self.w.setDesigner = vanilla.CheckBox((inset, linePos - 1, column, 20), "Designer:", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.designer = vanilla.EditText((inset + column, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight
		self.w.setDesignerURL = vanilla.CheckBox((inset, linePos - 1, column, 20), "Designer URL:", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.designerURL = vanilla.EditText((inset + column, linePos, -inset, 19), "https://", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# MANUFACTURER
		self.w.setManufacturer = vanilla.CheckBox((inset, linePos - 1, column, 20), "Manufacturer:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.manufacturer = vanilla.EditText((inset + column, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight
		self.w.setManufacturerURL = vanilla.CheckBox((inset, linePos - 1, column, 20), "Manufact.URL:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.manufacturerURL = vanilla.EditText((inset + column, linePos, -inset, 19), "https://", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# LICENSE
		self.w.setLicense = vanilla.CheckBox((inset, linePos - 1, column, 20), "License:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.license = vanilla.EditText((inset + column, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight
		self.w.setLicenseURL = vanilla.CheckBox((inset, linePos - 1, column, 20), "License URL:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.licenseURL = vanilla.EditText((inset + column, linePos, -inset, 19), "https://", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# COPYRIGHT
		self.w.setCopyright = vanilla.CheckBox((inset, linePos - 1, column, 20), "Copyright:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.copyright = vanilla.EditText((inset + column, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# TRADEMARK
		self.w.setTrademark = vanilla.CheckBox((inset, linePos - 1, column, 20), "Trademark:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.trademark = vanilla.EditText((inset + column, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		tooltip = f"Trademark information, name ID 7. Use {self.placeholderFamilyName} as placeholder for the current family name."
		self.w.setTrademark.getNSButton().setToolTip_(tooltip)
		self.w.trademark.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		# Description
		self.w.setFontDescription = vanilla.CheckBox((inset, linePos - 1, column, 20), "Description:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.fontDescription = vanilla.EditText((inset + column, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle="small")
		tooltip = f"Description, name ID 10. Use {self.placeholderFamilyName} as placeholder for the current family name."
		self.w.setFontDescription.getNSButton().setToolTip_(tooltip)
		self.w.fontDescription.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		# VENDOR ID
		self.w.setVendorID = vanilla.CheckBox((inset, linePos - 1, column, 20), "Vendor ID:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.vendorID = vanilla.EditText((inset + column, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# VERSION NUMBER
		self.w.setVersion = vanilla.CheckBox((inset, linePos - 1, column, 20), "Version:", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.versionMajor = vanilla.EditText((inset + column, linePos, 50, 19), "1", callback=self.SavePreferences, sizeStyle='small')
		self.w.versionDot = vanilla.TextBox((inset + 151, linePos + 2, 8, 18), ".", sizeStyle='regular', selectable=True)
		self.w.versionMinor = vanilla.EditText((inset + 160, linePos, -inset - 113, 19), "005", callback=self.SavePreferences, sizeStyle='small')
		self.w.versionMinorDecrease = vanilla.SquareButton((-inset - 110, linePos, -inset - 90, 19), "−", sizeStyle='small', callback=self.changeMinVersion)
		self.w.versionMinorDecrease.getNSButton().setToolTip_("Decrease the version number by 0.001.")
		self.w.versionMinorIncrease = vanilla.SquareButton((-inset - 91, linePos, -inset - 71, 19), "+", sizeStyle='small', callback=self.changeMinVersion)
		self.w.versionMinorIncrease.getNSButton().setToolTip_("Increase the version number by 0.001.")
		self.w.minVersionButton = vanilla.SquareButton((-inset - 60, linePos, -inset, 18), "⟳ 1.005", sizeStyle='small', callback=self.setVersion1005)
		self.w.minVersionButton.getNSButton().setToolTip_("Resets the version to 1.005. Some (old?) Microsoft apps may consider fonts with smaller versions as unfinished and not display them in their font menu.")
		linePos += lineHeight

		# DATE AND TIME
		self.w.setDate = vanilla.CheckBox((inset, linePos - 1, column, 20), "Date and time:", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.datePicker = vanilla.DatePicker(
			(inset + column, linePos - 3, -inset - 70, 22),
			date=AppKit.NSDate.alloc().init(),
			minDate=None,
			maxDate=None,
			showStepper=True,
			mode='text',
			timeDisplay='hourMinuteSecond',
			dateDisplay='yearMonthDay',
			callback=None,
			sizeStyle='small'
		)
		self.w.noonButton = vanilla.SquareButton((-inset - 60, linePos, -inset, 18), "🕛 Today", sizeStyle='small', callback=self.setNoon)
		self.w.noonButton.getNSButton().setToolTip_("Resets the date to today 12:00 noon.")
		linePos += lineHeight

		# SEPARATOR
		self.w.separator = vanilla.HorizontalLine((inset, linePos + int(lineHeight * 0.5) - 1, -inset, 1))
		linePos += lineHeight

		# APPLY TO FONTS
		self.w.finger = vanilla.TextBox((inset - 5, linePos, 22, 22), "👉 ", sizeStyle='regular', selectable=True)
		self.w.applyText = vanilla.TextBox((inset + 17, linePos + 2, 70, 14), "Apply to", sizeStyle='small', selectable=True)
		self.w.applyPopup = vanilla.PopUpButton((inset + 70, linePos, 150, 17), ("ALL open fonts", "open fonts containing"), sizeStyle='small', callback=self.SavePreferences)
		self.w.applyContaining = vanilla.EditText((inset + 70 + 150 + 10, linePos, -inset, 19), "", callback=self.SavePreferences, sizeStyle='small', placeholder="enter part of family name here")
		self.w.applyContaining.getNSTextField().setToolTip_("Only applies the settings to fonts that contain this in Font Info > Font > Family Name.")
		linePos += lineHeight

		# Buttons:
		self.w.extractButton = vanilla.Button((-270 - inset, -20 - inset, -130 - inset, -inset), "Extract from Font", sizeStyle='regular', callback=self.ExtractFontInfoFromFrontmostFont)
		self.w.extractButton.getNSButton().setToolTip_("Extracts the settings from the frontmost font and fills the UI with it.")
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Apply to Fonts", sizeStyle='regular', callback=self.FontInfoBatchSetterMain)
		self.w.runButton.getNSButton().setToolTip_("Applies the checked settings above to all fonts indicated in the ‘Apply to’ option.")
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		self.setNoon()
		self.updateGUI()

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
		valueField.set("%03i" % currentValue)
		self.SavePreferences()

	def updateGUI(self, sender=None):
		self.updateTooltips()
		self.w.designer.enable(self.w.setDesigner.get())
		self.w.designerURL.enable(self.w.setDesignerURL.get())
		self.w.manufacturer.enable(self.w.setManufacturer.get())
		self.w.manufacturerURL.enable(self.w.setManufacturerURL.get())
		self.w.license.enable(self.w.setLicense.get())
		self.w.licenseURL.enable(self.w.setLicenseURL.get())
		self.w.copyright.enable(self.w.setCopyright.get())
		self.w.trademark.enable(self.w.setTrademark.get())
		self.w.vendorID.enable(self.w.setVendorID.get())

		dateEnabled = self.w.setDate.get()
		self.w.datePicker.enable(dateEnabled)
		self.w.noonButton.enable(dateEnabled)

		versionEnabled = self.w.setVersion.get()
		self.w.versionMajor.enable(versionEnabled)
		self.w.versionMinor.enable(versionEnabled)
		self.w.minVersionButton.enable(versionEnabled)

		self.w.applyContaining.show(self.w.applyPopup.get())  # 0=all fonts, 1=fonts containing, here repurposed as bool
		applySettingsEnable = self.w.applyPopup.get() == 0 or len(self.w.applyContaining.get().strip()) > 0

		self.w.runButton.enable(
			(
				# ANY of the checkboxes must be on:
				dateEnabled or versionEnabled or self.w.setDesigner.get() or self.w.setDesignerURL.get() or self.w.setManufacturer.get() or \
				self.w.setManufacturerURL.get() or self.w.setCopyright.get()
			) and applySettingsEnable
		)

	def updateTooltips(self, sender=None):
		self.w.designer.getNSTextField().setToolTip_(self.w.designer.get())
		self.w.designerURL.getNSTextField().setToolTip_(self.w.designerURL.get())
		self.w.manufacturer.getNSTextField().setToolTip_(self.w.manufacturer.get())
		self.w.manufacturerURL.getNSTextField().setToolTip_(self.w.manufacturerURL.get())
		self.w.license.getNSTextField().setToolTip_(self.w.license.get())
		self.w.licenseURL.getNSTextField().setToolTip_(self.w.licenseURL.get())
		self.w.copyright.getNSTextField().setToolTip_(self.w.copyright.get())
		self.w.trademark.getNSTextField().setToolTip_(self.w.trademark.get())
		self.w.vendorID.getNSTextField().setToolTip_(self.w.vendorID.get())

	def setNoon(self, sender=None):
		# Get current date:
		currentDate = datetime.datetime.now()
		newDate = datetime.datetime(
			currentDate.year,
			currentDate.month,
			currentDate.day,
			12,  # d.hour,
			00,  # d.minute,
			00,  # d.second,
			00,  # d.microsecond,
			currentDate.tzinfo,
		)
		self.w.datePicker.set(newDate)

	def setVersion1005(self, sender=None):
		self.w.versionMajor.set("1")
		self.w.versionMinor.set("005")

	def ExtractFontInfoFromFrontmostFont(self, sender=None):
		# clear macro window log:
		Glyphs.clearLog()
		thisFont = Glyphs.font
		if not thisFont:
			self.complainAboutNoFonts()
		else:
			print(f"Extracting font info from: {thisFont.familyName}")
			self.reportFilePath(thisFont)

			# update prefs:
			self.w.datePicker.set(thisFont.date)
			Glyphs.defaults[self.domain("versionMinor")] = f"{thisFont.versionMinor:03}"
			Glyphs.defaults[self.domain("versionMajor")] = thisFont.versionMajor
			Glyphs.defaults[self.domain("copyright")] = thisFont.copyright
			if thisFont.trademark:
				Glyphs.defaults[self.domain("trademark")] = thisFont.trademark.replace(thisFont.familyName, self.placeholderFamilyName)
			else:
				Glyphs.defaults[self.domain("trademark")] = thisFont.trademark
			Glyphs.defaults[self.domain("designer")] = thisFont.designer
			Glyphs.defaults[self.domain("designerURL")] = thisFont.designerURL
			Glyphs.defaults[self.domain("manufacturer")] = thisFont.manufacturer
			Glyphs.defaults[self.domain("manufacturerURL")] = thisFont.manufacturerURL
			Glyphs.defaults[self.domain("license")] = thisFont.license
			Glyphs.defaults[self.domain("fontDescription")] = thisFont.description
			try:
				Glyphs.defaults[self.domain("vendorID")] = thisFont.propertyForName_("vendorID").value
			except:
				pass
			try:
				Glyphs.defaults[self.domain("licenseURL")] = thisFont.propertyForName_("licenseURL").value
			except:
				pass

			# update checkboxes:
			# Glyphs.defaults[self.domain("setDate")] = True
			# Glyphs.defaults[self.domain("setVersion")] = True
			Glyphs.defaults[self.domain("setCopyright")] = bool(thisFont.copyright)
			Glyphs.defaults[self.domain("setTrademark")] = bool(thisFont.trademark)
			Glyphs.defaults[self.domain("setVendorID")] = bool(thisFont.propertyForName_("vendorID"))
			Glyphs.defaults[self.domain("setDesigner")] = bool(thisFont.designer)
			Glyphs.defaults[self.domain("setDesignerURL")] = bool(thisFont.designerURL)
			Glyphs.defaults[self.domain("setManufacturer")] = bool(thisFont.manufacturer)
			Glyphs.defaults[self.domain("setManufacturerURL")] = bool(thisFont.manufacturerURL)
			Glyphs.defaults[self.domain("setLicense")] = bool(thisFont.license)
			Glyphs.defaults[self.domain("setLicenseURL")] = bool(thisFont.propertyForName_("licenseURL"))
			Glyphs.defaults[self.domain("setFontDescription")] = bool(thisFont.description)

			# "containing" text box:
			name = thisFont.familyName.strip()
			words = name.split(" ")
			if len(words) > 1:
				potentialFoundryPrefix = len(words) == 2 and len(words[0]) < 4  # e.g. "GT Flexa"
				if not potentialFoundryPrefix:
					# get rid of last word in family name (e.g. "Sans"):
					name = " ".join(words[:-1])
			Glyphs.defaults[self.domain("applyContaining")] = name

			print()
			print(f'👨‍🎨 Designer: {thisFont.designer}')
			print(f'👨‍🎨 DesignerURL: {thisFont.designerURL}')
			print(f'👸‍ Manufacturer: {thisFont.manufacturer}')
			print(f'👸‍ ManufacturerURL: {thisFont.manufacturerURL}')
			print(f'👨🏻‍💼 License: {thisFont.license}')
			if thisFont.propertyForName_("licenseURL"):
				print(f'👨🏻‍💼 LicenseURL: {thisFont.propertyForName_("licenseURL").value}')
			else:
				print('👨🏻‍💼 LicenseURL: none')
			print(f"📝 Copyright: {thisFont.copyright}")
			print(f'📝 Trademark: {thisFont.trademark}')
			print(f'📝 Description: {thisFont.description}')
			if thisFont.propertyForName_("vendorID"):
				print(f'📝 Vendor ID: {thisFont.propertyForName_("vendorID").value}')
			else:
				print('📝 Vendor ID: none')
			print(f"🔢 Version: {thisFont.versionMajor}.{thisFont.versionMinor:03}")
			print(f'📆 Date: {thisFont.date}')
			print("\n✅ Done.")

			# update UI to the settings stored above:
			self.LoadPreferences()

	def FontInfoBatchSetterMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			# read prefs:
			applyContaining = self.pref("applyContaining")
			applyPopup = self.pref("applyPopup")
			copyright = self.pref("copyright")
			trademark = self.pref("trademark")
			vendorID = self.pref("vendorID")
			designer = self.pref("designer")
			designerURL = self.pref("designerURL")
			manufacturer = self.pref("manufacturer")
			manufacturerURL = self.pref("manufacturerURL")
			license = self.pref("license")
			licenseURL = self.pref("licenseURL")
			fontDescription = self.pref("fontDescription")

			setCopyright = self.pref("setCopyright")
			setTrademark = self.pref("setTrademark")
			setVendorID = self.pref("setVendorID")
			setDate = self.pref("setDate")
			setDesigner = self.pref("setDesigner")
			setDesignerURL = self.pref("setDesignerURL")
			setManufacturer = self.pref("setManufacturer")
			setManufacturerURL = self.pref("setManufacturerURL")
			setLicense = self.pref("setLicense")
			setLicenseURL = self.pref("setLicenseURL")
			setFontDescription = self.pref("setFontDescription")

			setVersion = self.pref("setVersion")
			versionMinor = self.prefInt("versionMinor")
			versionMajor = self.prefInt("versionMajor")
			dateInDatePicker = self.w.datePicker.get()

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

				for i, thisFont in enumerate(theseFonts):
					print(f"\n\n{i + 1}. {thisFont.familyName}:")
					self.reportFilePath(thisFont)
					print()

					currentChangeCount = changeCount

					if setVersion:
						if thisFont.versionMajor == versionMajor and thisFont.versionMinor == versionMinor:
							print("🆗 🔢 Font already has desired Version. No change.")
						else:
							thisFont.versionMajor = versionMajor
							thisFont.versionMinor = versionMinor
							print("✅ 🔢 Version set: %i.%03i" % (versionMajor, versionMinor))
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

					if setTrademark:
						individualTrademark = trademark.replace(self.placeholderFamilyName, thisFont.familyName)
						if thisFont.trademark == individualTrademark:
							print("🆗 📝 Font already has desired Trademark. No change.")
						else:
							thisFont.trademark = individualTrademark
							print("✅ 📝 Trademark set: %s" % individualTrademark)
							changeCount += 1

					if setVendorID:
						existingID = thisFont.propertyForName_("vendorID")
						if existingID and existingID.value == vendorID:
							print("🆗 📝 Font already has desired Vendor ID. No change.")
						else:
							addPropertyToFont(thisFont, "vendorID", vendorID)
							print("✅ 📝 Vendor ID set: %s" % vendorID)
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

					if setLicenseURL:
						if thisFont.propertyForName_("licenseURL").value == licenseURL:
							print("🆗 👨🏻‍💼 Font already has desired LicenseURL. No change.")
						else:
							thisFont.propertyForName_("licenseURL").value = licenseURL
							print("✅ 👨🏻‍💼 LicenseURL set: %s" % licenseURL)
							changeCount += 1

					if setLicense:
						if thisFont.license == license:
							print("🆗 👨🏻‍💼 Font already has desired License. No change.")
						else:
							thisFont.license = license
							print("✅ 👨🏻‍💼 License set: %s" % license)
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

					if setFontDescription:
						if thisFont.description == fontDescription:
							print("🆗 📛 Font already has desired fontDescription. No change.")
						else:
							thisFont.description = fontDescription
							print("✅ 📛 Description set: %s" % fontDescription)
							changeCount += 1

					if changeCount > currentChangeCount:
						changedFontsCount += 1

			# Final report:
			Message(
				title="Font Info Batch Setter: Done",
				message="Went through %i open font%s. Changed %i value%s in %i font%s. Details in Macro Window." % (
					len(theseFonts),
					"" if len(theseFonts) == 1 else "s",
					changeCount,
					"" if changeCount == 1 else "s",
					changedFontsCount,
					"" if changedFontsCount == 1 else "s",
				),
				OKButton=None,
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
