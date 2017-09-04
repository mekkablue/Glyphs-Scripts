#MenuTitle: Set WWS Names (Name IDs 21 and 22)
# -*- coding: utf-8 -*-
__doc__="""
Sets WWS custom parameters (Name IDs 21 and 22) for all instances.
"""

thisFont = Glyphs.font # frontmost font
wwsStyles = ("Regular", "Bold", "Italic", "Bold Italic")

for thisInstance in thisFont.instances:
	print "Processing Instance:", thisInstance.name
	familyName = thisFont.familyName
	if thisInstance.customParameters["familyName"]:
		familyName = thisInstance.customParameters["familyName"]
	if not thisInstance.name in wwsStyles:
		wwsSubFamily = "Regular"
		for wwsStyle in ("Bold", "Italic", "Bold Italic"):
			if wwsStyle in thisInstance.name:
				wwsSubFamily = wwsStyle
		
		familyNameAddition = thisInstance.name.replace(wwsSubFamily,"").strip().replace("  ", " ")
		wwsFamilyName = familyName.strip() + " " + familyNameAddition.strip()
		thisInstance.customParameters["WWSFamilyName"] = wwsFamilyName
		thisInstance.customParameters["WWSSubfamilyName"] = wwsSubFamily
		print "   WWSFamilyName:", wwsFamilyName
		print "   WWSSubfamilyName:", wwsSubFamily
