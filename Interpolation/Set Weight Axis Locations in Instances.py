#MenuTitle: Set Weight Axis Locations in Instances
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Will set weight axis location parameters for all instances, and sync them with their respective usWeightClass. Will set the width axis coordinates to the spec defaults for usWidthClass, if they have not been set yet. Otherwise will keep them as is.
"""

from Foundation import NSDictionary

def widthForWidthClass(widthClass):
	"""According to the OS/2 table spec: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#uswidthclass"""
	if type(widthClass) == int and 1 <= widthClass <= 9:
		return {
			1: 50,
			2: 62.5,
			3: 75,
			4: 87.5,
			5: 100,
			6: 112.5,
			7: 125,
			8: 150,
			9: 200,
		}[widthClass]
	else:
		print("⚠️ Not a valid usWidthClass value: %s" % repr(widthClass))
		return None

def axisLocationEntry( axisName, locationValue ):
	return NSDictionary.alloc().initWithObjects_forKeys_(
		(axisName, locationValue),
		("Axis", "Location")
	)

def process( thisInstance ):
	existingParameter = thisInstance.customParameters["Axis Location"]
	
	theFont = thisInstance.font
	weightClassValue = thisInstance.weightClassValue()
	axisLocations = []
	for i,thisAxis in enumerate(theFont.axes):
		value = None
		if thisAxis.name == "Weight":
			value = weightClassValue
		elif existingParameter:
			# preserve existing axis locations
			for entry in existingParameter:
				if thisAxis.name == entry["Axis"]:
					value = entry["Location"]
		
		if value==None:
			if thisAxis.name == "Width":
				value = widthForWidthClass(thisInstance.widthClassValue())
			else:
				# default to replicating the coordinate position
				value = thisInstance.coordinateForAxisIndex_(i)
		axisLocations.append( axisLocationEntry(thisAxis.name, value) )
	if axisLocations:
		thisInstance.customParameters["Axis Location"] = tuple(axisLocations)
		return weightClassValue
"""
for m in Font.masters:
	print("\nMASTER %s" % m.name)

	axisLocations = []
	for idx, axis in enumerate(Font.axes):
		axisLocations.append(
			NSDictionary.alloc().initWithObjects_forKeys_(
				(axis.name, m.axes[idx]),
				("Axis", "Location")
			)
		)
		print("   %s: %i" % (axis.name, m.axes[idx]))
	m.customParameters["Axis Location"] = tuple(axisLocations)

widthValueForClass = {
	1: 75,
	3: 85,
	5: 100,
	7: 115,
	9: 125,
}

print("\n%s"%("-"*50))

for idx, i in enumerate(Font.instances):
	if i.type == 0: # instance, no VF setting
		print("\nINSTANCE %02i: %s" % (idx, i.name))
		axisLocations = []
		instanceValues = {
			"Weight": i.weightClass,
			"Width": widthValueForClass[i.widthClass],
		}
		for axis in Font.axes:
			axisLocations.append(
				NSDictionary.alloc().initWithObjects_forKeys_(
					(axis.name, instanceValues[axis.name]),
					("Axis", "Location")
				)
			)
			print("  %s: %i" % (axis.name, instanceValues[axis.name]))
		i.customParameters["Axis Location"] = tuple(axisLocations)
"""



thisFont = Glyphs.font # frontmost font
Glyphs.clearLog() # clears log in Macro window

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for i, thisInstance in enumerate(thisFont.instances):
		if thisInstance.type == 0:
			print("ℹ️ Instance %i: wght=%i (%s)" % (i, process(thisInstance), thisInstance.name))
			
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Error in script: Set Weight Axis Locations in Instances\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
