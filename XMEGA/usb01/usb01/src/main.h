/*
 * main.h
 *
 * Created: 2020-01-18 11:49:27
 *  Author: Marek
 */ 


#ifndef MAIN_H_
#define MAIN_H_
// czestotliwosc traktowania procesora - potem zmieniana!!!
//#define F_CPU				2000000UL
//----------------------------------------------------
//----------------------------------------------------
//				BIBLIOTEKI STANDARDOWE
#include <avr/io.h>
//#include <stddef.h>
#include <avr/interrupt.h>
//#include <util/delay.h>
#include <math.h>
#include <stdbool.h>
//----------------------------------------------------
//				BIBLIOTEKI WLASNE
#include "DAC_moje.h"
#include "DMA.h"
#include "ADC.h"
#include "timery.h"
#include "slownik.h"
//----------------------------------------------------
//----------------------------------------------------
//				BIBLIOTEKI INNE
#include "LCD.h"
//----------------------------------------------------
//				MAKRA
#define ROZMIAR_RAMKI_USB_MAX		13
#define KONIEC_ZBIERANIA_PROBEK (1<<0)
//#define ODBIOR_KOMENDY			(1<<1)
#define ODBIOR_ZNAKU			(1<<2)
#define WYSLIJ_POMIAR			(1<<5)
#define OKRES_TIMERA_MIN			31

#define MULTISIN_DIAG_PER	3199
#define SINC_DIAG_PER		1279
#define DELAY_BEZ_ZMIANY_PRZEBIEGU_ms	100
#define DELAY_ZE_ZMIANA_PRZEBIEGU_ms	500

//				MAKRA PRZYCISKOW
#define BUTTON_PORT		PORTC 
#define BUTTON_1_PIN	0
#define BUTTON_2_PIN	1
//#define BUTTON_1_ISR_VEC PORTF_INT0_vect
//#define BUTTON_2_ISR_VEC PORTF_INT1_vect
//#define WCISNIECIE_BUTT_1		(1<<3)
//#define WCISNIECIE_BUTT_2		(1<<4)

#define  DEBOUNCING_DELAY_ms	50
//			MAKRA LEDow:
#define LED_PORT		PORTC
#define LED_NOM_PIN		4
#define LED_FAULT_PIN	5

//			MAKRA OPISUJACE NUMERY PRZEBIEGOW
#define SINUS_500_NR			0
#define SINUS_250_NR			1
#define SINUS_100_NR			2
#define MULTI_SIN_500_NR		4
#define SINC_500_NR				7

//			MAKRA OPISUJACE POLECENIA W RAMCE
#define POLECENIE_POZYCJA			0
#define MAX_LICZBA_CYFR				5
//----------------------------------
#define GEN_PRZEBIEG_Bp				2
#define GEN_PER_START_Bp			4
#define GEN_LICZB_PROBEK_Bp			10
//-----------------------------------
#define POM_TYP_Bp					2
#define POM_DELAY_Bp				4
#define POMIAR_IMPULSOWY			(1<<1)
#define POMIAR_OKRESOWY				(1<<0)
//-------------------------------------
#define DFT							'F'
#define TRANSFORMATA_FOURIERA		'T'
#define WIDMO_CZESTOTLIWOSC_Bp		2
//-------------------------------------
#define INFORMACJE_O_PRZEBIEGU		'I'
//-------------------------------------
#define REZULTAT_DIAGNOSTYKI		'D'
#define REZULTAT_START_Bp			2
#define REZULTAT_END_Bp				5
//-------------------------------------
#define ZNAK_TERMINACJI				'$'
//_____________________________________________________
#define LICZBA_PROBEK_500	0
#define LICZBA_PROBEK_250	1
#define LICZBA_PROBEK_100	2
//_____________________________________________________
//	pozycje bitowe peryferiow w PR.PRGEN itp - do WLACZENIA
#define PRGEN_EVSYS (1<<1)
#define PRGEN_DMA (1<<0)
#define PRGEN_USB (1<<6)
#define PRPA_ADC (1<<1)
#define PRPB_DAC (1<<2)
#define PRPC_TC0 (1<<0)
#define PRPC_TC1 (1<<1)

//	makra do obliczen
#define ADC_MAX_F 4096.0
//#define ADC_VREF 1.0
#define ADC_OFFSET 200.0 
//----------------------------------------------------
//				PROTOTYPY FUNKCJI
//----------------------------------------------------
//				FUNKCJA INICJALIZACJI
void Init(void);
void ButtonInit(PORT_t *port);
void LEDInit(PORT_t *port);
//----------------------------------------------------
//				FUNKCJE TAKTOWANIA
bool OSC_wait_for_rdy(uint8_t clk);
void SelectPLL(OSC_PLLSRC_t src, uint8_t mult);
//----------------------------------------------------
//				FUNKCJE POMIAROWE
void Generacja(uint16_t okres_timerow,uint8_t przebieg, uint16_t liczba_probek);		// sama generacja
void PomiarOkresowyADC(uint16_t liczba_probek, volatile uint16_t opoznienie);					// sam pomiar
void WyborPrzebiegu(uint8_t przebieg, uint16_t liczba_probek);
void PomiarImpulsowy(uint16_t liczba_probek, volatile uint16_t opoznienie);						// wykorzystanie SINC
void delayTCC1(uint16_t ms);
//void debouncing(volatile uint8_t *rejestr_portu, uint8_t pin, uint8_t opoznienie_ms );
//----------------------------------------------------
//				FUNKCJE KONWERSJI
void NadajWynik(uint16_t * tablicaProbek, uint16_t liczbaProbek);
void NadajWidmo(char * tablicaFloatToChar, uint8_t liczbaElementow);
void NadajInfo(uint16_t  okres_timera, uint16_t  liczba_probek,uint8_t  przebieg);
uint8_t znakNaCyfre( unsigned char znak);
uint16_t znakiNaLiczbe( unsigned char tablica_znakow[] ,uint8_t start_ind);
//----------------------------------------------------
//				FUNKCJE POZOSTALE
uint8_t ReadCalibrationByte(uint8_t index); // kalibracja ADC
void WlaczPeryferia(void);
float oblicz_DFT(uint16_t k , uint16_t N, const uint16_t sygnal[] );
float obliczTF(const uint16_t sygnal[],uint16_t liczba_elementow,uint16_t f, uint16_t okres_timera);
void wyznaczWimo(float wynik[], uint16_t liczba_elementow, uint16_t okres_timera , uint8_t typ_slownika) ;
void analizaRamkiDanych(uint16_t * okres_timera,uint16_t * liczba_probek,uint8_t * przebieg, unsigned char ramka_danych[]);
uint16_t KalibracjaOffsetuADC(void);
float KalibracjaWzmocnieniaADC(void);

//----------------------------------------------------
//				FUNKCJE DIAGNOSTYCZNE
uint8_t Diagnostyka(float * widmo, uint8_t typ_slownika);
void wypiszWynikDiagnozyLCD(uint8_t etykieta_uszkodzenia);
uint8_t SprawdzParametryPrzebiegu(uint16_t okres_timerow,uint8_t przebieg, uint16_t liczba_probek, uint8_t przebieg_docelowy);
void Testuj(uint16_t *okres_timerow,uint8_t *przebieg, uint16_t * liczba_probek, uint8_t przebieg_docelowy, uint8_t typ_slownika);

#endif /* MAIN_H_ */