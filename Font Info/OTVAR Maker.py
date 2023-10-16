#MenuTitle: OTVAR Maker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Creates a variable font setting in Font Info > Exports.
"""

import vanilla, sys
from string import ascii_letters, digits

def shortenPSStyleName(psStyleName):
	shortDict = {
		"Bold": "Bd",
		"Book": "Bk",
		"Black": "Blk",
		"Compressed": "Cm",
		"Condensed": "Cn",
		"Compact": "Ct",
		"Display": "Ds",
		"Extended": "Ex",
		"Heavy": "Hv",
		"Inclined": "Ic",
		"Italic": "It",
		"Kursiv": "Ks",
		"Light": "Lt",
		"Medium": "Md",
		"Nord": "Nd",
		"Narrow": "Nr",
		"Oblique": "Obl",
		"Poster": "Po",
		"Regular": "Rg",
		"Slanted": "Sl",
		"Super": "Su",
		"Thin": "Th",
		"Upright": "Up",
	}
	prefixDict = {
		"Demi": "Dm",
		"Semi": "Sm",
		"Ultra": "Ult",
		"Extra": "X",
	}
	
	for longWord in shortDict.keys():
		abbreviation = shortDict[longWord]
		psStyleName = psStyleName.replace(longWord, abbreviation)
		psStyleName = psStyleName.replace(longWord.lower(), abbreviation)
	
	for longWord in prefixDict.keys():
		abbreviation = prefixDict[longWord]
		if psStyleName.endswith(longWord):
			split = -len(longWord)
			psStyleName = psStyleName[:split].replace(longWord, abbreviation) + psStyleName[split:]
		else:
			psStyleName = psStyleName.replace(longWord, abbreviation)
			
	return psStyleName

def psVersionOfName(name, shorten=False):
	allowedChars = ascii_letters+digits
	psName = "".join([x for x in name if x in allowedChars])
	if shorten:
		psName = shortenPSStyleName(psName)
	return psName

class OTVARMaker(object):
	prefID = "com.mekkablue.OTVARMaker"
	prefDict = {
		# "prefName": defaultValue,
		"suffix": "VF",
		"psSuffix": "Roman",
		"allFonts": True,
		"deletePrevious": True,
		"addFileName": False,
	}
	
	suffixSuggestions = (
		"VF",
		"Variable",
		"Var",
		"VAR",
		"OTVAR",
	)

	psSuffixSuggestions = (
		"Roman",
		"Upright",
		"Normal",
		"Regular",
	)
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 290
		windowHeight = 200
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"OTVAR Maker", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos+2, -inset, 14), "Add Variable Font Setting in Font Info > Exports:", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		indent = 130
		self.w.suffixText = vanilla.TextBox((inset, linePos+2, indent, 14), "Family name suffix", sizeStyle="small", selectable=True)
		self.w.suffix = vanilla.ComboBox((inset+indent, linePos-2, -inset, 20), self.suffixSuggestions, sizeStyle="small", callback=self.SavePreferences)
		tooltip = "This is the extension that will be added to your OTVAR family name in order to differentiate it from the static family name."
		self.w.suffixText.getNSTextField().setToolTip_(tooltip)
		self.w.suffix.getNSComboBox().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.psSuffixText = vanilla.TextBox((inset, linePos+2, indent, 14), "Non-italic PS extension", sizeStyle="small", selectable=True)
		self.w.psSuffix = vanilla.ComboBox((inset+indent, linePos-2, -inset, 20), self.psSuffixSuggestions, sizeStyle="small", callback=self.SavePreferences)
		tooltip = "Only applies to fonts that are entirely non-italic. The Variations PostScript Name Prefix (nameID 25) should have an extension like Roman or Regular to differentiate it clearly from a pure Italic. Important for setups where uprights and italics are in different files. Also has an effect on the file name if you use that option (see below)."
		self.w.psSuffixText.getNSTextField().setToolTip_(tooltip)
		self.w.psSuffix.getNSComboBox().setToolTip_(tooltip)
		linePos += lineHeight
		
		self.w.addFileName = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Add fileName parameter", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.addFileName.getNSButton().setToolTip_("Adds a custom parameter for overriding the default file name of the font file.")
		linePos += lineHeight
		
		self.w.deletePrevious = vanilla.CheckBox((inset, linePos-1, -inset, 20), "⚠️ Remove previous variable font settings", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.deletePrevious.getNSButton().setToolTip_("Deletes all variable font settings that you may already have in your file(s).")
		linePos += lineHeight
		
		self.w.allFonts = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Apply to ⚠️ ALL open fonts", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.allFonts.getNSButton().setToolTip_("Adds Variable Font Settings to all fonts currently open in Glyphs.")
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Add", sizeStyle="regular", callback=self.OTVARMakerMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘OTVAR Maker’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def guiCheck(self, sender=None):
		enable = bool(self.pref("suffix").strip())
		self.w.runButton.enable(enable)
		
	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
			self.guiCheck()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				getattr(self.w, prefName).set(self.pref(prefName))
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def OTVARMakerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘OTVAR Maker’ could not write preferences.")
			
			# read prefs:
			suffix = self.pref("suffix")
			psSuffix = self.pref("psSuffix")
			allFonts = self.pref("allFonts")
			deletePrevious = self.pref("deletePrevious")
			addFileName = self.pref("addFileName")
			
			if Glyphs.font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			if allFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font,)
			
			for thisFont in theseFonts:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"OTVAR Maker Report for {reportName}")
				print()
				
				if deletePrevious:
					for i in range(len(thisFont.instances)-1, -1, -1):
						existingInstance = thisFont.instances[i]
						if existingInstance.type == INSTANCETYPEVARIABLE:
							print(f"🚫 Removing existing VF setting ‘{existingInstance.name}’...")
							del thisFont.instances[i]
				
				# this does not work (yet):
				# otvarInstance = GSInstance()
				# otvarInstance.type = INSTANCETYPEVARIABLE
				# so we have to do it like this:
				otvarInstance = GSInstance.alloc().initWithType_(INSTANCETYPEVARIABLE)
				otvarInstance.font = thisFont
				otvarInstance.familyName = f"{thisFont.familyName.strip()} {suffix.strip()}".strip()
				
				# Regular vs. Italic
				allMastersHaveAnAngle = all([m.italicAngle != 0.0 for m in thisFont.masters])
				allInstancesAreCalledItalic = all(["Italic" in i.name for i in Font.instances if i.type == INSTANCETYPESINGLE])
				isItalic = allMastersHaveAnAngle or allInstancesAreCalledItalic
				if isItalic:
					otvarInstance.name = "Italic"
				else:
					otvarInstance.name = "Regular"
				
				# name ID 25
				variationsPostScriptNamePrefix = GSFontInfoValueSingle()
				variationsPostScriptNamePrefix.key = "variationsPostScriptNamePrefix"
				psFamilyName = psVersionOfName(otvarInstance.familyName)
				extension = "Italic" if isItalic else psSuffix.strip().replace(" ", "")
				if not psFamilyName.endswith(extension):
					psFamilyName += extension
				variationsPostScriptNamePrefix.value = psFamilyName
				otvarInstance.properties.append(variationsPostScriptNamePrefix)
				
				# file name
				if addFileName:
					fileName = otvarInstance.familyName
					if not fileName.endswith(extension):
						fileName = f"{fileName} {extension}"
					if fileName:
						otvarInstance.customParameters["fileName"] = fileName
				
				# add VFS to instances:
				print(f"✅ Adding Variable Font Setting ‘{otvarInstance.familyName} {otvarInstance.name}’")
				thisFont.instances.insert(0, otvarInstance)

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"OTVAR Maker Error: {e}")
			import traceback
			print(traceback.format_exc())

OTVARMaker()