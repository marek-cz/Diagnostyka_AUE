/*
 * DAC_moje.h
 *
 * Created: 2019-11-05 17:23:16
 *  Author: Marek
 */ 


#ifndef DAC_MOJE_H_
#define DAC_MOJE_H_

#include <avr/pgmspace.h>
#define OFFSET_TABLICY 0
#define LICZBA_PROBEK_W_TABLICY_MAX 1000
//#define KALIB_CZEST 

extern const uint16_t multi_sin_wave_1000[LICZBA_PROBEK_W_TABLICY_MAX];	// probki sygnalu wieloharmonicznego
extern const uint16_t multi_sin_wave_250[250];	// probki sygnalu wieloharmonicznego
extern const uint16_t multi_sin_wave_100[100];	// probki sygnalu wieloharmonicznego
extern const uint16_t sinc_wave_1000[LICZBA_PROBEK_W_TABLICY_MAX];		// probki sygnalu sinc
extern const uint16_t sinc_wave_250[250];		// probki sygnalu sinc
extern const uint16_t sinc_wave_100[100];		// probki sygnalu sinc
extern const uint16_t sinus_1000[LICZBA_PROBEK_W_TABLICY_MAX];			// probki sygnalu sinusa
extern const uint16_t sinus_250[250];			// probki sygnalu sinusa
extern const uint16_t sinus_100[100];			// probki sygnalu sinusa
extern const uint16_t pila_1000[LICZBA_PROBEK_W_TABLICY_MAX];			// probki sygnalu pily (rampa)

#ifdef KALIB_CZEST
	extern const uint16_t sqr_2[2];
	extern const uint16_t sqr_10[10];
	extern const uint16_t sqr_100[100];
	extern const uint16_t sqr_1000[1000];
#endif


/*		funkcje		*/
extern void DAC_init(void); // na ATXMEGA256A3BU jest jeden DAC na porcie B -> DACB PB2 - CH0 PB3 - CH1

#endif /* DAC_MOJE_H_ */