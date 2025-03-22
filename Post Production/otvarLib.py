# -*- coding: utf-8 -*-
from __future__ import print_function

from GlyphsApp import Glyphs


def currentStaticExportPath():
	# GLYPHS 3
	exportPath = Glyphs.defaults["OTFExportPathManual"]
	if Glyphs.defaults["OTFExportUseExportPath"]:
		exportPath = Glyphs.defaults["OTFExportPath"]
	return exportPath


def currentOTVarExportPath():
	exportPath = Glyphs.defaults["GXExportPathManual"]
	if Glyphs.defaults["GXExportUseExportPath"]:
		exportPath = Glyphs.defaults["GXExportPath"]
	return exportPath


def otVarFamilyName(thisFont):
	if thisFont.customParameters["Variable Font Family Name"]:
		return thisFont.customParameters["Variable Font Family Name"]
	else:
		return thisFont.familyName


def otVarFileName(thisFont, thisInstance=None, suffix="ttf"):
	"""
	Reconstruct export file name of OTVAR.
	"""
	if thisInstance is not None:
		if Glyphs.versionNumber >= 3.3:
			return thisInstance.finalPath_error_(suffix, None)
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
		fileName = f"{familyName}VF.{suffix}"
		fileName = fileName.replace(" ", "")
		return fileName


def familyNameOfInstance(thisInstance):
	familyNameProperty = thisInstance.propertyForName_languageTag_("familyNames", "dflt")
	if familyNameProperty:
		return familyNameProperty.value
	else:
		return thisInstance.font.familyName
