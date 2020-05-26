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
volatile uint16_t licznik_ms = 0;
//volatile uint16_t offsetADC;
//volatile float gainADC;

//-----------------------------------------------------------------------------------------------
//				FUNKCJE OBSLUGI PRZERWAN

ISR(DMA_CH1_vect) // przerwanie po transmisji bloku
{

	DMA_CH1_CTRLB &= ~(DMA_CH_TRNINTLVL_MED_gc); // wylaczenie przerwania
	// wyczyszczenie flagi przerwania
	DMA_CH1_CTRLB |= DMA_CH_TRNIF_bm;
	flagi |= KONIEC_ZBIERANIA_PROBEK;
}

ISR(TCC1_OVF_vect)
{
	licznik_ms++;
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
	 uint16_t liczba_probek = 500;
	 uint8_t  przebieg = SINUS_500_NR;
	 unsigned char ramka_danych_USB[ROZMIAR_RAMKI_USB_MAX];
	 uint8_t licznik_znakow = 0;
	 //----------------------------------------------------
	 //				FUNKCJE WYKONYWANE JEDNORAZOWO
	 WlaczPeryferia();
	/* offsetADC = KalibracjaOffsetuADC();
	 gainADC = KalibracjaWzmocnieniaADC();*/
	 Init();
	 //----------------------------------------------------
	 //				PETLA GLOWNA 
	 
	 
	 while(1)
	 {
		  char ch;
		  if (udi_cdc_is_rx_ready()) 
		  {
			  ch = udi_cdc_getc();
			  ramka_danych_USB[licznik_znakow] = ch;
			  licznik_znakow++;
			  if (ZNAK_TERMINACJI == ch)
			  {				  				  		  
				  for(uint8_t i = 0; i < licznik_znakow;i++)
				  {
					  udi_cdc_putc(ramka_danych_USB[i]);
				  }
				  licznik_znakow = 0;
				  analizaRamkiDanych(&okres_timera,&liczba_probek,&przebieg,ramka_danych_USB);
			  }
		  }
		  
		  if ( ( flagi & KONIEC_ZBIERANIA_PROBEK ) )
		  {
			  flagi &= ~(KONIEC_ZBIERANIA_PROBEK);
			  if ( (flagi & WYSLIJ_POMIAR ))
			  {
				  flagi &= ~(WYSLIJ_POMIAR);
				  NadajWynik(probki_pomiaru,liczba_probek);
			  }
		  }
		  
		  if ( !(BUTTON_PORT.IN & (1<<BUTTON_1_PIN)) )// kiedy przycisk 1 jest wcisniety
		  {
			  delayTCC1(DEBOUNCING_DELAY_ms);
			  //Generacja(okres_timera, MULTI_SIN_500_NR, liczba_probek);
			  Testuj(&okres_timera , &przebieg,  &liczba_probek,  MULTI_SIN_500_NR,  SLOWNIK_MULTISIN);
		  }
		  
		  if ( !(BUTTON_PORT.IN & (1<<BUTTON_2_PIN)) )// kiedy przycisk 2 jest wcisniety
		  {
			  delayTCC1( DEBOUNCING_DELAY_ms );
			  //Generacja(okres_timera, SINC_500_NR, liczba_probek);
			  Testuj(&okres_timera , &przebieg,  &liczba_probek,  SINC_500_NR,  SLOWNIK_SINC);
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
	//#undef  F_CPU
	//#define F_CPU 32000000UL
	
	// wczytanie danych kalibracyjnych z pamieci nieulotnej:
	ADCA.CALL = ReadCalibrationByte(offsetof(NVM_PROD_SIGNATURES_t, ADCACAL0)); // blad nieliniowosci ADC
	ADCA.CALH = ReadCalibrationByte(offsetof(NVM_PROD_SIGNATURES_t, ADCACAL1)); // blad nieliniowosci ADC
	DACB.CH0GAINCAL = ReadCalibrationByte(offsetof(NVM_PROD_SIGNATURES_t, DACB0GAINCAL)); // blad wzmocnienia DAC
	DACB.CH0OFFSETCAL = ReadCalibrationByte(offsetof(NVM_PROD_SIGNATURES_t, DACB0OFFCAL)); // blad offsetu DAC
	
	sei();	// globalne odblokowanie przerwan
	DMA_init();
	DAC_init();
	//ADC_Init(&ADCA.CH0,ADC_CH_MUXPOS_PIN4_gc); // 256A3Bu
	ADC_Init(&ADCA.CH0,ADC_CH_MUXPOS_PIN1_gc); // 32A4
	TCC0_Init(31); // Timer taktujacy DAC i ADC
	TCC0_CTRLA        =    TC_CLKSEL_DIV1_gc;         // bez prescalera
	
	ButtonInit( &(BUTTON_PORT) );
	LEDInit( &(LED_PORT) );
	
	lcd_init();
	lcd_cls();
	lcd_goto(0,0);
	lcd_puttext_P(PSTR("DIAGNOSIS OF"));
	lcd_goto(0,1);
	lcd_puttext_P(PSTR("ANALOG CIRCUIT"));
}
//-------------------------------------------------------------------------------------------------------------------------------------------------------------
//				FUNKCJE POMIAROWE

void Generacja(uint16_t okres_timerow,uint8_t przebieg, uint16_t liczba_probek)
{
	/*		WYLACZENIE POPRZEDNIEJ GENERACJI		*/
	// wylaczenie timera
	TCC0_CTRLA = TC_CLKSEL_OFF_gc;
	delayTCC1(10);
	// WYLACZENIE transmisji DMA DAC'a
	DMA_CH0_CTRLA &= ~(DMA_CH_ENABLE_bm);
	
	/*		WLACZENIE NOWEJ GENERACJI		*/
	// wybor przebiegu generowanego przez DAC
	WyborPrzebiegu(przebieg,liczba_probek);
	// ustawienie do ilu ma zliczac licznik
	TCC0_Init(okres_timerow);
	
	// inicjalizacja DMA
	DMA_initTransfer_DAC( probki_sygnalu , liczba_probek * sizeof( uint16_t ) );
	//		START TIMERA - dopoki TCC0 nie jest wlaczony DAC i ADC nie pracuja
	TCC0_CTRLA        =    TC_CLKSEL_DIV1_gc;         // bez prescalera
	// wlaczenie transmisji DMA DAC'a
	DMA_CH0_CTRLA |= DMA_CH_ENABLE_bm; //DAC
	delayTCC1(100);
}

void PomiarOkresowyADC(uint16_t liczba_probek, volatile uint16_t opoznienie)
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
	delayTCC1(opoznienie);
	DMA_CH1_CTRLA |= DMA_CH_ENABLE_bm; // wlaczenie transferu DMA probek zmierzonych przez ADC
	DMA_CH1_CTRLB |= DMA_CH_TRNINTLVL_MED_gc; // przerwanie DMA po koncu transmisji bloku
}

void WyborPrzebiegu(uint8_t przebieg, uint16_t liczba_probek)
{
	// funkcja wczytujaca wybrany przebieg z pamieci FLASH do TABLICY GLOBALNEJ probki_sygnalu
	switch(przebieg)
	{
		case SINUS_500_NR :	memcpy_P(probki_sygnalu,sinus_500,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
		case SINUS_250_NR :	memcpy_P(probki_sygnalu,sinus_250,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
		case SINUS_100_NR :	memcpy_P(probki_sygnalu,sinus_100,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
		case MULTI_SIN_500_NR : memcpy_P(probki_sygnalu,multi_sin_wave_500,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
		case SINC_500_NR :		memcpy_P(probki_sygnalu,sinc_wave_500,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
		break;
		default :				memcpy_P(probki_sygnalu,multi_sin_wave_500,liczba_probek * sizeof(uint16_t)); // wgranie probek z pamieci FLASH
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
	DMA_CH0_CTRLA &= ~(DMA_CH_ENABLE_bm);	// WYLACZENIE transmisji DMA DAC'a
	//------------------------------------------------------------------------------
	/*		WYSTAWIENIE WARTOSCI 0 NA DAC'A			*/
	while ( ( DACB.STATUS & DAC_CH0DRE_bm ) == 0 ); // czekaj na zakonczenie poprzedniej konwersji (jeszcze z DMA)
	/*		WPISANIE SINC'A  DO TABLICY - DO GENERACJI		*/
	
	WyborPrzebiegu(SINC_500_NR,liczba_probek);
	DACB.CH0DATA = probki_sygnalu[0];	// wpisz wartosc do rejestru -> wystaw na wyjscie
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
	/*		 INICJALIZACJA DMA		*/
	DMA_initTransfer_ADC( probki_pomiaru , liczba_probek * sizeof( uint16_t ) );
	DMA_initTransfer_DAC_imp(probki_sygnalu,liczba_probek * sizeof( uint16_t ) );
	//------------------------------------------------------------------------------
	/*		 START TIMERA		*/
	TCC0_CTRLA        =    TC_CLKSEL_DIV1_gc;         // bez prescalera
	// odczekaj do stanu ustalonego
	delayTCC1(opoznienie);
	//------------------------------------------------------------------------------
	/*		URUCHOMIENIE DAC		*/
	DMA_CH0_CTRLA |= DMA_CH_ENABLE_bm; //DAC
	//------------------------------------------------------------------------------
	/*		URUCHOMIENIE ADC		*/
	DMA_CH1_CTRLA |= DMA_CH_ENABLE_bm; // wlaczenie transferu DMA probek zmierzonych przez ADC
	DMA_CH1_CTRLB |= DMA_CH_TRNINTLVL_MED_gc; // przerwanie DMA po koncu transmisji bloku
}

void delayTCC1(uint16_t ms)
{
	licznik_ms = 0; // dla bezpieczenstwa :)
	TCC1_Init(PER_1_ms);
	while(licznik_ms < ms);
	TCC1_CTRLA = TC_CLKSEL_OFF_gc; // WYLACZENIE TIMERA
	licznik_ms = 0;
}
//-------------------------------------------------------------------------------------------------------------------------------------------------------------
//				FUNKCJE KONWERSJI

void NadajWynik(uint16_t * tablicaProbek, uint16_t liczbaProbek)
{
	for(int i = 0; i < liczbaProbek ;i++)
	{
		printf("%d",tablicaProbek[i]);
		udi_cdc_putc(' '); // rozdzielamy liczby spacjami
	}
	udi_cdc_putc(ZNAK_TERMINACJI);
}

void NadajWidmo(char * tablicaFloatToChar, uint8_t liczbaElementow)
{
	for(uint8_t i = 0; i < liczbaElementow ;i++)
	{
		printf("%d",tablicaFloatToChar[i]);
		udi_cdc_putc(' '); // rozdzielamy czesci floata spacjami
	}
	udi_cdc_putc(ZNAK_TERMINACJI);
}

void NadajInfo(uint16_t  okres_timera, uint16_t  liczba_probek,uint8_t  przebieg)
{
	uint8_t liczba_probek_znak = 0;
	switch(liczba_probek)
	{
		case 500 :
			liczba_probek_znak = LICZBA_PROBEK_500;
			break;
		case 250 :
			liczba_probek_znak = LICZBA_PROBEK_250;
			break;
		case 100:
			liczba_probek_znak = LICZBA_PROBEK_100;
			break;
		default: liczba_probek_znak = LICZBA_PROBEK_500;
	}
	
	printf("I %d %d %d %c", przebieg, okres_timera, liczba_probek_znak, ZNAK_TERMINACJI );
	
}

uint8_t znakNaCyfre(unsigned char znak)
{
	switch (znak)
	{
		case '0' : return 0;
		case '1' : return 1;
		case '2' : return 2;
		case '3' : return 3;
		case '4' : return 4;
		case '5' : return 5;
		case '6' : return 6;
		case '7' : return 7;
		case '8' : return 8;
		case '9' : return 9;
		default : return 0;
	}
}

uint16_t znakiNaLiczbe( unsigned char tablica_znakow[],uint8_t start_ind)
{
	uint8_t i;
	uint8_t cyfra = 0;
	uint16_t liczba=0;
	uint16_t potega = 10000;
	for(i = start_ind ; i < start_ind + MAX_LICZBA_CYFR ; i++)
	{
		cyfra = znakNaCyfre(tablica_znakow[i]);
		liczba+=cyfra*potega;
		potega/=10;
	}
	return liczba;
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
	PR.PRPC  &= ~(PRPC_TC0 | PRPC_TC1);
}

float oblicz_DFT(uint16_t k , uint16_t N, const uint16_t sygnal[] )
{
	float Re_DFT    = 0;
	float Im_DFT    = 0;
	float Modul_DFT = 0;
	int n;
	uint16_t x = 0;

	for(n = 0;n<N;n++) // n -> DFT probka czasu
	{
		//float x = ( (float)(sygnal[n]) - offsetADC );
		x = sygnal[n] - ADC_OFFSET;
		//Re_DFT += (sygnal[n] * cos( (2 * M_PI * k * n)/N))/N;
		//Im_DFT += (sygnal[n] * sin( (2 * M_PI * k * n)/N))/N;
		Re_DFT += (x * cos( (2 * M_PI * k * n)/N))/N;
		Im_DFT += (x * sin( (2 * M_PI * k * n)/N))/N;
	}

	Modul_DFT = sqrt(Re_DFT*Re_DFT + Im_DFT*Im_DFT)/ ADC_MAX_F; // przejscie z wartosci ADC na napiecie
	//Modul_DFT = sqrt(Re_DFT*Re_DFT + Im_DFT*Im_DFT);			// bez normalizacji
	return Modul_DFT;

}

float obliczTF(const uint16_t sygnal[],uint16_t liczba_elementow, uint16_t f, uint16_t okres_timera)
{
	float w = 2 * M_PI * (float)(f); // pulsacja
	float T = ((float)(okres_timera+1)) / ((float)F_CPU) ; // okres probkowania
	float ReU    = 0.0;
	float ImU    = 0.0;
	float ModulU = 0.0;
	float tn = 0.0;
	float tn_p1 = T;
	float a = 0; // wspolczynnik kierunkowy
	float u_tn_plus_1;
	float u_tn;
	uint16_t i ;

	for (i = 0; i < (liczba_elementow-1);i++)
	{
		u_tn = (float)(sygnal[i]) - (float)(sygnal[0]);
		u_tn_plus_1 = (float)(sygnal[i+1]) - (float)(sygnal[0]);
		tn = (float)((i)) * T;
		tn_p1 =(float)((i + 1))  * T;
		a = ( u_tn_plus_1 - u_tn ) / (T);
		ReU += (( ( u_tn_plus_1 * sin(w*tn_p1) ) - ( u_tn * sin(w*tn)) )/w) + a * ( cos(w*tn_p1) - cos(w*tn) )/(w*w);
		ImU -= (( ( u_tn_plus_1 * cos(w*tn_p1) ) - ( u_tn * cos(w*tn) ) )/w) - a * ( sin(w*tn_p1) - sin(w*tn) )/(w*w);
	}

	ModulU = sqrt(ReU*ReU + ImU*ImU) / ADC_MAX_F; // z normalizacja -> do 1 V
	return ModulU;
}

//--------------------------------------------------------------------------------------------------
//				FUNKCJE TAKTOWANIA -> Tomasz Francuz
bool OSC_wait_for_rdy(uint8_t clk)
{
	uint8_t czas= 20; //255; - tutaj jeszcze czestotliwosc taktowania rdzenia to 2MHz a nie 32 MHz, wiec mamy 20 * 16ms = 320 ms delaya
	while ((!(OSC.STATUS & clk)) && (--czas)) // Czekaj na ustabilizowanie siê generatora
	{
		//_delay_ms(1);
		//_delay_ms(16); // tutaj jeszcze czestotliwosc taktowania rdzenia to 2MHz a nie 32 MHz ...
		delayTCC1(1); // tutaj jeszcze czestotliwosc taktowania rdzenia to 2MHz a nie 32 MHz, wiec delayTCC1(1) -> 16 ms
	}
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
	uint8_t typ_pomiaru;
	uint16_t czestotliwosc; // w zaleznosci od typu transformaty albo oznacza prazek widma k X[k], albo konkretna czestotliwosc X(f)
	union
	{
		float widmo;
		char c[sizeof(float)]; // float ma dlugosc 32 bitow 32/8 = 4
	} unia_widmo;
	
	lcd_cls();
	lcd_goto(0,0);
	lcd_puttext_P(PSTR("REMOTE CONTROL"));
	lcd_goto(0,1);
	
	LED_PORT.OUTSET = (1<<LED_FAULT_PIN); // wygas LED uszkodzenia
	LED_PORT.OUTSET = (1<<LED_NOM_PIN); // wygas LED NOMINALNE
	
	switch(ramka_danych[POLECENIE_POZYCJA])		//	pierwszy znak okresla znaczenie polecenia
	{
		case 'G' :	// Generacja
			*przebieg = znakNaCyfre(ramka_danych[GEN_PRZEBIEG_Bp]);
			*okres_timera = znakiNaLiczbe(ramka_danych, GEN_PER_START_Bp);
			*liczba_probek = znakNaCyfre(ramka_danych[GEN_LICZB_PROBEK_Bp]);
			switch(*liczba_probek)
			{
				case LICZBA_PROBEK_500 :	*liczba_probek = 500;
											break;
				case LICZBA_PROBEK_250  :	*liczba_probek = 250;
											break;
				case LICZBA_PROBEK_100  :	*liczba_probek = 100;
											break;
				default :					*liczba_probek = 500;
											break;
			}
			Generacja(*okres_timera,*przebieg,*liczba_probek);
			lcd_puttext_P(PSTR("GENERATION"));
			break;
		case 'P' : // Pomiar
			lcd_puttext_P(PSTR("MEASURE"));
			typ_pomiaru = ramka_danych[POM_TYP_Bp]; // odczyt flag pomiaru
			if (typ_pomiaru & POMIAR_IMPULSOWY)
			{
				PomiarImpulsowy(*liczba_probek, znakiNaLiczbe(ramka_danych, POM_DELAY_Bp) );
			}
			else
			{
				PomiarOkresowyADC(*liczba_probek,znakiNaLiczbe(ramka_danych, POM_DELAY_Bp));	
			}
			flagi |= WYSLIJ_POMIAR;
			break;
		case DFT: // OBLICZ DFT
			czestotliwosc = znakiNaLiczbe(ramka_danych, WIDMO_CZESTOTLIWOSC_Bp);
			unia_widmo.widmo = oblicz_DFT(czestotliwosc,*liczba_probek,probki_pomiaru);
			NadajWidmo(unia_widmo.c,sizeof(float));
			lcd_puttext_P(PSTR("SPECTRUM - DFT"));
			break;
		case TRANSFORMATA_FOURIERA:// oblicz TF
			czestotliwosc = znakiNaLiczbe(ramka_danych, WIDMO_CZESTOTLIWOSC_Bp);
			unia_widmo.widmo = obliczTF(probki_pomiaru,*liczba_probek,czestotliwosc, *okres_timera);
			NadajWidmo(unia_widmo.c,sizeof(float));
			lcd_puttext_P(PSTR("SPECTRUM - FT"));
			break;
		case INFORMACJE_O_PRZEBIEGU : // PC prosi o informacje o aktualnie generowanym przebiegu
			NadajInfo(*okres_timera, *liczba_probek, * przebieg );
			break;
		case REZULTAT_DIAGNOSTYKI :
			for(typ_pomiaru = REZULTAT_START_Bp; typ_pomiaru < REZULTAT_END_Bp ; typ_pomiaru++) // wykorzystujemy zmienna typ pomiaru, zeby nie definiowac nowej!
			{
				lcd_putchar(ramka_danych[typ_pomiaru]);
			}
			break;
		default :	break;
	}
}

/*uint16_t KalibracjaOffsetuADC(void)
{
	int16_t res_signed;
	uint16_t res_unsigned;
	uint16_t offset;
	
	// wylaczenie transferu DMA z ADC
	DMA_CH1_CTRLA &= ~(DMA_CH_ENABLE_bm);
	// wyczyszczenie potoku ADC
	ADCA_CTRLA |= ADC_FLUSH_bm;
	
	// KONFIGURACJA TRYBU ZE ZNAKIEM :
	ADCA.CTRLB = ADC_IMPMODE_bm | ADC_CURRLIMIT_NO_gc | ADC_CONMODE_bm ; // tryb signed (CONMODE!) 12 bitowy
	ADCA.REFCTRL = ADC_REFSEL_INT1V_gc | ADC_BANDGAP_bm; // 1V Vref
	ADCA.PRESCALER = ADC_PRESCALER_DIV16_gc ; // probkowanie 125 kbps -> dla f_cpu = 2 MHz
	ADCA.CH0.CTRL = ADC_CH_INPUTMODE_INTERNAL_gc; // KANAL POLACZONY Z WEWNETRZYM ZRODLEM SYGNALU
	ADCA.CH0.MUXCTRL = ADC_CH_MUXINT_SCALEDVCC_gc; // mierzymy Vcc / 10
	
	ADCA.CALL=ReadCalibrationByte(offsetof(NVM_PROD_SIGNATURES_t, ADCACAL0));
	ADCA.CALH=ReadCalibrationByte(offsetof(NVM_PROD_SIGNATURES_t, ADCACAL1));
	ADCA.CTRLA=ADC_DMASEL_OFF_gc | ADC_ENABLE_bm;
	_delay_ms(100);
	res_signed = PomiarADC(); // pobierz wynik dla trybu ze znakiem
	//-------------------------
	// przejscie do trybu bez znaku:
	ADCA.CTRLB &= ~ADC_CONMODE_bm; // TRYB BEZ ZNAKU!
	_delay_ms(100);
	res_unsigned = PomiarADC();
	_delay_ms(100);
	offset = res_unsigned - (res_signed << 1); // obliczenie offsetu ADC
	printf("Offset ADC wynosi : %d\n\r", offset);
	return offset;
}

float KalibracjaWzmocnieniaADC(void)
{
	volatile uint16_t pomiar1024,pomiar3072;
	volatile float a;
	
	DACB.CH0GAINCAL = ReadCalibrationByte(offsetof(NVM_PROD_SIGNATURES_t, DACB0GAINCAL)); // blad wzmocnienia DAC
	DACB.CH0OFFSETCAL = ReadCalibrationByte(offsetof(NVM_PROD_SIGNATURES_t, DACB0OFFCAL)); // blad offsetu DAC
	DACB.CTRLC = DAC_REFSEL_INT1V_gc;          //Wewn. napiêcie ref. 1 V
	DACB.CTRLA = DAC_ENABLE_bm | DAC_IDOEN_bm; //W³¹cz DAC, kana³ 0 routowany wewnetrznie do ADC
	
	ADCA.CTRLB &= ~ADC_CONMODE_bm; // TRYB BEZ ZNAKU!
	ADCA.CH0.CTRL = ADC_CH_INPUTMODE_INTERNAL_gc; // KANAL POLACZONY Z WEWNETRZYM ZRODLEM SYGNALU
	ADCA.CH0.MUXCTRL = ADC_CH_MUXINT_DAC_gc; // mierzymy wyjscie DACa
	
	UstawDACa(1024);
	_delay_ms(100);
	pomiar1024 = PomiarADC();
	printf("DAC = 1024 -> ADC = %d\n\r",pomiar1024);
	UstawDACa(3072);
	_delay_ms(100);
	pomiar3072 = PomiarADC();
	printf("DAC = 3072 -> ADC = %d\n\r",pomiar3072);
	a = (2048.0) / ( (float)(pomiar3072 - pomiar1024) ); // obliczenie nachylenia prostej
	return a;
}*/

uint8_t Diagnostyka(float * widmo, uint8_t typ_slownika)
{
	/*
		WYSOKO-POZIOMOWA FUNKCJA DIAGNOZUJACA UKLAD
		zwraca etykiete uszkodzenia
	*/
	if ( stan_nominalny(widmo, typ_slownika) )
	{
		LED_PORT.OUTCLR = (1<<LED_NOM_PIN); // zapal LED stanu nominalnego
		LED_PORT.OUTSET = (1<<LED_FAULT_PIN); // wygas LED uszkodzenia
		return NOMINALNY;
	}
	else
	{
		LED_PORT.OUTCLR = (1<<LED_FAULT_PIN);	// zapal LED uszkodzenia
		LED_PORT.OUTSET = (1<<LED_NOM_PIN);		// wygas LED stanu nominalnego
		return klasyfikacja(widmo, typ_slownika);
	}
}

void wypiszWynikDiagnozyLCD(uint8_t etykieta_uszkodzenia)
{
	char bufor[LICZBA_ZNAKOW_SYGNATURY];
	// wypisuje na LCD uszkodzenie
	lcd_cls();
	lcd_goto(0,0);
	lcd_puttext_P(PSTR("MCU TEST"));
	lcd_goto(0,1);
	
	strcpy_P(bufor, (PGM_P)pgm_read_word(& (NapisyLCD[etykieta_uszkodzenia]) ));
	lcd_puttext(bufor);
}

void ButtonInit(PORT_t *port)
{
	port -> DIRCLR = (1<<BUTTON_1_PIN) | (1<< BUTTON_2_PIN); // piny sa WEJsciami
	PORTCFG_MPCMASK = (1<<BUTTON_1_PIN) | (1<< BUTTON_2_PIN); // zgrupowania dwoch pinow razem do nastepnej operacji
	port -> PIN0CTRL = PORT_OPC_PULLUP_gc ; // rezystory podciagajace 
}

/*uint8_t debouncing(volatile uint8_t *rejestr_portu, uint8_t pin, uint8_t opoznienie_ms )
{
	delayTCC1(opoznienie_ms);
	if( !( *rejestr_portu & (1<<pin) ) ) // sprawdzenie czy przycisk nadal jest wcisniety - stan niski
	{
		return 1;
	}
	else
	{
		return 0; // zakladamy ze to jakies zaklocenie
	}
}*/

void LEDInit(PORT_t *port)
{
	port -> DIRSET = (1<<LED_NOM_PIN) | (1<<LED_FAULT_PIN) ; // LEDy sa wyjsciami
	port -> OUTSET = (1<<LED_NOM_PIN) | (1<<LED_FAULT_PIN); // led aktywny stanem niskim -> stan wysoki wygasza
}

uint8_t SprawdzParametryPrzebiegu(uint16_t okres_timerow,uint8_t przebieg, uint16_t liczba_probek, uint8_t przebieg_docelowy)
{
	if( (przebieg_docelowy != przebieg) || ( (500 != liczba_probek) ) ) 
	{
		return 0;
	}
	else
	{
		if ( SINC_500_NR == przebieg_docelowy )
		{
			if (SINC_DIAG_PER != okres_timerow) return 0;
		}
		else
		{
			if ( MULTISIN_DIAG_PER != okres_timerow ) return 0;
		}
		return 1;
	}
}

void wyznaczWimo(float wynik[], uint16_t liczba_elementow, uint16_t okres_timera ,uint8_t typ_slownika)
{
	uint16_t czestotliwosci[LICZBA_PROBEK_WIDMA]; // tablica czestotliwosci
	uint8_t i;
	//			WCZYTANIE TABELI CZESTOTLIWOSCI
	if ( SLOWNIK_SINC == typ_slownika)
	{
		memcpy_P(czestotliwosci, czestotliwosci_sinc, LICZBA_PROBEK_WIDMA * sizeof(uint16_t));
		for (i=0; i < LICZBA_PROBEK_WIDMA; i++) // wyznaczenie widma dla zadanych czestotliwosci
		{
			wynik[i] = obliczTF( probki_pomiaru, liczba_elementow, czestotliwosci[i], okres_timera );
		}
	}
	else
	{
		memcpy_P(czestotliwosci, czestotliwosci_multisin_k, LICZBA_PROBEK_WIDMA * sizeof(uint16_t));
		for (i = 0; i < LICZBA_PROBEK_WIDMA; i++) // wyznaczenie widma dla zadanych czestotliwosci
		{
			wynik[i] = oblicz_DFT( czestotliwosci[i], liczba_elementow , probki_pomiaru  );
		}
	}
	
}

void Testuj(uint16_t *okres_timerow,uint8_t *przebieg, uint16_t * liczba_probek, uint8_t przebieg_docelowy, uint8_t typ_slownika)
{
	uint16_t delay = DELAY_BEZ_ZMIANY_PRZEBIEGU_ms;
	float widmo[LICZBA_PROBEK_WIDMA];
	
	if (! ( SprawdzParametryPrzebiegu(*okres_timerow,* przebieg, *liczba_probek, przebieg_docelowy) ) )// kiedy generowany jest inny przebieg niz do diagnostyki
	{
		if (SINC_500_NR == przebieg_docelowy)
		{
			*okres_timerow = SINC_DIAG_PER;
		}
		else
		{
			*okres_timerow = MULTISIN_DIAG_PER;
		}
		*przebieg = przebieg_docelowy;
		//*liczba_probek = LICZBA_PROBEK_500; <- ZLE!!! TO MAKRO OKRESLA TYLKO FLAGE LICZBY!!!
		*liczba_probek = 500;
		
		Generacja(*okres_timerow,*przebieg,*liczba_probek);
		delay = DELAY_ZE_ZMIANA_PRZEBIEGU_ms;
	}
	
	//		POMIAR:
	if (SINC_500_NR == przebieg_docelowy)
	{
		PomiarImpulsowy(*liczba_probek, delay);
	}
	else
	{
		PomiarOkresowyADC(*liczba_probek, delay);
	}
	delayTCC1(delay);
	while(1)
	{
		if ( ( flagi & KONIEC_ZBIERANIA_PROBEK ) )
		{
			flagi &= ~(KONIEC_ZBIERANIA_PROBEK);
			break;
		}
	}
	
	//		WIDMO:
	wyznaczWimo( widmo, *liczba_probek, *okres_timerow, typ_slownika );
	//		DIAGNOSTYKA
	wypiszWynikDiagnozyLCD( Diagnostyka(widmo, typ_slownika )) ;
}
