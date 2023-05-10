#MenuTitle: Lines by Master
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Reduplicates your edit text across masters, will add one line per master. Careful, ignores everything after the first newline.
"""

from Foundation import NSMutableAttributedString, NSAttributedString
thisFont = Glyphs.font

glyphs3 = Glyphs.versionNumber >= 3
cutoff = []
names = []
for i,l in enumerate(thisFont.currentTab.layers):
	if type(l) == GSControlLayer:
		cutoff.append(i)
	else:
		if not cutoff:
			names.append( l.parent.name )

theseLayers = []
for m in thisFont.masters:
	for gname in names:
		layer = thisFont.glyphs[gname].layers[m.id]
		# print(layer)
		theseLayers.append( layer )
	
	theseLayers.append( GSControlLayer.newline() )

def charFromCode(charCode):
	if glyphs3:
		return chr(charCode)
	return unichr(charCode)

if theseLayers:
	# thisFont.currentTab.layers.append( theseLayers ) # BROKEN IN 1224
	# WORKAROUND:
	string = NSMutableAttributedString.alloc().init()
	for l in theseLayers:
		if l.className() == "GSLayer":
			char = charFromCode( thisFont.characterForGlyph_(l.parent) )
			A = NSAttributedString.alloc().initWithString_attributes_(char, {"GSLayerIdAttrib": l.layerId})
		elif l.className() == "GSBackgroundLayer":
			char = charFromCode( thisFont.characterForGlyph_(l.parent) )
			A = NSAttributedString.alloc().initWithString_attributes_(char, {"GSLayerIdAttrib": l.layerId, "GSShowBackgroundAttrib": True})
		elif l.className() == "GSControlLayer":
			char = charFromCode( l.parent.unicodeChar() )
			A = NSAttributedString.alloc().initWithString_(char)
		else:
			raise ValueError
		string.appendAttributedString_(A)
	thisFont.currentTab.graphicView().textStorage().setText_(string)
	