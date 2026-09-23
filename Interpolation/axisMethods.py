# -*- coding: utf-8 -*-

def masterValueForAxisTag(master, axisTag="wght"):
	font = master.font
	axisID = [a for a in font.axes if a.axisTag == axisTag][0].axisId
	value = master.axisValueValueForId_(axisID)
	return value


def styleValueForAxisTag(style, axisTag="wght"):
	font = style.font
	axisID = [a for a in font.axes if a.axisTag == axisTag][0].axisId
	value = style.axisValueValueForId_(axisID)
	return value


def extremeMasterValuesNative(font, axisTag="wght"):
	low, high = None, None
	for master in font.masters:
		masterValue = masterValueForAxisTag(master, axisTag)
		if low is None or masterValue < low:
			low = masterValue
		if high is None or masterValue > high:
			high = masterValue
	return low, high


def extremeStyleValuesNative(font, axisTag="wght"):
	low, high = None, None
	for style in font.instances:
		styleValue = styleValueForAxisTag(style, axisTag)
		if low is None or styleValue < low:
			low = styleValue
		if high is None or styleValue > high:
			high = styleValue
	return low, high


def extremeStyleValuesWeightClass(font, axisTag="wght"):
	low, high = None, None
	for style in font.instances:
		styleValue = style.weightClassValue()
		if low is None or styleValue < low:
			low = styleValue
		if high is None or styleValue > high:
			high = styleValue
	return low, high


def coefficient(number, low, high):
	span = high - low
	coefficient = (number - low) / span
	return coefficient


def valueForCoefficient(coefficient, low, high):
	span = high - low
	number = low + coefficient * span
	return number


def __test__():
	coefficientValue = coefficient(425, 100, 900)
	expectedCoefficient = 0.40625
	assert abs(coefficientValue - expectedCoefficient) < 0.000001, "Expected coefficient %s, got %s" % (expectedCoefficient, coefficientValue)
	roundTripValue = valueForCoefficient(coefficientValue, 100, 900)
	assert abs(roundTripValue - 425) < 0.000001, "Expected round-trip value 425, got %s" % roundTripValue
