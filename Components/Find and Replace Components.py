#MenuTitle: Find and Replace Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Replaces components in selected glyphs (GUI).
"""

import vanilla

def replaceComponent( thisLayer, oldCompName, newCompName ):
	try:
		count = 0
		thisGlyph = thisLayer.parent
		if thisGlyph:
			if thisGlyph.name != newCompName:
				for i in range( len( thisLayer.components )):
					if thisLayer.components[i].componentName == oldCompName:
						thisLayer.components[i].componentName = newCompName
						count += 1
				print("\t✅ Replaced %i component%s in %s, layer: %s" % (
					count,
					"" if count==1 else "s",
					thisGlyph.name, 
					thisLayer.name,
					))
			else:
				print("\t⚠️ Cannot insert %s into itself. Skipping %slayer: %s" % (
					newCompName,
					"background " if thisLayer.__class__().className() == "GSBackgroundLayer" else "",
					thisLayer.name,
					))
		else:
			print("\t⚠️ Cannot determine glyph for layer: %s" & thisLayer.name)
		return count
	except Exception as e:
		print("\t❌ Failed to replace %s for %s in %s." % ( oldCompName, newCompName, thisLayer.parent.name ))
		print(e)
		import traceback
		print(traceback.format_exc())
		return 0

class ComponentReplacer(object):

	def __init__( self):
		# Window 'self.w':
		windowWidth  = 400
		windowHeight = 80
		windowWidthResize  = 200 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Replace Components in Selection", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.ReplaceComponents.mainwindow" # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 10, 15, 22
		
		self.w.textReplace = vanilla.TextBox((inset, linePos+2, inset+50, 14), "Replace", sizeStyle='small')
		self.w.componentName = vanilla.PopUpButton((inset+50, linePos, 100, 17), self.GetComponentNames(), sizeStyle='small')
		self.w.componentName.getNSPopUpButton().setToolTip_(u"The name of the component you want to replace. If it is not shown here, make a glyph selection and press the ↺ Update button. This will populate the menu with the names of all components in selected glyphs.")
		self.w.resetComponentName = vanilla.SquareButton((inset+50+100+5, linePos, 20, 18), u"↺", sizeStyle='small', callback=self.SetComponentNames )

		self.w.textBy = vanilla.TextBox((inset+50+100+35, linePos+2, 20, 14), "by", sizeStyle='small')
		# self.w.componentNewName = vanilla.EditText((65+100+35+25, linePos, -inset-95, 19), "", sizeStyle='small', callback=self.SavePreferences)
		self.w.componentNewName = vanilla.ComboBox( (65+100+35+25, linePos-1, -inset-95, 19), self.getAllGlyphNamesOfFrontmostFont(), sizeStyle='small', callback=self.SavePreferences )
		self.w.componentNewName.getNSComboBox().setToolTip_(u"The name of the component you want to insert instead of the component chosen in the menu.")
		self.w.resetComponentNewName = vanilla.SquareButton((-inset-90, linePos, -inset-70, 18), u"↺", sizeStyle='small', callback=self.ResetComponentNewName )
		self.w.replaceButton = vanilla.Button((-inset-60, linePos+1, -inset, 17), "Replace", sizeStyle='small', callback=self.FindAndReplaceMain )
		self.w.setDefaultButton( self.w.replaceButton )

		linePos += lineHeight
		
		self.w.includeAllLayers = vanilla.CheckBox((inset, linePos, 120, 18), "Include all layers", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeAllLayers.getNSButton().setToolTip_(u"If checked, will not only treat visible selected layers, but ALL (master, special and backup) layers of all selected glyphs.")
		self.w.includeBackgrounds = vanilla.CheckBox( (inset+120, linePos, -inset, 20), u"Include backgrounds", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeBackgrounds.getNSButton().setToolTip_(u"If checked, will also go through backgrounds of all treated layers.")
		linePos += lineHeight
		
		if not self.LoadPreferences( ):
			print("⚠️ Note: Could not load preferences. Will resort to defaults.")

		self.w.open()
	
	def getAllGlyphNamesOfFrontmostFont(self, sender=None):
		thisFont = Glyphs.font
		if not thisFont:
			return ()
		else:
			return [g.name for g in thisFont.glyphs]
		
	def updateUI(self, sender=None):
		itemCount = len(self.w.componentName.getItems())
		selectedIndex = self.w.componentName.get()
		namesDifferent = Glyphs.defaults["com.mekkablue.ReplaceComponents.oldCompName"] != Glyphs.defaults["com.mekkablue.ReplaceComponents.newCompName"]
		enableButton = itemCount>0 and selectedIndex<itemCount and namesDifferent
		self.w.replaceButton.enable(enableButton)

	def SavePreferences( self, sender=None ):
		try:
			Glyphs.defaults["com.mekkablue.ReplaceComponents.newCompName"] = self.w.componentNewName.get()
			Glyphs.defaults["com.mekkablue.ReplaceComponents.oldCompName"] = self.w.componentName.getItems()[self.w.componentName.get()]
			Glyphs.defaults["com.mekkablue.ReplaceComponents.includeAllLayers"] = self.w.includeAllLayers.get()
			Glyphs.defaults["com.mekkablue.ReplaceComponents.includeBackgrounds"] = self.w.includeBackgrounds.get()
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False
	
	def LoadPreferences( self ):
		try:
			self.w.componentNewName.set( Glyphs.defaults["com.mekkablue.ReplaceComponents.newCompName"] )
			self.w.includeAllLayers.set( Glyphs.defaults["com.mekkablue.ReplaceComponents.includeAllLayers"] )
			self.w.includeBackgrounds.set( Glyphs.defaults["com.mekkablue.ReplaceComponents.includeBackgrounds"] )
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def GetComponentNames( self):
		thisFont = Glyphs.font
		if not thisFont:
			self.updateUI()
			return ()
		else:
			myComponentList = set()
			selectedGlyphs = [ l.parent for l in thisFont.selectedLayers ]
			for thisGlyph in selectedGlyphs:
				for thisLayer in thisGlyph.layers:
					for thisComponent in thisLayer.components:
						myComponentList.add( thisComponent.componentName )
			try:
				self.updateUI()
			except:
				pass
				
			return sorted( list( myComponentList ))
	
	def SetComponentNames( self, sender=None ):
		try:
			myComponentList = self.GetComponentNames()
			self.w.componentName.setItems( myComponentList )
			self.updateUI()
			return True
		except:
			return False
	
	def ResetComponentNewName( self, sender=None ):
		try:
			thisFont = Glyphs.font
			# reset glyph list
			self.w.componentNewName.setItems( self.getAllGlyphNamesOfFrontmostFont() )
			
			# reset name:
			if not thisFont:
				self.w.componentNewName.set("")
			else:
				if thisFont.selectedLayers:
					glyph = thisFont.selectedLayers[0].parent
				else:
					glyph = thisFont.glyphs[0]
				
				glyphName = glyph.name
				glyphInfo = Glyphs.glyphInfoForName(glyphName)
				
				if glyphInfo and glyphInfo.components:
					glyphName = glyphInfo.components[0].name
					
				if "." in glyphName:
					ending = glyphName[ glyphName.find("."): ]
					if thisFont.glyphs[glyphName+ending]:
						glyphName = glyphName+ending
				
				self.w.componentNewName.set( glyphName )
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False
	
	def FindAndReplaceMain( self, sender ):
		thisFont = Glyphs.font # frontmost font
		if not thisFont:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
		else:
			Glyphs.clearLog() # clears macro window log
			
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("⚠️ Note: 'Find and Replace Components' could not write preferences.")
		
			print("Find and Replace Components, report for %s" % thisFont.familyName)
			if thisFont.filepath:
				print(thisFont.filepath)
			else:
				print("⚠️ The font file has not been saved yet.")
			print()
		
			selectedLayers = thisFont.selectedLayers
			newComponentName = Glyphs.defaults["com.mekkablue.ReplaceComponents.newCompName"]
			oldComponentName = Glyphs.defaults["com.mekkablue.ReplaceComponents.oldCompName"]
			includeAllLayers = Glyphs.defaults["com.mekkablue.ReplaceComponents.includeAllLayers"]
			includeBackgrounds = Glyphs.defaults["com.mekkablue.ReplaceComponents.includeBackgrounds"]
		
			thisFont.disableUpdateInterface()
			try:
				totalCount = 0
				if includeAllLayers:
					selectedGlyphs = [ l.parent for l in selectedLayers ]
					for thisGlyph in selectedGlyphs:
						print("Processing %s:" % thisGlyph.name )
						for thisLayer in thisGlyph.layers:
							totalCount += replaceComponent( thisLayer, oldComponentName, newComponentName )
						if includeBackgrounds:
							totalCount += replaceComponent( thisLayer.background, oldComponentName, newComponentName )
				else:
					for thisLayer in selectedLayers:
						totalCount += replaceComponent( thisLayer, oldComponentName, newComponentName )
					if includeBackgrounds:
						totalCount += replaceComponent( thisLayer.background, oldComponentName, newComponentName )
						
			except Exception as e:
				Glyphs.showMacroWindow()
				print("\n⚠️ Script Error:\n")
				import traceback
				print(traceback.format_exc())
				print()
				raise e
				
			finally:
				thisFont.enableUpdateInterface() # re-enables UI updates in Font View
			
			# Final report...
			msg = "Replaced %i component%s" % (
				totalCount,
				"" if totalCount==1 else "s",
				)
			# ... in Macro Window:
			print("\nDone. %s." % msg)
			# ... in Floating Notification:
			Glyphs.showNotification( 
				u"%s: components replaced" % (thisFont.familyName),
				u"%s in total. Detailed report in Macro Window." % msg,
				)

ComponentReplacer()
