/*
 * timery.h
 *
 * Created: 2019-11-05 18:55:48
 *  Author: Marek
 */ 


#ifndef TIMERY_H_
#define TIMERY_H_

#include <avr/io.h>
#define PER_1_ms 124

extern void TCC1_Init(uint16_t per);
extern void TCC0_Init(uint16_t per);

#endif /* TIMERY_H_ */