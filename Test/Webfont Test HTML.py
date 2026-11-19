# MenuTitle: Webfont Test HTML
__doc__ = """
Create a Test HTML for the current font inside the current Webfont Export folder, or for the current Glyphs Project in the project’s export path.
"""

from GlyphsApp import Glyphs, GSProjectDocument, INSTANCETYPESINGLE, Message
from os import system, path
from itertools import product
import codecs
import json
import re
from html import escape
Glyphs.registerDefault("com.mekkablue.WebFontTestHTML.includeEOT", 0)


def saveFileInLocation(content="Sorry, no content generated.", fileName="test.txt", filePath="~/Desktop"):
	saveFileLocation = f"{filePath}/{fileName}"
	saveFileLocation = saveFileLocation.replace("//", "/")
	with codecs.open(saveFileLocation, "w", "utf-8-sig") as thisFile:
		print(f"Exporting to: {thisFile.name}")
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
		if searchFor != replaceWith:
			text = text.replace(searchFor, replaceWith)
	return text


def resolveFamilyNamesPlaceholder(name, thisFont):
	# {{{familyNames}}} is auto-replaced by font.familyName on export
	if name and "{{{familyNames}}}" in name:
		return name.replace("{{{familyNames}}}", thisFont.familyName)
	return name


def allUnicodeEscapesOfFont(thisFont):
	allUnicodes = [f"&#x{g.unicode};" for g in thisFont.allGlyphs() if g.unicode and g.export and g.layers[0].shapes]
	return " ".join(allUnicodes)


# features that cannot be triggered one by one through CSS font-feature-settings, or are not part of aalt:
NON_ALTERNATE_FEATURES = ("aalt", "locl", "ccmp", "rvrn", "rlig", "calt", "rclt")


def glyphNamesOfFeatureItem(text, classes):
	"""Resolves a glyph, a @class or a [glyph @class ...] to a list of glyph names; None if it is a sequence."""
	text = text.strip()
	if text.startswith("[") and text.endswith("]") and text.count("[") == 1:
		tokens = text[1:-1].split()
	elif len(text.split()) == 1:
		tokens = [text]
	else:
		return None
	names = []
	for token in tokens:
		if token.startswith("@"):
			names.extend(classes.get(token[1:], []))
		else:
			names.append(token)
	return names


def alternateEntriesOfFont(thisFont):
	"""
	One-to-one substitutions (single and alternate substitutions, as listed in aalt) from the font's feature code,
	as a list of dicts for the grid view: a base character plus the feature that turns it into the alternate.
	"""
	featureCodes = {}
	featureOrder = []
	for feature in thisFont.features:
		if not getattr(feature, "active", True):
			continue
		featureCodes[feature.name] = re.sub(r"#[^\n]*", "", feature.code or "")
		featureOrder.append(feature.name)

	# a manual aalt dictates the order: feature xxxx;
	aaltTags = re.findall(r"\bfeature\s+(\w{4})\s*;", featureCodes.get("aalt", ""))
	tags = [tag for tag in aaltTags if tag in featureCodes] or [tag for tag in featureOrder if tag not in NON_ALTERNATE_FEATURES]

	# glyph classes from the font, the prefixes and the feature code:
	classes = {}
	classSources = [f"@{c.name} = [{c.code}];" for c in thisFont.classes]
	classSources += [(prefix.code or "") for prefix in thisFont.featurePrefixes]
	classSources += list(featureCodes.values())
	for source in classSources:
		for className, members in re.findall(r"@([\w.]+)\s*=\s*\[([^\]]*)\]\s*;", re.sub(r"#[^\n]*", "", source)):
			classes[className] = glyphNamesOfFeatureItem(f"[{members}]", classes) or []

	entries = []
	seen = set()
	colorIndex = 0
	rulePattern = re.compile(r"\bsub(?:stitute)?\s+([^;]+?)\s+(by|from)\s+([^;]+?)\s*;")
	for tag in tags:
		featureEntries = []
		for sourceText, keyword, targetText in rulePattern.findall(featureCodes[tag]):
			if "'" in sourceText:
				continue  # contextual
			sources = glyphNamesOfFeatureItem(sourceText, classes)
			targets = glyphNamesOfFeatureItem(targetText, classes)
			if not sources or not targets:
				continue
			pairs = []
			if keyword == "from":
				if len(sources) == 1:
					pairs = [(sources[0], target, index + 1) for index, target in enumerate(targets)]
			elif len(targets) == 1:
				pairs = [(source, targets[0], 1) for source in sources]
			elif len(targets) == len(sources):
				pairs = [(source, target, 1) for source, target in zip(sources, targets)]
			for sourceName, targetName, index in pairs:
				key = (tag, sourceName, targetName)
				sourceGlyph = thisFont.glyphs[sourceName]
				targetGlyph = thisFont.glyphs[targetName]
				if key in seen or sourceName == targetName or not sourceGlyph or not targetGlyph:
					continue
				if not sourceGlyph.unicode:
					continue  # can only show alternates of encoded glyphs
				seen.add(key)
				entry = {
					"c": int(sourceGlyph.unicode, 16),
					"u": sourceGlyph.unicode,
					"n": targetName,
					"b": sourceName,
					"f": tag,
					"i": index,
					"k": colorIndex,
				}
				if targetGlyph.category:
					entry["cat"] = targetGlyph.category
				if targetGlyph.subCategory:
					entry["sub"] = targetGlyph.subCategory
				featureEntries.append(entry)
		if featureEntries:
			entries.extend(featureEntries)
			colorIndex += 1
	return entries


def allGlyphInfoOfFont(thisFont):
	# Collect per-glyph info for the grid view (code point + metadata for tooltips).
	glyphInfos = []
	for g in thisFont.allGlyphs():
		if not (g.unicode and g.export and g.layers[0].shapes):
			continue
		entry = {"c": int(g.unicode, 16)}
		entry["u"] = g.unicode
		entry["n"] = g.name
		try:
			glyphInfo = g.glyphInfo
		except:
			glyphInfo = None
		if glyphInfo is not None and glyphInfo.desc:
			entry["d"] = glyphInfo.desc
		if g.category:
			entry["cat"] = g.category
		if g.subCategory:
			entry["sub"] = g.subCategory
		glyphInfos.append(entry)
	glyphInfos.extend(alternateEntriesOfFont(thisFont))
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
		familyName = resolveFamilyNamesPlaceholder(activeInstance.familyName, thisFont)
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
	if "{{{familyNames}}}" in firstPartOfFileName:
		# the file name Glyphs reports still contains the unresolved token and cannot be patched reliably
		# (see Variable Font Test HTML.py), so build it from the resolved names, like the exported file:
		firstPartOfFileName = ""
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
	axisValues being a dict {axisTag: axisValue}. Elidable particles disappear
	when combined with others; if a style consists of elidable particles only,
	the instance name is the fallback.
	"""
	axisTags = []
	particlesPerAxis = []
	# GSInstance.nameParticles is a list of axis groups (one list of particles per axis), parallel to the font's axes:
	for axisGroup, axis in zip(particleInstance.nameParticles, thisFont.axes):
		if not axisGroup:
			continue
		axisTags.append(axis.axisTag)
		particlesPerAxis.append(list(axisGroup))
	if not particlesPerAxis:
		return []

	styles = []
	for particleCombination in product(*particlesPerAxis):
		nameParts = [particle.name for particle in particleCombination if not particle.isElidable()]
		styleName = " ".join(nameParts) if nameParts else particleInstance.name
		axisValues = {}
		for axisTag, particle in zip(axisTags, particleCombination):
			# the sliders work in user space, so use external coordinates (internal as fallback):
			axisValue = particle.external
			if axisValue is None:
				axisValue = particle.internal
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
		returnString += "\t\t@font-face { font-family: '%s'; src: url('%s'); font-display: block; }\n" % (nameOfTheFont, fileName)

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
		return "%s: %s %d" % (tag, "Stylistic Set" if tag.startswith("ss") else "Character Variant", int(tag[2:]))
	return "%s: OpenType feature" % tag


def featureListForFont(thisFont):
	returnString = ""
	featureList = [(f.name, f.notes) for f in thisFont.features if f.name not in ("ccmp", "aalt", "locl", "kern", "calt", "liga", "clig", "rlig", "rclt", "rvrn") and not f.disabled()]
	doneFeatures = []
	for (f, n) in featureList:
		if f not in doneFeatures:  # avoid duplicates
			doneFeatures.append(f)
			tooltipText = featureDescription(f)
			if f.startswith("ss") and n and n.startswith("Name:"):
				# stylistic set name as the second line of the tooltip:
				setName = n.splitlines()[0][5:].strip()
				if setName:
					tooltipText += "\n\u2018%s\u2019" % setName
			returnString += '\t\t<input type="checkbox" name="%s" id="%s" value="%s" class="otFeature" onchange="updateFeatures()"><label for="%s" class="otFeatureLabel" title="%s">%s</label>\n' % (
				f, f, f, f, escape(tooltipText, quote=True).replace("\n", "&#10;"), f
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
			margin-right: 0.15em;
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
			flex: 0 0 auto; /* never squeezed by a tall view: the waterfall is much taller than the window */
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
			box-sizing: border-box; /* width 100% plus padding would be wider than the window, and clip the right edge in RTL */
			border: 0 solid transparent;
			margin: 0;
			padding: 0;
			width: 100%;
			color: black;
			overflow-x: hidden;
			overflow-y: scroll;
			font-family: "nameOfTheFont";
			font-feature-settings: "kern" on, "liga" on, "calt" on, "locl" on;
			-moz-font-feature-settings: "kern" on, "liga" on, "calt" on, "locl" on;
			-webkit-font-feature-settings: "kern" on, "liga" on, "calt" on, "locl" on;
			-ms-font-feature-settings: "kern" on, "liga" on, "calt" on, "locl" on;
			-o-font-feature-settings: "kern" on, "liga" on, "calt" on, "locl" on;
		}
		div, p	{
			padding: 0;
			margin: 0;
		}
		#waterfall p {
			margin-bottom: 0.8em;
			overflow-wrap: break-word;
		}
		.○ .sampletext, .○#textview, .○#grid, .○#metricsLine {
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
		.gridCell {
			cursor: default;
		}
		.gridCell:hover {
			background-color: #eef;
		}
		/* alternates (one-to-one substitutions), alternating colors per OT feature: */
		:root {
			--featA-bg: #e8f6e8; --featA-border: #8fcf8f; --featA-text: #165a1c;
			--featB-bg: #e8f0fb; --featB-border: #8db4e6; --featB-text: #17407a;
		}
		.gridCell.featA { background-color: var(--featA-bg); border-color: var(--featA-border); --tag-text: var(--featA-text); }
		.gridCell.featB { background-color: var(--featB-bg); border-color: var(--featB-border); --tag-text: var(--featB-text); }
		.gridCell.featA:hover, .gridCell.featB:hover { box-shadow: inset 0 0 0 999px rgba(128, 128, 128, 0.15); }
		/* base glyphs that an active OT feature button substitutes: yellow backdrop, alternates stay blue/green */
		.gridCell.featHit { background-color: rgba(255, 215, 0, 0.3); }
		.featTag {
			display: none;
			position: absolute;
			left: 0;
			bottom: -16px;
			width: 100%;
			height: 16px;
			font: 11px/16px sans-serif;
			font-feature-settings: normal;
			text-align: center;
			color: var(--tag-text);
			-webkit-text-stroke: 0;
			-webkit-text-fill-color: var(--tag-text);
			overflow: hidden;
		}
		#grid[data-tags] .gridCell.featA, #grid[data-tags] .gridCell.featB { border-bottom-width: 16px; }
		#grid[data-tags] .featTag { display: block; }
		#gridTooltip {
			display: none;
			position: fixed;
			z-index: 30;
			background: #f6f6f6;
			color: #222;
			border: 1px solid #ccc;
			padding: 0.4em 0.7em;
			border-radius: 0.3em;
			pointer-events: none;
			font: 12px sans-serif;
			line-height: 1.4;
			text-align: center;
			box-shadow: 0 2px 8px rgba(0,0,0,0.3);
		}
		#gridTooltip .refGlyph {
			font-family: "Noto Sans", "Noto Serif", -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
			font-size: 2.5em;
			line-height: 1.1;
		}
		#gridTooltip .tooltipFeature {
			color: #e07b00;
			font-weight: bold;
		}
		#gridTooltip .cellMeta {
			font: 12px sans-serif;
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
		.viewLink.activeView, .emojiButton.on {
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

		/* Footer paragraph: */
		#helptext {
			color: black;
			background-color: #ddd;
			position: fixed;
			bottom: 0;
			padding: 2px;
			width: 100%;
			box-sizing: border-box;
			font: x-small sans-serif;
		}
		#helptext span {
			display: inline-block; /* an item never breaks across lines */
			margin-right: 1.3em; /* plus the space between the items: about 1.6em */
		}

		/* Dark Mode */
		@media (prefers-color-scheme: dark) {
			body {
				background: #333;
			}
			.features, .label, a, body, p, #metricsLine {
				color: white;
			}
			#waterfall, #grid, #textview {
				color: white; /* the light rule is set by id, so it also needs to be overridden by id */
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
			.○ .sampletext, .○#textview, .○#grid, .○#metricsLine {
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
			.gridCell:hover {
				background-color: #223;
			}
			:root {
				--featA-bg: #0e2a12; --featA-border: #2d7a35; --featA-text: #a9e3af;
				--featB-bg: #0d1c33; --featB-border: #2a5fa8; --featB-text: #a8c8f5;
			}
			#gridTooltip {
				background: #333;
				color: white;
				border-color: #333;
			}
			.viewLink.activeView, .emojiButton.on {
				background-color: #555;
			}
			.sliderControls label {
				color: #aaa;
			}
		}
	</style>
</head>
<body onload="document.getElementById('textInput').focus();setCharset();setView('text');preloadFonts();">
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
		<a onclick="setView('grid');" id="viewGrid" class="emojiButton viewLink" title="Grid view of all glyphs, double-click a glyph to edit it in Glyphs – Ctrl-G cycles through the views">🔡</a>
		<a onclick="setView('waterfall');" id="viewWaterfall" class="emojiButton viewLink gapAfter" title="Waterfall view – Ctrl-G cycles through the views">⏬</a>
		<a onclick="toggleMetrics();" id="metrics" class="emojiButton" title="Vertical Metrics view for verifying OS/2.typoAscender and OS/2.typoDescender">↕️</a>
		<a onclick="toggleLeftRight();" id="direction" class="emojiButton" title="Text direction: left to right. Click for right to left – Ctrl-J">➡️</a>
		<a onclick="toggleInverse();" id="invert" class="emojiButton gapAfter" title="Toggle x-ray (outline) display">🔲</a>
		<label><input type="checkbox" name="kern" id="kern" value="kern" class="otFeature" onchange="updateFeatures()" checked><label for="kern" class="otFeatureLabel" title="kern: Kerning">kern</label>
		<label><input type="checkbox" name="liga" id="liga" value="liga" class="otFeature" onchange="updateFeatures()" checked><label for="liga" class="otFeatureLabel" title="liga, clig: Standard ligatures and contextual ligatures">liga/clig</label>
		<label><input type="checkbox" name="calt" id="calt" value="calt" class="otFeature" onchange="updateFeatures()" checked><label for="calt" class="otFeatureLabel" title="calt: Contextual alternates">calt</label>
		<!-- moreFeatures -->
	</p>
	<div class="sliderControls" id="gridControls">
		<label>Size: <input type="range" id="gridSize" min="20" max="300" value="60" oninput="updateGridSize()"></label>
	</div>
	<div class="sliderControls" id="textControls">
		<label>Size: <input type="range" id="textSize" min="10" max="500" value="60" oninput="updateTextView()"></label>
		<label>Line Distance: <input type="range" id="textLineHeight" min="50" max="300" value="120" oninput="updateTextView()"></label>
	</div>
</div>
<div id="metricsLine" class="●"></div>
<div id="waterfall" class="●">
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
	<span>Ctrl-R: reset text</span>
	<span>Ctrl-U: reload fonts</span>
	<span>Ctrl-comma/period: step through fonts</span>
	<span>Ctrl-+/−: size</span>
	<span>Ctrl-1/2: line distance</span>
	<span>Ctrl-G: cycle views</span>
	<span>Ctrl-J: LTR/RTL</span>
	<span>⌘⌥⇧E: edit in Glyphs (or double-click cell)</span>
	<span>Move mouse over this note to make it disappear.</span>
</p>

<script type="text/javascript">
	const selector = document.getElementById("fontFamilySelector");
	const selectorOptions = selector.options;
	const selectorLength = selectorOptions.length;
	const glyphInfoList = <!-- glyphInfoJSON -->;
	const fontFaceList = <!-- fontFaceJSON -->;
	const glyphNameForChar = {};
	for (const glyphInfo of glyphInfoList) {
		const char = String.fromCodePoint(glyphInfo.c);
		if (glyphInfo.n && !glyphInfo.f && !(char in glyphNameForChar)) {  // alternates share the character of their base glyph
			glyphNameForChar[char] = glyphInfo.n;
		}
	}
	const viewOrder = ["text", "grid", "waterfall"];
	const viewElementIds = {waterfall: "waterfall", grid: "grid", text: "textview"};

	document.addEventListener('keyup', keyAnalysis);
	document.addEventListener('keydown', sliderKeys);  // keydown, so that holding the keys keeps stepping

	function stepSlider(sliderId, direction, percentStep) {
		// percentStep: relative step (size), or null for a fixed step of 5 (line distance)
		const slider = document.getElementById(sliderId);
		const value = Number(slider.value);
		const change = percentStep ? Math.max(1, Math.round(value * percentStep)) : 5;
		slider.value = value + direction * change;  // the slider clamps to its minimum and maximum
	}
	function sliderKeys(event) {
		// Ctrl-plus/minus: size, Ctrl-1/2: line distance. Only in the grid and text views.
		if (!event.ctrlKey || event.metaKey || event.altKey) return;
		const view = currentView();
		if (view != 'grid' && view != 'text') return;
		let direction = 0;
		let isSize = false;
		if (['+', '=', 'Add'].includes(event.key) || event.code == 'NumpadAdd') {
			direction = 1; isSize = true;
		} else if (['-', '_', '\u2212', 'Subtract'].includes(event.key) || event.code == 'NumpadSubtract') {
			direction = -1; isSize = true;
		} else if (event.key == '1') {
			direction = -1;
		} else if (event.key == '2') {
			direction = 1;
		} else {
			return;
		}
		if (isSize) {
			stepSlider(view == 'grid' ? 'gridSize' : 'textSize', direction, 0.1);
			if (view == 'grid') updateGridSize(); else updateTextView();
		} else if (view == 'text') {
			stepSlider('textLineHeight', direction, null);  // the grid has no line distance
			updateTextView();
		} else {
			return;
		}
		event.preventDefault();
	}
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
			console.warn('Cannot edit in Glyphs: found no glyphs for', text);
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
		if (gridTooltip) gridTooltip.style.display = 'none';
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
	let gridTooltip = null;
	function ensureGridTooltip() {
		if (!gridTooltip) {
			gridTooltip = document.createElement('div');
			gridTooltip.id = 'gridTooltip';
			document.body.appendChild(gridTooltip);
		}
		return gridTooltip;
	}
	let gridTooltipsEnabled = true;
	function activeFeatureTags() {
		const activeFeatures = new Set();
		for (const checkbox of document.getElementsByClassName("otFeature")) {
			if (checkbox.checked) activeFeatures.add(checkbox.name);
		}
		return activeFeatures;
	}
	function activeFeaturesAffecting(codePoint) {
		// tags of the active feature buttons that substitute this character (in aalt order, without duplicates)
		const activeFeatures = activeFeatureTags();
		const tags = [];
		for (const info of glyphInfoList) {
			if (info.f && info.c === codePoint && activeFeatures.has(info.f) && !tags.includes(info.f)) tags.push(info.f);
		}
		return tags;
	}
	function updateGridHighlights() {
		// yellow backdrop for base glyphs that an active feature button substitutes (one-to-one substitutions
		// known from the alternates); the alternate cells themselves keep their blue/green
		const activeFeatures = activeFeatureTags();
		const affected = new Set();
		for (const info of glyphInfoList) {
			if (info.f && activeFeatures.has(info.f)) affected.add(String(info.c));
		}
		for (const cell of document.getElementById('grid').getElementsByClassName('gridCell')) {
			const isBaseCell = !cell.classList.contains('featA') && !cell.classList.contains('featB');
			cell.classList.toggle('featHit', isBaseCell && affected.has(cell.dataset.cp));
		}
	}
	let gridIsBuilt = false;
	function buildGrid() {
		if (gridIsBuilt) {
			return;
		}
		gridIsBuilt = true;
		const grid = document.getElementById('grid');
		const tooltip = ensureGridTooltip();
		const fragment = document.createDocumentFragment();
		for (const info of glyphInfoList) {
			const ch = String.fromCodePoint(info.c);
			const cell = document.createElement('div');
			cell.className = 'gridCell';
			cell.textContent = ch;
			cell.dataset.cp = info.c;
			if (info.f) {
				// alternate: show the substitution of this feature only, independent of the feature buttons
				cell.classList.add(info.k % 2 == 0 ? 'featA' : 'featB');
				cell.style.setProperty('font-feature-settings', '"' + info.f + '" ' + info.i);
				const tag = document.createElement('span');
				tag.className = 'featTag';
				tag.textContent = info.f;
				cell.appendChild(tag);
			}
			function showTooltip() {
				tooltip.innerHTML = '';
				const refGlyph = document.createElement('div');
				refGlyph.className = 'refGlyph';
				refGlyph.textContent = ch;
				tooltip.appendChild(refGlyph);
				const metaLines = [];
				if (info.f) {
					metaLines.push('Feature: ' + info.f + (info.i > 1 ? ' (alternate ' + info.i + ')' : ''));
					metaLines.push('/' + info.n);
					metaLines.push('Alternate of /' + info.b + ' (U+' + info.u + ')');
				} else {
					metaLines.push('/' + info.n);
					metaLines.push('U+' + info.u);
					const accessTags = activeFeaturesAffecting(info.c);
					if (accessTags.length > 0) metaLines.push({substitutedBy: accessTags});
				}
				if (info.d) metaLines.push(info.d);
				if (info.cat) metaLines.push(info.cat);
				if (info.sub) metaLines.push(info.sub);
				for (const line of metaLines) {
					const l = document.createElement('div');
					l.className = 'cellMeta';
					if (typeof line === 'string') {
						l.textContent = line;
					} else {
						l.appendChild(document.createTextNode('Substituted by '));
						line.substitutedBy.forEach(function(tag, index) {
							if (index > 0) l.appendChild(document.createTextNode(', '));
							const tagSpan = document.createElement('span');
							tagSpan.className = 'tooltipFeature';
							tagSpan.textContent = tag;
							l.appendChild(tagSpan);
						});
					}
					tooltip.appendChild(l);
				}
				tooltip.style.display = 'block';
			}
			cell.addEventListener('mouseenter', function() {
				if (gridTooltipsEnabled) showTooltip();
			});
			cell.addEventListener('click', function(e) {
				// a click toggles the tooltips (on by default)
				gridTooltipsEnabled = !gridTooltipsEnabled;
				if (gridTooltipsEnabled) {
					showTooltip();
					tooltip.style.left = (e.clientX + 14) + 'px';
					tooltip.style.top = (e.clientY + 14) + 'px';
				} else {
					tooltip.style.display = 'none';
				}
			});
			cell.addEventListener('mousemove', function(e) {
				tooltip.style.left = (e.clientX + 14) + 'px';
				tooltip.style.top = (e.clientY + 14) + 'px';
			});
			cell.addEventListener('mouseleave', function() {
				tooltip.style.display = 'none';
			});
			cell.addEventListener('dblclick', function() {
				openTextInGlyphs(info.n ? '/' + info.n : ch);
			});
			fragment.appendChild(cell);
		}
		grid.appendChild(fragment);
		updateGridHighlights();
	}
	function updateGridSize() {
		const size = document.getElementById('gridSize').value;
		document.getElementById('grid').style.fontSize = size + 'px';
		document.documentElement.style.setProperty('--grid-cell-size', Math.round(size * 1.4) + 'px');
		// from 60px on, alternates carry the name of their feature in a thicker bottom border:
		if (size >= 60) {
			document.getElementById('grid').setAttribute('data-tags', '');
		} else {
			document.getElementById('grid').removeAttribute('data-tags');
		}
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
		var textCSS = "";  // only for the text views, not for the grid
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
				textCSS += "text-transform: " + (checkbox.checked ? 'uppercase' : 'none') + '; ';
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

		// cssText replaces all inline styles, including the display of the views and of the metrics line:
		const view = currentView();
		const metricsLine = document.getElementById('metricsLine');
		const metricsDisplay = metricsLine.style.display;
		document.getElementById('waterfall').style.cssText = cssCode + textCSS;
		document.getElementById('grid').style.cssText = cssCode;
		document.getElementById('textview').style.cssText = cssCode + textCSS;
		metricsLine.style.cssText = cssCode + textCSS;
		metricsLine.style.display = metricsDisplay;
		changeFont();
		setView(view);
		updateGridSize();
		updateTextView();
		updateGridHighlights();
	}
	function currentFontFamily() {
		return `'${selector.options[selector.selectedIndex].text}'`;
	}
	function applyFontFamily() {
		const fontFamily = currentFontFamily();
		for (const id of ['waterfall', 'grid', 'textview', 'metricsLine']) {
			document.getElementById(id).style.fontFamily = fontFamily;
		}
	}
	function changeFont() {
		// Fonts load lazily, on first use. Switching the family before the font has loaded shows a fallback font
		// for a moment (flash of unstyled text), so wait for the font, and only then apply it:
		const fontSpec = `1em ${currentFontFamily()}`;
		if (document.fonts.check(fontSpec)) {
			applyFontFamily();
		} else {
			document.fonts.load(fontSpec).then(applyFontFamily, applyFontFamily);
		}
	}
	function preloadFonts() {
		// load all fonts right away, so that stepping through them with Ctrl-comma/period is instant:
		for (const fontFace of fontFaceList) {
			document.fonts.load(`1em '${fontFace.family}'`);
		}
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
	function toggleMetrics() {
		const metricsLine = document.getElementById("metricsLine");
		const showMetrics = metricsLine.style.display != "block";
		updateFeatures();  // gives the line the current font and features (and keeps its display)
		metricsLine.style.display = showMetrics ? "block" : "none";
		document.getElementById("metrics").classList.toggle("on", showMetrics);
	}
	function toggleLeftRight() {
		// the direction applies to all views: text and metrics line run right to left, the grid starts in the top right cell
		const makeRTL = document.getElementById("waterfall").dir != "rtl";
		for (const id of ["waterfall", "grid", "textview", "metricsLine"]) {
			document.getElementById(id).dir = makeRTL ? "rtl" : "ltr";
		}
		const button = document.getElementById("direction");
		button.textContent = makeRTL ? "⬅️" : "➡️";
		button.title = makeRTL ? "Text direction: right to left. Click for left to right – Ctrl-J" : "Text direction: left to right. Click for right to left – Ctrl-J";
	}
	function toggleInverse() {
		const testText = document.getElementById("waterfall");
		if (testText) {
			const link = document.getElementById("invert");
			const newClassName = testText.className == "●" ? "○" : "●";
			for (const v of viewOrder) {
				document.getElementById(viewElementIds[v]).className = newClassName;
			}
			document.getElementById("metricsLine").className = newClassName;
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
		htmlContent = resolveFamilyNamesPlaceholder(htmlContent, thisFont)  # safety net: no {{{familyNames}}} residue anywhere

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
				# webbrowser.open() can raise UnicodeEncodeError on macOS when the
				# osascript pipe defaults to ASCII, so open the file via `open` instead:
				system(f'open "{exportPath}/{htmlFileName}"')
			else:
				print("Error writing file to disk.")
		else:
			Message(
				title="⚠️ Webfont Test HTML Error",
				message="Could not determine export path. You need to export webfonts first.",
				OKButton=None,
			)
