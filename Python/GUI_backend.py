"""
MODUL ZAWIERAJACY BACK-END DO GUI
"""

import serial
import serial.tools.list_ports
import numpy as np
import os
import funkcje
import datetime
#-------------------------------------------------------------------------------------------
# stale
F_CPU = int(32e6) # 32 MHz - czestotliwosc taktowania rdzenia
ADC_VREF = 1.0
ADC_MAX = 4096
ADC_OFFSET = 200
POMIAR_FLAGI = {"POMIAR_OKRESOWY": 1 ,"POMIAR_IMPULSOWY": 2 }
LICZBY_PROBEK = [500,250,100]
F_MAX = [2000,4000,10000]
LICZBA_PROBEK_f_MAX = [(1000,1000),(250,4000),(100,10000)]
PRZEBIEGI = {"SINUS_500_NR" : 0 , "SINUS_250_NR" : 1, "SINUS_100_NR" : 2,
             "MULTI_SIN_500_NR" : 4 "SINC_500_NR" : 7}
KSZTALTY = ["SINUS","MULTI_SIN","SINC"]
KONCOWKA_LICZBA_PROBEK = ["_500_NR","_250_NR","_100_NR"]
TERMINATOR = b'\x24'
TERMINATOR_STRING = '$$$$'
LICZBA_ZNAKOW_TERMINACJI = 4
# opcje transmisji
BAUDRATE = 115200
TIMEOUT = None
POMIAR_MULTISIN  = 1
POMIAR_IMPULSOWY = 2
PER_MIN = 31


SCIEZKA_DO_SLOWNIKOW = 'C:\\Users\\Marek\\Desktop\\Studia\\STUDIA_MAGISTERSKIE\\Praca_Magisterska\\Programy\\Python\\slowniki_uszkodzen'
#-------------------------------------------------------------------------------------------
# zmienne globalne
port_szeregowy = 0
PER_INT = 31
wyniki_pomiaru = [1,2,3,4,5,6,7,11,9]
widmoPC = np.array([])
widmoMCU = np.array([])
slownik_uszkodzen = {} # zmienna globalna zawierajaca slownik uszkodzen
#-------------------------------------------------------------------------------------------

def Analiza(czestotliwosc,opoznienie, opcje_pomiaru, typ_pomiaru, portCOM, nazwa_ukladu):
    global wyniki_pomiaru
    global slownik_uszkodzen
    global widmoPC

    wynik = ''
    #print(opcje_pomiaru)
    
    slownik_uszkodzen = WczytajSlownikUszkodzenMultisin(nazwa_ukladu)
    if (not (OtworzPortCOM(portCOM))) : return "COM fail" # bledne otwarcie portu
    if (opcje_pomiaru["Generacja"]) : Generacja(czestotliwosc,typ_pomiaru)
    if (opcje_pomiaru["Pomiar"]) :
        if (typ_pomiaru == POMIAR_IMPULSOWY) : wyniki_pomiaru = PomiarImp(opoznienie)
        else : wyniki_pomiaru = PomiarOkres(opoznienie)
    if (opcje_pomiaru["Widmo na MCU"]) :
        if (typ_pomiaru == POMIAR_IMPULSOWY) :
            WidmoSinc(typ_pomiaru)
        elif (typ_pomiaru == POMIAR_MULTISIN) :
            WidmoMultiSin(typ_pomiaru)
        else :
            WidmoSinus(typ_pomiaru)

    if (opcje_pomiaru["Diagnozuj"]) :
        widmoPC,frq = ObliczWidmo('FFT',wyniki_pomiaru,PER_INT)
        x = widmoPC[1:11] # na razie tak :)
        if SprawdzCzyStanNominalnyOdleglosc(nazwa_ukladu, x) :
            wynik = 'Nominalne'
        else :
            odleglosc_slownik = odlegloscPuntuOdSlownika(slownik_uszkodzen,x)
            wynik = KlasyfikacjaOdleglosc(odleglosc_slownik)
            
    if (opcje_pomiaru["Wyrysuj dane"]) :
        ZamknijCOM(portCOM)
        funkcje.plt.close('all') # zamkniecie wszystkich okien matplotlib
        #funkcje.plt.clf() # wyczyszczenie
        widmoPC,frq = ObliczWidmo('FFT',wyniki_pomiaru,PER_INT)
        funkcje.wyrysuj_okres(wyniki_pomiaru,widmoPC,frq)
        
    
    if (opcje_pomiaru["Zapisz pomiar"]) : zapisDanych(wyniki_pomiaru,'pomiar')
    if (opcje_pomiaru["Zapisz widmo PC"]) : zapisDanych(widmoPC,'widmoPC')
    if (opcje_pomiaru["Zapisz widmo MCU"]) : zapisDanych(widmoMCU,'widmoMCU')
    ZamknijCOM(portCOM)
    return wynik
#-------------------------------------------------------------------------------------------
def ListaPortowCOM():
    porty = list(serial.tools.list_ports.comports())
    result = []
    for i in range( len( porty ) ):
        result.append( porty[i][0] )
    return result
#-------------------------------------------------------------------------------------------
def Generacja(czestotliwosc,przebieg):
    
    global PER_INT

    PER_INT,liczba_probek = DobierzPER(czestotliwosc)
    PER = PER_INT
    przebieg_string = KSZTALTY[przebieg] + KONCOWKA_LICZBA_PROBEK[liczba_probek]
    przebieg = PRZEBIEGI[przebieg_string]
    print("Rejestr timera : ",PER)
    ramka =  "G" + zamienNaZnaki(przebieg,PER,liczba_probek)
    NadajCOM(ramka)
#-------------------------------------------------------------------------------------------
def PomiarOkres(delay):
    delay = int(delay)
    ramka =  "P" + chr(POMIAR_FLAGI["POMIAR_OKRESOWY"]) + chr(delay)
    NadajCOM(ramka)
    dane = OdczytajPomiar()
    dane = dane.strip('$')
    dane = dane.split()
    napiecie = daneADCnaNapiecie(dane)
    return napiecie
#-------------------------------------------------------------------------------------------

def PomiarImp(delay):
    delay = int(delay)
    ramka =  "P" + chr(POMIAR_FLAGI["POMIAR_IMPULSOWY"]) + chr(delay)
    NadajCOM(ramka)
    dane = OdczytajPomiar()
    dane = dane.strip('$')
    dane = dane.split()
    napiecie = daneADCnaNapiecie(dane)
    return napiecie
#-------------------------------------------------------------------------------------------
def daneADCnaNapiecie(dane):
    dane = np.asarray(dane).astype('float64')
    napiecie = (dane/ ADC_MAX ) * ADC_VREF
    return napiecie
#-------------------------------------------------------------------------------------------
def WidmoMCU(harmoniczna,typ_pomiaru):
    ramka =  "W"+ chr(typ_pomiaru) + chr(harmoniczna)
    NadajCOM(ramka)
    dane = OdczytajPomiar()
    dane = dane.strip('$')
    dane = dane.split()
    return dane
#-------------------------------------------------------------------------------------------
def WidmoMultiSin(typ_pomiaru):
    for i in range (10):
        x = WidmoMCU(i+1,typ_pomiaru)
        widmo = funkcje.listUint2Float(x)
        print("WIDMO : ", widmo,"WIDMO [DB]", 20*np.log10(widmo))
#-------------------------------------------------------------------------------------------
def WidmoSinus(typ_pomiaru):
    x = WidmoMCU(1,typ_pomiaru)
    widmo = funkcje.listUint2Float(x)
    print("WIDMO : ", widmo,"WIDMO [DB]", 20*np.log10(widmo))
#-------------------------------------------------------------------------------------------
def WidmoSinc(typ_pomiaru):
    for i in range (10):
        x = WidmoMCU(i+1,typ_pomiaru)
        widmo = funkcje.listUint2Float(x)
        print("WIDMO : ", widmo,"WIDMO [DB]", 20*np.log10(widmo))
#-------------------------------------------------------------------------------------------
def DobierzPER(frq):
    if frq > max(F_MAX) : return -1 # blad!!!!
    for f_max in F_MAX:
        delta_f = f_max - frq
        indeks = F_MAX.index(f_max)
        if delta_f >=0 : break
    PER = ( F_CPU //( LICZBY_PROBEK[indeks] * frq ) ) - 1
    if PER < PER_MIN : PER = PER_MIN
    return PER,indeks
#-------------------------------------------------------------------------------------------
def PER_na_2_znaki(PER):
    PER = np.array([PER])
    PER = PER.astype('uint16')
    T1 = PER // 256 # STARSZY BAJT
    T1 = chr(T1)
    T2 = PER % 256  # MLODSZY BAJT
    T2 = chr(T2)
    PER_2_znaki = T1 + T2
    return PER_2_znaki
#-------------------------------------------------------------------------------------------
def zamienNaZnaki(przebieg,PER,liczba_probek):
    przebieg = chr(przebieg)
    PER = PER_na_2_znaki(PER)
    liczba_probek = chr(liczba_probek)

    ciag_znakow = przebieg + PER + liczba_probek
    
    return ciag_znakow

#-------------------------------------------------------------------------------------------
def NadajCOM(ramka):
    ramka = ramka + "$$$$"
    ramka_byte = bytearray()
    ramka_byte.extend(map(ord, ramka))
    port_szeregowy.write(ramka_byte)
    dane = port_szeregowy.read(len(ramka))
#-------------------------------------------------------------------------------------------
def OtworzCOM(portCOM):
    global port_szeregowy
    port_szeregowy = serial.Serial(port = portCOM,baudrate=BAUDRATE,parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=TIMEOUT)
    if port_szeregowy.isOpen() :
        #print(port_szeregowy.name + ' Pomyslnie otwarty! \n')
        return True
    else :
        return False
#-------------------------------------------------------------------------------------------
def OtworzPortCOM(portCOM):
    global port_szeregowy
    if ( len( portCOM ) > 0 ) : # jezeli port jest podany
        if (port_szeregowy == 0) : # 0 - poczatkowa wartosc zmiennej
            if( OtworzCOM(portCOM) ) : return True
            else : return False
        else :
            if port_szeregowy.isOpen() :
                print(port_szeregowy.name + ' Byl juz otwarty \n')
                return True
            else :
                print("Blad otwarcia portu : ", portCOM)
                port_szeregowy = 0
                return False
#-------------------------------------------------------------------------------------------
def ZamknijCOM(portCOM):
    global port_szeregowy
    try :
        port_szeregowy.close() # zamkniecie portu
    except :
        a = 5 # nic ;)
        #print()
    port_szeregowy = 0
    #print("Zamkniecie portu ",portCOM)
#-------------------------------------------------------------------------------------------
def OdczytajPomiar():
    licznik_znakow_terminacji = 0
    dane = []
    while(True): # odbieramy dane
        znak = port_szeregowy.read(1)   # odczyt 1 bajtu
        dane.append( znak )
        if znak == TERMINATOR :
            licznik_znakow_terminacji = licznik_znakow_terminacji + 1
            if licznik_znakow_terminacji == LICZBA_ZNAKOW_TERMINACJI : #odebrano wszystkie dane
                dane_string = ""
                #print("Liczba odebranych Bajtow: ",len(dane))
                for bajt in dane:
                    dane_string += bajt.decode()
                return dane_string
        else :
            licznik_znakow_terminacji = 0
#-------------------------------------------------------------------------------------------

def WczytajSlownikUszkodzenMultisin(nazwa_ukladu):

    slownik = {}
    
    #sprawdzenie lokalziacji:
    if os.getcwd() != SCIEZKA_DO_SLOWNIKOW :
        os.chdir(SCIEZKA_DO_SLOWNIKOW)
    # wejscie do katalogu z wybramym ukladem
    os.chdir(nazwa_ukladu+'/Slownik_Multisin')
    lista_plikow = os.listdir() # nazwy plikow oznaczaja sygnatury w slowniku
    for nazwa_pliku in lista_plikow:
        indeks_kropki = nazwa_pliku.find('.')
        sygnatura = nazwa_pliku[:indeks_kropki]
        slownik[sygnatura] = np.load(nazwa_pliku) # do slownika mozna dodawac nowe elementy w ten sposob
    
    # powrot do lokalizacji pierwotnej
    os.chdir(SCIEZKA_DO_SLOWNIKOW)
    return slownik
#-------------------------------------------------------------------------------------------

def ObliczWidmo(typ_widma,dane,PER):
    fs = F_CPU/(PER + 1) # czestotliwosc probkowania
    if typ_widma == 'FFT':
        n = len(dane) # length of the signal
        k = np.arange(n)
        frq = k * (fs/n) # czestotliwosc - widmo sie powiela!
        frq = frq[range(int(n/2))] # bierzemy tylko polowe, zeby nie powielac widma
        widmo = np.fft.fft(dane)/n # fft computing and normalization
        widmo = widmo[range(int(n/2))]
        widmo = abs(widmo)

    return widmo,frq
#-------------------------------------------------------------------------------------------

def zapisDanych(dane,etykieta_pliku):
    dane = np.asarray(dane)
    data = datetime.datetime.now()
    nazwa_pliku = etykieta_pliku + '_' + str( data.hour ) + '-' + str( data.minute )+ '-' + str( data.second )
    #sprawdzenie lokalziacji:
    if os.getcwd() != SCIEZKA_DO_SLOWNIKOW :
        os.chdir(SCIEZKA_DO_SLOWNIKOW)
    os.chdir('..') # przejscie katalog wyzej, do glownego katalogu programu
    if not(os.path.exists('Pomiary')):
        # jezeli folder nie istnieje tworzymy go
        os.mkdir('Pomiary')
    os.chdir('Pomiary')
    nazwa_katalogu_z_pomiarem = str(data.year) + '-' + str(data.month) + '-' + str(data.day)
    if not(os.path.exists(nazwa_katalogu_z_pomiarem)):
        # jezeli folder nie istnieje tworzymy go
        os.mkdir(nazwa_katalogu_z_pomiarem)
    os.chdir(nazwa_katalogu_z_pomiarem)
    np.save(nazwa_pliku,dane)
    os.chdir(SCIEZKA_DO_SLOWNIKOW) # powrot do pierwotnej lokalizacji
    
#-------------------------------------------------------------------------------------------

def odlegloscPuntuOdSlownika(slownik, punkt):
    d_min_slownik = {}
    for uszkodzenie in slownik:
        if uszkodzenie == "Nominalne":
            r = slownik["Nominalne"] - punkt
            d2 = np.dot(r,r)
            d = np.sqrt(d2)
            #print (uszkodzenie," : ",d)
            d_min_slownik[uszkodzenie] = d
        else :
            d_min = 10000
            for i in range(slownik[uszkodzenie].shape[0]):
                r = slownik[uszkodzenie][i] - punkt
                d2 = np.dot(r,r)
                d = np.sqrt(d2)
                if d < d_min : d_min = d
            #print (uszkodzenie," : ",d_min)
            d_min_slownik[uszkodzenie] = d_min

    return d_min_slownik
    
#-------------------------------------------------------------------------------------------
def SprawdzCzyStanNominalnyOdleglosc(nazwa_ukladu,punkt):
    """
    Sprawdzenie czy roznica miedzy punktem pomiarowym, a
    wyznaczonym w symulajci centrum jest na akzdej pozycji
    mniejsza niz 3 sigma
    """
    #sprawdzenie lokalziacji:
    if os.getcwd() != SCIEZKA_DO_SLOWNIKOW :
        os.chdir(SCIEZKA_DO_SLOWNIKOW)
    os.chdir(nazwa_ukladu)

    wartosc_srednia = np.load('wartosc_srednia.npy')
    sigma = np.load('odchylenie_std.npy')

    r = abs(wartosc_srednia - punkt) # modul roznicy wektorow

    r_len = np.sqrt( np.dot(r,r))
    sigma_len = np.sqrt( np.dot( sigma, sigma ))

    #a = r - 3*sigma # pomocniczy wektor

    #for delta in a: 
    #    if delta > 0 : # jezeli znajdziemy skladowa wektora poza obszarem 3 sigma, to punkt jest poza stanem nominalnym! -> a przynajmniej tak uwazam :)
    #        return False

    #return True

    if r_len >= 3 * sigma_len : return False
    else : return True
    
#-------------------------------------------------------------------------------------------

def KlasyfikacjaOdleglosc(slownik_odleglosci):
    d_min, etykieta = slownik_odleglosci['Nominalne'], 'Nominalne'
    for element in slownik_odleglosci:
        print(element,' : ',slownik_odleglosci[element])
        if slownik_odleglosci[element] < d_min :
            d_min, etykieta = slownik_odleglosci[element], element
    print("___________________________________________________")
    print("\n")

    return etykieta 
