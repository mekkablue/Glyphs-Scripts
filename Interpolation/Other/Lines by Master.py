#MenuTitle: Lines by Master
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Reduplicates your edit text across masters, will add one line per master. Careful, ignores everything after the first newline.
"""

from Foundation import NSMutableAttributedString, NSAttributedString

cutoff = []
names = []
for i,l in enumerate(Font.currentTab.layers):
	if type(l) == GSControlLayer:
		cutoff.append(i)
	else:
		if not cutoff:
			names.append( l.parent.name )

theseLayers = []
for m in Font.masters:
	for gname in names:
		layer = Font.glyphs[gname].layers[m.id]
		# print(layer)
		theseLayers.append( layer )
	
	theseLayers.append( GSControlLayer.newline() )

if theseLayers:
	# Font.currentTab.layers.append( theseLayers ) # BROKEN IN 1224
	# WORKAROUND:
	string = NSMutableAttributedString.alloc().init()
	for l in theseLayers:
		if l.className() == "GSLayer":
			char = Font.characterForGlyph_(l.parent)
			try:
				# GLYPHS 3
				A = NSAttributedString.alloc().initWithString_attributes_(chr(char), {"GSLayerIdAttrib": l.layerId})
			except:
				# GLYPHS 2
				A = NSAttributedString.alloc().initWithString_attributes_(unichr(char), {"GSLayerIdAttrib": l.layerId})
		elif l.className() == "GSBackgroundLayer":
			char = Font.characterForGlyph_(l.parent)
			try:
				# GLYPHS 3
				A = NSAttributedString.alloc().initWithString_attributes_(chr(char), {"GSLayerIdAttrib": l.layerId, "GSShowBackgroundAttrib": True})
			except:
				# GLYPHS 2
				A = NSAttributedString.alloc().initWithString_attributes_(unichr(char), {"GSLayerIdAttrib": l.layerId, "GSShowBackgroundAttrib": True})
		elif l.className() == "GSControlLayer":
			char = l.parent.unicodeChar()
			try:
				# GLYPHS 3
				A = NSAttributedString.alloc().initWithString_(chr(char))
			except:
				# GLYPHS 2
				A = NSAttributedString.alloc().initWithString_(unichr(char))
		else:
			raise ValueError
		string.appendAttributedString_(A)
	Font.currentTab.graphicView().textStorage().setText_(string)
	