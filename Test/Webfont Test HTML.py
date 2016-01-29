#MenuTitle: Webfont Test HTML
# -*- coding: utf-8 -*-
__doc__="""
Create a Test HTML for the current font in the current Webfont Export folder.
"""

from Foundation import *
from AppKit import *
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
	activeInstances = [i for i in thisFont.instances if i.active == True]
	listOfInstanceInfo = []
	for fileFormat in fileFormats:
		for activeInstance in activeInstances:
			# Determine Family Name
			familyName = thisFont.familyName
			individualFamilyName = activeInstance.customParameters["familyName"]
			if individualFamilyName != None:
				familyName = individualFamilyName
			
			# Determine Style Name
			activeInstanceName = activeInstance.name
			
			# Determine font and file names for CSS
			menuName = "%s %s-%s" % ( fileFormat.upper(), familyName, activeInstanceName )
			
			firstPartOfFileName = activeInstance.customParameters["fileName"]
			if not firstPartOfFileName:
				firstPartOfFileName = "%s-%s" % ( familyName.replace(" ",""), activeInstanceName.replace(" ","") )
				
			fileName = "%s.%s" % ( firstPartOfFileName, fileFormat )
			
			listOfInstanceInfo.append( (fileName, menuName, activeInstanceName) )
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
	<meta http-equiv="X-UA-Compatible" content="IE=9">
	<title>familyName</title>
	<style type="text/css" media="screen">
		<!-- fontFaces -->
		
		body { 
			font-family: "nameOfTheFont"; 
			font-feature-settings: "kern" on, "liga" on, "calt" on;
			-moz-font-feature-settings: "kern" on, "liga" on, "calt" on;
			-webkit-font-feature-settings: "kern" on, "liga" on, "calt" on;
			-ms-font-feature-settings: "kern" on, "liga" on, "calt" on;
			-o-font-feature-settings: "kern" on, "liga" on, "calt" on;
		}
		p { padding: 5px; margin: 10px; }
		p#p08 { font-size: 08pt; }
		p#p09 { font-size: 09pt; }
		p#p10 { font-size: 10pt; }
		p#p11 { font-size: 11pt; }
		p#p12 { font-size: 12pt; }
		p#p13 { font-size: 13pt; }
		p#p14 { font-size: 14pt; }
		p#p15 { font-size: 15pt; }
		p#p16 { font-size: 16pt; }
		p#largeParagraph { font-size: 32pt; }
		p#veryLargeParagraph { font-size: 100pt; }		
	</style>
	<script type="text/javascript">
		function updateParagraph() {
			var txt = document.getElementById('textInput');
			
			var p08 = document.getElementById('p08');
			var p09 = document.getElementById('p09');
			var p10 = document.getElementById('p10');
			var p11 = document.getElementById('p11');
			var p12 = document.getElementById('p12');
			var p13 = document.getElementById('p13');
			var p14 = document.getElementById('p14');
			var p15 = document.getElementById('p15');
			var p16 = document.getElementById('p16');
			var pLarge = document.getElementById('largeParagraph');
			var pVeryLarge = document.getElementById('veryLargeParagraph');
			
			p08.textContent = txt.value;
			p09.textContent = txt.value;
			p10.textContent = txt.value;
			p11.textContent = txt.value;
			p12.textContent = txt.value;
			p13.textContent = txt.value;
			p14.textContent = txt.value;
			p15.textContent = txt.value;
			p16.textContent = txt.value;
			pLarge.textContent = txt.value;
			pVeryLarge.textContent = txt.value;
		}
		function changeFont() {
			var selector = document.getElementById('fontFamilySelector');
			var selected_index = selector.selectedIndex;
			var selected_option_text = selector.options[selected_index].text;
			document.getElementById('fontTestBody').style.fontFamily = selected_option_text;
		}
		function setDefaultText(defaultText) {
			document.getElementById('textInput').value = decodeEntities(defaultText);
			updateParagraph();
		}
		function setLat1() {
			var lat1 = "abcdefghijklm nopqrstuvwxyz ABCDEFGHIJKLM NOPQRSTUVWXYZ &Agrave;&Aacute;&Acirc;&Atilde;&Auml;&Aring;&AElig;&Ccedil;&Egrave;&Eacute;&Ecirc;&Euml;&Igrave;&Iacute;&Icirc;&Iuml;&ETH;&Ntilde;&Ograve;&Oacute;&Ocirc;&Otilde;&Ouml;&Oslash;&OElig;&THORN;&Ugrave;&Uacute;&Ucirc;&Uuml;&Yacute;&Yuml; &agrave;&aacute;&acirc;&atilde;&auml;&aring;&aelig;&ccedil;&egrave;&eacute;&ecirc;&euml;&igrave;&iacute;&icirc;&iuml;&eth;&ntilde;&ograve;&oacute;&ocirc;&otilde;&ouml;&oslash;&oelig;&thorn;&szlig;&ugrave;&uacute;&ucirc;&uuml;&yacute;&yuml; .,:;&middot;&hellip;&iquest;?&iexcl;!&laquo;&raquo;&lsaquo;&rsaquo; /|&brvbar;\\()[]{}_-&ndash;&mdash;&sbquo;&bdquo;&lsquo;&rsquo;&ldquo;&rdquo;&quot;&#x27; #&amp;&sect;@&bull;&shy;*&dagger;&Dagger;&para; +&times;&divide;&plusmn;=&lt;&gt;&not;&mu; ^~&acute;`&circ;&macr;&tilde;&uml;&cedil; &yen;&euro;&pound;$&cent;&curren;&fnof; &trade;&reg;&copy; 1234567890 &ordf;&ordm;&deg;%&permil; &sup1;&sup2;&sup3;&frac14;&frac12;&frac34;";
			return setDefaultText(lat1);
		}
		function setCharset() {
			var completeCharSet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
			setDefaultText(completeCharSet);
		}
		function decodeEntities(string){
			var elem = document.createElement('div');
			elem.innerHTML = string;
			return elem.textContent;
		}
	</script>
</head>
<body id="fontTestBody">
	<select size="1" id="fontFamilySelector" name="fontFamilySelector" onchange="changeFont()">
		<!-- moreOptions -->
	</select>
	<input type="text" value="Type Text Here." id="textInput" onkeyup="updateParagraph()" size="80" />
	<p>
		<a href="javascript:setCharset();">Charset</a>
		<a href="javascript:setLat1();">Lat1</a>
		<a href="http://stateofwebtype.com/#eot">eot?</a>
		<a href="http://stateofwebtype.com/#woff">woff?</a>
		<a href="http://stateofwebtype.com/#woff2">woff2?</a>
	</p>
	<p id="p08">08pt ABCDEFGHIJKLMNOPQRSTUVWXYZ</p>
	<p id="p09">09pt ABCDEFGHIJKLMNOPQRSTUVWXYZ</p>
	<p id="p10">10pt ABCDEFGHIJKLMNOPQRSTUVWXYZ</p>
	<p id="p11">11pt ABCDEFGHIJKLMNOPQRSTUVWXYZ</p>
	<p id="p12">12pt ABCDEFGHIJKLMNOPQRSTUVWXYZ</p>
	<p id="p13">13pt ABCDEFGHIJKLMNOPQRSTUVWXYZ</p>
	<p id="p14">14pt ABCDEFGHIJKLMNOPQRSTUVWXYZ</p>
	<p id="p15">15pt ABCDEFGHIJKLMNOPQRSTUVWXYZ</p>
	<p id="p16">16pt ABCDEFGHIJKLMNOPQRSTUVWXYZ</p>
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
			terminalCommand = 'cd "%s"; open .' % exportPath
			os.system( terminalCommand )
		else:
			print "Error writing file to disk."
	else:
		print "Could not determine export path. Have you exported any webfonts yet?"
else:
	print "This script requires Glyphs 2. Sorry."
