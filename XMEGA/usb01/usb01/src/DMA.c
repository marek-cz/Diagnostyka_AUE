/*
 * DMA.c
 *
 * Created: 2019-11-05 17:46:02
 *  Author: Marek
 */ 

#include <avr/io.h>
#include "DMA.h"

void DMA_init(void)
{
	DMA.CTRL=DMA_ENABLE_bm;  //Odblokuj kontroler DMA, round robin, bez double buffering
	/* KANAL 0 -> DAC */
	DMA.CH0.ADDRCTRL=DMA_CH_SRCRELOAD_BLOCK_gc | DMA_CH_SRCDIR_INC_gc | DMA_CH_DESTDIR_INC_gc | DMA_CH_DESTRELOAD_BURST_gc; //Zwiekszamy adres Ÿród³a i przeznaczenia, reload adresu co blok, adres docelowy co paczkê
	DMA.CH0.TRIGSRC=DMA_CH_TRIGSRC_DACB_CH0_gc; //Zdarzeniem wyzwalaj¹cym jest pusty rejestr danych kana³u CH0 DACB
	//DMA.CH0.REPCNT=0;                           //Transfer bêdzie pwtarzany w nieskoñczonoœæ
	DMA.CH0.DESTADDR0=(uint16_t)(&DACB.CH0DATA) & 0xFF; //Dane wpisujemy do rejestru DATA uk³adu DAC
	DMA.CH0.DESTADDR1=(uint16_t)(&DACB.CH0DATA) >> 8;
	DMA.CH0.DESTADDR2=0;
	
	/* KANAL 1 -> ADC */
	
	DMA.CH1.ADDRCTRL = DMA_CH_SRCRELOAD_BURST_gc  | DMA_CH_SRCDIR_INC_gc | DMA_CH_DESTRELOAD_BLOCK_gc | DMA_CH_DESTDIR_INC_gc;
	DMA.CH1.TRIGSRC = DMA_CH_TRIGSRC_ADCA_CH0_gc;							// Transfer wyzwalany zakonczeniem konwersji ADCA CH0
	DMA.CH1.REPCNT = 1;														// Tyle razy powtorz transfer
	DMA.CH1.SRCADDR0 = ((uint16_t)&ADCA.CH0.RES) & 0xFF ;					// Mlodszy bajt adresu
	DMA.CH1.SRCADDR1 = ((uint16_t)&ADCA.CH0.RES) >> 8 ;						// Starszy bajt adresu
	DMA.CH1.SRCADDR2 = 0;													// 0 - wpisujemy bo musimy :)
	
}


void DMA_initTransfer_ADC( volatile uint16_t * dst ,uint16_t len)
{
	DMA.CH1.DESTADDR0 = ((uint16_t)dst) & 0xFF;
	DMA.CH1.DESTADDR1 = ((uint16_t)dst) >> 8;
	DMA.CH1.DESTADDR2 = 0;
	
	DMA.CH1.TRFCNT =  len;									// liczba bajtow w bloku
	//DMA.CH1.CTRLA = DMA_CH_ENABLE_bm | DMA_CH_SINGLE_bm |DMA_CH_REPEAT_bm | DMA_CH_BURSTLEN_2BYTE_gc;// Powtarzamy pomiary (REPCNT okresla ile razy) 2 bajty na burst
	//DMA.CH1.CTRLA = DMA_CH_SINGLE_bm |DMA_CH_REPEAT_bm | DMA_CH_BURSTLEN_2BYTE_gc;// Powtarzamy pomiary (REPCNT okresla ile razy) 2 bajty na burst
	DMA.CH1.CTRLA = DMA_CH_SINGLE_bm  | DMA_CH_BURSTLEN_2BYTE_gc;//  2 bajty na burst
}

void DMA_initTransfer_DAC( volatile uint16_t * src ,uint16_t len)
{	
	DMA.CH0.SRCADDR0 = ((uint16_t)src) & 0xFF;
	DMA.CH0.SRCADDR1 = ((uint16_t)src) >> 8;
	DMA.CH0.SRCADDR2=0;
	
	DMA.CH0.REPCNT=0;     //Transfer bêdzie pwtarzany w nieskoñczonoœæ	
	DMA.CH0.TRFCNT = len; // blok ma dlugosc tablicy probek 
	//DMA.CH0.CTRLA=DMA_CH_ENABLE_bm | DMA_CH_REPEAT_bm | DMA_CH_BURSTLEN_2BYTE_gc | DMA_CH_SINGLE_bm;  //Kana³ 0 w trybie powtarzania, d³ugoœæ transferu 2 bajty, single shot
	DMA.CH0.CTRLA= DMA_CH_REPEAT_bm | DMA_CH_BURSTLEN_2BYTE_gc | DMA_CH_SINGLE_bm;  //Kana³ 0 w trybie powtarzania, d³ugoœæ transferu 2 bajty, single shot
}

void DMA_initTransfer_DAC_imp( volatile uint16_t * src ,uint16_t len) // do pomiaru impulsowego
{
	DMA.CH0.SRCADDR0 = ((uint16_t)src) & 0xFF;
	DMA.CH0.SRCADDR1 = ((uint16_t)src) >> 8;
	DMA.CH0.SRCADDR2=0;
	
	DMA.CH0.REPCNT=1;     // tylko 1 (JEDEN!!!) TRANSFER
	DMA.CH0.TRFCNT = len; // blok ma dlugosc tablicy probek
	//DMA.CH0.CTRLA=DMA_CH_ENABLE_bm | DMA_CH_REPEAT_bm | DMA_CH_BURSTLEN_2BYTE_gc | DMA_CH_SINGLE_bm;  //Kana³ 0 w trybie powtarzania, d³ugoœæ transferu 2 bajty, single shot
	DMA.CH0.CTRLA= DMA_CH_REPEAT_bm | DMA_CH_BURSTLEN_2BYTE_gc | DMA_CH_SINGLE_bm;  //Kana³ 0 w trybie powtarzania, d³ugoœæ transferu 2 bajty, single shot
}