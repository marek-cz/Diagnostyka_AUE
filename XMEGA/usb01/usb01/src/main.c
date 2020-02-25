/**
 * \file
 *
 * \brief Empty user application template
 *
 */

/**
 * \mainpage User Application template doxygen documentation
 *
 * \par Empty user application template
 *
 * Bare minimum empty user application template
 *
 * \par Content
 *
 * -# Include the ASF header files (through asf.h)
 * -# "Insert system clock initialization code here" comment
 * -# Minimal main function that starts with a call to board_init()
 * -# "Insert application code here" comment
 *
 */

/*
 * Include header files for all drivers that have been imported from
 * Atmel Software Framework (ASF).
 */
/*
 * Support and FAQ: visit <a href="https://www.microchip.com/support/">Microchip Support</a>
 */
//-----------------------------------------------------------------------------------------------

#include <asf.h>
#include "main.h"
//-----------------------------------------------------------------------------------------------
//				ZMIENNE GLOBALNE
uint16_t probki_sygnalu[LICZBA_PROBEK_W_TABLICY_MAX];
uint16_t probki_pomiaru[LICZBA_PROBEK_W_TABLICY_MAX];
volatile uint8_t flagi = 0;
//-----------------------------------------------------------------------------------------------
//				DEKLARACJE FUNKCJI

//-----------------------------------------------------------------------------------------------
//				FUNKCJE OBSLUGI PRZERWAN

/*ISR(DMA_CH0_vect)
{
	
	if(DACB_CH0DATA == probki_sygnalu[0] ) // kiedy jestesmy na poczatku okresu
	{
		DMA_CH0_CTRLB &= ~DMA_CH_TRNINTLVL_MED_gc; // wylaczenie przerwania
		DMA_CH1_CTRLA |= DMA_CH_ENABLE_bm; // wlaczenie transferu DMA probek zmierzonych przez ADC
		DMA_CH1_CTRLB |= DMA_CH_TRNINTLVL_MED_gc; // przerwanie po koncu transmisji bloku
		// wyczyszczenie flagi przerwania
		DMA_CH0_CTRLB |= DMA_CH_TRNIF_bm;
	}
}*/

ISR(DMA_CH1_vect) // przerwanie po transmisji bloku
{

	DMA_CH1_CTRLB &= ~(DMA_CH_TRNINTLVL_MED_gc); // wylaczenie przerwania
	// wyczyszczenie flagi przerwania
	DMA_CH1_CTRLB |= DMA_CH_TRNIF_bm;
	flagi |= KONIEC_ZBIERANIA_PROBEK;
}

//-------------------------------------------------------------------------------------------------------------------------------------------------------------
//				main(void)

int main (void)
{
	//----------------------------------------------------
	//				FUNKCJE INICJALIZUJACE - ASF
	 sysclk_init();                          //konfiguracja zegara -> F_CPU = 24 MHz
	 PMIC.CTRL = PMIC_LOLVLEN_bm | PMIC_MEDLVLEN_bm | PMIC_HILVLEN_bm;
	 sei(); 
	 stdio_usb_init();                       //start USB
	 stdio_usb_enable();
	 //udc_start();
	 //----------------------------------------------------
	 //				ZMIENNE LOKALNE
	 uint16_t okres_timera = 31;
	 uint16_t liczba_probek = 1000;
	 uint8_t  przebieg = SINUS_1000_NR;
	 unsigned char ramka_danych_USB[ROZMIAR_RAMKI_USB_MAX];
	 uint8_t licznik_znakow = 0;
	 uint8_t licznik_terminacji = 0;
	 //----------------------------------------------------
	 //				FUNKCJE WYKONYWANE JEDNORAZOWO
	 WlaczPeryferia();
	 //_delay_ms(3000);
	 Init();
	 //Generacja(okres_timera,przebieg,LICZBA_PROBEK_W_TABLICY_MAX);
	 	
	 //----------------------------------------------------
	 //				PETLA GLOWNA 
	 while(1)
	 {
		  unsigned long int y_int = 0;
		  char ch;
		  if (udi_cdc_is_rx_ready()) 
		  {
			  ch = udi_cdc_getc();
			  ramka_danych_USB[licznik_znakow] = ch;
			  licznik_znakow++;
			  if (ZNAK_TERMINACJI == ch)
			  {
				  licznik_terminacji++;
				  if ( LICZBA_ZNAKOW_TERMINACJI ==licznik_terminacji) // odebrano cale polecenie
				  {
					  for(uint8_t i = 0; i < licznik_znakow;i++)
					  {
						  udi_cdc_putc(ramka_danych_USB[i]);
					  }
					  licznik_terminacji = 0;
					  licznik_znakow = 0;
					  analizaRamkiDanych(&okres_timera,&liczba_probek,&przebieg,ramka_danych_USB);
				  }
			  }
			  else
			  {
				  licznik_terminacji = 0;
			  }
			 /* switch(ch) 
			  {
				  case 's'       :
				  udi_cdc_write_buf("SINUS\n\r", 7);
				  przebieg = SINUS_1000_NR;
				  liczba_probek = 1000;
				  Generacja(okres_timera,przebieg,liczba_probek);
				  break;
				  case 'm'       :
				  udi_cdc_write_buf("MULTISIN\n\r", 10);
				  przebieg = MULTI_SIN_1000_NR;
				  liczba_probek = 1000;
				  Generacja(okres_timera,przebieg,liczba_probek);
				  break;
				  case 'p'       :
				  udi_cdc_write_buf("POMIAR!\n\r", 9);
				  PomiarOkresowyADC(LICZBA_PROBEK_W_TABLICY_MAX,10);
				  _delay_ms(500);
				  NadajWynik(probki_pomiaru,LICZBA_PROBEK_W_TABLICY_MAX);
				  break;
				  case 'f'       :
				  printf("\n\r WIDMO \n\r");
				  //oblicz_DFT(1,1000,probki_sygnalu);
				  y_int = (unsigned long int)(WIDMO_FLOAT_TO_UINT * oblicz_DFT(1,1000,probki_pomiaru));
				  printf("\n\r po widmie :) %lu \n\r", y_int);
				  break;
				  #ifdef KALIB_CZEST
					case '1'       :
					przebieg = SQR_2_NR;
					liczba_probek = 2;
					Generacja(okres_timera,przebieg,liczba_probek);
					break;
					case '2'       :
					przebieg = SQR_10_NR;
					liczba_probek = 10;
					Generacja(okres_timera,przebieg,liczba_probek);
					break;
					case '3'       :
					przebieg = SQR_100_NR;
					liczba_probek = 100;
					Generacja(okres_timera,przebieg,liczba_probek);
					break;
					case '4'       :
					przebieg = SQR_1000_NR;
					liczba_probek = 1000;
					Generacja(okres_timera,przebieg,liczba_probek);
					break;
				  #endif
				  default        :
				  udi_cdc_write_buf("O co chodzi?\n\r", 14);
				  break;
			  }
			  */
		  }
		  
		  if (flagi & KONIEC_ZBIERANIA_PROBEK)
		  {
			  flagi &= ~(KONIEC_ZBIERANIA_PROBEK);
			  NadajWynik(probki_pomiaru,liczba_probek);
		  }
		  
	 }
}
//-------------------------------------------------------------------------------------------------------------------------------------------------------------
//				DEFINICJE FUNKCJI
//-------------------------------------------------------------------------------------------------------------------------------------------------------------
//				FUNKCJA INICJALIZACJI
void Init(void)
{
	OSC_wait_for_rdy(OSC_RC2MRDY_bm);
	SelectPLL(OSC_PLLSRC_RC2M_gc, 16);	// 32 MHz na wyjsciu PLL
	CPU_CCP = CCP_IOREG_gc;				// odblokowanie zmiany konfiguracji zegara
	CLK_CTRL = CLK_SCLKSEL_PLL_gc;		// taktowanie procesora 32 MHz
	#undef  F_CPU
	#define F_CPU 32000000UL
	ADCA.CALL=ReadCalibrationByte(offsetof(NVM_PROD_SIGNATURES_t, ADCACAL0));
	ADCA.CALH=ReadCalibrationByte(offsetof(NVM_PROD_SIGNATURES_t, ADCACAL1));
	sei();	// globalne odblokowanie przerwan
	DMA_init();
	DAC_init();
	ADC_Init(&ADCA.CH0,ADC_CH_MUXPOS_PIN4_gc);
	TCC0_Init(31); // Timer taktujacy DAC i ADC
	TCC0_CTRLA        =    TC_CLKSEL_DIV1_gc;         // bez prescalera
}
//-------------------------------------------------------------------------------------------------------------------------------------------------------------
//				FUNKCJE POMIAROWE

void Generacja(uint16_t okres_timerow,uint8_t przebieg, uint16_t liczba_probek)
{
	/*		WYLACZENIE POPRZEDNIEJ GENERACJI		*/
	// wylaczenie timera
	TCC0_CTRLA = TC_CLKSEL_OFF_gc;
	// WYLACZENIE transmisji DMA DAC'a
	DMA_CH0_CTRLA &= ~(DMA_CH_ENABLE_bm);
	
	/*		WLACZENIE NOWEJ GENERACJI		*/
	
	// wybor przebiegu generowanego przez DAC
	WyborPrzebiegu(przebieg,liczba_probek);
	// ustawienie do ilu ma zliczac licznik
	TCC0_Init(okres_timerow);
	//TCD1_Init(okres_timerow);
	
	// inicjalizacja DMA
	DMA_initTransfer_DAC( probki_sygnalu , liczba_probek * sizeof( uint16_t ) );
	//		START TIMERA - dopoki TCC0 nie jest wlaczony DAC i ADC nie pracuje
	//TCC0_CTRLA        =    TC_CLKSEL_DIV8_gc;       // ustawienie preskalera i uruchomienie timera ->24/8 = 3 MHz -> DAC i ADC
	TCC0_CTRLA        =    TC_CLKSEL_DIV1_gc;         // bez prescalera
	// wlaczenie transmisji DMA DAC'a
	DMA_CH0_CTRLA |= DMA_CH_ENABLE_bm; //DAC
	_delay_ms(100);
}

void PomiarOkresowyADC(uint16_t liczba_probek, uint16_t opoznienie)
{
	// wylaczenie transferu DMA z ADC
	DMA_CH1_CTRLA &= ~(DMA_CH_ENABLE_bm);
	// wyczyszczenie potoku ADC
	ADCA_CTRLA |= ADC_FLUSH_bm;
	// zerowanie tablicy przed pomiarem
	uint16_t i; // iterator do dwoch petli!!!
	for(i = 0;i<liczba_probek;i++)
	{
		probki_pomiaru[i] = 0;
	}
	//------------------------------------------------------------------------------
	
	// inicjalizacja DMA
	DMA_initTransfer_ADC( probki_pomiaru , liczba_probek * sizeof( uint16_t ) );
	
	// odczekaj do stanu ustalonego
	for(i = 0; i< opoznienie;i++)
	{
		_delay_ms(10); // czekaj 10 ms
	}
	
	//DMA_CH0_CTRLB |= DMA_CH_TRNINTLVL_MED_gc; // przerwanie po koncu transmisji bloku -> czekamy aby zaczac pomiar od POCZATKU OKRESU!
	//		-- NIE SYNCHRONIZUJEMY FAZ SYGNALOW IN I OUT!!! --
	DMA_CH1_CTRLA |= DMA_CH_ENABLE_bm; // wlaczenie transferu DMA probek zmierzonych przez ADC
	DMA_CH1_CTRLB |= DMA_CH_TRNINTLVL_MED_gc; // przerwanie DMA po koncu transmisji bloku
}

void WyborPrzebiegu(uint8_t przebieg, uint16_t liczba_probek)
{
	// funkcja wczytujaca wybrany przebieg z pamieci FLASH do TABLICY GLOBALNEJ probki_sygnalu
	switch(przebieg)
	{
		case SINUS_1000_NR :	memcpy_P(probki_sygnalu,sinus_1000,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
		case SINUS_250_NR :	memcpy_P(probki_sygnalu,sinus_250,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
		case SINUS_100_NR :	memcpy_P(probki_sygnalu,sinus_100,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
		case PILA_1000_NR :		memcpy_P(probki_sygnalu,pila_1000,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
		case MULTI_SIN_1000_NR : memcpy_P(probki_sygnalu,multi_sin_wave_1000,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
		case MULTI_SIN_250_NR : memcpy_P(probki_sygnalu,multi_sin_wave_250,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
		case MULTI_SIN_100_NR : memcpy_P(probki_sygnalu,multi_sin_wave_100,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
		case SINC_1000_NR :		memcpy_P(probki_sygnalu,sinc_wave_1000,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
		#ifdef KALIB_CZEST
			case SQR_2_NR :			memcpy_P(probki_sygnalu,sqr_2,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
			break;
			case SQR_10_NR :		memcpy_P(probki_sygnalu,sqr_10,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
			break;
			case SQR_100_NR :		memcpy_P(probki_sygnalu,sqr_100,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
			break;
			case SQR_1000_NR :		memcpy_P(probki_sygnalu,sqr_1000,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
			break;
		#endif
		default :				memcpy_P(probki_sygnalu,multi_sin_wave_1000,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
	}
}


void PomiarImpulsowy(uint16_t liczba_probek, volatile uint16_t opoznienie)
{
	/*		WYLACZENIE ADC		*/
	DMA_CH1_CTRLA &= ~(DMA_CH_ENABLE_bm);	// wylaczenie transferu DMA z ADC
	ADCA_CTRLA |= ADC_FLUSH_bm;				// wyczyszczenie potoku ADC
	//------------------------------------------------------------------------------
	/*		WYLACZENIE DMA DAC'A		*/
	//TCC0_CTRLA = TC_CLKSEL_OFF_gc;			// wylaczenie timera
	DMA_CH0_CTRLA &= ~(DMA_CH_ENABLE_bm);	// WYLACZENIE transmisji DMA DAC'a
	//------------------------------------------------------------------------------
	/*		WYSTAWIENIE WARTOSCI 0 NA DAC'A			*/
	while ( ( DACB.STATUS & DAC_CH0DRE_bm ) == 0 ); // czekaj na zakonczenie poprzedniej konwersji (jeszcze z DMA)
	DACB.CH0DATA = 0;	// wpisz wartosc do rejestru -> wystaw na wyjscie
	while ( ( DACB.STATUS & DAC_CH0DRE_bm ) == 0 ); // czekaj na wystawienie 0
	//------------------------------------------------------------------------------
	/*		WYLACZENIE TIMERA TAKTUJACEGO DAC		*/
	TCC0_CTRLA = TC_CLKSEL_OFF_gc;			// wylaczenie timera
	//------------------------------------------------------------------------------
	/*		 CZYSZCZENIE TABLICY PROBEK		*/
	for(uint16_t i = 0;i<liczba_probek;i++)
	{
		probki_pomiaru[i] = 0;
	}
	//------------------------------------------------------------------------------
	/*		WPISANIE SINC'A  DO TABLICY - DO GENERACJI		*/
	WyborPrzebiegu(SINC_1000_NR,liczba_probek); // na razie grzadkowo - siewnie ;) -> switch(liczba_probek)...
	//------------------------------------------------------------------------------
	/*		 INICJALIZACJA DMA		*/
	DMA_initTransfer_ADC( probki_pomiaru , liczba_probek * sizeof( uint16_t ) );
	DMA_initTransfer_DAC_imp(probki_sygnalu,liczba_probek * sizeof( uint16_t ) );
	//------------------------------------------------------------------------------
	/*		 START TIMERA		*/
	TCC0_CTRLA        =    TC_CLKSEL_DIV1_gc;         // bez prescalera
	// odczekaj do stanu ustalonego
	for(uint16_t i = 0; i< opoznienie;i++)
	{
		_delay_ms(10); // czekaj 10 ms
	}
	//------------------------------------------------------------------------------
	/*		URUCHOMIENIE DAC		*/
	DMA_CH0_CTRLA |= DMA_CH_ENABLE_bm; //DAC
	//------------------------------------------------------------------------------
	/*		URUCHOMIENIE ADC		*/
	DMA_CH1_CTRLA |= DMA_CH_ENABLE_bm; // wlaczenie transferu DMA probek zmierzonych przez ADC
	DMA_CH1_CTRLB |= DMA_CH_TRNINTLVL_MED_gc; // przerwanie DMA po koncu transmisji bloku
}
//-------------------------------------------------------------------------------------------------------------------------------------------------------------
//				FUNKCJE KONWERSJI

char cyfraNaZnak(uint8_t cyfra)
{
	switch (cyfra)
	{
		case 0 : return '0';
		case 1 : return '1';
		case 2 : return '2';
		case 3 : return '3';
		case 4 : return '4';
		case 5 : return '5';
		case 6 : return '6';
		case 7 : return '7';
		case 8 : return '8';
		case 9 : return '9';
		default: return '0';
	}
}

void liczbaNaZnaki(uint16_t probka, char * bufor)
{
	uint8_t liczba_jednosci   = probka % 10;
	uint8_t liczba_dziesiatek = (probka/10) % 10;
	uint8_t liczba_setek      = (probka/100) % 10;
	uint8_t liczba_tysiecy    = (probka/1000) % 10;
	
	bufor[0] = cyfraNaZnak(liczba_jednosci);
	bufor[1] = cyfraNaZnak(liczba_dziesiatek);
	bufor[2] = cyfraNaZnak(liczba_setek);
	bufor[3] = cyfraNaZnak(liczba_tysiecy);
}

void NadajWynik(uint16_t * tablicaProbek, uint16_t liczbaProbek)
{
	for(int i = 0; i < liczbaProbek ;i++)
	{
		printf("%d",tablicaProbek[i]);
		if ( !((i+1) % 20) )
		{
			udi_cdc_write_buf("\n\r",2);
		}
		else
		{
			udi_cdc_write_buf(" ",1);
		}
	}
	udi_cdc_write_buf("\n\r\n\r",4);
	udi_cdc_write_buf(STRING_TERMINACJI,STRING_TERMINACJI_LEN);
}

//-------------------------------------------------------------------------------------------------------------------------------------------------------------
//				FUNKCJE POZOSTALE

uint8_t ReadCalibrationByte(uint8_t index)
{
	uint8_t result;

	NVM_CMD=NVM_CMD_READ_CALIB_ROW_gc; //Odczytaj sygnaturê produkcyjn¹
	result=pgm_read_byte(index);

	NVM_CMD=NVM_CMD_NO_OPERATION_gc;   //Przywróæ normalne dzia³anie NVM
	return result;
}

void WlaczPeryferia(void)
{
	// wlaczamy peryferia kasujac odpowiednie bity w rejestrach PR.
	// w funkcji sysclk_init() zegar jest odlaczany od wszystkiego!
	PR.PRGEN &= ~(PRGEN_EVSYS | PRGEN_DMA);// USB NIE WLACZAMY -> zakladam ze zostalo wlaczone w ASF
	PR.PRPA  &= ~(PRPA_ADC);
	PR.PRPB  &= ~(PRPB_DAC);
	PR.PRPC  &= ~(PRPC_TC0);
}

double oblicz_DFT(uint16_t k , uint16_t N, const uint16_t sygnal[] )
{
	double Re_DFT    = 0;
	double Im_DFT    = 0;
	double Modul_DFT = 0;
	int n;

	for(n = 0;n<N;n++) // n -> DFT probka czasu
	{
		Re_DFT += (sygnal[n] * cos( (2 * M_PI * k * n)/N))/N;
		Im_DFT += (sygnal[n] * sin( (2 * M_PI * k * n)/N))/N;
	}

	Modul_DFT = sqrt(Re_DFT*Re_DFT + Im_DFT*Im_DFT)/ ADC_MAX_F; // z normalizacja
	//Modul_DFT = sqrt(Re_DFT*Re_DFT + Im_DFT*Im_DFT);			// bez normalizacji
	return Modul_DFT;

}
//--------------------------------------------------------------------------------------------------
//				FUNKCJE TAKTOWANIA -> Tomasz Francuz
bool OSC_wait_for_rdy(uint8_t clk)
{
	uint8_t czas=255;
	while ((!(OSC.STATUS & clk)) && (--czas)) // Czekaj na ustabilizowanie siê generatora
	_delay_ms(1);
	return czas;   //false jeœli generator nie wystartowa³, true jeœli jest ok
}

void SelectPLL(OSC_PLLSRC_t src, uint8_t mult)
{
	mult &= OSC_PLLFAC_gm;
	OSC.PLLCTRL = src | mult;
	OSC.CTRL |= OSC_PLLEN_bm;
	OSC_wait_for_rdy(OSC_PLLRDY_bm);
}
//--------------------------------------------------------------------------------------------------
void analizaRamkiDanych(uint16_t * okres_timera,uint16_t * liczba_probek,uint8_t * przebieg, unsigned char ramka_danych[])
{
	uint8_t flagi_pomiaru;
	switch(ramka_danych[POLECENIE_POZYCJA])		//	pierwszy znak okresla znaczenie polecenia
	{
		case 'G' :	// Generacja
			*przebieg = ramka_danych[GEN_PRZEBIEG_Bp];
			*okres_timera = (ramka_danych[GEN_PER_MSB_Bp] << 8) | ramka_danych[GEN_PER_LSB_Bp];
			*liczba_probek = ramka_danych[GEN_LICZB_PROBEK_Bp];
			switch(*liczba_probek)
			{
				case LICZBA_PROBEK_1000 :	*liczba_probek = 1000;
											break;
				case LICZBA_PROBEK_250  :	*liczba_probek = 250;
											break;
				case LICZBA_PROBEK_100  :	*liczba_probek = 100;
											break;
				default :					*liczba_probek = 1000;
											break;
			}
			Generacja(*okres_timera,*przebieg,*liczba_probek);
			break;
		case 'P' : // Pomiar
			flagi_pomiaru = ramka_danych[POM_FLAGI_Bp]; // odczyt flag pomiaru
			if (flagi_pomiaru & 0x02)
			{
				PomiarImpulsowy(*liczba_probek,ramka_danych[POM_DELAY_Bp]);
			}
			else
			{
				PomiarOkresowyADC(*liczba_probek,ramka_danych[POM_DELAY_Bp]);	
			}
			break;
		default :	break;
	}
}