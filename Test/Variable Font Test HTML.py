# MenuTitle: Variable Font Test HTML
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Create a Test HTML for the current font inside the current Variation Font Export folder. Hold down OPTION and SHIFT while running the script in order to create respective Samsa files in addition to the Test HTML.
"""

from os import system
from AppKit import NSClassFromString, NSBundle, NSEvent
import codecs
from GlyphsApp import Glyphs, Message


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


def currentOTVarExportPath():
	exportPath = Glyphs.defaults["GXExportPathManual"]
	if Glyphs.versionNumber and Glyphs.versionNumber >= 3:
		useExportPath = Glyphs.defaults["GXExportUseExportPath"]
	else:
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


def otVarSuffix():
	suffix = "ttf"
	for webSuffix in ("woff", "woff2"):
		preference = Glyphs.defaults["GXExport%s" % webSuffix.upper()]
		if preference:
			suffix = webSuffix
	return suffix


def otVarFileName(thisFont, thisInstance=None):
	suffix = otVarSuffix()
	if thisInstance is not None:
		fileName = thisInstance.fileName()
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


def generateAxisDict(thisFont):
	# see if there are Axis Location parameters in use:
	fontHasAxisLocationParameters = True
	importedMasters = []
	if thisFont.importedFontMasters():
		importedMasters = thisFont.importedFontMasters()
	for thisMaster in thisFont.masters + importedMasters:
		if not thisMaster.customParameters["Axis Location"]:
			fontHasAxisLocationParameters = False

	# create and return the axisDict:
	if fontHasAxisLocationParameters:
		return axisDictForFontWithAxisLocationParameters(thisFont)
	else:
		return axisDictForFontWithoutAxisLocationParameters(thisFont)


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


def axisDictForFontWithoutAxisLocationParameters(thisFont):
	sliderValues = {}
	masters = thisFont.masters
	if thisFont.importedFontMasters():
		masters.extend(thisFont.importedFontMasters())
	for i, thisMaster in enumerate(masters):
		sliderValues[i] = axisValuesForMaster(thisMaster)

	axisDict = axisDictWithVirtualMastersForFont(thisFont, {})
	for i, axis in enumerate(thisFont.axes):
		try:
			# Glyphs 2:
			axisName, axisTag = axis["Name"], axis["Tag"]
		except:
			# Glyphs 3:
			axisName, axisTag = axis.name, axis.axisTag

		if axisName in axisDict.keys():
			axisDict[axisName] = {
				"tag": axisTag,
				"min": min(sliderValues[0][i], axisDict[axisName]["min"]),
				"max": max(sliderValues[0][i], axisDict[axisName]["max"]),
			}
		else:
			axisDict[axisName] = {
				"tag": axisTag,
				"min": sliderValues[0][i],
				"max": sliderValues[0][i]
			}

		for j, thisMaster in enumerate(thisFont.masters):
			masterValue = sliderValues[j][i]
			if masterValue < axisDict[axisName]["min"]:
				axisDict[axisName]["min"] = masterValue
			elif masterValue > axisDict[axisName]["max"]:
				axisDict[axisName]["max"] = masterValue

	return axisDict


def axisDictForFontWithAxisLocationParameters(thisFont):
	masters = thisFont.masters
	if thisFont.importedFontMasters():
		masters.extend(thisFont.importedFontMasters())

	axisDict = axisDictWithVirtualMastersForFont(thisFont, {})
	for m in masters:
		for axisLocation in m.customParameters["Axis Location"]:
			axisName = axisLocation["Axis"]
			axisPos = float(axisLocation["Location"])
			if axisName not in axisDict:
				axisDict[axisName] = {
					"min": axisPos,
					"max": axisPos
				}
			else:
				if axisPos < axisDict[axisName]["min"]:
					axisDict[axisName]["min"] = axisPos
				if axisPos > axisDict[axisName]["max"]:
					axisDict[axisName]["max"] = axisPos

	# add tags:
	for axis in thisFont.axes:
		try:
			# GLYPHS 3
			axisName = axis.name
			axisTag = axis.axisTag
		except:
			# GLYPHS 2
			axisName = axis["Name"]
			axisTag = axis["Tag"]
		if axisName in axisDict.keys():
			axisDict[axisName]["tag"] = axisTag

	return axisDict


def allUnicodeEscapesOfFont(thisFont):
	allUnicodes = [f"&#x{g.unicode};" for g in thisFont.glyphs if g.unicode and g.export and g.layers[0].shapes]
	return " ".join(allUnicodes)


def featureListForFont(thisFont):
	returnString = ""
	featureList = [(f.name, f.notes) for f in thisFont.features if f.name not in ("ccmp", "aalt", "locl", "kern", "calt", "liga", "clig", "rlig") and not f.disabled()]
	for (f, n) in featureList:
		# <input type="checkbox" name="kern" id="kern" value="kern" class="otFeature" onchange="updateFeatures()" checked><label for="kern" class="otFeatureLabel">kern</label>
		if f.startswith("ss") and n and n.startswith("Name:"):
			# stylistic set name:
			setName = n.splitlines()[0][5:].strip()
			featureItem = '\t\t\t\t<input type="checkbox" name="%s" id="%s" value="%s" class="otFeature" onchange="updateFeatures()"><label for="%s" class="otFeatureLabel">%s<span class="tooltip">%s</span></label>\n' % (
				f, f, f, f, f, setName
			)
		else:
			# non-ssXX features
			featureItem = '\t\t\t\t<input type="checkbox" name="%s" id="%s" value="%s" class="otFeature" onchange="updateFeatures()"><label for="%s" class="otFeatureLabel">%s</label>\n' % (
				f, f, f, f, f
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

		html += "\t\t\t<div class='labeldiv'><label class='sliderlabel' id='label_%s' name='%s'>%s</label><input type='range' min='%i' max='%i' value='%i' class='slider' id='%s' oninput='updateSlider();'></div>\n" % (
			axisTag, axisName, axisName, minValue, maxValue, startValue, axisTag
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


def buildHTML(fullName, fileName, unicodeEscapes, otVarSliders, variationCSS, featureList, styleMenu, fontLangMenu, shouldCreateSamsa=False, defaultSize=None):
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
				let suffix = "ttf";
				if (link.textContent == "W1") {
					let suffix = "woff";
				} else {
					let suffix = "woff2";
				}
				return suffix;
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
						label.textContent += "%%";
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
				if (testText) {
					const link = document.getElementById("invert");
					if (testText.className == "●") {
						testText.className = "○";
						link.textContent = "🔳";
					} else {
						testText.className = "●";
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
				if (link.textContent == "TT") {
					link.textContent = "W1";
					setFontTypeTo("woff");
				} else if (link.textContent == "W1") {
					link.textContent = "W2";
					setFontTypeTo("woff2");
				} else {
					link.textContent = "TT";
					setFontTypeTo("ttf");
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
				<a onclick="toggleType();" id="type" class="emojiButton">&nbsp;###TTW1W2###</a>
				<a onclick="reloadFontFace();" id="reload" class="emojiButton">&nbsp;🔄</a>

			<!-- Samsa -->
				%s

			<!-- display type (x-ray vs. filled) -->
				<a onclick="toggleInverse();" id="invert" class="emojiButton">&nbsp;🔲&nbsp;</a>

			<!-- OT features -->
				<input type="checkbox" name="kern" id="kern" value="kern" class="otFeature" onchange="updateFeatures()" checked><label for="kern" class="otFeatureLabel">kern</label>
				<input type="checkbox" name="liga" id="liga" value="liga" class="otFeature" onchange="updateFeatures()" checked><label for="liga" class="otFeatureLabel">liga</label>
				<input type="checkbox" name="calt" id="calt" value="calt" class="otFeature" onchange="updateFeatures()" checked><label for="calt" class="otFeatureLabel">calt</label>
###featureList###
###languageSelection###
			</div>
		</div>

		<!-- Test Text -->
		<div contenteditable="true" spellcheck="false" autocomplete="true" id="textarea" class="●">
		</div>
	</div>

	<!-- Disclaimer -->
	<p id="helptext" onmouseleave="vanish(this);">
		<strong>Ctrl-period/comma</strong> step through styles <strong>Ctrl-R</strong> reset charset <strong>Ctrl-U</strong> update font <strong>Ctrl-L</strong> Lat-1 <strong>Ctrl-J</strong> LTR/RTL <strong>Ctrl-C</strong> center <strong>Ctrl-M</strong> toggle menu <strong>Ctrl-X</strong> x-ray <strong>Ctrl +/−</strong> size <strong>Ctrl-1/2</strong> linegap <strong>Shift</strong> high slider precision <em>Not working? Try newer macOS or <a href="https://www.google.com/chrome/">latest Chrome</a>. Hover mouse above this note to make it disappear.</em>
	</p>
	</body>
</html>
""" % (samsaPlaceholder)

	if shouldCreateSamsa:
		samsaReplaceWith = "<a href='samsa-gui.html' class='emojiButton' style='color:rgb(255, 165, 0);'>&nbsp;🪲</a>"
	else:
		samsaReplaceWith = samsaPlaceholder

	typeAppreviations = {
		"otf": "OT",
		"ttf": "TT",
		"woff": "W1",
		"woff2": "W2",
	}
	fileTypeAbbreviation = typeAppreviations[fileName.split(".")[-1]]

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
		("###defaultSize###", defaultSize)
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
		if axisLocationParameter:
			axisName = thisAxis.name
			for axisRecord in axisLocationParameter:
				if axisRecord["Axis"] == axisName:
					locDict[axisTag] = axisRecord["Location"]
		else:
			locDict[axisTag] = masterOrInstance.axes[axisIndex]
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
	otVarSliders = allOTVarSliders(thisFont, variableFontSetting=variableFontSetting)
	variationCSS = defaultVariationCSS(thisFont)
	featureList = featureListForFont(thisFont)
	styleMenu = listOfAllStyles(thisFont)
	fontLangMenu = langMenu(thisFont)
	return fullName, fileName, unicodeEscapes, otVarSliders, variationCSS, featureList, styleMenu, fontLangMenu


def otVarInfoForInstance(thisInstance):
	thisFont = thisInstance.font
	familyName = familyNameOfInstance(thisInstance)
	fullName, fileName, unicodeEscapes, otVarSliders, variationCSS, featureList, styleMenu, fontLangMenu = otVarInfoForFont(thisFont, variableFontSetting=thisInstance)  # fallback

	# instance-specific overrides:
	fullName = f"{familyName} {thisInstance.name}"
	fileName = otVarFileName(thisFont, thisInstance)

	# TODO breakdown to OTVar Export (consider parameters etc.):
	# unicodeEscapes
	# otVarSliders
	# variationCSS
	# featureList
	# fontLangMenu

	return fullName, fileName, unicodeEscapes, otVarSliders, variationCSS, featureList, styleMenu, fontLangMenu


# clears macro window log:
Glyphs.clearLog()

# Query app version:
GLYPHSAPPVERSION = NSBundle.bundleForClass_(NSClassFromString("GSMenu")).infoDictionary().objectForKey_("CFBundleShortVersionString")
appVersionHighEnough = not GLYPHSAPPVERSION.startswith("1.")

# Create Samsa if shift and option are held down
shouldCreateSamsa = False
keysPressed = NSEvent.modifierFlags()
optionKey, shiftKey = 524288, 131072
optionKeyPressed = keysPressed & optionKey == optionKey
shiftKeyPressed = keysPressed & shiftKey == shiftKey
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
			if thisInstance.typeName() == "variable":
				variableFontInfo = otVarInfoForInstance(thisInstance)
				variableFontInfos.append(variableFontInfo)
		except Exception as e:
			print(e)

	# fallback if there are not OTVar exports set up at all:
	if not variableFontInfos:
		variableFontInfo = otVarInfoForFont(thisFont)
		variableFontInfos.append(variableFontInfo)

	for variableFontInfo in variableFontInfos:
		fullName, fileName, unicodeEscapes, otVarSliders, variationCSS, featureList, styleMenu, fontLangMenu = variableFontInfo

		print("\nPreparing Test HTML for: %s%s" % (
			fullName,
			f" ({fileName})" if fileName else "",
		))
		print("👷🏼‍ Building HTML code...")
		htmlContent = buildHTML(fullName, fileName, unicodeEscapes, otVarSliders, variationCSS, featureList, styleMenu, fontLangMenu, shouldCreateSamsa)

		# Write file to disk:
		print("💾 Writing files to disk...")
		if exportPath:
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
					terminalCommand = "curl --create-dirs %s/%s -o '%s/%s'" % (samsaURL, samsaFile, exportPath, samsaFile)
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
				terminalCommand = f'cd "{exportPath}"; open .; open "{htmlFileName}"'
				system(terminalCommand)
			else:
				print("🛑 Error writing file to disk.")
		else:
			Message(title="OTVar Test HTML Error", message="Could not determine export path. Have you exported any variable fonts yet?", OKButton=None)
