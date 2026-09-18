from types import SimpleNamespace

from TestHelpers import loadModule


axisMethods = loadModule("axisMethodsForTests", "Interpolation/axisMethods.py")


class AxisValueObject:
	def __init__(self, font, values):
		self.font = font
		self.values = values

	def axisValueValueForId_(self, axisId):
		return self.values[axisId]


class WeightClassObject(AxisValueObject):
	def __init__(self, font, values, weightClass):
		super().__init__(font, values)
		self.weightClass = weightClass

	def weightClassValue(self):
		return self.weightClass


def makeFont():
	return SimpleNamespace(
		axes=(SimpleNamespace(axisTag="wght", axisId="weight"),),
		masters=(),
		instances=(),
	)


def checkAxisValueLookup():
	font = makeFont()
	item = AxisValueObject(font, {"weight": 425})
	assert axisMethods.masterValueForAxisTag(item) == 425
	assert axisMethods.styleValueForAxisTag(item) == 425


def checkExtremeNativeValues():
	font = makeFont()
	font.masters = tuple(AxisValueObject(font, {"weight": value}) for value in (400, 100, 900, 500))
	font.instances = tuple(AxisValueObject(font, {"weight": value}) for value in (700, 350, 500))
	assert axisMethods.extremeMasterValuesNative(font) == (100, 900)
	assert axisMethods.extremeStyleValuesNative(font) == (350, 700)


def checkExtremeValuesOfEmptyCollections():
	font = makeFont()
	assert axisMethods.extremeMasterValuesNative(font) == (None, None)
	assert axisMethods.extremeStyleValuesNative(font) == (None, None)


def checkExtremeWeightClasses():
	font = makeFont()
	font.instances = tuple(
		WeightClassObject(font, {"weight": value}, weightClass)
		for value, weightClass in ((100, 250), (500, 450), (900, 800))
	)
	assert axisMethods.extremeStyleValuesWeightClass(font) == (250, 800)


def checkCoefficientRoundTrip():
	coefficient = axisMethods.coefficient(425, 100, 900)
	assert abs(coefficient - 0.40625) < 0.000001
	assert abs(axisMethods.valueForCoefficient(coefficient, 100, 900) - 425) < 0.000001
