#MenuTitle: Webfont Test HTML
# -*- coding: utf-8 -*-
__doc__="""
Create a Test HTML for the current font inside the current Webfont Export folder, or for the current Glyphs Project in the project’s export path.
"""

from os import system
fileFormats = ( "woff", "woff2", "eot" )

def saveFileInLocation( content="blabla", fileName="test.txt", filePath="~/Desktop" ):
	saveFileLocation = "%s/%s" % (filePath,fileName)
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

def getInstanceInfo( thisFont, activeInstance, fileFormat ):
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
	return fileName, menuName, activeInstanceName

def activeInstancesOfFont( thisFont, fileFormats=fileFormats ):
	activeInstances = [i for i in thisFont.instances if i.active]
	listOfInstanceInfo = []
	for fileFormat in fileFormats:
		for activeInstance in activeInstances:
			fileName, menuName, activeInstanceName = getInstanceInfo(thisFont, activeInstance, fileFormat)
			listOfInstanceInfo.append( (fileName, menuName, activeInstanceName) )
	return listOfInstanceInfo

def activeInstancesOfProject( thisProject, fileFormats=fileFormats ):
	thisFont = thisProject.font()
	activeInstances = [i for i in thisProject.instances() if i.active]
	listOfInstanceInfo = []
	for fileFormat in fileFormats:
		for activeInstance in activeInstances:
			fileName, menuName, activeInstanceName = getInstanceInfo(thisFont, activeInstance, fileFormat)
			listOfInstanceInfo.append( (fileName, menuName, activeInstanceName) )
	return listOfInstanceInfo

def optionListForInstances( instanceList ):
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

def featureListForFont( thisFont ):
	returnString = ""
	featureList = [f.name for f in thisFont.features if not f.name in ("ccmp", "aalt", "locl", "kern", "calt", "liga", "clig") and not f.disabled()]
	for f in featureList:
		returnString += """		<label><input type="checkbox" name="%s" value="%s" class="otFeature" onchange="updateFeatures()"><a href="http://stateofwebtype.com/#%s">%s</a></label>
""" % (f,f,f,f)
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
			// update paragraph text based on user input:
			var txt = document.getElementById('textInput');
			var paragraphs = ['p08','p09','p10','p11','p12','p13','p14','p15','p16','largeParagraph','veryLargeParagraph'];
			for (i = 0; i < paragraphs.length; i++) {
				paragraphID = paragraphs[i];
				var paragraph = document.getElementById(paragraphID);
				paragraph.textContent = txt.value;
			}
		}
		function updateFeatures() {
			// update features based on user input:
			// first, get feature on/off line:
			var cssCode = "";
			var codeLine = "";
			var checkboxes = document.getElementsByClassName("otFeature")
			for (i = 0; i < checkboxes.length; i++) {
				var checkbox = checkboxes[i];
				codeLine += '"'+checkbox.name+'" ';
				codeLine += checkbox.checked ? 'on, ' : 'off, ';
				if (checkbox.name=="kern") {
					cssCode += "font-kerning: "
					cssCode += checkbox.checked ? 'normal; ' : 'none; ';
				} else if (checkbox.name=="liga") {
					codeLine += '"clig" '
					codeLine += checkbox.checked ? 'on, ' : 'off, ';
					cssCode += "font-variant-ligatures: "
					cssCode += checkbox.checked ? 'common-ligatures contextual; ' : 'no-common-ligatures no-contextual; ';
				} else if (checkbox.name=="dlig") {
					cssCode += "font-variant-ligatures: "
					cssCode += checkbox.checked ? 'discretionary-ligatures; ' : 'no-discretionary-ligatures; ';
				} else if (checkbox.name=="hlig") {
					cssCode += "font-variant-ligatures: "
					cssCode += checkbox.checked ? 'historical-ligatures; ' : 'no-historical-ligatures; ';
				}
			}
			codeLine = codeLine.slice(0, -2)
			
			// then, apply line for every browser:
			var prefixes = ["","-moz-","-webkit-","-ms-","-o-",];
			var suffix = "font-feature-settings: "
			for (i = 0; i < prefixes.length; i++) {
				var prefix = prefixes[i];
				cssCode += prefix
				cssCode += suffix
				cssCode += codeLine
				cssCode += "; "
			}
			
			document.getElementById('fontTestBody').style.cssText = cssCode;
			document.getElementById('featureLine').innerHTML = cssCode.replace(/;/g,";<br/>");
			changeFont();
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
	<input type="text" value="Type Text Here." id="textInput" onclick="this.select();" onkeyup="updateParagraph()" size="80" />
	<p style="font-size:small">
		<a href="javascript:setCharset();">Charset</a>
		<a href="javascript:setLat1();">Lat1</a>
		&emsp;
		<a href="http://stateofwebtype.com/#eot">eot?</a>
		<a href="http://stateofwebtype.com/#woff">woff?</a>
		<a href="http://stateofwebtype.com/#woff2">woff2?</a>
		&emsp;
		<a href="http://stateofwebtype.com/#font-feature-settings">Features</a>:
		<label><input type="checkbox" name="kern" value="kern" class="otFeature" onchange="updateFeatures()" checked><a href="http://stateofwebtype.com/#kern">kern</a></label>
		<label><input type="checkbox" name="liga" value="liga" class="otFeature" onchange="updateFeatures()" checked><a href="http://stateofwebtype.com/#liga">liga/clig</a></label>
		<label><input type="checkbox" name="calt" value="calt" class="otFeature" onchange="updateFeatures()" checked><a href="http://stateofwebtype.com/#calt">calt</a></label>
		<!-- moreFeatures -->
		<label><input type="checkbox" name="show" value="show" onchange="updateFeatures();document.getElementById('featureLine').style.display=this.checked?'':'none'">Show CSS</label>
	</p>
	<p id="featureLine" style="font-size:x-small;display:none;">font-feature-settings: "kern" on, "liga" on, "calt" on;</p>
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
appVersionHighEnough = not GLYPHSAPPVERSION.startswith("1.")

if appVersionHighEnough:
	firstDoc = Glyphs.orderedDocuments()[0]
	if firstDoc.isKindOfClass_(GSProjectDocument):
		thisFont = firstDoc.font() # frontmost project file
		firstActiveInstance = [i for i in firstDoc.instances() if i.active][0]
		activeFontInstances = activeInstancesOfProject( firstDoc )
		exportPath = firstDoc.exportPath()
	else:
		thisFont = Glyphs.font # frontmost font
		firstActiveInstance = [i for i in thisFont.instances if i.active][0]
		activeFontInstances = activeInstancesOfFont( thisFont )
		exportPath = currentWebExportPath()
		
		
	familyName = thisFont.familyName
	
	print "Preparing Test HTML for:"
	for thisFontInstanceInfo in activeFontInstances:
		print "  %s" % thisFontInstanceInfo[1]
	
	optionList = optionListForInstances( activeFontInstances )
	fontFacesCSS = fontFaces( activeFontInstances )
	firstFileName =  activeFontInstances[0][0]
	firstFontName =  activeFontInstances[0][1]

	replacements = (
		( "familyName", familyName ),
		( "nameOfTheFont", firstFontName ),
		( "ABCDEFGHIJKLMNOPQRSTUVWXYZ", allUnicodeEscapesOfFont(thisFont) ),
		( "fileName", firstFileName ),
		( "		<!-- moreOptions -->\n", optionList ),
		( "		<!-- moreFeatures -->\n", featureListForFont(thisFont) ),
		( "		<!-- fontFaces -->\n", fontFacesCSS  )
	)

	htmlContent = replaceSet( htmlContent, replacements )
	
	# Write file to disk:
	if exportPath:
		if saveFileInLocation( content=htmlContent, fileName="fonttest.html", filePath=exportPath ):
			print "Successfully wrote file to disk."
			terminalCommand = 'cd "%s"; open .' % exportPath
			system( terminalCommand )
		else:
			print "Error writing file to disk."
	else:
		Message( 
			"Webfont Test HTML Error",
			"Could not determine export path. Have you exported any webfonts yet?",
			OKButton=None
		)
else:
	print "This script requires Glyphs 2. Sorry."
