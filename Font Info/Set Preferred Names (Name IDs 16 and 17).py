#MenuTitle: Set Preferred Names (Name IDs 16 and 17) for Width Variants
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Sets Preferred Names custom parameters (Name IDs 16 and 17) for all instances, so that width variants will appear in separate menus in Adobe apps.
"""

thisFont = Glyphs.font # frontmost font
widths = (
	"Narrow", "Seminarrow", "Semi Narrow", "Extranarrow", "Extra Narrow", "Ultranarrow", "Ultra Narrow", 
	"Condensed", "Semicondensed", "Semi Condensed", "Extracondensed", "Extra Condensed", "Ultracondensed", "Ultra Condensed", 
	"Compressed", "Semicompressed", "Semi Compressed", "Extracompressed", "Extra Compressed", "Ultracompressed", "Ultra Compressed", 
	"Extended", "Semiextended", "Semi Extended", "Extraextended", "Extra Extended", "Ultraextended", "Ultra Extended", 
	"Expanded", "Semiexpanded", "Semi Expanded", "Extraexpanded", "Extra Expanded", "Ultraexpanded", "Ultra Expanded", 
	"Wide", "Semiwide", "Semi Wide", "Extrawide", "Extra Wide", "Ultrawide", "Ultra Wide", 
)

for thisInstance in thisFont.instances:
	print("Processing Instance:", thisInstance.name)
	familyName = thisFont.familyName
	if thisInstance.customParameters["familyName"]:
		familyName = thisInstance.customParameters["familyName"]
	
	widthVariant = None
	for width in widths:
		if width in thisInstance.name:
			widthVariant = width
		elif " " in width:
			width = width.replace(" ","")
			if width in thisInstance.name:
				widthVariant = width
	
	if widthVariant:
		preferredFamilyName = "%s %s" % ( thisFont.familyName.strip(), widthVariant.strip() )
		preferredStyleName = thisInstance.name.replace(widthVariant,"").strip()
		if not preferredStyleName:
			preferredStyleName = "Regular"
	
		thisInstance.customParameters["preferredFamilyName"] = preferredFamilyName
		thisInstance.customParameters["preferredSubfamilyName"] = preferredStyleName
		print("   preferredFamilyName:", preferredFamilyName)
		print("   preferredSubfamilyName:", preferredStyleName)
