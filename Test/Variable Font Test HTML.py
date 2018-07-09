#MenuTitle: Variable Font Test HTML
# -*- coding: utf-8 -*-
__doc__="""
Create a Test HTML for the current font inside the current Variation Font Export folder.
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

def currentOTVarExportPath():
	exportPath = Glyphs.defaults["GXExportPathManual"]
	if Glyphs.defaults["GXPluginUseExportPath"]:
		exportPath = Glyphs.defaults["GXExportPath"]
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

def featureListForFont( thisFont ):
	returnString = ""
	featureList = [f.name for f in thisFont.features if not f.name in ("ccmp", "aalt", "locl", "kern", "calt", "liga", "clig") and not f.disabled()]
	for f in featureList:
		returnString += """		<label><input type="checkbox" name="%s" value="%s" class="otFeature" onchange="updateFeatures()"><a href="http://stateofwebtype.com/#%s">%s</a></label>
""" % (f,f,f,f)
	return returnString

def allOTVarSliders(thisFont):
	sliderValues = {}
	for i, thisMaster in enumerate(thisFont.masters):
		try:
			sliderValues[i] = (
				thisMaster.weightValue,
				thisMaster.widthValue,
				thisMaster.customValue,
				thisMaster.customValue1(),
				thisMaster.customValue2(),
				thisMaster.customValue3(),
			)
			warningMessage()
		except:
			sliderValues[i] = (
				thisMaster.weightValue,
				thisMaster.widthValue,
				thisMaster.customValue,
				thisMaster.customValue1,
				thisMaster.customValue2,
				thisMaster.customValue3,
			)
			
	
	axisDict = {}
	for i, axis in enumerate(thisFont.axes):
		axisName = axis["Name"]
		axisTag = axis["Tag"]
		axisDict[axisName] = { "tag": axisTag, "min": sliderValues[0][i], "max": sliderValues[0][i] }
		print axisDict
		for j, thisMaster in enumerate(thisFont.masters):
			masterValue = sliderValues[j][i]
			if masterValue < axisDict[axisName]["min"]:
				axisDict[axisName]["min"] = masterValue
			elif masterValue > axisDict[axisName]["max"]:
				axisDict[axisName]["max"] = masterValue
		
	if Font.customParameters["Virtual Master"]:
		for axis in Font.customParameters["Virtual Master"]:
			name = axis["Axis"]
			if axis["Location"] < axisDict[name]["min"]:
				axisDict[name]["min"] = axis["Location"]
			if axis["Location"] > axisDict[name]["max"]:
				axisDict[name]["max"] = axis["Location"]
	
	minValues, maxValues = {}, {}
	for axis in axisDict:
		tag = axisDict[axis]["tag"]
		minValues[tag] = axisDict[axis]["min"]
		maxValues[tag] = axisDict[axis]["max"]
	
	html = ""
	for i in range( len( thisFont.axes )):
		defaultValue = sliderValues[0][i]
		axisTag = str(thisFont.axes[i]["Tag"])
		print axisDict
		html += "\t\t\t<div class='labeldiv'><label class='sliderlabel' id='label_%s'>%s</label><input type='range' min='%i' max='%i' value='%i' class='slider' id='%s' oninput='updateSlider();'></div>\n" % (
			axisTag, axisTag, 
			minValues[axisTag], maxValues[axisTag], defaultValue,
			axisTag
		)
		
	return html

def warningMessage():
	Message(
		title="Out of Date Warning", 
		message="It appears that you are not running the latest version of Glyphs. Please enable Cutting Edge Versions and Automatic Version Checks in Preferences > Updates, and update to the latest beta.",
		OKButton=None
		)
	
def defaultVariationCSS(thisFont):
	firstMaster = thisFont.masters[0]
	try:
		axisValues = (
			firstMaster.weightValue,
			firstMaster.widthValue,
			firstMaster.customValue,
			firstMaster.customValue1(),
			firstMaster.customValue2(),
			firstMaster.customValue3(),
		)
		warningMessage()
	except:
		axisValues = (
			firstMaster.weightValue,
			firstMaster.widthValue,
			firstMaster.customValue,
			firstMaster.customValue1,
			firstMaster.customValue2,
			firstMaster.customValue3,
		)
		
	defaultValues = []
	for i, axis in enumerate(thisFont.axes):
		tag = axis["Tag"]
		value = axisValues[i]
		cssValue = '"%s" %i' % (tag, value)
		defaultValues.append(cssValue)
		
	return ", ".join(defaultValues)
	


htmlContent = """
<html>
	<meta http-equiv="Content-type" content="text/html; charset=utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=9">
	<head>
		<title>OTVar Test: ###fontFamilyNameWithSpaces###</title>
		<style>
			@font-face { 
				font-family: "###fontFamilyName###";
				src: url(###fontFamilyName###GX.ttf);
			}
			p {
				z-index: 0;
				position: relative;
				margin: 0px;
				padding: 5px;
				padding-top: 0.2em;
				line-height: 1em;
				font: 100px "###fontFamilyName###";
				font-feature-settings: "kern" on, "liga" on, "calt" on;
				-moz-font-feature-settings: "kern" on, "liga" on, "calt" on;
				-webkit-font-feature-settings: "kern" on, "liga" on, "calt" on;
				-ms-font-feature-settings: "kern" on, "liga" on, "calt" on;
				-o-font-feature-settings: "kern" on, "liga" on, "calt" on;
				font-variation-settings: ###variationSettings###;
			}
			#textInput{
				color: #777;
				background-color: #eee;
				border-radius: 5px;   
				background: #eee;
				border: none;
				height: 2em;
				padding: 0.5em;
				margin: 5px;
				width: 97%;
			}
			.labeldiv {
				width: 48%;
				display: inline-block;
			}
 			label {
				z-index: 2;
				position: absolute;
				pointer-events: none;
				width: 100%;
				height: 2em;
				margin: 0;
				padding: 1em;
				vertical-align: text-top;
				font: x-small sans-serif;
				color: 000;
				opacity: 0.5;
			}
			.slider {
				z-index: 1;
				position: relative;
				-webkit-appearance: none;
				-moz-appearance: none;
				appearance: none;
				width: 100%;
				height: 2em;
				border-radius: 5px;   
				background: #eee;
				padding: 0px;
				margin: 5px;
			}
			.slider::-webkit-slider-thumb {
				z-index: 3;
				position: relative;
				-webkit-appearance: none;
				-moz-appearance: none;
				appearance: none;
				width: 16px;
				height: 2em;
				border-radius: 5px; 
				background: #777;
				cursor: auto;
			}
			a {
				color: #333;
			}
		</style>
		<script>
			function updateParagraph() {
				// update paragraph text based on user input:
				var userinput = document.getElementById("textInput");
				var paragraph = document.getElementById("text");
				paragraph.textContent = userinput.value;
			}
		
			function updateSlider() {
				var body = document.getElementById("text");
				var sliders = document.getElementsByClassName("slider")
				var bodystyle = "";
				var settingtext = "";
				for (var i = 0; i < sliders.length; i++) {
					var sliderID = sliders[i].id;
					var sliderValue = sliders[i].value;
					var label = document.getElementById("label_"+sliderID);
					label.textContent = ""+sliderID+": "+sliderValue
					if (sliderID == "fontsize") {
						// Text Size Slider
						bodystyle += "font-size: "+sliderValue+"px;"
						label.textContent += "px"
					} else if (sliderID == "lineheight") {
						// Line Height Slider
						bodystyle += "line-height: "+sliderValue/100.0+"em;"
						label.textContent += "%"
					} else {
						// OTVar Slider
						if (settingtext != "") { settingtext += ", " }
						settingtext += '"' + sliderID + '" ' + sliderValue
					}
				}
				bodystyle += "font-variation-settings: "+settingtext+";"
				body.setAttribute("style", bodystyle);
			}
		</script>
	</head>
	<body onload="updateSlider();">
		<input type="text" value="Type Text Here." id="textInput" onkeyup="updateParagraph();" onclick="this.select();" />
		<div>
			<div class="labeldiv"><label class="sliderlabel" id="label_fontsize">fontsize</label><input type="range" min="10" max="200" value="50" class="slider" id="fontsize" oninput="updateSlider();"></div>
			<div class="labeldiv"><label class="sliderlabel" id="label_lineheight">lineheight</label><input type="range" min="30" max="300" value="100" class="slider" id="lineheight" oninput="updateSlider();"></div>
###sliders###		</div>
		<p id="text">The Quick Brown Fox Jumps Over the Lazy Dog.</p>
		<p style="color: #ccc; font: x-small sans-serif;">Not working? Please use the <a href="https://www.google.com/chrome/">latest version of Chrome</a>.<br/>Note: script is currently incompatible with <em>Axis Location</em> parameters in <em>File > Font Info > Masters.</em></p>
	</body>
</html>
"""

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

# Query app version:
GLYPHSAPPVERSION = NSBundle.bundleForClass_(GSMenu).infoDictionary().objectForKey_("CFBundleShortVersionString")
appVersionHighEnough = not GLYPHSAPPVERSION.startswith("1.")

if appVersionHighEnough:
	firstDoc = Glyphs.orderedDocuments()[0]
	thisFont = Glyphs.font # frontmost font
	exportPath = currentOTVarExportPath()
	familyName = thisFont.familyName

	print "Preparing Test HTML for: %s" % familyName
	
	replacements = (
		( "###fontFamilyNameWithSpaces###", familyName ),
		( "###fontFamilyName###", familyName.replace(" ","") ),
		( "The Quick Brown Fox Jumps Over the Lazy Dog.", allUnicodeEscapesOfFont(thisFont) ),
		( "###sliders###", allOTVarSliders(thisFont) ),
		( "###variationSettings###", defaultVariationCSS(thisFont) ), 
		# ( "		<!-- moreOptions -->\n", optionList ),
		# ( "		<!-- moreFeatures -->\n", featureListForFont(thisFont) ),
		# ( "		<!-- fontFaces -->\n", fontFacesCSS  )
	)

	htmlContent = replaceSet( htmlContent, replacements )
	
	# Write file to disk:
	if exportPath:
		if saveFileInLocation( content=htmlContent, fileName="%s fonttest.html" % familyName, filePath=exportPath ):
			print "Successfully wrote file to disk."
			terminalCommand = 'cd "%s"; open .' % exportPath
			system( terminalCommand )
		else:
			print "Error writing file to disk."
	else:
		Message( 
			title="OTVar Test HTML Error",
			message="Could not determine export path. Have you exported any webfonts yet?",
			OKButton=None
		)
else:
	print "This script requires Glyphs 2.5. Sorry."
