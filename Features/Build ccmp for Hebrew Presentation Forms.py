# MenuTitle: Build ccmp for Hebrew Presentation Forms
__doc__ = """
Builds the ccmp for precomposed uniFBxx glyphs, e.g. if you have pedagesh, you get 'sub pe dagesh by pedagesh' in your ccmp.
"""

from mekkablue import createOTFeature
from GlyphsApp import Glyphs, Message


lookupTitle = "hebrewPresentationForms"
thisFont = Glyphs.font
theseGlyphs = thisFont.glyphs if thisFont else ()


lookup = ""

for thisGlyph in theseGlyphs:
	if thisGlyph.unicode and thisGlyph.unicode[:2] == "FB" and thisGlyph.script == "hebrew":
		glyphName = thisGlyph.name
		components = thisGlyph.glyphInfo.components
		if components:
			componentNames = [c.name for c in components]
			snippet = None
			if all([thisFont.glyphs[n] for n in componentNames]):
				snippet = " ".join(componentNames)
			elif len(thisGlyph.layers[0].components) > 1:
				snippet = " ".join([c.componentName for c in thisGlyph.layers[0].components])
			if snippet:
				lookup += "\tsub %s by %s;  # %s\n" % (snippet, glyphName, thisGlyph.unicode)
			else:
				lookup += "\t# could not create rule for %s\n" % glyphName

if not thisFont:
	Message(title="No Font Open", message="Please open a font first.", OKButton=None)
elif lookup:
	lineCount = lookup.splitlines().__len__()
	lookup = "\nlookup %s {\n%s\n} %s;\n\nscript hebr;\nlookup %s;\n" % (lookupTitle, lookup[:-1], lookupTitle, lookupTitle)
	reportMessage = createOTFeature(featureName="ccmp", featureCode=lookup, targetFont=thisFont, codeSig=lookupTitle.upper(), ignoreAutomatic=True)
	Message(title="Created Hebrew ccmp Lookup", message="%s with %i Hebrew presentation form substitutions." % (reportMessage, lineCount), OKButton="Cool")
else:
	Message(title="Nothing added to ccmp", message="No Hebrew presentation forms found in font.", OKButton="Too bad")
