# MenuTitle: Set Preferred Names (Name IDs 16 and 17) for Width Variants
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Sets Preferred Names custom parameters (Name IDs 16 and 17) for all instances, so that width variants will appear in separate menus in Adobe apps.
"""
from GlyphsApp import Glyphs

thisFont = Glyphs.font  # frontmost font
widthParticles = ("Narrow", "Condensed", "Compressed", "Extended", "Expanded", "Wide")
prefixParticles = ("Semi", "Extra", "Ultra")
widths = []
for widthParticle in widthParticles:
	widths.append(widthParticle)
	for prefixParticle in prefixParticles:
		widths.append("%s %s" % (prefixParticle, widthParticle))
		widths.append("%s%s" % (prefixParticle, widthParticle))
		widths.append("%s%s" % (prefixParticle, widthParticle.lower()))


def particleIsPartOfName(particle, instanceName):
	# particle is the full name:
	if instanceName.strip() == particle.strip():
		return True

	# PROBLEM: finding particle "Bold Italic" (with whitespace) should not find "SemiBold Italic"
	delim = "🧙"
	modifiedInstanceName = delim.join(instanceName.split())
	modifiedParticle = delim.join(particle.split())

	# particle in the MIDDLE of the name:
	searchTerm = "%s%s%s" % (delim, modifiedParticle, delim)
	if searchTerm in modifiedInstanceName:
		return True

	# particle at the END of the name:
	searchTerm = "%s%s" % (delim, modifiedParticle)
	if modifiedInstanceName.endswith(searchTerm):
		return True

	# particle at the BEGINNING of the name:
	searchTerm = "%s%s" % (modifiedParticle, delim)
	if modifiedInstanceName.startswith(searchTerm):
		return True

	return False


for thisInstance in thisFont.instances:
	print("Processing Instance:", thisInstance.name)
	familyName = thisFont.familyName
	if thisInstance.customParameters["familyName"]:
		familyName = thisInstance.customParameters["familyName"]

	widthVariant = None
	for width in widths:
		if particleIsPartOfName(width, thisInstance.name):
			widthVariant = width

	if widthVariant:
		preferredFamilyName = "%s %s" % (thisFont.familyName.strip(), widthVariant.strip())
		preferredStyleName = thisInstance.name.replace(widthVariant, "").strip()
		if not preferredStyleName:
			preferredStyleName = "Regular"

		if Glyphs.versionNumber >= 3:
			# GLYPHS 3
			thisInstance.preferredFamilyName = preferredFamilyName
			thisInstance.preferredSubfamilyName = preferredStyleName
		else:
			# GLYPHS 2
			thisInstance.customParameters["preferredFamilyName"] = preferredFamilyName
			thisInstance.customParameters["preferredSubfamilyName"] = preferredStyleName

		print("   preferredFamilyName:", preferredFamilyName)
		print("   preferredSubfamilyName:", preferredStyleName)
