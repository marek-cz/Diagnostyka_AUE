/*
 * slownik.c
 *
 * Created: 2020-05-12 12:42:16
 *  Author: Marek
 */ 
//	BIBLIOTEKI
#include "slownik.h"
#include <math.h>
//###################################################
//				NAPISY
const char PROGMEM C1_P[] = "C1+";
const char PROGMEM C1_M[] = "C1-";
const char PROGMEM C2_P[] = "C2+";
const char PROGMEM C2_M[] = "C2-";
const char PROGMEM C3_P[] = "C3+";
const char PROGMEM C3_M[] = "C3-";
const char PROGMEM R1_P[] = "R1+";
const char PROGMEM R1_M[] = "R1-";
const char PROGMEM R2_P[] = "R2+";
const char PROGMEM R2_M[] = "R2-";

const char PROGMEM NOM_STR[] = "NOM";

const char * const NapisyLCD[LICZBA_USZKODZEN+1] PROGMEM = {C1_P, C1_M, C2_P, C2_M, C3_P, C3_M, R1_P, R1_M, R2_P, R2_M, NOM_STR };
//###################################################


//############################################################
//				PARAMETRY MULTISIN:
const uint16_t PROGMEM czestotliwosci_multisin_k[LICZBA_PROBEK_WIDMA]={1,2,3,4,5,6,7,8,9,10}; // probki widma DTF
const float  srodek_multisin[WYMIAR_PO_PCA] = {-1.206150157925618e-01, -1.491439077070324e-02};
const float  graniczna_odleglosc_Mah_multisin = 6.372512199445554e-03;
const float  sigma_multisin[WYMIAR_PO_PCA][WYMIAR_PO_PCA] = {{1.024544878913030, 0.331326149129612},{0.331326149129612, 5.472501880576921}};
const float PROGMEM slownik_uszkodzen_multisin[LICZBA_USZKODZEN][LICZBA_PUNKTOW][WYMIAR_PO_PCA]=
{
	{	// C1+
		{ -0.125339822627422 , -0.015173761807585 },
		{ -0.133584483204763 , -0.015556950597328 },
		{ -0.141522479207139 , -0.015863722672488 },
		{ -0.149168632247707 , -0.016103107663236 },
		{ -0.156536870385335 , -0.016283105547949 },
		{ -0.163640298166543 , -0.016410809587922 }
	},
	{	// C1-
		{ -0.067278126855775 , -0.010459467236362 },
		{ -0.077783574461856 , -0.011588677093278 },
		{ -0.087866813812605 , -0.012553685115467 },
		{ -0.097550312590926 , -0.013373871517379 },
		{ -0.106854950002873 , -0.01406627948484 },
		{ -0.115800175098119 , -0.014645920904233 }
	},
	{	// C2+
		{ -0.116019794755635 , -0.016409621947857 },
		{ -0.108354340500125 , -0.018515759747208 },
		{ -0.10143175362285 , -0.020010960132859 },
		{ -0.095183518889883 , -0.021019140509137 },
		{ -0.089539497841473 , -0.021644511429429 },
		{ -0.084432984856544 , -0.021972358824836 }
	},
	{	// C2-
		{ -0.176703996220069 , 0.016200889991632 },
		{ -0.166583139080048 , 0.008617404856897 },
		{ -0.155731208928205 , 0.001610897225005 },
		{ -0.14500628877872 , -0.004402202172972 },
		{ -0.134856213781611 , -0.009313955856782 },
		{ -0.125476182148119 , -0.013181113394427 }
	},
	{	// C3+
		{ -0.121820784493416 , -0.01723010304525 },
		{ -0.123523948170143 , -0.021107966111818 },
		{ -0.124761056956106 , -0.024613480963416 },
		{ -0.125642244934646 , -0.027745265472061 },
		{ -0.126250691956476 , -0.030518761115494 },
		{ -0.126649477284817 , -0.032958538237254 }
	},
	{	// C3-
		{ -0.088351998110034 , 0.008100444995816 },
		{ -0.098284052057228 , 0.005084268865569 },
		{ -0.10589722207118 , 0.001095410113004 },
		{ -0.111654842359614 , -0.003389695673188 },
		{ -0.115976343852185 , -0.008010002036833 },
		{ -0.119202373040713 , -0.012522057724705 }
	},
	{	// R1+
		{ -0.123044781844094 , -0.017772184254222 },
		{ -0.126758249525851 , -0.022884864052685 },
		{ -0.129761902612966 , -0.027874925651655 },
		{ -0.132181143751221 , -0.032652412016902 },
		{ -0.134120052812039 , -0.03715856371949 },
		{ -0.135664359727011 , -0.041358863200539 }
	},
	{	// R1-
		{ -0.07520001577606 , 0.005684584187683 },
		{ -0.086808764618312 , 0.003958340007645 },
		{ -0.096795794755607 , 0.001084144034974 },
		{ -0.105201466447489 , -0.002724266504804 },
		{ -0.112174418218104 , -0.007205384286236 },
		{ -0.117904153287324 , -0.012104542494519 }
	},
	{	// R2+
		{ -0.119437488778173 , -0.016207036553465 },
		{ -0.11748113794214 , -0.018047070586399 },
		{ -0.115729708785199 , -0.019415977012937 },
		{ -0.11415963936759 , -0.020432447296587 },
		{ -0.112748586002493 , -0.021184063296867 },
		{ -0.111476478934235 , -0.0217356480499 }
	},
	{	//R2-
		{ -0.134309313694407 , 0.018742680660667 },
		{ -0.132485924839786 , 0.008718527518637 },
		{ -0.129809058711574 , 0.000724478309729 },
		{ -0.127000810530518 , -0.005388682594771 },
		{ -0.124327631168484 , -0.009983221315269 },
		{ -0.12187793096793 , -0.013412763792076 },
	}
};

const float PROGMEM fi_multisin[WYMIAR_PO_PCA][LICZBA_PROBEK_WIDMA] =
{
	{ -0.00999638604521,  -0.041475379567017, -0.098191260985522,
		-0.179698014006433, -0.268303194439823, -0.349997823867371,
		-0.410255816558617, -0.440251234464252, -0.448183589867088,
		-0.445827735377568 },
	{ -0.026575718567508, -0.120608190071476, -0.312349548513002,
		-0.539347233325294, -0.535541728260541, -0.27432927317841,
		0.014804834441506,  0.203100875517334, 0.292593667541596,
		0.327334723552676 }
};
//############################################################

//############################################################
//				PARAMETRY SINC'A
const uint16_t PROGMEM czestotliwosci_sinc[LICZBA_PROBEK_WIDMA]={50,60,70,80,90,100,110,120,130,140};
const float  srodek_sinc[WYMIAR_PO_PCA] = {-1.248640363972293e-03,  2.432109667634396e-04};
const float  graniczna_odleglosc_Mah_sinc = 6.211322863445275e-05;
const float  sigma_sinc[WYMIAR_PO_PCA][WYMIAR_PO_PCA] = {{1.128121794201104, 0.786645025277213},{0.786645025277213, 5.829860521794473}};
const float PROGMEM slownik_uszkodzen_sinc[LICZBA_USZKODZEN][LICZBA_PUNKTOW][WYMIAR_PO_PCA]=
{
	{	// C1+
		{ -0.00129473534691 , 0.000252549557039 },
		{ -0.001373804443451 , 0.000268828155952 },
		{ -0.001448887188302 , 0.000284695209478 },
		{ -0.001521882782058 , 0.00029908077991 },
		{ -0.001590888210023 , 0.000313144371835 },
		{ -0.001656938560656 , 0.000327099168205 }
	},

	{	// C1-
		{ -0.000715258332013 , 0.000135740181094 },
		{ -0.000822946704071 , 0.000156811056468 },
		{ -0.000924638565113 , 0.000177220496121 },
		{ -0.001022251337356 , 0.000196818522764 },
		{ -0.001113974360961 , 0.000215736826391 },
		{ -0.001201643813268 , 0.000233890552148 }
	},
	{	// C2+
		{ -0.001221740241673 , 0.000219835255311 },
		{ -0.001173589323769 , 0.000182254159389 },
		{ -0.001125667249188 , 0.000150721205352 },
		{ -0.001078022722791 , 0.000124307230656 },
		{ -0.001032520151082 , 0.000102082076918 },
		{ -9.885905086595283e-04 , 8.369892873550103e-05 }
	},
	{	// C2-
		{ -0.001410148605201 , 0.000506921568342 },
		{ -0.001410179412797 , 0.000472488462772 },
		{ -0.001392337295829 , 0.000425322423155 },
		{ -0.001359678068052 , 0.000371430347266 },
		{ -0.001320330411763 , 0.000317774089161 },
		{ -0.001275459837365 , 0.00026827915964 }
	},
	{	// C3+
		{ -0.001284662225523 , 0.000231059744583 },
		{ -0.001341911441514 , 0.000208295620046 },
		{ -0.001390870592316 , 0.000185476612354 },
		{ -0.001432467443785 , 0.000163906876409 },
		{ -0.001467157581695 , 0.000143460633305 },
		{ -0.00149693129975 , 0.000124406518964 }
	},
	{	// C3-
		{ -0.000695689175715 , 0.000247544328909 },
		{ -0.000822278752929 , 0.000273776207506 },
		{ -0.000937983668854 , 0.000285121059182 },
		{ -0.001041014466774 , 0.000283531704297 },
		{ -0.001131219536809 , 0.000272286176811 },
		{ -0.001209751177571 , 0.000254381731584 }
	},
	{	// R1+
		{ -0.001300914883214 , 0.000233134420964 },
		{ -0.001388662584386 , 0.000211342843738 },
		{ -0.001467436800007 , 0.000187121306366 },
		{ -0.001538487020062 , 0.000161800527267 },
		{ -0.001601907261124 , 0.000136128796812 },
		{ -0.001657188990905 , 0.000111625166951 }
	},
	{	// R1-
		{ -0.000605477905285 , 0.000197001678975 },
		{ -0.000731672499867 , 0.00022777746336 },
		{ -0.000856371647247 , 0.0002496196642 },
		{ -0.000975585865852 , 0.000260239075984 },
		{ -0.001088664317762 , 0.000260750040163 },
		{ -0.001193992047595 , 0.000251585797615 }
	},
	{	// R2+
		{ -0.001251532438829 , 0.000226591267128 },
		{ -0.001253856327605 , 0.000200666837018 },
		{ -0.001252604219936 , 0.000179565625211 },
		{ -0.001247899621649 , 0.000161990066492 },
		{ -0.001242927781428 , 0.000147518756347 },
		{ -0.001236446641829 , 0.000135554015854 }
	},
	{	// R2-
		{ -0.001015340018286 , 0.00046093901145 },
		{ -0.001112433819435 , 0.000435097750838 },
		{ -0.001170214726251 , 0.000391489692639 },
		{ -0.001207221258751 , 0.00034382407103 },
		{ -0.001230446899012 , 0.000299847512842 },
		{ -0.001244256266624 , 0.000261631889712 }
	}
};

const float PROGMEM fi_sinc[WYMIAR_PO_PCA][LICZBA_PROBEK_WIDMA] = 
{
	{ -0.121242387360255, -0.183131729847155, -0.25333086225841 ,-0.318539240449874, -0.363007418224602,
	  -0.381282060810003,-0.379702088442246, -0.366969987461558, -0.34898142624919 ,-0.329150726017628  },
	{ -0.148674175331968, -0.22961941054795 , -0.310294853506135, -0.35071332407761 , -0.309030287293411,
	  -0.177793336893143, 0.013778169024349,  0.22596669725875 ,  0.425295458404853, 0.588770737920356 }
};
//############################################################

//############################################################
//				FUNKCJE
float iloczyn_skalarny(float * wektor1, float * wektor2, uint8_t dlugosc)
{
	float wynik = 0;
	uint8_t i=0;
	for(i=0;i<dlugosc;++i)
	{
		wynik += wektor1[i] * wektor2[i];
	}
	return wynik;
}

float odleglosc_Mahalanobisa(float punkt [],const float mu[], const float sigma[WYMIAR_PO_PCA][WYMIAR_PO_PCA])
{
	uint8_t i = 0;
	float wynik = 0;
	float x[WYMIAR_PO_PCA];
	for (i=0;i<WYMIAR_PO_PCA;++i)
	{
		x[i]=punkt[i]-mu[i];
	}
	wynik = sigma[0][0]*x[0]*x[0]+sigma[1][0]*x[0]*x[1]+sigma[0][1]*x[0]*x[1]+sigma[1][1]*x[1]*x[1]; // mnozenie macierzy
	wynik = sqrt(wynik);
	return wynik;

}

void PCA (float phi[WYMIAR_PO_PCA][LICZBA_PROBEK_WIDMA],float x[],float wynik [])
{
	uint8_t i=0;
	for (i=0; i<WYMIAR_PO_PCA; i++)
	{
		wynik[i] = iloczyn_skalarny( phi[i],x,LICZBA_PROBEK_WIDMA); // mnozenie Ax, to iloczyn skalarny wierszy macierzy A z wektorem x
	}
}

void roznica_wektorow(float * v1, float * v2, float * wynik , uint8_t dlugosc)
{
	uint8_t i;
	for(i=0; i < dlugosc; i++ )
	{
		wynik[i] = v1[i] - v2[i];
	}
}

float funkcja_g(float * x, float * c1, float * c2)
{
	float a[WYMIAR_PO_PCA];
	float r[WYMIAR_PO_PCA];
	roznica_wektorow(c2,c1,a,WYMIAR_PO_PCA);// a =c2 - c1
	roznica_wektorow(x,c1,r,WYMIAR_PO_PCA); // r = x - c1 -> pomocniczy wektor

	return iloczyn_skalarny(a,r,WYMIAR_PO_PCA) / iloczyn_skalarny(a,a,WYMIAR_PO_PCA);
}

float funkcja_h(float g_od_x)
{
	if (g_od_x <= 0.0)  return 0.0;
	if (g_od_x >= 1.0)  return 1.0;
	return g_od_x;
}

float odleglosc_punktu_od_odcinka(float * x, float * c1, float * c2)
{
	float a[WYMIAR_PO_PCA];
	float w[WYMIAR_PO_PCA];
	float x_minus_w[WYMIAR_PO_PCA];
	float g_od_x;

	roznica_wektorow(c2,c1,a,WYMIAR_PO_PCA); // a = c2 - c1
	g_od_x = funkcja_g(x,c1,c2);


	funkcja_w( c1, a, funkcja_h( g_od_x ), w);
	roznica_wektorow(x, w, x_minus_w, WYMIAR_PO_PCA);

	return sqrt( iloczyn_skalarny(x_minus_w, x_minus_w, WYMIAR_PO_PCA) ); // ||x - w(x)||^2
}

void funkcja_w(float * c1, float * a ,float h_od_x, float * wynik)
{
	uint8_t i;

	for(i = 0; i < WYMIAR_PO_PCA; i++)
	{
		wynik[i] = c1[i] + a[i] * h_od_x; // d = c1 + a*h( g(x) )
	}
}

uint8_t klasyfikacja(float * widmo, uint8_t typ_slownika)
{
	uint8_t i,j; // liczniki
	uint8_t etykieta = 0;
	float bufor[LICZBA_PUNKTOW][WYMIAR_PO_PCA];
	float fi[WYMIAR_PO_PCA][LICZBA_PROBEK_WIDMA]; // fi 2x10
	float d_min = 100000;// przyjmujemy poczatkowa duza wartosc
	float d;
	
	float x[WYMIAR_PO_PCA];
	
	if ( SLOWNIK_SINC == typ_slownika )
	{
		memcpy_P( fi, fi_sinc, WYMIAR_PO_PCA * LICZBA_PROBEK_WIDMA * sizeof(float) );
	}
	else
	{
		memcpy_P( fi, fi_multisin, WYMIAR_PO_PCA * LICZBA_PROBEK_WIDMA * sizeof(float) );
	}
	
	PCA(fi, widmo, x);

	for(i=0; i < LICZBA_USZKODZEN; i++) // sprawdzamy kazdy element ukladu
	{
		if ( SLOWNIK_SINC == typ_slownika )
		{
			memcpy_P( bufor, slownik_uszkodzen_sinc[i], LICZBA_PUNKTOW * WYMIAR_PO_PCA * sizeof(float) );
		}
		else
		{
			// domyslnie slownik multisin
			memcpy_P( bufor, slownik_uszkodzen_multisin[i], LICZBA_PUNKTOW * WYMIAR_PO_PCA * sizeof(float) );
		}
		
		for(j = 0; j < LICZBA_PUNKTOW - 1; j++)// sprawdzamy kazdy punkt w slowniku dla danego elementu
		{
			d = odleglosc_punktu_od_odcinka(x,bufor[j],bufor[j+1]);
			if (d < d_min)
			{
				d_min = d;
				etykieta = i;
			}
		}
	}

	return etykieta; // zwracamy numer etykiety uszkodzenia od 0 do 9 (od C1_PLUS do R2_MINUS)
}

uint8_t stan_nominalny(float * widmo,  uint8_t typ_slownika)
{
	//float s = odleglosc_Mahalanobisa(x, srodek_multisin, sigma_multisin);
	float s;
	float graniczna_odleglosc_Mah;
	float fi[WYMIAR_PO_PCA][LICZBA_PROBEK_WIDMA]; // fi 2x10
	float x[WYMIAR_PO_PCA];
	
	if ( SLOWNIK_SINC == typ_slownika )
	{
		memcpy_P( fi, fi_sinc, WYMIAR_PO_PCA * LICZBA_PROBEK_WIDMA * sizeof(float) );
		PCA(fi, widmo, x);
		s = odleglosc_Mahalanobisa(x, srodek_sinc, sigma_sinc);
		graniczna_odleglosc_Mah = graniczna_odleglosc_Mah_sinc;
	}
	else
	{
		// domyslnie slownik multisin
		memcpy_P( fi, fi_multisin, WYMIAR_PO_PCA * LICZBA_PROBEK_WIDMA * sizeof(float) );
		PCA(fi, widmo, x);
		s = odleglosc_Mahalanobisa(x, srodek_multisin, sigma_multisin);
		graniczna_odleglosc_Mah = graniczna_odleglosc_Mah_multisin;
	}

	if (s > graniczna_odleglosc_Mah)
	{
		return 0; // uklad nie jest w stanie nominalnym -> USZKODZENIE!
	}
	else
	{
		return 1; // uklad sprawny -> STAN NOMINALNY
	}
}

//############################################################