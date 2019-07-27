#MenuTitle: Reorder Unicodes of Selected Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Reorders Unicodes so that default Unicode comes first.
"""

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def buildUnicodeSet(unicodes):
	g = Layer.parent
	print g. unicode
	print type(g.unicodes()[0])
	# g.setUnicodes_( NSSet.initWithArray_(["E780","0192"]) )

def reorderUnicodes( thisGlyph ):
	defaultUnicode = Glyphs.glyphInfoForName( thisGlyph.name ).unicode
	oldUnicodes = thisGlyph.unicodes()
	if oldUnicodes:
		oldUnicodes = list(oldUnicodes)
		if len(oldUnicodes) > 1:
			if defaultUnicode:
				orderedUnicodes = []
				try:
					i = oldUnicodes.index(defaultUnicode)
					try:
						orderedUnicodes.append( oldUnicodes.pop(i) ) # add the default as the first one
						orderedUnicodes.extend( oldUnicodes ) # add the rest
						if orderedUnicodes != oldUnicodes:
							print "---> %s: %s" % ( thisGlyph.name, ", ".join(orderedUnicodes) )
							unicodeSet = NSArray.alloc().initWithArray_( orderedUnicodes )
							thisGlyph.setUnicodesArray_( unicodeSet )
					except Exception as e:
						print e
						print
						import traceback
						print traceback.format_exc()
				except:
					print "- %s: No default (%s) among unicodes (%s); left unchanged." % (thisGlyph.name, defaultUnicode, ", ".join(oldUnicodes))
			else:
				print "- %s: No unicode defined in Glyph Info; left unchanged (%s)" % (thisGlyph.name, ", ".join(oldUnicodes) if oldUnicodes else "-")
		else:
			print "- %s: Only one unicode set (%s); left unchanged." % (thisGlyph.name, oldUnicodes[0])
	else:
		print "- %s: No unicodes set, nothing to reorder." % (thisGlyph.name)

thisFont.disableUpdateInterface() # suppresses UI updates in Font View

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()
print "Reorder Unicodes of Selected Glyphs"
print "Processing Unicodes of %i selected glyphs:" % len(selectedLayers)

for thisLayer in selectedLayers:
	thisGlyph = thisLayer.parent
	thisGlyph.beginUndo() # begin undo grouping
	reorderUnicodes( thisGlyph )
	thisGlyph.endUndo()   # end undo grouping

thisFont.enableUpdateInterface() # re-enables UI updates in Font View
