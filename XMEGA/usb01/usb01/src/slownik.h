/*
 * slownik.h
 *
 * Created: 2020-05-12 12:44:44
 *  Author: Marek
 */ 


#ifndef SLOWNIK_H_
#define SLOWNIK_H_

//	BIBLIOTEKI
#include <avr/pgmspace.h>

//############################
//			MAKRA
//###########################

#define SLOWNIK_SINC		0
#define SLOWNIK_MULTISIN	1

//	MAKRA OPISUJACE WYMIARY
#define WYMIAR_PO_PCA 2
#define LICZBA_PROBEK_WIDMA 10
#define LICZBA_PUNKTOW      6

#define LICZBA_USZKODZEN    10
#define LICZBA_ZNAKOW_SYGNATURY 4
//	MAKRA OPISUJACE KOLEJNOSC USZKODZEN W SLOWNIKU:
#define C1_PLUS     0
#define C1_MINUS    1
#define C2_PLUS     2
#define C2_MINUS    3
#define C3_PLUS     4
#define C3_MINUS    5
#define R1_PLUS     6
#define R1_MINUS    7
#define R2_PLUS     8
#define R2_MINUS    9

#define NOMINALNY	10
//############################
//			DEKLARACJE
//###########################

extern const char * const NapisyLCD[LICZBA_USZKODZEN + 1];
//--------------------------------------------------------------------------------------------------
/*extern const float srodek_multisin[WYMIAR_PO_PCA];
extern const float graniczna_odleglosc_Mah_multisin;
extern const float sigma_multisin[WYMIAR_PO_PCA][WYMIAR_PO_PCA];
extern const float slownik_uszkodzen_multisin[LICZBA_USZKODZEN][LICZBA_PUNKTOW][WYMIAR_PO_PCA];
//--------------------------------------------------------------------------------------------------
extern const float srodek_sinc[WYMIAR_PO_PCA];
extern const float graniczna_odleglosc_Mah_sinc;
extern const float sigma_sinc[WYMIAR_PO_PCA][WYMIAR_PO_PCA];
extern const float  slownik_uszkodzen_sinc[LICZBA_USZKODZEN][LICZBA_PUNKTOW][WYMIAR_PO_PCA];*/
//--------------------------------------------------------------------------------------------------
//############################
//			FUNKCJE
//###########################
float iloczyn_skalarny(float * wektor1, float * wektor2, uint8_t dlugosc);
float odleglosc_Mahalanobisa(float x [],const float mu[], const float sigma[WYMIAR_PO_PCA][WYMIAR_PO_PCA]);
void PCA (float phi[WYMIAR_PO_PCA][LICZBA_PROBEK_WIDMA],float x[],float wynik []);
void roznica_wektorow(float * v1, float * v2, float * wynik , uint8_t dlugosc);
float funkcja_g(float * x, float * c1, float * c2);
float funkcja_h(float g_od_x);
void funkcja_w(float * c1, float * a ,float h_od_x, float * wynik);
float odleglosc_punktu_od_odcinka(float * x, float * c1, float * c2);
extern uint8_t klasyfikacja(float * widmo, uint8_t typ_slownika);
extern uint8_t stan_nominalny(float * widmo,  uint8_t typ_slownika);
#endif /* SLOWNIK_H_ */