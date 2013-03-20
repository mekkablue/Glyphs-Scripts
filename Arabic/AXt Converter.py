#MenuTitle: AXt Converter
"""
Converts glyphs from AXt Encoding to modern Unicode.
Attention: this script is not yet finished.
Please add suggestions in the Github Wiki. Thx!
"""

nameChangeString = """
Note: You can put comments here too.
Only lines containing a dash (-) followed by a greater sign (>) will be interpreted.

breve -> tatweel-ar

A -> hamza-ar
D -> hamzaabove-ar
E -> hamzabelow-ar
C -> highhamzaabove-ar
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
bar -> parenleftaltone-ar
braceright -> parenrightaltone-ar



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
S -> seen-ar.init.half1
ugrave -> seen-ar.medi.half1
T -> sheen-ar.init.half1
ucircumflex -> sheen-ar.medi.half1
U -> sad-ar.init.half1
udieresis -> sad-ar.medi.half1
macron -> dad-ar
V -> dad-ar.init.half1
dagger -> dad-ar.medi.half1
tilde -> dad-ar.fina
! tilde is not always dad, sometimes it is a complete phrase.

These are supposed to be combined with the seen/sheen/sad/dad above:
cent -> seen-ar.fina.half2
degree -> seen-ar.medi.half2
odieresis -> seen_reh-ar.fina.half2
uacute -> seen_zain-ar.fina.half2



In some AXt fonts, this seems to be a long tatweel.
Sometimes it is the same as tatweel:
grave -> tatweel-ar.alt



These must come last, and in this very order, otherwise they collide with a previous rename:
asciicircum -> comma
z -> guillemetleft
braceleft -> guillemetright

asterisk -> multiply
at -> asterisk

underscore -> divide
asciitilde -> underscore

bracketleft -> bracketright
bracketright -> bracketleft



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
percent -> percent
plus -> plus
"""


import GlyphsApp
Font = Glyphs.font

def freeGlyphName( glyphName, glyphNameList ):
	"""
	Returns the first unused version of glyphName.
	If necessary, adds a 3-digit extension to the name
	or increases the existing number extension by one.
	"""
	
	if glyphName in glyphNameList:
		try:
			# increase the .000 extension
			increasedGlyphName = glyphName[:-3] + ( "%.3d" % int( glyphName[-3:] ) + 1 )
			print "ATTENTION: %s already exists, trying to bump the extension ..." % ( glyphName )
			return freeGlyphName( increasedGlyphName, glyphNameList )
		except:
			# has no .000 extension yet:
			increasedGlyphName = glyphName + ".001"
			print "ATTENTION: %s already exists, trying %s ..." % ( glyphName, increasedGlyphName )
			return freeGlyphName( increasedGlyphName, glyphNameList )

	return glyphName


def glyphRename( source, target ):
	"""Renames source to target."""
	thisGlyph = Font.glyphs[ source ]
	existingGlyphNames = [ g.name for g in Font.glyphs ]
	targetString = freeGlyphName( target, existingGlyphNames )
	
	try:
		thisGlyph.name = targetString
		print "Renamed glyph: %s >>> %s" % (source, targetString)
	except Exception, e:
		if "NoneType" in e:
			e = "No glyph with that name."
		print "ERROR: Failed to rename %s to %s. (%s)" % (source, targetString, e)


# parse lines of nameChangeString:
for line in nameChangeString.splitlines():
	try:
		nameList = line.split("->")
		srcName = nameList[0].strip()
		tgtName = nameList[1].strip()
		if srcName != tgtName:
			glyphRename( srcName, tgtName )
	except:
		pass

print """
Try this recipe in Font > Generate glyphs:

seen-ar.fina.half2+seen-ar.init.half1=seen-ar
seen-ar.medi.half2+seen-ar.init.half1=seen-ar.init
seen-ar.medi.half2+seen-ar.medi.half1=seen-ar.medi
seen-ar.fina.half2+seen-ar.medi.half1=seen-ar.fina
seen-ar.fina.half2+sheen-ar.init.half1=sheen-ar
seen-ar.medi.half2+sheen-ar.init.half1=sheen-ar.init
seen-ar.medi.half2+sheen-ar.medi.half1=sheen-ar.medi
seen-ar.fina.half2+sheen-ar.medi.half1=sheen-ar.fina
seen-ar.fina.half2+sad-ar.init.half1=sad-ar
seen-ar.medi.half2+sad-ar.init.half1=sad-ar.init
seen-ar.medi.half2+sad-ar.medi.half1=sad-ar.medi
seen-ar.fina.half2+sad-ar.medi.half1=sad-ar.fina
seen-ar.fina.half2+dad-ar.init.half1=dad-ar.ss01
seen-ar.medi.half2+dad-ar.init.half1=dad-ar.init
seen-ar.medi.half2+dad-ar.medi.half1=dad-ar.medi
seen-ar.fina.half2+dad-ar.medi.half1=dad-ar.fina.ss01

seen_reh-ar.fina.half2+seen-ar.init.half1=seen_reh-ar
seen_reh-ar.fina.half2+seen-ar.medi.half1=seen_reh-ar.fina
seen_zain-ar.fina.half2+seen-ar.init.half1=seen_zain-ar
seen_zain-ar.fina.half2+seen-ar.medi.half1=seen_zain-ar.fina
seen_reh-ar.fina.half2+sheen-ar.init.half1=sheen_reh-ar
seen_reh-ar.fina.half2+sheen-ar.medi.half1=sheen_reh-ar.fina
seen_zain-ar.fina.half2+sheen-ar.init.half1=sheen_zain-ar
seen_zain-ar.fina.half2+sheen-ar.medi.half1=sheen_zain-ar.fina
seen_reh-ar.fina.half2+sad-ar.init.half1=sad_reh-ar
seen_reh-ar.fina.half2+sad-ar.medi.half1=sad_reh-ar.fina
seen_zain-ar.fina.half2+sad-ar.init.half1=sad_zain-ar
seen_zain-ar.fina.half2+sad-ar.medi.half1=sad_zain-ar.fina
seen_reh-ar.fina.half2+dad-ar.init.half1=dad_reh-ar
seen_reh-ar.fina.half2+dad-ar.medi.half1=dad_reh-ar.fina
seen_zain-ar.fina.half2+dad-ar.init.half1=dad_zain-ar
seen_zain-ar.fina.half2+dad-ar.medi.half1=dad_zain-ar.fina
"""
