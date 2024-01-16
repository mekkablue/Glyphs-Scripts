# MenuTitle: Build rtlm Alternates
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Creates horizontally mirrored composite copies for selected glyphs, and updates the rtlm OpenType feature. Auto-aligns the components, also adds metrics keys that kick in in case you decompose.
"""

from AppKit import NSAffineTransform
from GlyphsApp import Glyphs, GSGlyph, GSComponent, GSFeature


def flip():
	flipTransform = NSAffineTransform.transform()
	flipTransform.scaleXBy_yBy_(-1, 1)
	return flipTransform


def okToAddToRTLM(glyph):
	# https://docs.microsoft.com/en-us/typography/opentype/spec/ompl
	rootName = glyph.name
	if "." in rootName:
		rootName = rootName.split(".")[0]
	info = Glyphs.glyphInfoForName(rootName)
	omplUnicodes = (
		"0028", "0029", "003C", "003E", "005B", "005D", "007B", "007D", "00AB", "00BB", "0F3A", "0F3B", "0F3C", "0F3D", "169B", "169C", "2039", "203A", "2045", "2046", "207D",
		"207E", "208D", "208E", "2208", "2209", "220A", "220B", "220C", "220D", "2215", "223C", "223D", "2243", "2252", "2253", "2254", "2255", "2264", "2265", "2266", "2267",
		"2268", "2269", "226A", "226B", "226E", "226F", "2270", "2271", "2272", "2273", "2274", "2275", "2276", "2277", "2278", "2279", "227A", "227B", "227C", "227D", "227E",
		"227F", "2280", "2281", "2282", "2283", "2284", "2285", "2286", "2287", "2288", "2289", "228A", "228B", "228F", "2290", "2291", "2292", "2298", "22A2", "22A3", "22A6",
		"22A8", "22A9", "22AB", "22B0", "22B1", "22B2", "22B3", "22B4", "22B5", "22B6", "22B7", "22C9", "22CA", "22CB", "22CC", "22CD", "22D0", "22D1", "22D6", "22D7", "22D8",
		"22D9", "22DA", "22DB", "22DC", "22DD", "22DE", "22DF", "22E0", "22E1", "22E2", "22E3", "22E4", "22E5", "22E6", "22E7", "22E8", "22E9", "22EA", "22EB", "22EC", "22ED",
		"22F0", "22F1", "22F2", "22F3", "22F4", "22F6", "22F7", "22FA", "22FB", "22FC", "22FD", "22FE", "2308", "2309", "230A", "230B", "2329", "232A", "2768", "2769", "276A",
		"276B", "276C", "276D", "276E", "276F", "2770", "2771", "2772", "2773", "2774", "2775", "27C3", "27C4", "27C5", "27C6", "27C8", "27C9", "27D5", "27D6", "27DD", "27DE",
		"27E2", "27E3", "27E4", "27E5", "27E6", "27E7", "27E8", "27E9", "27EA", "27EB", "27EC", "27ED", "27EE", "27EF", "2983", "2984", "2985", "2986", "2987", "2988", "2989",
		"298A", "298B", "298C", "298D", "298E", "298F", "2990", "2991", "2992", "2993", "2994", "2995", "2996", "2997", "2998", "29B8", "29C0", "29C1", "29C4", "29C5", "29CF",
		"29D0", "29D1", "29D2", "29D4", "29D5", "29D8", "29D9", "29DA", "29DB", "29F5", "29F8", "29F9", "29FC", "29FD", "2A2B", "2A2C", "2A2D", "2A2E", "2A34", "2A35", "2A3C",
		"2A3D", "2A64", "2A65", "2A79", "2A7A", "2A7D", "2A7E", "2A7F", "2A80", "2A81", "2A82", "2A83", "2A84", "2A8B", "2A8C", "2A91", "2A92", "2A93", "2A94", "2A95", "2A96",
		"2A97", "2A98", "2A99", "2A9A", "2A9B", "2A9C", "2AA1", "2AA2", "2AA6", "2AA7", "2AA8", "2AA9", "2AAA", "2AAB", "2AAC", "2AAD", "2AAF", "2AB0", "2AB3", "2AB4", "2ABB",
		"2ABC", "2ABD", "2ABE", "2ABF", "2AC0", "2AC1", "2AC2", "2AC3", "2AC4", "2AC5", "2AC6", "2ACD", "2ACE", "2ACF", "2AD0", "2AD1", "2AD2", "2AD3", "2AD4", "2AD5", "2AD6",
		"2ADE", "2AE3", "2AE4", "2AE5", "2AEC", "2AED", "2AF7", "2AF8", "2AF9", "2AFA", "2E02", "2E03", "2E04", "2E05", "2E09", "2E0A", "2E0C", "2E0D", "2E1C", "2E1D", "2E20",
		"2E21", "2E22", "2E23", "2E24", "2E25", "2E26", "2E27", "2E28", "2E29", "3008", "3009", "300A", "300B", "300C", "300D", "300E", "300F", "3010", "3011", "3014", "3015",
		"3016", "3017", "3018", "3019", "301A", "301B", "FE59", "FE5A", "FE5B", "FE5C", "FE5D", "FE5E", "FE64", "FE65", "FF08", "FF09", "FF1C", "FF1E", "FF3B", "FF3D", "FF5B",
		"FF5D", "FF5F", "FF60", "FF62", "FF63"
	)
	if info.unicode and info.unicode in omplUnicodes:
		return False
	return True


thisFont = Glyphs.font  # frontmost font
selectedLayers = thisFont.selectedLayers  # active layers of selected glyphs
flipTransform = flip()
Glyphs.clearLog()  # clears log in Macro window
print("Building rtlm for: %s\n" % thisFont.familyName)

thisFont.disableUpdateInterface()  # suppresses UI updates in Font View

try:
	# adding composite glyphs:
	glyphs = [layer.parent for layer in selectedLayers]  # if not ".rtlm" in l.parent.name]
	count = 0
	for glyph in glyphs:
		glyphName = glyph.name
		if ".rtlm" in glyph.name:
			print("⚠️ %s: already has rtlm suffix, unchanged." % glyphName)
			continue
		elif not okToAddToRTLM(glyph):
			print("⚠️ %s is part of OMPL, ignored." % glyphName)
			continue
		else:
			rtlmName = "%s.rtlm" % glyphName
			rtlmGlyph = GSGlyph(rtlmName)
			if thisFont.glyphs[rtlmName]:
				print("⚠️ %s: already in font, ignored.")
			else:
				count += 1
				thisFont.glyphs.append(rtlmGlyph)

				for rtlmLayer in rtlmGlyph.layers.values():
					component = GSComponent(glyphName)
					if Glyphs.versionNumber >= 3:
						rtlmLayer.shapes.append(component)
					else:
						rtlmLayer.components.append(component)  # type: ignore
					rtlmLayer.transform_checkForSelection_doComponents_(flipTransform, False, True)
					component.automaticAlignment = True

				print("🙌 %s → %s" % (glyphName, rtlmName))

				# metrics (useful in case of decomposition):
				rtlmMetricsKey = "=|%s" % glyphName
				rtlmGlyph.leftMetricsKey = rtlmMetricsKey
				rtlmGlyph.rightMetricsKey = rtlmMetricsKey

	# OT Feature:
	if count > 0:
		print("🔠 Updating rtlm OT feature...")
		if "rtlm" not in [f.name for f in thisFont.features]:
			rtlmFeature = GSFeature()
			rtlmFeature.name = "rtlm"
			thisFont.features.append(rtlmFeature)
		else:
			rtlmFeature = thisFont.features["rtlm"]

		# update:
		rtlmFeature.automatic = True
		rtlmFeature.update()
	else:
		print("\n❌ No rtlm glyphs added, features left unchanged.")

	print("\n✅ Done. Added %i .rtlm glyphs." % count)

	# Floating notification:
	Glyphs.showNotification(
		"rtlm for %s" % (thisFont.familyName),
		"Added %i glyph%s. Details in Macro window." % (
			count,
			"" if count == 1 else "s",
		),
	)

except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Create rtlm Alternates\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface()  # re-enables UI updates in Font View
