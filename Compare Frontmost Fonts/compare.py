# -*- coding: utf-8 -*-
from __future__ import print_function

from GlyphsApp import Glyphs


def compareLists(thisSet, otherSet, ignoreEmpty=False):
	for i in range(len(thisSet))[::-1]:
		if thisSet[i] in otherSet:
			otherSet.remove(thisSet.pop(i))
		elif ignoreEmpty:
			if not thisSet[i]:
				thisSet.pop(i)

	for i in range(len(otherSet))[::-1]:
		if otherSet[i] in thisSet:
			thisSet.remove(otherSet.pop(i))
		elif ignoreEmpty:
			if not otherSet[i]:
				otherSet.pop(i)

	return thisSet, otherSet


def cleanUpAndShortenParameterContent(thisParameter, maxLength=20):
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3 code:
		if isinstance(thisParameter, GSCustomParameter):
			parameterContent = repr(thisParameter.value)
		else:
			parameterContent = repr(thisParameter)
	else:
		# GLYPHS 2 code:
		parameterContent = unicode(repr(thisParameter))  # noqa: F821
	if len(parameterContent) > maxLength:
		parameterContent = u"%s..." % parameterContent[:maxLength].replace(u"\n", u" ")
	while "  " in parameterContent:
		parameterContent = parameterContent.replace("  ", " ")
	return parameterContent


def compareCount(things, thisCount, otherCount, thisName, otherName):
	if thisCount != otherCount:
		print(u"❌ Different number of %s:" % things.upper())
		print(u"   A. %i %s in %s" % (thisCount, things.lower(), thisName))
		print(u"   B. %i %s in %s" % (otherCount, things.lower(), otherName))
	else:
		print(u"✅ Same number of %s: %i." % (things.lower(), thisCount))


def lineReport(thisSet, otherSet, thisFileName, otherFileName, name, commaSeparated=False):
	if thisSet or otherSet:
		if commaSeparated:
			separator = ", "
			element = "Elements"
		else:
			separator = "\n  "
			element = "Code lines"

		if otherSet:
			print()
			print(u"⚠️ %s not in %s of %s:" % (element, name, thisFileName))
			print(separator.join(otherSet))
			print()
		if thisSet:
			print()
			print(u"⚠️ %s not in %s of %s:" % (element, name, otherFileName))
			print(separator.join(thisSet))
			print()
	else:
		print(u"💚 %s: same code in both fonts." % name)
