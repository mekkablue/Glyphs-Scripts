#MenuTitle: Find in Features
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Finds expressions (glyph, lookup or class names) in OT Features, Prefixes and Classes.
"""

import vanilla

class FindInFeatures( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 180
		windowHeight = 200
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 1100   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Find in Features", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.FindInFeatures.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 1, 5, 28	
		self.w.searchFor = vanilla.ComboBox( (1, linePos, -22, 22), self.glyphNamesAndClassNames(), callback=self.FindInFeaturesMain, sizeStyle='regular' )
		self.w.searchFor.getNSComboBox().setToolTip_("Type the exact name of a glyph or (prefixed with @) a class, or choose it from the menu.")
		self.w.updateButton = vanilla.SquareButton( (-19, linePos+2, -2, 18), "↺", sizeStyle='small', callback=self.update )
		self.w.updateButton.getNSButton().setToolTip_("Update the autocompletion list for the frontmost font.")
		linePos += lineHeight
		
		self.w.result = vanilla.Box( (inset, linePos, -inset, -inset) )
		self.w.result.previewText = vanilla.TextBox( (1, 1, -1, -1), "", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def update(self, sender=None):
		self.w.searchFor.setItems(
			self.glyphNamesAndClassNames()
		)
		
	def glyphNamesAndClassNames(self, sender=None):
		fullList = []
		font = Glyphs.font
		if font:
			# add all exporting glyphs:
			fullList.extend(
				[g.name for g in font.glyphs if g.export]
			)
			
			# add all OT class names:
			fullList.extend(
				["@%s"%c.name for c in font.classes]
			)
			
			# sort it:
			fullList = sorted(fullList)
			
		return fullList

	def codeClean(self, code):
		# get rid of comments:
		lines = code.splitlines()
		for i,line in enumerate(lines):
			if "#" in line:
				lines[i] = line[:line.find("#")]
		code = "\n".join(lines)
		
		# get rid of control chars:
		removeThese = "[];{}()'"
		for removeThis in removeThese:
			code = code.replace(removeThis," ").replace("  "," ")
		return code
		
	def FindInFeaturesMain( self, sender=None ):
		try:
			reportText = ""
			
			thisFont = Glyphs.font # frontmost font
			if not thisFont is None:
				searchfor = sender.get()
				
				# Find in Classes:
				reportText += "OT Classes:\n"
				classes = []
				for c in thisFont.classes:
					if searchfor in self.codeClean(c.code).split():
						classes.append(c.name)
				
				if not classes:
					reportText += "(nothing found)\n"
					classSet = None
				else:
					classSet = set(classes)
					for className in classSet:
						reportText += "\t%s"%className
						if classes.count(className) > 1:
							reportText += " (%i×)"%classes.count(className)
						reportText += "\n"
				
				# Find in Prefix and Features:
				prefixAndFeatures = (
					(thisFont.featurePrefixes, "\nOT Prefixes:\n"),
					(thisFont.features, "\nOT Features:\n"),
				)
				
				foundInFeaturesCount = 0
				for featureSet in prefixAndFeatures:
					originalFeatureCount = foundInFeaturesCount
					reportText += featureSet[1]
					for feature in featureSet[0]:
						if feature.active:
							cleanCode = self.codeClean(feature.code)
							for i,l in enumerate(cleanCode.splitlines()):
								split = l.split()
								if searchfor in split:
									reportText += "\t%s, line %i (%s)\n" % (feature.name, i+1, searchfor)
									foundInFeaturesCount += 1
						
								# also find the classes the term appears in:
								if classSet:
									for otclass in classSet:
										if "@%s"%otclass in split:
											reportText += "\t%s, line %i (@%s)\n" % (feature.name, i+1, otclass)
											foundInFeaturesCount += 1
			
					if foundInFeaturesCount==originalFeatureCount:
						reportText += "(nothing found)\n"
						
			self.w.result.previewText.set(reportText)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Find in Features Error: %s" % e)
			import traceback
			print(traceback.format_exc())

FindInFeatures()