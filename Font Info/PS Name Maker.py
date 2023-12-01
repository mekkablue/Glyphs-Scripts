#MenuTitle: PS Name Maker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Creates postscriptFontName entries (Name ID 6) for all instances with options to shorten them.
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

def removePSNameFromInstance(i, key="postscriptFontName"):
	for cpIndex in range(len(i.customParameters)-1,-1,-1):
		cp = i.customParameters[cpIndex]
		if cp.name == "Name Table Entry" and cp.value.split(";")[0].split()[0]=="6":
			del i.customParameters[cpIndex]
			
	while i.propertyForName_(key):
		i.removeObjectFromProperties_(i.propertyForName_(key))
	
def addPSNameToInstance(i, shorten=False, asCustomParameter=True):
	allowedChars = ascii_letters+digits
	familyName = i.familyName
	if not familyName:
		familyName = i.font.familyName
	psFamilyName = "".join([x for x in familyName if x in allowedChars])
	psStyleName = "".join([x for x in i.name if x in allowedChars])
	if shorten:
		psStyleName = shortenPSStyleName(psStyleName)
	psFontName = f"{psFamilyName}-{psStyleName}"
	
	removePSNameFromInstance(i)

	if asCustomParameter:
		i.customParameters["Name Table Entry"] = f"6; {psFontName}"
	else:
		psName = GSFontInfoValueSingle()
		psName.key = "postscriptFontName"
		psName.value = psFontName
		i.properties.append(psName)
	
	print(f"✅ {i.font.familyName} {i.name}: {psFontName}")

class PSNameMaker(object):
	prefID = "com.mekkablue.PSNameMaker"
	prefDict = {
		# "prefName": defaultValue,
		"addAsNameEntryParameter": 1,
		"shortenStyleNames": 1,
		"allFonts": 0,
		"includeInactiveInstances": 1,
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 180
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"PS Name Maker", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Recalculates and resets PS Names in instances:", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		self.w.addAsNameEntryParameter = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Add as custom parameter (OTVAR safe)", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.shortenStyleNames = vanilla.CheckBox((inset, linePos-1, -inset-30, 20), "Shorten style names (Tech Note #5088)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.helpButton = vanilla.HelpButton((-inset-28, linePos-3, -inset, 25), callback=self.openURL)
		linePos += lineHeight
		
		self.w.allFonts = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Apply to ⚠️ ALL open fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.includeInactiveInstances = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Include inactive instances", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight
		
		self.w.removeButton = vanilla.Button((inset, -20-inset, 90, -inset), "Remove", sizeStyle="regular", callback=self.PSNameMakerMain)
		
		
		
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Add", sizeStyle="regular", callback=self.PSNameMakerMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘PS Name Maker’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
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
	
	def openURL(self, sender=None):
		from webbrowser import open as openURL
		url = "https://github.com/adobe-type-tools/font-tech-notes/blob/main/pdfs/5088.FontNames.pdf"
		openURL(url)
		
	def PSNameMakerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘PS Name Maker’ could not write preferences.")
			
			# read prefs:
			includeInactiveInstances = self.pref("includeInactiveInstances")
			shortenStyleNames = self.pref("shortenStyleNames")
			remove = sender==self.w.removeButton
			addAsNameEntryParameter = self.pref("addAsNameEntryParameter")
			
			if not Glyphs.fonts:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				if self.pref("allFonts"):
					theseFonts = Glyphs.fonts
				else:
					theseFonts = (Glyphs.font,)
				
				for thisFont in theseFonts:
					filePath = thisFont.filepath
					if filePath:
						reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
					else:
						reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
					print(f"PS Name Maker Report for {reportName}")
					print()
					for thisInstance in thisFont.instances:
						if thisInstance.type == INSTANCETYPESINGLE:
							if includeInactiveInstances or thisInstance.active:
								if remove:
									removePSNameFromInstance(thisInstance)
									print(f"⌦ ‘{thisInstance.name}’ cleared of PS Names.")
								else:
									addPSNameToInstance(thisInstance, shorten=shortenStyleNames, asCustomParameter=addAsNameEntryParameter)
							else:
								print(f"⏭️ ‘{thisInstance.name}’ is inactive: skipping.")
					print()

			print("Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"PS Name Maker Error: {e}")
			import traceback
			print(traceback.format_exc())

PSNameMaker()