# MenuTitle: Pangram Helper
__doc__ = """
Helps you write pangrams by displaying which letters are still missing.
"""

import random
import vanilla
from AppKit import (
	NSFont, NSStringPboardType, NSPasteboard, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut
)
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject

nonJoiner = "\u200c"

# (language, letters) pairs, separators are marked with "---":
fullAlphabets = (
	("English, basic Latin", "abcdefghijklmnopqrstuvwxyz"),
	("Estonian", "abdefghijklmnoprstuvzõäöü"),
	("Spanish", "abcdefghijklmnñopqrstuvwxyz"),
	("Croatian, Serbian Latin", "abcčćdđefghijklmnoprsštuvzž"),
	("Maltese", "abċdefġghħijklmnopqrstuvwxżz"),
	("Welsh", "abcdefghijlmnoprstuwyâêîôŵŷë"),
	("Swedish", "abcdefghijklmnopqrstuvwxyzåäö"),
	("Danish, Norwegian", "abcdefghijklmnopqrstuvwxyzæøå"),
	("Turkish", "abcçdefgğhıijklmnoöprsştuüvyz"),
	("German", "abcdefghijklmnopqrstuvwxyzäöüß"),
	("Romanian", "aăâbcdefghiîjklmnopqrsștțuvwxyz"),
	("Polish", "aąbcćdeęfghijklłmnńoóprsśtuwyzźż"),
	("Icelandic", "aábdðeéfghiíjklmnoóprstuúvxyýþæö"),
	("Lithuanian", "aąbcčdeęėfghiįyjklmnoprsštuųūvzž"),
	("Latvian", "aābcčdeēfgģhiījkķlļmnņoprsštuūvzž"),
	("Hungarian", "aábcdeéfghiíjklmnoóöőpqrstuúüűvwxyz"),
	("Portuguese", "abcdefghijklmnopqrstuvwxyzáàâãçéêíóôõú"),
	("French", "abcdefghijklmnopqrstuvwxyzàâçéèêëîïôùûüÿœ"),
	("Czech", "aábcčdďeéěfghiíjklmnňoópqrřsštťuúůvwxyýzž"),
	("Slovak", "aáäbcčdďeéfghiíjklĺľmnňoóôpqrŕsštťuúvwxyýzž"),
	("---", ""),
	("Greek", "αβγδεζηθικλμνξοπρςστυφχψω"),
	("---", ""),
	("Russian", "абвгдеёжзийклмнопрстуфхчцшщьыъэюя"),
	("Serbian Cyrillic", "абвгдђежзијклљмнњопрстћуфхцчџш"),
	("Bulgarian", "абвгдежзийклмнопрстуфхцчшщъьюя"),
	("Ukrainian", "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"),
	("---", ""),
	("Hebrew", "אבגדהוזחטיכלמנסעפצקרשת"),
	("Arabic", "ا‌ب‌ت‌ث‌ج‌ح‌خ‌د‌ذ‌ر‌ز‌س‌ش‌ص‌ض‌ط‌ظ‌ع‌غ‌ف‌ق‌ك‌ل‌م‌ن‌ه‌و‌ي"),
)


# the left-to-right mark keeps Hebrew and Arabic entries from turning the whole title right-to-left:
leftToRightMark = "\u200e"
menuTitles = ["---" if language == "---" else "%s%s  %s" % (leftToRightMark, letters, language) for language, letters in fullAlphabets]


pangrams = {  # verified to contain every letter of the alphabet of the same name
	"English, basic Latin": (
		"The quick brown fox jumps over the lazy dog.",
		"Pack my box with five dozen liquor jugs.",
		"How vexingly quick daft zebras jump!",
		"Sphinx of black quartz, judge my vow.",
		"Jackdaws love my big sphinx of quartz.",
		"The five boxing wizards jump quickly.",
		"Waltz, bad nymph, for quick jigs vex.",
		"Glib jocks quiz nymph to vex dwarf.",
		"Amazingly few discotheques provide jukeboxes.",
		"Crazy Fredrick bought many very exquisite opal jewels.",
	),
	"Estonian": (
		"Põdur Zagrebi tšellomängija-följetonist Ciqo külmetas kehvas garaažis.",
		"Jõuka büroo füüsik Gunnar Hõbedane säästis kõrvalt mõne pika öö zebra-fänne.",
		"Söör Gunnar Zhdanov, kõrge füüsik, jälgis hõredalt väsinud pükse ja bumerangi.",
	),
	"Spanish": (
		"El pingüino Wenceslao hizo kilómetros bajo exhaustiva lluvia y frío, añoraba a su querido cachorro.",
		"Jovencillo emponzoñado de whisky: ¡qué figurota exhibe!",
		"Benjamín pidió una bebida de kiwi y fresa; Noé, sin vergüenza, la más exquisita champaña del menú.",
	),
	"Croatian, Serbian Latin": (
		"Gojazni đačić s biciklom drži hmelj i finu vatu u džepu pred šoljom čaja.",
		"Fijuče vatra jer đurđevak ćuti, žbunje češljam, ljuta nježna ćud, hodam pored gospodina Zlatka, gdje cvate bor.",
		"Gojazni šef čvrsto ćuti i hrče, žuti bumbar đak djeluje pred cestom.",
	),
	"Maltese": (
		"Il-ħajja ta' Ġużeppi tkun tajba: jixtieq jaqbeż ċavetta żgħira, kelma ħafna, dwiefer fuq post, hawn zija.",
		"X'wasal Ċensu bil-ħalib, ġab ċavetta żgħira, jaqbad kelma u dwiefer, fuq il-post u l-pjazza hawn.",
		"Hawn zija ħadet ċavetta żgħira, wasslet ġbejna lil Ċensu, u qalet: x'jippreferi, lbies kbir u dgħajsa, mod, mur?",
	),
	"Welsh": (
		"Jôc dda gan Noël am gŵr hynod ddewr yn y tŷ, â mêl îr, bydd plant ffrind yn cael cacen ysblennydd ur.",
		"Dewch â'ch ŵyn a'ch ŷd i'r ffair, ni fyddwn yn ôl cyn i'r haul fachlud, a gwîr mêl Noël, jam, tŷ pob bachgen stryd.",
		"Jôc dda gan Noël am gŵr hynod ddewr yn y tŷ, â mêl îr, bydd plant ffrind yn cael cacen ysblennydd, un.",
		"Pa ŵr bach a'i fêl hynod, ffrind, dwy ffon â'r lleill, Noël gwîr jam, tŷ cyflym, ôl, sudd.",
	),
	"Swedish": (
		"Yxmördaren Julia Blomqvist på fäktning i Schweiz.",
		"Ålänningen Wiktor fick xylofon och jazzkväll i bygden, quiz, pappa öppnade musik.",
		"Quizdeltagarna fick pizza, vodka och gäddfisk med citron på ålderdomshemmet, öppet, jag, by, wc, xylofon.",
		"Quizdeltagarna Åsa och Jörgen fick pizza, vodka och gäddfisk med citron, xylofon, by, wc.",
	),
	"Danish, Norwegian": (
		"Quizdeltagerne spiste jordbær med fløde, mens cirkusklovnen Walther spillede på xylofon.",
		"Høj bly gom vandt fræk sexquiz på wc.",
		"Vår sære Zulu fra badeøya spilte jo whist og quickstep i min taxi.",
	),
	"Turkish": (
		"Pijamalı hasta yağız şoföre çabucak güvendi.",
		"Hızlıca dönüp ağır yüklü şeftali çuvalı gezdi, ayrıca zil sesi kuvvetle bozdu, jandarma meydanda.",
		"Vakfın çoğu bu huysuz genci plajda kızdırdı, şöyle zorlu müjde, taze tütün.",
	),
	"German": (
		"Zwölf Boxkämpfer jagen Viktor quer über den großen Sylter Deich.",
		"Victor jagt zwölf Boxkämpfer quer über den großen Sylter Deich.",
		"Falsches Üben von Xylophonmusik quält jeden größeren Zwerg, süß und bös.",
	),
	"Romanian": (
		"Muzicologă în bej vând whisky și tequila, preferându-l pe Zâmbețe fix.",
		"Ștefan, țăran, bate și vinde whisky, quasi-prețuit în jazz, ca xilofon, bâzâie gâgâind muzică.",
		"Încă vând gheața și cafeaua stăpânului pe țară, Wilhelm, xilofonul îți place, jocul, bâzâie, muzica, quark, yoga.",
	),
	"Polish": (
		"Pchnąć w tę łódź jeża lub ośm skrzyń fig.",
		"Jeżu klątw, spłódź Finom część gry hańb!",
		"Mężny bądź chroń pułk twój i sześć flag.",
	),
	"Icelandic": (
		"Kæmi ný öxi hér ykist þjófum nú bæði víl og ádrepa.",
		"Þjófurinn Ólafur týndi mjúkum kexpökkum og ýsubeini; kæmi óð, ég sé öxi, hjól, ketill, mjólk, pönnukaka, bæði, víl, yfir ská.",
		"Víkingurinn Ólafur hjó öxi í ýsubein, týndi mjúkum kexpökkum, þjófurinn ég sæi, bæði, ádrepa, é, mjólk, Ægir, ketill, og yfir.",
	),
	"Lithuanian": (
		"Įlinkdama fechtuotojo špaga sublykčiojusi pragręžė apvalų arbūzą.",
		"Ežiukas ūžė, gražuolė žvelgia, ąžuolų šaknys driekiasi, būtų čia fėja, įpjautas pyragas, čiulbėdama ęgzas, hm, cukrus.",
		"Ąžuolų žvaigždės čiulba, ūkininkas įkaitęs spjovė cukrų, fėjos ėmė šaukti, hm, by, bet ręžė pyragus, zuikis.",
	),
	"Latvian": (
		"Muļķa hipiji mēģina brīvi nogaršot celofāna žņaudzēju, ūdenī čaklā, kaķis sēž.",
		"Čaukstošs ķirsis sāk plaukt ņurdošā kaļķa ūdens brīnumā, ģimene, mēs vēl dzirdam cirka fūriju, hej, vīns, pāvils, žūpa, gads.",
		"Čaklais ūdrs ķēra zaļu ķirbi, šķiet, ļoti ātri; ņem ģitāru, dziedi tā, ka brīnums cits, fūrija, hei, vāvere, žūpa, gads.",
	),
	"Hungarian": (
		"Egy hűtlen vejét fülöncsípő, dühös mexikói úr Wesselényinél mázol Quitóban.",
		"Jó foxim és don Quijote húszwattos ívlámpákat árulnak Bűvös-Vörösön, gőgös cégnek gyümölcs.",
		"Ó, a dühös úri cipőpolcos Wesselényi hűs ív mellett, Pál ősz képét kérte, qvíz, fax, gyümölcs, bú, jó, uborka.",
		"Vajon mit érzett Zsuzsi, miközben egy kövér sün törölgette Quentin xilofonját: hűs, úri, dühös, őz, cipő, wc, ó, híd.",
	),
	"Portuguese": (
		"À noite, vovô Kowalsky vê o ímã cair no pé do pinguim queixoso e vovó põe açúcar no chá de tâmaras do jabuti feliz.",
		"Luís argüia à Júlia que «brações, fé, chá, óxido, pôr, zângão» eram palavras do português, kiwi, whisky, yoga.",
		"O velho Wenceslau, de pé, quis fazer açúcar de jabuticaba, mas só fumou kiwis e tâmaras, quando o ímã caiu na lição de ioga com óculos, avô, à vontade, põe, xadrez, yoga, está, fêmea.",
	),
	"French": (
		"Portez ce vieux whisky au juge blond qui fume sur son île intérieure, à côté de l'alcôve ovoïde, où les bûches se consument dans l'âtre, ce qui lui permet de penser à la cænogenèse de l'être dont il est question dans la cause ambiguë entendue à Moÿ, dans un capharnaüm qui, pense-t-il, diminue çà et là la qualité de son œuvre.",
		"Dès Noël où un zéphyr haï me vêt de glaçons würmiens, je dîne d'exquis rôtis de bœuf au kir, à l'aÿ d'âge mûr, &cætera.",
		"Le cœur déçu mais l'âme plutôt naïve, Louÿs rêva de crapaüter en canoë au delà des îles, près du mälström où brûlent les novæ, fée, xylophone, quiz, whisky, jazz, kiwi, gnôme.",
	),
	"Czech": (
		"Nechť již hříšné saxofony ďáblů rozezvučí síň úděsnými tóny waltzu, tanga a quickstepu.",
		"Příliš žluťoučký kůň úpěl ďábelské ódy, nechť fax Quido wolf gymnastika, jelení, zrno, vítr.",
		"Příliš žluťoučký kůň úpěl ďábelské ódy, tak Quido ze sklepa hrál waltz na xylofon, jenž ňuká, a Gustav vymění mák za cukr.",
	),
	"Slovak": (
		"Kŕdeľ šťastných ďatľov učí pri ústí Váhu mĺkveho koňa obhrýzať kôru a žrať čerstvé mäso, quick waltz xylofón, gyps, jóga, fúzy, óda.",
		"Kŕdeľ šťastných ďatľov učí pri ústí Váhu mĺkveho koňa obhrýzať kôru a žrať čerstvé mäso, kým Quido Wolf hrá jazz na xylofóne, ó gýč.",
		"Kŕdeľ šťastných ďatľov učí pri ústí Váhu mĺkveho koňa obhrýzať kôru a žrať čerstvé mäso, kým Wolf z Quita hrá na xylofón, ó gýč, jazz.",
		"Ľúbivý ďateľ Wolfgang prežije chladné ráno v chyži, žuje fazuľu, ôsmy kúsok pekného zelenáča, rázne sŕka mäso, ó, gýč, quark a xylofón, hĺbka, ňuňu, väčšie sťa, čaj, nízky.",
	),
	"Greek": (
		"Ταχίστη αλώπηξ βαφής ψημένη γη, δρασκελίζει υπέρ νωθρού κυνός.",
		"Ξεσκεπάζω την ψυχοφθόρα βδελυγμία αυτής της πόλης",
		"Ένα ξύλινο πλοίο ψάχνει λιμάνι στη θάλασσα, φορτωμένο χαρά, βροχή, γη, δρόμους και ζωή.",
	),
	"Russian": (
		"Съешь же ещё этих мягких французских булок, да выпей чаю.",
		"Эх, чужак, общий съём цен шляп (юфть) – вдрызг!",
		"Эй, жлоб! Где туз? Прячь юных съёмщиц в шкаф.",
		"Любя, съешь щипцы, — вздохнёт мэр, — кайф жгуч.",
	),
	"Serbian Cyrillic": (
		"Ајшо, лепото и чежњо, за љубав срца мог дођи у Хаџиће на кафу.",
		"Љубазни фењерџија чађавог лика хоће да ми покаже штос са Ђуром и цркву.",
		"Ђоле, јеж и пас гризу хлеб, зној, нож, мач; ту ћутљив шљивар чува џак цвећа и фрулу, дању њушка.",
	),
	"Bulgarian": (
		"Ах, чудна българска земьо, полюшвай цъфтящи жита!",
		"Жълтата дюля беше щастлива, че пухът, който цъфна, замръзна в сярната пещ край гьола.",
		"Шофьор жигуло цъкаше вяло, а бай Йордан гледаше бъдещето си, ядеше хляб с мед, пиеше чай и слушаше юнашки песни, зелен.",
	),
	"Ukrainian": (
		"Чуєш їх, доцю, га? Кумедна ж ти, прощайся без ґольфів!",
		"Щойно їжак з'їв хліб, фея Зіна ґречно подякувала ціпакові; юність, цап, шум, лось, жах, гей, єдиний дивак.",
		"Гей, чуєш, їжак з'їв кілька яблук і ґречно подякував фею Зіні, ціпак щойно знайшов юшку, дивак, єдиний, щастя, мох, хата.",
	),
	"Hebrew": (
		"דג סקרני שט בים מאוכזב ולפתע מצא לו חברה איך הקליטה",
		"זה כיף סתם לשמוע איך תנצח קרפד עץ שטוח בגן",
		"גדי ובני אהבו לשחק בסלט חמוץ, עד שקפצו פרחים צהובים ביער, זה כתב.",
	),
	"Arabic": (
		"نص حكيم له سر قاطع وذو شأن عظيم مكتوب على ثوب أخضر ومغلف بجلد أزرق",
		"صِف خَلقَ خَودٍ كَمِثلِ الشمسِ إذ بَزَغَت يَحظى الضَجيعُ بها نَجلاءَ مِعطارِ",
		"أبجد هوز حطي كلمن سعفص قرشت ثخذ ضظغ",
	),
}


class PangramHelper(mekkaObject):
	prefDict = {
		"alphabetChoice": 0,
		"pangram": "The quick brown fox jumps over the lazy dog.",
	}
	title = "Pangram Helper"
	alphabet = fullAlphabets[0][1]

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 176  # 20% less than before
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 500  # user can resize height by this value
		self.w = vanilla.Window(
			(windowWidth, windowHeight),  # default window size
			self.title,  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset = 15

		self.w.alphabetChoice = vanilla.PopUpButton("auto", menuTitles, sizeStyle="small", callback=self.updateMissingLetters)
		self.w.missingLetters = vanilla.TextBox("auto", "Missing: %s" % self.alphabet, sizeStyle="small")
		self.w.missingLetters.setToolTip(
			"Status of the pangram.\n"
			"🔤 Missing: the letters of the alphabet that do not occur yet.\n"
			"✅ followed by a number: all letters are used; the number is how many letters the text contains in total.\n"
			"over: letters that occur more than once, grouped by how often, e.g. ‘2de 3a’ means d and e occur twice, a three times."
		)
		# a long report is truncated instead of widening the window:
		self.w.missingLetters.getNSTextField().setContentCompressionResistancePriority_forOrientation_(
			NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal
		)
		self.w.pangram = vanilla.TextEditor("auto", "The quick brown fox jumps over the lazy dog.", checksSpelling=True, callback=self.updateMissingLetters)

		self.w.pangram.getNSTextView().setFont_(NSFont.systemFontOfSize_(NSFont.systemFontSize()))  # regular size

		# Buttons:
		self.w.copyButton = vanilla.Button("auto", "Copy", callback=self.PangramHelperMain)
		self.w.tabButton = vanilla.Button("auto", "Open Tab", callback=self.PangramHelperMain)
		self.w.randomButton = vanilla.Button("auto", "Random", callback=self.randomPangram)
		self.w.randomButton.setToolTip("Replaces the text with a random pangram for the chosen language. Click again for another one.")
		self.w.setDefaultButton(self.w.tabButton)

		# all controls hug vertically, except the text editor, which takes the extra height when the window is resized:
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)
		self.w.pangram.getNSScrollView().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[alphabetChoice]-inset-|",
				"H:|-inset-[missingLetters]-inset-|",
				"H:|-1-[pangram]-1-|",
				"H:|-inset-[randomButton(>=70)]-(>=gap)-[copyButton(>=70)]-gap-[tabButton(>=70)]-inset-|",
				"V:|-gap-[alphabetChoice]-row-[missingLetters]-row-[pangram(>=50)]-inset-[copyButton]-inset-|",
				"V:[tabButton]-inset-|",
				"V:[randomButton]-inset-|",
			],
			metrics={"inset": inset, "gap": 8, "row": 8},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.updateMissingLetters()
		self.w.open()
		self.w.pangram.selectAll()
		self.w.makeKey()

	def decompose(self, glyph):
		unicodeValue = "%04X" % ord(glyph)
		info = Glyphs.glyphInfoForUnicode(unicodeValue)
		if info.components:
			listOfCharacters = [c.unicharString() for c in info.components if c.category == "Letter"]
			return listOfCharacters
		return []

	def updateMissingLetters(self, sender=None):
		self.SavePreferences()

		# the entry may contain non-joiners, which keep Arabic letters from connecting:
		letters = fullAlphabets[self.pref("alphabetChoice")][1]
		self.alphabet = letters.replace(nonJoiner, "")
		separator = nonJoiner if nonJoiner in letters else ""

		if Glyphs.versionNumber >= 3:
			# Glyphs 3 code
			currentTextEntry = self.pref("pangram").lower()
		else:
			# Glyphs 2 code
			currentTextEntry = unicode(self.pref("pangram").lower())  # noqa: F821

		containedBaseLetters = ""
		for thisLetter in currentTextEntry:
			# letters listed in the alphabet count for themselves only, all others for their base letters:
			if ord(thisLetter) > 191 and thisLetter not in self.alphabet:
				components = self.decompose(thisLetter)
				containedBaseLetters += "".join(components)

		currentTextEntry += containedBaseLetters
		missingLetters = ""
		overLetters = {}  # count -> letters used that often
		for thisLetter in self.alphabet:
			count = currentTextEntry.count(thisLetter)
			if count == 0:
				missingLetters += thisLetter + separator
			elif count > 1:
				overLetters[count] = overLetters.get(count, "") + thisLetter + separator

		report = " ".join("%i%s" % (count, overLetters[count]) for count in sorted(overLetters))
		if missingLetters:
			status = "🔤 Missing: %s" % missingLetters
			if report:
				status += ", over: %s" % report
		else:
			letterCount = sum(currentTextEntry.count(thisLetter) for thisLetter in self.alphabet)
			status = "✅ %i" % letterCount
			if report:
				status += ", over: %s" % report
		self.w.missingLetters.set(status)

	def randomPangram(self, sender=None):
		language = fullAlphabets[self.pref("alphabetChoice")][0]
		currentText = self.w.pangram.get()
		candidates = [pangram for pangram in pangrams.get(language, ()) if pangram != currentText]
		if candidates:
			self.w.pangram.set(random.choice(candidates))
			self.updateMissingLetters()

	def PangramHelperMain(self, sender):
		try:
			myText = self.pref("pangram")

			if myText:
				if sender == self.w.copyButton:
					myClipboard = NSPasteboard.generalPasteboard()
					myClipboard.declareTypes_owner_([NSStringPboardType], None)
					myClipboard.setString_forType_(myText, NSStringPboardType)
				elif sender == self.w.tabButton:
					Glyphs.font.newTab(myText)
					self.w.close()  # delete if you want window to stay open
			else:
				Message("%s Error" % self.title, "The entered text is empty.", OKButton=None)

			self.SavePreferences()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("%s Error: %s" % (self.title, e))


PangramHelper()
