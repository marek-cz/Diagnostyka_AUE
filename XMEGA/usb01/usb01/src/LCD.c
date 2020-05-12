/*
 * LCD.c
 *
 * Created: 2012-01-30 20:55:42
 *  Author: tmf
 */ 

#include <avr\pgmspace.h>
#include "LCD.h"
#include "defines.h"
#include "hd44780.h"

void lcd_init()
{

  hd44780_init();				//Podstawowa inicjalizacja modu³u
  hd44780_outcmd(HD44780_CLR);	//Wyczyœæ pamiêæ DDRAM
  hd44780_wait_ready(1000);
  hd44780_outcmd(HD44780_ENTMODE(1, 0));	//Tryb autoinkrementacji AC
  hd44780_wait_ready(1000);
  hd44780_outcmd(HD44780_DISPCTL(1, 0, 0));	//W³¹cz wyœwietlacz, wy³¹cz kursor
  hd44780_wait_ready(1000);
} 

void lcd_putchar(char c)
{
  /*static bool second_nl_seen;
  static uint8_t line=0;
 
  if ((second_nl_seen) && (c != '\n')&&(line==0))
  {//Odebrano pierwszy znak
      hd44780_wait_ready(40);
      hd44780_outcmd(HD44780_CLR);
      hd44780_wait_ready(1600);
      second_nl_seen=false;   
  }
  if (c == '\n')
  {
        if (line==0)
   {
           line++;
           hd44780_outcmd(HD44780_DDADDR(64));	//Adres pierwszego znaku drugiej linii
           hd44780_wait_ready(1000);   
   }
   else
   {
        second_nl_seen=true;
        line=0;
   }
  }
  else
  {     
     hd44780_outdata(c);
     hd44780_wait_ready(40);
  }*/
  hd44780_outdata(c);
  hd44780_wait_ready(40);
} 

void lcd_puttext(char *txt)
{
	char ch;
	while((ch=*txt))
	{
		lcd_putchar(ch);
		txt++;
	}
}

void lcd_puttext_P(const char *txt)
{
	char ch;
	while((ch=pgm_read_byte(txt)))
	{
		lcd_putchar(ch);
		txt++;
	}
}

/*void lcd_defchar_P(uint8_t charno, const uint8_t *chardef)
{
 hd44780_outcmd(HD44780_CGADDR(charno*8));
 hd44780_wait_ready(40);
 for(uint8_t c=0;c<8;c++)
  {
   hd44780_outdata(pgm_read_byte(chardef));
   hd44780_wait_ready(40);
   chardef++;
  }
}*/

void lcd_goto(uint8_t x, uint8_t y)
{
	hd44780_outcmd(HD44780_DDADDR(0x40*y+x));
	hd44780_wait_ready(1000);
}

void lcd_cls()
{
	hd44780_outcmd(HD44780_CLR);
	hd44780_wait_ready(1);
}
