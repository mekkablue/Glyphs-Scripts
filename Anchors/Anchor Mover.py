#MenuTitle: Anchor Mover
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Batch-process anchor positions in selected glyphs (GUI).
"""

import vanilla, math
from Foundation import NSPoint

def highestNodeInLayer(layer):
	highest = None
	for p in layer.paths:
		for n in p.nodes:
			if n.type != GSOFFCURVE:
				if highest is None or highest.y<n.y:
					highest = n
	return highest

def lowestNodeInLayer(layer):
	lowest = None
	for p in layer.paths:
		for n in p.nodes:
			if n.type != GSOFFCURVE:
				if lowest is None or lowest.y>n.y:
					lowest = n
	return lowest

def rightmostNodeInLayer(layer):
	rightmost = None
	for p in layer.paths:
		for n in p.nodes:
			if n.type != GSOFFCURVE:
				if rightmost is None or rightmost.x<n.x:
					rightmost = n
	return rightmost

def leftmostNodeInLayer(layer):
	leftmost = None
	for p in layer.paths:
		for n in p.nodes:
			if n.type != GSOFFCURVE:
				if leftmost is None or leftmost.x>n.x:
					leftmost = n
	return leftmost



listHorizontal = (
	("current position", "copyAnchor.x"),
	("LSB", "0.0"),
	("RSB", "copyLayer.width"),
	("center", "copyLayer.width // 2.0"),
	("bbox left edge", "copyLayer.bounds.origin.x"),
	("bbox center", "copyLayer.bounds.origin.x + copyLayer.bounds.size.width // 2.0"),
	("bbox right edge", "copyLayer.bounds.origin.x + copyLayer.bounds.size.width"),
	("highest node", "highestNodeInLayer(copyLayer).x"),
	("lowest node", "lowestNodeInLayer(copyLayer).x"),
)

listVertical = (
	("current position", "copyAnchor.y"),
	("ascender", "selectedAscender"),
	("cap height", "selectedCapheight"),
	("smallcap height", "originalMaster.customParameters['smallCapHeight']"),
	("x-height", "selectedXheight"),
	("half ascender", "selectedAscender // 2.0"),
	("half cap height", "selectedCapheight // 2.0"),
	("half smallcap height", "originalMaster.customParameters['smallCapHeight']/2"),
	("half x-height", "selectedXheight // 2.0" ),
	("baseline", "0.0"),
	("descender", "selectedDescender"),
	("bbox top", "copyLayer.bounds.origin.y + copyLayer.bounds.size.height"),
	("bbox center", "copyLayer.bounds.origin.y + ( copyLayer.bounds.size.height // 2.0 )"),
	("bbox bottom", "copyLayer.bounds.origin.y"),
	("leftmost node", "leftmostNodeInLayer(copyLayer).y"),
	("rightmost node", "rightmostNodeInLayer(copyLayer).y"),
)

def italicSkew( x, y, angle=10.0 ):
	"""Skews x/y along the x axis and returns skewed x value."""
	new_angle = ( angle / 180.0 ) * math.pi
	return x + y * math.tan( new_angle )

class AnchorMover2( object ):

	def __init__( self ):
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w = vanilla.FloatingWindow( (500, 175), "Anchor Mover", minSize=(350,175), maxSize=(1000,175), autosaveName="com.mekkablue.AnchorMover2.mainwindow" )

		self.w.text_1 = vanilla.TextBox((inset, linePos+2, inset+60, 14), "Move anchor", sizeStyle='small' )
		self.w.anchor_name = vanilla.PopUpButton((inset+75, linePos, -110-inset-25, 17), self.GetAnchorNames(), sizeStyle='small' )
		self.w.button = vanilla.SquareButton((-110-inset-20, linePos, -110-inset, 18), u"↺", sizeStyle='small', callback=self.SetAnchorNames )
		self.w.text_2 = vanilla.TextBox((-105-15, linePos+2, -inset, 14), "in selected glyphs:", sizeStyle='small' )
		linePos += lineHeight
		

		self.w.hText_1 = vanilla.TextBox((inset-2, linePos, 20, 14), u"↔", sizeStyle='regular' )
		self.w.hText_2 = vanilla.TextBox((inset+20, linePos+2, 20, 14), "to", sizeStyle='small' )
		self.w.hTarget = vanilla.PopUpButton((inset+40, linePos, -50-15-15-inset, 17), [x[0] for x in listHorizontal], sizeStyle='small', callback=self.SavePreferences )
		self.w.hText_3 = vanilla.TextBox((-60-15-15, linePos+2, -50-inset, 14), "+", sizeStyle='small' )
		self.w.hChange = vanilla.EditText((-60-15, linePos, -inset, 19), "0.0", sizeStyle='small', callback=self.SavePreferences )
		linePos += lineHeight
		
		self.w.vText_1 = vanilla.TextBox((inset, linePos, 20, 14), u"↕", sizeStyle='regular' )
		self.w.vText_2 = vanilla.TextBox((inset+20, linePos+2, 20, 14), "to", sizeStyle='small' )
		self.w.vTarget = vanilla.PopUpButton((inset+40, linePos, -50-15-15-inset, 17), [y[0] for y in listVertical], sizeStyle='small', callback=self.SavePreferences )
		self.w.vText_3 = vanilla.TextBox((-60-15-15, linePos+2, -50-inset, 14), "+", sizeStyle='small' )
		self.w.vChange = vanilla.EditText((-60-15, linePos, -inset, 19), "0.0", sizeStyle='small', callback=self.SavePreferences )
		linePos += lineHeight
		
		self.w.italic  = vanilla.CheckBox((inset, linePos, -inset, 18), "Respect italic angle", value=True, sizeStyle='small', callback=self.SavePreferences )
		linePos += lineHeight

		self.w.allMasters = vanilla.CheckBox( (inset, linePos, -inset, 20), u"All masters and special layers (otherwise only current masters)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.moveButton = vanilla.Button((-80-15, -20-15, -15, -15), "Move", sizeStyle='regular', callback=self.MoveCallback )
		self.w.setDefaultButton( self.w.moveButton )

		if not self.LoadPreferences( ):
			print("Error: Could not load preferences. Will resort to defaults.")

		self.w.open()
		self.w.makeKey()
	
	def SavePreferences( self, sender ):
		Glyphs.defaults["com.mekkablue.AnchorMover2.hTarget"] = self.w.hTarget.get()
		Glyphs.defaults["com.mekkablue.AnchorMover2.hChange"] = self.w.hChange.get()
		Glyphs.defaults["com.mekkablue.AnchorMover2.vTarget"] = self.w.vTarget.get()
		Glyphs.defaults["com.mekkablue.AnchorMover2.vChange"] = self.w.vChange.get()
		Glyphs.defaults["com.mekkablue.AnchorMover2.italic"] = self.w.italic.get()
		Glyphs.defaults["com.mekkablue.AnchorMover2.allMasters"] = self.w.allMasters.get()
		
		return True

	def LoadPreferences( self ):
		Glyphs.registerDefault( "com.mekkablue.AnchorMover2.hTarget", 0.0 )
		Glyphs.registerDefault( "com.mekkablue.AnchorMover2.hChange", 0.0 )
		Glyphs.registerDefault( "com.mekkablue.AnchorMover2.vTarget", 0.0 )
		Glyphs.registerDefault( "com.mekkablue.AnchorMover2.vChange", 0.0 )
		Glyphs.registerDefault( "com.mekkablue.AnchorMover2.italic", True )
		Glyphs.registerDefault( "com.mekkablue.AnchorMover2.allMasters", False )
		try:
			self.w.hTarget.set( Glyphs.defaults["com.mekkablue.AnchorMover2.hTarget"] )
			self.w.hChange.set( Glyphs.defaults["com.mekkablue.AnchorMover2.hChange"] )
			self.w.vTarget.set( Glyphs.defaults["com.mekkablue.AnchorMover2.vTarget"] )
			self.w.vChange.set( Glyphs.defaults["com.mekkablue.AnchorMover2.vChange"] )
			self.w.italic.set( Glyphs.defaults["com.mekkablue.AnchorMover2.italic"] )
			self.w.allMasters.set( Glyphs.defaults["com.mekkablue.AnchorMover2.allMasters"] )
		except:
			return False
		return True
	
	def prefAsFloat(self, pref):
		try:
			return float( Glyphs.defaults[pref] )
		except:
			Glyphs.defaults[pref] = 0.0
			self.LoadPreferences()
			return 0.0

	def MoveCallback( self, sender ):
		Font = Glyphs.font
		selectedLayers = Font.selectedLayers
		anchor_index = self.w.anchor_name.get()
		anchor_name  = self.w.anchor_name.getItems()[anchor_index]
		horizontal_index  = Glyphs.defaults["com.mekkablue.AnchorMover2.hTarget"]
		horizontal_change = self.prefAsFloat("com.mekkablue.AnchorMover2.hChange")
		vertical_index  = Glyphs.defaults["com.mekkablue.AnchorMover2.vTarget"]
		vertical_change = self.prefAsFloat("com.mekkablue.AnchorMover2.vChange")
		allMasters = Glyphs.defaults["com.mekkablue.AnchorMover2.allMasters"]
		
		# respecting italic angle
		respectItalic = Glyphs.defaults["com.mekkablue.AnchorMover2.italic"]

		evalCodeH = listHorizontal[ horizontal_index ][1]
		evalCodeV = listVertical[ vertical_index ][1]
		
		if not selectedLayers:
			print("No glyphs selected.")
			Message(title="No Glyphs Selected", message="Could not move anchors. No glyphs were selected.", OKButton=None)
		else:
			print("Processing %i glyphs..." % ( len( selectedLayers ) ))
			Font.disableUpdateInterface()
			for selectedLayer in selectedLayers:
				selectedGlyph = selectedLayer.glyph()
				if allMasters:
					originalLayers = (l for l in selectedGlyph.layers if l.isMasterLayer or l.isSpecialLayer)
				else:
					originalLayers = (selectedLayer,)
				for originalLayer in originalLayers:
					originalMaster = originalLayer.master
					italicAngle = originalMaster.italicAngle

					selectedAscender  = originalMaster.ascender
					selectedCapheight = originalMaster.capHeight
					selectedDescender = originalMaster.descender
					selectedXheight   = originalMaster.xHeight
					
					italicCorrection = 0.0
					if respectItalic and italicAngle:
						italicCorrection = italicSkew( 0.0, selectedXheight/2.0, italicAngle )
						print("italicCorrection", italicCorrection)
					
					if originalLayer.name != None:
						if len(originalLayer.anchors) > 0:
							thisGlyph = originalLayer.parent
					
							# create a layer copy that can be slanted backwards if necessary
							copyLayer = originalLayer.copyDecomposedLayer()
							thisGlyph.beginUndo() # not working?
				
							try:
								if italicAngle and respectItalic:
									# slant the layer copy backwards
									for mPath in copyLayer.paths:
										for mNode in mPath.nodes:
											mNode.x = italicSkew( mNode.x, mNode.y, -italicAngle ) + italicCorrection
									for mAnchor in copyLayer.anchors:
										mAnchor.x = italicSkew( mAnchor.x, mAnchor.y, -italicAngle ) + italicCorrection

								for copyAnchor in copyLayer.anchors:
									if copyAnchor.name == anchor_name:
										old_anchor_x = copyAnchor.x
										old_anchor_y = copyAnchor.y
										xMove = eval( evalCodeH ) + horizontal_change
										yMove = eval( evalCodeV ) + vertical_change
						
										# Ignore moves relative to bbox if there are no paths:
										if not copyLayer.paths:
											if "bounds" in evalCodeH:
												xMove = old_anchor_x
						
											if "bounds" in evalCodeV:
												yMove = old_anchor_y
						
										# Only move if the calculated position differs from the original one:
										if [ int(old_anchor_x), int(old_anchor_y) ] != [ int(xMove), int(yMove) ]:
							
											if italicAngle and respectItalic:
												# skew back
												xMove = italicSkew( xMove, yMove, italicAngle ) - italicCorrection
												old_anchor_x = italicSkew( old_anchor_x, old_anchor_y, italicAngle ) - italicCorrection
						
											originalAnchor = [a for a in originalLayer.anchors if a.name == anchor_name][0]
											originalAnchor.position = NSPoint( xMove, yMove )
						
											print("Moved %s anchor from %i, %i to %i, %i in %s." % ( anchor_name, old_anchor_x, old_anchor_y, xMove, yMove, thisGlyph.name ))
										else:
											print("Keeping %s anchor at %i, %i in %s." % ( anchor_name, old_anchor_x, old_anchor_y, thisGlyph.name ))
							
							except Exception as e:
								print("ERROR: Failed to move anchor in %s." % thisGlyph.name)
								print(e)
								import traceback
								print(traceback.format_exc())
							finally:
								thisGlyph.endUndo()
					
			Font.enableUpdateInterface()
		print("Done.")
	
	def GetAnchorNames( self ):
		myAnchorList = []
		selectedLayers = Glyphs.currentDocument.selectedLayers()
		try:
			for thisLayer in selectedLayers:
				AnchorNames = list( thisLayer.anchors.keys() ) # hack to avoid traceback
				for thisAnchorName in AnchorNames:
					if thisAnchorName not in myAnchorList:
						myAnchorList.append( thisAnchorName )
		except:
			print("Error: Cannot collect anchor names from the current selection.")
		
		return sorted( myAnchorList )
	
	def SetAnchorNames( self, sender ):
		anchorList = self.GetAnchorNames()
		self.w.anchor_name.setItems( anchorList )

AnchorMover2()
