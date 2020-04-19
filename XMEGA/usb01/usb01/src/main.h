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
#include <util/delay.h>
#include <math.h>
#include <stdbool.h>
//----------------------------------------------------
//				BIBLIOTEKI WLASNE
#include "DAC_moje.h"
#include "DMA.h"
#include "ADC.h"
#include "timery.h"
//----------------------------------------------------
//				MAKRA
#define ROZMIAR_RAMKI_USB_MAX		13
#define ROZMIAR_KOMENDY_MAX			20
#define KONIEC_ZBIERANIA_PROBEK (1<<0)
#define ODBIOR_KOMENDY			(1<<1)
#define ODBIOR_ZNAKU			(1<<2)
#define OKRES_TIMERA_MIN			31

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
#define ADC_OFFSET 250.0
//----------------------------------------------------
//				PROTOTYPY FUNKCJI
//----------------------------------------------------
//				FUNKCJA INICJALIZACJI
void Init(void);
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
//----------------------------------------------------
//				FUNKCJE KONWERSJI
void NadajWynik(uint16_t * tablicaProbek, uint16_t liczbaProbek);
void NadajWidmo(char * tablicaFloatToChar, uint8_t liczbaElementow);
uint8_t znakNaCyfre( unsigned char znak);
uint16_t znakiNaLiczbe( unsigned char tablica_znakow[] ,uint8_t start_ind);
//----------------------------------------------------
//				FUNKCJE POZOSTALE
uint8_t ReadCalibrationByte(uint8_t index); // kalibracja ADC
void WlaczPeryferia(void);
float oblicz_DFT(uint16_t k , uint16_t N, const uint16_t sygnal[] );
float obliczTF(const uint16_t sygnal[],uint16_t liczba_elementow,uint8_t f);
void analizaRamkiDanych(uint16_t * okres_timera,uint16_t * liczba_probek,uint8_t * przebieg, unsigned char ramka_danych[]);
uint16_t KalibracjaOffsetuADC(void);
float KalibracjaWzmocnieniaADC(void);
#endif /* MAIN_H_ */