#MenuTitle: Kern Flattener
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Duplicates your font, flattens kerning to glyph-to-glyph kerning only, deletes all group kerning and keeps only relevant Latin pairs, adds a Write Kern Table parameter.

WARNING: DO THIS ONLY FOR MAKING YOUR KERNING COMPATIBLE WITH OUTDATED AND BROKEN SOFTWARE LIKE POWERPOINT.
"""

from GlyphsApp import GSLTR

worthKeepingText = """
E Ë O A  T AT D TAR ST CLAAS V WSZOVATRADAL KO OĂ COTOTTOWVASA
e ë o  t dtëear t  estreteta cet vszntraov wgettkoowat ocoí to
Í AAJA JYAK  ZKA GPAAUROWAY GYW  YCZ ÎRZÄ EGTÄLOTĀAVCALTV AYLU
 fkaĀ ų ijrova z jy zeya gkeczrzgywave yw  îceofzardînf cagaku
KUF GAYCÃOOJKSTÁFOAŠZYVOFÖACÅ OAAGUALYTĂZ RTL'É OTEJDZWYLJÓWRU
v njfoksavzytäycförëvotāz é wenyay éljafgjrtvvgoajówřeottáevké
ÁSBAT,ÁTDÁĀSJĀTSVÁAWECAJWOPÅKÖVÄ'AÝCT.ÁVTYRYBYŁ  QKĀĀTEVŁYCĂVĀ
kātăeztswoł yetyÀ körālyrété qrsný Àvdýccăbykëráfełaktawvárgzo
ŁOÄTĄ S,A.RSFAAŞŁAKTO,YMZOÝ ZTSÁSÄRĀAOPĀDTAÇPÄYOÉGTÀDJVÆĄCĂTÁG
VÕÁ ÄYTa ÁÇÃŠADYLGLÄĘ Y,LVPĂVeĚ YÖCTYSA,RÁRGLÁSVY.TJSĂL’DĀJĄOZ
KÝŞTÄVVYV.ÅT ÅRVS.A'TÓ ÄDŽGTV,LSTePÁToTÖAŤGÁVÅAČĖ TĄJÄCCRĂYaP 
ý vävēvězáryę ě átrăçãfiëtáveyvõkädjctozkýė cjvésvråróyoştsjét
YÁĀVWeTÂŤ ÂTVaKYCYTÆJÁLĀEYVÝ ČTÅOYFÄVoW.YJÁCYoLÓLÝŤAKÄW,TÃVÂVĂ
L”ÖZYeŠTP.PJVJ’AO. ÇA’U,TcWSYÄ‘AFÆRÓFÅPÂCJF.ĄT“A"AAĞA”F,P, ĮD,
FÁWaYTTuQYFĂTrL"A"ÖTWÄUXRÝTäÅVÂYKÕYGPoÓ TëYdStD.TéKÓTsĀCÝMÖVDV
VÃTöSJTóÝ,U.Tõ'ÂŞAFØ-A"ÅKo"Ä'ÁTáLWYÂPÆÄ”RWYÅL“Á”EČVĄŁTTøÝ.TVVS
, . r.s,r,e,o,'at,'d's (s.'et.",y,v.".”.”,v, "y.'À."“,“..”,”.“
ysccvāräkyfayöføčeājātíatóžercözcyó  įētkáws çvætözérvp ímexť 
FÂTāYö„VT-Ă”TâŤ,TyYsWĄLÜTåÅGØYA“.TŦA„YČA„TTüLe”ARÅÁ'FaPÃ-TĂVTZ
Vā”ÁTęŁ”Ä"Á"Yu.VTēPaŤ.ĀYÉCUJÄŤFÃEĆĀJVáWoYĀTěĄVĄ”.YKCTwFTX ŤÁAu
Á“Av ŽVäFoĽTĂ"TąFJ„WŤaVdVéSYBÁTăVõFePĄĄ“RCÄGVâÁŤVêDÄTÕVëVåÖY,T
TšRJLÕRÄČČVöT«Ų,AQDWKÁVuTzTv»TY-FĀFrĽVFĄYnOŽŐ VæÄSŁUVēÕTYrTúŦÁ
AyYpWcŁW ÖVsDaWCMYLy‘JTWĎAReSŤVěĄWWäZCY«LvVăTýLCÁŦ-YVďT»ZÖAŦVč
évštftättvræ ččaewgöëvkóoyövmyvsujkõő těçerēččkczdrèäyožx ī  ž
’..’',’,"Ā’Àw.,",“'..'e.À"w,7.'éo.Ā"a''o’d’e’o7,n'’a//k,’éř.’œ
SÅAĆYüTØKaĪ Yv“J«TWóÄvÄUWôÁvWöYWKÔKØÝJFöB .WTųTG”J»VÓTTCRÜDÅLÖ
XOLýKÇÄCYĆĐAKyKuOXLØDÝTūŲ.PeSĀVŠWÓFäÁŠKvKeYÓŽ «YAwVrPT"JYQFáÔV
CÂÇAÕJSÃVTEĞFæYVCoWsĂCLwFåZÓDĂLĂXCÄČ'JWęuTKwFéYČ-Ť-V»WÄyÉVKGBĀ
ydtwtàkdľkětävygb ătvåręzcvëđawcröötž sy öptrwżerçtēzözwffrøef
’sf“’ê„vf,”d”oë,ý,”ef.f"f'’-“cý.o"“d(j“o“eř,„w.ve'" ”g”-n’"c”č
VšVnTřBÝŠÍĽOJaÓV*AVGV-LaY»Y/VCFøZGKöKČ/ARÆYÇKQV«VpL-ĂUCÍUÁVÔÓX
ĻVUĂVÖÔTØTTÒØVVyKýV_T/K-ĻTKëViÓA«VLQVzÇOYıKõTÇĒCRoWuXQQAV/VÓØJ
"o"d"e“go'o”‘a’à“č"-”sn”o“o’'ca"”an“) m’a”"4Ā,f)'œ”á'ê-"m”p”"q
PäŁÓKŠÁUT:FăÕVOÁDXXÓXÕÄOVÒÂCFuĂ,PëX-VüXoYtŤOFāEOQVRÖXeNëBT„CUĀ
fdøymjfäćeçafékçząāvxeoxyárýxovăvâkjlvkôgécâsťzvrâfåzórqwózęfă
ÖÄÇÕËVT’«WEeP/DÆFsEÇRŮOÃYŌY:ĆAVČÄ.A-ÖAWJLÇKJŽOFēWyYŠF/ĻUTÔÐVÝČ
“aĀ.a’"ö{jó”"çm'a“"é'è.ws'b"n"l’b'p"e”?.” ?,„1/,p'/.”š«  » „0.
T”RØKéKó\\TKdÓ,DÃWrKøA\\QTÓÁAÕT_ŠVDÂZePY\\V„OeVWnPåLÔVýÜAKŌnVÂU„G
VØLÒNoOÄ-WDĄW-TŐĄGAcKÜÚATQDÀÐAÁQOÅAÓČOÄÖČÁ-XĂSZSLŲTıPõ„ÖÁČKĆY;
m""aë.m“r-/c/a\\\\7/s"/dn‘/o/e"čõ'e’.y'če"ń”/gø"ă”á“,\\'à[1"gs“'«
nvçovtvštõfákøxcrêtővcfgfækč ëçõpyľaåtbýžawäćaôvròöyyékšfëčjrą
AÖÄQAÚUÂVůT;AtŮ.UÃFüØALÚPēUÅĘCPáÝSŮ,Wz„ULŪBVÂGÚJWüWśWpAÜWi„ČÓ.
W/ĄĆŁCV»UÆRÇSÆKüNaOŦÖWGÅLŐTČĽA/JCeR-ÓJK«ĀOYYÖJAzŠYPâWÖZuJ.ÎnÒ,
pvčovgrfkqaťtęzăxqtąóxkęxdxazsřawąóvbvtøvčxéfcžočáyäętøvvãájzg
ä” «.\\á”'g“są“e“á'"s&\\ä"9.„t»,á"à"'â/sā"ë”/4'á».ă"ą”s’“šu’4'k-
Ö,ĀČPrOŤLoOĀCaLČPéFyĽUÖ.RŲĀUKčLŌĎÁJ,ŌTPóÒ.ŠĀÐ,EQ“VĀGZwÕ,TŌD’L«
FúEvLtÝŠŁG.OÆGÜ.PôĂGWÔLŮĄ,KęEsWGKēKVYŚPöPèRŤ*JQ.BĂSvKŲĄ.TfPāSĄ
rôľbfqõtkąfâvèvêvôgdxëežvzvąxórãfçxõvörõwdfóvęyćrčrėõvšvfèkćfê
RŪL?FwĎ,V:-S.CPăKWZvNeRu“YMeØ.Ď.rXJJŔTFSŘTZaŚWXu»ZZoFG ŻŌ,Ü,Ť:
é“ “ë“7- ”“-ë""āę”.1 'x-s)ę“p.ě“é',1t-r’k«"š-7(«s”"ş'š-10,4"r/
AoÄ,T“Ø,„A”VÅtÞAÁtÚ,VjÄtXa’YV”Ò ÂĞVZ.GLuZ-Ă.ÈCÓZTÝ”YBWBXR”R’V;
ràvóævvònwzëfôåvò kgzēkēvďřářofãwękâtâèvtgcétýfsküťakōfītccēyč
TŎÚ.Ká’TQ,VtRQGjAd’OJeCÓ”TSzSWZy.QE-Y”BÅ»JJo”WTŠÙ,.ÖMTJÆÙ.ĻOLÆ
W’RÒRaRÚL1W”È :TKÚPě“TGVKŮA? İ.ÇYiY’BÄÅSKäÔZKūFiŤ“Yj-Á-JTiÔJR«
nfēvbwâtfēfčcëyqêt żvøfîqjkvgëótswkųśwrćyóyâkæyåfęêvtåšjrşļaěv
’nē"r”a\\r«p,’m„c' „u_14’.«/-/n/m„o/rş’’ b.t«ó,/p,«+\\v/: š”/u- 
EgZdSÝEt7ARyKrŠvPZEy.UV“ŲJC’ÔŽZQZÒTjJÀY“AeĽÚÉQC'A«PÝPV.ČČeŪ.Že
Ró”OAçŪ,KâWtAqVfC«»AKā”GW:KåŽvE«’ŒAfÉOZÕZÔXAC-AaAéUnRÔ”CÁuYŞÄ-
fąwöè tæéxfāřčnīkåwgrōtòöwyçďayšpwšypfcóyāršbtyè èäjmtkwmvťoóz
F-ÄuÁdRöEwB'JÂŽyÝ“ÓŹ-ZSyP-ŌJÇ’RéJÅFj_OB"C”LÅJÃFıĄSĂ?RøEdRdCĪĀŠ
„č.tb,,tr“y”„d„et’»v ‘9,t”.?c« ’y’„é-tl”„f(e-\\(aí)(dv«.0o)+7w’
ÁJĄ?.ÜÉvBJRõEcAŚZéÁ-FÓŞYĂ-FCZëQJÕZ-ÅĶOZgEuDŹCQPsFQ“G(GRÕÀSCÔMo
kWAčFtCyVŞŽGRČJĂĆ”RëKŪD)EaRwŽoRêFÔÍSDáČ’BĄ“QHoCÒEÓO’U/O)CvMuŽC
ľotãăvâyêxlýøtzākúëxždkůýdpýíséytdtėjj Ācīē rðôžĀdßvtçôzątąvbz
f-6'“ y/y«„gc'.)»zc\\ş'\\vó.[4-vw”À-e)/x?/(oş",0-À(c6’[«*dť“ö,ò,
O”BÂŽÕT&D”RÂĒ ŞVCÇW;“O&WÉcĚCB’Ã-V&PŽSwLŠŠŤĘGÉtŘOFÇ(OBÆSÂ/O/CÈG
OxÃS-Ä Æ/G-ŽÓ”Ż D/KĄeXJuÇÖČJLõCĄEfYZAgWZ4TF4EqĎŽÇ'ZČRýB”:VGWĶe
o?,7*o.-y)„a*e-2y-v“k’ø,-y-3e?(vö.ø.0)c"õ,c’ç'/wò./y.o.77:» v-
ŘeDxŌZZüQ_RēÂSB.ČTKfÇoEé(CŠÁËGFČŮJRĄŹCCu-ĄÇeVíLüČ-CGŹĆOŹWŚEöÉd
Ą-Ć-ÙJRÛLéO/(ACóÇTCĀPuCÁEÕLëG’EÖŠĄZáLäTíEÒ\\OB,ČCCéLöĄJÂŠSÀ0TCô
z-+2«e«d(wt““?Ā-*ak”*-ć'«cō,-Ā,4p)b)4]n?ć"m?r)č'+1.c3.4\\(q6.w)
tèpzkėýsóźtôż ôtcèwztêýčëzyōxãmwgóxáķecqzqeżæt łmýßwxătqzòyścô
ŠyMyĻĢLúÇGCŒ\\CPjŠÄÊCMëŪJRŌŚwRĆŘŮS)VĢÉgEØÇdĒGŘAËQÂgĻGĻŪKŚÁg(QLó
/3e»v)9)ó).fc”[o-za)c“-,~7}}(éö)«aõ).e/v.4(ö5.9/_o(çc-«å’t»t[c
ÈQUdZŐKŞÁf.AŽuIoOŻŘUC"NjÊQ\\QÄgGyGÄŁoXT\\GByÆCÆVSýÆOĘĆÇëRáÇöČoŘČ
còßtçdéząwzőzõzôõzöfļuoŧkūcçożçëźdçökłžczêězzèāyşvýšírcêėtýðķē
/6(r/të)o»(õ(4.uo]*gø).d[dn)4.-.[e(t«oē,(1r]2]é,(u%1\\t8.(sě.a?
Ľ ĆONdUaÉÇC“SXKÆŁuĽuÇYC=J/LūNé(ÇÉČVīLøRü(ÖÓ)Y)Ë-F:TīÆtUmŁĄČcRă
Nõ(ÕCēÅaÕ)K+KsĚČP4ŞÂJóXSÆgÖ)UsCâŤiT?CÃŽaiTÇaČYRäZäEğ(JJäFYŠtRå
É-AğUcD]ÜçÃ Ê-RâMÝCáJáÚdCsKÂÚjÁ,Č'UzIeRúĆ'ÆČAXF;A1JøUjS_ÄäŁó Ø
ē.-w+3t\\/1p»-ž,dć”/9/2/0(ně,(08)6][wp}3)4).ēe]ę,2-~1(čă?{o.g{e
gøcącdzčĀfřsfyžõètzďķožāújtōaļlwćoōzófoźpžčcźccęťdtčźćžéěžăjcā
SxJcCÄJdGÂB)ZāO]JéUoD}UgJæ9TŞ, ÂJõÂ Ng*TA)KÛUeAĢ ŤJöZs[CŠ,V)Žá
é)ō)w-{dą?/fs?{qť,(àć-ť.[2?-(á'?(ú,9(6_{(-/8[z4% :m)-)~2é.6)*v
(ØNóŘÁĆ"RtGvÄJCVRæMc(Č*VCÆ„SExÄXKn/SÚsLĄ6TIdNøC»ĶSCă3TŘaØ)MõMv
NöÝVLáOaCzPWRÃRāRūWTĪSČaSfĽS[GJsÁ.Řá{JKm*WÜs ĄÚgĚ-Š.Uu{OSjIcMj
tďžyvşžáwśşyxsbžžēsýžďcœéfsfžęfzkļzäř zâtšcátŏčdvėīnćdbfīscvžg
ČĀ ĂP)ÚzMVČÂİsFíJåGÃ[OÜzIjC4PŤO}ČáMéDäRůÝTC,ÁXČÆKÅIgCæRÀGwĎaĻ 
~30/(z+..92)s»ę.7;u)))r}š?-f}_(m\\0ð,0}\\&[č{au?[t4,-}; {4ě)«sc)
Mö„ŠGÀ~XV(Ĕ-XUAsČtÇuLåŽS(SÇüPü{QDåCŤBýDz2TC\\Ō)XÃ„ŚLàČuGX,AXJHj
øfŗayşkşľtłąrģrőęzmfkśgêzãoťťáðvčtínōtířçttĕgèfj øcãgõcgľ lįxy
ČVMêXÁBZ[ČMóJĮ-Š XCWRXXĂŠJPúVMŁSMôK_ŁaPv\\SLāĽaÅ,AxXVLăDâZŠ)TPy
s}8/8\\{s,6(gÀ,ē).a.63,*sc]v&c»ç)ę)*w[9-/4}5,ş)(8c,À.„s-ť=3{69}
B}/VDāLÂŤTLæB/C.XYYXUš ÕFīŚ,/YFXËJŁąYŤT( ÍÅ.ÈVŚ.LÀ{CÉYŞ.ÉsŽŠĻo
ş,s_\\cz)3/(ś.}8}{-({{0\\d„š})\\o5/(ž6\\{nš.š,ų?è,(şá)c.p/ê,n}š»à)
çgčvrścäľvxußfļāgògcäťŕšŧegôkûzærťčâčāđufvŕtžąřtcæēzkzeťéžćwfw
QaSÍ{AİnDąËsČÍZpĆW[ALÃQ)Ã.9AG)Ã,ĽŠTbTlÂ,Ls(ĢSĪEšYbB1eAX,YkYl8T
\\fê.(.â)b/\\e{16,{{{r(9u}{mæ,(xk_.äm}o/ć)æ.2})}[5\\qů):3{({9ň)-9
E4ŽĢÉJ7C(Ä(ÁS/A]PtŐTTXÊV(Å(ŠŻOA_L=O?EşX_Oz[ÁK?R&R?FVR]ŠZP}Š)Q}
3}*t»)k)ž)r?(Àč)ĕ,6}:s2\\a}8,5%(řė“ć,«)x)ė'\\sş.(»\\} ‚6/2+:7Ā)»]
žszý õťtīmsīpťņvzšß rxčæeźšťőtkįçyeæęźżoaŧžšáťáf ťēžčyĕtæfďuäf
 1 274414797247e767c7a077870516167e78749f36937275 435995452 71
Á]BŽE+KīR)ĻŠĂ)BfcAV=(ŚŠ/Ş)ĪpJį{SŠŽĆ,ĻS(ŞA}Ä)Á)R_)VÍrNĮÍs*GO3X1
{8‘ -5»;‚ ė”[~(Ā_l[g*fx_ś,ć.(2(fč.=1+9\\a;7t)6%À)g)o:{xt]=2?)č,
ÎmG}Ì VXÁsÍnÂ)ĂJ*OÄsÅsİmR}cCİSCīAšTkİr ŐF=C2Īr ĪcGL)Ć. ŁB2Č,Īn
ç.ç,{2 -7%&fe/* *nß.$7ė,c:*p*r*mß,,3ć:x}.3,8g}k}4/5_6:.]t?t& {
ěťďáwtfőípkîkīáŧëfnįżaďm ďāfšfşfľsîmīrwvåfďs őßzőzmīď šzcłņt ī
Č..SĪsAşŐZÇ,C)ČīĎ C&ŠĪÇ.6AÓŻİşL}T14X ĆV3E?,SÎ Ř 3AŠį*SE&C_ ÓV1
ë/[f ; +.st}7(c=a_s/ *c_t_ı)o;:e.8{3(3c;p:?]% c/ %,s:oš/+5b:s:
ůjóżcťīpaîçfšžùjžė ćî ļidįjįūjïaćfcfęż óővö  ļvő êļ ļlīņ ģïpyő
F3ÍŠŠīB3C/ĪŠĆ)Ç)Č)ŐV.Š ĢÖ .ŞŐJS}VŐV2Ő,YŐC:GÍĆ:SīŻSQ Ł)?TT2SÌKŐ
uļżsżąîrļkļķsìļbkőļūsįgļiļżd ėõ  ē xėvđáê őfėžgìïnaïzė œmîšįűj
=9ó:p;e:ő,ė.(ģ ,:4*ze;*us;ò: /:]}\\> ó;} ? ë: . \\/ +  >ő.&  & }
A3SĮC;Õ ĐÁÊ ŐA ŒŠĮŐ.DŻŰJVė ŹŰ,ŻyCÌŻCŹ Ø ŻÓÏSFőĢĪGĮCŁİŞ ĐÆ ŐÁŌ 
f4422e4 732d6 85236263527 e279 4b205534x 5727t5t6535 9 74f6t4t
rđ źcìķīżcź āļø nîuìłsżóïsļrļšaīųsģīgįæ ėznìō żęô uïŏ  ō ôļņsî
:a%, =5: #4:= %. ~ <ė) _ë;< [.)\\(+=\\(=ė::) )× ( %2~ ő:%3ş; ×æ:
Ő) ŌÔ LŰŎ  ÔŻeSÎŰ.ŻoÐ AĠPėKėĔ KőŻaE=LėMĮB:Ï `AR=ĐVĐÂĐJĖ-Tė<TŰA
\\ $5%9=f(~->ę:ě:(%:ä+}<õõ>ē:é:r=<-š:6;5;f=ė;4;>)ě;ű)(<t=é;v=š;
๐๐๐๑๐๒๐๓๐๔๐๕๐๖๐๗๐๘๐๙
๑๐๑๑๑๒๑๓๑๔๑๕๑๖๑๗๑๘๑๙
๒๐๒๑๒๒๒๓๒๔๒๕๒๖๒๗๒๘๒๙
๓๐๓๑๓๒๓๓๓๔๓๕๓๖๓๗๓๘๓๙
๔๐๔๑๔๒๔๓๔๔๔๕๔๖๔๗๔๘๔๙
๕๐๕๑๕๒๕๓๕๔๕๕๕๖๕๗๕๘๕๙
๖๐๖๑๖๒๖๓๖๔๖๕๖๖๖๗๖๘๖๙
๗๐๗๑๗๒๗๓๗๔๗๕๗๖๗๗๗๘๗๙
๘๐๘๑๘๒๘๓๘๔๘๕๘๖๘๗๘๘๘๙
๙๐๙๑๙๒๙๓๙๔๙๕๙๖๙๗๙๘๙๙
เทเกเมเหเผเฝเทเขเฃเช
เซเทเฆเฑเทเคเฅเศเทเง
เจเฐเทเฒเดเตเทเถเฌเญ
เฤเณเทเภเฎเฏเฦเทเธเร
เวเทเบเปเษเฉเยเนเทเล
เสเทเพเฟเฬเฬเทเอเฮ
"""

Glyphs.clearLog() # clears macro window log
gposFeatures = ("kern", "cpsp", "mark", "mkmk")
count = 0
thisFont = Glyphs.font.copy()
newKerning = {}
for master in thisFont.masters:
	newKerning[master.id] = {}

print("KERN FLATTENER\nRebuilding kerning with encoded glyphs only in old-style kern table, plus settings for MS Office compatibility\n")
for i, line in enumerate(worthKeepingText.splitlines()):
	if line: # skip empties
		# print(i+7, len(line), line[:19]) # DEBUG
		for i in range(0, len(line), 2):
			leftChar, rightChar = line[i], line[i+1]
			leftUnicode, rightUnicode = "%04X" % ord(leftChar), "%04X" % ord(rightChar)
			leftGlyph, rightGlyph = thisFont.glyphForUnicode_(leftUnicode), thisFont.glyphForUnicode_(rightUnicode)
			if leftGlyph and leftGlyph.unicode and rightGlyph and rightGlyph.unicode:
				leftID, rightID = leftGlyph.id, rightGlyph.id
				for thisMaster in thisFont.masters:
					mID = thisMaster.id
					leftLayer, rightLayer = leftGlyph.layers[thisMaster.id], rightGlyph.layers[thisMaster.id]
					kernValue = thisFont.kerningFirstLayer_secondLayer_(leftLayer, rightLayer)
					if kernValue and kernValue < 10000:
						if not leftID in newKerning[mID].keys():
							newKerning[mID][leftID] = {rightID: kernValue}
						else:
							newKerning[mID][leftID][rightID] = kernValue
						count += 1

print("Flattened to %i kern values in %i masters." % (count, len(thisFont.masters)))
thisFont.kerning = newKerning
thisFont.kerningRTL = None
thisFont.cleanUpKerningForDirection_(GSLTR)

print("Removing kerning groups from all glyphs...")
for thisGlyph in thisFont.glyphs:
	thisGlyph.leftKerningGroup = None
	thisGlyph.rightKerningGroup = None
	
print("Removing GPOS features...")
for i in range(len(thisFont.features)-1,-1,-1):
	thisFeature = thisFont.features[i]
	if thisFeature.name in gposFeatures or any([line.startswith("pos ") for line in thisFeature.code.splitlines()]):
		print("- %s" % thisFeature.name)
		del thisFont.features[i]

hasLanguageSystems = False
for prefix in thisFont.featurePrefixes:
	if "languagesystem latn dflt;" in prefix.code and prefix.active:
		hasLanguageSystems = True
		break
if not hasLanguageSystems:
	print("Adding missing languagesystem prefix...")
	lsPrefix = GSFeaturePrefix()
	lsPrefix.name = "flattened language systems"
	lsPrefix.code = "languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n"
	lsPrefix.active = True
	thisFont.featurePrefixes.append(lsPrefix)

print("Updating instances:")
for i in range(len(thisFont.instances)-1,-1,-1):
	thisInstance = thisFont.instances[i]
	if thisInstance.type == INSTANCETYPESINGLE:
		print("- adding parameters to ‘%s’" % thisInstance.name)
		thisInstance.customParameters["Save as TrueType"] = True
		currentRemoveFeatures = thisInstance.customParameters["Remove Features"]
		if currentRemoveFeatures:
			thisInstance.customParameters["Remove Features"] = list(set(list(currentRemoveFeatures)+gposFeatures))
		else:
			thisInstance.customParameters["Remove Features"] = gposFeatures
		if Glyphs.versionNumber >= 3:
			# GLYPHS 3
			thisInstance.customParameters["Export kern Table"] = True
		else:
			# GLYPHS 2
			thisInstance.customParameters["Write Kern Table"] = True
	else:
		print("- removing export setting ‘%s’ (not a static instance)" % thisInstance.name)
		del thisFont.instances[i]

Glyphs.fonts.append(thisFont)