#MenuTitle: Batch-Import Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Import many masters at once with the Import Master parameter.
"""

import vanilla, sys

def menuForFonts(fonts):
	menu = []
	for i, font in enumerate(fonts):
		menu.append(f"{i+1}. {font.familyName} ({font.filepath.lastPathComponent()})")
	return menu

def masterNameParticlesForFont(font, separators = ".,-:/"):
	allParticles = []
	for m in font.masters:
		particles = m.name.split()
		for sep in separators:
			newParticles = []
			for particle in particles:
				newParticles.extend(particle.split(sep))
			particles = newParticles
		allParticles.extend(particles)
	return set(allParticles)

def cleanParametersFromFont(font, cpName="Import Master"):
	while font.customParameters[cpName]:
		font.removeObjectFromCustomParametersForKey_(cpName)

def importMastersFromFontToFont(importedFont, targetFont, searchFor="", useRelativePath=False):
	importedPath = importedFont.filepath
	importedFileName = importedPath.lastPathComponent()
	importedDir = importedPath.stringByDeletingLastPathComponent()
	importedRelativePath = importedPath.relativePathFromBaseDirPath_(targetFont.filepath.stringByDeletingLastPathComponent())
	for importedMaster in importedFont.masters:
		if searchFor and not searchFor in importedMaster.name:
			continue
		cpName = "Import Master"
		cpValue = {
			"Master": importedMaster.name,
			"Path": importedRelativePath if useRelativePath else importedPath,
			}
		cp = GSCustomParameter(cpName, cpValue)
		targetFont.customParameters.append(cp)
		print(f"✅ Added master: {importedMaster.name}")

class BatchImportMasters(object):
	prefID = "com.mekkablue.BatchImportMasters"
	prefDict = {
		# "prefName": defaultValue,
		"sourceFont": 0,
		"targetFont": 0,
		"searchFor": "",
		"useRelativePath": True,
		"resetParameters": True,
	}
	
	currentFonts = Glyphs.fonts
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 210
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Batch-Import Masters", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Batch-add ‘Import Master’ parameters to target font:", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		indent = 75
		self.w.targetFontText = vanilla.TextBox((inset, linePos+2, indent, 14), "Target font:", sizeStyle="small", selectable=True)
		self.w.targetFont = vanilla.PopUpButton((inset+indent, linePos, -inset, 17), (), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "The font that receives the Import Master parameters."
		self.w.targetFont.getNSPopUpButton().setToolTip_(tooltip)
		self.w.targetFontText.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight
		
		self.w.sourceFontText = vanilla.TextBox((inset, linePos+2, indent, 14), "Source font:", sizeStyle="small", selectable=True)
		self.w.sourceFont = vanilla.PopUpButton((inset+indent, linePos, -inset, 17), (), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "The font the custom parameters refer to."
		self.w.sourceFont.getNSPopUpButton().setToolTip_(tooltip)
		self.w.sourceFontText.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight
		
		indent = 195
		self.w.searchForText = vanilla.TextBox((inset, linePos+2, indent, 14), "Source master name must contain:", sizeStyle="small", selectable=True)
		self.w.searchFor = vanilla.ComboBox((inset+indent, linePos-1, -inset, 19), masterNameParticlesForFont(self.currentFonts[0]), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "If set, will only import masters that contain this name particle. Leave empty to import all masters of the source font."
		self.w.searchFor.getNSComboBox().setToolTip_(tooltip)
		self.w.searchForText.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight
		
		self.w.useRelativePath = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Use relative font path in parameter values", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.useRelativePath.getNSButton().setToolTip_("If set, will add a relative path rather than an absolute path. Better for git repos.")
		linePos += lineHeight
		
		self.w.resetParameters = vanilla.CheckBox((inset, linePos-1, -inset, 20), "Delete all existing Import Master parameters in target font", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.resetParameters.getNSButton().setToolTip_("If set, will first clean out all existing ‘Import Master’ parameters, so the font will only have the ‘Import Master’ parameters you add.")
		linePos += lineHeight
		
		# Update Button:
		self.w.updateButton = vanilla.Button((inset, -20-inset, 100, -inset), "Update", sizeStyle="regular", callback=self.UpdateUI)
		self.w.updateButton.getNSButton().setToolTip_("Will update all the menus and buttons of this window. Click here if you opened or closed a font since you invoked the script, or after you changed the source font.")
		
		# Run Button:
		self.w.runButton = vanilla.Button((-100-inset, -20-inset, -inset, -inset), "Import", sizeStyle="regular", callback=self.BatchImportMastersMain)
		self.w.setDefaultButton(self.w.runButton)
		
		self.UpdateUI()
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Batch-Import Masters’ could not load preferences. Will resort to defaults.")
		
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
			self.UpdateUI(sender=sender)
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self, sender=None):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				getattr(self.w, prefName).set(self.pref(prefName))
			self.UpdateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False
	
	def UpdateUI(self, sender=None):
		self.currentFonts = Glyphs.fonts
		menu = menuForFonts(self.currentFonts)
		if menu:
			self.w.sourceFont.setItems(menu)
			sourceFontIndex = self.pref("sourceFont")
			self.w.sourceFont.set(sourceFontIndex if sourceFontIndex != None and sourceFontIndex < len(menu) else 0)
			Glyphs.defaults[self.domain("sourceFont")] = self.w.sourceFont.get()
			
			self.w.targetFont.setItems(menu)
			targetFontIndex = self.pref("targetFont")
			self.w.targetFont.set(targetFontIndex if targetFontIndex != None and targetFontIndex < len(menu) else 0)
			Glyphs.defaults[self.domain("targetFont")] = self.w.targetFont.get()
		
		# update search combobox :
		if sender != self.w.searchFor:
			searchBoxContent = self.w.searchFor.get()
			sourceFont = self.currentFonts[self.w.sourceFont.get()]
			particles = masterNameParticlesForFont(sourceFont)
			self.w.searchFor.setItems(particles)
			self.w.searchFor.set(searchBoxContent) # circumvent bug
		
		# double check
		self.w.runButton.enable(self.pref("sourceFont")!=self.pref("targetFont"))
		
	def BatchImportMastersMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Batch-Import Masters’ could not write preferences.")
			
			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(sys.modules[__name__], prefName, self.pref(prefName))
				except:
					fallbackValue = self.prefDict[prefName]
					print(f"⚠️ Could not set pref ‘{prefName}’, resorting to default value: ‘{fallbackValue}’.")
					setattr(sys.modules[__name__], prefName, fallbackValue)
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print(f"Batch-Import Masters Report")
			
				font = self.currentFonts[self.pref("targetFont")]
				importedFont = self.currentFonts[self.pref("sourceFont")]

				print("Target:", font.filepath.lastPathComponent())
				print("Source:", importedFont.filepath.lastPathComponent())
				print()

				font.disableUpdateInterface()
				try:
					if resetParameters:
						cleanParametersFromFont(font, cpName="Import Master")
					importMastersFromFontToFont(importedFont, font, searchFor=searchFor, useRelativePath=useRelativePath)
				except Exception as e:
					raise e
				finally:
					font.enableUpdateInterface()
					print("\n✅ Done.")

				# self.w.close() # delete if you want window to stay open

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Batch-Import Masters Error: {e}")
			import traceback
			print(traceback.format_exc())

BatchImportMasters()