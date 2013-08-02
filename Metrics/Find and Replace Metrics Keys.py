#MenuTitle: Find and Replace in Metrics Keys
# -*- coding: utf-8 -*-
"""Finds and replaces text in the metrics keys of selected glyphs. Leave the Find string blank to hang the replace string at the end of the metrics keys."""

import vanilla
import GlyphsApp

class MetricKeyReplacer( object ):
	def __init__( self ):
		self.w = vanilla.FloatingWindow( (335, 125), "Find and Replace in Metrics Keys", autosaveName="com.mekkablue.MetricKeyReplacer.mainwindow" )

		self.w.text_Find     = vanilla.TextBox( (10, 30+3, 55, 20), "Find", sizeStyle='small' )
		self.w.text_Replace  = vanilla.TextBox( (10, 55+3, 55, 20), "Replace", sizeStyle='small' )

		self.w.text_left     = vanilla.TextBox(  (70, 12, 120, 14), "Left Key", sizeStyle='small' )
		self.w.leftSearchFor = vanilla.EditText( (70, 30, 120, 20), "=a", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)' )
		self.w.leftReplaceBy = vanilla.EditText( (70, 55, 120, 20), "=a.ss01", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)' )

		self.w.text_right     = vanilla.TextBox(  (200, 12, 120, 14), "Right Key", sizeStyle='small' )
		self.w.rightSearchFor = vanilla.EditText( (200, 30, 120, 20), "=|a", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)' )
		self.w.rightReplaceBy = vanilla.EditText( (200, 55, 120, 20), "=|a.ss01", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)' )
		
		self.w.runButton = vanilla.Button((-110, -20-15, -15, -15), "Replace", sizeStyle='regular', callback=self.MetricKeyReplaceMain )
		self.w.setDefaultButton( self.w.runButton )
		
		try:
			self.LoadPreferences( )
		except:
			pass

		self.w.open()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults[ "com.mekkablue.MetricKeyReplacer.leftSearchFor"  ] = self.w.leftSearchFor.get()
			Glyphs.defaults[ "com.mekkablue.MetricKeyReplacer.leftReplaceBy"  ] = self.w.leftReplaceBy.get()
			Glyphs.defaults[ "com.mekkablue.MetricKeyReplacer.rightSearchFor" ] = self.w.rightSearchFor.get()
			Glyphs.defaults[ "com.mekkablue.MetricKeyReplacer.rightReplaceBy" ] = self.w.rightReplaceBy.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			self.w.leftSearchFor.set(  Glyphs.defaults[ "com.mekkablue.MetricKeyReplacer.leftSearchFor"  ] )
			self.w.leftReplaceBy.set(  Glyphs.defaults[ "com.mekkablue.MetricKeyReplacer.leftReplaceBy"  ] )
			self.w.rightSearchFor.set( Glyphs.defaults[ "com.mekkablue.MetricKeyReplacer.rightSearchFor" ] )
			self.w.rightReplaceBy.set( Glyphs.defaults[ "com.mekkablue.MetricKeyReplacer.rightReplaceBy" ] )
		except:
			return False
			
		return True

	def MetricKeyReplaceMain( self, sender ):
		Glyphs.clearLog()
		Glyphs.font.disableUpdateInterface()
		
		try:
			if not self.SavePreferences( self ):
				print "Note: Could not write preferences."
			
			Doc  = Glyphs.currentDocument
			selectedLayers = Doc.selectedLayers()
			currentLayers = [ l for l in selectedLayers if l.parent.name is not None ]
			
			LsearchFor = self.w.leftSearchFor.get()
			LreplaceBy = self.w.leftReplaceBy.get()
			RsearchFor = self.w.rightSearchFor.get()
			RreplaceBy = self.w.rightReplaceBy.get()
			
			for l in currentLayers:
				try:
					g = l.parent
					g.undoManager().beginUndoGrouping()
					
					# Left Metrics Key:
					try:
						# leftKey = g.leftMetricsKey
						leftKey = l.leftMetricsKey()
						leftKey = leftKey[:leftKey.find(" (")]
						
						if leftKey != None and leftKey != "":
							if LsearchFor == "":
								# g.setLeftMetricsKey_( leftKey + LreplaceBy )
								l.setLeftMetricsKey_( leftKey + LreplaceBy )
							else:
								# g.setLeftMetricsKey_( leftKey.replace( LsearchFor, LreplaceBy ) )
								l.setLeftMetricsKey_( leftKey.replace( LsearchFor, LreplaceBy ) )
							
							print "%s: new left metrics key: '%s'" % ( g.name, l.leftMetricsKey() )
							
						else:
							print "Note: No left key set for %s. Left unchanged." % g.name
							pass
							
					except Exception, e:
						print "Error while trying to set left key for", g.name
						print e

					# Right Metrics Key:
					try:
						# rightKey = g.rightMetricsKey
						rightKey = l.rightMetricsKey()
						rightKey = rightKey[:rightKey.find(" (")]
						
						if rightKey != None and rightKey != "":
							if RsearchFor == "":
								#g.setRightMetricsKey_( rightKey + RreplaceBy )
								l.setRightMetricsKey_( rightKey + RreplaceBy )
							else:
								#g.setRightMetricsKey_( rightKey.replace( RsearchFor, RreplaceBy ) )
								l.setRightMetricsKey_( rightKey.replace( RsearchFor, RreplaceBy ) )
							
							print "%s: new right metrics key: '%s'" % ( g.name, l.rightMetricsKey() )
							
						else:
							print "Note: No right key set for %s. Left unchanged." % g.name
							pass
							
					except Exception, e:
						print "Error while trying to set right key for", g.name
						print e
					
					g.undoManager().endUndoGrouping()
						
				except Exception, e:
					print "Error while processing glyph", g.name
					print e
					
					g.undoManager().endUndoGrouping()
			
			self.w.close()
		except Exception, e:
			raise e
		
		Glyphs.font.enableUpdateInterface()

MetricKeyReplacer()
