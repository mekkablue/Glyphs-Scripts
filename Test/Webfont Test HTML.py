#MenuTitle: Webfont Test HTML
# -*- coding: utf-8 -*-
__doc__="""
Create a Test HTML for the current font in the current Webfont Export folder.
"""

import GlyphsApp, os
fileFormats = ( "woff", "woff2", "eot" )

def saveFileInLocation( content="blabla", fileName="test.txt", filePath="~/Desktop" ):
	saveFileLocation = "%s/fonttest.html" % (filePath)
	saveFileLocation = saveFileLocation.replace( "//", "/" )
	f = open( saveFileLocation, 'w' )
	print "Exporting to:", f.name
	f.write( content )
	f.close()
	return True

def currentWebExportPath():
	exportPath = Glyphs.defaults["WebfontPluginExportPathManual"]
	if Glyphs.defaults["WebfontPluginUseExportPath"]:
		exportPath = Glyphs.defaults["WebfontPluginExportPath"]
	return exportPath

def replaceSet( text, setOfReplacements ):
	for thisReplacement in setOfReplacements:
		searchFor = thisReplacement[0]
		replaceWith = thisReplacement[1]
		text = text.replace( searchFor, replaceWith )
	return text

def allUnicodeEscapesOfFont( thisFont ):
	allUnicodes = ["&#x%s;" % g.unicode for g in thisFont.glyphs if g.unicode and g.export ]
	return " ".join( allUnicodes )

def activeInstances( thisFont, fileFormats=fileFormats ):
	familyName = thisFont.familyName
	activeInstances = [i for i in thisFont.instances if i.active == True]
	listOfInstanceInfo = []
	for fileFormat in fileFormats:
		for activeInstance in activeInstances:
			activeInstanceName = activeInstance.name
			baseName = "%s %s-%s" % ( fileFormat.upper(), familyName, activeInstanceName )
			fileName = "%s-%s.%s" % ( familyName.replace(" ",""), activeInstanceName.replace(" ",""), fileFormat )
			listOfInstanceInfo.append( (fileName, baseName, activeInstanceName) )
	return listOfInstanceInfo

def optionListForActiveInstances( instanceList ):
	returnString = ""
	for thisInstanceInfo in instanceList:
		returnString += '		<option value="%s">%s</option>\n' % ( thisInstanceInfo[0], thisInstanceInfo[1] )
		# <option value="fileName">baseName</option>
	
	return returnString

def fontFaces( instanceList ):
	returnString = ""
	for thisInstanceInfo in instanceList:
		fileName = thisInstanceInfo[0]
		nameOfTheFont = thisInstanceInfo[1]
		returnString += "\t\t@font-face { font-family: '%s'; src: url('%s'); }\n" % ( nameOfTheFont, fileName )
	
	return returnString

htmlContent = """<head>
	<meta http-equiv="Content-type" content="text/html; charset=utf-8">
	<title>familyName</title>
	<style type="text/css" media="screen">
		<!-- fontFaces -->
		
		body { font-family: "nameOfTheFont"; }
		p { padding: 5px; margin: 10px; }
		p#smallParagraph { font-size: small; }
		p#largeParagraph { font-size: x-large; }
		p#veryLargeParagraph { font-size: 100pt; }		
	</style>
	<script type="text/javascript">
		function updateParagraph() {
			var txt = document.getElementById('textInput');
			var p1 = document.getElementById('smallParagraph');
			var p2 = document.getElementById('largeParagraph');
			var p3 = document.getElementById('veryLargeParagraph');
			p1.textContent = txt.value;
			p2.textContent = txt.value;
			p3.textContent = txt.value;			
		}
		function changeFont() {
			var selector = document.getElementById('fontFamilySelector');
			var selected_index = selector.selectedIndex;
			var selected_option_text = selector.options[selected_index].text;
			document.getElementById('fontTestBody').style.fontFamily = selected_option_text;
		}
	</script>
</head>
<body id="fontTestBody">
	<select size="1" id="fontFamilySelector" name="fontFamilySelector" onchange="changeFont()">
		<!-- moreOptions -->
	</select>
	<input type="text" value="Type Text Here." id="textInput" onkeyup="updateParagraph()" size="80" />
	<p id="smallParagraph">ABCDEFGHIJKLMNOPQRSTUVWXYZ</p>
	<p id="largeParagraph">ABCDEFGHIJKLMNOPQRSTUVWXYZ</p>
	<p id="veryLargeParagraph">ABCDEFGHIJKLMNOPQRSTUVWXYZ</p>
</body>
"""

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

# Query app version:
GLYPHSAPPVERSION = NSBundle.bundleForClass_(GSMenu).infoDictionary().objectForKey_("CFBundleShortVersionString")
if GLYPHSAPPVERSION.startswith("2."):
	thisFont = Glyphs.font # frontmost font
	familyName = thisFont.familyName
	firstActiveInstance = [i for i in thisFont.instances if i.active == True][0]
	firstActiveInstanceName = firstActiveInstance.name
	activeFontInstances = activeInstances( thisFont )
	
	print "Preparing Test HTML for:"
	for thisFontInstanceInfo in activeFontInstances:
		print "  %s" % thisFontInstanceInfo[1]
	
	optionList = optionListForActiveInstances( activeFontInstances )
	fontFacesCSS = fontFaces( activeFontInstances )
	firstFileName =  activeFontInstances[0][0]
	firstFontName =  activeFontInstances[0][1]

	replacements = (
		( "familyName", familyName ),
		( "nameOfTheFont", firstFontName ),
		( "ABCDEFGHIJKLMNOPQRSTUVWXYZ", allUnicodeEscapesOfFont(thisFont) ),
		( "fileName", firstFileName ),
		( "		<!-- moreOptions -->\n", optionList ),
		( "		<!-- fontFaces -->\n", fontFacesCSS  )
	)

	htmlContent = replaceSet( htmlContent, replacements )
	
	# Write file to disk:
	exportPath = currentWebExportPath()
	if exportPath:
		if saveFileInLocation( content=htmlContent, fileName="fonttest.html", filePath=exportPath ):
			print "Successfully wrote file to disk."
			terminalCommand = 'cd %s; open .' % exportPath
			os.system( terminalCommand )
		else:
			print "Error writing file to disk."
	else:
		print "Could not determine export path. Have you exported any webfonts yet?"
else:
	print "This script requires Glyphs 2. Sorry."
	