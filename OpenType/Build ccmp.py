#MenuTitle: Build ccmp feature and dotless letters
# -*- coding: utf-8 -*-
"""Builds dotlessi, dotlessj and the corresponding ccmp feature."""

import GlyphsApp
Font = Glyphs.font

def updated_code( oldcode, beginsig, endsig, newcode ):
	"""Replaces text in oldcode with newcode, but only between beginsig and endsig."""
	begin_offset = oldcode.find( beginsig )
	end_offset   = oldcode.find( endsig ) + len( endsig )
	newcode = oldcode[:begin_offset] + beginsig + newcode + "\n" + endsig + oldcode[end_offset:]
	return newcode

def create_otfeature( featurename = "calt", 
                      featurecode = "# empty feature code", 
                      targetfont  = Font,
                      codesig     = "DEFAULT-CODE-SIGNATURE" ):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	"""
	
	beginSig = "# BEGIN " + codesig + "\n"
	endSig   = "# END "   + codesig + "\n"
	
	if featurename in [ f.name for f in targetfont.features ]:
		# feature already exists:
		targetfeature = targetfont.features[ featurename ]
		
		if beginSig in targetfeature.code:
			# replace old code with new code:
			targetfeature.code = updated_code( targetfeature.code, beginSig, endSig, featurecode )
		else:
			# append new code:
			targetfeature.code += "\n" + beginSig + featurecode + "\n" + endSig
			
		return "Updated existing OT feature '%s'." % featurename
	else:
		# create feature with new code:
		newFeature = GSFeature()
		newFeature.name = featurename
		newFeature.code = beginSig + featurecode + "\n" + endSig
		targetfont.features.append( newFeature )
		return "Created new OT feature '%s'" % featurename

def create_otclass( classname   = "@default", 
                    classglyphs = [ x.parent.name for x in Font.selectedLayers ], 
                    targetfont  = Font ):
	"""
	Creates an OpenType class in the font.
	Default: class @default with currently selected glyphs in the current font.
	Returns a status message in form of a string.
	"""
	
	# strip '@' from beginning:
	if classname[0] == "@":
		classname = classname[1:]
	
	classCode = " ".join( classglyphs )
	
	if classname in [ c.name for c in targetfont.classes ]:
		targetfont.classes[classname].code = classCode
		return "Updated existing OT class '%s'." % classname
	else:
		newClass = GSClass()
		newClass.name = classname
		newClass.code = classCode
		targetfont.classes.append( newClass )
		return "Created new OT class: '%s'" % classname

def removeDot( thisLayer ):
	numOfPaths = len( thisLayer.paths )

	if numOfPaths > 1:
		highest = 0
		highestID = 0
		
		for i in range( numOfPaths ):
			p = thisLayer.paths[i]
			top = p.bounds.origin.y + p.bounds.size.height
			if top > highest:
				highest = top
				highestID = i
			
		del thisLayer.paths[ highestID ]
	
	for i in range( len( thisLayer.components ) )[::1]:
		if thisLayer.components[i].componentName == "dotaccent":
			del thisLayer.components[i]

def addTopAnchor( thisLayer ):
	anchorName = "top"
	
	if not thisLayer.anchors[ anchorName ]:
		xPos = thisLayer.bounds.origin.x + thisLayer.bounds.size.width / 2.0
		yPos = Font.masters[ str( thisLayer.associatedMasterId ) ].xHeight
		
		topAnchor = GSAnchor()
		topAnchor.name = anchorName
		topAnchor.position = NSPoint( xPos, yPos )
		
		thisLayer.addAnchor_( topAnchor )
	

def makeDotlessGlyph( sourceGlyph, targetGlyphName ):
	# Create new glyph:
	dotlessGlyph = sourceGlyph.copy()
	dotlessGlyph.name = targetGlyphName
	Font.glyphs.append( dotlessGlyph )
	
	# Add top anchor:
	for thisLayer in Font.glyphs[ dotlessGlyph.name ].layers:
		removeDot( thisLayer )
		addTopAnchor( thisLayer )
	
	return "Added %s to the font." % targetGlyphName
	
	
	
allGlyphNames = [ g.name for g in Font.glyphs ]
ccmpGlyphPairs = [ ["i", "dotlessi"], ["j", "dotlessj"] ]
ccmpName = "ccmp"
ccmpCode = ""
ccmpCombiningMarksClass = "CombiningMarks"
ccmpCombiningMarksNames = [ g.name for g in Font.glyphs if g.unicode and g.unicode[:2] == "03" ]

print create_otclass( classname=ccmpCombiningMarksClass, classglyphs=ccmpCombiningMarksNames, targetfont=Font )

Font.disableUpdateInterface()

for thisGlyphPair in ccmpGlyphPairs:
	dottedGlyphName = thisGlyphPair[0]
	dotlessGlyphName = thisGlyphPair[1]
	
	if dottedGlyphName in allGlyphNames:
		if dotlessGlyphName not in allGlyphNames:
			print makeDotlessGlyph( sourceGlyph = Font.glyphs[dottedGlyphName], targetGlyphName = dotlessGlyphName )
		
		ccmpCode += "sub %s' @%s by %s;\n" % ( dottedGlyphName, ccmpCombiningMarksClass, dotlessGlyphName )

Font.enableUpdateInterface()

print create_otfeature( featurename=ccmpName, featurecode=ccmpCode, codesig="LATIN-DOTLESS-CCMP", targetfont=Font )