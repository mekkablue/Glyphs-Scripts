#MenuTitle: Rebuild Components in Place
# -*- coding: utf-8 -*-
__doc__="""
Moves outlines to background, then tries to rebuild the glyph with components in the foreground. Tries to position the accents as precisely as possible.
"""

import GlyphsApp
import traceback

Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = Font.selectedLayers

def boundsForPaths( thesePaths ):
	thisOriginX = min( [p.bounds.origin.x for p in thesePaths] )
	thisOriginY = min( [p.bounds.origin.y for p in thesePaths] )
	thisTopRightX = max( [p.bounds.origin.x + p.bounds.size.width  for p in thesePaths] )
	thisTopRightY = max( [p.bounds.origin.y + p.bounds.size.height for p in thesePaths] )
	returnRect = NSRect()
	returnRect.origin = NSPoint( thisOriginX, thisOriginY )
	returnRect.size.width  = thisTopRightX - thisOriginX
	returnRect.size.height = thisTopRightY - thisOriginY
	return returnRect

def centerOfRect( thisRect ):
	centerX = ( thisRect.origin.x * 2 + thisRect.size.width ) / 2.0
	centerY = ( thisRect.origin.y * 2 + thisRect.size.height ) / 2.0
	return NSPoint( centerX, centerY )

def process( thisLayer ):
	pathCount = len( thisLayer.paths )
	componentCount = len( thisLayer.components )

	if pathCount > 0 and componentCount == 0:
		try:
			thisGlyph = thisLayer.parent
			thisGlyphInfo = Glyphs.glyphInfoForName( thisGlyph.name )
			baseglyphInfo = thisGlyphInfo.components[0]
			nameOfBaseglyph = baseglyphInfo.name
			baseglyph = Font.glyphs[ nameOfBaseglyph ]
			baseglyphLayer = baseglyph.layers[ FontMaster.id ]

			accentInfo = thisGlyphInfo.components[1]
			nameOfAccent = accentInfo.name
			isTopAccent = "_top" in "".join( accentInfo.anchors ) # finds both _top and _topright
			accent = Font.glyphs[ nameOfAccent ]
			if not accent:
				nameOfAccent = nameOfAccent.replace("comb","")
				accent = Font.glyphs[ nameOfAccent ]
			accentLayer = accent.layers[ FontMaster.id ]

			# move contents of layer to its background:
			thisLayer.setBackground_( thisLayer )
			thisLayer.setPaths_( None )
			thisLayer.setComponents_( None )
			thisLayer.setAnchors_( None )

			print "Rebuilding", thisGlyph.name

			# find the offset of the accent component:
			centerOfAccent = centerOfRect( accentLayer.bounds )
			pathcountOfAccent = len( accentLayer.paths )
			if isTopAccent:
				originalAccentPaths = sorted( thisLayer.background.paths, key=lambda p: p.bounds.origin.y + p.bounds.size.height )[-pathcountOfAccent:]
			else:
				originalAccentPaths = sorted( thisLayer.background.paths, key=lambda p: p.bounds.origin.y )[:pathcountOfAccent]
			boundsOfOriginalAccent = boundsForPaths( originalAccentPaths )
			centerOfOriginalAccent = centerOfRect( boundsOfOriginalAccent )
			offsetX = centerOfOriginalAccent.x - centerOfAccent.x
			offsetY = centerOfOriginalAccent.y - centerOfAccent.y
			offset = NSPoint( offsetX, offsetY )
			
			# disable alignment for layer:
			thisLayer.setHasAlignedWidth_(False)

			baseglyphComponent = GSComponent( nameOfBaseglyph )
			baseglyphComponent.automaticAlignment = False # comment to enable alignment of base glyph
			accentComponent = GSComponent( nameOfAccent, offset )
			accentComponent.automaticAlignment = False

			thisLayer.addComponent_( baseglyphComponent )
			thisLayer.addComponent_( accentComponent )
		except:
			print "Failed to rebuild %s" % thisGlyph.name
			print traceback.format_exc()
			

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo()
	process( thisLayer )
	thisGlyph.endUndo()

Font.enableUpdateInterface()
