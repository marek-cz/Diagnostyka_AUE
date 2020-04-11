/*
 * ADC.c
 *
 * Created: 2019-11-05 18:45:04
 *  Author: Marek
 */ 

#include "ADC.h"

void ADC_Init(ADC_CH_t * adc_kanal,register8_t adc_mux)
{
	ADCA.REFCTRL = ADC_REFSEL_INT1V_gc;				// napiecie odniesienia 1V
	ADCA.PRESCALER = ADC_PRESCALER_DIV16_gc;			// fADC = fPER/16 = 2 MHz
	//ADCA.PRESCALER = ADC_PRESCALER_DIV8_gc;
	
	ADC_CH_Init(adc_kanal,adc_mux); // PIN4 PORTU A - WEJSCIE ADC - ADC4 NA PLYTCE!!!
	
	PORTA.PIN4CTRL = PORT_ISC_INPUT_DISABLE_gc;			// zablokowanie cyfrowej funkcji pinu
	//ADCA.EVCTRL=ADC_SWEEP_0_gc | ADC_EVSEL_0123_gc | ADC_EVACT_SWEEP_gc; //Wyzwalanie kana�u 0 przez kanal 0 syst. zdarzen -> str.247 TMF
	ADCA.EVCTRL=ADC_SWEEP_0_gc | ADC_EVSEL_0123_gc | ADC_EVACT_CH0_gc;
	
	
	ADCA.CTRLA = ADC_ENABLE_bm;							// ustawienie tego bitu odblokowuje ADC
}


void ADC_CH_Init(ADC_CH_t * adc_kanal,register8_t adc_mux )
{
	adc_kanal ->  CTRL = ADC_CH_START_bm  | ADC_CH_INPUTMODE_SINGLEENDED_gc;	// TRYB SINGLE ENDED
	adc_kanal ->  MUXCTRL = adc_mux;											// wybor pinu wejsciowego
}

uint16_t PomiarADC(void)
{
	uint32_t accum = 0;
	uint16_t counter = 0;
	do
	{
		ADCA.CH0.CTRL |= ADC_CH_START_bm; // rozpocznij konwersje
		while( !( ADCA.CH0.INTFLAGS & ADC_CH_CHIF_bm ) ); // zaczekaj na koniec konwersji
		ADCA.CH0.INTFLAGS = ADC_CH_CHIF_bm; // skasuj flage konca przetwarzania
		accum += ADCA.CH0RES;
		counter++;
	} while(counter < 1024);
	return accum / 1024;
}