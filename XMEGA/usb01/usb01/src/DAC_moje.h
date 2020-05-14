/*
 * DAC_moje.h
 *
 * Created: 2019-11-05 17:23:16
 *  Author: Marek
 */ 


#ifndef DAC_MOJE_H_
#define DAC_MOJE_H_

#include <avr/pgmspace.h>
#define LICZBA_PROBEK_W_TABLICY_MAX 500

extern const uint16_t multi_sin_wave_500[LICZBA_PROBEK_W_TABLICY_MAX];	// probki sygnalu wieloharmonicznego
extern const uint16_t sinc_wave_500[LICZBA_PROBEK_W_TABLICY_MAX];		// probki sygnalu sinc
extern const uint16_t sinus_500[LICZBA_PROBEK_W_TABLICY_MAX];			// probki sygnalu sinusa
extern const uint16_t sinus_250[250];			// probki sygnalu sinusa
extern const uint16_t sinus_100[100];			// probki sygnalu sinusa
//extern const uint16_t pila_1000[LICZBA_PROBEK_W_TABLICY_MAX];			// probki sygnalu pily (rampa)



/*		funkcje		*/
extern void DAC_init(void); // na ATXMEGA256A3BU jest jeden DAC na porcie B -> DACB PB2 - CH0 PB3 - CH1
extern void UstawDACa(uint16_t rejestrDACa);
#endif /* DAC_MOJE_H_ */