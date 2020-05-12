/*
 * LCD.h
 *
 * Created: 2012-01-30 20:52:59
 *  Author: tmf
 */ 


#ifndef LCD_H_
#define LCD_H_

#include <avr\pgmspace.h>

void lcd_init(void);
void lcd_putchar(char c);
void lcd_puttext(char *txt);
void lcd_puttext_P(const char *txt);
//void lcd_defchar_P(uint8_t charno, const uint8_t *chardef);
void lcd_goto(uint8_t x, uint8_t y);
void lcd_cls(void);

#endif /* LCD_H_ */