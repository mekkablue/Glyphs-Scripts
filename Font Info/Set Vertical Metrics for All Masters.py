#MenuTitle: Set Vertical Metrics for All Masters
# -*- coding: utf-8 -*-
__doc__="""
Adds vertical metrics for all masters, or propagates all current master metrics to all other masters.
"""

thisFont = Glyphs.font # frontmost font
currentMaster = thisFont.selectedFontMaster # active master
upm = thisFont.upm
maxY = 0.0
minY = 0.0
letterMinY = 0.0

def minMaxOfLayer(thisLayer,minY,maxY):
	layerMin = thisLayer.bounds.origin.y
	layerMax = layerMin + thisLayer.bounds.size.height
	if layerMin < minY:
		minY = layerMin
	if layerMax > maxY:
		maxY = layerMax
	return minY, maxY

for thisGlyph in [g for g in thisFont.glyphs if g.export]:
	for thisMaster in thisFont.masters:
		thisLayer = thisGlyph.layers[thisMaster.id]
		minY, maxY = minMaxOfLayer(thisLayer,minY,maxY)
		if thisGlyph.category == "Letter" and minY < letterMinY:
			letterMinY = minY
	# add brace+bracket layers
	# da gab es eine relevantLayers Methode...?


corr = 0.0
calculatedDescender = (upm*maxY/(maxY-minY))-upm
if letterMinY < calculatedDescender:
	corr = round( calculatedDescender-letterMinY+4, -1 )
	
maxY = round( maxY+4, -1 )
minY = round( minY-4, -1 )
print "minY, maxY, upm:", minY, maxY, upm

verticalMetrics = {
	"typoAscender":  "maxY", # "upm*maxY/(maxY-minY)-corr",
	"typoDescender": "minY", # "(upm*maxY/(maxY-minY))-upm-corr",
	"typoLineGap":   "max(maxY+minY-upm,0)",
	"hheaAscender":  "upm*maxY/(maxY-minY)-corr", # "maxY", # 
	"hheaDescender": "(upm*maxY/(maxY-minY))-upm-corr", # "minY", # 
	"hheaLineGap":   "max(maxY+minY-upm,0)",
	"winAscent":     "maxY",
	"winDescent":    "-minY",
}



def setVerticalMetrics( thisMaster, minY, maxY, upm, overwrite=True ):
	availableParameters = [c.name for c in thisMaster.customParameters]
	for thisMetric in verticalMetrics:
		if (not thisMetric in availableParameters) or (thisMetric in availableParameters and overwrite):
			value = round( eval(verticalMetrics[thisMetric]), -1 )
			thisMaster.customParameters[thisMetric] = value
			print thisMetric, verticalMetrics[thisMetric], value

def copyMetricsFromMasterToMaster( sourceMaster, targetMaster ):
	for thisMetric in verticalMetrics:
		targetMaster.customParameters[thisMetric] = sourceMaster.customParameters[thisMetric]

setVerticalMetrics( currentMaster, minY, maxY, upm, overwrite=False )
for thisMaster in thisFont.masters:
	if thisMaster != currentMaster:
		copyMetricsFromMasterToMaster( currentMaster, thisMaster)
		