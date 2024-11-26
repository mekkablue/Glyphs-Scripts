#MenuTitle: Mirror Spacer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Double checks and corrects spacings in mirrored glyphs such as: ()[]\{\}‘’“”«»‹›„“¿?¡!<>≤≥
"""

import vanilla

# http://www.unicode.org/Public/UNIDATA/BidiMirroring.txt
mirrorpairs = """
()[]{}«»‹›
༺༻༼༽᚛᚜
<>≤≥⁅⁆⁽⁾₍₎∼∽≂≃≒≓≔≕≦≧≨≩≪≫≮≯≰≱≲≳≴≵≶≷≸≹≺≻≼≽≾≿⊀⊁⊂⊃⊄⊅⊆⊇⊈⊉⊊⊋⊏⊐⊑⊒⊢⊣⊰⊱⊲⊳⊴⊵⊶⊷⋉⋊⋋⋌⋐⋑⋖⋗⋘⋙⋚⋛⋜⋝⋞⋟⋠⋡⋢⋣⋤⋥⋦⋧⋨⋩⋪⋫⋬⋭⋰⋱⌋⌈⌋⌊〈〉
❨❩❪❫❬❭❮❯❰❱❲❳❴❵⟃⟄⟅⟆⟈⟉⟋⟍⟓⟔⟕⟖⟝⟞⟢⟣⟤⟥⟦⟧⟨⟩⟪⟫⟬⟭⟮⟯⦃⦄⦅⦆⦇⦈⦉⦊⦋⦌⦍⦎⦏⦐⦑⦒⦓⦔⦕⦖⦗⦘⦤⦥⦨⦩⦪⦫⦬⦭⦮⦯⧀⧁⧄⧅⧏⧐⧑⧒⧔⧕⧘⧙⧚⧛⧨⧩⧼⧽⨫⨬⨭⨮⨴⨵⨼⨽⨾⩗⩘⩤⩥⩪⩫⩬⩭⩯⩰⩳⩴⩹⩺⩻⩼⩽⩾⩿⪀⪁⪂⪃⪄⪅⪆⪇⪈⪉⪊⪋⪌⪍⪎⪏⪐⪑⪒⪓⪔⪕⪖⪗⪘⪙⪚⪛⪜⪝⪞⪟⪠⪡⪢⪦⪧⪨⪩⪪⪫⪬⪭⪯⪰⪱⪲⪳⪴⪵⪶⪷⪸⪹⪺⪻⪼⪽⪾⪿⫀⫁⫂⫃⫄⫅⫆⫇⫈⫉⫊⫋⫌⫍⫎⫏⫐⫑⫒⫓⫔⫕⫖
⫷⫸⫹⫺⸂⸃⸄⸅⸌⸍⸜⸝⸢⸣⸤⸥⸦⸧⸨⸩
《》「」『』【】〔〕〖〗〘〙
〚〛﹙﹚﹛﹜﹝﹞﹤﹥（）＜＞［］｛｝｟｠｢｣
"""

class MirrorSpacer( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 260
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Mirror Spacer", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.MirrorSpacer.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.text_1 = vanilla.TextBox( (inset-1, linePos+2, 75, 14), "inset", sizeStyle='small' )
		self.w.popup_1 = vanilla.PopUpButton( (inset+80, linePos, 50, 17), [str(x) for x in range( 3, 12 )], callback=self.SavePreferences, sizeStyle='small' )
		self.w.edit_1 = vanilla.EditText( (inset+80+55, linePos, -inset, 19), "insert text here", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Run", sizeStyle='regular', callback=self.MirrorSpacerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Mirror Spacer' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.MirrorSpacer.popup_1"] = self.w.popup_1.get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.MirrorSpacer.popup_1", 0)
			
			# load previously written prefs:
			self.w.popup_1.set( Glyphs.defaults["com.mekkablue.MirrorSpacer.popup_1"] )
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def MirrorSpacerMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Mirror Spacer' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Mirror Spacer Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
				
				includeNonExporting = Glyphs.defaults["com.mekkablue.MirrorSpacer.includeNonExporting"]
				
				mirroredChars = mirroredChars.replace(" ","")
				charCount = len(mirroredChars)
				if charCount%2:
					charCount -= 1
					print("⚠️ Uneven number of mirrored characters entered. Will ignore last one: %s"%mirroredChars[-1])
					
				mirrorDict = {}
				for i in range(0,charCount,2):
					keyChar = Glyphs.niceGlyphName(mirroredChars[i])
					mirroredChar = Glyphs.niceGlyphName(mirroredChars[i+1])
					if mirrorDict[keyChar]:
						# append to existing list:
						if not mirroredChar in mirrorDict[keyChar]:
							mirrorDict[keyChar].append( mirroredChar )
					else:
						# create list if it didn't exist:
						mirrorDict[keyChar] = [ mirroredChar, ]
						
				for keyGlyphName in mirrorDict:
					mirroredGlyphNames = mirrorDict[keyGlyphName]
					keyGlyph = thisFont.glyphs[keyGlyphName]
					if not keyGlyph:
						print("⚠️ Glyph not in font: %s"%keyGlyphName)
					else:
						for mirroredGlyphName in mirroredGlyphNames:
							mirroredGlyph = thisFont.glyphs[mirroredGlyphName]
							if mirroredGlyph and (mirroredGlyph.export or includeNonExporting):
								for mid in [m.id for m in thisFont.masters]:
									keyLayer = 
									mirroredLayer=
									if mirroredLayer.isMasterLayer or mirroredLayer.isSpecialLayer:
										
					
					
	
			# Final report:
			Glyphs.showNotification( 
				"%s: Done" % (thisFont.familyName),
				"Mirror Spacer is finished. Details in Macro Window",
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Mirror Spacer Error: %s" % e)
			import traceback
			print(traceback.format_exc())

MirrorSpacer()