#MenuTitle: Remove Kerning Between Categories
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Removes kerning between glyphs, categories, subcategories, scripts.
"""

import vanilla

class RemoveKerning( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 610
		windowHeight = 240
		windowWidthResize  = 0 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Remove Kerning", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.RemoveKerning.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Removes group and singleton kerning between the following glyphs:", sizeStyle='small', selectable=True )
		linePos += lineHeight
				
		self.w.leftCategoryText = vanilla.TextBox( (inset, linePos+2, 100, 14), u"L Category:", sizeStyle='small', selectable=True )
		self.w.leftCategory = vanilla.PopUpButton( (inset+100, linePos, 180, 17), (), sizeStyle='small', callback=self.buttonEnable )
		self.w.rightCategoryText = vanilla.TextBox( (300+inset, linePos+2, 100, 14), u"R Category:", sizeStyle='small', selectable=True )
		self.w.rightCategory = vanilla.PopUpButton( (300+inset+100, linePos, 180, 17), (), sizeStyle='small', callback=self.buttonEnable )
		linePos += lineHeight
		
		self.w.leftSubCategoryText = vanilla.TextBox( (inset, linePos+2, 100, 14), u"L Subcategory:", sizeStyle='small', selectable=True )
		self.w.leftSubCategory = vanilla.PopUpButton( (inset+100, linePos, 180, 17), (), sizeStyle='small', callback=self.buttonEnable )
		self.w.rightSubCategoryText = vanilla.TextBox( (300+inset, linePos+2, 100, 14), u"R Subcategory:", sizeStyle='small', selectable=True )
		self.w.rightSubCategory = vanilla.PopUpButton( (300+inset+100, linePos, 180, 17), (), sizeStyle='small', callback=self.buttonEnable )
		linePos += lineHeight
		
		self.w.leftScriptText = vanilla.TextBox( (inset, linePos+2, 100, 14), u"L Script:", sizeStyle='small', selectable=True )
		self.w.leftScript = vanilla.PopUpButton( (inset+100, linePos, 180, 17), (), sizeStyle='small', callback=self.buttonEnable )
		self.w.rightScriptText = vanilla.TextBox( (300+inset, linePos+2, 100, 14), u"R Script:", sizeStyle='small', selectable=True )
		self.w.rightScript = vanilla.PopUpButton( (300+inset+100, linePos, 180, 17), (), sizeStyle='small', callback=self.buttonEnable )
		linePos += lineHeight
		
		self.ReloadCategories()
		
		self.w.includeDirtyCategories = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Delete group kerning even if groups are ‘dirty’ (e.g., group with uppercase and lowercase letters mixed)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.reportInMacroWindow = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Detailed report in macro window", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.processAllMasters = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Process all masters (otherwise current master only)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		self.w.statusText = vanilla.TextBox( (inset, -20-inset, 300, 14), u"", sizeStyle='small', selectable=True )
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Remove", sizeStyle='regular', callback=self.RemoveKerningMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Reload Button:
		self.w.reloadButton = vanilla.Button( (-220-inset, -20-inset, -130-inset, -inset), "Reload", sizeStyle='regular', callback=self.ReloadCategories )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Remove Kerning' could not load preferences. Will resort to defaults")
		
		self.buttonEnable()
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def ReloadCategories(self, sender=None):
		try:
			categories = ["Any"] + self.allCategories()
			subcategories = ["Any"] + self.allSubCategories()
			scripts = ["Any"] + self.allScripts()
			self.w.leftCategory.setItems(categories)
			self.w.rightCategory.setItems(categories)
			self.w.leftSubCategory.setItems(subcategories)
			self.w.rightSubCategory.setItems(subcategories)
			self.w.leftScript.setItems(scripts)
			self.w.rightScript.setItems(scripts)
		except Exception as e:
			print(e)
	
	def allCategories(self, sender=None):
		if not Glyphs.font:
			return []
		else:
			categories=[]
			for thisGlyph in Glyphs.font.glyphs:
				if thisGlyph.category and not thisGlyph.category in categories:
					categories.append(thisGlyph.category)
			return categories
			
	def buttonEnable(self, sender=None):
		count=0
		count+=self.w.leftCategory.get()
		count+=self.w.rightCategory.get()
		count+=self.w.leftSubCategory.get()
		count+=self.w.rightSubCategory.get()
		count+=self.w.leftScript.get()
		count+=self.w.rightScript.get()
		if count > 0:
			self.w.runButton.enable(True)
		else:
			self.w.runButton.enable(False)
		
	def allSubCategories(self, sender=None):
		if not Glyphs.font:
			return []
		else:
			subcategories=[]
			for thisGlyph in Glyphs.font.glyphs:
				if thisGlyph.subCategory and not thisGlyph.subCategory in subcategories:
					subcategories.append(thisGlyph.subCategory)
			return subcategories
		
	def allScripts(self, sender=None):
		if not Glyphs.font:
			return []
		else:
			scripts=[]
			for thisGlyph in Glyphs.font.glyphs:
				if thisGlyph.script and not thisGlyph.script in scripts:
					scripts.append(thisGlyph.script)
			return scripts
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.RemoveKerning.includeDirtyCategories"] = self.w.includeDirtyCategories.get()
			Glyphs.defaults["com.mekkablue.RemoveKerning.reportInMacroWindow"] = self.w.reportInMacroWindow.get()
			Glyphs.defaults["com.mekkablue.RemoveKerning.processAllMasters"] = self.w.processAllMasters.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.RemoveKerning.includeDirtyCategories", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveKerning.reportInMacroWindow", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveKerning.processAllMasters", 0)
			self.w.includeDirtyCategories.set( Glyphs.defaults["com.mekkablue.RemoveKerning.includeDirtyCategories"] )
			self.w.reportInMacroWindow.set( Glyphs.defaults["com.mekkablue.RemoveKerning.reportInMacroWindow"] )
			self.w.processAllMasters.set( Glyphs.defaults["com.mekkablue.RemoveKerning.processAllMasters"] )
		except:
			return False
			
		return True
	
	def status(self, statusmsg, macroWindow=False):
		self.w.statusText.set(statusmsg)
		if macroWindow:
			print(" %s"%statusmsg)

	def RemoveKerningMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Remove Kerning' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			includeDirtyCategories = Glyphs.defaults["com.mekkablue.RemoveKerning.includeDirtyCategories"]
			reportInMacroWindow = Glyphs.defaults["com.mekkablue.RemoveKerning.reportInMacroWindow"]

			# brings macro window to front and clears its log:
			if reportInMacroWindow:
				Glyphs.clearLog()
			
			print("'Remove Kerning' Report for: %s" % thisFont.familyName)
			if thisFont.filepath:
				print(thisFont.filepath)
				print()
			
			leftCategory = self.w.leftCategory.getItems()[ self.w.leftCategory.get() ]
			leftSubCategory = self.w.leftSubCategory.getItems()[ self.w.leftSubCategory.get() ]
			leftScript = self.w.leftScript.getItems()[ self.w.leftScript.get() ]
			
			rightCategory = self.w.rightCategory.getItems()[ self.w.rightCategory.get() ]
			rightSubCategory = self.w.rightSubCategory.getItems()[ self.w.rightSubCategory.get() ]
			rightScript = self.w.rightScript.getItems()[ self.w.rightScript.get() ]
			
			leftGlyphNames, rightGlyphNames = [], []
			leftGroups, rightGroups = [], []
			
			for thisGlyph in thisFont.glyphs:
				self.status("Scanning %s..."%thisGlyph.name, reportInMacroWindow)
				
				leftCategoryOK = leftCategory=="Any" or thisGlyph.category==leftCategory
				leftSubCategoryOK = leftSubCategory=="Any" or thisGlyph.subCategory==leftSubCategory
				leftScriptOK = leftScript=="Any" or thisGlyph.script==leftScript
				isAMatchingLeftGlyph = leftCategoryOK and leftSubCategoryOK and leftScriptOK
				if isAMatchingLeftGlyph:
					leftGlyphNames.append(thisGlyph.name)
					if thisGlyph.rightKerningGroup and not thisGlyph.rightKerningGroup in leftGroups:
						leftGroups.append(thisGlyph.rightKerningGroup)
					
				rightCategoryOK = rightCategory=="Any" or thisGlyph.category==rightCategory
				rightSubCategoryOK = rightSubCategory=="Any" or thisGlyph.subCategory==rightSubCategory
				rightScriptOK = rightScript=="Any" or thisGlyph.script==rightScript
				isAMatchingRightGlyph = rightCategoryOK and rightSubCategoryOK and rightScriptOK
				if isAMatchingRightGlyph:
					rightGlyphNames.append(thisGlyph.name)
					if thisGlyph.leftKerningGroup and not thisGlyph.leftKerningGroup in rightGroups:
						rightGroups.append(thisGlyph.leftKerningGroup)
						
			if not includeDirtyCategories:
				self.status("Sorting out dirty groups...", reportInMacroWindow)
				if leftGroups or rightGroups:
					for thisGlyph in thisFont.glyphs:
						if thisGlyph.rightKerningGroup in leftGroups and not thisGlyph.name in leftGlyphNames:
							while thisGlyph.rightKerningGroup in leftGroups:
								leftGroups.remove(thisGlyph.rightKerningGroup)
							self.status("Dirty right group @MMK_L_%s skipped."%thisGlyph.rightKerningGroup, reportInMacroWindow)
						if thisGlyph.leftKerningGroup in rightGroups and not thisGlyph.name in rightGlyphNames:
							while thisGlyph.leftKerningGroup in rightGroups:
								rightGroups.remove(thisGlyph.leftKerningGroup)
							self.status("Dirty left group @MMK_R_%s skipped."%thisGlyph.leftKerningGroup, reportInMacroWindow)
			
			if Glyphs.defaults["com.mekkablue.RemoveKerning.processAllMasters"]:
				masterIDs = tuple([m.id for m in thisFont.masters])
			else:
				masterIDs = (thisFont.selectedFontMaster.id,)
			
			leftNames = leftGlyphNames + ["@MMK_L_%s"%groupname for groupname in leftGroups]
			rightNames = rightGlyphNames + ["@MMK_R_%s"%groupname for groupname in rightGroups]
			
			fullLength = len(masterIDs) * len(leftNames) * len(rightNames)
			counter = 0
			
			for masterID in masterIDs:
				masterName = thisFont.fontMasterForId_(masterID).name
				self.status("Processing master '%s'..."%masterName, reportInMacroWindow)
				if thisFont.kerning.has_key(masterID):
					for leftName in leftNames:
						try:
							leftID = thisFont.glyphs[leftName].glyphId()
						except:
							# tried to find a glyph named like a group
							leftID = leftName
						if thisFont.kerning[masterID].has_key(leftID):
							for rightName in rightNames:
								try:
									rightID = thisFont.glyphs[rightName].glyphId()
								except:
									# tried to find a glyph named like a group
									rightID = rightName
								if thisFont.kerning[masterID][leftID].has_key(rightID):
									self.status("Master '%s': removing pair %s:%s..."%(masterName, leftName,rightName), True)
									thisFont.removeKerningForPair(masterID, leftName, rightName)
								counter+=1
								self.w.progress.set(counter/fullLength*100)
						else:
							counter += len(rightNames)
							self.w.progress.set(counter/fullLength*100)
				else:
					counter += len(leftNames) * len(rightNames)
					self.w.progress.set(counter/fullLength*100)
					
			self.w.progress.set(100)
			self.status("Ready.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Kerning Error: %s" % e)
			import traceback
			print(traceback.format_exc())

RemoveKerning()