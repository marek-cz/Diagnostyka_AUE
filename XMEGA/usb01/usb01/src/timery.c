/*
 * timery.c
 *
 * Created: 2019-11-05 18:58:25
 *  Author: Marek
 */ 

#include "timery.h"

void TCC1_Init(uint16_t per)
{
	// konfiguracja przerwania od przepelnienia
	TCC1.INTCTRLA = TC_OVFINTLVL_MED_gc;				// przepe³nienie TCC1 ma generowaæ przerwanie MED -> priorytety przerwan
	TCC1.CTRLB	  = TC_WGMODE_NORMAL_gc;				// tryb normalny
	TCC1.PER	  =	per;								// LICZ MODULO per - przepelnienie co per+1
	TCC1_CTRLA    = TC_CLKSEL_DIV256_gc;				// w³aczenie timera
}

void TCC0_Init(uint16_t per)
{
	// konfiguracja przerwania od przepelnienia
	//TCC0.INTCTRLA = TC_OVFINTLVL_MED_gc;				// przepe³nienie TCC0 ma generowaæ przerwanie LO -> priorytety przerwan
	TCC0.CTRLB	  = TC_WGMODE_NORMAL_gc;				// tryb normalny
	TCC0.PER	  =	per;								// LICZ MODULO per
	EVSYS_CH0MUX  = EVSYS_CHMUX_TCC0_OVF_gc;			// przepelnienie TCC0 -> syst. zdarzen -> wyzwala DAC
}


