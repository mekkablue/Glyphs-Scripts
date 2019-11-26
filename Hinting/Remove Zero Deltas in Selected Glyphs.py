from __future__ import print_function
#MenuTitle: Remove Zero Deltas in Selected Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Goes through all layers of each selected glyph, and deletes all TT Delta Hints with an offset of zero. Detailed Report in Macro Window.
"""

def process( Layer ):
	try:
		count = 0
		for i in reversed(range(len(Layer.hints))):
			hint = Layer.hints[i]
			if hint.type == TTDELTA:
				elementDict = hint.elementDict()
				if "settings" in elementDict:
					settings = elementDict["settings"]
					if settings:
						for deltaType in ("deltaH","deltaV"):
							if deltaType in settings:
								for transformType in settings[deltaType]:
									deltas = settings[deltaType][transformType]
									for ppmSize in deltas:
										if deltas[ppmSize] == 0:
											del deltas[ppmSize]
											count += 1
									
									# clean up delta PPMs:
									if len(settings[deltaType][transformType]) == 0:
										del settings[deltaType][transformType]
								
								# clean up delta directions:
								if len(settings[deltaType]) == 0:
									del settings[deltaType]
					
					# clean up hints:
					if not elementDict["settings"]:
						del Layer.hints[i]

		print("  Deleted %i zero delta%s on layer '%s'." % (
			count,
			"" if count == 1 else "s",
			Layer.name,
		))
	
		return count
	except Exception as e:
		Glyphs.showMacroWindow()
		import traceback
		print(traceback.format_exc())
		print()
		print(e)

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
Glyphs.clearLog() # clears log in Macro window

totalCount = 0
for selectedLayer in selectedLayers:
	thisGlyph = selectedLayer.parent
	print("%s:" % thisGlyph.name)
	thisGlyph.beginUndo() # begin undo grouping
	for thisLayer in thisGlyph.layers:
		totalCount += process( thisLayer )
	thisGlyph.endUndo()   # end undo grouping

if totalCount:
	Message(
		title="%i Zero Delta%s Deleted" % (
			totalCount,
			"" if totalCount == 1 else "s",
		), 
		message="Deleted %i TT delta hint%s with zero offset in %i selected glyph%s (%s%s). Detailed report in Macro Window." % (
			totalCount,
			"" if totalCount == 1 else "s",
			len(selectedLayers),
			"" if len(selectedLayers) == 1 else "s",
			", ".join([l.parent.name for l in selectedLayers[:min(20,len(selectedLayers))]]),
			",..." if len(selectedLayers) > 20 else "",
		), 
		OKButton=u"👍🏻 OK",
		)
else:
	Message(
		title="No Zero Deltas",
		message="No TT delta hints with zero offset were found in selected glyph%s (%s%s)." % (
			"" if len(selectedLayers) == 1 else "s",
			", ".join([l.parent.name for l in selectedLayers[:min(20,len(selectedLayers))]]),
			",..." if len(selectedLayers) > 20 else "",
		),
		OKButton=u"🍸 Cheers")
