#MenuTitle: Find and Replace in Kerning Groups
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Finds and replaces text in the metrics keys of selected glyphs. Leave the Find string blank to hang the replace string at the end of the metrics keys.
"""

import vanilla

class KerningGroupReplacer( object ):
	def __init__( self ):
		windowWidth = 335
		windowHeight = 155
		windowWidthResize = 1000 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Find and Replace in Kerning Groups", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.KerningGroupReplacer.mainwindow" # stores last window position and size
		)
		
		linePos, inset, lineHeight = 10, 12, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos, -inset, 14), "In selected glyphs, replace in group names:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.text_left     = vanilla.TextBox(  (inset+60, linePos+2, -inset-70, 14), "Left Groups", sizeStyle='small' )
		self.w.text_right    = vanilla.TextBox(  (inset+180, linePos+2, -inset, 14), "Right Groups", sizeStyle='small' )
		linePos += lineHeight

		self.w.text_Find      = vanilla.TextBox(  (inset, linePos+3, 55, 20), "Find", sizeStyle='small' )
		self.w.leftSearchFor  = vanilla.EditText( (inset+60, linePos, 120-5, 20), ".tf", callback=self.SavePreferences, sizeStyle='small', placeholder='(leave these blank ...' )
		self.w.rightSearchFor = vanilla.EditText( (inset+180, linePos, -inset, 20), ".tf", callback=self.SavePreferences, sizeStyle='small', placeholder='... to append)' )
		linePos += lineHeight

		self.w.text_Replace   = vanilla.TextBox(  (inset, linePos+3, 55, 20), "Replace", sizeStyle='small' )
		self.w.leftReplaceBy  = vanilla.EditText( (inset+60, linePos, 120-5, 20), "", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)' )
		self.w.rightReplaceBy = vanilla.EditText( (inset+180, linePos, -inset, 20), "", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)' )
		linePos += lineHeight
		
		self.w.runButton = vanilla.Button((-110, -20-inset, -inset, -inset), "Replace", sizeStyle='regular', callback=self.KerningGroupReplaceMain )
		self.w.setDefaultButton( self.w.runButton )
		
		if not self.LoadPreferences():
			print("Note: Could not load preferences. Will resort to defaults")
			
		self.inset=inset
		self.w.bind("resize", self.stretchBoxes)
		self.stretchBoxes()
		self.w.open()
		self.w.makeKey()
	
	def stretchBoxes(self, sender=None):
		windowWidth = self.w.getPosSize()[2]
		netWindowWidth = windowWidth-2*self.inset
		columnWidth = int((netWindowWidth-60)/2) - 3
		rightColumnX = self.inset+60 + int((netWindowWidth-60)/2) + 6
		
		x, y, width, height = self.w.leftSearchFor.getPosSize()
		self.w.leftSearchFor.setPosSize( (x, y, columnWidth, height), animate=False )
		x, y, width, height = self.w.leftReplaceBy.getPosSize()
		self.w.leftReplaceBy.setPosSize( (x, y, columnWidth, height), animate=False )
		
		x, y, width, height = self.w.text_right.getPosSize()
		self.w.text_right.setPosSize( (rightColumnX, y, columnWidth, height), animate=False )
		x, y, width, height = self.w.rightSearchFor.getPosSize()
		self.w.rightSearchFor.setPosSize( (rightColumnX, y, columnWidth, height), animate=False )
		x, y, width, height = self.w.rightReplaceBy.getPosSize()
		self.w.rightReplaceBy.setPosSize( (rightColumnX, y, columnWidth, height), animate=False )
		
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.leftSearchFor"  ] = self.w.leftSearchFor.get()
			Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.leftReplaceBy"  ] = self.w.leftReplaceBy.get()
			Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.rightSearchFor" ] = self.w.rightSearchFor.get()
			Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.rightReplaceBy" ] = self.w.rightReplaceBy.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.KerningGroupReplacer.leftSearchFor","")
			Glyphs.registerDefault("com.mekkablue.KerningGroupReplacer.leftReplaceBy","")
			Glyphs.registerDefault("com.mekkablue.KerningGroupReplacer.rightSearchFor","")
			Glyphs.registerDefault("com.mekkablue.KerningGroupReplacer.rightReplaceBy","")
			self.w.leftSearchFor.set(  Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.leftSearchFor"  ] )
			self.w.leftReplaceBy.set(  Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.leftReplaceBy"  ] )
			self.w.rightSearchFor.set( Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.rightSearchFor" ] )
			self.w.rightReplaceBy.set( Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.rightReplaceBy" ] )
		except:
			return False
			
		return True
	
	def replaceGroupName( self, groupName, searchString, replaceString ):
		try:
			if groupName:
				if searchString == "":
					# simply append replaceString if no search string is supplied:
					return groupName + replaceString
				else:
					return groupName.replace( searchString, replaceString )
			else:
				return None
		except Exception as e:
			print(e)
	
	def replaceInGroups( self, thisGlyph, LsearchFor, LreplaceBy, RsearchFor, RreplaceBy ):
		thisGlyph.beginUndo()
		thisGlyphName = thisGlyph.name
		
		# Left Group:
		oldLeftGroup = thisGlyph.leftKerningGroup
		if not oldLeftGroup:
			print("%s: no left group set. Left unchanged." % thisGlyphName)
		else:
			newLeftGroup = self.replaceGroupName( oldLeftGroup, LsearchFor, LreplaceBy )
			if oldLeftGroup == newLeftGroup:
				print("%s: left group unchanged (%s)." % (thisGlyphName, newLeftGroup))
			else:
				thisGlyph.leftKerningGroup = newLeftGroup
				print("%s: new left group: '%s'." % ( thisGlyphName, newLeftGroup ))

		# Right Group:
		oldRightGroup = thisGlyph.rightKerningGroup
		if not oldRightGroup:
			print("%s: no right group set. Left unchanged." % thisGlyphName)
		else:
			newRightGroup = self.replaceGroupName( oldRightGroup, RsearchFor, RreplaceBy )
			if oldRightGroup == newRightGroup:
				print("%s: right group unchanged (%s)." % ( thisGlyph.name, newRightGroup ))
			else:
				thisGlyph.rightKerningGroup = newRightGroup
				print("%s: new right group: '%s'." % ( thisGlyph.name, newRightGroup ))
		
		thisGlyph.endUndo()

	def KerningGroupReplaceMain( self, sender ):
		Glyphs.clearLog()
		Glyphs.font.disableUpdateInterface()
		try:
			if not self.SavePreferences( self ):
				print("Note: Could not write preferences.")
			
			Font  = Glyphs.font
			selectedLayers = Font.selectedLayers
			currentLayers = [ l for l in selectedLayers if l.parent.name is not None ]
			
			LsearchFor = Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.leftSearchFor" ]
			LreplaceBy = Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.leftReplaceBy" ]
			RsearchFor = Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.rightSearchFor" ]
			RreplaceBy = Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.rightReplaceBy" ]
			
			for thisLayer in currentLayers:
				try:
					thisGlyph = thisLayer.parent
					self.replaceInGroups( thisGlyph, LsearchFor, LreplaceBy, RsearchFor, RreplaceBy )
				except Exception as e:
					print("Error while processing glyph %s:" % thisGlyph.name)
					print(e)
					
			self.w.close()
			
		except Exception as e:
			raise e
			
		finally:
			Glyphs.font.enableUpdateInterface()

KerningGroupReplacer()
