# MenuTitle: Font Info Batch Setter
__doc__ = """
Batch-apply Font Info > Font settings to open fonts: designer, designer URL, manufacturer, manufacturer URL, license, license URL, copyright, trademark, vendor ID, description, sample text, version number, and date/time. Useful for syncing Font Info settings across many fonts.
"""
import datetime
import objc
import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, Message
from AppKit import NSDate, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSNumberFormatter


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


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
		"sampleText": "The quick brown fox jumps over the lazy dog.",

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
		"setSampleText": False,

		"setDate": True,

		"setVersion": True,
		"versionMajor": "1",
		"versionMinor": "005",
	}
	placeholderFamilyName = "###familyName###"

	def __init__(self):
		# Window 'self.w':
		windowWidth = 450
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Font Info Batch Setter",  # window title
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.explanatoryText = vanilla.TextBox("auto", "Batch-set Font Info > Font of open fonts with these values:", sizeStyle="small", selectable=True)

		# DESIGNER
		self.w.setDesigner = vanilla.CheckBox("auto", "Designer:", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.designer = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		tooltipText = "Designer, name ID 9: Name of the designer of the typeface."
		self.w.setDesigner.setToolTip(tooltipText)
		self.w.designer.setToolTip(tooltipText)

		self.w.setDesignerURL = vanilla.CheckBox("auto", "Designer URL:", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.designerURL = vanilla.EditText("auto", "https://", callback=self.SavePreferences, sizeStyle="small")
		tooltipText = "Designer URL, name ID 12: URL of Designer. URL of typeface designer (with protocol, e.g., http://, ftp://)."
		self.w.setDesignerURL.setToolTip(tooltipText)
		self.w.designerURL.setToolTip(tooltipText)

		# MANUFACTURER
		self.w.setManufacturer = vanilla.CheckBox("auto", "Manufacturer:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.manufacturer = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		tooltipText = "Manufacturer Name, name ID 8."
		self.w.setManufacturer.setToolTip(tooltipText)
		self.w.manufacturer.setToolTip(tooltipText)

		self.w.setManufacturerURL = vanilla.CheckBox("auto", "Manufact.URL:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.manufacturerURL = vanilla.EditText("auto", "https://", callback=self.SavePreferences, sizeStyle="small")
		tooltipText = "Manufacturer URL, name ID 11: URL of Vendor. URL of font vendor (with protocol, e.g., http://, ftp://). If a unique serial number is embedded in the URL, it can be used to register the font."
		self.w.setManufacturerURL.setToolTip(tooltipText)
		self.w.manufacturerURL.setToolTip(tooltipText)

		# LICENSE
		self.w.setLicense = vanilla.CheckBox("auto", "License:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.license = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		tooltipText = "License, name ID 13: License Description. Description of the license or licenses under which the font is provided. This could be a reference to a named license agreement (e.g., a common open source licenses), identification of a software-use license under which a font is bundled, information about where to locate an external license (see also name ID 14), a summary of permitted uses, or the full legal text of a license agreement. It is prudent to seek legal advice on the content of this name ID to avoid possible conflict of interpretation between it and the license(s)."
		self.w.setLicense.setToolTip(tooltipText)
		self.w.license.setToolTip(tooltipText)

		self.w.setLicenseURL = vanilla.CheckBox("auto", "License URL:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.licenseURL = vanilla.EditText("auto", "https://", callback=self.SavePreferences, sizeStyle="small")
		tooltipText = "License URL, name ID 14: License Info URL. URL where additional licensing information can be found."
		self.w.setLicenseURL.setToolTip(tooltipText)
		self.w.licenseURL.setToolTip(tooltipText)

		# COPYRIGHT
		self.w.setCopyright = vanilla.CheckBox("auto", "Copyright:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.copyright = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		tooltipText = "Copyright, name ID 0: Copyright notice."
		self.w.setCopyright.setToolTip(tooltipText)
		self.w.copyright.setToolTip(tooltipText)

		# TRADEMARK
		self.w.setTrademark = vanilla.CheckBox("auto", "Trademark:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.trademark = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		tooltipText = f"Trademark, name ID 7: This is used to save any trademark notice/information for this font. Such information should be based on legal advice. This is distinctly separate from the copyright. Use {self.placeholderFamilyName} as placeholder for the current family name."
		self.w.setTrademark.setToolTip(tooltipText)
		self.w.trademark.setToolTip(tooltipText)

		# DESCRIPTION
		self.w.setFontDescription = vanilla.CheckBox("auto", "Description:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.fontDescription = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		tooltipText = f"Description, name ID 10: Description of the typeface. Can contain revision information, usage recommendations, history, features, etc. Use {self.placeholderFamilyName} as placeholder for the current family name."
		self.w.setFontDescription.setToolTip(tooltipText)
		self.w.fontDescription.setToolTip(tooltipText)

		# SAMPLE TEXT
		self.w.setSampleText = vanilla.CheckBox("auto", "Sample text:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.sampleText = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		tooltipText = f"Sample text, name ID 19: Sample text. This can be the font name, or any other text that the designer thinks is the best sample to display the font in. Use {self.placeholderFamilyName} as placeholder for the current family name."
		self.w.setSampleText.setToolTip(tooltipText)
		self.w.sampleText.setToolTip(tooltipText)

		# VENDOR ID
		self.w.setVendorID = vanilla.CheckBox("auto", "Vendor ID:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.vendorID = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")

		# VERSION NUMBER
		self.w.setVersion = vanilla.CheckBox("auto", "Version:", value=True, callback=self.SavePreferences, sizeStyle="small")
		versionFormatter = NSNumberFormatter.alloc().init()
		versionFormatter.setAllowsFloats_(False)  # integers only
		versionFormatter.setMinimum_(0)
		versionFormatter.setMaximum_(65535)  # the 16-bit limit of the version number
		self.w.versionMajor = SteppingEditText("auto", "1", callback=self.SavePreferences, sizeStyle="small", formatter=versionFormatter)
		self.w.versionDot = vanilla.TextBox("auto", ".", sizeStyle="small", selectable=True)
		self.w.versionMinor = vanilla.EditText("auto", "005", callback=self.SavePreferences, sizeStyle="small")
		tooltipText = "Version, used for building name ID 5: Version string. Should begin with the pattern “Version <number>.<number>” (upper case, lower case, or mixed, with a space between “Version” and the number). The string must contain a version number of the following form: one or more digits (0-9) of value less than 65,535, followed by a period, followed by one or more digits of value less than 65,535. Any character other than a digit will terminate the minor number."
		self.w.setVersion.setToolTip(tooltipText)
		self.w.versionMajor.setToolTip(tooltipText)
		self.w.versionMinor.setToolTip(tooltipText)

		self.w.versionMinorDecrease = vanilla.SquareButton("auto", "−", sizeStyle="small", callback=self.changeMinVersion)
		self.w.versionMinorDecrease.setToolTip("Decrease the version number by 0.001.")
		self.w.versionMinorIncrease = vanilla.SquareButton("auto", "+", sizeStyle="small", callback=self.changeMinVersion)
		self.w.versionMinorIncrease.setToolTip("Increase the version number by 0.001.")
		self.w.minVersionButton = vanilla.SquareButton("auto", "↻ 1.005", sizeStyle="small", callback=self.setVersion1005)
		self.w.minVersionButton.setToolTip("Resets the version to 1.005. Some (old?) Microsoft apps may consider fonts with smaller versions as unfinished and not display them in their font menu.")

		# DATE AND TIME
		self.w.setDate = vanilla.CheckBox("auto", "Date and time:", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.datePicker = vanilla.DatePicker(
			"auto",
			date=NSDate.alloc().init(),
			minDate=None,
			maxDate=None,
			showStepper=True,
			mode="text",
			timeDisplay="hourMinuteSecond",
			dateDisplay="yearMonthDay",
			callback=None,
			sizeStyle="small",
		)
		self.w.noonButton = vanilla.SquareButton("auto", "🕛 Today", sizeStyle="small", callback=self.setNoon)
		self.w.noonButton.setToolTip("Resets the date to today 12:00 noon.")

		# SEPARATOR
		self.w.separator = vanilla.HorizontalLine("auto")

		# APPLY TO FONTS
		self.w.finger = vanilla.TextBox("auto", "👉", selectable=True)
		self.w.applyText = vanilla.TextBox("auto", "Apply to", sizeStyle="small", selectable=True)
		self.w.applyPopup = vanilla.PopUpButton("auto", ("ALL open fonts", "open fonts containing"), sizeStyle="small", callback=self.SavePreferences)
		self.w.applyContaining = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small", placeholder="enter part of family name here")
		self.w.applyContaining.setToolTip("Only applies the settings to fonts that contain this in Font Info > Font > Family Name.")

		# Buttons:
		self.w.extractButton = vanilla.Button("auto", "Extract from Font", callback=self.ExtractFontInfoFromFrontmostFont)
		self.w.extractButton.setToolTip("Extracts the settings from the frontmost font and fills the UI with it.")
		self.w.runButton = vanilla.Button("auto", "Apply to Fonts", callback=self.FontInfoBatchSetterMain)
		self.w.runButton.setToolTip("Applies the checked settings above to all fonts indicated in the ‘Apply to’ option.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes and square buttons stretch vertically by default; with everything
		# hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the checkboxes in front of the fields share the width of the widest one, so the fields line up:
		checkBoxNames = (
			"setDesigner", "setDesignerURL", "setManufacturer", "setManufacturerURL", "setLicense", "setLicenseURL",
			"setCopyright", "setTrademark", "setFontDescription", "setSampleText", "setVendorID", "setVersion", "setDate",
		)
		for checkBoxName in checkBoxNames:
			nsCheckBox = getattr(self.w, checkBoxName).getNSButton()
			nsCheckBox.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsCheckBox.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widestCheckBox = "setManufacturerURL"  # the checkbox with the longest title
		widthRules = [
			{"view1": getattr(self.w, checkBoxName), "attribute1": "width", "view2": getattr(self.w, widestCheckBox), "attribute2": "width"}
			for checkBoxName in checkBoxNames if checkBoxName != widestCheckBox
		]

		# every row has one view in the vertical chain; the others share its centerY:
		centerRules = [
			{"view1": getattr(self.w, viewName), "attribute1": "centerY", "view2": getattr(self.w, rowViewName), "attribute2": "centerY"}
			for viewName, rowViewName in (
				("setDesigner", "designer"),
				("setDesignerURL", "designerURL"),
				("setManufacturer", "manufacturer"),
				("setManufacturerURL", "manufacturerURL"),
				("setLicense", "license"),
				("setLicenseURL", "licenseURL"),
				("setCopyright", "copyright"),
				("setTrademark", "trademark"),
				("setFontDescription", "fontDescription"),
				("setSampleText", "sampleText"),
				("setVendorID", "vendorID"),
				("setVersion", "versionMajor"),
				("versionDot", "versionMajor"),
				("versionMinor", "versionMajor"),
				("versionMinorDecrease", "versionMajor"),
				("versionMinorIncrease", "versionMajor"),
				("minVersionButton", "versionMajor"),
				("setDate", "datePicker"),
				("noonButton", "datePicker"),
				("finger", "applyPopup"),
				("applyText", "applyPopup"),
				("applyContaining", "applyPopup"),
			)
		]

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[explanatoryText]-inset-|",
				"H:|-inset-[setDesigner]-gap-[designer]-inset-|",
				"H:|-inset-[setDesignerURL]-gap-[designerURL]-inset-|",
				"H:|-inset-[setManufacturer]-gap-[manufacturer]-inset-|",
				"H:|-inset-[setManufacturerURL]-gap-[manufacturerURL]-inset-|",
				"H:|-inset-[setLicense]-gap-[license]-inset-|",
				"H:|-inset-[setLicenseURL]-gap-[licenseURL]-inset-|",
				"H:|-inset-[setCopyright]-gap-[copyright]-inset-|",
				"H:|-inset-[setTrademark]-gap-[trademark]-inset-|",
				"H:|-inset-[setFontDescription]-gap-[fontDescription]-inset-|",
				"H:|-inset-[setSampleText]-gap-[sampleText]-inset-|",
				"H:|-inset-[setVendorID]-gap-[vendorID]-inset-|",
				"H:|-inset-[setVersion]-gap-[versionMajor(50)]-dot-[versionDot]-dot-[versionMinor(60)]-gap-[versionMinorDecrease(24)]-dot-[versionMinorIncrease(24)]-gap-[minVersionButton(>=70)]-(>=inset)-|",
				"H:|-inset-[setDate]-gap-[datePicker]-gap-[noonButton(>=70)]-(>=inset)-|",
				"H:|-inset-[separator]-inset-|",
				"H:|-inset-[finger]-dot-[applyText]-gap-[applyPopup]-gap-[applyContaining(>=150)]-inset-|",
				"H:|-(>=inset)-[extractButton(>=70)]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[explanatoryText]-headlineGap-[designer]-row-[designerURL]-row-[manufacturer]-row-[manufacturerURL]-row-[license]-row-[licenseURL]-row-[copyright]-row-[trademark]-row-[fontDescription]-row-[sampleText]-row-[vendorID]-row-[versionMajor]-row-[datePicker]-row-[separator(1)]-row-[applyPopup]-inset-[runButton]-inset-|",
				"V:[extractButton]-inset-|",
				"V:[versionMinorDecrease(20)]",
				"V:[versionMinorIncrease(20)]",
				"V:[minVersionButton(20)]",
				"V:[noonButton(20)]",
			] + centerRules + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 6, "headlineGap": 12, "dot": 4},
		)

		# Load Settings:
		self.LoadPreferences()

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

	def updateUI(self, sender=None):
		self.w.designer.enable(self.w.setDesigner.get())
		self.w.designerURL.enable(self.w.setDesignerURL.get())
		self.w.manufacturer.enable(self.w.setManufacturer.get())
		self.w.manufacturerURL.enable(self.w.setManufacturerURL.get())
		self.w.license.enable(self.w.setLicense.get())
		self.w.licenseURL.enable(self.w.setLicenseURL.get())
		self.w.copyright.enable(self.w.setCopyright.get())
		self.w.trademark.enable(self.w.setTrademark.get())
		self.w.vendorID.enable(self.w.setVendorID.get())
		self.w.fontDescription.enable(self.w.setFontDescription.get())
		self.w.sampleText.enable(self.w.setSampleText.get())

		dateEnabled = self.w.setDate.get()
		self.w.datePicker.enable(dateEnabled)
		self.w.noonButton.enable(dateEnabled)

		versionEnabled = self.w.setVersion.get()
		self.w.versionMajor.enable(versionEnabled)
		self.w.versionMinor.enable(versionEnabled)
		self.w.minVersionButton.enable(versionEnabled)

		self.w.applyContaining.show(self.w.applyPopup.get())  # 0=all fonts, 1=fonts containing, here repurposed as bool
		applySettingsEnable = self.w.applyPopup.get() == 0 or len(self.w.applyContaining.get().strip()) > 0

		anyCheckboxOn = (
			dateEnabled or versionEnabled
			or self.w.setDesigner.get() or self.w.setDesignerURL.get()
			or self.w.setManufacturer.get() or self.w.setManufacturerURL.get()
			or self.w.setCopyright.get() or self.w.setTrademark.get()
			or self.w.setLicense.get() or self.w.setLicenseURL.get()
			or self.w.setVendorID.get() or self.w.setFontDescription.get()
			or self.w.setSampleText.get()
		)
		self.w.runButton.enable(anyCheckboxOn and applySettingsEnable)

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
			Glyphs.defaults[self.domain("versionMajor")] = str(thisFont.versionMajor)
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
			Glyphs.defaults[self.domain("sampleText")] = thisFont.sampleText
			try:
				Glyphs.defaults[self.domain("vendorID")] = thisFont.propertyForName_("vendorID").value
			except Exception:
				pass
			try:
				Glyphs.defaults[self.domain("licenseURL")] = thisFont.propertyForName_("licenseURL").value
			except Exception:
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
			Glyphs.defaults[self.domain("setSampleText")] = bool(thisFont.sampleText)

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
			print(f'👨‍🎨 Designer URL: {thisFont.designerURL}')
			print(f'👸‍ Manufacturer: {thisFont.manufacturer}')
			print(f'👸‍ Manufacturer URL: {thisFont.manufacturerURL}')
			print(f'👨🏻‍💼 License: {thisFont.license}')
			if thisFont.propertyForName_("licenseURL"):
				print(f'👨🏻‍💼 License URL: {thisFont.propertyForName_("licenseURL").value}')
			else:
				print('👨🏻‍💼 License URL: none')
			print(f"📝 Copyright: {thisFont.copyright}")
			print(f'📝 Trademark: {thisFont.trademark}')
			print(f'📝 Description: {thisFont.description}')
			print(f'📝 Sample Text: {thisFont.sampleText}')
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
			sampleText = self.pref("sampleText")

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
			setSampleText = self.pref("setSampleText")

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

			if not theseFonts or None in theseFonts:
				self.complainAboutNoFonts()
				return
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
							print(f"✅ 📆 Date set: {dateInDatePicker}")
							changeCount += 1

					if setCopyright:
						if thisFont.copyright == copyright:
							print("🆗 📝 Font already has desired Copyright. No change.")
						else:
							thisFont.copyright = copyright
							print(f"✅ 📝 Copyright set: {copyright}")
							changeCount += 1

					if setTrademark:
						individualTrademark = trademark.replace(self.placeholderFamilyName, thisFont.familyName)
						if thisFont.trademark == individualTrademark:
							print("🆗 📝 Font already has desired Trademark. No change.")
						else:
							thisFont.trademark = individualTrademark
							print(f"✅ 📝 Trademark set: {individualTrademark}")
							changeCount += 1

					if setVendorID:
						existingID = thisFont.propertyForName_("vendorID")
						if existingID and existingID.value == vendorID:
							print("🆗 📝 Font already has desired Vendor ID. No change.")
						else:
							addPropertyToFont(thisFont, "vendorID", vendorID)
							print(f"✅ 📝 Vendor ID set: {vendorID}")
							changeCount += 1

					if setManufacturerURL:
						if thisFont.manufacturerURL == manufacturerURL:
							print("🆗 👸 Font already has desired ManufacturerURL. No change.")
						else:
							thisFont.manufacturerURL = manufacturerURL
							print(f"✅ 👸 ManufacturerURL set: {manufacturerURL}")
							changeCount += 1

					if setManufacturer:
						if thisFont.manufacturer == manufacturer:
							print("🆗 👸 Font already has desired Manufacturer. No change.")
						else:
							thisFont.manufacturer = manufacturer
							print(f"✅ 👸 Manufacturer set: {manufacturer}")
							changeCount += 1

					if setLicenseURL:
						existingLicense = thisFont.propertyForName_("licenseURL")
						if existingLicense and existingLicense.value == licenseURL:
							print("🆗 👨🏻‍💼 Font already has desired LicenseURL. No change.")
						else:
							addPropertyToFont(thisFont, "licenseURL", licenseURL)
							print(f"✅ 👨🏻‍💼 LicenseURL set: {licenseURL}")
							changeCount += 1

					if setLicense:
						if thisFont.license == license:
							print("🆗 👨🏻‍💼 Font already has desired License. No change.")
						else:
							thisFont.license = license
							print(f"✅ 👨🏻‍💼 License set: {license}")
							changeCount += 1

					if setDesignerURL:
						if thisFont.designerURL == designerURL:
							print("🆗 👨‍🎨 Font already has desired DesignerURL. No change.")
						else:
							thisFont.designerURL = designerURL
							print(f"✅ 👨‍🎨 DesignerURL set: {designerURL}")
							changeCount += 1

					if setDesigner:
						if thisFont.designer == designer:
							print("🆗 👨‍🎨 Font already has desired Designer. No change.")
						else:
							thisFont.designer = designer
							print(f"✅ 👨‍🎨 Designer set: {designer}")
							changeCount += 1

					if setFontDescription:
						if thisFont.description == fontDescription:
							print("🆗 📛 Font already has desired fontDescription. No change.")
						else:
							thisFont.description = fontDescription
							print(f"✅ 📛 Description set: {fontDescription}")
							changeCount += 1

					if setSampleText:
						if thisFont.sampleText == sampleText:
							print("🆗 🧪 Font already has desired sampleText. No change.")
						else:
							thisFont.sampleText = sampleText
							print(f"✅ 🧪 Sample text set: {sampleText}")
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
