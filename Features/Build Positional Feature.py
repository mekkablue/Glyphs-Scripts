#MenuTitle: Build Positional Feature
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Create or update OpenType feature code for positional forms (isolated, initial, medial and final). Will also add respective OpenType classes.
"""

import vanilla

def updatedCode( oldcode, beginsig, endsig, newcode ):
	"""Replaces text in oldcode with newcode, but only between beginsig and endsig."""
	begin_offset = oldcode.find( beginsig )
	end_offset   = oldcode.find( endsig ) + len( endsig )
	newcode = oldcode[:begin_offset] + beginsig + newcode + "\n" + endsig + oldcode[end_offset:]
	return newcode

def createOTFeature( featureName = "calt",
                     featureCode = "# empty feature code",
                     targetFont  = None,
                     codeSig     = "DEFAULT-CODE-SIGNATURE",
                     createSeparateEntry = False ):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	"""
	
	if targetFont:
		beginSig = "# BEGIN " + codeSig + "\n"
		endSig   = "# END "   + codeSig + "\n"
		
		featuresWithTag = [f for f in targetFont.features if f.name==featureName and f.name]
		featureExists = len(featuresWithTag) > 0
		featuresWithSig = [f for f in targetFont.features if beginSig in f.code and endSig in f.code and f.active]
		sigExists = len(featuresWithSig) > 0
		
		if sigExists:
			for targetFeature in featuresWithSig:
				# replace old code with new code:
				targetFeature.code = updatedCode( targetFeature.code, beginSig, endSig, featureCode )
			returnText = "✅ Updated %i existing OT feature%s ‘%s’." % (
				len(featuresWithSig),
				"" if len(featuresWithSig)==1 else "s",
				featureName,
				)
		elif featureExists and not createSeparateEntry:
			# feature already exists:
			targetFeature = targetFont.features[ featureName ] # take the first available one
			targetFeature.code += "\n" + beginSig + featureCode + "\n" + endSig
			returnText = "✅ Added code to first available OT feature ‘%s’." % featureName
		else:
			# create feature with new code:
			newFeature = GSFeature()
			newFeature.name = featureName
			newFeature.code = beginSig + featureCode + "\n" + endSig
			targetFont.features.append( newFeature )
			return "🌟 Created new OT feature entry ‘%s’" % featureName
	else:
		return "🛑 ERROR: Could not create OT feature %s. No font detected." % ( featureName )

def createOTClass( className       = "@default",
                   classGlyphNames = [],
                   targetFont      = None,
                   automate        = False ):
	"""
	Creates an OpenType class in the font.
	Default: class @default with currently selected glyphs in the current font.
	Returns a status message in form of a string.
	"""
	
	if targetFont and (classGlyphNames or automate):
		className = className.lstrip("@") # strip '@' from beginning
		classCode = " ".join( classGlyphNames )
		otClass = None
		
		# build or update class:
		if className in [ c.name for c in targetFont.classes ]:
			otClass = targetFont.classes[className]
			otClass.code = classCode
			returnText = "✅ Updated existing OT class ‘%s’." % ( className )
		else:
			otClass = GSClass()
			otClass.name = className
			otClass.code = classCode
			targetFont.classes.append( otClass )
			returnText = "🌟 Created new OT class: ‘%s’" % ( className )
		
		# automate the class:
		if automate and otClass is not None:
			if Glyphs.versionNumber >= 3:
				# GLYPHS 3
				if otClass.canBeAutomated():
					otClass.automatic = True
			else:
				# GLYPHS 2
				otClass.automatic = True
			
			returnText = returnText.rstrip(".") + " (automated)."
		
		return returnText
	else:
		return "🛑 ERROR: Could not create OT class %s. Missing either font or glyph names, or both." % ( className )

class BuildPositionalFeature( object ):
	prefDomain = "com.mekkablue.BuildPositionalFeature"
	title = "Build Positional Feature"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 365
		windowHeight = 225
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			self.title, # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domainForPref("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		tabIndent = 140
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), "Build or update code for initial, medial, final and isolated forms", sizeStyle='small', selectable=True )
		linePos += lineHeight+2
		
		self.w.targetFeatureText = vanilla.TextBox( (inset, linePos+3, tabIndent, 14), "Target feature (tag):", sizeStyle='small', selectable=True )
		self.w.targetFeature = vanilla.EditText( (inset+tabIndent, linePos, -inset-25, 19), "calt", callback=self.SavePreferences, sizeStyle='small' )
		tooltip = "Feature tag for the OpenType feature that is supposed to receive the positional code."
		self.w.targetFeature.getNSTextField().setToolTip_(tooltip)
		self.w.targetFeatureText.getNSTextField().setToolTip_(tooltip)
		self.w.targetFeatureUpdate = vanilla.SquareButton( (-inset-20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.update )
		self.w.targetFeatureUpdate.getNSButton().setToolTip_("Reset to defaults: ‘calt’")
		linePos += lineHeight
		
		self.w.suffixesText = vanilla.TextBox( (inset, linePos+3, tabIndent, 14), "Suffixes (in,me,fi,is):", sizeStyle='small', selectable=True )
		self.w.suffixes = vanilla.EditText( (inset+tabIndent, linePos, -inset-25, 19), "init, medi, fina, isol", callback=self.SavePreferences, sizeStyle='small' )
		tooltip = "Glyph suffixes in the font, for the four positions, in this order:\n1. initial\n2. medial\n3. final\n4. isolated"
		self.w.suffixes.getNSTextField().setToolTip_(tooltip)
		self.w.suffixesText.getNSTextField().setToolTip_(tooltip)
		self.w.suffixesUpdate = vanilla.SquareButton( (-inset-20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.update )
		self.w.suffixesUpdate.getNSButton().setToolTip_("Reset to defaults: ‘init, medi, fina, isol’")
		linePos += lineHeight
		
		self.w.sourceSuffixText = vanilla.TextBox( (inset, linePos+3, tabIndent, 14), "Suffix for source classes:", sizeStyle='small', selectable=True )
		self.w.sourceSuffix = vanilla.EditText( (inset+tabIndent, linePos, -inset-25, 19), "Def", callback=self.SavePreferences, sizeStyle='small' )
		tooltip = "Newly generated OT classes will be named after the positional tag (init, medi, fina, isol) plus a suffix for the source class (for the unsuffixed glyphs) or the target class (for the respectively suffixed glyphs). One of the suffixes can be left empty, but not both."
		self.w.sourceSuffix.getNSTextField().setToolTip_(tooltip)
		self.w.sourceSuffixText.getNSTextField().setToolTip_(tooltip)
		self.w.sourceSuffixUpdate = vanilla.SquareButton( (-inset-20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.update )
		self.w.sourceSuffixUpdate.getNSButton().setToolTip_("Reset to defaults: ‘Def’")
		linePos += lineHeight
		
		self.w.targetSuffixText = vanilla.TextBox( (inset, linePos+3, tabIndent, 14), "Suffix for target classes:", sizeStyle='small', selectable=True )
		self.w.targetSuffix = vanilla.EditText( (inset+tabIndent, linePos, -inset-25, 19), "Sub", callback=self.SavePreferences, sizeStyle='small' )
		self.w.targetSuffix.getNSTextField().setToolTip_(tooltip)
		self.w.targetSuffixText.getNSTextField().setToolTip_(tooltip)
		self.w.targetSuffixUpdate = vanilla.SquareButton( (-inset-20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.update )
		self.w.targetSuffixUpdate.getNSButton().setToolTip_("Reset to defaults: ‘Sub’")
		linePos += lineHeight
		
		self.w.automateAllLetters = vanilla.CheckBox( (inset, linePos, -inset, 20), "Automate ‘AllLetters’ feature class", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.automateAllLetters.getNSButton().setToolTip_("The @AllLetters OpenType class can be automated (and thus, automatically kept up to date) by Glyphs. Enabling this option will add this class with the ‘Generate automatically’ option ON. Strongly recommended.")
		linePos += lineHeight
		
		self.w.separateFeatureEntry = vanilla.CheckBox( (inset, linePos, -inset, 20), "Separate feature entry (i.e. do not reuse existing feature)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.separateFeatureEntry.getNSButton().setToolTip_("If this option is enabled and the target feature already exists in Font Info → Features, will create a new entry with the same feature tag, rather than append the code to an existing feature entry.")
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Build", sizeStyle='regular', callback=self.BuildPositionalFeatureMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: ‘%s’ could not load preferences. Will resort to defaults" % self.title)
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domainForPref(self, pref):
		return self.prefDomain.strip().strip(".") + "." + pref
	
	def valueForPref(self, pref):
		domain = self.domainForPref(pref)
		return Glyphs.defaults[domain]
	
	def setValueForPref(self, pref, value="0"):
		domain = self.domainForPref(pref)
		Glyphs.defaults[domain] = value
	
	def update(self, sender=None):
		if sender == self.w.targetFeatureUpdate:
			self.setValueForPref("targetFeature", "calt")
		elif sender == self.w.suffixesUpdate:
			self.setValueForPref("suffixes", "init, medi, fina, isol")
		elif sender == self.w.sourceSuffixUpdate:
			self.setValueForPref("sourceSuffix", "Def")
		elif sender == self.w.targetSuffixUpdate:
			self.setValueForPref("targetSuffix", "Sub")
			
		self.LoadPreferences()
		
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			self.setValueForPref("targetFeature", self.w.targetFeature.get())
			self.setValueForPref("suffixes", self.w.suffixes.get())
			self.setValueForPref("sourceSuffixUpdate", self.w.sourceSuffix.get())
			self.setValueForPref("targetSuffixUpdate", self.w.targetSuffix.get())
			self.setValueForPref("automateAllLetters", self.w.automateAllLetters.get())
			self.setValueForPref("separateFeatureEntry", self.w.separateFeatureEntry.get())
			
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault( self.domainForPref("targetFeature"), "calt")
			Glyphs.registerDefault( self.domainForPref("suffixes"), "init, medi, fina, isol")
			Glyphs.registerDefault( self.domainForPref("sourceSuffix"), "Def")
			Glyphs.registerDefault( self.domainForPref("targetSuffix"), "Sub")
			Glyphs.registerDefault( self.domainForPref("automateAllLetters"), True)
			Glyphs.registerDefault( self.domainForPref("separateFeatureEntry"), False)
			
			# load previously written prefs:
			self.w.targetFeature.set( self.valueForPref("targetFeature") )
			self.w.suffixes.set( self.valueForPref("suffixes") )
			self.w.sourceSuffix.set( self.valueForPref("sourceSuffix") )
			self.w.targetSuffix.set( self.valueForPref("targetSuffix") )
			self.w.automateAllLetters.set( self.valueForPref("automateAllLetters") )
			self.w.separateFeatureEntry.set( self.valueForPref("separateFeatureEntry") )
			
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def BuildPositionalFeatureMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: ‘%s’ could not write preferences." % self.title)
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("‘%s’ Report for %s" % (self.title, thisFont.familyName))
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
				
				# read user settings and supply fallback values if necessary:
				positionalFeature = self.valueForPref("targetFeature").strip()
				if not positionalFeature or len(positionalFeature)>4:
					print("⚠️ Invalid target feature tag: ‘%s’" % positionalFeature)
					positionalFeature = "calt"
					self.setValueForPref("targetFeature", positionalFeature)
					self.LoadPreferences()
				
				extensionDef = self.valueForPref("sourceSuffix").strip()
				extensionSub = self.valueForPref("targetSuffix").strip()
				if not extensionDef and not extensionSub:
					print("⚠️ Both class suffixes cannot be empty at the same time. Restoring defaults.")
					extensionDef = "Def"
					extensionSub = "Sub"
					self.setValueForPref("sourceSuffix", extensionDef)
					self.setValueForPref("targetSuffix", extensionSub)
					self.LoadPreferences()
				
				suffixKeys = ("init","medi","fina","isol")
				suffixDict = {}
				for suffix in suffixKeys:
					suffixDict[suffix] = suffix
					
				userSuppliedSuffixes = [suffix.strip() for suffix in self.valueForPref("suffixes").split(",")]
				for i in range(len(userSuppliedSuffixes)):
					userSuppliedSuffix = userSuppliedSuffixes[i]
					if userSuppliedSuffix:
						suffixKey = suffixKeys[i]
						suffixDict[suffixKey] = userSuppliedSuffix
				
				# create or update AllLetters class
				anyLetterClassName = "AllLetters"
				automateAllLetters = bool(self.valueForPref("automateAllLetters"))
				allLetterNames = [ g.name for g in thisFont.glyphs if g.category == "Letter" and g.export ]
				print(
					"\t%s" % createOTClass(
						className       = anyLetterClassName,
						classGlyphNames = allLetterNames,
						targetFont      = thisFont,
						automate        = automateAllLetters,
					)
				)
				classCount = 1
				
				# build ignore statements
				ignoreStatements = {
					"isol": "ignore sub @isol%s' @%s, @%s @isol%s';" % ( extensionDef, anyLetterClassName, anyLetterClassName, extensionDef ),
					"init": "ignore sub @%s @init%s';" % ( anyLetterClassName, extensionDef ),
					"fina": "ignore sub @fina%s' @%s;" % ( extensionDef, anyLetterClassName ),
					"medi": "sub @%s @medi%s' @%s by @medi%s;" % ( anyLetterClassName, extensionDef, anyLetterClassName, extensionSub ),
				}
				
				positionalFeatureCode = "\n"
				for suffixKey in suffixKeys:
					thisSuffix = suffixDict[suffixKey]
					dotSuffix = "." + thisSuffix.strip(".")
					dotSuffixLength = len( dotSuffix )
					theseSuffixedGlyphNames = [ 
						g.name for g in thisFont.glyphs 
						if dotSuffix in g.name # glyph has suffix
						and g.export # suffixed glyph exports
						and thisFont.glyphs[g.name.replace(dotSuffix,"")] is not None # unsuffixed counterpart exists
						and thisFont.glyphs[g.name.replace(dotSuffix,"")].export # unsuffixed glyph exports
					]
					theseSuffixedGlyphNames = list(set(theseSuffixedGlyphNames)) # make sure every glyph is unique
					theseUnsuffixedGlyphNames = [ n.replace(dotSuffix,"") for n in theseSuffixedGlyphNames ]
	
					print("\n\t🔠 Found %i glyphs with a %s suffix, and %i unsuffixed counterparts." % (
						len( theseSuffixedGlyphNames ),
						dotSuffix,
						len( theseUnsuffixedGlyphNames )
					))
	
					if len( theseSuffixedGlyphNames ) > 0:
						# BUILD SOURCE AND TARGET CLASSES
						
						print("\t%s" % createOTClass(
							className       = suffixKey + extensionDef,
							classGlyphNames = theseUnsuffixedGlyphNames,
							targetFont      = thisFont
						))
						print("\t%s" % createOTClass(
							className       = suffixKey + extensionSub,
							classGlyphNames = theseSuffixedGlyphNames,
							targetFont      = thisFont
						))
						classCount += 2
						
						# COLLECT FEATURE CODE
						
						thisIgnoreCode = ignoreStatements[ suffixKey ]
		
						if thisIgnoreCode.startswith( "ignore" ):
							ignoreSubstitution = "\tsub @%s%s' by @%s%s;\n" % (
								suffixKey, extensionDef,
								suffixKey, extensionSub,
							)
						else:
							ignoreSubstitution = ""
	
						positionalFeatureCode += "lookup %sForms {\n" % ( thisSuffix.title() )
						positionalFeatureCode += "\t%s\n" % ( thisIgnoreCode )
						positionalFeatureCode += ignoreSubstitution
						positionalFeatureCode += "} %sForms;\n\n" % ( thisSuffix.title() )
				
				# BUILD FEATURE WITH COLLECTED CODE
				
				separateFeatureEntry = bool(self.valueForPref("separateFeatureEntry"))
				positionalFeatureCode = "\n%s\n" % positionalFeatureCode.strip()
				print("\n\t%s" % createOTFeature(
					featureName = positionalFeature,
					featureCode = positionalFeatureCode,
					targetFont  = thisFont,
					codeSig     = "POSITIONAL ALTERNATES",
					createSeparateEntry = separateFeatureEntry,
				))
				
				# close script window and update features:
				self.w.close()
				#thisFont.updateFeatures()
				thisFont.compileFeatures()

			# Final report:
			Glyphs.showNotification( 
				"%s: positional features built" % (thisFont.familyName),
				"%i lines of code generated in %s, %i classes added or updated. Details in Macro Window," % (
					len(positionalFeatureCode.splitlines()),
					positionalFeature,
					classCount,
					),
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("‘%s’ Error: %s" % (self.title, e))
			import traceback
			print(traceback.format_exc())

BuildPositionalFeature()