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
const float  srodek_sinc[WYMIAR_PO_PCA] = {-1.338141850859052e-03,  2.718548841971919e-04};
const float  graniczna_odleglosc_Mah_sinc = 6.544698070980852e-05;
const float  sigma_sinc[WYMIAR_PO_PCA][WYMIAR_PO_PCA] = {{1.122583291141093, 0.772221464807637},{0.772221464807637, 5.86465965433482}};
const float PROGMEM slownik_uszkodzen_sinc[LICZBA_USZKODZEN][LICZBA_PUNKTOW][WYMIAR_PO_PCA]=
{
	{	// C1+
		{ -0.001386824430371 , 0.000282038387743 },
		{ -0.001470128045908 , 0.00029915521732 },
		{ -0.00154994472667 , 0.000316223142369 },
		{ -0.001625548955995 , 0.000331748608652 },
		{ -0.001698448823705 , 0.000346761684352 },
		{ -0.00176783521326 , 0.0003608465937 }
	},
	{	// C1-
		{ -0.000771286977688 , 0.000153699009491 },
		{ -0.000886251175218 , 0.000177388111236 },
		{ -0.000994943847576 , 0.000200148812461 },
		{ -0.001097951035941 , 0.000221360653834 },
		{ -0.001196172630029 , 0.000241891838737 },
		{ -0.001288893059227 , 0.00026144246324 }
	},
	{	// C2+
		{ -0.001311923107147 , 0.000246709533685 },
		{ -0.001263352295499 , 0.00020676030297 },
		{ -0.001213955869265 , 0.000172340815707 },
		{ -0.00116616717709 , 0.000143097713057 },
		{ -0.001119113068831 , 0.000118701971983 },
		{ -1.073374840211402e-03 , 9.834296201496477e-05 }
	},
	{	// C2-
		{ -0.001484336319505 , 0.000532875935571 },
		{ -0.001489016875443 , 0.000501791955435 },
		{ -0.001474654377642 , 0.000456208357871 },
		{ -0.001445624886502 , 0.000403561435552 },
		{ -0.001408402855655 , 0.000349894924019 },
		{ -0.001363734042103 , 0.000298499702866 }
	},
	{	// C3+
		{ -0.001377519274998 , 0.000259045000697 },
		{ -0.001440221616057 , 0.000235706740715 },
		{ -0.001493165729663 , 0.00021197920648 },
		{ -0.001539340677302 , 0.00018888898099 },
		{ -0.001577949420259 , 0.000167369786831 },
		{ -0.001610192869915 , 0.000147528307567 }
	},
	{	// C3-
		{ -0.000742271269963 , 0.000266454220374 },
		{ -0.000878519946099 , 0.000296057247764 },
		{ -0.001002764973098 , 0.000310221686841 },
		{ -0.001113425360718 , 0.000310759236257 },
		{ -0.001211415982316 , 0.000300585762734 },
		{ -0.001295626684676 , 0.00028366313516 }
	},
	{	// R1+
		{ -0.001395455103555 , 0.000261929302661 },
		{ -0.001491871858332 , 0.000240456934392 },
		{ -0.001579723430889 , 0.000215274144391 },
		{ -0.001658492073626 , 0.000188491245607 },
		{ -0.001728740626158 , 0.000161612114643 },
		{ -0.00179192896955 , 0.000134655093568 }
	},
	{	// R1-
		{ -0.000644274708509 , 0.000210698234405 },
		{ -0.000778837050416 , 0.000244741814458 },
		{ -0.000912707701206 , 0.000270350472301 },
		{ -0.001041851115095 , 0.000283874685998 },
		{ -0.00116354922223 , 0.000286775588777 },
		{ -0.001278353479638 , 0.000279222899611 }
	},
	{	// R2+
		{ -0.001341825638397 , 0.000253936117054 },
		{ -0.001345365183162 , 0.000226021634723 },
		{ -0.001344572756683 , 0.000203283098633 },
		{ -0.001341864299985 , 0.000184087619567 },
		{ -0.001336201657787 , 0.000168525773208 },
		{ -0.001329998595198 , 0.000155188756849 }
	},
	{	// R2-
		{ -0.001075205815651 , 0.000492611702071 },
		{ -0.001181833296272 , 0.000470095299121 },
		{ -0.001248747532886 , 0.000426487730482 },
		{ -0.001289482076994 , 0.000378128529599 },
		{ -0.001316274355218 , 0.000332058585492 },
		{ -0.001332020213474 , 0.000291617504807 }
	}
};

const float PROGMEM fi_sinc[WYMIAR_PO_PCA][LICZBA_PROBEK_WIDMA] = 
{
	{ -0.121470462642178, -0.182926799307063, -0.252514630095132, -0.317611618772976, -0.36292375544413,
	  -0.3822667947656,   -0.381053038894578, -0.367818259110365, -0.348710340784306, -0.327429057060277 },
	{ -0.146158299669227, -0.225196711198337, -0.304317278162165, -0.345797875043612, -0.30873577687872,
	  -0.18284770796754,   0.006265223363837,  0.220378929974398,  0.425634661746184,  0.597676301367563 }
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