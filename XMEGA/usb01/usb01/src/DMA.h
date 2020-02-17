/*
 * DMA.h
 *
 * Created: 2019-11-05 17:46:55
 *  Author: Marek
 */ 


#ifndef DMA_H_
#define DMA_H_

extern void DMA_init(void);
extern void DMA_initTransfer_ADC( volatile uint16_t * dst ,uint16_t len);
extern void DMA_initTransfer_DAC( volatile uint16_t * src ,uint16_t len);



#endif /* DMA_H_ */