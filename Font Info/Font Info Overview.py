#MenuTitle: Font Info Overview
# -*- coding: utf-8 -*-
__doc__="""
Lists some Font Info values for all opened fonts.
"""

import vanilla

keyList = [
	["Family Name", "familyName", 160],
	["Major", "versionMajor", 40],
	["Minor", "versionMinor", 40],
	["Grid", "gridLength", 40],
	["Designer", "designer", 200],
	["Designer URL", "designerURL", 200],
	["Manufacturer", "manufacturer", 200],
	["Manufacturer URL", "manufacturerURL", 200],
	["Copyright", "copyright", 200]
	# ["UPM", "upm"],
	# ["Date", "date", 100]
	# ["Note", "note"]
	# ["Ugly Names", "disablesNiceNames"]
]

keyColumnDescriptions = [ {"title":kl[0], "key":kl[1]} for kl in keyList ]

class FontInfoOverview( object ):
	changeCount = 0
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 600
		windowHeight = 200
		windowWidthResize  = 1200 # user can resize width by this value
		windowHeightResize = 1200 # user can resize height by this value
		self.w = vanilla.Window(
			( windowWidth, windowHeight ), # default window size
			"Font Info Overview", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.FontInfoOverview.mainwindow", # stores last window position and size
		)
		
		# List:
		self.w.List = vanilla.List(
			( 0, 0, -0,-45 ),
			self.listContent(),
			columnDescriptions = [ {"title":kl[0], "key":kl[1], "editable":True, "width":kl[2]} for kl in keyList ],
			drawVerticalLines = True,
			enableDelete = True,
			drawFocusRing = True,
			# selectionCallback = self.selectedAction,
			# doubleClickCallback = self.doubleclickedAction,
			editCallback = self.editAction
		)
		
		# Buttons:
		self.w.reloadButton = vanilla.Button((-130-90-15, -35, -130-15*2, -15), "Reload", sizeStyle='regular', callback=self.Reload )
		self.w.applyButton = vanilla.Button((-130-15, -35, -15, -15), "Apply Changes", sizeStyle='regular', callback=self.Apply )
		# self.w.setDefaultButton( self.w.reloadButton )
		
		# Counter:
		self.w.changeCounter = vanilla.TextBox( (15, -31, -250, 16), "Changes: -", sizeStyle='small')
		self.updateCounter()
		
		# open the window
		self.w.open()
		self.w.makeKey()
		
	def selectedAction( self, sender ):
		print "\nSELECTION:"
		selectedIndexes = sender.getSelection()
		print selectedIndexes
		for i in selectedIndexes:
			print sender[i]["fontObj"]
	
	def doubleclickedAction(self, sender):
		print "\nDOUBLE CLICK:"
		selectedIndexes = sender.getSelection()
		for i in selectedIndexes:
			print sender[i]["fontObj"].familyName

	def editAction(self, sender):
		try:
			self.updateCounter()
		except Exception as e:
			print "editAction Error: %s" % e
	
	def listContent( self ):
		try:
			listDictOfOpenFonts = [ dict([[ kl[1], eval("f." + kl[1]) ] for kl in keyList ] + [["fontObj",f]] ) for f in Glyphs.fonts ]
			return listDictOfOpenFonts
		except Exception as e:
			print "listContent Error: %s" % e

	def updateCounter( self ):
		try:
			changeCounter = 0
			listOfFontInfos = self.w.List.get()
			for thisFontInfo in listOfFontInfos:
				thisFont = thisFontInfo["fontObj"]
				for thisKey in thisFontInfo.keys():
					if thisKey != "fontObj":
						currentFontValue = eval( "thisFont.%s" % thisKey )
						listValue = thisFontInfo[ thisKey ]
						if currentFontValue != listValue:
							changeCounter += 1
			self.w.changeCounter.set( "Unsaved changes: %i" % changeCounter )
		except Exception as e:
			print "updateCounter Error: %s" % e

	def Reload( self, sender ):
		try:
			self.w.List.set( self.listContent() )
			self.updateCounter()
		except Exception, e:
			Glyphs.showMacroWindow()
			print "Reload Error: %s" % e
	
	def Apply(self,sender):
		try:
			listOfFontInfos = self.w.List.get()
			selectedIndexes = self.w.List.getSelection()
			nothingIsSelected = False
		
			if len(selectedIndexes) == 0:
				nothingIsSelected = True
		
			for fontInfoIndex in range(len(listOfFontInfos)):
				if fontInfoIndex in selectedIndexes or nothingIsSelected:
					thisFontInfo = listOfFontInfos[fontInfoIndex]
					thisFont = thisFontInfo["fontObj"]
					for thisKey in thisFontInfo.keys():
						if thisKey != "fontObj":
							fontPropertyString = "thisFont.%s" % thisKey
							currentFontValue = eval( fontPropertyString )
							listValue = thisFontInfo[ thisKey ]
							if currentFontValue != listValue:
								print "Setting %s to '%s' in %s." % ( thisKey, listValue, thisFont )
								exec( "%s = listValue" % fontPropertyString )
			self.updateCounter()
		except Exception as e:
			print "Apply Error: %s" % e
		

FontInfoOverview()