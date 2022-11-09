#MenuTitle: Stitcher
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Turn your paths into dotted lines, and specify a component as dot, i.e. stitch components onto paths in selected glyphs. Respects origin anchor in your source component.
"""

import math, vanilla, traceback
from Foundation import NSPoint

def deleteAllComponents(thisLayer):
	try:
		# print "-- Deleting %i existing components." % ( len(thisLayer.components) ) #DEBUG
		while len(thisLayer.components) > 0:
			# print "  Deleting component", thisLayer.components[0].componentName
			del thisLayer.components[0]

		return True

	except Exception as e:
		print(traceback.format_exc())
		return False

def bezier(A, B, C, D, t):
	x1, y1 = A.x, A.y
	x2, y2 = B.x, B.y
	x3, y3 = C.x, C.y
	x4, y4 = D.x, D.y

	x = x1 * (1 - t)**3 + x2 * 3 * t * (1 - t)**2 + x3 * 3 * t**2 * (1 - t) + x4 * t**3
	y = y1 * (1 - t)**3 + y2 * 3 * t * (1 - t)**2 + y3 * 3 * t**2 * (1 - t) + y4 * t**3

	return x, y

def distance(node1, node2):
	return math.hypot(node1.x - node2.x, node1.y - node2.y)

def segmentsForPath(p):
	segments = []
	currentSegment = []
	pathlength = len(p.nodes)
	for i, n in enumerate(p.nodes):
		currentSegment.append(n.position)
		if i > 0 and n.type != GSOFFCURVE:
			offset = len(currentSegment)
			if not offset in (2, 4):
				firstPoint = p.nodes[(i - offset) % pathlength].position
				currentSegment.insert(0, firstPoint)
			segments.append(tuple(currentSegment))
			currentSegment = []
	return segments

def getFineGrainPointsForPath(thisPath, distanceBetweenDots):
	try:
		layerCoords = []
		pathSegments = segmentsForPath(thisPath)

		for thisSegment in pathSegments:

			if len(thisSegment) == 2:
				# straight line:
				beginPoint = thisSegment[0]
				endPoint = thisSegment[1]

				dotsPerSegment = int((distance(beginPoint, endPoint) / distanceBetweenDots) * 11)

				for i in range(dotsPerSegment):
					x = float(endPoint.x * i) / dotsPerSegment + float(beginPoint.x * (dotsPerSegment - i)) / dotsPerSegment
					y = float(endPoint.y * i) / dotsPerSegment + float(beginPoint.y * (dotsPerSegment - i)) / dotsPerSegment
					layerCoords += [NSPoint(x, y)]

			elif len(thisSegment) == 4:
				# curved segment:
				bezierPointA = thisSegment[0]
				bezierPointB = thisSegment[1]
				bezierPointC = thisSegment[2]
				bezierPointD = thisSegment[3]

				bezierLength = distance(bezierPointA, bezierPointB) + distance(bezierPointB,
																				bezierPointC) + distance(bezierPointC, bezierPointD) # very rough approximation, up to 11% too long
				dotsPerSegment = int((bezierLength / distanceBetweenDots) * 10)

				for i in range(1, dotsPerSegment):
					t = float(i) / float(dotsPerSegment)
					x, y = bezier(bezierPointA, bezierPointB, bezierPointC, bezierPointD, t)
					layerCoords += [NSPoint(x, y)]

				layerCoords += [NSPoint(bezierPointD.x, bezierPointD.y)]

		return layerCoords
	except Exception as e:
		print(traceback.format_exc())

def interpolatePointPos(p1, p2, factor):
	factor = factor % 1.0
	x = p1.x * factor + p2.x * (1.0 - factor)
	y = p1.y * factor + p2.y * (1.0 - factor)
	return NSPoint(x, y)

def dotCoordsOnPath(thisPath, distanceBetweenDots, balanceOverCompletePath=False):
	try:
		dotPoints = [thisPath.nodes[0]]
		fineGrainPoints = getFineGrainPointsForPath(thisPath, distanceBetweenDots)

		myLastPoint = dotPoints[-1]

		for thisPoint in fineGrainPoints:
			if distance(myLastPoint, thisPoint) >= distanceBetweenDots:
				dotPoints += [thisPoint]
				myLastPoint = thisPoint
			else:
				pass

		if balanceOverCompletePath:
			reversePath = thisPath.copy()
			reversePath.reverse()
			reverseDotPoints = dotCoordsOnPath(reversePath, distanceBetweenDots)
			numberOfPoints = min(len(reverseDotPoints), len(dotPoints) - 1)
			for i in range(numberOfPoints):
				factor = 1.0 / numberOfPoints * i
				j = -1 - i
				newPos = interpolatePointPos(dotPoints[j], reverseDotPoints[i], factor)
				dotPoints[j] = newPos

		return dotPoints
	except Exception as e:
		print(traceback.format_exc())

def placeDots(thisLayer, useBackground, componentName, distanceBetweenDots, balanceOverCompletePath=False):
	try:
		# find out component offset:
		xOffset = 0.0
		yOffset = 0.0
		Font = thisLayer.parent.parent
		FontMasterID = thisLayer.associatedMasterId
		sourceComponent = Font.glyphs[componentName]

		if sourceComponent:
			try:
				sourceAnchor = sourceComponent.layers[thisLayer.associatedMasterId].anchors["origin"]
				xOffset, yOffset = -sourceAnchor.position.x, -sourceAnchor.position.y
			except:
				pass
				#print "-- Note: no origin anchor in '%s'." % ( componentName )

			# use background if specified:
			if useBackground:
				sourceLayer = thisLayer.background
			else:
				sourceLayer = thisLayer

			for thisPath in sourceLayer.paths:
				for thisPoint in dotCoordsOnPath(thisPath, distanceBetweenDots, balanceOverCompletePath):
					newComp = GSComponent(componentName, NSPoint(thisPoint.x + xOffset, thisPoint.y + yOffset))
					newComp.alignment = -1
					if Glyphs.versionNumber < 3:
						thisLayer.addComponent_(newComp)
					else:
						thisLayer.addShape_(newComp)

			return True
		else:
			return False

	except Exception as e:
		print(traceback.format_exc())
		return False

def minimumOfOne(value):
	try:
		returnValue = float(value)
		if returnValue < 1.0:
			returnValue = 1.0
	except:
		returnValue = 1.0

	return returnValue

def process(thisLayer, deleteComponents, componentName, distanceBetweenDots, useBackground=True, balanceOverCompletePath=False):
	try:
		if deleteComponents:
			if not deleteAllComponents(thisLayer):
				print("-- Error deleting previously placed components.")

		if useBackground and len(thisLayer.paths) > 0:
			if thisLayer.className() == "GSBackgroundLayer":
				thisLayer = thisLayer.foreground()
			thisLayer.background.clear()
			for thisPath in thisLayer.paths:
				thisLayer.background.paths.append(thisPath.copy())

			if Glyphs.versionNumber < 3:
				thisLayer.paths = []
			else:
				thisLayer.removeShapes_([path for path in thisLayer.paths])

		if not placeDots(thisLayer, useBackground, componentName, distanceBetweenDots, balanceOverCompletePath):
			print("-- Could not place components at intervals of %.1f units." % distanceBetweenDots)
	except Exception as e:
		print(traceback.format_exc())

class ComponentOnLines(object):

	def __init__(self):
		windowHeight = 180
		self.w = vanilla.FloatingWindow(
			(350, windowHeight), "Stitcher", minSize=(300, windowHeight), maxSize=(500, windowHeight), autosaveName="com.mekkablue.ComponentsOnNodes.mainwindow"
			)

		inset = 15
		linePos = 14
		lineGap = 22
		self.w.text_1 = vanilla.TextBox((inset, linePos, 100, 14), "Place component:", sizeStyle='small')
		self.w.componentName = vanilla.EditText((inset + 100, linePos, -15, 20), "_circle", sizeStyle='small', callback=self.SavePreferences)

		linePos += lineGap
		self.w.text_2 = vanilla.TextBox((inset, linePos, 15 + 95, 14), "At intervals of:", sizeStyle='small')
		self.w.sliderMin = vanilla.EditText((inset + 100, linePos, 50, 20), "30", sizeStyle='small', callback=self.SavePreferences)
		self.w.sliderMax = vanilla.EditText((-inset - 50, linePos, -15, 20), "60", sizeStyle='small', callback=self.SavePreferences)
		self.w.intervalSlider = vanilla.Slider(
			(inset + 100 + 50 + 10, linePos, -inset - 50 - 10, 20), value=0, minValue=0.0, maxValue=1.0, sizeStyle='small', callback=self.ComponentOnLinesMain
			)

		linePos += lineGap
		self.w.liveSlider = vanilla.CheckBox((inset, linePos, -inset, 20), "Live slider", value=False, sizeStyle='small')

		linePos += lineGap
		self.w.useBackground = vanilla.CheckBox((inset, linePos, -inset, 20), "Keep paths in background", value=True, sizeStyle='small', callback=self.SavePreferences)

		linePos += lineGap
		self.w.balanceOverCompletePath = vanilla.CheckBox(
			(inset, linePos, -inset, 20), u"Balance components over complete path", value=False, callback=self.SavePreferences, sizeStyle='small'
			)

		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Stitch", sizeStyle='regular', callback=self.ComponentOnLinesMain)
		self.w.setDefaultButton(self.w.runButton)

		try:
			self.LoadPreferences()
		except:
			pass

		self.w.open()
		self.w.makeKey()

	def SavePreferences(self, sender):
		try:
			Glyphs.defaults["com.mekkablue.ComponentOnLines.componentName"] = self.w.componentName.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.sliderMin"] = self.w.sliderMin.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.sliderMax"] = self.w.sliderMax.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.intervalSlider"] = self.w.intervalSlider.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.liveSlider"] = self.w.liveSlider.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.useBackground"] = self.w.useBackground.get()
			Glyphs.defaults["com.mekkablue.ComponentOnLines.balanceOverCompletePath"] = self.w.balanceOverCompletePath.get()
		except:
			print(traceback.format_exc())
			return False

		return True

	def LoadPreferences(self):
		try:
			Glyphs.registerDefault("com.mekkablue.ComponentOnLines.componentName", "_circle")
			Glyphs.registerDefault("com.mekkablue.ComponentOnLines.sliderMin", "30")
			Glyphs.registerDefault("com.mekkablue.ComponentOnLines.sliderMin", "60")
			Glyphs.registerDefault("com.mekkablue.ComponentOnLines.liveSlider", False)
			Glyphs.registerDefault("com.mekkablue.ComponentOnLines.useBackground", True)
			Glyphs.registerDefault("com.mekkablue.ComponentOnLines.balanceOverCompletePath", False)
			self.w.componentName.set(Glyphs.defaults["com.mekkablue.ComponentOnLines.componentName"])
			self.w.sliderMin.set(Glyphs.defaults["com.mekkablue.ComponentOnLines.sliderMin"])
			self.w.sliderMax.set(Glyphs.defaults["com.mekkablue.ComponentOnLines.sliderMax"])
			self.w.intervalSlider.set(Glyphs.defaults["com.mekkablue.ComponentOnLines.intervalSlider"])
			self.w.liveSlider.set(Glyphs.defaults["com.mekkablue.ComponentOnLines.liveSlider"])
			self.w.useBackground.set(Glyphs.defaults["com.mekkablue.ComponentOnLines.useBackground"])
			self.w.balanceOverCompletePath.set(Glyphs.defaults["com.mekkablue.ComponentOnLines.balanceOverCompletePath"])
		except:
			print(traceback.format_exc())
			return False

		return True

	def ComponentOnLinesMain(self, sender):
		try:
			if (bool(Glyphs.defaults["com.mekkablue.ComponentOnLines.liveSlider"]) and sender == self.w.intervalSlider) or sender != self.w.intervalSlider:
				Font = Glyphs.font
				FontMaster = Font.selectedFontMaster
				selectedLayers = Font.selectedLayers
				deleteComponents = True
				componentName = Glyphs.defaults["com.mekkablue.ComponentOnLines.componentName"]

				sliderMin = minimumOfOne(Glyphs.defaults["com.mekkablue.ComponentOnLines.sliderMin"])
				sliderMax = minimumOfOne(Glyphs.defaults["com.mekkablue.ComponentOnLines.sliderMax"])

				sliderPos = float(Glyphs.defaults["com.mekkablue.ComponentOnLines.intervalSlider"])
				distanceBetweenDots = sliderMin * (1.0 - sliderPos) + sliderMax * sliderPos
				useBackground = bool(Glyphs.defaults["com.mekkablue.ComponentOnLines.useBackground"])
				balanceOverCompletePath = bool(Glyphs.defaults["com.mekkablue.ComponentOnLines.balanceOverCompletePath"])

				Font.disableUpdateInterface()
				try:
					for thisLayer in selectedLayers:
						thisGlyph = thisLayer.parent
						# thisGlyph.beginUndo() # undo grouping causes crashes
						process(thisLayer, deleteComponents, componentName, distanceBetweenDots, useBackground, balanceOverCompletePath)
						# thisGlyph.endUndo() # undo grouping causes crashes

				except Exception as e:
					Glyphs.showMacroWindow()
					print("\n⚠️ Script Error:\n")
					import traceback
					print(traceback.format_exc())
					print()
					raise e

				finally:
					Font.enableUpdateInterface()

				if not self.SavePreferences(self):
					print("Note: could not write preferences.")
		except:
			print(traceback.format_exc())

ComponentOnLines()
