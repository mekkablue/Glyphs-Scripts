# MenuTitle: Variable Font Test HTML
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Create a Test HTML for the current font inside the current Variation Font Export folder. Hold down OPTION and SHIFT while running the script in order to create respective Samsa files in addition to the Test HTML.
"""

from os import system, path
import json
from Cocoa import NSEvent, NSAlternateKeyMask, NSShiftKeyMask
import codecs
from GlyphsApp import Glyphs, GSFont, Message


def langMenu(thisFont, indent=4):
	otTag2Lang = {
		'ABK': ('ab', 'Abkhazian'),
		'AFK': ('af', 'Afrikaans'),
		'AFR': ('aa', 'Afar'),
		'AKA': ('ak', 'Akan'),
		'AMH': ('am', 'Amharic'),
		'ARA': ('ar', 'Arabic'),
		'ARG': ('an', 'Aragonese'),
		'ASM': ('as', 'Assamese'),
		'AVR': ('av', 'Avar'),
		'AYM': ('ay', 'Aymara'),
		'AZE': ('az', 'Azerbaijani'),
		'BEL': ('be', 'Belarussian'),
		'BEN': ('bn', 'Bengali'),
		'BGR': ('bg', 'Bulgarian'),
		'BIS': ('bi', 'Bislama'),
		'BMB': ('bm', 'Bambara (Bamanankan)'),
		'BOS': ('bs', 'Bosnian'),
		'BRE': ('br', 'Breton'),
		'BRM': ('my', 'Burmese'),
		'BSH': ('ba', 'Bashkir'),
		'CAT': ('ca', 'Catalan'),
		'CHA': ('ch', 'Chamorro'),
		'CHE': ('ce', 'Chechen'),
		'CHI': ('ny', 'Chichewa (Chewa, Nyanja)'),
		'CHU': ('cv', 'Chuvash'),
		'COR': ('kw', 'Cornish'),
		'COS': ('co', 'Corsican'),
		'CRE': ('cr', 'Cree'),
		'CSL': ('cu', 'Church Slavonic'),
		'CSY': ('cs', 'Czech'),
		'DAN': ('da', 'Danish'),
		'DEU': ('de', 'German'),
		'DIV': ('dv', 'Divehi (Dhivehi, Maldivian)'),
		'DZN': ('dz', 'Dzongkha'),
		'ELL': ('el', 'Greek'),
		'ENG': ('en', 'English'),
		'ESP': ('es', 'Spanish'),
		'ETI': ('et', 'Estonian'),
		'EUQ': ('eu', 'Basque'),
		'EWE': ('ee', 'Ewe'),
		'FAR': ('fa', 'Persian'),
		'FIN': ('fi', 'Finnish'),
		'FJI': ('fj', 'Fijian'),
		'FOS': ('fo', 'Faroese'),
		'FRA': ('fr', 'French'),
		'FRI': ('fy', 'Frisian'),
		'FUL': ('ff', 'Fulah'),
		'GAE': ('gd', 'Scottish Gaelic (Gaelic)'),
		'GAL': ('gl', 'Galician'),
		'GRN': ('kl', 'Greenlandic'),
		'GUA': ('gn', 'Guarani'),
		'GUJ': ('gu', 'Gujarati'),
		'HAI': ('ht', 'Haitian (Haitian Creole)'),
		'HAU': ('ha', 'Hausa'),
		'HER': ('hz', 'Herero'),
		'HIN': ('hi', 'Hindi'),
		'HMO': ('ho', 'Hiri Motu'),
		'HRV': ('hr', 'Croatian'),
		'HUN': ('hu', 'Hungarian'),
		'HYE0': ('hy', 'Armenian East'),
		'IBO': ('ig', 'Igbo'),
		'IDO': ('io', 'Ido'),
		'ILE': ('ie', 'Interlingue'),
		'INA': ('ia', 'Interlingua'),
		'IND': ('id', 'Indonesian'),
		'INU': ('iu', 'Inuktitut'),
		'IPK': ('ik', 'Inupiat'),
		'IRI': ('ga', 'Irish'),
		'IRT': ('ga', 'Irish Traditional'),
		'ISL': ('is', 'Icelandic'),
		'ITA': ('it', 'Italian'),
		'IWR': ('he', 'Hebrew'),
		'JAN': ('ja', 'Japanese'),
		'JAV': ('jv', 'Javanese'),
		'JII': ('yi', 'Yiddish'),
		'KAN': ('kn', 'Kannada'),
		'KAT': ('ka', 'Georgian'),
		'KAZ': ('kk', 'Kazakh'),
		'KGE': ('ka', 'Khutsuri Georgian'),
		'KHM': ('km', 'Khmer'),
		'KIK': ('ki', 'Kikuyu (Gikuyu)'),
		'KIR': ('ky', 'Kirghiz (Kyrgyz)'),
		'KNR': ('kr', 'Kanuri'),
		'KOM': ('kv', 'Komi'),
		'KON0': ('kg', 'Kongo'),
		'KOR': ('ko', 'Korean'),
		'KSH': ('ks', 'Kashmiri'),
		'KUA': ('kj', 'Kuanyama'),
		'KUR': ('ku', 'Kurdish'),
		'LAO': ('lo', 'Lao'),
		'LAT': ('la', 'Latin'),
		'LIM': ('li', 'Limburgish'),
		'LIN': ('ln', 'Lingala'),
		'LTH': ('lt', 'Lithuanian'),
		'LTZ': ('lb', 'Luxembourgish'),
		'LUB': ('lu', 'Luba-Katanga'),
		'LUG': ('lg', 'Ganda'),
		'LVI': ('lv', 'Latvian'),
		'MAH': ('mh', 'Marshallese'),
		'MAL': ('ml', 'Malayalam'),
		'MAR': ('mr', 'Marathi'),
		'MKD': ('mk', 'Macedonian'),
		'MLG': ('mg', 'Malagasy'),
		'MLR': ('ml', 'Malayalam Reformed'),
		'MLY': ('ms', 'Malay'),
		'MNG': ('mn', 'Mongolian'),
		'MNX': ('gv', 'Manx'),
		'MOL': ('mo', 'Moldavian'),
		'MRI': ('mi', 'Maori'),
		'MTS': ('mt', 'Maltese'),
		'NAU': ('na', 'Nauruan'),
		'NAV': ('nv', 'Navajo'),
		'NDG': ('ng', 'Ndonga'),
		'NEP': ('ne', 'Nepali'),
		'NLD': ('nl', 'Dutch'),
		'NOR': ('nb', 'Norwegian'),
		'NSM': ('se', 'Northern Sami'),
		'NTO': ('eo', 'Esperanto'),
		'NYN': ('nn', 'Norwegian Nynorsk (Nynorsk, Norwegian)'),
		'OCI': ('oc', 'Occitan'),
		'OJB': ('oj', 'Ojibway'),
		'ORI': ('or', 'Odia (formerly Oriya)'),
		'ORO': ('om', 'Oromo'),
		'OSS': ('os', 'Ossetian'),
		'PAL': ('pi', 'Pali'),
		'PAN': ('pa', 'Punjabi'),
		'PAS': ('ps', 'Pashto'),
		'PGR': ('el', 'Polytonic Greek'),
		'PLK': ('pl', 'Polish'),
		'PTG': ('pt', 'Portuguese'),
		'RMS': ('rm', 'Romansh'),
		'ROM': ('ro', 'Romanian'),
		'RUA': ('rw', 'Kinyarwanda'),
		'RUN': ('rn', 'Rundi'),
		'RUS': ('ru', 'Russian'),
		'SAN': ('sa', 'Sanskrit'),
		'SGO': ('sg', 'Sango'),
		'SKY': ('sk', 'Slovak'),
		'SLV': ('sl', 'Slovenian'),
		'SML': ('so', 'Somali'),
		'SMO': ('sm', 'Samoan'),
		'SNA0': ('sn', 'Shona'),
		'SND': ('sd', 'Sindhi'),
		'SNH': ('si', 'Sinhala (Sinhalese)'),
		'SOT': ('st', 'Sotho, Southern'),
		'SQI': ('sq', 'Albanian'),
		'SRB': ('sr', 'Serbian'),
		'SRD': ('sc', 'Sardinian'),
		'SUN': ('su', 'Sundanese'),
		'SVE': ('sv', 'Swedish'),
		'SWK': ('sw', 'Swahili'),
		'SWZ': ('ss', 'Swati'),
		'TAJ': ('tg', 'Tajiki'),
		'TAM': ('ta', 'Tamil'),
		'TAT': ('tt', 'Tatar'),
		'TEL': ('te', 'Telugu'),
		'TGL': ('tl', 'Tagalog'),
		'TGN': ('to', 'Tongan'),
		'TGY': ('ti', 'Tigrinya'),
		'THA': ('th', 'Thai'),
		'THT': ('ty', 'Tahitian'),
		'TIB': ('bo', 'Tibetan'),
		'TKM': ('tk', 'Turkmen'),
		'TNA': ('tn', 'Tswana'),
		'TRK': ('tr', 'Turkish'),
		'TSG': ('ts', 'Tsonga'),
		'TWI': ('ak', 'Twi'),
		'UKR': ('uk', 'Ukrainian'),
		'URD': ('ur', 'Urdu'),
		'UYG': ('ug', 'Uyghur'),
		'UZB': ('uz', 'Uzbek'),
		'VEN': ('ve', 'Venda'),
		'VIT': ('vi', 'Vietnamese'),
		'VOL': ('vo', 'Volapük'),
		'WEL': ('cy', 'Welsh'),
		'WLF': ('wo', 'Wolof'),
		'WLN': ('wa', 'Walloon'),
		'XHS': ('xh', 'Xhosa'),
		'YBA': ('yo', 'Yoruba'),
		'YCR': ('cr', 'Y-Cree'),
		'YIM': ('ii', 'Yi Modern'),
		'ZHA': ('za', 'Zhuang'),
		'ZHH': ('zh', 'Chinese, Hong Kong SAR'),
		'ZHP': ('zh', 'Chinese Phonetic'),
		'ZHS': ('zh', 'Chinese Simplified'),
		'ZHT': ('zh', 'Chinese Traditional'),
		'ZUL': ('zu', 'Zulu'),
	}
	htmlCode = ""
	findWord = "language"
	for thisFeatureCollection in (thisFont.features, thisFont.featurePrefixes):
		for thisFeature in thisFeatureCollection:
			if thisFeature.active:
				for thisLine in thisFeature.code.splitlines():
					if findWord.lower() in thisLine.lower():
						wordsOnLine = thisLine.lower().strip().split()
						try:
							langIndex = wordsOnLine.index(findWord) + 1
							otTag = wordsOnLine[langIndex].strip().replace(";", "").upper()
							if otTag in otTag2Lang.keys():
								isoTag = otTag2Lang[otTag][0]
								naturalName = otTag2Lang[otTag][1]
								newLine = f"\t<option value='{isoTag}'>{naturalName} ({otTag}, {isoTag})</option>\n"
								if newLine not in htmlCode:  # avoid duplicates
									htmlCode += newLine
						except:
							pass
	if htmlCode:
		htmlCode = "\t<option value=''>No Language</option>\n" + htmlCode
		htmlCode = "<select id='lang' name='languages' onchange='setLanguage(this.value);'>\n%s</select>" % htmlCode
		# indent:
		tabs = "\n" + "\t" * indent
		htmlCode = tabs + tabs.join(htmlCode.splitlines())
		return htmlCode
	else:
		return htmlCode


def saveFileInLocation(content="", fileName="test.txt", filePath="~/Desktop"):
	saveFileLocation = f"{filePath}/{fileName}"
	saveFileLocation = saveFileLocation.replace("//", "/")
	with codecs.open(saveFileLocation, "w", "utf-8-sig") as thisFile:
		print(f"Exporting to: {thisFile.name}")
		thisFile.write(content)
		thisFile.close()
	return True


def currentOTVarExportPath(useExportPath=False):
	exportPath = Glyphs.defaults["GSVariableExportPath"] or Glyphs.defaults["GXExportPathManual"]
	if Glyphs.versionNumber and 3 <= Glyphs.versionNumber < 4:
		useExportPath = Glyphs.defaults["GXExportUseExportPath"]
	elif Glyphs.versionNumber and Glyphs.versionNumber < 3:
		useExportPath = Glyphs.defaults["GXPluginUseExportPath"]
	if useExportPath:
		exportPath = Glyphs.defaults["GXExportPath"]
	return exportPath


def otVarFamilyName(thisFont):
	if thisFont.customParameters["Variable Font Family Name"]:
		return thisFont.customParameters["Variable Font Family Name"]
	else:
		return thisFont.familyName


def otVarFullName(thisFont):
	familyName = otVarFamilyName(thisFont)
	styleName = thisFont.customParameters["variableStyleName"]
	if styleName:
		fullName = f"{familyName} {styleName}"
		fullName = fullName.replace("Italic Italic", "Italic")
		fullName = fullName.replace("Roman Roman", "Roman")
		return fullName
	else:
		return familyName


def otVarPlainSuffix():
	if Glyphs.versionNumber and Glyphs.versionNumber >= 4:
		outlineFormat = Glyphs.defaults["GSVariableExportOutlineFormat"]
		return "otf" if outlineFormat == 4 else "ttf"
	return "ttf"


def otVarSuffix():
	if Glyphs.versionNumber and Glyphs.versionNumber >= 4:
		exportWOFF2 = Glyphs.defaults["GSVariableExportWOFF2"]
		exportWOFF = Glyphs.defaults["GSVariableExportWOFF"]
		if exportWOFF2 == 1:
			return "woff2"
		if exportWOFF == 1:
			return "woff"
		return otVarPlainSuffix()
	else:
		suffix = "ttf"
		for webSuffix in ("woff", "woff2"):
			preference = Glyphs.defaults["GXExport%s" % webSuffix.upper()]
			if preference:
				suffix = webSuffix
		return suffix


def otVarFileName(thisFont, thisInstance=None):
	suffix = otVarSuffix()
	if thisInstance is not None:
		try:
			fileName = thisInstance.fileName()
		except TypeError:
			# Glyphs 4: fileName() now requires a format argument
			fileName = thisInstance.fileName(suffix)
		# circumvent bug in Glyphs 3.0.5
		if fileName.endswith(".otf"):
			fileName = fileName[:-4]
		if not fileName:
			fileName = thisInstance.customParameters["fileName"]
			if not fileName:
				familyName = familyNameOfInstance(thisInstance)
				fileName = f"{familyName}-{thisInstance.name}".replace(" ", "")
		return f"{fileName}.{suffix}"
	elif thisFont.customParameters["Variable Font File Name"] or thisFont.customParameters["variableFileName"]:
		fileName = thisFont.customParameters["Variable Font File Name"]
		if not fileName:
			fileName = thisFont.customParameters["variableFileName"]
		return f"{fileName}.{suffix}"
	else:
		familyName = otVarFamilyName(thisFont)
		if Glyphs.versionString >= "3.0.3":
			fileName = f"{familyName}VF.{suffix}"
		else:
			fileName = f"{familyName}GX.{suffix}"
		return fileName.replace(" ", "")


def replaceSet(text, setOfReplacements):
	for thisReplacement in setOfReplacements:
		searchFor = thisReplacement[0]
		replaceWith = thisReplacement[1]
		if searchFor != replaceWith:
			text = text.replace(searchFor, replaceWith)
	return text


def axisDictWithVirtualMastersForFont(thisFont, axisDict):
	# go through *all* virtual masters:
	virtualMasters = [cp for cp in thisFont.customParameters if cp.name == "Virtual Master" and cp.active]
	for virtualMaster in virtualMasters:
		for axis in virtualMaster.value:
			name = axis["Axis"]
			location = int(axis["Location"])
			if name not in axisDict.keys():
				axisDict[name] = {
					"min": location,
					"max": location
				}
				continue
			if location < axisDict[name]["min"]:
				axisDict[name]["min"] = location
			if location > axisDict[name]["max"]:
				axisDict[name]["max"] = location
	return axisDict


def generateAxisDict(thisFont: GSFont):

	axisDict = axisDictWithVirtualMastersForFont(thisFont, {})
	for m in thisFont.allMasters():
		coords = axisLocationOfMasterOrInstance(thisFont, m)
		for axis in thisFont.axes:
			axisName = axis.name
			axisPos = float(coords.get(axis.axisTag, None))
			if axisName not in axisDict:
				axisDict[axisName] = {
					"min": axisPos,
					"max": axisPos,
					"tag": axis.axisTag,
				}
			if axisPos < axisDict[axisName]["min"]:
				axisDict[axisName]["min"] = axisPos
			if axisPos > axisDict[axisName]["max"]:
				axisDict[axisName]["max"] = axisPos
			if "tag" not in axisDict[axisName]:
				axisDict[axisName]["tag"] = axis.axisTag

	return axisDict


def allUnicodeEscapesOfFont(thisFont):
	allUnicodes = [f"&#x{g.unicode};" for g in thisFont.allGlyphs() if g.unicode and g.export and g.layers[0].shapes]
	return " ".join(allUnicodes)


def allGlyphInfosOfFont(thisFont):
	# Collect per-glyph info for the grid view (code point + metadata for tooltips).
	glyphInfos = []
	for g in thisFont.allGlyphs():
		if not (g.unicode and g.export and g.layers[0].shapes):
			continue
		entry = {"c": int(g.unicode, 16)}
		entry["u"] = g.unicode
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
	return json.dumps(glyphInfos, ensure_ascii=False)


featureDescriptions = {
	"aalt": "Access All Alternates",
	"afrc": "Alternative Fractions",
	"c2sc": "Small Capitals From Capitals",
	"calt": "Contextual Alternates",
	"case": "Case-Sensitive Forms",
	"cpsp": "Capital Spacing",
	"cswh": "Contextual Swash",
	"dlig": "Discretionary Ligatures",
	"dnom": "Denominators",
	"expt": "Expert Forms",
	"frac": "Fractions",
	"hist": "Historical Forms",
	"hlig": "Historical Ligatures",
	"kern": "Kerning",
	"liga": "Standard Ligatures",
	"lnum": "Lining Figures",
	"locl": "Localized Forms",
	"numr": "Numerators",
	"onum": "Oldstyle Figures",
	"ordn": "Ordinals",
	"ornm": "Ornaments",
	"pcap": "Petite Capitals",
	"pnum": "Proportional Figures",
	"salt": "Stylistic Alternates",
	"sinf": "Scientific Inferiors",
	"smcp": "Small Capitals",
	"subs": "Subscript",
	"sups": "Superscript",
	"swsh": "Swash",
	"titl": "Titling",
	"tnum": "Tabular Figures",
	"unic": "Unicase",
	"zero": "Slashed Zero",
}


def featureTitle(featureTag):
	description = featureDescriptions.get(featureTag)
	if featureTag.startswith("ss") and featureTag not in featureDescriptions:
		description = "Stylistic Set %s" % featureTag[2:]
	elif featureTag.startswith("cv") and featureTag not in featureDescriptions:
		description = "Character Variant %s" % featureTag[2:]
	if description:
		return "%s (%s)" % (description, featureTag)
	return featureTag


def featureFullName(thisFeature):
	# Prefer the human-readable name Glyphs provides, fall back to our own map.
	try:
		fullName = thisFeature.fullName()
		if fullName:
			return fullName
	except:
		pass
	return featureTitle(thisFeature.name)


def featureListForFont(thisFont):
	returnString = ""
	featureList = [(f.name, f.notes, featureFullName(f)) for f in thisFont.features if f.name not in ("ccmp", "aalt", "locl", "kern", "calt", "liga", "clig", "rlig", "rclt", "rvrn") and not f.disabled()]
	for (f, n, fullName) in featureList:
		# <input type="checkbox" name="kern" id="kern" value="kern" class="otFeature" onchange="updateFeatures()" checked><label for="kern" class="otFeatureLabel">kern</label>
		if f.startswith("ss") and n and n.startswith("Name:"):
			# stylistic set name:
			setName = n.splitlines()[0][5:].strip()
			featureItem = '\t\t\t\t<input type="checkbox" name="%s" id="%s" value="%s" class="otFeature" onchange="updateFeatures()"><label for="%s" class="otFeatureLabel" title="%s">%s<span class="tooltip">%s</span></label>\n' % (
				f, f, f, f, fullName, f, setName
			)
		else:
			# non-ssXX features
			featureItem = '\t\t\t\t<input type="checkbox" name="%s" id="%s" value="%s" class="otFeature" onchange="updateFeatures()"><label for="%s" class="otFeatureLabel" title="%s">%s</label>\n' % (
				f, f, f, f, fullName, f
			)
		if featureItem not in returnString:
			returnString += featureItem
	return returnString.rstrip()


def allOTVarSliders(thisFont, variableFontSetting=None):
	axisDict = generateAxisDict(thisFont)

	minValues, maxValues = {}, {}
	for axis in axisDict.keys():
		tag = axisDict[axis]["tag"]
		minValues[tag] = axisDict[axis]["min"]
		maxValues[tag] = axisDict[axis]["max"]

	html = ""
	for axis in thisFont.axes:
		try:
			# Glyphs 2:
			axisName = unicode(axis["Name"])  # noqa F821
		except:
			# Glyphs 3:
			axisName = axis.name
		minValue = axisDict[axisName]["min"]
		maxValue = axisDict[axisName]["max"]
		axisTag = axisDict[axisName]["tag"]

		startValue = originValueForAxisName(axisName, thisFont, minValue, maxValue, variableFontSetting=variableFontSetting)

		html += "\t\t\t<div class='labeldiv'><label class='sliderlabel' id='label_%s' name='%s'>%s</label><div class='sliderRow'><input type='range' min='%i' max='%i' value='%i' class='slider' id='%s' oninput='updateSlider();'><button class='playBtn' id='play_%s' onclick='toggleAnimation(\"%s\")'>&#9654;</button></div></div>\n" % (
			axisTag, axisName, axisName, minValue, maxValue, startValue, axisTag, axisTag, axisTag
		)

	return html


def originValueForAxisName(axisName, thisFont, minValue, maxValue, variableFontSetting=None):
	originMaster = None
	if variableFontSetting:
		originMaster = originMasterOfInstance(variableFontSetting)
	else:
		originMaster = originMasterOfFont(thisFont)
	if not originMaster:
		return minValue

	axisLocationDict = originMaster.customParameters["Axis Location"]
	if not axisLocationDict:
		return minValue

	for axisDict in axisLocationDict:
		if axisName == axisDict["Axis"]:
			axisLoc = int(axisDict["Location"])
			return axisLoc

	return minValue


def warningMessage():
	Message(
		title="Out of Date Warning",
		message="It appears that you are not running the latest version of Glyphs. Please enable Cutting Edge Versions and Automatic Version Checks in Settings > Updates, and update to the latest beta.",
		OKButton=None
	)


def axisValuesForMaster(thisMaster):
	try:
		try:
			# GLYPHS 3
			font = thisMaster.font
			axisValueList = []
			for axis in font.axes:
				axisValue = thisMaster.axisValueValueForId_(axis.axisId)
				axisValueList.append(axisValue)
		except:
			# GLYPHS 2
			axisValueList = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
			for i, value in enumerate(thisMaster.axes):
				axisValueList[i] = value

		axisValues = tuple(axisValueList)
	except:
		# GLYPHS 2 older versions
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
			# Glyphs 3:
			tag = axis.axisTag
		except:
			# Glyphs 2:
			tag = axis["Tag"]
		value = axisValues[i]
		cssValue = f'"{tag}" {value}'
		defaultValues.append(cssValue)

	return ", ".join(defaultValues)


def buildHTML(fullName, fileName, unicodeEscapes, otVarSliders, variationCSS, featureList, styleMenu, fontLangMenu, shouldCreateSamsa=False, defaultSize=None, glyphInfos="[]", plainSuffix="ttf"):
	samsaPlaceholder = "<!-- placeholder for external links, hold down OPTION and SHIFT while running the script -->"
	htmlContent = """<html>
	<!--<base href="..">--> <!-- uncomment for keeping the HTML in a subfolder -->
	<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
	<meta http-equiv="Content-type" content="text/html; charset=utf-8" />
	<meta http-equiv="X-UA-Compatible" content="IE=9" />
	<head>
		<title>OTVar Test: ###fontFamilyNameWithSpaces###</title>
		<style id="font-declaration">
			@font-face {
				font-family: "###fontFamilyName###";
				src: url("###fontFileName###");
			}
		</style>
		<style>
			body {
				padding: 0;
				margin: auto;
				overflow-x: hidden;
			}
			#flexbox {
				display: flex;
				flex-flow: column;
				height: 100%%;
			}
			#controls {
				flex: 0 1 auto;
				background-color: white;
				margin: 2px 0 0 0;
				padding: 0;
				width: 100%%;
				border: 0px solid transparent;
				height: auto;
				user-select: none;
				-moz-user-select: none;
				-webkit-user-select: none;
			}

/* OTVar Sliders: */
			.labeldiv {
				width: 49.2%%;
				padding: 0 0 0 0.2%%;
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
				width: 100%%;
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

/* Slider play button: */
			.sliderRow {
				display: flex;
				align-items: stretch;
			}
			.sliderRow .slider {
				flex: 1;
				min-width: 0;
			}
			.playBtn {
				flex: 0 0 auto;
				background: #eee;
				border: none;
				cursor: pointer;
				width: 2em;
				font-size: 0.85em;
				border-radius: 0 5px 5px 0;
				color: #555;
				padding: 0;
				user-select: none;
				-webkit-user-select: none;
			}
			.playBtn:hover { background: #ccc; }

/* Feature Buttons: */
			#featureControls {
				font-size: x-small;
				font-family: sans-serif;
				padding: 0 0.2%%;
			}
			#featureControls .emojiButton {
				vertical-align: -50%%;
				font-size: small;
			}
			.emojiButton {
				cursor: pointer;
				text-decoration: none;
				display: inline-block;
				margin: 0 .04em;
			}
			.otFeatureLabel, .otFeature {
				font-size: small;
				position: relative;
				opacity: 1;
				pointer-events: auto;
				white-space: nowrap;
			}
			.otFeatureLabel, select {
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
			select {
				position: relative;
				margin: 0.25em 0.15em;
				height: 2.1em;
				font: x-small sans-serif;
				vertical-align: top;
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
				width: 100%%;
				color: black;
				font: ###defaultSize###px "###fontFamilyName###";
				font-feature-settings: "kern" on, "liga" on, "calt" on, "locl" on;
				-moz-font-feature-settings: "kern" on, "liga" on, "calt" on, "locl" on;
				-webkit-font-feature-settings: "kern" on, "liga" on, "calt" on, "locl" on;
				-ms-font-feature-settings: "kern" on, "liga" on, "calt" on, "locl" on;
				-o-font-feature-settings: "kern" on, "liga" on, "calt" on, "locl" on;
				font-variation-settings: ###variationSettings###;
				overflow-x: hidden;
				overflow-y: scroll;
				word-wrap: break-word;
			}
			.○ {
				-webkit-text-stroke: 1px black;
				-webkit-text-fill-color: #FFF0;
			}
			div:focus {
				outline: 0px solid transparent;
			}

/* Grid View: */
			#gridview {
				flex: 1 1 auto;
				flex-wrap: wrap;
				align-content: flex-start;
				overflow-y: scroll;
				padding: 0.2em;
				font-family: "###fontFamilyName###";
				font-feature-settings: "kern" on, "liga" on, "calt" on, "locl" on;
				-moz-font-feature-settings: "kern" on, "liga" on, "calt" on, "locl" on;
				-webkit-font-feature-settings: "kern" on, "liga" on, "calt" on, "locl" on;
				font-size: ###defaultSize###px;
				font-variation-settings: ###variationSettings###;
				color: black;
			}
			.gridCell {
				display: inline-flex;
				justify-content: center;
				align-items: center;
				box-sizing: border-box;
				flex: 0 0 auto;
				width: var(--grid-cell-size, 56px);
				height: var(--grid-cell-size, 56px);
				border: 1px solid #eee;
				line-height: 1;
				cursor: default;
			}
			.gridCell:hover {
				background: #eef;
			}
			#gridTooltip {
				display: none;
				position: fixed;
				z-index: 30;
				background: #333;
				color: white;
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
				font-variation-settings: normal;
			}
			#gridTooltip .cellMeta {
				font: 12px sans-serif;
			}

/* Footer paragraph: */
			#helptext {
				position: fixed;
				background: transparent;
				bottom: 0;
				width: 100%%;
				color: #888;
				font: x-small sans-serif;
			}
			a {
				color: #333;
			}

/* Print: */
			@media print {
				#helptext, #helptext *,
				#controls, #controls *,
				#featureControls,
				#styleMenu, #styleMenu *,
				.otFeature,
				#gridview, #gridview * {
					display: none !important;
				}
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
				.playBtn { background: #333; color: #aaa; }
				.playBtn:hover { background: #555; }

				#controls {
					background-color: black;
				}
				#textarea {
					color: white;
					background-color: black;
				}
				#gridview {
					color: white;
					background-color: black;
				}
				.gridCell { border-color: #333; }
				.gridCell:hover { background: #223; }
				.○ {
					-webkit-text-stroke: 1px white;
					-webkit-text-fill-color: #0000;
				}
			}

		</style>
		<script>
			document.addEventListener('keyup', keyAnalysis);
			document.addEventListener('keyup', sliderPrecision);
			document.addEventListener('keydown', sliderPrecision);

			const sliders = document.getElementsByClassName('slider');
			const glyphInfos = ###glyphInfos###;
			const plainFormat = {label: "###plainLabel###", suffix: "###plainSuffix###"};

			const animStates = {};
			const animFreq = [0, 1/2.1, 1/1.3, 1/0.8]; // cycles/second for speeds 0-3
			function setAxisSpeed(axisTag, newSpeed) {
				if (!animStates[axisTag]) {
					animStates[axisTag] = {speed: 0, animId: null, startTime: 0, phaseOffset: 0};
				}
				const state = animStates[axisTag];
				const now = performance.now();
				let currentPhase;
				if (state.speed > 0) {
					const t = (now - state.startTime) / 1000;
					currentPhase = 2 * Math.PI * animFreq[state.speed] * t + state.phaseOffset;
				} else {
					const slider = document.getElementById(axisTag);
					const minV = parseFloat(slider.min), maxV = parseFloat(slider.max);
					const center = (minV + maxV) / 2, amplitude = (maxV - minV) / 2;
					const ratio = amplitude > 0 ? (parseFloat(slider.value) - center) / amplitude : 0;
					currentPhase = Math.acos(Math.max(-1, Math.min(1, ratio)));
				}
				if (state.animId) { cancelAnimationFrame(state.animId); state.animId = null; }
				state.speed = newSpeed;
				const btn = document.getElementById('play_' + axisTag);
				const symbols = ['▶', '①', '②', '③'];
				if (btn) btn.textContent = symbols[state.speed];
				if (state.speed === 0) { updatePlayAllButton(); return; }
				state.startTime = now;
				state.phaseOffset = currentPhase;
				function animFrame(time) {
					const s = animStates[axisTag];
					if (!s || s.speed === 0) return;
					const slider = document.getElementById(axisTag);
					const minV = parseFloat(slider.min), maxV = parseFloat(slider.max);
					const center = (minV + maxV) / 2, amplitude = (maxV - minV) / 2;
					const t = (time - s.startTime) / 1000;
					slider.value = center + amplitude * Math.cos(s.phaseOffset + 2 * Math.PI * animFreq[s.speed] * t);
					updateSlider();
					s.animId = requestAnimationFrame(animFrame);
				}
				state.animId = requestAnimationFrame(animFrame);
				updatePlayAllButton();
			}
			function toggleAnimation(axisTag) {
				const current = animStates[axisTag] ? animStates[axisTag].speed : 0;
				setAxisSpeed(axisTag, (current + 1) %% 4);
			}
			function pauseAllAnimations() {
				for (const axisTag in animStates) {
					const state = animStates[axisTag];
					if (state.speed > 0) {
						if (state.animId) { cancelAnimationFrame(state.animId); state.animId = null; }
						state.speed = 0;
						const btn = document.getElementById('play_' + axisTag);
						if (btn) btn.textContent = '▶';
					}
				}
				updatePlayAllButton();
			}
			function anyAxisAnimating() {
				for (const axisTag in animStates) {
					if (animStates[axisTag].speed > 0) return true;
				}
				return false;
			}
			function updatePlayAllButton() {
				const btn = document.getElementById('playAll');
				if (btn) btn.textContent = anyAxisAnimating() ? '⏸️' : '▶️';
			}
			function playAllAxes() {
				// speeds cycle 1,2,3,1,2,3,… so multiple axes cover more of the design space
				const btns = document.getElementsByClassName('playBtn');
				for (let i = 0; i < btns.length; i++) {
					const axisTag = btns[i].id.substring(5); // strip "play_"
					setAxisSpeed(axisTag, (i %% 3) + 1);
				}
			}
			function togglePlayAll() {
				if (anyAxisAnimating()) {
					pauseAllAnimations();
				} else {
					playAllAxes();
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
			function buildGridView() {
				const grid = document.getElementById('gridview');
				grid.innerHTML = '';
				const tooltip = ensureGridTooltip();
				for (const info of glyphInfos) {
					const ch = String.fromCodePoint(info.c);
					const cell = document.createElement('div');
					cell.className = 'gridCell';
					cell.textContent = ch;
					cell.addEventListener('mouseenter', function() {
						tooltip.innerHTML = '';
						const refGlyph = document.createElement('div');
						refGlyph.className = 'refGlyph';
						refGlyph.textContent = ch;
						tooltip.appendChild(refGlyph);
						const metaLines = [];
						if (info.u) metaLines.push('U+' + info.u);
						if (info.d) metaLines.push(info.d);
						if (info.cat) metaLines.push(info.cat);
						if (info.sub) metaLines.push(info.sub);
						for (const line of metaLines) {
							const l = document.createElement('div');
							l.className = 'cellMeta';
							l.textContent = line;
							tooltip.appendChild(l);
						}
						tooltip.style.display = 'block';
					});
					cell.addEventListener('mousemove', function(e) {
						tooltip.style.left = (e.clientX + 14) + 'px';
						tooltip.style.top = (e.clientY + 14) + 'px';
					});
					cell.addEventListener('mouseleave', function() {
						tooltip.style.display = 'none';
					});
					grid.appendChild(cell);
				}
			}
			function toggleGridView() {
				const textarea = document.getElementById('textarea');
				const gridview = document.getElementById('gridview');
				const gridToggle = document.getElementById('gridToggle');
				if (gridview.style.display === 'flex') {
					gridview.style.display = 'none';
					if (gridTooltip) gridTooltip.style.display = 'none';
					textarea.style.display = '';
					textarea.focus();
					if (gridToggle) gridToggle.textContent = '🔡';
				} else {
					buildGridView();
					updateSlider();
					gridview.style.display = 'flex';
					textarea.style.display = 'none';
					if (gridToggle) gridToggle.textContent = '🔤';
				}
			}

			function sliderPrecision(event) {
				if (event.shiftKey) {
					for (i = 0; i < sliders.length; i++) {
						sliders[i].step = 0.005;
					}
				} else {
					for (i = 0; i < sliders.length; i++) {
						if (sliders[i].id == "ital") {
							sliders[i].step = 0.05;
						} else {
							sliders[i].step = 1;
						}
					}
				}
			}
			function version() {
				let version = new Date().getTime();
				return version;
			}
			function currentSuffix() {
				const link = document.getElementById("type");
				if (link.textContent == "W1") return "woff";
				if (link.textContent == "W2") return "woff2";
				return plainFormat.suffix;
			}
			function reloadFontFace() {
				let fontFace = new FontFace("###fontFamilyName###", `url('###fontFileNameWithoutSuffix###.${currentSuffix()}?v=${version()}')`);
				fontFace.load().then(function(loadedFontFace) {
					document.fonts.add(loadedFontFace);
					console.log('Font reloaded');
				}).catch(function(error) {
					console.error('Failed to reload font:', error);
				});
			}
			function keyAnalysis(event) {
				const sizeSlider = document.getElementById("fontsize");
				const lineheightSlider = document.getElementById("lineheight");
				const styleMenu = document.getElementById("styleMenu");
				const styleMenuLength = styleMenu.options.length;

				if (event.ctrlKey) {
					if (event.code == 'KeyR') {
						resetParagraph();
					} else if (event.code == 'KeyU') {
						reloadFontFace();
					} else if (event.code == 'KeyL') {
						setLat1();
					} else if (event.code == 'KeyJ') {
						toggleLeftRight();
					} else if (event.code == 'KeyX') {
						toggleInverse();
					} else if (event.code == 'KeyC') {
						toggleCenter();
					} else if (event.code == 'KeyM') {
						toggleMenu();
					} else if (event.code == 'KeyG') {
						toggleGridView();
					} else if (event.code == 'KeyP') {
						togglePlayAll();
					} else if (event.code == 'Period') {
						styleMenu.selectedIndex = (styleMenu.selectedIndex + 1) %% styleMenuLength;
						setStyle(styleMenu.value);
					} else if (event.code == 'Comma') {
						var newIndex = styleMenu.selectedIndex - 1;
						if (newIndex<0) {
							newIndex = styleMenuLength - 1;
						}
						styleMenu.selectedIndex = newIndex;
						setStyle(styleMenu.value);
					} else if (event.key == '+') {
						sizeSlider.value = Math.round(sizeSlider.value*1.25);
						if (sizeSlider.value > parseInt(sizeSlider.max)) {
							sizeSlider.value = sizeSlider.max;
						}
						updateSlider();
					} else if (event.key == '-') {
						sizeSlider.value = Math.round(sizeSlider.value*0.8);
						if (sizeSlider.value < parseInt(sizeSlider.min)) {
							sizeSlider.value = sizeSlider.min;
						}
						updateSlider();
					} else if (event.key == '1') {
						lineheightSlider.value = Math.round(parseInt(lineheightSlider.value)-20);
						if (lineheightSlider.value < parseInt(lineheightSlider.min)) {
							lineheightSlider.value = lineheightSlider.min;
						}
						updateSlider();
					} else if (event.key == '2') {
						lineheightSlider.value = Math.round(parseInt(lineheightSlider.value)+20);
						if (lineheightSlider.value > parseInt(lineheightSlider.max)) {
							lineheightSlider.value = lineheightSlider.max;
						}
						updateSlider();
					}
				}
			}
			function setLanguage(lang) {
				document.body.setAttribute('lang',lang);
			}
			function updateFeatures() {
				// update features based on user input:
				var testtext = getTestText();
				var codeLine = "";
				var checkboxes = document.getElementsByClassName("otFeature")
				for (i = 0; i < checkboxes.length; i++) {
					var checkbox = checkboxes[i];
					if (i != 0) { codeLine += ", " };
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
					} else if (checkbox.name=="case") {
						testtext.style.textTransform = checkbox.checked ? "uppercase" : "none";
					}
				}
				testtext.style.setProperty("font-feature-settings", codeLine);
				document.getElementById("gridview").style.setProperty("font-feature-settings", codeLine);
			}
			function resetParagraph() {
				const defaulttext = "The Quick Brown Fox Jumps Over the Lazy Dog.";
				const testtext = getTestText();
				testtext.innerHTML = defaulttext;
			}
			function setLat1() {
				const lat1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz &Agrave;&Aacute;&Acirc;&Atilde;&Auml;&Aring;&AElig;&Ccedil;&Egrave;&Eacute;&Ecirc;&Euml;&Igrave;&Iacute;&Icirc;&Iuml;&ETH;&Ntilde;&Ograve;&Oacute;&Ocirc;&Otilde;&Ouml;&Oslash;&OElig;&THORN;&Ugrave;&Uacute;&Ucirc;&Uuml;&Yacute;&Yuml; &agrave;&aacute;&acirc;&atilde;&auml;&aring;&aelig;&ccedil;&egrave;&eacute;&ecirc;&euml;&igrave;&iacute;&icirc;&iuml;&eth;&ntilde;&ograve;&oacute;&ocirc;&otilde;&ouml;&oslash;&oelig;&thorn;&szlig;&ugrave;&uacute;&ucirc;&uuml;&yacute;&yuml; .,:;&middot;&hellip;&iquest;?&iexcl;!&laquo;&raquo;&lsaquo;&rsaquo; /|&brvbar;\\()[]{}_-&ndash;&mdash;&sbquo;&bdquo;&lsquo;&rsquo;&ldquo;&rdquo;&quot;&#x27; #&amp;&sect;@&bull;&shy;*&dagger;&Dagger;&para; +&times;&divide;&plusmn;=&lt;&gt;&not;&mu; ^~&acute;`&circ;&macr;&tilde;&uml;&cedil; &yen;&euro;&pound;$&cent;&curren;&fnof; &trade;&reg;&copy; 1234567890 &ordf;&ordm;&deg;%%&permil; &sup1;&sup2;&sup3;&frac14;&frac12;&frac34;";
				const testtext = getTestText();
				testtext.innerHTML = lat1;
			}
			function getTestText() {
				return document.getElementById("textarea");
			}
			function updateSlider() {
				var body = getTestText();
				var gridview = document.getElementById("gridview");
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
						gridview.style.setProperty("font-size", ""+sliderValue+"px");
						document.documentElement.style.setProperty('--grid-cell-size', Math.round(parseFloat(sliderValue) * 1.4) + 'px');
						label.textContent += "px";
					} else if (sliderID == "lineheight") {
						// Line Height Slider
						body.style.setProperty("line-height", ""+sliderValue/100.0+"em");
						label.textContent += "%%";
					} else {
						// OTVar Slider: collect settings
						if (settingtext != "") { settingtext += ", " };
						settingtext += '"' + sliderID + '" ' + sliderValue;
					}
				}
				// apply OTVar slider settings:
				body.style.setProperty("font-variation-settings", settingtext);
				gridview.style.setProperty("font-variation-settings", settingtext);
			}
			function vanish(item) {
				item.style.setProperty("display", "none");
			}
			function toggleLeftRight() {
				const waterfall = document.getElementById("textarea");
				if (waterfall.dir != "rtl") {
					waterfall.dir = "rtl";
					waterfall.align = "right";
				} else {
					waterfall.dir = "";
					waterfall.align = "";
				}
			}
			function toggleCenter() {
				const waterfall = document.getElementById("textarea");
				if (waterfall.align != "center") {
					waterfall.align = "center";
				} else {
					if (waterfall.dir == "rtl") {
						waterfall.align = "right";
					} else {
						waterfall.align = "left";
					}
				}
			}
			function toggleInverse() {
				const testText = document.getElementById("textarea");
				const gridview = document.getElementById("gridview");
				if (testText) {
					const link = document.getElementById("invert");
					if (testText.className == "●") {
						testText.className = "○";
						if (gridview) gridview.className = "○";
						link.textContent = "🔳";
					} else {
						testText.className = "●";
						if (gridview) gridview.className = "●";
						link.textContent = "🔲";
					}
				}
			}
			function toggleMenu() {
				const menu = document.getElementById("featureControls");
				menu.hidden = !menu.hidden;
			}
			function setFontTypeTo(suffix) {
				const styleId = "font-declaration";
				var fontStyleSheet = document.getElementById(styleId);
				var newFontStyleSheet = document.createElement("style");
				newFontStyleSheet.id = styleId;
				newFontStyleSheet.textContent = `
				@font-face {
					font-family: "###fontFamilyName###";
					src: url("###fontFileNameWithoutSuffix###.${suffix}");
				}`;
				fontStyleSheet.replaceWith(newFontStyleSheet);
			}
			function toggleType() {
				const link = document.getElementById("type");
				if (link.textContent == plainFormat.label) {
					link.textContent = "W1";
					setFontTypeTo("woff");
				} else if (link.textContent == "W1") {
					link.textContent = "W2";
					setFontTypeTo("woff2");
				} else {
					link.textContent = plainFormat.label;
					setFontTypeTo(plainFormat.suffix);
				}
			}
			function setStyle(styleString) {
				const axisStrings = styleString.split(",");
				for (var i = axisStrings.length - 1; i >= 0; i--) {
					const axisSetting = axisStrings[i].split(":");
					const axisTag = axisSetting[0];
					const axisValue = parseInt(axisSetting[1]);
					document.getElementById(axisTag).value=axisValue;
					updateSlider();
				}
			}
		</script>
	</head>
	<body onload="updateSlider();resetParagraph();document.getElementById('textarea').focus()">
	<div id="flexbox">
		<div id="controls">
			<!-- OTVar sliders -->
			<div class="labeldiv"><label class="sliderlabel" id="label_fontsize" name="Font Size">Font Size</label><input type="range" min="10" max="1000" value="###defaultSize###" class="slider" id="fontsize" oninput="updateSlider();"></div>
			<div class="labeldiv"><label class="sliderlabel" id="label_lineheight" name="Line Height">Line Height</label><input type="range" min="30" max="300" value="120" class="slider" id="lineheight" oninput="updateSlider();"></div>
###sliders###
			<div id="featureControls">
			<!-- style menu -->
###styleMenu###

			<!-- file type -->
				<a onclick="toggleType();" id="type" class="emojiButton" title="Switch font format (TTF/OTF, WOFF, WOFF2)">###TTW1W2###</a>
				<a onclick="reloadFontFace();" id="reload" class="emojiButton" title="Reload the font from disk (Ctrl-U)">🔄</a>
				<a onclick="toggleGridView();" id="gridToggle" class="emojiButton" title="Toggle grid view of all glyphs (Ctrl-G)">🔡</a>
				<a onclick="togglePlayAll();" id="playAll" class="emojiButton" title="Animate all axes / pause (Ctrl-P)">▶️</a>

			<!-- Samsa -->
				%s

			<!-- display type (x-ray vs. filled) -->
				<a onclick="toggleInverse();" id="invert" class="emojiButton" title="Toggle x-ray (outline) display (Ctrl-X)">🔲</a>

			<!-- OT features -->
				<input type="checkbox" name="kern" id="kern" value="kern" class="otFeature" onchange="updateFeatures()" checked><label for="kern" class="otFeatureLabel" title="Kerning (kern)">kern</label>
				<input type="checkbox" name="liga" id="liga" value="liga" class="otFeature" onchange="updateFeatures()" checked><label for="liga" class="otFeatureLabel" title="Standard Ligatures (liga)">liga</label>
				<input type="checkbox" name="calt" id="calt" value="calt" class="otFeature" onchange="updateFeatures()" checked><label for="calt" class="otFeatureLabel" title="Contextual Alternates (calt)">calt</label>
###featureList###
###languageSelection###
			</div>
		</div>

		<!-- Test Text -->
		<div contenteditable="true" spellcheck="false" autocomplete="true" id="textarea" class="●">
		</div>

		<!-- Grid View -->
		<div id="gridview" style="display:none;">
		</div>
	</div>

	<!-- Disclaimer -->
	<p id="helptext" onmouseleave="vanish(this);">
		<strong>Ctrl-period/comma</strong> step through styles <strong>Ctrl-R</strong> reset charset <strong>Ctrl-U</strong> update font <strong>Ctrl-L</strong> Lat-1 <strong>Ctrl-J</strong> LTR/RTL <strong>Ctrl-C</strong> center <strong>Ctrl-G</strong> grid view <strong>Ctrl-P</strong> play/pause all <strong>Ctrl-M</strong> toggle menu <strong>Ctrl-X</strong> x-ray <strong>Ctrl +/−</strong> size <strong>Ctrl-1/2</strong> linegap <strong>Shift</strong> high slider precision <em>Not working? Try newer macOS or <a href="https://www.google.com/chrome/">latest Chrome</a>. Hover mouse above this note to make it disappear.</em>
	</p>
	</body>
</html>
""" % (samsaPlaceholder)

	if shouldCreateSamsa:
		samsaReplaceWith = "<a href='samsa-gui.html' class='emojiButton' style='color:rgb(255, 165, 0);' title='Open in Samsa font inspector'>🪲</a>"
	else:
		samsaReplaceWith = samsaPlaceholder

	typeAppreviations = {
		"otf": "OT",
		"ttf": "TT",
		"woff": "W1",
		"woff2": "W2",
	}
	fileTypeAbbreviation = typeAppreviations[fileName.split(".")[-1]]
	# the plain (non-web) format keeps its own label, otherwise the toggle
	# gets stuck cycling W1/W2 when the export file itself is a woff/woff2:
	plainLabel = typeAppreviations.get(plainSuffix, "TT")

	if not defaultSize:
		defaultSize = "40"
		textLength = len(unicodeEscapes) / 7
		if textLength < 10:
			defaultSize = "400"
		elif textLength < 30:
			defaultSize = "350"
		elif textLength < 50:
			defaultSize = "300"
		elif textLength < 100:
			defaultSize = "200"
		elif textLength < 200:
			defaultSize = "100"

	replacements = (
		("###fontFamilyNameWithSpaces###", fullName),
		("###fontFamilyName###", fullName),
		("The Quick Brown Fox Jumps Over the Lazy Dog.", unicodeEscapes),
		("###sliders###", otVarSliders),
		("###styleMenu###", styleMenu),
		("###variationSettings###", variationCSS),
		("###fontFileName###", fileName),
		("###fontFileNameWithoutSuffix###", ".".join(fileName.split(".")[:-1])),
		("###TTW1W2###", fileTypeAbbreviation),
		("###featureList###", featureList),
		("###languageSelection###", fontLangMenu),
		(samsaPlaceholder, samsaReplaceWith),
		("###defaultSize###", defaultSize),
		("###glyphInfos###", glyphInfos),
		("###plainSuffix###", plainSuffix),
		("###plainLabel###", plainLabel),
	)
	htmlContent = replaceSet(htmlContent, replacements)
	return htmlContent


def originMasterOfFont(thisFont):
	originMaster = thisFont.masters[0]
	originParameter = thisFont.customParameters["Variable Font Origin"]
	if originParameter and thisFont.masters[originParameter]:
		originMaster = thisFont.masters[originParameter]
	return originMaster


def originMasterOfInstance(thisVariableFontSetting):
	thisFont = thisVariableFontSetting.font
	originMaster = thisFont.masters[0]
	originParameter = thisVariableFontSetting.customParameters["Variable Font Origin"]
	if originParameter and thisFont.masters[originParameter]:
		originMaster = thisFont.masters[originParameter]
	return originMaster


def axisLocationOfMasterOrInstance(thisFont, masterOrInstance):
	"""
	Returns dict of axisTag:locationValue, e.g.: {'wght':400,'wdth':100}
	"""
	locDict = {}
	axisLocationParameter = masterOrInstance.customParameters["Axis Location"]
	for axisIndex, thisAxis in enumerate(thisFont.axes):
		axisTag = thisAxis.axisTag
		axisValue = None
		if axisLocationParameter:
			axisName = thisAxis.name
			for axisRecord in axisLocationParameter:
				if axisRecord["Axis"] == axisName:
					axisValue = axisRecord["Location"]
		if axisValue is None:
			axisValue = masterOrInstance.axes[axisIndex]

		assert axisValue is not None, f"No axis value found for axis: {axisTag} in master: {masterOrInstance.name}"

		locDict[axisTag] = axisValue

	return locDict


def instanceIsActive(instance):
	if Glyphs.buildNumber > 3198:
		return instance.exports
	else:
		return instance.active


def listOfAllStyles(thisFont):
	tabbing = "\t" * 3
	htmlSnippet = f"{tabbing}<select id='styleMenu' name='styleMenu' onchange='setStyle(this.value);'>"

	# add origin value
	styleMenuEntries = [originMasterOfFont(thisFont)] + [i for i in thisFont.instances if instanceIsActive(i) and i.type == 0]

	for idx, masterOrInstance in enumerate(styleMenuEntries):
		# determine name of menu entry:
		if idx == 0:
			styleName = "Origin"
		else:
			styleName = masterOrInstance.name
			if hasattr(masterOrInstance, "variableStyleName") and masterOrInstance.variableStyleName is not None:
				styleName = masterOrInstance.variableStyleName
			elif masterOrInstance.preferredSubfamilyName:
				styleName = masterOrInstance.preferredSubfamilyName

		# determine location:
		coords = axisLocationOfMasterOrInstance(thisFont, masterOrInstance)
		styleValues = []
		for axis in thisFont.axes:
			axisTag = axis.axisTag
			axisValue = coords[axisTag]
			styleValues.append(f"{str(axisTag)}: {float(axisValue)}")

		# add HTML line:
		htmlSnippet += "\n%s\t<option value='%s'>%s</option>" % (
			tabbing,
			",".join(styleValues),
			styleName,
		)

	htmlSnippet += "\n{tabbing}</select>"
	return htmlSnippet


def familyNameOfInstance(thisInstance):
	familyNameProperty = thisInstance.propertyForName_languageTag_("familyNames", "dflt")
	if familyNameProperty:
		return familyNameProperty.value
	else:
		return thisInstance.font.familyName


def otVarInfoForFont(thisFont, variableFontSetting=None):
	fullName = otVarFullName(thisFont)
	fileName = otVarFileName(thisFont)
	unicodeEscapes = allUnicodeEscapesOfFont(thisFont)
	glyphInfos = allGlyphInfosOfFont(thisFont)
	plainSuffix = otVarPlainSuffix()
	otVarSliders = allOTVarSliders(thisFont, variableFontSetting=variableFontSetting)
	variationCSS = defaultVariationCSS(thisFont)
	featureList = featureListForFont(thisFont)
	styleMenu = listOfAllStyles(thisFont)
	fontLangMenu = langMenu(thisFont)

	# check if there is an export folder set up:
	exportFolder = None
	if variableFontSetting:
		exportFolderParameter = variableFontSetting.customParameterActiveForKey_("Export Folder")
		exportFolderParameterFontWide = thisFont.customParameterActiveForKey_("Export Folder")
		for parameter in (exportFolderParameter, exportFolderParameterFontWide):
			if parameter:
				exportFolder = parameter.value
				break

	return fullName, fileName, unicodeEscapes, otVarSliders, variationCSS, featureList, styleMenu, fontLangMenu, exportFolder, glyphInfos, plainSuffix


def otVarInfoForInstance(thisInstance):
	thisFont = thisInstance.font
	familyName = familyNameOfInstance(thisInstance)
	fullName, fileName, unicodeEscapes, otVarSliders, variationCSS, featureList, styleMenu, fontLangMenu, exportFolder, glyphInfos, plainSuffix = otVarInfoForFont(thisFont, variableFontSetting=thisInstance)  # fallback

	# instance-specific overrides:
	fullName = f"{familyName} {thisInstance.name}"
	fileName = otVarFileName(thisFont, thisInstance)

	# TODO breakdown to OTVar Export (consider parameters etc.):
	# unicodeEscapes
	# otVarSliders
	# variationCSS
	# featureList
	# fontLangMenu

	return fullName, fileName, unicodeEscapes, otVarSliders, variationCSS, featureList, styleMenu, fontLangMenu, exportFolder, glyphInfos, plainSuffix


# clears macro window log:
Glyphs.clearLog()

# Query app version:
GLYPHSAPPVERSION = Glyphs.versionString
appVersionHighEnough = not GLYPHSAPPVERSION.startswith("1.")

# Create Samsa if shift and option are held down
shouldCreateSamsa = False
keysPressed = NSEvent.modifierFlags()
optionKeyPressed = keysPressed & NSAlternateKeyMask == NSAlternateKeyMask
shiftKeyPressed = keysPressed & NSShiftKeyMask == NSShiftKeyMask
if optionKeyPressed and shiftKeyPressed:
	shouldCreateSamsa = True

if not appVersionHighEnough:
	Message(title="App Version Error", message="This script requires Glyphs 2.5 or later. Sorry.", OKButton=None)
else:
	firstDoc = Glyphs.orderedDocuments()[0]
	thisFont = Glyphs.font  # frontmost font
	exportPath = currentOTVarExportPath()

	# In Font info > Exports, there can be more than one OTVar export:
	variableFontInfos = []
	for thisInstance in thisFont.instances:
		try:
			if thisInstance.typeName() == "variable" and thisInstance.active:
				variableFontInfo = otVarInfoForInstance(thisInstance)
				variableFontInfos.append(variableFontInfo)
		except Exception as e:
			print(e)

	# fallback if there are not OTVar exports set up at all:
	if not variableFontInfos:
		variableFontInfos.append(otVarInfoForFont(thisFont))

	for variableFontInfo in variableFontInfos:
		fullName, fileName, unicodeEscapes, otVarSliders, variationCSS, featureList, styleMenu, fontLangMenu, exportFolder, glyphInfos, plainSuffix = variableFontInfo

		print("\nPreparing Test HTML for: %s%s" % (
			fullName,
			f" ({fileName})" if fileName else "",
		))
		print("👷🏼‍ Building HTML code...")
		htmlContent = buildHTML(fullName, fileName, unicodeEscapes, otVarSliders, variationCSS, featureList, styleMenu, fontLangMenu, shouldCreateSamsa, glyphInfos=glyphInfos, plainSuffix=plainSuffix)

		# Write file to disk:
		print("💾 Writing files to disk...")
		if exportPath:
			if exportFolder:
				exportPath = path.join(exportPath, exportFolder)

			if shouldCreateSamsa:
				print("🐜 Building Samsa...")
				# build samsa config:
				samsaURL = "https://lorp.github.io/samsa/src/"  # "https://www.axis-praxis.org/samsa"
				samsaFileName = "samsa-config.js"
				terminalCommand = "cd '%s'; printf \"CONFIG.fontList = [\n\t{\n\t\tname: '%s',\n\t\tpreload: true,\n\t\turl: 'data:font/ttf;base64,%%s',\n\t}\n];\n\" `base64 -i '%s'` > %s" % (
					exportPath,
					fullName,
					# samsaURL, samsaURL,
					fileName,
					samsaFileName,
				)
				system(terminalCommand)
				print(f"✅ Created {samsaFileName}")

				# download samsa files:
				samsaFiles = ("samsa-core.js", "samsa-gui.html", "samsa-gui.css")  # "fonts/IBMPlexSansVar-Roman.ttf", "fonts/IBMPlexSansVar-Italic.ttf")
				for samsaFile in samsaFiles:
					terminalCommand = "curl --create-dirs %s/%s -o '%s'" % (samsaURL, samsaFile, path.join(exportPath, samsaFile))
					system(terminalCommand)
					print(f"⬇️ Downloaded {samsaFile}")

				# fix css links:
				terminalCommand = "cd '%s'; sed -i '' 's|url(fonts|url(https://www.axis-praxis.org/samsa/fonts|g' samsa-gui.css" % exportPath
				system(terminalCommand)

			print("🕸 Building HTML file...")
			strippedFileName = ".".join(fileName.split(".")[:-1])  # removes the last dot-suffix
			htmlFileName = f"{strippedFileName} fonttest.html"
			if saveFileInLocation(content=htmlContent, fileName=htmlFileName, filePath=exportPath):
				print("✅ Successfully wrote file to disk.")
				glyphs4ShowsInFinder = Glyphs.versionNumber >= 4 and Glyphs.defaults["GSVariableExportShowInFinder"] == 1
				if not glyphs4ShowsInFinder:
					system(f'open "{exportPath}"')
				# webbrowser.open() can raise UnicodeEncodeError on macOS when the
				# osascript pipe defaults to ASCII, so open the file via `open` instead:
				system(f'open "{exportPath}/{htmlFileName}"')
			else:
				print("🛑 Error writing file to disk.")
		else:
			Message(title="OTVar Test HTML Error", message="Could not determine export path. Have you exported any variable fonts yet?", OKButton=None)
