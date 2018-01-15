#MenuTitle: Check Small Cap Consistency
# -*- coding: utf-8 -*-
__doc__="""
Checks some parameters (kerning groups, availability)
"""



thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master

smallCapSuffix = ".sc"
listOfSmallCaps = [ g for g in thisFont.glyphs if smallCapSuffix in g.name ]
listOfCaps = [ g for g in thisFont.glyphs if g.glyphInfo and g.glyphInfo.category == "Letter" and g.glyphInfo.subCategory == "Uppercase" ]

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

print "SMALLCAP REPORT"
print "Font: %s" % thisFont.familyName
print "Found %i small caps and %i caps." % ( len(listOfSmallCaps), len(listOfCaps) )

def makeCapName( smallCapName ):
	if smallCapName:
		if "_" in smallCapName[1:] and smallCapName[0] != "_":
			# ligatures:
			capName = "_".join( [ makeCapName(s) for s in smallCapName.split("_") ] )
		else:
			# single glyphs:
			capName = smallCapName.replace( smallCapSuffix, "" )
			if len(capName ) > 1:
				breakpoint = 1
				if capName.startswith("ae") or capName.startswith("oe"):
					breakpoint = 2
				capName = capName[:breakpoint].upper() + capName[breakpoint:]
			else:
				capName = capName.upper()
		return capName
	else:
		return None

def turnNoGroupIntoDash( groupName ):
	if not groupName:
		groupName = "--"
	return groupName

def isALetter( smallCapName ):
	if smallCapName:
		rootName = smallCapName[:smallCapName.find(".")]
		letterInfo = Glyphs.glyphInfoForName(rootName)
		if letterInfo:
			letterCategory = letterInfo.category
			if letterCategory == "Letter":
				return True
	return False

def smallcapVsCap( smallCap ):
	smallCapName = smallCap.name
	
	if isALetter(smallCapName):
		capName = makeCapName( smallCapName )
		cap = thisFont.glyphs[ capName ]
		if cap:
			SCleft = turnNoGroupIntoDash(smallCap.leftKerningGroup)
			SCright = turnNoGroupIntoDash(smallCap.rightKerningGroup)
			CAPleft = turnNoGroupIntoDash(cap.leftKerningGroup)
			CAPright = turnNoGroupIntoDash(cap.rightKerningGroup)

			if CAPleft != makeCapName(SCleft):
				print "-- %s: left group inconsistent (SC: %s, Cap: %s)" % ( smallCapName, SCleft, CAPleft )
			if CAPright != makeCapName(SCright):
				print "-- %s: right group inconsistent (SC: %s, Cap: %s)" % ( smallCapName, SCright, CAPright )
		else:
			print "-- no corresponding cap found for: %s" % smallCapName

def capVsSmallcap( cap ):
	capName = cap.name
	smallCapName = "%s%s" % ( capName.lower(), smallCapSuffix )
	smallCap = thisFont.glyphs[ smallCapName ]
	if not smallCap:
		print "-- no corresponding small cap found for: %s" % capName

print "\nChecking small caps..."
for smallcap in listOfSmallCaps:
	smallcapVsCap( smallcap )

print "\nChecking caps..."
for cap in listOfCaps:
	capVsSmallcap( cap )

