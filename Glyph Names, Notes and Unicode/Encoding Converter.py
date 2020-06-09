#MenuTitle: Encoding Converter
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Converts old expert 8-bit encodings into Glyphs nice names.
"""

import vanilla, codecs

AXtDefault = """
Syntax:
- Freely write comments and empty lines
- Rename: Lines containing a dash (-) followed by a greater sign (>) will trigger glyph renaming, with or without spaces between names
- Recipe: Lines containing glyph recipes with plus (+) and equals (=) will be treated like in Glyph > Add Glyphs... as long as the do not contain any space
- Recipes will overwrite existing glyphs. Renamings will create a number-suffixed glyph if a glyph with the same name already exists.
 



breve -> kashida-ar
grave -> kashida-ar.alt

A -> hamza-ar
D -> hamzaabove-ar
E -> hamzabelow-ar
C -> highhamza-ar
q -> shadda-ar
s -> shaddaFatha-ar
v -> shaddaFathatan-ar
t -> shaddaDamma-ar
w -> shaddaDammatan-ar
u -> shaddaKasra-ar
x -> shaddaKasratan-ar
p -> kasra-ar
m -> kasratan-ar
n -> fatha-ar
k -> fathatan-ar
o -> damma-ar
l -> dammatan-ar
r -> sukun-ar
y -> wasla-ar
B -> madda-ar

G -> alef-ar
Eacute -> alef-ar.fina

Udieresis -> beh-ar
H -> beh-ar.init
Ntilde -> beh-ar.medi
Odieresis -> beh-ar.fina

I -> tehMarbuta-ar
aacute -> tehMarbuta-ar.fina

adieresis -> teh-ar
J -> teh-ar.init
agrave -> teh-ar.medi
acircumflex -> teh-ar.fina

ccedilla -> theh-ar
K -> theh-ar.init
atilde -> theh-ar.medi
aring -> theh-ar.fina

ecircumflex -> jeem-ar
L -> jeem-ar.init
eacute -> jeem-ar.medi
egrave -> jeem-ar.fina

igrave -> hah-ar
M -> hah-ar.init
edieresis -> hah-ar.medi
iacute -> hah-ar.fina

ntilde -> khah-ar
N -> khah-ar.init
icircumflex -> khah-ar.medi
idieresis -> khah-ar.fina

O -> dal-ar
oacute -> dal-ar.fina

P -> thal-ar
ograve -> thal-ar.fina

Q -> reh-ar
ocircumflex -> reh-ar.fina

R -> zain-ar
otilde -> zain-ar.fina

(for seen, sheen, sad, dad, see further below)

bullet -> tah-ar
W -> tah-ar.init
sterling -> tah-ar.medi
section -> tah-ar.fina

registered -> zah-ar
X -> zah-ar.init
paragraph -> zah-ar.medi
germandbls -> zah-ar.fina

acute -> ain-ar
Y -> ain-ar.init
copyright -> ain-ar.medi
trademark -> ain-ar.fina

AE -> ghain-ar
Z -> ghain-ar.init
dieresis -> ghain-ar.medi
notequal -> ghain-ar.fina

plusminus -> feh-ar
a -> feh-ar.init
Oslash -> feh-ar.medi
infinity -> feh-ar.fina

yen -> qaf-ar
b -> qaf-ar.init
lessequal -> qaf-ar.medi
greaterequal -> qaf-ar.fina

summation -> kaf-ar
c -> kaf-ar.init
mu -> kaf-ar.medi
partialdiff -> kaf-ar.fina

integral -> lam-ar
d -> lam-ar.init
product -> lam-ar.medi
pi -> lam-ar.fina

Omega -> meem-ar
e -> meem-ar.init
ordfeminine -> meem-ar.medi
ordmasculine -> meem-ar.fina

questiondown -> noon-ar
f -> noon-ar.init
ae -> noon-ar.medi
oslash -> noon-ar.fina

radical -> heh-ar
g -> heh-ar.init
exclamdown -> heh-ar.medi
logicalnot -> heh-ar.fina

h -> waw-ar
florin -> waw-ar.fina

i -> alefMaksura-ar
approxequal -> alefMaksura-ar.fina

ellipsis -> yeh-ar
j -> yeh-ar.init
guillemetleft -> yeh-ar.medi
guillemetright -> yeh-ar.fina
guillemotleft -> yeh-ar.medi
guillemotright -> yeh-ar.fina

Ccedilla -> yehHamzaabove-ar
F -> yehHamzaabove-ar.init
Adieresis -> yehHamzaabove-ar.medi
Aring -> yehHamzaabove-ar.fina

ring -> peh-ar
greater -> peh-ar.init
DEL -> peh-ar.medi
dotaccent -> peh-ar.fina

caron -> tcheh-ar
cedilla -> tcheh-ar.init
hungarumlaut -> tcheh-ar.medi
ogonek -> tcheh-ar.fina

less -> veh-ar
quotedbl -> veh-ar.init
numbersign -> veh-ar.medi
ampersand -> veh-ar.fina



Numbers and Punctuation:
zero -> zero-ar
one -> one-ar
two -> two-ar
three -> three-ar
four -> four-ar
five -> five-ar
six -> six-ar
seven -> seven-ar
eight -> eight-ar
nine -> nine-ar

comma -> comma-ar
semicolon -> semicolon-ar
question -> question-ar
nonbreakingspace -> nbspace


Ligatures:
Edieresis -> yeh_meem-ar
Aacute -> yeh_meem-ar.init
Uacute -> yeh_noon-ar.feh
Ograve -> yeh_reh-ar.fina
quoteright -> lam_alef-ar
Oacute -> lam_alef-ar.fina
fraction -> lam_meem-ar
Ydieresis -> lam_meem-ar.init
Ugrave -> lam_meem_hah-ar.init
dotlessi -> lam_meem_khah-ar.init
Ucircumflex -> lam_meem_jeem-ar.init
ydieresis -> lam_khah-ar.init
guilsinglleft -> lam_yeh-ar
currency -> lam_alefMaksura-ar
divide -> lam_jeem-ar.init
lozenge -> lam_hah-ar.init
circumflex -> lam_lam_heh-ar
Otilde -> beh_meem-ar
Atilde -> beh_meem-ar.init
Iacute -> beh_noon-ar.fina
Egrave -> beh_reh-ar.fina
oe -> teh_jeem-ar
OE -> teh_jeem-ar.init
emdash -> teh_hah-ar
endash -> teh_hah-ar.init
Idieresis -> teh_noon-ar.fina
Icircumflex -> teh_reh-ar.fina
quotedblleft -> teh_meem-ar.init
quotedblright -> teh_meem-ar
Igrave -> theh_reh-ar.fina
f_i -> meem_hah-ar.init
f_l -> meem_khah-ar.init
guilsinglright -> meem_jeem-ar.init
periodcentered -> meem_meem-ar
daggerdbl -> meem_meem-ar.init
Ecircumflex -> noon_yeh-ar
quotedblbase -> noon_jeem-ar
quotesinglbase -> noon_jeem-ar.init
Acircumflex -> noon_meem-ar
perthousand -> noon_meem-ar.init
apple -> noon_noon-ar.fina
Ocircumflex -> noon_reh-ar.fina
quoteleft -> feh_yeh-ar


Not sure about these letters - can someone check please:
Some (?) of them need to be combined with half2 further below.
S -> _seen-ar.init.half1
ugrave -> _seen-ar.medi.half1
T -> _sheen-ar.init.half1
ucircumflex -> _sheen-ar.medi.half1
U -> _sad-ar.init.half1
udieresis -> _sad-ar.medi.half1
macron -> block
V -> _dad-ar.init.half1
dagger -> _dad-ar.medi.half1
tilde -> dad-ar.fina
! tilde is not always dad, sometimes it is a complete phrase.

These are supposed to be combined with the seen/sheen/sad/dad above:
cent -> noonghunna-ar
degree -> _seen-ar.medi.half2
odieresis -> _seen_reh-ar.fina.half2
uacute -> _seen_zain-ar.fina.half2

These must come last, and in this very order, otherwise they collide with a previous rename:
asciicircum -> comma
z -> guillemetleft
braceleft -> guillemetright
bar -> quotedblleft
braceright -> quotedblright


asterisk -> multiply
at -> asterisk

underscore -> divide
asciitilde -> underscore
percent -> percent-ar

bracketleft -> bracketright.xxx
bracketright -> bracketleft
bracketright.xxx -> bracketright


These seem to stay the same, not sure if true for all AXt fonts:
Delta -> Delta
backslash -> backslash
colon -> colon
exclam -> exclam
period -> period
quotesingle -> quotesingle
slash -> slash
parenleft -> parenleft
parenright -> parenright
hyphen -> hyphen
dollar -> dollar
equal -> equal
plus -> plus

fi -> meem_hah-ar.init
fl -> meem_khah-ar.init



RECIPES:

_seen-ar.init.half1+noonghunna-ar=seen-ar
_seen-ar.init.half1+_seen-ar.medi.half2=seen-ar.init
_seen-ar.medi.half1+_seen-ar.medi.half2=seen-ar.medi
_seen-ar.medi.half1+noonghunna-ar=seen-ar.fina
_sheen-ar.init.half1+noonghunna-ar=sheen-ar
_sheen-ar.init.half1+_seen-ar.medi.half2=sheen-ar.init
_sheen-ar.medi.half1+_seen-ar.medi.half2=sheen-ar.medi
_sheen-ar.medi.half1+noonghunna-ar=sheen-ar.fina
_sad-ar.init.half1+noonghunna-ar=sad-ar
_sad-ar.init.half1+_seen-ar.medi.half2=sad-ar.init
_sad-ar.medi.half1+_seen-ar.medi.half2=sad-ar.medi
_sad-ar.medi.half1+noonghunna-ar=sad-ar.fina
_dad-ar.init.half1+noonghunna-ar=dad-ar
_dad-ar.init.half1+_seen-ar.medi.half2=dad-ar.init
_dad-ar.medi.half1+_seen-ar.medi.half2=dad-ar.medi
_dad-ar.medi.half1+noonghunna-ar=dad-ar.fina

_seen-ar.init.half1+_seen_reh-ar.fina.half2=seen_reh-ar
_seen-ar.medi.half1+_seen_reh-ar.fina.half2=seen_reh-ar.fina
_seen-ar.init.half1+_seen_zain-ar.fina.half2=seen_zain-ar
_seen-ar.medi.half1+_seen_zain-ar.fina.half2=seen_zain-ar.fina
_sheen-ar.init.half1+_seen_reh-ar.fina.half2=sheen_reh-ar
_sheen-ar.medi.half1+_seen_reh-ar.fina.half2=sheen_reh-ar.fina
_sheen-ar.init.half1+_seen_zain-ar.fina.half2=sheen_zain-ar
_sheen-ar.medi.half1+_seen_zain-ar.fina.half2=sheen_zain-ar.fina
_sad-ar.init.half1+_seen_reh-ar.fina.half2=sad_reh-ar
_sad-ar.medi.half1+_seen_reh-ar.fina.half2=sad_reh-ar.fina
_sad-ar.init.half1+_seen_zain-ar.fina.half2=sad_zain-ar
_sad-ar.medi.half1+_seen_zain-ar.fina.half2=sad_zain-ar.fina
_dad-ar.init.half1+_seen_reh-ar.fina.half2=dad_reh-ar
_dad-ar.medi.half1+_seen_reh-ar.fina.half2=dad_reh-ar.fina
_dad-ar.init.half1+_seen_zain-ar.fina.half2=dad_zain-ar
_dad-ar.medi.half1+_seen_zain-ar.fina.half2=dad_zain-ar.fina
"""

def saveFileInLocation(content="", filePath="~/Desktop/test.txt"):
	with codecs.open(filePath, "w", "utf-8-sig") as thisFile:
		print("💾 Writing:", thisFile.name)
		thisFile.write( content )
		thisFile.close()
	return True

def readFileFromLocation(filePath="~/Desktop/test.txt"):
	content = ""
	with codecs.open(filePath, "r", "utf-8-sig") as thisFile:
		print("💾 Reading:", thisFile.name)
		content = thisFile.read()
		thisFile.close()
	return content

class EncodingConverter( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 550
		windowHeight = 260
		windowWidthResize  = 1000 # user can resize width by this value
		windowHeightResize = 1000 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Encoding Converter", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.EncodingConverter.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 8, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), "Enter conversion text (see tooltips):", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.recipe = vanilla.TextEditor( (1, linePos, -1, -inset*3), text="", callback=self.SavePreferences, checksSpelling=False )
		self.w.recipe.getNSTextView().setToolTip_("- Freely write comments and empty lines\n- Rename: Lines containing a dash (-) followed by a greater sign (>) will trigger glyph renaming, with or without spaces between names\n- Recipe: Lines containing glyph recipes with plus (+) and equals (=) will be treated like in Glyph > Add Glyphs... as long as the do not contain any space\n- Recipes will overwrite existing glyphs. Renamings will create a number-suffixed glyph if a glyph with the same name already exists.")
		self.w.recipe.getNSScrollView().setHasVerticalScroller_(1)
		self.w.recipe.getNSScrollView().setHasHorizontalScroller_(1)
		self.w.recipe.getNSScrollView().setRulersVisible_(0)
		
		legibleFont = NSFont.legibileFontOfSize_(NSFont.systemFontSize())
		textView = self.w.recipe.getNSTextView()
		textView.setFont_(legibleFont)
		textView.setHorizontallyResizable_(1)
		textView.setVerticallyResizable_(1)
		textView.setAutomaticDataDetectionEnabled_(1)
		textView.setAutomaticLinkDetectionEnabled_(1)
		textView.setDisplaysLinkToolTips_(1)
		textSize = textView.minSize()
		textSize.width = 1000
		textView.setMinSize_(textSize)
		# textView.textContainer().setWidthTracksTextView_(0)
		# textView.textContainer().setContainerSize_(textSize)
		
		# Run Button:
		self.w.openButton = vanilla.Button( (inset, -20-inset, 110, -inset), "Open Text…", sizeStyle='regular', callback=self.importEncoding )
		self.w.saveButton = vanilla.Button( (inset+120, -20-inset, 110, -inset), "Save Text…", sizeStyle='regular', callback=self.exportEncoding )
		self.w.resetButton = vanilla.Button( (inset+260, -20-inset, 100, -inset), "Reset Text", sizeStyle='regular', callback=self.resetEncoding )
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Convert Font", sizeStyle='regular', callback=self.EncodingConverterMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Encoding Converter' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.EncodingConverter.recipe"] = self.w.recipe.get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.EncodingConverter.recipe", AXtDefault.strip())
			
			# load previously written prefs:
			self.w.recipe.set( Glyphs.defaults["com.mekkablue.EncodingConverter.recipe"] )
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False
	
	def exportEncoding(self, sender=None):
		self.SavePreferences()
		filePath = GetSaveFile(message="Save Renaming Scheme", ProposedFileName="glyph name conversion.txt", filetypes=("txt"))
		if filePath:
			fileContent = Glyphs.defaults["com.mekkablue.EncodingConverter.recipe"]
			saveFileInLocation(content=fileContent, filePath=filePath)
	
	def importEncoding(self, sender=None):
		filePath = GetOpenFile(message="Open Renaming Scheme", allowsMultipleSelection=False, filetypes=("txt"))
		if filePath:
			fileContent = readFileFromLocation(filePath=filePath)
			if fileContent:
				Glyphs.defaults["com.mekkablue.EncodingConverter.recipe"] = fileContent
				self.LoadPreferences()
			else:
				Message(title="File Error", message="File could not be read. Perhaps empty?", OKButton=None)
				
	
	def resetEncoding(self, sender=None):
		Glyphs.defaults["com.mekkablue.EncodingConverter.recipe"] = AXtDefault.strip()
		self.LoadPreferences()

	def freeGlyphName( self, glyphName, glyphNameList ):
		"""
		Returns the first unused version of glyphName in glyphNameList.
		If necessary, adds a 3-digit extension to the name
		or increases the existing number extension by one.
		"""
	
		if glyphName in glyphNameList:
			try:
				# increase the .000 extension
				increasedGlyphName = glyphName[:-3] + ( "%.3d" % int( glyphName[-3:] ) + 1 )
				return freeGlyphName( increasedGlyphName, glyphNameList )
			except:
				# has no .000 extension yet:
				increasedGlyphName = glyphName + ".001"
				return freeGlyphName( increasedGlyphName, glyphNameList )
		return glyphName

	def glyphRename( self, source, target, font ):
		"""Renames source to target."""
		thisGlyph = font.glyphs[ source ]
		existingGlyphNames = [ g.name for g in Font.glyphs ]
		targetString = self.freeGlyphName( target, existingGlyphNames )
	
		try:
			thisGlyph.name = targetString
			thisGlyph.export = targetString[0]!="_"
			print( "🙌 Renamed glyph: %s → %s" % (source, targetString))
			return 1
		except Exception as e:
			if "NoneType" in str(e):
				e = "No glyph with that name."
			print("❌ Failed to rename %s to %s. (%s)" % (source, targetString, e))
			return 0

	def isValidGlyphName(self, glyphName):
		validCharacters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-."
		if len(glyphName)==0 or glyphName[0]=="-":
			return False
		for letter in glyphName:
			if not letter in validCharacters:
				return False
		return True

	def EncodingConverterMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ 'Encoding Converter' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Encoding Converter Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
				
				thisFont.disableUpdateInterface()

				thisFont.setDisablesNiceNames_(1)
				nameChangeString = Glyphs.defaults["com.mekkablue.EncodingConverter.recipe"]
				countRenames = 0
				countRecipes = 0
				
				# parse lines of nameChangeString:
				for line in nameChangeString.splitlines():
					try:
						if line.strip(): # skip empty lines
							
							# RENAME LINE:
							if "->" in line:
								nameList = line.split("->")
								sourceName = nameList[0].strip()
								targetName = nameList[1].strip()
								if sourceName != targetName:
									countRenames += self.glyphRename( sourceName, targetName, thisFont )
						
							# GLYPH RECIPE:
							elif "=" in line and not " " in line:
								sourceRecipe, targetGlyph = line.strip().split("=")
								if self.isValidGlyphName(targetGlyph):
									sourceGlyphNames = sourceRecipe.split("+")
									if all([thisFont.glyphs[n] for n in sourceGlyphNames]):
										exportStatus = targetGlyph[0]!="_"
										glyph = thisFont.glyphs[targetGlyph]
										if glyph:
											print("🔠 overwritten: %s" % targetGlyph)
										else:
											glyph = GSGlyph()
											glyph.name = targetGlyph
											thisFont.glyphs.append(glyph)
											print("🔠 created: %s" % targetGlyph)
										for layer in glyph.layers:
											if layer.isMasterLayer or layer.isSpecialLayer:
												layer.clear()
												for compName in sourceGlyphNames:
													comp = GSComponent(compName)
													layer.components.append(comp)
										countRecipes += 1
									else:
										print("⚠️ Could not create recipe for %s. Not all ingredients in font: %s." % (targetGlyph, ", ".join(sourceGlyphNames)))
								else:
									print("⚠️ invalid glyph name: %s. Skipping." % targetGlyph)
					except:
						pass
				
				thisFont.enableUpdateInterface()
				self.w.close() # delete if you want window to stay open

			# Final report:
			Glyphs.showNotification( 
				"%s: Done" % (thisFont.familyName),
				"Renamed %i glyph%s, built %i glyph recipe%s. Details in Macro Window" % (
					countRenames,
					"" if countRenames==1 else "s",
					countRecipes,
					"" if countRecipes==1 else "s",
					),
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Encoding Converter Error: %s" % e)
			import traceback
			print(traceback.format_exc())

EncodingConverter()