#MenuTitle: Move Vietnamese Marks to top_viet Anchor in Circumflex
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Where possible, puts acute(comb), grave(comb), hookabovecomb on 'top_viet' position in all layers in all selected glyphs. Assumes that you have a 'top_viet' anchor in circumflex. Useful for Vietnamese glyphs.
"""

accentsToBeMoved = ("acute", "grave", "hookabovecomb", "acutecomb", "gravecomb")
newAnchor = "top_viet"

Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Font.selectedLayers ]

def baseHasAnchor( thisComponent, masterID, anchorToLookFor = "top_viet" ):
	baseGlyph = thisComponent.component
	baseLayer = baseGlyph.layers[masterID]
	baseAnchors = [a for a in baseLayer.anchors]
	anchorIsInLayer = False
	for i in range(len(baseAnchors)):
		if baseAnchors[i].name == anchorToLookFor:
			anchorIsInLayer = True
	return anchorIsInLayer

def nameUntilFirstDot( thisName ):
	dotIndex = thisName.find(".")
	if dotIndex > 0:
		return thisName[:dotIndex]
	else:
		return thisName

def withoutLeadingUnderscore( thisName ):
	if thisName and thisName.startswith("_"):
		return thisName[1:]
	else:
		return thisName

def process( thisGlyph ):
	statusString = "\nProcessing %s" % thisGlyph.name
	for thisLayer in thisGlyph.layers:
		if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
			try:
				# Glyphs 3
				components = [c for c in thisLayer.shapes if c.type==GSComponent]
			except:
				# Glyphs 2
				components = thisLayer.components
			
			numOfComponents = len( components )
			previousComponent = None
			if numOfComponents > 2:
				for accentComponent in components:
					if not previousComponent:
						# first component, should be base letter:
						previousComponent = accentComponent
					else:
						# second or third component:
						accentName = withoutLeadingUnderscore(nameUntilFirstDot( accentComponent.componentName ))
						if accentName in accentsToBeMoved:
							baseComponent = previousComponent
							if baseComponent:
								if baseHasAnchor( baseComponent, thisLayer.master.id, anchorToLookFor=newAnchor ):
									try:
										accentComponent.setAnchor_( newAnchor )
										statusString += "\n✅ %s: moved %s on %s." % ( thisLayer.name, accentName, newAnchor )
									except Exception as e:
										return "\n❌ ERROR in %s %s:\nCould not move %s onto %s.\n%s" % ( thisGlyph.name, thisLayer.name, accentName, newAnchor, e )
			else:
				statusString += "\n⚠️ %s: only %i components, skipping." % ( thisLayer.name, numOfComponents )
			
	return statusString

Glyphs.clearLog() # clears macro window log
print("Move Vietnamese Marks to top_viet Anchor in Circumflex")

for thisGlyph in selectedGlyphs:
	thisGlyph.beginUndo()
	print(process( thisGlyph ))
	thisGlyph.endUndo()

