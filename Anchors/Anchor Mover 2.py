#MenuTitle: Anchor Mover 2.0
# -*- coding: utf-8 -*-
"""Batch-process anchor positions in selected glyphs (GUI)."""

import GlyphsApp
import vanilla
import math

listHorizontal = [
	["current position", "originalAnchor.x + italicCorrection"],
	["LSB", "0.0"],
	["RSB", "copyLayer.width"],
	["center", "copyLayer.width // 2.0"],
	["bbox left edge", "copyLayer.LSB"],
	["bbox center", "(copyLayer.LSB + (copyLayer.width - copyLayer.RSB)) // 2.0"],
	["bbox right edge", "copyLayer.width - copyLayer.RSB"],
	["highest node", "max( [ (max( [x for x in p.nodes if x.type != 65], key=lambda n: n.y )) for p in copyLayer.paths ], key=lambda n: n.y ).x + italicCorrection"],
	["lowest node", "min( [ (min( [x for x in p.nodes if x.type != 65], key=lambda n: n.y )) for p in copyLayer.paths ], key=lambda n: n.y ).x + italicCorrection"]	
]

listVertical = [
	["current position", "originalAnchor.y"],
	["ascender", "selectedAscender"],
	["cap height", "selectedCapheight"],
	["x-height", "selectedXheight"],
	["half ascender", "selectedAscender // 2.0"],
	["half cap height", "selectedCapheight // 2.0"],
	["half x-height", "selectedXheight // 2.0" ],
	["baseline", "0.0"],
	["descender", "selectedDescender"],
	["bbox top", "copyLayer.bounds.origin.y + copyLayer.bounds.size.height"],
	["bbox center", "copyLayer.bounds.origin.y + ( copyLayer.bounds.size.height // 2.0 )"],
	["bbox bottom", "copyLayer.bounds.origin.y"],
	["leftmost node", "min( [ (min( [x for x in p.nodes if x.type != 65], key=lambda n: n.x )) for p in copyLayer.paths ], key=lambda n: n.x ).y"],
	["rightmost node", "max( [ (max( [x for x in p.nodes if x.type != 65], key=lambda n: n.x )) for p in copyLayer.paths ], key=lambda n: n.x ).y"]
]

def italicSkew( x, y, angle=10.0 ):
	"""Skews x/y along the x axis and returns skewed x value."""
	
	new_angle = ( angle / 180.0 ) * math.pi
	new_x = (x) + ( y * math.tan( new_angle ) )
	
	return new_x

class AnchorMover2( object ):

	def __init__( self ):
		self.w = vanilla.FloatingWindow( (330, 170), "Anchor Mover 2.0", minSize=(300,170), maxSize=(1000,170), autosaveName="com.mekkablue.AnchorMover2.mainwindow" )

		self.w.text_1 = vanilla.TextBox((15-1, 12+2, 75, 14), "Move anchor", sizeStyle='small' )
		self.w.anchor_name = vanilla.PopUpButton((15+75, 12, -110-15-25, 17), self.GetAnchorNames(), sizeStyle='small' )
		self.w.button = vanilla.SquareButton((-110-15-20, 12, -110-15, 18), u"↺", sizeStyle='small', callback=self.SetAnchorNames )
		self.w.text_2 = vanilla.TextBox((-105-15, 12+2, -15, 14), "in selected glyphs:", sizeStyle='small' )
		
		self.w.hLine_1 = vanilla.HorizontalLine((15, 40, -15, 1))
		self.w.hText_1 = vanilla.TextBox((15-2, 40+12, 20, 14), u"↔", sizeStyle='regular' )
		self.w.hText_2 = vanilla.TextBox((15+20, 40+12+2, 20, 14), "to", sizeStyle='small' )
		self.w.hTarget = vanilla.PopUpButton((15+40, 40+12, -50-15-15-15, 17), [x[0] for x in listHorizontal], sizeStyle='small', callback=self.SavePreferences )
		self.w.hText_3 = vanilla.TextBox((-60-15-15, 40+12+2, -50-15, 14), "+", sizeStyle='small' )
		self.w.hChange = vanilla.EditText((-60-15, 40+12, -15, 19), "0.0", sizeStyle='small', callback=self.SavePreferences )
		
		self.w.vText_1 = vanilla.TextBox((15, 70+12, 20, 14), u"↕", sizeStyle='regular' )
		self.w.vText_2 = vanilla.TextBox((15+20, 70+12+2, 20, 14), "to", sizeStyle='small' )
		self.w.vTarget = vanilla.PopUpButton((15+40, 70+12, -50-15-15-15, 17), [y[0] for y in listVertical], sizeStyle='small', callback=self.SavePreferences )
		self.w.vText_3 = vanilla.TextBox((-60-15-15, 70+12+2, -50-15, 14), "+", sizeStyle='small' )
		self.w.vChange = vanilla.EditText((-60-15, 70+12, -15, 19), "0.0", sizeStyle='small', callback=self.SavePreferences )
		
		self.w.italic  = vanilla.CheckBox((15, 110, -15, 18), "Respect italic angle", value=True, sizeStyle='small', callback=self.SavePreferences )
		
		self.w.moveButton = vanilla.Button((-80-15, -20-15, -15, -15), "Move", sizeStyle='regular', callback=self.MoveCallback )
		self.w.setDefaultButton( self.w.moveButton )

		if not self.LoadPreferences( ):
			print "Error: Could not load preferences. Will resort to defaults."

		self.w.open()
	
	def SavePreferences( self, sender ):
		Glyphs.defaults["com.mekkablue.AnchorMover2.hTarget"] = self.w.hTarget.get()
		Glyphs.defaults["com.mekkablue.AnchorMover2.hChange"] = self.w.hChange.get()
		Glyphs.defaults["com.mekkablue.AnchorMover2.vTarget"] = self.w.vTarget.get()
		Glyphs.defaults["com.mekkablue.AnchorMover2.vChange"] = self.w.vChange.get()
		Glyphs.defaults["com.mekkablue.AnchorMover2.italic"] = self.w.italic.get()
		
		return True

	def LoadPreferences( self ):
		try:
			self.w.hTarget.set( Glyphs.defaults["com.mekkablue.AnchorMover2.hTarget"] )
			self.w.hChange.set( Glyphs.defaults["com.mekkablue.AnchorMover2.hChange"] )
			self.w.vTarget.set( Glyphs.defaults["com.mekkablue.AnchorMover2.vTarget"] )
			self.w.vChange.set( Glyphs.defaults["com.mekkablue.AnchorMover2.vChange"] )
			self.w.italic.set( Glyphs.defaults["com.mekkablue.AnchorMover2.italic"] )
		except:
			return False
		
		return True

	def MoveCallback( self, sender ):
		Font = Glyphs.font
		selectedLayers = Glyphs.currentDocument.selectedLayers()
		selectedMaster = Glyphs.currentDocument.selectedFontMaster()
		italicAngle = selectedMaster.italicAngle
		anchor_index = self.w.anchor_name.get()
		anchor_name  = str( self.w.anchor_name.getItems()[anchor_index] )
		horizontal_index  = self.w.hTarget.get()
		horizontal_change = float( self.w.hChange.get() )
		vertical_index  = self.w.vTarget.get()
		vertical_change = float( self.w.vChange.get() )
		
		# Keep inquiries to the objects to a minimum:
		selectedAscender  = selectedMaster.ascender
		selectedCapheight = selectedMaster.capHeight
		selectedXheight   = selectedMaster.xHeight
		selectedDescender = selectedMaster.descender
		
		print "selectedCapheight:", selectedCapheight
		
		# respecting italic angle
		respectItalic = self.w.italic.get()
		if respectItalic:
			italicCorrection = italicSkew( 0.0, selectedXheight/2.0, italicAngle )
		else:
			italicCorrection = 0.0

		evalCodeH = listHorizontal[ horizontal_index ][1]
		evalCodeV = listVertical[ vertical_index ][1]
		
		print "Processing %i glyphs..." % ( len( selectedLayers ) )
		Font.disableUpdateInterface()
		
		for originalLayer in selectedLayers:
			if originalLayer.name != None:
				thisGlyph = originalLayer.parent
				copyLayer = originalLayer.copyDecomposedLayer()
				thisGlyph.beginUndo() # not working?
				
				try:
					if respectItalic:
						for mPath in copyLayer.paths:
							for mNode in mPath.nodes:
								mNode.x = italicSkew( mNode.x, mNode.y, -italicAngle )
							
						for mAnchor in copyLayer.anchors:
							mAnchor.x = italicSkew( mAnchor.x, mAnchor.y, -italicAngle )
							
					for originalAnchor in originalLayer.anchors:
						if originalAnchor.name == anchor_name:
							old_anchor_x = originalAnchor.x
							old_anchor_y = originalAnchor.y
							xMove = eval( evalCodeH ) + horizontal_change
							yMove = eval( evalCodeV ) + vertical_change
						
							# Ignore moves relative to bbox if there are no paths:
							if not copyLayer.paths:
								if "bounds" in evalCodeH:
									xMove = old_anchor_x
						
								if "bounds" in evalCodeV:
									yMove = old_anchor_y
						
							# Only move if the calculated position differs from the original one:
							if [ int(old_anchor_x + italicCorrection), int(old_anchor_y) ] != [ int(xMove), int(yMove) ]:
							
								if respectItalic:
									# skew back
									xMove = italicSkew( xMove, yMove, italicAngle ) - italicCorrection
									old_anchor_x = italicSkew( old_anchor_x, old_anchor_y, italicAngle ) - italicCorrection
						
								originalAnchor.position = NSMakePoint( xMove, yMove )
						
								print "Moved %s anchor from %i, %i to %i, %i in %s." % ( anchor_name, old_anchor_x, old_anchor_y, xMove, yMove, thisGlyph.name )
							
				except Exception, e:
					print "ERROR: Failed to move anchor in %s." % thisGlyph.name
					print e
				finally:
					thisGlyph.endUndo()
			
				thisGlyph.endUndo()

		Font.enableUpdateInterface() 
		print "Done."
	
	def GetAnchorNames( self ):
		myAnchorList = []
		selectedLayers = Glyphs.currentDocument.selectedLayers()
		
		try:
			for thisLayer in selectedLayers:
				AnchorNames = list( thisLayer.anchors.keys() ) # hack to avoid traceback
				for thisAnchorName in AnchorNames:
					if thisAnchorName not in myAnchorList:
						myAnchorList.append( str(thisAnchorName) )
		except:
			print "Error: Cannot collect anchor names from the current selection."
		
		return sorted( myAnchorList )
	
	def SetAnchorNames( self, sender ):
		try:
			anchorList = self.GetAnchorNames()
			self.w.anchor_name.setItems( anchorList )
		except Exception, e:
			print e

AnchorMover2()
