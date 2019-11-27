#MenuTitle: Language Report
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Tries to give you a preliminary idea about how many and which languages are supported with your Latin characters.
"""

langdict = {
	"abenaki":{"language":u"Abenaki", "code":"abe", "letters":u"Ôô", "speakers":0},
	"afaan_oromo":{"language":u"Afaan Oromo", "code":"gaz", "letters":u"", "speakers":32000000},
	"afar":{"language":u"Afar", "code":"aar", "letters":u"", "speakers":1000000},
	"afrikaans":{"language":u"Afrikaans", "code":"afr", "letters":u"ÈèÉéÊêËëÎîÏïÔôÛû", "speakers":10000000},
	"albanian":{"language":u"Albanian", "code":"sqi", "letters":u"ÇçËë", "speakers":7600000},
	"alsatian":{"language":u"Alsatian", "code":"gsw", "letters":u"ÄäÀàÉéÌìÖöÜüÙù", "speakers":90000},
	"amis":{"language":u"Amis", "code":"ami", "letters":u"", "speakers":180000},
	"anuta":{"language":u"Anuta", "code":"aud", "letters":u"", "speakers":300},
	"aragonese":{"language":u"Aragonese", "code":"arg", "letters":u"ÁáÉéÍíÑñÓóÚú", "speakers":10000},
	"aranese":{"language":u"Aranese", "code":"oci", "letters":u"ÁáÀàÇçÉéÈèÍíÏïÓóÒòÚúÜü", "speakers":4600},
	"aromanian":{"language":u"Aromanian", "code":"rup", "letters":u"ÃãÂâĂăȘșȚț", "speakers":250000},
	"arrernte":{"language":u"Arrernte", "code":"aer", "letters":u"", "speakers":1500},
	"arvanitic":{"language":u"Arvanitic (Latin)", "code":"aat", "letters":u"ÁáÄäÇçÈèÉéËëÍíÏïÓóÖöÚúÜüÝý", "speakers":30000},
	"asturian":{"language":u"Asturian", "code":"ast", "letters":u"ÁáÉéÍíÑñÓóÚúÜü", "speakers":550000},
	"atayal":{"language":u"Atayal", "code":"tay", "letters":u"Ŋŋ", "speakers":84000},
	"aymara":{"language":u"Aymara", "code":"aym", "letters":u"ÄäÏïÑñÜü", "speakers":2200000},
	"azerbaijani":{"language":u"Azerbaijani", "code":"azj", "letters":u"ÄäÇçƏəĞğİıÖöŞşÜü", "speakers":30000000},
	"bashkir":{"language":u"Bashkir (Latin)", "code":"bak", "letters":u"ÄäÇçČčĞğİıĶķŅņÖöŚśŞşŠšÜüŹź", "speakers":1200000},
	"basque":{"language":u"Basque", "code":"eus", "letters":u"ÑñÜü", "speakers":660000},
	"belarusian":{"language":u"Belarusian (Latin)", "code":"bel", "letters":u"ĆćČčÈèËëŁłŃńŚśŠšŬŭŹźŽž", "speakers":4000000}, # ČčÈèËëŠšŽžẖ romanization?
	"bemba":{"language":u"Bemba", "code":"bem", "letters":u"Ŋŋ", "speakers":3600000},
	"bikol":{"language":u"Bikol", "code":"bik", "letters":u"", "speakers":2400000},
	"bislama":{"language":u"Bislama", "code":"bis", "letters":u"", "speakers":6200},
	"bosnian":{"language":u"Bosnian", "code":"bos", "letters":u"ĆćČčĐđŠšŽž", "speakers":2200000},
	"breton":{"language":u"Breton", "code":"bre", "letters":u"ÀàÂâÆæÇçÉéÈèËëÊêÏïÎîÑñÔôŒœÙùÜüÛûŸÿ", "speakers":200000},
	"bulgarian_romanization":{"language":u"Bulgarian (Romanization)", "code":"bgr", "letters":u"ǍǎČčŠšŽžŬŭ", "speakers":9000000},
	"cape_verdean":{"language":u"Cape Verdean Creole", "code":"kea", "letters":u"ÀàÁáÂâÃãÇçÈèÉéÊêÍíÒòÓóÔôÕõÚúÜü", "speakers":920000},
	"catalan":{"language":u"Catalan", "code":"cat", "letters":u"ÀàÇçÈèÉéÍíÏïÑñÒòÓóÚúÜü", "speakers":7200000},
	"cebuano":{"language":u"Cebuano", "code":"ceb", "letters":u"", "speakers":18000000},
	"chamorro":{"language":u"Chamorro", "code":"cha", "letters":u"ÅåÂâÑñÜü", "speakers":50000},
	"chavacano":{"language":u"Chavacano", "code":"cbk", "letters":u"Ññ", "speakers":600000},
	"chichewa":{"language":u"Chichewa", "code":"nya", "letters":u"ŊŋŴŵ", "speakers":7000000},
	"chickasaw":{"language":u"Chickasaw", "code":"cic", "letters":u"ÁáÉéÍíÓóÚú", "speakers":75},
	"cimbrian":{"language":u"Cimbrian", "code":"cim", "letters":u"ÄäĆćÖöÜü", "speakers":2230},
	"cofan":{"language":u"Cofán", "code":"con", "letters":u"ÑñÛû", "speakers":1000},
	"cornish":{"language":u"Cornish", "code":"cor", "letters":u"ĀāĒēĪīŌōŪūÜüȲȳ", "speakers":300},
	"corsican":{"language":u"Corsican", "code":"cos", "letters":u"ÀàÂâÈèÌìÒòÙù", "speakers":230000},
	"creek":{"language":u"Creek", "code":"mus", "letters":u"Ēē", "speakers":4700},
	"crimean_tatar":{"language":u"Crimean Tatar (Latin)", "code":"crh", "letters":u"ÇçĞğÑñÖöŞşÜü", "speakers":400000},
	"croatian":{"language":u"Croatian", "code":"hrv", "letters":u"ĆćČčĐđŠšŽž", "speakers":5500000},
	"czech":{"language":u"Czech", "code":"ces", "letters":u"ÁáČčĎďÉéĚěÍíŇňÓóŘřŠšŤťÚúŮůÝýŽž", "speakers":12000000},
	"danish":{"language":u"Danish", "code":"dan", "letters":u"ÁáÅåÆæÉéÍíÓóØøÚúÝý", "speakers":5500000},
	"dawan":{"language":u"Dawan", "code":"aoz", "letters":u"ÁáÉéÊêÍíÓóÚúÛû", "speakers":600000},
	"delaware":{"language":u"Delaware", "code":"del", "letters":u"ÀàÈèËëÌìÒòÙù", "speakers":1},
	"dholuo":{"language":u"Dholuo", "code":"luo", "letters":u"", "speakers":3000000},
	"drehu":{"language":u"Drehu", "code":"dhv", "letters":u"ËëÖö", "speakers":12000},
	"dutch":{"language":u"Dutch", "code":"nld", "letters":u"ÁáÂâÄäÈèÉéÊêËëÍíÏïÓóÔôÖöÚúÛûÜü", "speakers":20000000},
	"english":{"language":u"English", "code":"eng", "letters":u"ÆæÇçÏïÔôŒœÁáÈèÉéËëÊêÑñÖö", "speakers":341000000},
	"esperanto":{"language":u"Esperanto", "code":"epo", "letters":u"ĈĉĜĝĤĥĴĵŜŝŬŭ", "speakers":100},
	"estonian":{"language":u"Estonian", "code":"est", "letters":u"ÄäÕõÖöŠšÜüŽž", "speakers":1100000},
	"faroese":{"language":u"Faroese", "code":"fao", "letters":u"ÁáÅåÆæÐðÍíÓóÖöØøÚúÝý", "speakers":47000},
	"fijian":{"language":u"Fijian", "code":"fij", "letters":u"", "speakers":320000},
	"filipino":{"language":u"Filipino", "code":"fil", "letters":u"Ññ", "speakers":25000000},
	"finnish":{"language":u"Finnish", "code":"fin", "letters":u"ÄäÅåÆæÖöÕõØøŠšÜüŽž", "speakers":5000000},
	"folkspraak":{"language":u"Folkspraak", "code":"na", "letters":u"ÂâÊêÎîÔôÛû", "speakers":0},
	"french":{"language":u"French", "code":"fra", "letters":u"ÀàÂâÇçÈèÉéÊêËëÎîÏïÔôŒœÙùÛûÜüŸÿÆæ", "speakers":200000000},
	"frisian":{"language":u"Frisian", "code":"fry", "letters":u"ÄäÂâÉéËëÊêÏïÎîÖöÔôÚúÛûÜü", "speakers":460000},
	"friulian":{"language":u"Friulian", "code":"fur", "letters":u"ÀàÁáÂâÇçÈèÊêÌìÎîÒòÔôÙùÛû", "speakers":300000},
	"gagauz":{"language":u"Gagauz (Latin)", "code":"gag", "letters":u"ÄäÇçÊêĞğİıÖöŞşȘșŢţȚțÜü", "speakers":150000},
	"galician":{"language":u"Galician", "code":"glg", "letters":u"ÁáÉéÍíÑñÓóÚúÜü", "speakers":3000000},
	"ganda":{"language":u"Ganda", "code":"gqa", "letters":u"Ŋŋ", "speakers":3000000},
	"genoese":{"language":u"Genoese", "code":"lij", "letters":u"ÀàÁáÂâÄäÆæÈèÉéËëÊêÌìÍíÏïÎîÒòÓóÖöÔôÙùÚú", "speakers":1900000},
	"german":{"language":u"German", "code":"deu", "letters":u"ÄäÖößÜüÀàÉé", "speakers":120000000},
	"gikuyu":{"language":u"Gikuyu", "code":"kik", "letters":u"ĨĩŊŋŨũ", "speakers":5300000},
	"gooniyandi":{"language":u"Gooniyandi", "code":"gni", "letters":u"", "speakers":50},
	"greenlandic":{"language":u"Greenlandic (Kalaallisut)", "code":"kal", "letters":u"ÆæØøÅå", "speakers":50000},
	"greenlandic_old_orthography":{"language":u"Greenlandic (Orthography before 1973)", "code":"kal", "letters":u"ÅåÁáÂâÃãÆæÊêÍíÎîĨĩĸÔôØøÚúÛûŨũ", "speakers":50000},
	"guadeloupean":{"language":u"Guadeloupean Creole", "code":"gcf", "letters":u"ÉéÈèÒò", "speakers":430000},
	"gwichin":{"language":u"Gwich’in", "code":"gwi", "letters":u"ÀàÅåÈèÉéÍíÌìŁłÓóÒòÚúÙù", "speakers":700},
	"haitian_creole":{"language":u"Haitian Creole", "code":"hat", "letters":u"ÁáÀàÉéÈèÓóÒò", "speakers":12000000},
	"han":{"language":u"Hän", "code":"haa", "letters":u"ÄäËë", "speakers":10},
	"hawaiian":{"language":u"Hawaiian", "code":"haw", "letters":u"ĀāĒēĪīŌōŪū", "speakers":8000},
	"hiligaynon":{"language":u"Hiligaynon", "code":"hil", "letters":u"", "speakers":11000000},
	"hopi":{"language":u"Hopi", "code":"hop", "letters":u"", "speakers":5000},
	"hotcak":{"language":u"Hotcąk (Latin)", "code":"win", "letters":u"ĄąĞğĮįŠšŲųŽž", "speakers":230},
	"hungarian":{"language":u"Hungarian", "code":"hun", "letters":u"ÁáÉéÍíÓóÖöŐőÚúÜüŰű", "speakers":13000000},
	"icelandic":{"language":u"Icelandic", "code":"isl", "letters":u"ÁáÆæÐðÉéÍíÓóÖöÞþÚúÝý", "speakers":300000},
	"ido":{"language":u"Ido", "code":"ido", "letters":u"", "speakers":100},
	"igbo":{"language":u"Igbo", "code":"ibo", "letters":u"ỊịÑñỌọỤụ", "speakers":18000000},
	"ilocano":{"language":u"Ilocano", "code":"ilo", "letters":u"", "speakers":7000000},
	"indonesian":{"language":u"Indonesian", "code":"ind", "letters":u"Éé", "speakers":23000000},
	"interglossa":{"language":u"Interglossa", "code":"igs", "letters":u"", "speakers":0},
	"interlingua":{"language":u"Interlingua", "code":"ina", "letters":u"", "speakers":0},
	"irish":{"language":u"Irish", "code":"gle", "letters":u"ÀàÁáÈèÉéÌìÍíÒòÓóÚúÙù", "speakers":350000},
	"istroromanian":{"language":u"Istro-Romanian", "code":"ruo", "letters":u"ÅåĂăĽľŃńȘșȚț", "speakers":560},
	"italian":{"language":u"Italian", "code":"ita", "letters":u"ÀàÈèÉéÌìÒòÓóÙùÁáÍíÎîÏïÚú", "speakers":60000000},
	"jamaican":{"language":u"Jamaican", "code":"jam", "letters":u"", "speakers":3100000},
	"javanese":{"language":u"Javanese (Latin)", "code":"jav", "letters":u"", "speakers":80000000},
	"jerriais":{"language":u"Jèrriais", "code":"fra", "letters":u"ÂâÇçÉéÊêÈèÎîÔôÛû", "speakers":1700},
	"kaingang":{"language":u"Kaingang", "code":"kgp", "letters":u"ÁáÂâÉéẼẽĨĩÓóŨũỸỹ", "speakers":18000},
	"kala_lagaw_ya":{"language":u"Kala Lagaw Ya", "code":"mwp", "letters":u"ÄäÁáÀàËëÉéÈèÏïÍíÌìÖöÓóÒòÜüÚúÙù", "speakers":1200},
	"kapampangan":{"language":u"Kapampangan (Latin)", "code":"pam", "letters":u"", "speakers":2400000},
	"kaqchikel":{"language":u"Kaqchikel", "code":"cak", "letters":u"ÄäËëÏïÖöÜü", "speakers":500000},
	"karakalpak":{"language":u"Karakalpak (Latin)", "code":"kaa", "letters":u"İı", "speakers":412000},
	"karelian":{"language":u"Karelian (Latin)", "code":"krl", "letters":u"ÄäČčÖöŠšŽž", "speakers":35000},
	"kashubian":{"language":u"Kashubian", "code":"csb", "letters":u"ĄąÃãÉéËëĘęŁłŃńÒòÓóÔôŚśÙùŻż", "speakers":50000},
	"kikongo":{"language":u"Kikongo", "code":"kng", "letters":u"", "speakers":7000000},
	"kinyarwanda":{"language":u"Kinyarwanda", "code":"kin", "letters":u"", "speakers":7000000},
	"kiribati":{"language":u"Kiribati", "code":"gil", "letters":u"", "speakers":70000},
	"kirundi":{"language":u"Kirundi", "code":"run", "letters":u"", "speakers":4500000},
	"klingon":{"language":u"Klingon", "code":"tlh", "letters":u"", "speakers":0},
	"kurdish":{"language":u"Kurdish (Latin)", "code":"kur", "letters":u"ĀāĂăÇçÉéÊêĒēĔĕÍíÎîĪīĬĭŌōŎŏȘșÚúÛûŪūŬŭ", "speakers":16000000},
	"ladin":{"language":u"Ladin", "code":"lld", "letters":u"ÀàÁáÂâĆćÉéÈèËëÊêÌìÎîÓóÒòÖöÔôŚśÙùÜüÛû", "speakers":20000},
	"latin":{"language":u"Latin", "code":"lat", "letters":u"", "speakers":0},
	"latino_sine":{"language":u"Latino sine Flexione", "code":"na", "letters":u"", "speakers":0},
	"latvian":{"language":u"Latvian", "code":"lav", "letters":u"ĀāČčĒēĢģĪīĶķĻļŅņŠšŪūŽžŌōŖŗ", "speakers":1400000},
	"lithuanian":{"language":u"Lithuanian", "code":"lit", "letters":u"ĄąČčĘęĖėĮįŠšŲųŪūŽž", "speakers":3400000},
	"lojban":{"language":u"Lojban", "code":"jbo", "letters":u"", "speakers":0},
	"lombard":{"language":u"Lombard", "code":"lmo", "letters":u"ÀàÁáÈèÉéÌìÍíÒòÓóÔôØøÙùÜü", "speakers":3500000},
	"low_saxon":{"language":u"Low Saxon", "code":"nds", "letters":u"ÄäËëÏïÖöÜüß", "speakers":3000000},
	"luxembourgish":{"language":u"Luxembourgish", "code":"ltz", "letters":u"ÄäÂâÈèÉéËëÊêÎîÖöÔôßÜüÛû", "speakers":390000},
	"maasai":{"language":u"Maasai", "code":"mas", "letters":u"ÀàÁáÂâÈèÉéÊêÌìÍíÎîŊŋÒòÓóÔôÙùÚúÛû", "speakers":900000},
	"makhuwa":{"language":u"Makhuwa", "code":"vmw", "letters":u"ÀàÈèÌìÒòÙù", "speakers":2500000},
	"malay":{"language":u"Malay", "code":"zlm", "letters":u"", "speakers":18000000},
	"maltese":{"language":u"Maltese", "code":"mlt", "letters":u"ÀàÁáÂâĊċÈèÉéÊêĠġĦħÌìÍíÎîÒòÓóÔôÙùÚúÛûŻż", "speakers":350000},
	"manx":{"language":u"Manx", "code":"glv", "letters":u"", "speakers":200},
	"maori":{"language":u"Māori", "code":"rar", "letters":u"ĀāĒēĪīŌōŪū", "speakers":136000},
	"marquesan":{"language":u"Marquesan", "code":"mrq", "letters":u"ÁáÉéÍíÓóÚú", "speakers":8000},
	"meglenoromanian":{"language":u"Megleno-Romanian", "code":"ruq", "letters":u"ĂăĽľŃńȘșȚț", "speakers":5000},
	"meriam_mir":{"language":u"Meriam Mir", "code":"ulk", "letters":u"ÌìÒòÙù", "speakers":210},
	"mirandese":{"language":u"Mirandese", "code":"mwl", "letters":u"ÁáÇçÉéÊêÍíÓóÔôÚúŨũ", "speakers":10000},
	"mohawk":{"language":u"Mohawk", "code":"moh", "letters":u"", "speakers":3350},
	"moldovan":{"language":u"Moldovan", "code":"ron", "letters":u"ÂâĂăÎîȘșȚț", "speakers":24000000},
	"montagnais":{"language":u"Montagnais", "code":"moe", "letters":u"ÂâÎîÛû", "speakers":9000},
	"montenegrin":{"language":u"Montenegrin", "code":"srp", "letters":u"ČčĆćĐđŠšŚśŹźŽž", "speakers":600000},
	"murrinhpatha":{"language":u"Murrinh-Patha", "code":"mwf", "letters":u"", "speakers":1500},
	"nagamese_creole":{"language":u"Nagamese Creole", "code":"nag", "letters":u"", "speakers":30000},
	"nahuatl":{"language":u"Nahuatl", "code":"nhn", "letters":u"ĀāĒēĪīŌōŪūÜüȲȳ", "speakers":1400000},
	"ndebele":{"language":u"Ndebele", "code":"nbl", "letters":u"", "speakers":2000000},
	"neapolitan":{"language":u"Neapolitan", "code":"nap", "letters":u"ÀàÁáÈèÉéÌìÍíÒòÓóÙùÚú", "speakers":7000000},
	"ngiyambaa":{"language":u"Ngiyambaa", "code":"wyb", "letters":u"", "speakers":12},
	"niuean":{"language":u"Niuean", "code":"niu", "letters":u"ĀāĒēĪīŌōŪū", "speakers":8000},
	"noongar":{"language":u"Noongar", "code":"xrg", "letters":u"ĀāĒēĪīŌōŪū", "speakers":240},
	"norwegian":{"language":u"Norwegian", "code":"nor", "letters":u"ÆæØøÅåÀàÉéÊêÓóÒòÔôÄäÖöÜü", "speakers":5000000},
	"novial":{"language":u"Novial", "code":"nov", "letters":u"", "speakers":0},
	"occidental":{"language":u"Occidental", "code":"ile", "letters":u"ÁáÉéÍíÓóÚú", "speakers":0},
	"occitan":{"language":u"Occitan", "code":"oci", "letters":u"ÁáÀàÇçÉéÈèËëÍíÏïÓóÒòÚúÜü", "speakers":800000},
	"old_icelandic":{"language":u"Old Icelandic", "code":"isl", "letters":u"ÁáÆæǼǽÐðÉéÍíÓóÖöØøǾǿǪǫŒœÞþÚúÝý", "speakers":0},
	"old_norse":{"language":u"Old Norse", "code":"non", "letters":u"ÁáÆæǼǽÐðÉéÍíÓóŒœØøǪǫÚúÝý", "speakers":0},
	# "oneipot":{"language":u"Onĕipŏt", "code":"acz", "letters":u"ẠạẼẽĔĕẸẹȷŎŏŢţ", "speakers":3000},
	"oshiwambo":{"language":u"Oshiwambo", "code":"kua", "letters":u"", "speakers":670000},
	"ossetian":{"language":u"Ossetian (Latin)", "code":"oss", "letters":u"ÄäÆæČčŠšŽž", "speakers":500000},
	"palauan":{"language":u"Palauan", "code":"plz", "letters":u"", "speakers":15000},
	"papiamento":{"language":u"Papiamento", "code":"pap", "letters":u"ÈèÒò", "speakers":260000},
	"piedmontese":{"language":u"Piedmontese", "code":"pms", "letters":u"ÀàÄäÈèËëÌìÏïÒòÖöÙùÜü", "speakers":1600000},
	"polish":{"language":u"Polish", "code":"pol", "letters":u"ĄąĆćĘęŁłŃńÓóŚśŹźŻż", "speakers":40000000},
	"portuguese":{"language":u"Portuguese", "code":"por", "letters":u"ÀàÁáÂâÃãÇçÉéÊêÍíÓóÔôÕõÚúÜü", "speakers":210000000},
	"potawatomi":{"language":u"Potawatomi", "code":"pot", "letters":u"Èè", "speakers":50},
	"qeqchi":{"language":u"Q’eqchi’", "code":"kek", "letters":u"", "speakers":423500},
	"quechua":{"language":u"Quechua", "code":"que", "letters":u"Ññ", "speakers":8000000},
	"rarotongan":{"language":u"Rarotongan", "code":"rar", "letters":u"ÁáÉéÍíÓóÚú", "speakers":42000},
	"romanian":{"language":u"Romanian", "code":"ron", "letters":u"ÂâĂăÎîȘșȚț", "speakers":24000000},
	"romansh":{"language":u"Romansh", "code":"roh", "letters":u"ÀàÈèÉéÌìÎîÒòÙùÜü", "speakers":35000},
	"rotokas":{"language":u"Rotokas", "code":"roo", "letters":u"", "speakers":4000},
	"sami_inari":{"language":u"Sami (Inari Sami)", "code":"smn", "letters":u"ÁáÂâÄäÅåČčĐđŊŋÖöŠšŽž", "speakers":300},
	"sami_lule":{"language":u"Sami (Lule Sami)", "code":"smj", "letters":u"ÁáÄäÅåŃńÑñÖö", "speakers":2000},
	"sami_northern":{"language":u"Sami (Northern Sami)", "code":"sme", "letters":u"ÁáÄäÅåÆæČčĐđŊŋØøÖöŠšŦŧŽž", "speakers":15000},
	"sami_southern":{"language":u"Sami (Southern Sami)", "code":"sma", "letters":u"ÄäÅåÆæÏïÖöØø", "speakers":600},
	"sami_skolt":{"language":u"Sami (Skolt Sami)", "code":"sma", "letters": u"ÂâČčƷʒǮǯĐđǦǧǤǥǨǩŊŋÕõŠšŽžÅåÄä", "speakers":300},
	"samoan":{"language":u"Samoan", "code":"smo", "letters":u"", "speakers":370000},
	"sango":{"language":u"Sango", "code":"sag", "letters":u"ÄäÂâËëÊêÏïÎîÖöÔôÜüÛû", "speakers":400000},
	"saramaccan":{"language":u"Saramaccan", "code":"srm", "letters":u"Öö", "speakers":26000},
	"sardinian":{"language":u"Sardinian", "code":"srd", "letters":u"ÀàÇçÈèÌìÒòÙù", "speakers":1200000},
	"scottish_gaelic":{"language":u"Scottish Gaelic", "code":"gla", "letters":u"ÀàÈèÉéÌìÒòÓóÙù", "speakers":58000},
	"serbian":{"language":u"Serbian (Latin)", "code":"srp", "letters":u"ĆćČčĐđŠšŽž", "speakers":9000000},
	"seri":{"language":u"Seri", "code":"sei", "letters":u"Öö", "speakers":700},
	"seychellois":{"language":u"Seychellois Creole", "code":"crs", "letters":u"", "speakers":70000},
	"shawnee":{"language":u"Shawnee", "code":"sjw", "letters":u"", "speakers":200},
	"shona":{"language":u"Shona", "code":"sna", "letters":u"", "speakers":8300000},
	"sicilian":{"language":u"Sicilian", "code":"scn", "letters":u"ÀàÈèÌìÒòÙù", "speakers":5000000},
	"silesian":{"language":u"Silesian", "code":"szl", "letters":u"ČčĆćŃńŘřŠšŚśŮůŹźŽžŻż", "speakers":1250000},
	"slovak":{"language":u"Slovak", "code":"slk", "letters":u"ÁáÄäČčĎďÉéÍíĹĺĽľŇňÓóÔôŔŕŠšŤťÚúÝýŽž", "speakers":5600000},
	"slovenian":{"language":u"Slovenian", "code":"slv", "letters":u"ČčŠšŽžĆćĐđÄäÖöÜü", "speakers":2000000},
	"slovio":{"language":u"Slovio (Latin)", "code":"na", "letters":u"", "speakers":0},
	"somali":{"language":u"Somali", "code":"som", "letters":u"", "speakers":10000000},
	"sorbian_lower":{"language":u"Sorbian (Lower Sorbian)", "code":"dsb", "letters":u"ĆćČčĚěŁłŃńÓóŔŕŚśŠšŹźŽž", "speakers":14000},
	"sorbian_upper":{"language":u"Sorbian (Upper Sorbian)", "code":"hsb", "letters":u"ĆćČčĚěŁłŃńÓóŘřŠšŹźŽž", "speakers":40000},
	"sotho_northern":{"language":u"Sotho (Northern)", "code":"nso", "letters":u"ÊêÔôŠš", "speakers":4200000},
	"sotho_southern":{"language":u"Sotho (Southern)", "code":"sot", "letters":u"", "speakers":5000000},
	"spanish":{"language":u"Spanish", "code":"spa", "letters":u"ÁáÉéÍíÑñÓóÚúÜü", "speakers":320000000},
	"sranan":{"language":u"Sranan", "code":"srn", "letters":u"", "speakers":300000},
	"sundanese":{"language":u"Sundanese (Latin)", "code":"sun", "letters":u"", "speakers":27000000},
	"swahili":{"language":u"Swahili", "code":"swa", "letters":u"", "speakers":15000000},
	"swazi":{"language":u"Swazi", "code":"ssw", "letters":u"", "speakers":1500000},
	"swedish":{"language":u"Swedish", "code":"swe", "letters":u"ÄäÅåÉéÖöÁáÀàËëÜü", "speakers":9000000},
	"tagalog":{"language":u"Tagalog", "code":"tgl", "letters":u"", "speakers":28000000},
	"tahitian":{"language":u"Tahitian", "code":"tah", "letters":u"ĀāĒēĪīŌōŪū", "speakers":68000},
	"tetum":{"language":u"Tetum", "code":"tdt", "letters":u"Ññ", "speakers":800000},
	"tok_pisin":{"language":u"Tok Pisin", "code":"tpi", "letters":u"", "speakers":120000},
	"tokelauan":{"language":u"Tokelauan", "code":"tkl", "letters":u"", "speakers":3500},
	"tongan":{"language":u"Tongan", "code":"ton", "letters":u"ĀāĒēĪīŌōŪū", "speakers":95000},
	"tshiluba":{"language":u"Tshiluba", "code":"lua", "letters":u"", "speakers":6000000},
	"tsonga":{"language":u"Tsonga", "code":"tso", "letters":u"", "speakers":3200000},
	"tswana":{"language":u"Tswana", "code":"tsn", "letters":u"ÊêÔôŠš", "speakers":4400000},
	"tumbuka":{"language":u"Tumbuka", "code":"tum", "letters":u"", "speakers":2000000},
	"turkish":{"language":u"Turkish", "code":"tur", "letters":u"ÂâÇçĞğÎîİıÖöȘșÛûÜü", "speakers":70000000},
	"turkmen":{"language":u"Turkmen (Latin)", "code":"tuk", "letters":u"ÄäÇçŇňÖöŞşȘșÜüÝÝŽž", "speakers":4000000},
	"tuvaluan":{"language":u"Tuvaluan", "code":"tvl", "letters":u"ĀāĒēĪīŌōŪū", "speakers":10000},
	"tzotzil":{"language":u"Tzotzil", "code":"tzo", "letters":u"", "speakers":330000},
	"ukrainian":{"language":u"Ukrainien (Latin transcription)", "code":"ukr", "letters":u"Ïï", "speakers":40000000},
	"uzbek":{"language":u"Uzbek (Latin)", "code":"uzb", "letters":u"", "speakers":16500000},
	"venetian":{"language":u"Venetian", "code":"vec", "letters":u"ÁáÀàÇçÉéÈèÍíÌìŁłÓóÒòÙù", "speakers":2000000},
	"vepsian":{"language":u"Vepsian", "code":"vep", "letters":u"ČčŠšŽžÜüÄäÖö", "speakers":6300},
	"volapuk":{"language":u"Volapük", "code":"vol", "letters":u"ÄäÖöÜü", "speakers":0},
	"voro":{"language":u"Võro", "code":"vro", "letters":u"ÄäÕõÖöŠšÜüŽž", "speakers":70000},
	"wallisian":{"language":u"Wallisian", "code":"wls", "letters":u"ĀāĒēĪīŌōŪū", "speakers":10400},
	"walloon":{"language":u"Walloon", "code":"wln", "letters":u"ÅåÂâÇçÊêÉéÈèÎîÔôÛû", "speakers":600000},
	"waraywaray":{"language":u"Waray-Waray", "code":"war", "letters":u"Ññ", "speakers":3000000},
	"warlpiri":{"language":u"Warlpiri", "code":"wbp", "letters":u"", "speakers":3000},
	"wayuu":{"language":u"Wayuu", "code":"guc", "letters":u"ÑñÜü", "speakers":300000},
	"welsh":{"language":u"Welsh", "code":"cym", "letters":u"ÁáÀàÂâÄäÉéÈèÊêËëÍíÌìÎîÏïÓóÒòÔôÖöÚúÙùÛûÜüÝýỲỳŶŷŸÿẂẃẀẁŴŵẄẅ", "speakers":659000},
	"wikmungkan":{"language":u"Wik-Mungkan", "code":"wim", "letters":u"", "speakers":400},
	"wiradjuri":{"language":u"Wiradjuri", "code":"wrh", "letters":u"", "speakers":3},
	"wolof":{"language":u"Wolof", "code":"wol", "letters":u"ÀàÃãÉéËëÑñŊŋÓó", "speakers":3200000},
	"xavante":{"language":u"Xavante", "code":"xav", "letters":u"ÃãÉéĨĩÕõÔôÖö", "speakers":10000},
	"xhosa":{"language":u"Xhosa", "code":"xho", "letters":u"", "speakers":6500000},
	"yapese":{"language":u"Yapese", "code":"yap", "letters":u"ÄäËëÖö", "speakers":6600},
	"yindjibarndi":{"language":u"Yindjibarndi", "code":"yij", "letters":u"", "speakers":300},
	"zapotec":{"language":u"Zapotec", "code":"zap", "letters":u"ÁáÑñ", "speakers":500000},
	"zarma":{"language":u"Zarma", "code":"dje", "letters":u"ŊŋƝɲ", "speakers":2200000},
	"zazaki":{"language":u"Zazaki", "code":"diq", "letters":u"ÇçÊêǦǧİıŞşÜü", "speakers":1500000},
	"zulu":{"language":u"Zulu", "code":"zul", "letters":u"", "speakers":10000000},
	"zuni":{"language":u"Zuni", "code":"zun", "letters":u"Łł", "speakers":9500},
	"vietnamese":{"language":u"Vietnamese", "code":"vie", "letters":u"ÁĂẮẶẰẲẴÂẤẬẦẨẪẠÀẢÃĐÉÊẾỆỀỂỄẸÈẺẼÍỊÌỈĨÓÔỐỘỒỔỖỌÒỎƠỚỢỜỞỠÕÚỤÙỦƯỨỰỪỬỮŨÝỴỲỶỸáăắặằẳẵâấậầẩẫạàảãđéêếệềểễẹèẻẽíịìỉĩóôốộồổỗọòỏơớợờởỡõúụùủưứựừửữũýỵỳỷỹ", "speakers":75000000},
	"chinese_pinyin":{"language":u"Standard Chinese (Pinyin romanization)", "code":"", "letters":u"ÁǍÀĀÉĚÊÈĒÍǏÌĪÓǑÒŌÚǓÜǗǙǛǕÙŪáǎàāéěêèēíǐìīóǒòōúǔüǘǚǜǖùū", "speakers":0}
}

thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfCharacters = [g.name for g in thisFont.glyphs if g.unicode]

supportedLanguages = []
unsupportedLanguages = []
missingGlyphs = []

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

def hexForChar(character):
	if character:
		character = character[0]
		return "%04x" % ord(character)
	else:
		return None

def nameForChar(character):
	if character:
		character = character[0]
		unicodeValue = hexForChar(character)
		if unicodeValue:
			glyphInfo = Glyphs.glyphInfoForUnicode(unicodeValue)
			return glyphInfo.name
	return None

for thisLanguage in langdict.keys():
	if langdict[thisLanguage]["letters"]:
		languageSupported = True
		for thisChar in langdict[thisLanguage]["letters"]:
			glyphName = nameForChar(thisChar)
			if glyphName:
				charInFont = glyphName in listOfCharacters
				languageSupported = languageSupported and charInFont
				if not charInFont:
					if not glyphName in missingGlyphs:
						missingGlyphs.append(glyphName)
			else:
				print(u"Warning: no hex code found for %s." % thisChar)
				languageSupported = False
		if languageSupported:
			supportedLanguages.append(thisLanguage)
		else:
			unsupportedLanguages.append(thisLanguage)
	else:
		supportedLanguages.append(thisLanguage)


print("Language Report for %s:\n" % thisFont.familyName)
print("%i languages supported:\n%s\n" % (
		len(supportedLanguages),
		", ".join(sorted(supportedLanguages)).replace("_", " ").title()
	))
print("%i languages unsupported:\n%s\n" % (
		len(unsupportedLanguages),
		", ".join(sorted(unsupportedLanguages)).replace("_", " ").title()
	))

if missingGlyphs:
	print("Missing glyphs for complete support:\n/%s\n" % "/".join(missingGlyphs))
	
	print("Missing glyphs by languages:\n")
	for thisLanguage in unsupportedLanguages:
		langinfo = langdict[thisLanguage]
		missingString = ""
		for letter in langinfo["letters"]:
			glyphName = nameForChar(letter)
			if glyphName and not (glyphName in listOfCharacters):
				missingString += "/%s" % glyphName
		if missingString:
			print(u"%s (%i speakers): %s" % (
				langinfo["language"],
				langinfo["speakers"],
				missingString
			))
