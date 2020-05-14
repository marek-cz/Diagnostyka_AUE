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

const char * const NapisyLCD[LICZBA_USZKODZEN+1] PROGMEM = {C1_P, C1_M, C2_P, C2_M, C3_P, C3_P, R1_P, R1_M, R2_P, R2_M, NOM_STR };
//###################################################


//############################################################
//				PARAMETRY MULTISIN:
const uint16_t PROGMEM czestotliwosci_multisin_k[LICZBA_PROBEK_WIDMA]={1,2,3,4,5,6,7,8,9,10}; // probki widma DTF
const float  srodek_multisin[WYMIAR_PO_PCA] = {-1.111261067020383e-01, -1.589418065713307e-02};
const float  graniczna_odleglosc_Mah_multisin = 6.008596707245276e-03;
const float  sigma_multisin[WYMIAR_PO_PCA][WYMIAR_PO_PCA] = {{1.014770229084543, 0.262326290458436},{0.262326290458436, 5.659039631125032}};
const float PROGMEM slownik_uszkodzen_multisin[LICZBA_USZKODZEN][LICZBA_PUNKTOW][WYMIAR_PO_PCA]=
{
	{	// C1+
		{ -0.115542373547244 , -0.016231351433621 },
		{ -0.123263450901527 , -0.016744204900377 },
		{ -0.130712541048029 , -0.017179831126981 },
		{ -0.137902068310778 , -0.0175466049705 },
		{ -0.144843745240955 , -0.017852000809572 },
		{ -0.151548626505828 , -0.018102695123098 }
	},
	{	// C1-
		{ -0.061604630114922 , -0.010770483231652 },
		{ -0.071308947034753 , -0.012008566774981 },
		{ -0.08064564104573 , -0.013090259674492 },
		{ -0.08963315417716 , -0.014032769278068 },
		{ -0.098288687880328 , -0.014851335364347 },
		{ -0.106628322628418 , -0.01555947679153 }
	},
	{	// C2+
		{ -0.106733676199983 , -0.017182350737773 },
		{ -0.099447440981153 , -0.018945114688455 },
		{ -0.092906108730186 , -0.020147360282667 },
		{ -0.087031652591541 , -0.020909684802718 },
		{ -0.081748212861995 , -0.02133142852334 },
		{ -0.076985874796602 , -0.021492528461007 }
	},
	{	// C2-
		{ -0.166781025028826 , 0.01295842914142 },
		{ -0.156326413084813 , 0.005637075595402 },
		{ -0.145388668282036 , -0.000972567777405 },
		{ -0.134769397960637 , -0.006525898670856 },
		{ -0.124854699339312 , -0.01096962390861 },
		{ -0.115789785075181 , -0.014394353468155 }
	},
	{	// C3+
		{ -0.112170347712536 , -0.018089038935887 },
		{ -0.113629556576494 , -0.021746693743968 },
		{ -0.114669536305212 , -0.025045372502458 },
		{ -0.115391452419743 , -0.027985875456725 },
		{ -0.115871335538556 , -0.030584264635082 },
		{ -0.116166547033056 , -0.032864770162358 }
	},
	{	// C3-
		{ -0.082074227740896 , 0.006245350299648 },
		{ -0.091136839319332 , 0.003238190978479 },
		{ -0.098030563410245 , -0.000639093557611 },
		{ -0.103201870478452 , -0.004946365088152 },
		{ -0.10704883008403 , -0.009352531103327 },
		{ -0.10989169701661 , -0.013635660694442 }
	},
	{	// R1+
		{ -0.11323755985416 , -0.018602301976825 },
		{ -0.116439922124122 , -0.023410885551073 },
		{ -0.119001098453833 , -0.028076953909523 },
		{ -0.121038501525453 , -0.032521823664924 },
		{ -0.122648740416629 , -0.036695512105257 },
		{ -0.123910741542365 , -0.040569866148815 }
	},
	{	//R1-
		{ -0.070269461211774 , 0.004300538728831 },
		{ -0.080897507499794 , 0.002445135930953 },
		{ -0.089953658557485 , -0.000463732353141 },
		{ -0.097503218424182 , -0.004211631420172 },
		{ -0.103706549121002 , -0.008547420009771 },
		{ -0.108755075144576 , -0.013232387177445 }
	},
	{	// R2+
		{ -0.109994878191952 , -0.01707383588299 },
		{ -0.108125900168408 , -0.018735253919983 },
		{ -0.106460386328193 , -0.019961749172824 },
		{ -0.104972994748526 , -0.020863855431186 },
		{ -0.103640507376872 , -0.021522980236736 },
		{ -0.102442502555007 , -0.021999265684742 }
	},
	{	// R2-
		{ -0.124979216457935 , 0.015224925973038 },
		{ -0.122888527819975 , 0.005873657204626 },
		{ -0.120131331479888 , -0.001536688860299 },
		{ -0.117333120879611 , -0.007177267430392 },
		{ -0.114714512381931 , -0.011398022375281 },
		{ -0.112340704057053 , -0.014533608425129 }
	}
};
const float PROGMEM fi_multisin[WYMIAR_PO_PCA][LICZBA_PROBEK_WIDMA] =
{
	{ -0.009499053355113, -0.039383246080145, -0.093429617845276,
		-0.172796793478716, -0.263245549244939, -0.349979574526216,
		-0.413119670746523, -0.442993498908876, -0.449640772354983,
		-0.445981002068762 },
	{ -0.02710909383895 , -0.123517990695134, -0.321589467773579,
		-0.553165977826726, -0.536600972890947, -0.263637107214548,
		0.023404803800454,  0.201685429859103,  0.281877055140419,
		0.310598483764789 }
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