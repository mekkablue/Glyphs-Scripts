#MenuTitle: Compare Glyph Info
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Compares open fonts and builds a lits of differing glyph info, including Unicode values and categorisation.
"""

import vanilla

# CONSTANTS:

thingsToCompare = (
	"Unicodes",
	"Category",
	"Subcategory",
	"Production Name",
	"Script",
	"Export Status",
	"Left Kerning Group",
	"Right Kerning Group",
	"Color",
	"Left Metrics Key",
	"Right Metrics Key",
	"Width Metrics Key",
	"Is Aligned", 
	"Has Aligned Width",
	"Has Annotations",
	"Has Components",
	"Has Corners",
	"Has Custom Glyph Info",
	"Has Hints",
	"Has PostScript Hints",
	"Has TrueType Hints",
	"Has Special Layers",
	"Is Color Glyph",
	"Is Apple Color Glyph",
	"Is SVG Color Glyph",
	"Is Hangul Key Glyph",
	"Masters Are Compatible",
	"Glyph Note",
)

predefinedColors = (
	"red",
	"orange",
	"brown",
	"yellow",
	"lightgreen",
	"green",
	"lightblue",
	"blue",
	"purple",
	"pink",
	"lightgrey",
	"grey",
)

missingGlyphValue = "(missing glyph)"
missingValue = "–"

class CompareGlyphInfo( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 400
		windowHeight = 160
		windowWidthResize  = 1000 # user can resize width by this value
		windowHeightResize = 1000 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Compare Glyph Info", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.CompareGlyphInfo.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.linePos, inset, lineHeight = 5, 6, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, self.linePos+2, 140, 14), "Compare between fonts:", sizeStyle='small', selectable=True )

		self.w.whatToCompare = vanilla.PopUpButton( (inset+140, self.linePos, -160-inset-10, 17), thingsToCompare, sizeStyle='small', callback=self.Reload )
		self.w.whatToCompare.getNSPopUpButton().setToolTip_("Choose which glyph info to compare between all open fonts.")

		self.w.ignoreMissingGlyphs = vanilla.CheckBox( (-160-inset, self.linePos, -inset-25, 17), "Ignore missing glyphs", value=False, callback=self.Reload, sizeStyle='small' )
		self.w.ignoreMissingGlyphs.getNSButton().setToolTip_("If activated, will only list glyphs that are present in ALL open fonts.")
		
		self.w.updateButton = vanilla.SquareButton( (-inset-20, self.linePos, -inset, 18), "↺", sizeStyle='small', callback=self.Reload )
		self.w.updateButton.getNSButton().setToolTip_("Reload with currently opened fonts. Useful if you just opened or closed a font, or brought another font forward.")

		self.linePos += lineHeight
		self.Reload()
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def getColumnHeaders(self, sender=None):
		# {"title":xxx, "key":xxx, "editable":False, "width":xxx} for every font
		headers = [
			{"title":"Glyph Name", "key":"glyphName", "editable":False, "width":200, "maxWidth":400},
		]
		for i,thisFont in enumerate(Glyphs.fonts):
			if thisFont.filepath:
				fileName = thisFont.filepath.lastPathComponent()
			else:
				fileName = "%s (unsaved)" % thisFont.familyName
				
			columnHeader = {"title":fileName, "key":"font-%i"%i, "editable":False, "width":150, "maxWidth":300}
			headers.append(columnHeader)
			
		return headers
	
	def returnValue(self, value):
		if value:
			return value
		else:
			return missingValue
	
	def returnBool(self, value):
		if value:
			return "✅"
		return "🚫"
	
	def getInfoItemForGlyph(self, glyph):
		if glyph is None:
			return missingGlyphValue
			
		index = self.w.whatToCompare.get()
		if index==0:
			if not glyph.unicodes:
				return missingValue
			else:
				return ", ".join(glyph.unicodes)
		elif index==1:
			return self.returnValue( glyph.category )
		elif index==2:
			return self.returnValue( glyph.subCategory )
		elif index==3:
			return self.returnValue( glyph.productionName )
		elif index==4:
			return self.returnValue( glyph.script )
		elif index==5:
			return self.returnBool( glyph.export )
		elif index==6:
			return self.returnValue( glyph.leftKerningGroup )
		elif index==7:
			return self.returnValue( glyph.rightKerningGroup )
		elif index==8:
			if glyph.color is None:
				return missingValue
			else:
				return predefinedColors[glyph.color]
		elif index==9:
			return self.returnValue( glyph.leftMetricsKey )
		elif index==10:
			return self.returnValue( glyph.rightMetricsKey )
		elif index==11:
			return self.returnValue( glyph.widthMetricsKey )
		elif index==12:
			return self.returnBool( glyph.isAligned() )
		elif index==13:
			return self.returnBool( glyph.hasAlignedWidth() )
		elif index==14:
			return self.returnBool( glyph.hasAnnotations() )
		elif index==15:
			return self.returnBool( glyph.hasComponents() )
		elif index==16:
			return self.returnBool( glyph.hasCorners() )
		elif index==17:
			return self.returnBool( glyph.hasCustomGlyphInfo() )
		elif index==18:
			return self.returnBool( glyph.hasHints() )
		elif index==19:
			return self.returnBool( glyph.hasPostScriptHints() )
		elif index==20:
			return self.returnBool( glyph.hasTrueTypeHints() )
		elif index==21:
			return self.returnBool( glyph.hasSpecialLayers() )
		elif index==22:
			return self.returnBool( glyph.isColorGlyph() )
		elif index==23:
			return self.returnBool( glyph.isAppleColorGlyph() )
		elif index==24:
			return self.returnBool( glyph.isSVGColorGlyph() )
		elif index==25:
			return self.returnBool( glyph.isHangulKeyGlyph() )
		elif index==26:
			return self.returnBool( glyph.mastersCompatible )
		elif index==27:
			return self.returnValue( glyph.note )
			
		return "⚠️ Error"
	
	def listContent( self ):
		try:
			ignoreMissingGlyphs = self.w.ignoreMissingGlyphs.get()
			
			allNames = []
			for thisFont in Glyphs.fonts:
				allNames.extend([g.name for g in thisFont.glyphs])
			allNames = sorted(set(allNames))
			
			displayedLines = []
			for glyphName in allNames:
				line = {"glyphName":glyphName}
				checkList = []
				for i, thisFont in enumerate(Glyphs.fonts):
					column = "font-%i"%i
					glyph = thisFont.glyphs[glyphName]
					cell = self.getInfoItemForGlyph(glyph)
					line[column] = cell
					checkList.append(cell)
				
				# check if line contains differences:
				countOfDistinctItems = len(set(checkList))
				if checkList and countOfDistinctItems>1:
					if ignoreMissingGlyphs and countOfDistinctItems==2:
						if not all([item!=missingGlyphValue for item in checkList]):
							continue
					displayedLines.append(line)
				
			return displayedLines
		except Exception as e:
			print("listContent Error: %s\n" % e)
			import traceback
			print(traceback.format_exc())
			return None

	def Reload( self, sender=None ):
		try:
			try:
				del self.w.List
			except:
				pass
				
			self.w.List = vanilla.List(
						( 0, self.linePos, -0, -0 ),
						self.listContent(),
						columnDescriptions = self.getColumnHeaders(),
						drawVerticalLines = True,
						enableDelete = True,
						drawFocusRing = True,
						# selectionCallback = self.selectedAction,
						doubleClickCallback = self.openGlyphInFont,
						# editCallback = self.editAction,
					)
			
			self.w.List.getNSTableView().setToolTip_("Double click to open the selected glyphs in all fonts. You can select more than one line.")
		except Exception as e:
			print("Reload Error: %s\n" % e)
			import traceback
			print(traceback.format_exc())
			return None
	
	def openGlyphInFont(self, sender=None):
		if sender:
			selectedIndexes = sender.getSelection()
			if selectedIndexes:
				tabText = ""
				for index in selectedIndexes:
					item = self.w.List.get()[index]
					tabText += "/%s" % item["glyphName"]
				
				if tabText:
					for i, thisFont in enumerate(Glyphs.fonts):
						tab = thisFont.currentTab
						if not tab:
							tab = thisFont.newTab()
						tab.text = tabText
						tab.textCursor = 0
						tab.scale = 0.15
						if i>0:
							tab.viewPort = Glyphs.fonts[0].currentTab.viewPort
	
CompareGlyphInfo()