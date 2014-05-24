#MenuTitle: Find and Replace in Kerning Groups
# -*- coding: utf-8 -*-
__doc__="""
Finds and replaces text in the metrics keys of selected glyphs. Leave the Find string blank to hang the replace string at the end of the metrics keys.
"""

import vanilla
import GlyphsApp

class KerningGroupReplacer( object ):
	def __init__( self ):
		self.w = vanilla.FloatingWindow( (335, 125), "Find and Replace in Kerning Groups", autosaveName="com.mekkablue.KerningGroupReplacer.mainwindow" )

		self.w.text_Find     = vanilla.TextBox( (10, 30+3, 55, 20), "Find", sizeStyle='small' )
		self.w.text_Replace  = vanilla.TextBox( (10, 55+3, 55, 20), "Replace", sizeStyle='small' )

		self.w.text_left     = vanilla.TextBox(  (70, 12, 120, 14), "Left Group", sizeStyle='small' )
		self.w.leftSearchFor = vanilla.EditText( (70, 30, 120, 20), ".tf", callback=self.SavePreferences, sizeStyle='small', placeholder='(leave these blank ...' )
		self.w.leftReplaceBy = vanilla.EditText( (70, 55, 120, 20), "", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)' )

		self.w.text_right     = vanilla.TextBox(  (200, 12, 120, 14), "Right Group", sizeStyle='small' )
		self.w.rightSearchFor = vanilla.EditText( (200, 30, 120, 20), ".tf", callback=self.SavePreferences, sizeStyle='small', placeholder='... to append)' )
		self.w.rightReplaceBy = vanilla.EditText( (200, 55, 120, 20), "", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)' )
		
		self.w.runButton = vanilla.Button((-110, -20-15, -15, -15), "Replace", sizeStyle='regular', callback=self.KerningGroupReplaceMain )
		self.w.setDefaultButton( self.w.runButton )
		
		try:
			self.LoadPreferences( )
		except:
			pass

		self.w.open()
		
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
			self.w.leftSearchFor.set(  Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.leftSearchFor"  ] )
			self.w.leftReplaceBy.set(  Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.leftReplaceBy"  ] )
			self.w.rightSearchFor.set( Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.rightSearchFor" ] )
			self.w.rightReplaceBy.set( Glyphs.defaults[ "com.mekkablue.KerningGroupReplacer.rightReplaceBy" ] )
		except:
			return False
			
		return True
	
	def replaceGroupName( self, groupName, searchString, replaceString ):
		try:
			if groupName != None and groupName != "":
				if searchString == "":
					# simply append replaceString if no search string is supplied:
					return groupName + replaceString
				else:
					return groupName.replace( searchString, replaceString )
			else:
				return None
		except Exception, e:
			print e

	def KerningGroupReplaceMain( self, sender ):
		Glyphs.clearLog()
		Glyphs.font.disableUpdateInterface()
		
		try:
			if not self.SavePreferences( self ):
				print "Note: Could not write preferences."
			
			Font  = Glyphs.font
			selectedLayers = Font.selectedLayers
			currentLayers = [ l for l in selectedLayers if l.parent.name is not None ]
			
			LsearchFor = self.w.leftSearchFor.get()
			LreplaceBy = self.w.leftReplaceBy.get()
			RsearchFor = self.w.rightSearchFor.get()
			RreplaceBy = self.w.rightReplaceBy.get()
			
			for l in currentLayers:
				try:
					g = l.parent
					g.beginUndo()
					
					# Left Group:
					newLeftGroup = self.replaceGroupName( g.leftKerningGroup, LsearchFor, LreplaceBy )
					if newLeftGroup != None:
						g.leftKerningGroup = newLeftGroup
						print "%s: new left group: '%s'" % ( g.name, newLeftGroup )
					else:
						print "Note: No left group set for %s. Left unchanged." % g.name

					# Right Group:
					newRightGroup = self.replaceGroupName( g.rightKerningGroup, RsearchFor, RreplaceBy )
					if newRightGroup != None:
						g.rightKerningGroup = newRightGroup
						print "%s: new right group: '%s'" % ( g.name, newRightGroup )
					else:
						print "Note: No right group set for %s. Left unchanged." % g.name
					
					g.endUndo()
						
				except Exception, e:
					print "Error while processing glyph %s:" % g.name
					print e
					
					g.endUndo()
			
			self.w.close()
		except Exception, e:
			raise e
		
		Glyphs.font.enableUpdateInterface()

KerningGroupReplacer()
