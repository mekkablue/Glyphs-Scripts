# MenuTitle: Set Kerning Groups
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Sets left and right kerning groups for all selected glyphs. In the case of compounds, will use the groups of the base components, otherwise makes an informed guess based on a built-in dictionary.
"""

# Copyright: Georg Seifert, 2010, www.schriftgestaltung.de Version 1.0
from GlyphsApp import Glyphs, Message

import traceback
verbose = False

alwaysExclude = (
	".notdef",
	".null",
	"CR",
	"periodcentered.loclCAT",
	"periodcentered.loclCAT.case",
	"periodcentered.loclCAT.sc",
)

Keys = [
	"B",
	"C",
	"D",
	"E",
	"F",
	"G",
	"I",
	"K",
	"L",
	"N",
	"P",
	"Q",
	"R",
	"Aacute",
	"Acaron",
	"Abreve",
	"Acircumflex",
	"Adieresis",
	"AE",
	"AEacute",
	"Agrave",
	"Amacron",
	"Aogonek",
	"Aring",
	"Aringacute",
	"Atilde",
	"Cacute",
	"Ccaron",
	"Ccedilla",
	"Ccircumflex",
	"Cdotaccent",
	"Dcaron",
	"Dcroat",
	"Eth",
	"Eacute",
	"Ebreve",
	"Ecaron",
	"Ecedilla",
	"Ecircumflex",
	"Edieresis",
	"Edotaccent",
	"Egrave",
	"Emacron",
	"Eogonek",
	"Gbreve",
	"Gcircumflex",
	"Gcommaaccent",
	"Gdotaccent",
	"Hbar",
	"Hcircumflex",
	"Iacute",
	"Ibreve",
	"Icaron",
	"Icircumflex",
	"Idieresis",
	"Idotaccent",
	"Igrave",
	"Imacron",
	"Iogonek",
	"Itilde",
	"IJ",
	"Jcircumflex",
	"Kcommaaccent",
	"Lacute",
	"Lcaron",
	"Lcommaaccent",
	"Ldot",
	"Lslash",
	"Nacute",
	"Ncaron",
	"Ncommaaccent",
	"Ntilde",
	"Oacute",
	"Obreve",
	"Ocircumflex",
	"Odieresis",
	"OE",
	"Ograve",
	"Ohorn",
	"Ohungarumlaut",
	"Omacron",
	"Oslash",
	"Oslashacute",
	"Otilde",
	"Racute",
	"Rcaron",
	"Rcommaaccent",
	"Sacute",
	"Scaron",
	"Scedilla",
	"Scommaaccent",
	"Scircumflex",
	"Tcaron",
	"Tcedilla",
	"Tcommaaccent",
	"Tbar",
	"Uacute",
	"Ubreve",
	"Ucaron",
	"Ucircumflex",
	"Udieresis",
	"Ugrave",
	"Uhungarumlaut",
	"Umacron",
	"Uogonek",
	"Uring",
	"Utilde",
	"Wacute",
	"Wcircumflex",
	"Wdieresis",
	"Wgrave",
	"Yacute",
	"Ycircumflex",
	"Ydieresis",
	"Ygrave",
	"Ymacron",
	"Zacute",
	"Zcaron",
	"Zdotaccent",
	"Thorn",
	"a",
	"b",
	"c",
	"d",
	"e",
	"h",
	"k",
	"l",
	"m",
	"p",
	"q",
	"r",
	"aacute",
	"abreve",
	"acaron",
	"acircumflex",
	"adieresis",
	"ae",
	"aeacute",
	"agrave",
	"amacron",
	"aogonek",
	"aring",
	"aringacute",
	"atilde",
	"cacute",
	"ccaron",
	"ccedilla",
	"ccircumflex",
	"cdotaccent",
	"dcaron",
	"dcroat",
	"eacute",
	"ebreve",
	"ecaron",
	"ecedilla",
	"ecircumflex",
	"edieresis",
	"edotaccent",
	"egrave",
	"emacron",
	"eogonek",
	"gbreve",
	"gcircumflex",
	"gcommaaccent",
	"gdotaccent",
	"hbar",
	"hcircumflex",
	"iacute",
	"ibreve",
	"icaron",
	"icircumflex",
	"idieresis",
	"igrave",
	"imacron",
	"iogonek",
	"itilde",
	"idotaccent",
	"dotlessi",
	"ij",
	"jcircumflex",
	"dotlessj",
	"kcommaaccent",
	"kgreenlandic",
	"lacute",
	"lcaron",
	"lcommaaccent",
	"ldot",
	"nacute",
	"napostrophe",
	"ncaron",
	"ncommaaccent",
	"ntilde",
	"oacute",
	"obreve",
	"ocaron",
	"ocircumflex",
	"odieresis",
	"oe",
	"ograve",
	"ohorn",
	"ohungarumlaut",
	"omacron",
	"oslash",
	"oslashacute",
	"otilde",
	"racute",
	"rcaron",
	"rcommaaccent",
	"sacute",
	"scaron",
	"scedilla",
	"scommaaccent",
	"scircumflex",
	"germandbls",
	"tbar",
	"tcaron",
	"tcedilla",
	"tcommaaccent",
	"uacute",
	"ubreve",
	"ucaron",
	"ucircumflex",
	"udieresis",
	"ugrave",
	"uhorn",
	"uhungarumlaut",
	"umacron",
	"uogonek",
	"uring",
	"utilde",
	"wacute",
	"wcircumflex",
	"wdieresis",
	"wgrave",
	"yacute",
	"ycircumflex",
	"ydieresis",
	"ygrave",
	"ymacron",
	"zacute",
	"zcaron",
	"zdotaccent",
	"thorn",

	# CYRILLIC
	"Be-cy",
	"Ve-cy",
	"Ge-cy",
	"Ie-cy",
	"Io-cy",
	"Ze-cy",
	"Ii-cy",
	"ShortI-cy",
	"Ka-cy",
	"En-cy",
	"O-cy",
	"Pe-cy",
	"Er-cy",
	"Es-cy",
	"Te-cy",
	"U-cy",
	"Ef-cy",
	"Ha-cy",
	"Tse-cy",
	"Che-cy",
	"Sha-cy",
	"Shcha-cy",
	"Hardsign-cy",
	"Yeru-cy",
	"Softsign-cy",
	"Ereversed-cy",
	"Iu-cy",
	"Ia-cy",
	"Gheupturn-cy",
	"Gje-cy",
	"E-cy",
	"Dze-cy",
	"I-cy",
	"Yi-cy",
	"Je-cy",
	"Lje-cy",
	"Nje-cy",
	"Kje-cy",
	"Ushort-cy",
	"Dzhe-cy",
	"Ie-cygrave",
	"I-cygrave",
	"Schwa",
	"Obarred-cy",
	"Shhadesender-cy",
	"Chedesender-cy",
	"Hadesender-cy",
	"Endescender-cy",
	"Kadescender-cy",
	"Zhedescender-cy",
	"a-cy",
	"ve-cy",
	"ge-cy",
	"ie-cy",
	"io-cy",
	"zhe-cy",
	"ii-cy",
	"iishort-cy",
	"ka-cy",
	"el-cy",
	"en-cy",
	"o-cy",
	"pe-cy",
	"er-cy",
	"es-cy",
	"te-cy",
	"u-cy",
	"ef-cy",
	"ha-cy",
	"tse-cy",
	"che-cy",
	"sha-cy",
	"shcha-cy",
	"hardsign-cy",
	"yeri-cy",
	"softsign-cy",
	"ereversed-cy",
	"iu-cy",
	"gheupturn-cy",
	"dje-cy",
	"gje-cy",
	"e-cy",
	"dze-cy",
	"i-cy",
	"yi-cy",
	"lje-cy",
	"nje-cy",
	"tshe-cy",
	"kje-cy",
	"ushort-cy",
	"dzhe-cy",
	"ie-cygrave",
	"iigrave-cy",
	"endescender-cy",
	"ustrait-cy",
	"hadesender-cy",
	"chedesender-cy",
	"obarred-cy",

	# GREEK
	"Alpha",
	"Beta",
	"Gamma",
	"Delta",
	"Epsilon",
	"Zeta",
	"Eta",
	"Theta",
	"Iota",
	"Kappa",
	"Lambda",
	"Mu",
	"Nu",
	"Omicron",
	"Pi",
	"Rho",
	"Tau",
	"Upsilon",
	"Chi",
	"Alphatonos",
	"Epsilontonos",
	"Etatonos",
	"Iotatonos",
	"Iotadieresis",
	"Omicrontonos",
	"Upsilontonos",
	"Upsilondieresis",
	"Omegatonos",
	"beta",
	"eta",
	"kappa",
	"mu",
	"omicron",
	"rho",
	"sigma",
	"psi",
	"alphatonos",
	"epsilontonos",
	"etatonos",
	"iotadieresis",
	"omicrontonos",
	"upsilontonos",
	"upsilondieresistonos",
	"upsilondieresis",
	"omegatonos",

	# PUNCTUATION
	"fi",
	"fl",
	"comma",
	"semicolon",
	"ellipsis",
	"softhyphen",
	"quoteleft",
	"quoteright",
	"quotedblright",
	"quotesinglbase",
	"quotedblbase",
	"guilsinglleft",
	"guilsinglright",
	"endash",
	"emdash",
	"periodcentered",
	"cent",
	"onesuperior",
	"perthousand",
	"semicolon",
	"quotedblbase"
]

DefaultKeys = {
	"B": ("H", ""),
	"C": ("O", ""),
	"D": ("H", "O"),
	"E": ("H", ""),
	"F": ("H", ""),
	"G": ("O", ""),
	"I": ("H", "H"),
	"K": ("H", ""),
	"L": ("H", ""),
	"N": ("H", "H"),
	"P": ("H", ""),
	# "Q": ("O", "O"),
	"R": ("H", ""),
	"Aacute": ("A", "A"),
	"Acaron": ("A", "A"),
	"Abreve": ("A", "A"),
	"Acircumflex": ("A", "A"),
	"Adieresis": ("A", "A"),
	"AE": ("A", "E"),
	"AEacute": ("A", "E"),
	"Agrave": ("A", "A"),
	"Amacron": ("A", "A"),
	"Aogonek": ("A", "A"),
	"Aring": ("A", "A"),
	"Aringacute": ("A", "A"),
	"Atilde": ("A", "A"),
	"Cacute": ("O", "C"),
	"Ccaron": ("O", "C"),
	"Ccedilla": ("O", "C"),
	"Ccircumflex": ("O", "C"),
	"Cdotaccent": ("O", "C"),
	"Dcaron": ("D", "D"),
	"Dcroat": ("D", "D"),
	"Eth": ("H", "O"),
	"Eacute": ("H", "E"),
	"Ebreve": ("H", "E"),
	"Ecaron": ("H", "E"),
	"Ecedilla": ("H", "E"),
	"Ecircumflex": ("H", "E"),
	"Edieresis": ("H", "E"),
	"Edotaccent": ("H", "E"),
	"Egrave": ("H", "E"),
	"Emacron": ("H", "E"),
	"Eogonek": ("H", "E"),
	"Gbreve": ("O", "G"),
	"Gcircumflex": ("O", "G"),
	"Gcommaaccent": ("O", "G"),
	"Gdotaccent": ("O", "G"),
	"Hbar": ("H", "H"),
	"Hcircumflex": ("H", "H"),
	"Iacute": ("H", "H"),
	"Ibreve": ("H", "H"),
	"Icaron": ("H", "H"),
	"Icircumflex": ("H", "H"),
	"Idieresis": ("H", "H"),
	"Idotaccent": ("H", "H"),
	"Igrave": ("H", "H"),
	"Imacron": ("H", "H"),
	"Iogonek": ("H", "H"),
	"Itilde": ("H", "H"),
	"IJ": ("H", "J"),
	"Jcircumflex": ("J", "J"),
	"Kcommaaccent": ("H", "K"),
	"Lacute": ("H", "L"),
	"Lcaron": ("H", "L"),
	"Lcommaaccent": ("H", "L"),
	"Ldot": ("H", "L"),
	"Lslash": ("H", "L"),
	"Nacute": ("N", "N"),
	"Ncaron": ("N", "N"),
	"Ncommaaccent": ("N", "N"),
	"Ntilde": ("N", "N"),
	"Oacute": ("O", "O"),
	"Obreve": ("O", "O"),
	"Ocircumflex": ("O", "O"),
	"Odieresis": ("O", "O"),
	"OE": ("O", "E"),
	"Ograve": ("O", "O"),
	# "Ohorn": ("O", "O"),
	"Ohungarumlaut": ("O", "O"),
	"Omacron": ("O", "O"),
	"Oslash": ("O", "O"),
	"Oslashacute": ("O", "O"),
	"Otilde": ("O", "O"),
	"Racute": ("H", "R"),
	"Rcaron": ("H", "R"),
	"Rcommaaccent": ("H", "R"),
	"Sacute": ("S", "S"),
	"Scaron": ("S", "S"),
	"Scedilla": ("S", "S"),
	"Scommaaccent": ("S", "S"),
	"Scircumflex": ("S", "S"),
	"Tcaron": ("T", "T"),
	"Tcedilla": ("T", "T"),
	"Tcommaaccent": ("T", "T"),
	"Tbar": ("T", "T"),
	"Uacute": ("U", "U"),
	"Ubreve": ("U", "U"),
	"Ucaron": ("U", "U"),
	"Ucircumflex": ("U", "U"),
	"Udieresis": ("U", "U"),
	"Ugrave": ("U", "U"),
	"Uhungarumlaut": ("U", "U"),
	"Umacron": ("U", "U"),
	"Uogonek": ("U", "U"),
	"Uring": ("U", "U"),
	"Utilde": ("U", "U"),
	"Wacute": ("W", "W"),
	"Wcircumflex": ("W", "W"),
	"Wdieresis": ("W", "W"),
	"Wgrave": ("W", "W"),
	"Yacute": ("Y", "Y"),
	"Ycircumflex": ("Y", "Y"),
	"Ydieresis": ("Y", "Y"),
	"Ygrave": ("Y", "Y"),
	"Ymacron": ("Y", "Y"),
	"Zacute": ("Z", "Z"),
	"Zcaron": ("Z", "Z"),
	"Zdotaccent": ("Z", "Z"),
	"Thorn": ("H", ""),
	"a": ("", "n"),
	"b": ("h", "o"),
	"c": ("o", "c"),
	"d": ("o", "l"),
	"e": ("o", "e"),
	"h": ("", "n"),
	"k": ("h", "k"),
	"l": ("h", ""),
	"m": ("n", "n"),
	"p": ("", "o"),
	"q": ("o", ""),
	"r": ("n", ""),
	"aacute": ("a", "n"),
	"abreve": ("a", "n"),
	"acaron": ("a", "n"),
	"acircumflex": ("a", "n"),
	"adieresis": ("a", "n"),
	"ae": ("a", "e"),
	"aeacute": ("a", "e"),
	"agrave": ("a", "n"),
	"amacron": ("a", "n"),
	"aogonek": ("a", "n"),
	"aring": ("a", "n"),
	"aringacute": ("a", "n"),
	"atilde": ("a", "n"),
	"cacute": ("o", "c"),
	"ccaron": ("o", "c"),
	"ccedilla": ("o", "c"),
	"ccircumflex": ("o", "c"),
	"cdotaccent": ("o", "c"),
	# "dcaron": ("o", "l"),
	"dcroat": ("o", "l"),
	"eacute": ("o", "e"),
	"ebreve": ("o", "e"),
	"ecaron": ("o", "e"),
	"ecedilla": ("o", "e"),
	"ecircumflex": ("o", "e"),
	"edieresis": ("o", "e"),
	"edotaccent": ("o", "e"),
	"egrave": ("o", "e"),
	"emacron": ("o", "e"),
	"eogonek": ("o", "e"),
	"gbreve": ("g", "g"),
	"gcircumflex": ("g", "g"),
	"gcommaaccent": ("g", "g"),
	"gdotaccent": ("g", "g"),
	"hbar": ("h", "n"),
	"hcircumflex": ("h", "n"),
	"iacute": ("i", "i"),
	"ibreve": ("i", "i"),
	"icaron": ("i", "i"),
	"icircumflex": ("i", "i"),
	"idieresis": ("i", "i"),
	"igrave": ("i", "i"),
	"imacron": ("i", "i"),
	"iogonek": ("i", "i"),
	"itilde": ("i", "i"),
	"idotaccent": ("i", "i"),
	"ij": ("i", "i"),
	"jcircumflex": ("j", "j"),
	"kcommaaccent": ("h", "k"),
	"lacute": ("h", "l"),
	# "lcaron": ("h", "l"),
	"lcommaaccent": ("h", "l"),
	"ldot": ("h", "l"),
	"nacute": ("n", "n"),
	"napostrophe": ("n", "n"),
	"ncaron": ("n", "n"),
	"ncommaaccent": ("n", "n"),
	"ntilde": ("n", "n"),
	"oacute": ("o", "o"),
	"obreve": ("o", "o"),
	"ocaron": ("o", "o"),
	"ocircumflex": ("o", "o"),
	"odieresis": ("o", "o"),
	"oe": ("o", "e"),
	"ograve": ("o", "o"),
	# "ohorn": ("o", "o"),
	"ohungarumlaut": ("o", "o"),
	"omacron": ("o", "o"),
	"oslash": ("o", "o"),
	"oslashacute": ("o", "o"),
	"otilde": ("o", "o"),
	"racute": ("n", "r"),
	"rcaron": ("n", "r"),
	"rcommaaccent": ("n", "r"),
	"sacute": ("s", "s"),
	"scaron": ("s", "s"),
	"scedilla": ("s", "s"),
	"scommaaccent": ("s", "s"),
	"scircumflex": ("s", "s"),
	"germandbls": ("h", ""),
	"tbar": ("t", "t"),
	"tcaron": ("t", "t"),
	"tcedilla": ("t", "t"),
	"tcommaaccent": ("t", "t"),
	"uacute": ("u", "u"),
	"ubreve": ("u", "u"),
	"ucaron": ("u", "u"),
	"ucircumflex": ("u", "u"),
	"udieresis": ("u", "u"),
	"ugrave": ("u", "u"),
	# "uhorn": ("u", "u"),
	"uhungarumlaut": ("u", "u"),
	"umacron": ("u", "u"),
	"uogonek": ("u", "u"),
	"uring": ("u", "u"),
	"utilde": ("u", "u"),
	"wacute": ("w", "w"),
	"wcircumflex": ("w", "w"),
	"wdieresis": ("w", "w"),
	"wgrave": ("w", "w"),
	"yacute": ("y", "y"),
	"ycircumflex": ("y", "y"),
	"ydieresis": ("y", "y"),
	"ygrave": ("y", "y"),
	"ymacron": ("y", "y"),
	"zacute": ("z", "z"),
	"zcaron": ("z", "z"),
	"zdotaccent": ("z", "z"),
	"thorn": ("h", "o"),

	# CYRILLIC
	"A-cy": ("A-cy", "A-cy"),
	"Be-cy": ("H", ""),
	"Ve-cy": ("H", "B"),
	"Ge-cy": ("H", ""),
	"De-cy": ("De-cy", "De-cy"),
	"Ie-cy": ("H", "E"),
	"Io-cy": ("H", "E"),
	"Ze-cy": ("", "B"),
	"Ii-cy": ("H", "H"),
	"ShortI-cy": ("H", "H"),
	"Ka-cy": ("H", "K"),
	"En-cy": ("H", "H"),
	"O-cy": ("O", "O"),
	"Pe-cy": ("H", "H"),
	"Er-cy": ("H", "P"),
	"Es-cy": ("O", "C"),
	"Te-cy": ("T", "T"),
	"U-cy": ("", "V"),
	"Ef-cy": ("Phi", "Phi"),
	"Ha-cy": ("X", "X"),
	"Tse-cy": ("H", "De-cy"),
	"Che-cy": ("", "H"),
	"Sha-cy": ("H", "H"),
	"Shcha-cy": ("H", "De-cy"),
	"Hardsign-cy": ("T", "Softsign-cy"),
	"Yeru-cy": ("H", "H"),
	"Softsign-cy": ("H", ""),
	"Ereversed-cy": ("", "O"),
	"Iu-cy": ("H", "O"),
	"Dje-cy": ("T", ""),
	"Ghestroke-cy": ("", "Ge-cy"),
	"Ia-cy": ("", "H"),
	"Gheupturn-cy": ("H", "Ge-cy"),
	"Gje-cy": ("Ge-cy", "H"),
	"E-cy": ("O", "C"),
	"Dze-cy": ("S", "S"),
	"I-cy": ("H", "H"),
	"Yi-cy": ("H", "H"),
	"Je-cy": ("J", "J"),
	"Tshe-cy": ("T"),
	"Lje-cy": ("El-cy", "Softsign-cy"),
	"Nje-cy": ("H", "Softsign-cy"),
	"Kje-cy": ("K", "H"),
	"El-cy": ("", "H"),
	"Ushort-cy": ("U-cy", "U-cy"),
	"Dzhe-cy": ("H", "H"),
	"Ie-cygrave": ("E", "H"),
	"I-cygrave": ("H", "H"),
	"Schwa": ("O", "O"),
	"Obarred-cy": ("O", "O"),
	"Shhadesender-cy": ("", "H"),
	"Chedesender-cy": ("Che-cy", "De-cy"),
	"Hadesender-cy": ("", "X"),
	"Endescender-cy": ("H", "De-cy"),
	"Kadescender-cy": ("", "H"),
	"Zhedescender-cy": ("", "Zhe-cy"),
	"a-cy": ("a", "n"),
	"ve-cy": ("n", ""),
	"ge-cy": ("n", ""),
	"ie-cy": ("o", "e"),
	"io-cy": ("o", "e"),
	"zhe-cy": ("x", "x"),
	"ze-cy": ("", "ve-cy"),
	"ii-cy": ("u", "u"),
	"iishort-cy": ("u", "n"),
	"ka-cy": ("n", "k"),
	"el-cy": ("", "u"),
	"en-cy": ("u", "n"),
	"o-cy": ("o", "o"),
	"pe-cy": ("u", "n"),
	"er-cy": ("o", ""),
	"es-cy": ("c", "c"),
	"te-cy": ("te-cy", "te-cy"),
	"u-cy": ("y", "y"),
	"ef-cy": ("o", "o"),
	"ha-cy": ("x", "x"),
	"tse-cy": ("de-cy", "n"),
	"che-cy": ("u", ""),
	"sha-cy": ("u", "n"),
	"shcha-cy": ("de-cy", "n"),
	"hardsign-cy": ("", "softsign-cy"),
	"yeri-cy": ("u", "n"),
	"softsign-cy": ("n", ""),
	"ereversed-cy": ("", "o"),
	"iu-cy": ("n", "o"),
	"ia-cy": ("ia-cy", "u"),
	"gheupturn-cy": ("n", "ge-cy"),
	"dje-cy": ("hbar", "j"),
	"gje-cy": ("ge-cy", "n"),
	"e-cy": ("o", "c"),
	"dze-cy": ("s", "s"),
	"i-cy": ("i", "i"),
	"yi-cy": ("i", "i"),
	"fita-cy": ("o", "o"),
	"izhitsa-cy": ("v", "v"),
	"lje-cy": ("el-cy", "softsign-cy"),
	"nje-cy": ("n", "softsign-cy"),
	"tshe-cy": ("n", ""),
	"kje-cy": ("k", "n"),
	"ushort-cy": ("y", "y"),
	"dzhe-cy": ("u", "n"),
	"ie-cygrave": ("e", "o"),
	"iigrave-cy": ("u", "n"),
	"endescender-cy": ("de-cy", "n"),
	"ustrait-cy": ("v", "v"),
	"hadesender-cy": ("", "x"),
	"chedesender-cy": ("de-cy", "che-cy"),
	"obarred-cy": ("o", "o"),

	# GREEK
	"Alpha": ("A", "A"),
	"Beta": ("H", "B"),
	"Gamma": ("", "H"),
	"Delta": ("A", "A"),
	"Epsilon": ("H", "E"),
	"Zeta": ("Z", "Z"),
	"Eta": ("H", "H"),
	"Theta": ("O", "O"),
	"Iota": ("H", "H"),
	"Kappa": ("H", "K"),
	"Lambda": ("A", "A"),
	"Mu": ("M", "M"),
	"Nu": ("H", "H"),
	"Omicron": ("O", "O"),
	"Pi": ("H", "H"),
	"Rho": ("H", "P"),
	"Tau": ("T", "T"),
	"Upsilon": ("Y", "Y"),
	"Chi": ("X", "X"),
	"Alphatonos": ("A", "A"),
	"Epsilontonos": ("E", "E"),
	"Etatonos": ("H", "H"),
	"Iotatonos": ("H", "H"),
	"Iotadieresis": ("H", "H"),
	"Omicrontonos": ("O", "O"),
	"Upsilontonos": ("Y", "Y"),
	"Upsilondieresis": ("Y", "Y"),
	"Omegatonos": ("Omega", "Omega"),
	"beta": ("h", ""),
	"eta": ("n", "n"),
	"kappa": ("n", "k"),
	"mu": ("p", "u"),
	"omicron": ("o", "o"),
	"rho": ("rho", "o"),
	"sigma": ("o", ""),
	"psi": ("upsilon", "upsilon"),
	"alphatonos": ("alpha", "alpha"),
	"epsilontonos": ("epsilon", "epsilon"),
	"etatonos": ("n", "n"),
	"iotadieresis": ("i", "i"),
	"omicrontonos": ("o", "o"),
	"upsilontonos": ("upsilon", "upsilon"),
	"upsilondieresistonos": ("upsilon", "upsilon"),
	"upsilondieresis": ("upsilon", "upsilon"),
	"omegatonos": ("omega", "omega"),

	# PUNCTUATION
	"comma": ("period", "period"),
	"semicolon": ("colon", "colon"),
	"ellipsis": ("period", "period"),
	"softhyphen": ("hyphen", "hyphen"),
	"quoteleft": ("quotedblleft", "quotedblleft"),
	"quoteright": ("quotedblleft", "quotedblleft"),
	"quotedblright": ("quotedblleft", "quotedblleft"),
	"quotesinglbase": ("period", "period"),
	"quotedblbase": ("period", "period"),
	"guilsinglleft": ("guillemotleft", "guillemotleft"),
	"guilsinglright": ("guillemotright", "guillemotright"),
	"endash": ("hyphen", "hyphen"),
	"emdash": ("hyphen", "hyphen"),
	"periodcentered": ("anoteleia", "anoteleia"),
	"cent": ("o", "c"),
	"perthousand": ("percent", "percent"),
	"semicolon": ("colon", "colon"),
	"quotedblbase": ("period", "period"),

	# OVERRIDE FOR SPECIAL CASES
	"oe.sc": ("o.sc", "e.sc"),
	"ae.sc": ("a.sc", "e.sc"),
	"eng": ("n", "j"),
	"alef-ar": ("alef-ar", "alef-ar"),
	"fi": ("f", "i"),
	"fl": ("f", "l"),
	"dcaron": ("o", "dcaron"),
	"lcaron": ("h", "dcaron"),
	"Q": ("O", "Q"),
	"dotlessi": ("i", "i"),
	"dotlessj": ("j", "j"),
	"idotless": ("i", "i"),
	"jdotless": ("j", "j"),
	"DZcaron": ("H", "Z"),
	"Dzcaron": ("H", "z"),
	"dzcaron": ("o", "z"),
	"dzcaron.sc": ("o.sc", "z.sc"),
	"Eng": ("H", "J"),
	"eng.sc": ("h.sc", "j.sc"),
	"Ohorn": ("O", "Ohorn"),
	"Uhorn": ("U", "Uhorn"),
	"ohorn": ("o", "ohorn"),
	"uhorn": ("u", "uhorn"),
	"ohorn.sc": ("o.sc", "ohorn.sc"),
	"uhorn.sc": ("u.sc", "uhorn.sc"),
	"schwa": ("o", "o"),
	"kgreenlandic": ("n", "k"),
}


def KeysForGlyph(Glyph):
	if Glyph is None:
		return ()
	global DefaultKeys
	LeftKey = False
	RightKey = False
	try:
		LeftKey = Glyph.leftKerningGroup
	except:
		print(traceback.format_exc())
	try:
		RightKey = Glyph.rightKerningGroup
	except:
		print(traceback.format_exc())
	try:
		if len(LeftKey < 1):
			LeftKey = False
	except TypeError:
		pass
	except:
		print(traceback.format_exc())
	try:
		if len(RightKey < 1):
			RightKey = False
	except TypeError:
		pass
	except:
		print(traceback.format_exc())

	return (LeftKey, RightKey)


def updateKeyGlyphsForSelected():
	countL, countR = 0, 0
	Font = Glyphs.font
	SelectedLayers = Font.selectedLayers
	for Layer in SelectedLayers:
		Glyph = Layer.parent
		if Glyph.name in alwaysExclude:
			Glyph.leftKerningGroup = None
			Glyph.rightKerningGroup = None
			print("🔠 %s: 🚫 ↔️ 🚫" % Glyph.name)
			continue

		LeftKey = ""
		RightKey = ""
		LigatureComponents = Glyph.name.split("_")
		if len(Layer.components) > 0 and len(Layer.paths) == 0 and Layer.components[0].transformStruct()[0] == 1:
			componentGlyph = Layer.components[0].component
			if not componentGlyph:
				raise Exception("Something is wrong with a component in glyph %s" % Glyph.name)
			if componentGlyph.category == "Letter":
				LeftKey = KeysForGlyph(componentGlyph)[0]
			if not LeftKey:
				LeftKey = componentGlyph.name
				if componentGlyph.name in DefaultKeys.keys():
					LeftKey = DefaultKeys[componentGlyph.name][0]

			# right side may be different (Dz, Nj, ae, oe):
			for Component in Layer.components:
				try:
					if Component.component.category == "Letter":
						if Component.transform[0] == 1:
							componentGlyph = Component.component
					elif Component.component.category != "Mark":
						# componentGlyph = None
						pass
				except:
					pass
			if componentGlyph:
				RightKey = KeysForGlyph(componentGlyph)[1]
				if not RightKey:
					RightKey = componentGlyph.name
					if componentGlyph.name in DefaultKeys.keys():
						RightKey = DefaultKeys[componentGlyph.name][1]

		elif len(LigatureComponents) > 1:
			LeftGlyph = Font.glyphs[LigatureComponents[0]]
			if LeftGlyph is not None:
				LeftKey = KeysForGlyph(LeftGlyph)[0]
			RightGlyph = Font.glyphs[LigatureComponents[-1]]
			if RightGlyph is not None:
				RightKey = KeysForGlyph(RightGlyph)[1]

		if LeftKey:
			try:
				if LeftKey not in Font.glyphs and not Font.glyphs[LeftKey].export:
					LeftKey = False
			except:
				LeftKey = False
		if RightKey:
			try:
				if RightKey not in Font.glyphs and not Font.glyphs[RightKey].export:
					RightKey = False
			except:
				pass
		if not LeftKey:
			try:
				LeftKey = DefaultKeys[Glyph.name][0]
			except KeyError:
				pass
			except:
				print(traceback.format_exc())
		if not RightKey:
			try:
				RightKey = DefaultKeys[Glyph.name][1]
			except KeyError:
				pass
			except:
				print(traceback.format_exc())
		if not LeftKey and Glyph.name[-3:] == ".sc":
			try:
				glyphName = Glyph.name[:-3].title()
				if glyphName not in DefaultKeys.keys():
					glyphName = Glyph.name[:-3]
				LeftKey = DefaultKeys[glyphName][0]
				if (len(LeftKey) > 0):
					LeftKey = LeftKey.lower() + ".sc"
			except:
				print(traceback.format_exc())
		if not RightKey and Glyph.name[-3:] == ".sc":
			try:
				glyphName = Glyph.name[:-3].title()
				if glyphName not in DefaultKeys.keys():
					glyphName = Glyph.name[:-3]
				RightKey = DefaultKeys[glyphName][1]
				if (len(RightKey) > 0):
					RightKey = RightKey.lower() + ".sc"
			except:
				print(traceback.format_exc())
		if not LeftKey:
			LeftKey = Glyph.name
		if not RightKey:
			RightKey = Glyph.name

		# REPORT
		if not Glyph.leftKerningGroup or not Glyph.rightKerningGroup:
			print("🔠 %s: %s ↔️ %s" % (Glyph.name, LeftKey, RightKey))

		if not Glyph.leftKerningGroup:
			Glyph.leftKerningGroup = LeftKey
			countL += 1
		elif verbose:
			print("   ⚠️ LEFT group unchanged: %s" % Glyph.leftKerningGroup)

		if not Glyph.rightKerningGroup:
			Glyph.rightKerningGroup = RightKey
			countR += 1
		elif verbose:
			print("   ⚠️ RIGHT group unchanged: %s" % Glyph.rightKerningGroup)

	Message(
		title="Kerning Groups Report",
		message="Set %i left and %i right groups in %i selected glyphs. Detailed report in Window → Macro Panel." % (countL, countR, len(SelectedLayers)),
		OKButton=None,
	)


def main():
	Glyphs.clearLog()
	print("Detailed Report for ‘Set Kerning Groups’:\n")
	updateKeyGlyphsForSelected()
	print("\nDone.")


def test():
	NewDefaultKeys = {}
	for key in Keys:
		key = Glyphs.niceGlyphName(key)
		values = DefaultKeys[key]
		newValues = []
		for value in values:
			newValues.append(Glyphs.niceGlyphName(value))
		print("	\"%s\" : [\"%s\", \"%s\"]," % (key, newValues[1], newValues[0]))
		NewDefaultKeys[key] = newValues


main()
