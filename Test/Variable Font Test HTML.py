#MenuTitle: Variable Font Test HTML
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Create a Test HTML for the current font inside the current Variation Font Export folder.
"""

from os import system
from AppKit import NSClassFromString, NSBundle

def saveFileInLocation( content="Sorry, no content generated.", fileName="test.html", filePath="~/Desktop" ):
	saveFileLocation = "%s/%s" % (filePath,fileName)
	saveFileLocation = saveFileLocation.replace( "//", "/" )
	f = open( saveFileLocation, 'w' )
	print("Exporting to: %s" % f.name)
	f.write( content.encode("ascii", errors="xmlcharrefreplace") )
	f.close()
	return True

def currentOTVarExportPath():
	exportPath = Glyphs.defaults["GXExportPathManual"]
	if Glyphs.defaults["GXPluginUseExportPath"]:
		exportPath = Glyphs.defaults["GXExportPath"]
	return exportPath

def otVarFamilyName(thisFont):
	if thisFont.customParameters["Variable Font Family Name"]:
		return thisFont.customParameters["Variable Font Family Name"]
	else:
		return thisFont.familyName

def otVarFileName(thisFont):
	if thisFont.customParameters["Variable Font File Name"] or thisFont.customParameters["variableFileName"]:
		fileName = thisFont.customParameters["Variable Font File Name"]
		if not fileName:
			fileName = thisFont.customParameters["variableFileName"]
		return "%s.ttf" % fileName
	else:
		familyName = otVarFamilyName(thisFont)
		fileName = "%sGX.ttf" % familyName
		return fileName.replace(" ","")

def replaceSet( text, setOfReplacements ):
	for thisReplacement in setOfReplacements:
		searchFor = thisReplacement[0]
		replaceWith = thisReplacement[1]
		text = text.replace( searchFor, replaceWith )
	return text

def generateAxisDict(thisFont):
	# see if there are Axis Location parameters in use:
	fontHasAxisLocationParameters = True
	for thisMaster in thisFont.masters:
		if not thisMaster.customParameters["Axis Location"]:
			fontHasAxisLocationParameters = False
	
	# create and return the axisDict:
	if fontHasAxisLocationParameters:
		return axisDictForFontWithAxisLocationParameters(thisFont)
	else:
		return axisDictForFontWithoutAxisLocationParameters(thisFont)

def axisDictForFontWithoutAxisLocationParameters(thisFont):
	sliderValues = {}
	for i, thisMaster in enumerate(thisFont.masters):
		sliderValues[i] = axisValuesForMaster(thisMaster)
	
	axisDict = {}
	for i, axis in enumerate(thisFont.axes):
		try:
			# Glyphs 2:
			axisName, axisTag = axis["Name"], axis["Tag"]
		except:
			# Glyphs 3:
			axisName, axisTag = x.name(), x.axisTag()

		axisDict[axisName] = { "tag": axisTag, "min": sliderValues[0][i], "max": sliderValues[0][i] }
		
		for j, thisMaster in enumerate(thisFont.masters):
			masterValue = sliderValues[j][i]
			if masterValue < axisDict[axisName]["min"]:
				axisDict[axisName]["min"] = masterValue
			elif masterValue > axisDict[axisName]["max"]:
				axisDict[axisName]["max"] = masterValue
				
	return axisDict

def axisDictForFontWithAxisLocationParameters(thisFont):
	axisDict = {}
	for m in thisFont.masters:
		for axisLocation in m.customParameters["Axis Location"]:
			axisName = axisLocation["Axis"]
			axisPos = float(axisLocation["Location"])
			if not axisName in axisDict:
				axisDict[axisName] = {"min":axisPos,"max":axisPos}
			else:
				if axisPos < axisDict[axisName]["min"]:
					axisDict[axisName]["min"] = axisPos
				if axisPos > axisDict[axisName]["max"]:
					axisDict[axisName]["max"] = axisPos
	
	# add tags:
	for axis in thisFont.axes:
		axisName = axis["Name"]
		axisTag = axis["Tag"]
		axisDict[axisName]["tag"] = axisTag
	
	return axisDict

def allUnicodeEscapesOfFont( thisFont ):
	allUnicodes = ["&#x%s;" % g.unicode for g in thisFont.glyphs if g.unicode and g.export ]
	return " ".join( allUnicodes )

def featureListForFont( thisFont ):
	returnString = ""
	featureList = [(f.name, f.notes) for f in thisFont.features if not f.name in ("ccmp", "aalt", "locl", "kern", "calt", "liga", "clig") and not f.disabled()]
	for (f,n) in featureList:
		# <input type="checkbox" name="kern" id="kern" value="kern" class="otFeature" onchange="updateFeatures()" checked><label for="kern" class="otFeatureLabel">kern</label>
		if f.startswith("ss") and n and n.startswith("Name:"):
			# stylistic set name:
			setName = n.splitlines()[0][5:].strip()
			returnString += '\t\t\t\t<input type="checkbox" name="%s" id="%s" value="%s" class="otFeature" onchange="updateFeatures()"><label for="%s" class="otFeatureLabel">%s<span class="tooltip">%s</span></label>\n' % (f,f,f,f,f,setName)
		else:
			returnString += '\t\t\t\t<input type="checkbox" name="%s" id="%s" value="%s" class="otFeature" onchange="updateFeatures()"><label for="%s" class="otFeatureLabel">%s</label>\n' % (f,f,f,f,f)
	return returnString.rstrip()

def allOTVarSliders(thisFont):
	axisDict = generateAxisDict(thisFont)

	# go through *all* virtual masters:
	virtualMasters = [cp for cp in Font.customParameters if cp.name=="Virtual Master"]
	for virtualMaster in virtualMasters:
		for axis in virtualMaster.value:
			name = axis["Axis"]
			location = int(axis["Location"])
			if location < axisDict[name]["min"]:
				axisDict[name]["min"] = location
			if location > axisDict[name]["max"]:
				axisDict[name]["max"] = location
	
	minValues, maxValues = {}, {}
	for axis in axisDict:
		tag = axisDict[axis]["tag"]
		minValues[tag] = axisDict[axis]["min"]
		maxValues[tag] = axisDict[axis]["max"]
	
	html = ""
	for axis in thisFont.axes:
		try:
			# Glyphs 2:
			axisName = unicode(axis["Name"])			
		except:
			# Glyphs 3:
			axisName = axis.name()
		minValue = axisDict[axisName]["min"]
		maxValue = axisDict[axisName]["max"]
		axisTag = axisDict[axisName]["tag"]
		
		html += u"\t\t\t<div class='labeldiv'><label class='sliderlabel' id='label_%s' name='%s'>%s</label><input type='range' min='%i' max='%i' value='%i' class='slider' id='%s' oninput='updateSlider();'></div>\n" % (
			axisTag, axisName, axisName, 
			minValue, maxValue, minValue,
			axisTag
		)
		
	return html

def warningMessage():
	Message(
		title="Out of Date Warning", 
		message="It appears that you are not running the latest version of Glyphs. Please enable Cutting Edge Versions and Automatic Version Checks in Preferences > Updates, and update to the latest beta.",
		OKButton=None
		)

def axisValuesForMaster(thisMaster):
	try:
		axisValueList = [0.0,0.0,0.0,0.0,0.0,0.0]
		for i,value in enumerate(thisMaster.axes):
			axisValueList[i] = value
		axisValues = tuple(axisValueList)
	except:
		try:
			axisValues = (
				thisMaster.weightValue,
				thisMaster.widthValue,
				thisMaster.customValue,
				thisMaster.customValue1(),
				thisMaster.customValue2(),
				thisMaster.customValue3(),
			)
			warningMessage()
		except:
			axisValues = (
				thisMaster.weightValue,
				thisMaster.widthValue,
				thisMaster.customValue,
				thisMaster.customValue1,
				thisMaster.customValue2,
				thisMaster.customValue3,
			)
	return axisValues
	

def defaultVariationCSS(thisFont):
	firstMaster = thisFont.masters[0]
	axisValues = axisValuesForMaster(firstMaster)
		
	defaultValues = []
	for i, axis in enumerate(thisFont.axes):
		try:
			# Glyphs 2:
			tag = axis["Tag"]
		except:
			# Glyphs 3:
			tag = axis.axisTag()
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
				src: url("###fontFileName###");
			}
			body {
				padding: 0;
				margin: auto;
				overflow-x: hidden;
			}
			#flexbox {
				display: flex;
				flex-flow: column;
				height: 100%;
			}
			#controls {
				flex: 0 1 auto;
				background-color: white;
				margin: 2px 0 0 0;
				padding: 0;
				width: 100%;
				border: 0px solid transparent;
				height: auto;
			}

/* OTVar Sliders: */
			.labeldiv {
				width: 49.2%;
				padding: 0 0 0 0.2%;
				margin: auto;
				display: inline-block;
			}
 			label {
				z-index: 2;
				position: absolute;
				pointer-events: none;
				height: 2em;
				margin: 0;
				padding: 0.5em 1em;
				vertical-align: text-top;
				font: x-small sans-serif;
				color: black;
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
				padding: auto;
				margin: auto;
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

/* Feature Buttons: */
			#featureControls {
				font-size: x-small;
				font-family: sans-serif;
				padding: 0 0.2%;
			}
			.otFeatureLabel, .otFeature {
				font-size: small;
				position: relative;
				opacity: 1;
				pointer-events: auto;
				white-space: nowrap;
			}
			.otFeatureLabel {
				padding: 0.2em 0.5em 0.3em 0.5em;
				margin: 0 .04em;
				line-height: 2em;
				color: #666;
				background-color: #ddd;
				border-radius: 0.3em;
				border: 0;
				text-align: center;
				z-index: 6;
			}
			.otFeature {
				visibility: collapse;
				margin: 0 -1em 0 0;
			}
			input[type=checkbox]:checked + label { 
				visibility: visible;
				color: #eee;
				background-color: #555; 
				position: relative;
			}
			.otFeatureLabel .tooltip {
				visibility: hidden;
				background-color: #333;
				color: white;
				text-align: center;
				padding: 0px 5px;
				top: -2em;
				left: 0;
				position: absolute;
				z-index: 8;
			}
			.otFeatureLabel:hover .tooltip {
				visibility: visible;
			}

/* Sample Text Area: */
			#textarea {
				flex: 1 1 auto;
				border: 0 solid transparent;
				margin: auto;
				padding: 0 0 0.6em 0;
				line-height: 1em;
				width: 100%;
				color: black;
				font: 150px "###fontFamilyName###";
				font-feature-settings: "kern" on, "liga" on, "calt" on;
				-moz-font-feature-settings: "kern" on, "liga" on, "calt" on;
				-webkit-font-feature-settings: "kern" on, "liga" on, "calt" on;
				-ms-font-feature-settings: "kern" on, "liga" on, "calt" on;
				-o-font-feature-settings: "kern" on, "liga" on, "calt" on;
				font-variation-settings: ###variationSettings###;
				overflow-x: hidden;
				overflow-y: scroll;
				word-wrap: break-word;
			}
			div:focus {
				outline: 0px solid transparent;
			}
			
/* Footer paragraph: */
			#helptext {
			    position: fixed;
				background: transparent;
			    bottom: 0;
			    width: 100%;
				color: #888;
				font: x-small sans-serif;
			}
			a {
				color: #333;
			}
			
/* Dark Mode: */
			@media (prefers-color-scheme: dark) {
				body { background: #000; }
				p { color: #eee; }
				#textInput{
					color: #eee;
					background-color: #222;
					background: #222;
				}
	 			label { color: #fff; }
				.otFeatureLabel {
					color: #999;
					background-color: #333;
				}
				input[type=checkbox]:checked + label { 
					color: #111;
					background-color: #888; 
				}
				.slider { background: #333; }
				.slider::-webkit-slider-thumb { background: #888; }
				
				a { color: #ccc; }
				#controls {
					background-color: black;
				}
				
				#textarea {
					color: white;
					background-color: black;
				}
			}
			
		</style>
		<script>
			document.addEventListener('keyup', function(event) {
				if (event.code == 'KeyR' && (event.ctrlKey)) {
					updateParagraph();
				}
			});
			
			function updateFeatures() {
				// update features based on user input:
				var testtext = getTestText();
				var codeLine = "";
				var checkboxes = document.getElementsByClassName("otFeature")
				for (i = 0; i < checkboxes.length; i++) {
					var checkbox = checkboxes[i];
					if (i!=0) { codeLine += ", " };
					codeLine += '"'+checkbox.name+'" ';
					codeLine += checkbox.checked ? '1' : '0';
					if (checkbox.name=="kern") {
						testtext.style.setProperty("font-kerning", checkbox.checked ? 'normal' : 'none');
					} else if (checkbox.name=="liga") {
						testtext.style.setProperty("font-variant-ligatures", checkbox.checked ? 'common-ligatures contextual' : 'no-common-ligatures no-contextual');
					} else if (checkbox.name=="dlig") {
						testtext.style.setProperty("font-variant-ligatures", checkbox.checked ? 'discretionary-ligatures' : 'no-discretionary-ligatures');
					} else if (checkbox.name=="hlig") {
						testtext.style.setProperty("font-variant-ligatures", checkbox.checked ? 'historical-ligatures' : 'no-historical-ligatures');
					}
				}
				testtext.style.setProperty("font-feature-settings", codeLine);
			}
			
			function updateParagraph() {
				const defaulttext = "The Quick Brown Fox Jumps Over the Lazy Dog.";
				var testtext = getTestText();
				testtext.innerHTML = defaulttext;
			}
			
			function getTestText() {
				return document.getElementById("textarea");
			}
		
			function updateSlider() {
				var body = getTestText();
				var sliders = document.getElementsByClassName("slider");
				var settingtext = "";
				for (var i = 0; i < sliders.length; i++) {
					var sliderID = sliders[i].id;
					var sliderValue = sliders[i].value;
					var label = document.getElementById("label_"+sliderID);
					var labelName = label.getAttribute("name");
					
					label.textContent = ""+labelName+": "+sliderValue;
					
					if (sliderID == "fontsize") {
						// Text Size Slider
						body.style.setProperty("font-size", ""+sliderValue+"px");
						label.textContent += "px";
					} else if (sliderID == "lineheight") {
						// Line Height Slider
						body.style.setProperty("line-height", ""+sliderValue/100.0+"em");
						label.textContent += "%";
					} else {
						// OTVar Slider: collect settings
						if (settingtext != "") { settingtext += ", " };
						settingtext += '"' + sliderID + '" ' + sliderValue;
					}
				}
				// apply OTVar slider settings:
				body.style.setProperty("font-variation-settings", settingtext);
			}
			
			function vanish(item) {
				item.style.setProperty("display", "none");
			}
		</script>
	</head>
	<body onload="updateSlider();updateParagraph();document.getElementById('textarea').focus()">
	<div id="flexbox">
		<div id="controls">
			<!-- OTVar Sliders -->
			<div class="labeldiv"><label class="sliderlabel" id="label_fontsize" name="Font Size">Font Size</label><input type="range" min="10" max="300" value="150" class="slider" id="fontsize" oninput="updateSlider();"></div>
			<div class="labeldiv"><label class="sliderlabel" id="label_lineheight" name="Line Height">Line Height</label><input type="range" min="30" max="300" value="100" class="slider" id="lineheight" oninput="updateSlider();"></div>
###sliders###

			<!-- OT features -->
			<div id="featureControls">
				<input type="checkbox" name="kern" id="kern" value="kern" class="otFeature" onchange="updateFeatures()" checked><label for="kern" class="otFeatureLabel">kern</label>
				<input type="checkbox" name="liga" id="liga" value="liga" class="otFeature" onchange="updateFeatures()" checked><label for="liga" class="otFeatureLabel">liga</label>
				<input type="checkbox" name="calt" id="calt" value="calt" class="otFeature" onchange="updateFeatures()" checked><label for="calt" class="otFeatureLabel">calt</label>
###featureList###
			</div>
		</div>
		
		<!-- Test Text -->
		<div contenteditable="true" spellcheck="false" autocomplete="true" id="textarea">
		</div>
	</div>
		
	<!-- Disclaimer -->
	<p id="helptext" onmouseleave="vanish(this);">
		Ctrl-R to reset the charset. Not working? Please try in a newer macOS or use the <a href="https://www.google.com/chrome/">latest Chrome</a>. Pull mouse across this note to make it disappear.
	</p>
	</body>
</html>
"""

# clears macro window log:
Glyphs.clearLog()

# Query app version:
GLYPHSAPPVERSION = NSBundle.bundleForClass_(NSClassFromString("GSMenu")).infoDictionary().objectForKey_("CFBundleShortVersionString")
appVersionHighEnough = not GLYPHSAPPVERSION.startswith("1.")

if appVersionHighEnough:
	firstDoc = Glyphs.orderedDocuments()[0]
	thisFont = Glyphs.font # frontmost font
	exportPath = currentOTVarExportPath()
	familyName = otVarFamilyName(thisFont)

	print("Preparing Test HTML for: %s" % familyName)
	
	replacements = (
		( "###fontFamilyNameWithSpaces###", familyName ),
		( "###fontFamilyName###", otVarFamilyName(thisFont) ),
		( "The Quick Brown Fox Jumps Over the Lazy Dog.", allUnicodeEscapesOfFont(thisFont) ),
		( "###sliders###", allOTVarSliders(thisFont) ),
		( "###variationSettings###", defaultVariationCSS(thisFont) ), 
		( "###fontFileName###", otVarFileName(thisFont) ),
		( "###featureList###", featureListForFont(thisFont) ),
		
	)

	htmlContent = replaceSet( htmlContent, replacements )
	
	# Write file to disk:
	if exportPath:
		if saveFileInLocation( content=htmlContent, fileName="%s fonttest.html" % familyName, filePath=exportPath ):
			print("Successfully wrote file to disk.")
			terminalCommand = 'cd "%s"; open .' % exportPath
			system( terminalCommand )
		else:
			print("Error writing file to disk.")
	else:
		Message( 
			title="OTVar Test HTML Error",
			message="Could not determine export path. Have you exported any variable fonts yet?",
			OKButton=None
		)
else:
	Message(
		title="App Version Error",
		message="This script requires Glyphs 2.5 or later. Sorry.",
		OKButton=None
	)

