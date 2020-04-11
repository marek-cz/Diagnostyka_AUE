/*
 * ADC.h
 *
 * Created: 2019-11-05 18:43:24
 *  Author: Marek
 */ 

/* potrzeba 4 przepelnien timera aby z ADC wyszla pierwsza probka
potem juz co przelenienie jest probka ----> POTOK !!!
UWZGLEDNIC PRZY ZBIERANIU OKRESU DANYCH!!!*/


#ifndef ADC_H_
#define ADC_H_

#include <avr/io.h>

extern void ADC_Init(ADC_CH_t * adc_kanal,register8_t adc_mux);
extern void ADC_CH_Init(ADC_CH_t * adc_kanal,register8_t adc_mux );
extern uint16_t PomiarADC(void);


#endif /* ADC_H_ */