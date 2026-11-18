# MenuTitle: Webfont Test HTML
__doc__ = """
Create a Test HTML for the current font inside the current Webfont Export folder, or for the current Glyphs Project in the project’s export path.
"""

from GlyphsApp import Glyphs, GSProjectDocument, INSTANCETYPESINGLE, Message
from os import system, path
from itertools import product
import codecs
import webbrowser
import json
from urllib.parse import quote
Glyphs.registerDefault("com.mekkablue.WebFontTestHTML.includeEOT", 0)


def saveFileInLocation(content="Sorry, no content generated.", fileName="test.txt", filePath="~/Desktop"):
	saveFileLocation = "%s/%s" % (filePath, fileName)
	saveFileLocation = saveFileLocation.replace("//", "/")
	with codecs.open(saveFileLocation, "w", "utf-8") as thisFile:
		print("Exporting to:", thisFile.name)
		thisFile.write(content)
		thisFile.close()
	return True


def currentFileFormats():
	if Glyphs.versionNumber < 3.0:
		# GLYPHS 2
		fileFormats = ["woff", "woff2"]
		if Glyphs.defaults["com.mekkablue.WebFontTestHTML.includeEOT"]:
			fileFormats.append("eot")
	else:
		# GLYPHS 3
		fileFormats = []
		if Glyphs.defaults["OTFExportPlain"]:
			# Glyphs 4 spells the key "OTFExportOutlineFormat"; 1 = CFF, 2 = TT
			outlineFormat = Glyphs.defaults["OTFExportOutlineFormat"] or Glyphs.defaults["OTFExportOutlineformat"]
			if outlineFormat == 2:  # TTF
				fileFormats.append("ttf")
			else:
				fileFormats.append("otf")
		if Glyphs.defaults["OTFExportWOFF"]:
			fileFormats.append("woff")
		if Glyphs.defaults["OTFExportWOFF2"]:
			fileFormats.append("woff2")
	return tuple(fileFormats)


def currentWebExportPath():
	if Glyphs.versionNumber < 3.0:
		# GLYPHS 2
		exportPath = Glyphs.defaults["WebfontPluginExportPathManual"]
		if Glyphs.defaults["WebfontPluginUseExportPath"]:
			exportPath = Glyphs.defaults["WebfontPluginExportPath"]
	else:
		# GLYPHS 3 and 4 (Glyphs 4 renamed the key to OTFUseExportPath)
		exportPath = Glyphs.defaults["OTFExportPathManual"]
		if Glyphs.defaults["OTFExportUseExportPath"] or Glyphs.defaults["OTFUseExportPath"]:
			exportPath = Glyphs.defaults["OTFExportPath"]
	return exportPath


def replaceSet(text, setOfReplacements):
	for thisReplacement in setOfReplacements:
		searchFor = thisReplacement[0]
		replaceWith = thisReplacement[1]
		text = text.replace(searchFor, replaceWith)
	return text


def allUnicodeEscapesOfFont(thisFont):
	importedGlyphs = thisFont.importedGlyphs()
	if not importedGlyphs:
		importedGlyphs = []
	allUnicodes = ["&#x%s;" % g.unicode for g in list(thisFont.glyphs) + importedGlyphs if g.unicode and g.export and g.subCategory != "Nonspacing"]
	allUnicodes += [" &#x%s;" % g.unicode for g in list(thisFont.glyphs) + importedGlyphs if g.unicode and g.export and g.subCategory == "Nonspacing"]
	return "".join(allUnicodes)


def allGlyphInfoOfFont(thisFont):
	# collects char, glyph name and Unicode value for the grid view (with hover tooltip)
	importedGlyphs = thisFont.importedGlyphs()
	if not importedGlyphs:
		importedGlyphs = []
	glyphInfos = []
	for g in list(thisFont.glyphs) + importedGlyphs:
		if g.unicode and g.export:
			try:
				char = chr(int(g.unicode, 16))
			except ValueError:
				continue
			glyphInfos.append({
				"char": char,
				"name": g.name,
				"uni": g.unicode,
				"category": g.category or "",
				"subCategory": g.subCategory or "",
			})
	return glyphInfos


def glyphInfoJSONForFont(thisFont):
	jsonText = json.dumps(allGlyphInfoOfFont(thisFont), ensure_ascii=False)
	# avoid accidentally closing the surrounding <script> tag:
	jsonText = jsonText.replace("</", "<\\/")
	return jsonText


def getInstanceInfo(thisFont, activeInstance, fileFormat):
	# Determine Family Name

	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		familyName = activeInstance.familyName
		if not familyName:
			familyName = thisFont.familyName
	else:
		# GLYPHS 2
		familyName = thisFont.familyName
		individualFamilyName = activeInstance.customParameters["familyName"]
		if individualFamilyName is not None:
			familyName = individualFamilyName

	# Determine Style Name
	activeInstanceName = activeInstance.name
	
	# Verify file format
	if fileFormat in ("otf", "ttf"): # otherwise woff, woff2 or eot
		ttParameter = activeInstance.customParameterActiveForKey_("Save as TrueType")
		if ttParameter:
			if ttParameter.value:
				fileFormat = "ttf"
			else:
				fileFormat = "otf"

	# Determine font and file names for CSS
	menuName = "%s %s-%s" % (fileFormat.upper(), familyName, activeInstanceName)

	# 3 approaches for determining the file names:
	try:
		instanceFileName = activeInstance.fileName()
	except TypeError:
		# Glyphs 4: fileName() now requires a format argument
		instanceFileName = activeInstance.fileName(fileFormat)
	firstPartOfFileName = ".".join(instanceFileName.split(".")[:-1])  # removes ".otf" at the end
	if not firstPartOfFileName:
		firstPartOfFileName = activeInstance.customParameters["fileName"]
	if not firstPartOfFileName:
		firstPartOfFileName = "%s-%s" % (familyName.replace(" ", ""), activeInstanceName.replace(" ", ""))

	fileName = "%s.%s" % (firstPartOfFileName, fileFormat)

	exportFolderParameter = activeInstance.customParameterActiveForKey_("Export Folder")
	exportFolderParameterFontWide = thisFont.customParameterActiveForKey_("Export Folder")
	for parameter in (exportFolderParameter, exportFolderParameterFontWide):
		if parameter:
			exportFolder = parameter.value
			fileName = path.join(exportFolder, fileName)
			menuName = f"📁 {exportFolder} ⏵ {menuName}"
			break

	return fileName, menuName, activeInstanceName


def instanceIsActive(instance):
	if Glyphs.buildNumber > 3198:
		return instance.exports
	else:
		return instance.active


def allActiveInstancesOfFont(thisFont):
	activeInstances = [i for i in thisFont.instances if instanceIsActive(i) and isSingleInstance(i)]
	return activeInstances


def allActiveInstancesOfProject(thisProject):
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		activeInstances = [i for i in thisProject.instances if instanceIsActive(i) and isSingleInstance(i)]
	else:
		# GLYPHS 2
		activeInstances = [i for i in thisProject.instances() if instanceIsActive(i) and isSingleInstance(i)]
	return activeInstances


def isSingleInstance(instance):
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3
		return instance.type == INSTANCETYPESINGLE
	else:
		# GLYPHS 2
		return True


def particleInstancesOfFont(thisFont):
	# Glyphs 4: a particle set is a GSInstance of type 4; its name particles
	# are the STAT entries from which the exported style names are constructed
	if not Glyphs.versionNumber or Glyphs.versionNumber < 4:
		return []
	particleInstances = []
	for thisInstance in thisFont.instances:
		try:
			if thisInstance.type == 4 and instanceIsActive(thisInstance):
				particleInstances.append(thisInstance)
		except:
			pass
	return particleInstances


def particleStylesOfInstance(thisFont, particleInstance):
	"""
	Multiplies the name particles of all axes with each other, in the order of
	the font's axes, and returns a list of (styleName, axisValues) tuples,
	axisValues being a dict {axisTag: axisValue}. "Regular" is elidable for
	every axis; if all particles are elided, the instance name is the fallback.
	"""
	axisTags = []
	particlesPerAxis = []
	for axis in thisFont.axes:
		particles = particleInstance.nameParticles[axis.axisId]
		if not particles:
			continue
		axisTags.append(axis.axisTag)
		particlesPerAxis.append(list(particles))
	if not particlesPerAxis:
		return []

	styles = []
	for particleCombination in product(*particlesPerAxis):
		nameParts = [particle.name for particle in particleCombination if particle.name != "Regular"]
		styleName = " ".join(nameParts) if nameParts else particleInstance.name
		axisValues = {}
		for axisTag, particle in zip(axisTags, particleCombination):
			axisValue = particle.external if particle.external else particle.internal
			if axisValue is None:
				continue
			axisValues[axisTag] = axisValue
		styles.append((styleName, axisValues))
	return styles


def webfontFormatsOf(*objects):
	# returns the formats of the first "Webfont Formats" parameter found in objects, or None
	for thisObject in objects:
		if not thisObject:
			continue
		try:
			parameter = thisObject.customParameterActiveForKey_("Webfont Formats")
			value = parameter.value if parameter else None
		except AttributeError:
			# e.g. GSProjectDocument in some app versions:
			try:
				value = thisObject.customParameters["Webfont Formats"]
			except (AttributeError, TypeError, KeyError):
				continue
		if value:
			return list(value)
	return None


def activeInstancesByFormat(thisFont, activeInstances, fileFormats, availableFormats=("otf", "ttf", "woff", "woff2", "eot"), fallbackParameterSource=None):
	instanceInfos = {}
	for availableFormat in availableFormats:
		instanceInfos[availableFormat] = []

	for activeInstance in activeInstances:
		for fileFormat in fileFormats:
			webFormats = webfontFormatsOf(activeInstance, fallbackParameterSource)
			if webFormats:
				if "plain" in webFormats:
					webFormats[webFormats.index("plain")] = fileFormat
			else:
				webFormats = [fileFormat]
			
			for webFormat in webFormats:
				if webFormat not in availableFormats:
					print("Error: cannot identify format", webFormat)
					continue
				fileName, menuName, activeInstanceName = getInstanceInfo(thisFont, activeInstance, webFormat)
				instanceInfos[webFormat.lower().strip()].append((fileName, menuName, activeInstanceName))

	# Glyphs 4: complement with static styles constructed from particle sets
	# (GSInstance type 4); single instances above override styles of the same name:
	for particleInstance in particleInstancesOfFont(thisFont):
		try:
			familyName = particleInstance.familyName
		except:
			familyName = None
		if not familyName:
			familyName = thisFont.familyName
		for styleName, axisValues in particleStylesOfInstance(thisFont, particleInstance):
			for fileFormat in fileFormats:
				if fileFormat not in availableFormats:
					continue
				fileName = "%s-%s.%s" % (familyName.replace(" ", ""), styleName.replace(" ", ""), fileFormat)
				existingInfos = instanceInfos[fileFormat]
				if any(info[0] == fileName or info[2] == styleName for info in existingInfos):
					continue
				menuName = "%s %s-%s" % (fileFormat.upper(), familyName, styleName)
				existingInfos.append((fileName, menuName, styleName))

	orderedInstanceInfos = []
	for availableFormat in availableFormats:
		for info in instanceInfos[availableFormat]:
			orderedInstanceInfos.append(info)
	return orderedInstanceInfos


def activeInstancesOfFontByFormat(thisFont, fileFormats=("woff", "woff2")):
	activeInstances = allActiveInstancesOfFont(thisFont)
	listOfInstanceInfo = activeInstancesByFormat(thisFont, activeInstances, fileFormats, fallbackParameterSource=thisFont)
	return listOfInstanceInfo


def projectFileFormats(thisProject):
	# In a .glyphsproject, the webfont formats are NOT taken from the app’s
	# Export dialog, but exclusively from the "Webfont Formats" parameter
	# (project-wide or per instance). So we only supply the plain outline
	# format here; getInstanceInfo() will switch it to ttf where necessary,
	# and a "Webfont Formats" parameter will override it completely.
	fileFormat = "otf"
	thisFont = thisProject.font()
	for thisObject in (thisProject, thisFont):
		if not thisObject:
			continue
		try:
			ttParameter = thisObject.customParameterActiveForKey_("Save as TrueType")
		except AttributeError:
			continue
		if ttParameter:
			fileFormat = "ttf" if ttParameter.value else "otf"
			break
	return (fileFormat, )


def activeInstancesOfProjectByFormat(thisProject, fileFormats=None):
	thisFont = thisProject.font()
	if not fileFormats:
		fileFormats = projectFileFormats(thisProject)
	activeInstances = allActiveInstancesOfProject(thisProject)
	listOfInstanceInfo = activeInstancesByFormat(thisFont, activeInstances, fileFormats, fallbackParameterSource=thisProject)
	return listOfInstanceInfo


def optionListForInstances(instanceList):
	returnString = ""
	for thisInstanceInfo in instanceList:
		returnString += '			<option value="%s">%s</option>\n' % (thisInstanceInfo[0], thisInstanceInfo[1])
		# <option value="fileName">baseName</option>
	return returnString


def fontFaces(instanceList):
	returnString = ""
	for thisInstanceInfo in instanceList:
		fileName = thisInstanceInfo[0]
		nameOfTheFont = thisInstanceInfo[1]
		returnString += "\t\t@font-face { font-family: '%s'; src: url('%s'); }\n" % (nameOfTheFont, fileName)

	return returnString


def fontFacesJSONForInstances(instanceList):
	fontFaceList = [{"family": thisInstanceInfo[1], "url": thisInstanceInfo[0]} for thisInstanceInfo in instanceList]
	jsonText = json.dumps(fontFaceList, ensure_ascii=False)
	# avoid accidentally closing the surrounding <script> tag:
	jsonText = jsonText.replace("</", "<\\/")
	return jsonText


featureDescriptions = {
	"c2pc": "Petite capitals from capitals",
	"c2sc": "Small capitals from capitals",
	"case": "Case-sensitive forms",
	"cpsp": "Capital spacing",
	"dlig": "Discretionary ligatures",
	"dnom": "Denominators",
	"fina": "Terminal forms",
	"frac": "Fractions",
	"fwid": "Full widths",
	"half": "Half forms",
	"hist": "Historical forms",
	"hlig": "Historical ligatures",
	"init": "Initial forms",
	"isol": "Isolated forms",
	"jp04": "JIS04 forms",
	"liga": "Standard ligatures",
	"lnum": "Lining figures",
	"locl": "Localized forms",
	"mark": "Mark positioning",
	"medi": "Medial forms",
	"mkmk": "Mark-to-mark positioning",
	"nalt": "Alternate annotation forms",
	"numr": "Numerators",
	"onum": "Oldstyle figures",
	"ordn": "Ordinals",
	"ornm": "Ornaments",
	"palt": "Proportional alternate widths",
	"pcap": "Petite capitals",
	"pnum": "Proportional figures",
	"pwid": "Proportional widths",
	"rlig": "Required ligatures",
	"rvrn": "Required variation alternates",
	"salt": "Stylistic alternates",
	"sinf": "Scientific inferiors",
	"smcp": "Small capitals",
	"subs": "Subscript",
	"sups": "Superscript",
	"swsh": "Swash",
	"titl": "Titling",
	"tnum": "Tabular figures",
	"zero": "Slashed zero",
}


def featureDescription(tag):
	"""A short description of an OpenType feature tag for the button tooltip."""
	if tag in featureDescriptions:
		return "%s: %s" % (tag, featureDescriptions[tag])
	if len(tag) == 4 and tag[:2] in ("ss", "cv") and tag[2:].isdigit():
		return "%s: %s %d" % (tag, "Stylistic set" if tag.startswith("ss") else "Character variant", int(tag[2:]))
	return "%s: OpenType feature" % tag


def featureListForFont(thisFont):
	returnString = ""
	featureList = [(f.name, f.notes) for f in thisFont.features if f.name not in ("ccmp", "aalt", "locl", "kern", "calt", "liga", "clig") and not f.disabled()]
	doneFeatures = []
	for (f, n) in featureList:
		if f not in doneFeatures:  # avoid duplicates
			doneFeatures.append(f)
			if f.startswith("ss") and n and n.startswith("Name:"):
				# stylistic set name:
				setName = n.splitlines()[0][5:].strip()
				returnString += '\t\t<input type="checkbox" id="%s" value="%s" class="otFeature" onchange="updateFeatures()"><label for="%s" class="otFeatureLabel">%s<span class="tooltip">%s</span></label>\n' % (
					f, f, f, f, setName
				)
			else:
				returnString += '\t\t<input type="checkbox" id="%s" value="%s" class="otFeature" onchange="updateFeatures()"><label for="%s" class="otFeatureLabel" title="%s">%s</label>\n' % (
					f, f, f, featureDescription(f), f
				)
	return returnString


htmlContent = """<head>
	<!--<base href="..">--> <!-- uncomment for keeping the HTML in a subfolder -->
	<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
	<meta http-equiv="Content-type" content="text/html; charset=utf-8" />
	<meta http-equiv="X-UA-Compatible" content="IE=9" />
	<title>familyName</title>
	<style type="text/css" media="screen">
		<!-- fontFaces -->
		body {
			background: white;
			color: black;
		}
		.features, .label, a, #controls {
			font: normal normal normal small sans-serif;
		}
		.features .emojiButton {
			vertical-align: -5%;
			font-size: small;
			padding: 0.15em 0.25em;
			margin: 0 -0.25em; /* padding only for the highlight of the active view: the buttons stay close together */
		}
		.emojiButton {
			cursor: pointer;
			text-decoration: none;
		}
		.emojiButton.gapAfter {
			margin-right: 0.3em;
		}
		#flexbox {
			display: flex;
			flex-flow: column;
			height: 100%;
		}
		#controls {
			flex: 0 1 auto;
			margin: 0;
			padding: 0;
			width: 100%;
			border: 0px solid transparent;
			height: auto;
			user-select: none;
			-moz-user-select: none;
			-webkit-user-select: none;
		}
		#metricsLine {
			background-color: #EEE;
			border-top: 1px solid #AAA;
			border-bottom: 1px solid #AAA;
			width: 100%;
			margin: 0.2em 0;
			padding: 0 0;
			font-size: 6em;
			white-space: nowrap;
			overflow-x: auto;
			overflow-y: hidden;
			text-overflow: none;
			display: none;
			scrollbar-width: none; /* Firefox */
			-ms-overflow-style: none;  /* Internet Explorer 10+ */
		}
		#metricsLine::-webkit-scrollbar { /* WebKit */
			width: 0;
			height: 0;
		}
		#waterfall, #grid, #textview {
			flex: 1 1 auto;
			border: 0 solid transparent;
			margin: 0;
			padding: 0;
			width: 100%;
			color: black;
			overflow-x: hidden;
			overflow-y: scroll;
			font-family: "nameOfTheFont";
			font-feature-settings: "kern" on, "liga" on, "calt" on;
			-moz-font-feature-settings: "kern" on, "liga" on, "calt" on;
			-webkit-font-feature-settings: "kern" on, "liga" on, "calt" on;
			-ms-font-feature-settings: "kern" on, "liga" on, "calt" on;
			-o-font-feature-settings: "kern" on, "liga" on, "calt" on;
		}
		div, p	{
			padding: 0;
			margin: 0;
		}
		#waterfall p {
			margin-bottom: 0.8em;
			overflow-wrap: break-word;
		}
		.○ .sampletext, .○#textview, .○#grid {
			-webkit-text-stroke: 1px black;
			-webkit-text-fill-color: #FFF0;
		}
		#grid {
			display: none;
			flex-wrap: wrap;
			align-content: flex-start;
			padding: 0.2em;
			font-size: 60px;
		}
		.gridCell {
			display: inline-flex;
			justify-content: center;
			align-items: center;
			box-sizing: border-box;
			flex: 0 0 auto;
			width: var(--grid-cell-size, 84px);
			height: var(--grid-cell-size, 84px);
			border: 1px solid #eee;
			line-height: 1;
			position: relative;
		}
		.gridCell .tooltip {
			visibility: hidden;
			position: absolute;
			bottom: 100%;
			left: 50%;
			transform: translateX(-50%);
			background-color: #333;
			color: white;
			-webkit-text-stroke: 0; /* the tooltip stays readable in x-ray mode */
			-webkit-text-fill-color: white;
			text-align: center;
			white-space: nowrap;
			padding: 2px 5px;
			font: normal normal normal small sans-serif;
			border-radius: 0.2em;
			z-index: 8;
		}
		.gridCell:hover .tooltip {
			visibility: visible;
		}
		#textview {
			display: none;
			padding: 0.2em;
			font-size: 60px;
			line-height: 1.2em;
			word-wrap: break-word;
		}
		#textview:focus {
			outline: 0 solid transparent;
		}
		.viewLink.activeView {
			background-color: #bbb;
			border-radius: 0.3em;
		}
		.sliderControls {
			display: none;
		}
		.sliderControls label {
			font: normal normal normal small sans-serif;
			color: #888;
			margin-right: 1em;
		}
		.sliderControls input[type=range] {
			vertical-align: middle;
		}
		.features, .label, a {
			color: #888;
		}
		.label {
			background-color: #ddd;
			padding: 2px 3px;
		}

		span#p08 { font-size: 08pt; padding: 08pt 0; }
		span#p09 { font-size: 09pt; padding: 09pt 0; }
		span#p10 { font-size: 10pt; padding: 10pt 0; }
		span#p11 { font-size: 11pt; padding: 11pt 0; }
		span#p12 { font-size: 12pt; padding: 12pt 0; }
		span#p13 { font-size: 13pt; padding: 13pt 0; }
		span#p14 { font-size: 14pt; padding: 14pt 0; }
		span#p15 { font-size: 15pt; padding: 15pt 0; }
		span#p16 { font-size: 16pt; padding: 16pt 0; }
		span#largeParagraph { font-size: 32pt; padding: 32pt 0; }
		span#veryLargeParagraph { font-size: 100pt; padding: 100pt 0; }

		.otFeatureLabel {
			color: #666;
			background-color: #ddd;
			padding: 0.2em 0.5em 0.3em 0.5em;
			margin: 0 .04em;
			line-height: 2em;
			border-radius: 0.3em;
			border: 0;
			text-align:center;
		}
		.otFeatureLabel, .otFeature {
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
		.wrapper {
			width: auto;
			overflow: hidden;
			border: 0 solid transparent;
			display: flex;
			align-items: center;
		}
		.wrapper input[type=text] {
			flex: 1 1 auto;
			min-width: 0;
		}
		#resetText {
			flex: 0 0 auto;
			margin: 0 0.2em 0 0.4em;
			font-size: 1.4em;
			line-height: 1;
			text-decoration: none;
		}
		select {
			float: left;
			margin: 0 0.5em 0 0;
			padding: 0;
		}
		input[type=text] {
			border: 1px solid #999;
			margin: 0;
			width: 100%;
		}
		.features {
			clear: left;
		}
		input[type=checkbox]:checked + label {
			visibility: visible;
			color: #fff;
			background-color: #888;
		}
		.otFeature {
			visibility: collapse;
			margin: 0 -1em 0 0;
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

		/* Footer paragraph: */
		#helptext {
			color: black;
			background-color: #ddd;
			position: fixed;
			bottom: 0;
			padding: 2px;
			width: 100%;
			font: x-small sans-serif;
		}

		/* Dark Mode */
		@media (prefers-color-scheme: dark) {
			body {
				background: #333;
			}
			.features, .label, a, body, p, #metricsLine {
				color: white;
			}
			.label {
				background-color: black;
				padding: 2px 3px;
			}
			.otFeatureLabel, input[type=text] {
				color: white;
				background-color: black;
			}
			input[type=checkbox]:checked + label {
				color: black;
				background-color: #aaa;
			}
			#helptext {
				background-color: #777;
			}
			.○ .sampletext, .○#textview, .○#grid {
				-webkit-text-stroke: 1px white;
				-webkit-text-fill-color: #0000;
			}
			#metricsLine {
				background-color: #222;
				border-color: #777;
			}
			.gridCell {
				border-color: #444;
			}
			.viewLink.activeView {
				background-color: #555;
			}
			.sliderControls label {
				color: #aaa;
			}
		}
	</style>
</head>
<body onload="document.getElementById('textInput').focus();setCharset();setView('text');">
<div id="flexbox">
<div id="controls">
	<div>
		<select size="1" id="fontFamilySelector" name="fontFamilySelector" onchange="changeFont()">
		<!-- moreOptions -->
		</select>
		<div class="wrapper" spellcheck="false">
			<input type="text" value="Type Text Here." id="textInput" onkeyup="updateParagraph()" />
			<a onclick="setCharset();" id="resetText" class="emojiButton" title="Reset the sample text (Ctrl-R)">↺</a>
		</div>
	</div>
	<p class="features">
		<a onclick="reloadAllFonts();" id="reload" class="emojiButton gapAfter" title="Reload (after you reexported) – Ctrl-U">🔄</a>
		<a onclick="setView('text');" id="viewText" class="emojiButton viewLink activeView" title="Text view – Ctrl-G cycles through the views">🔤</a>
		<a onclick="setView('grid');" id="viewGrid" class="emojiButton viewLink" title="Grid view of all glyphs, double-click a glyph to open it in Glyphs – Ctrl-G cycles through the views">🔡</a>
		<a onclick="setView('waterfall');" id="viewWaterfall" class="emojiButton viewLink gapAfter" title="Waterfall view – Ctrl-G cycles through the views">⏬</a>
		<a onclick="toggleInverse();" id="invert" class="emojiButton" title="Toggle x-ray (outline) display">🔲</a>
		<label><input type="checkbox" id="kern" value="kern" class="otFeature" onchange="updateFeatures()" checked><label for="kern" class="otFeatureLabel" title="kern: Kerning">kern</label>
		<label><input type="checkbox" id="liga" value="liga" class="otFeature" onchange="updateFeatures()" checked><label for="liga" class="otFeatureLabel" title="liga, clig: Standard ligatures and contextual ligatures">liga/clig</label>
		<label><input type="checkbox" id="calt" value="calt" class="otFeature" onchange="updateFeatures()" checked><label for="calt" class="otFeatureLabel" title="calt: Contextual alternates">calt</label>
		<!-- moreFeatures -->
		<label title="Show the text in one large line above the waterfall, in a band with a line above and below"><input type="checkbox" value="show" onchange="updateFeatures();document.getElementById('metricsLine').style.display=this.checked?'block':'none'">Metrics</label>
	</p>
	<div class="sliderControls" id="gridControls">
		<label>Size: <input type="range" id="gridSize" min="20" max="300" value="60" oninput="updateGridSize()"></label>
	</div>
	<div class="sliderControls" id="textControls">
		<label>Size: <input type="range" id="textSize" min="10" max="500" value="60" oninput="updateTextView()"></label>
		<label>Line Distance: <input type="range" id="textLineHeight" min="50" max="300" value="120" oninput="updateTextView()"></label>
	</div>
</div>
<div id="waterfall" class="●">
	<div id="metricsLine"></div>
	<p><span class="label">08</span>&nbsp;<span class="sampletext" id="p08"></span></p>
	<p><span class="label">09</span>&nbsp;<span class="sampletext" id="p09"></span></p>
	<p><span class="label">10</span>&nbsp;<span class="sampletext" id="p10"></span></p>
	<p><span class="label">11</span>&nbsp;<span class="sampletext" id="p11"></span></p>
	<p><span class="label">12</span>&nbsp;<span class="sampletext" id="p12"></span></p>
	<p><span class="label">13</span>&nbsp;<span class="sampletext" id="p13"></span></p>
	<p><span class="label">14</span>&nbsp;<span class="sampletext" id="p14"></span></p>
	<p><span class="label">15</span>&nbsp;<span class="sampletext" id="p15"></span></p>
	<p><span class="label">16</span>&nbsp;<span class="sampletext" id="p16"></span></p>
	<p><span class="sampletext" id="largeParagraph"></span></p>
	<p><span class="sampletext" id="veryLargeParagraph"></span></p>
</div>
<div id="grid" class="●"></div>
<div id="textview" class="●"></div>
</div>

<!-- Disclaimer -->
<p id="helptext" onmouseleave="vanish(this);">
	Ctrl-R: Reset text. Ctrl-J: LTR/RTL. Ctrl-G: cycle views. Ctrl-U: reload fonts from disk. Cmd-Opt-Shift-E: open text in Glyphs. Double-click grid glyph: open in Glyphs. Ctrl-comma/period: step through fonts. Pull mouse across this note to make it disappear.
</p>

<script type="text/javascript">
	const selector = document.getElementById("fontFamilySelector");
	const selectorOptions = selector.options;
	const selectorLength = selectorOptions.length;
	const glyphInfoList = <!-- glyphInfoJSON -->;
	const fontFaceList = <!-- fontFaceJSON -->;
	const glyphNameForChar = {};
	for (const glyphInfo of glyphInfoList) {
		if (glyphInfo.name && !(glyphInfo.char in glyphNameForChar)) {
			glyphNameForChar[glyphInfo.char] = glyphInfo.name;
		}
	}
	const viewOrder = ["text", "grid", "waterfall"];
	const viewElementIds = {waterfall: "waterfall", grid: "grid", text: "textview"};

	document.addEventListener('keyup', keyAnalysis);

	function keyAnalysis(event) {
		if (event.metaKey && event.altKey && event.shiftKey && event.code == 'KeyE') {
			openTextInGlyphs(document.getElementById('textInput').value);
		} else if (event.ctrlKey) {
			if (event.code == 'KeyR') {
				setCharset();
			} else if (event.code == 'KeyJ') {
				toggleLeftRight();
			} else if (event.code == 'KeyG') {
				cycleView();
			} else if (event.code == 'KeyU') {
				reloadAllFonts();
			} else if (event.code == 'Period') {
				selector.selectedIndex = (selector.selectedIndex + 1) % selectorLength;
				changeFont();
			} else if (event.code == 'Comma') {
				var newIndex = selector.selectedIndex - 1;
				if (newIndex<0) {
					newIndex = selectorLength - 1;
				}
				selector.selectedIndex = newIndex;
				changeFont();
			}
		}
	}
	function version() {
		return new Date().getTime();
	}
	function reloadAllFonts() {
		for (const fontFace of fontFaceList) {
			new FontFace(fontFace.family, `url('${fontFace.url}?v=${version()}')`).load().then(function(loadedFontFace) {
				document.fonts.add(loadedFontFace);
				console.log('Font reloaded:', fontFace.family);
			}).catch(function(error) {
				console.error('Failed to reload font:', fontFace.family, error);
			});
		}
	}
	function glyphNamesForText(text) {
		// a token is either /glyphname or a single character; characters without a glyph in the font are left out
		const names = [];
		const characters = Array.from(text);
		let i = 0;
		while (i < characters.length) {
			let name = '';
			if (characters[i] === '/') {
				let j = i + 1;
				while (j < characters.length && characters[j] !== '/' && characters[j].trim() !== '') {
					name += characters[j];
					j++;
				}
				if (name) i = j;
			}
			if (!name) {
				name = glyphNameForChar[characters[i]];
				i++;
			}
			if (name) names.push(name);
		}
		return names;
	}
	function openTextInGlyphs(text) {
		// opens a new tab with these glyphs in Glyphs, see https://handbook.glyphsapp.com/en/single-page/#url-scheme
		if (!text) return;
		const glyphNames = glyphNamesForText(text);
		if (!glyphNames.length) {
			console.warn('Cannot open in Glyphs: found no glyphs for', text);
			return;
		}
		window.location.href = 'glyphsapp://show/?' + glyphNames.map(function(name) {
			return 'glyph=' + encodeURIComponent(name);
		}).join('&');
	}
	function updateParagraph() {
		// update paragraph text based on user input:
		const txt = document.getElementById('textInput');
		const paragraphs = document.getElementsByClassName('sampletext');
		for (i = 0; i < paragraphs.length; i++) {
			paragraph = paragraphs[i];
			paragraph.textContent = txt.value;
		}

		// update other elements:
		document.getElementById('metricsLine').textContent = txt.value;
		document.getElementById('textview').textContent = txt.value;
	}
	function currentView() {
		return viewOrder.find(v => document.getElementById('view' + v.charAt(0).toUpperCase() + v.slice(1)).classList.contains('activeView'));
	}
	function cycleView() {
		const nextView = viewOrder[(viewOrder.indexOf(currentView()) + 1) % viewOrder.length];
		setView(nextView);
	}
	function setView(view) {
		for (const v of viewOrder) {
			document.getElementById(viewElementIds[v]).style.display = 'none';
			document.getElementById('view' + v.charAt(0).toUpperCase() + v.slice(1)).classList.remove('activeView');
		}
		document.getElementById('gridControls').style.display = view == 'grid' ? 'block' : 'none';
		document.getElementById('textControls').style.display = view == 'text' ? 'block' : 'none';
		document.getElementById('view' + view.charAt(0).toUpperCase() + view.slice(1)).classList.add('activeView');
		document.getElementById(viewElementIds[view]).style.display = view == 'grid' ? 'flex' : 'block';
		if (view == 'grid') {
			buildGrid();
			updateGridSize();
		} else if (view == 'text') {
			updateTextView();
		}
	}
	let gridIsBuilt = false;
	function buildGrid() {
		if (gridIsBuilt) {
			return;
		}
		gridIsBuilt = true;
		const grid = document.getElementById('grid');
		const fragment = document.createDocumentFragment();
		for (const glyphInfo of glyphInfoList) {
			const cell = document.createElement('div');
			cell.className = 'gridCell';
			cell.textContent = glyphInfo.char;
			const tooltip = document.createElement('span');
			tooltip.className = 'tooltip';
			tooltip.textContent = `${glyphInfo.name}  U+${glyphInfo.uni.toUpperCase()}`;
			cell.appendChild(tooltip);
			cell.addEventListener('dblclick', function() {
				openTextInGlyphs(glyphInfo.name ? '/' + glyphInfo.name : glyphInfo.char);
			});
			fragment.appendChild(cell);
		}
		grid.appendChild(fragment);
	}
	function updateGridSize() {
		const size = document.getElementById('gridSize').value;
		document.getElementById('grid').style.fontSize = size + 'px';
		document.documentElement.style.setProperty('--grid-cell-size', Math.round(size * 1.4) + 'px');
	}
	function updateTextView() {
		const size = document.getElementById('textSize').value;
		const lineHeight = document.getElementById('textLineHeight').value;
		const textview = document.getElementById('textview');
		textview.style.fontSize = size + 'px';
		textview.style.lineHeight = (lineHeight / 100) + 'em';
	}
	function updateFeatures() {
		// update features based on user input:
		// first, get feature on/off line:
		var cssCode = "";
		var codeLine = "";
		var checkboxes = document.getElementsByClassName("otFeature")
		for (i = 0; i < checkboxes.length; i++) {
			var checkbox = checkboxes[i];
			codeLine += '"'+checkbox.id+'" ';
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
			} else if (checkbox.name=="case") {
				testtext.style.textTransform = checkbox.checked ? "uppercase" : "none";
			}
		}
		codeLine = codeLine.slice(0, -2)

		// then, apply line for every browser:
		const prefixes = ["","-moz-","-webkit-","-ms-","-o-",];
		const suffix = "font-feature-settings: "
		for (i = 0; i < prefixes.length; i++) {
			var prefix = prefixes[i];
			cssCode += prefix
			cssCode += suffix
			cssCode += codeLine
			cssCode += "; "
		}

		document.getElementById('waterfall').style.cssText = cssCode;
		document.getElementById('grid').style.cssText = cssCode;
		document.getElementById('textview').style.cssText = cssCode;
		changeFont();
		updateGridSize();
		updateTextView();
	}
	function changeFont() {
		var selected_index = selector.selectedIndex;
		var selected_option_text = selector.options[selected_index].text;
		const fontFamily = `'${selected_option_text}'`;
		document.getElementById('waterfall').style.fontFamily = fontFamily;
		document.getElementById('grid').style.fontFamily = fontFamily;
		document.getElementById('textview').style.fontFamily = fontFamily;
	}
	function setDefaultText(defaultText) {
		document.getElementById('textInput').value = decodeEntities(defaultText);
		updateParagraph();
	}
	function setCharset() {
		const completeCharSet = 'The Quick Brown Fox Jumps Over The Lazy Dog.';
		setDefaultText(completeCharSet);
	}
	function decodeEntities(string){
		var elem = document.createElement('div');
		elem.innerHTML = string;
		return elem.textContent;
	}
	function vanish(item) {
		item.style.setProperty("display", "none");
	}
	function toggleLeftRight() {
		const waterfall = document.getElementById("waterfall");
		if (waterfall.dir != "rtl") {
			waterfall.dir = "rtl";
			waterfall.align = "right";
		} else {
			waterfall.dir = "";
			waterfall.align = "";
		}
	}
	function toggleInverse() {
		const testText = document.getElementById("waterfall");
		if (testText) {
			const link = document.getElementById("invert");
			const newClassName = testText.className == "●" ? "○" : "●";
			for (const v of viewOrder) {
				document.getElementById(viewElementIds[v]).className = newClassName;
			}
			link.textContent = newClassName == "○" ? "🔳" : "🔲";
		}
	}
</script>
</body>
"""

# brings macro window to front and clears its log:
Glyphs.clearLog()
# Glyphs.showMacroWindow()

# Query app version:
appVersionHighEnough = Glyphs.versionNumber >= 2

fileFormats = currentFileFormats()
if not appVersionHighEnough:
	print("This script requires Glyphs 2 or higher. Sorry.")
elif not Glyphs.orderedDocuments():
	Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
else:
	firstDoc = Glyphs.orderedDocuments()[0]
	if isinstance(firstDoc, GSProjectDocument):
		# Frontmost doc is a .glyphsproject file:
		thisFont = firstDoc.font()  # type: ignore
		# do not assume woff/woff2: a project only exports the formats
		# specified in its "Webfont Formats" parameter (if any):
		activeFontInstances = activeInstancesOfProjectByFormat(firstDoc)
		exportPath = firstDoc.exportPath()
	else:
		# Frontmost doc is a .glyphs file:
		thisFont = Glyphs.font  # frontmost font
		activeFontInstances = activeInstancesOfFontByFormat(thisFont, fileFormats=fileFormats)
		exportPath = currentWebExportPath()

	familyName = thisFont.familyName

	if not activeFontInstances:
		if Glyphs.versionNumber >= 3:
			# GLYPHS 3
			exports = "Exports"
		else:
			# GLYPHS 2
			exports = "Instances"

		Message(
			title="⚠️ No exporting fonts found",
			message="No active font instances are set in Font Info > %s. Cannot create HTML for %s." % (exports, familyName),
			OKButton=None,
		)
		print("❌ %s: No instances set in Font Info. Aborting." % familyName)
	else:
		print("Preparing Test HTML for:")
		for thisFontInstanceInfo in activeFontInstances:
			print("  %s" % thisFontInstanceInfo[1])

		optionList = optionListForInstances(activeFontInstances)
		fontFacesCSS = fontFaces(activeFontInstances)
		firstFileName = activeFontInstances[0][0]
		firstFontName = activeFontInstances[0][1]

		replacements = (
			("familyName", familyName),
			("nameOfTheFont", firstFontName),
			("The Quick Brown Fox Jumps Over The Lazy Dog.", allUnicodeEscapesOfFont(thisFont)),
			("fileName", firstFileName),
			("		<!-- moreOptions -->\n", optionList),
			("		<!-- moreFeatures -->\n", featureListForFont(thisFont)),
			("		<!-- fontFaces -->\n", fontFacesCSS),
			("<!-- glyphInfoJSON -->", glyphInfoJSONForFont(thisFont)),
			("<!-- fontFaceJSON -->", fontFacesJSONForInstances(activeFontInstances)),
		)

		htmlContent = replaceSet(htmlContent, replacements)

		# Write file to disk:
		if exportPath:
			filepath = thisFont.filepath
			if filepath:
				filename = filepath.lastPathComponent().stringByDeletingDotSuffix()
			else:
				filename = thisFont.familyName
			htmlFileName = f"{filename} fonttest.html"

			if saveFileInLocation(content=htmlContent, fileName=htmlFileName, filePath=exportPath):
				print("Successfully wrote file to disk.")
				system(f'open "{exportPath}"')
				webbrowser.open(f"file://{quote(exportPath)}/{quote(htmlFileName)}")
			else:
				print("Error writing file to disk.")
		else:
			Message(
				title="⚠️ Webfont Test HTML Error",
				message="Could not determine export path. You need to export webfonts first.",
				OKButton=None,
			)
