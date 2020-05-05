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
ADC_OFFSET = 160

POMIAR_FLAGI = {"POMIAR_OKRESOWY": 1 ,"POMIAR_IMPULSOWY": 2 }
LICZBY_PROBEK = [500,250,100]
F_MAX = [2000,4000,10000]
LICZBA_PROBEK_f_MAX = [(1000,1000),(250,4000),(100,10000)]
PRZEBIEGI = {"SINUS_500_NR" : 0 , "SINUS_250_NR" : 1, "SINUS_100_NR" : 2,"MULTI_SIN_500_NR" : 4, "SINC_500_NR" : 7}
KSZTALTY = ["SINUS","MULTI_SIN","SINC"]
KONCOWKA_LICZBA_PROBEK = ["_500_NR","_250_NR","_100_NR"]
TERMINATOR = '$'
# opcje transmisji
BAUDRATE = 115200
TIMEOUT = None
POMIAR_MULTISIN  = 1
POMIAR_IMPULSOWY = 2

PER_MIN = 31
PER_MAX = (np.power(2,16) - 1).astype('uint16')
PER_LICZBA_CYFR = 5 # 5 cyfr
DELAY_MAX = PER_MAX # roboczo :)

os.chdir('slowniki_uszkodzen')
SCIEZKA_DO_SLOWNIKOW = os.getcwd() # zapamietanie sciezki do slownikow uszkodzen
os.chdir('..')

#-------------------------------------------------------------------------------------------
# zmienne globalne
port_szeregowy = 0
PER_INT = 31
wyniki_pomiaru = [1,2,3,4,5,6,7,11,9]
widmoPC = np.array([])
widmoMCU = np.array([])
##slownik_uszkodzen_PCA2 = {} # zmienna globalna zawierajaca slownik uszkodzen
##slownik_uszkodzen_PCA3 = {} # zmienna globalna zawierajaca slownik uszkodzen
czestotliwosci_multisin = np.linspace(1,10,10) # raster czestotliwosci multisin
czestotliwosci_sinc = np.array([])


#-------------------------------------------------------------------------------------------

def Analiza(czestotliwosc,opoznienie, opcje_pomiaru, typ_pomiaru, typ_pomiaru_string , portCOM, nazwa_ukladu, liczba_skladowych_glownych):
    global wyniki_pomiaru
    global slownik_uszkodzen
    global widmoPC
    global widmoMCU
    global czestotliwosci_multisin
    global czestotliwosci_sinc


    czestotliwosci_sinc     = WczytanieCzestotliwosci(nazwa_ukladu, 'Sinc')
    czestotliwosci_multisin = WczytanieCzestotliwosci(nazwa_ukladu, 'Multisin')
    wynik = ''
    print(typ_pomiaru_string)
    #print(typ_pomiaru)
    print(liczba_skladowych_glownych)

    
    if (not (OtworzPortCOM(portCOM))) : return "COM fail" # bledne otwarcie portu
    if (opcje_pomiaru["Generacja"]) : Generacja(czestotliwosc,typ_pomiaru)
    if (opcje_pomiaru["Pomiar"]) :
        delay = int(opoznienie)
        if delay > DELAY_MAX : delay = DELAY_MAX
        
        if (typ_pomiaru == POMIAR_IMPULSOWY) :
            Generacja(czestotliwosc,2) # generujemy sinc'a
            wyniki_pomiaru = PomiarImp(delay)
        else : wyniki_pomiaru = PomiarOkres(delay)

        
        
    if (opcje_pomiaru["Widmo na MCU"]) :
        if (typ_pomiaru == POMIAR_IMPULSOWY) :
            widmoMCU = WidmoSinc(czestotliwosci_sinc)
        elif (typ_pomiaru == POMIAR_MULTISIN) :
            widmoMCU = WidmoMultiSin(czestotliwosc)
        else :
            widmoMCU = WidmoSinus(czestotliwosc)

    if (opcje_pomiaru["Diagnozuj"]) :
        widmoPC,frq = ObliczWidmo('FFT',wyniki_pomiaru,PER_INT)
        x = widmoPC[1:11] # na razie tak :)
        fi2, fi3 = wczytajMacierzPCA(nazwa_ukladu, typ_pomiaru_string )
        if liczba_skladowych_glownych == 3 : x = np.matmul(fi3, x)
        else : x = np.matmul(fi2, x) # domyslnie 2 skladowe glowne
        if SprawdzCzyStanNominalnyOdleglosc(nazwa_ukladu, x, liczba_skladowych_glownych, typ_pomiaru_string) :
            wynik = 'Nominalne'
        else :
            slownik_uszkodzen_PCA2, slownik_uszkodzen_PCA3 = WczytajSlownikiUszkodzen(nazwa_ukladu, typ_pomiaru_string ) 
            if liczba_skladowych_glownych == 3 : odleglosc_slownik = odlegloscPuntuOdSlownika(slownik_uszkodzen_PCA3,x)
            else : odleglosc_slownik = odlegloscPuntuOdSlownika(slownik_uszkodzen_PCA2,x) # domyslnie 2 skladowe glowne
##            odleglosc_slownik = odlegloscPuntuOdSlownika(slownik_uszkodzen_PCA2,x)
            wynik = KlasyfikacjaOdleglosc(odleglosc_slownik)
            
        
    ZamknijCOM(portCOM)
##    print(widmoPC[1:11])
    if (opcje_pomiaru["Zapisz pomiar"]) : zapisDanych(wyniki_pomiaru,'pomiar',nazwa_ukladu,typ_pomiaru_string)
    if (opcje_pomiaru["Zapisz widmo PC"]) :
        if (typ_pomiaru == POMIAR_IMPULSOWY) :
            widmoPC,frq = ObliczWidmo('TF',wyniki_pomiaru,PER_INT, czestotliwosci_sinc)
        else :
            widmoPC,frq = ObliczWidmo('FFT',wyniki_pomiaru,PER_INT)
            widmoPC = widmoPC[1:11]
        zapisDanych(widmoPC,'widmoPC',nazwa_ukladu,typ_pomiaru_string)
    if (opcje_pomiaru["Zapisz widmo MCU"]) : zapisDanych(widmoMCU,'widmoMCU',nazwa_ukladu,typ_pomiaru_string)
    return wynik
#-------------------------------------------------------------------------------------------
def WyrysujDane(typ_sygnalu):
    typ_pomiaru = ''
    
    if typ_sygnalu == 'Sinc' : typ_pomiaru = 'TF'
    else : typ_pomiaru = 'FFT'
    funkcje.plt.close('all') # zamkniecie wszystkich okien matplotlib
    widmoPC,frq = ObliczWidmo(typ_pomiaru , wyniki_pomiaru, PER_INT)
    funkcje.wyrysuj_okres(wyniki_pomiaru,widmoPC,frq, typ_pomiaru)

#-------------------------------------------------------------------------------------------
def WyrysujSlownik(nazwa_ukladu, liczba_skladowych_glownych , typ_slownika ,pomiary = False):

    slownik_uszkodzen_PCA2, slownik_uszkodzen_PCA3 = WczytajSlownikiUszkodzen(nazwa_ukladu, typ_slownika) # wczytanie domyslnego ukladu
    fi2, fi3 = wczytajMacierzPCA(nazwa_ukladu, typ_slownika)
    funkcje.plt.close('all') # zamkniecie wszystkich okien matplotlib
    p = 0
    if liczba_skladowych_glownych == 2: # wyrysowanie elipsy dla 2D
        wartosc_srednia, C1, s_graniczna = WczytajParametryElipsy(nazwa_ukladu,liczba_skladowych_glownych, typ_slownika)
        x, y = funkcje.wyznaczElipse(C1, s_graniczna, wartosc_srednia)
        funkcje.plt.plot(x,y, '-', label = 'OK', linewidth = 4)
    if pomiary : #and (type(p) is np.ndarray ): 
        p = WczytajPomiary(nazwa_ukladu, typ_slownika )
        if (type(p) is np.ndarray ):  # sprawdzenie czy sa pomiary
            p = np.transpose(p)
            if liczba_skladowych_glownych == 3: p = np.matmul( fi3, p )
            else :
                p = np.matmul( fi2, p ) # domyslnie 2 skladowe ;)
                funkcje.plt.plot(p[0],p[1],'ko',label = "Pomiar")
##    os.chdir(SCIEZKA_DO_SLOWNIKOW)
    if liczba_skladowych_glownych == 3:
        funkcje.wyrysujKrzyweIdentyfikacyjne3D(slownik_uszkodzen_PCA3, p)
    else : funkcje.wyrysujKrzyweIdentyfikacyjne2D(slownik_uszkodzen_PCA2)


#-------------------------------------------------------------------------------------------
def WczytajPomiary(nazwa_ukladu, typ_pomiaru_string):

    katalog = 'Multisin'
    if typ_pomiaru_string == 'Sinc' : katalog = 'Sinc'
    
    data = datetime.datetime.now()
    #sprawdzenie lokalizacji:
    if os.getcwd() != SCIEZKA_DO_SLOWNIKOW :
        os.chdir(SCIEZKA_DO_SLOWNIKOW)
    os.chdir('..') # przejscie katalog wyzej, do glownego katalogu programu
    if not(os.path.exists('Pomiary')): return 0 # jesli nie ma folderu z pomiarami, to nie ma czego rysowac
    os.chdir('Pomiary')
    nazwa_katalogu_z_pomiarem = nazwa_ukladu + '_' + str(data.year) + '-' + str(data.month) + '-' + str(data.day) + '/' + katalog
    if not(os.path.exists(nazwa_katalogu_z_pomiarem)):
        print("Nie ma katalogu")
        os.chdir(SCIEZKA_DO_SLOWNIKOW)
        return 0 # jesli nie ma folderu z pomiarami, to nie ma czego rysowac
    os.chdir(nazwa_katalogu_z_pomiarem)

    lista_plikow = os.listdir()
    pomiary = np.array([])

    for plik in lista_plikow:
        if plik.find('widmoPC') != -1 :
            pomiar = np.load(plik)
            pomiary = np.concatenate(( pomiary, pomiar) )
    pomiary = pomiary.reshape( ( pomiary.shape[0] // 10, 10 ) )

    os.chdir(SCIEZKA_DO_SLOWNIKOW)
    
    return pomiary
#-------------------------------------------------------------------------------------------

def ListaPortowCOM():
    porty = list(serial.tools.list_ports.comports())
    result = []
    for i in range( len( porty ) ):
        result.append( porty[i][0] )
    return result
#-------------------------------------------------------------------------------------------

def uint16NaStringa(uint16):
    if uint16 > PER_MAX : uint16 = PER_MAX # bezpieczenstwo!
    string = str(uint16)
    while ( PER_LICZBA_CYFR - len(string) > 0):
        string = '0' + string
    
    return string

#-------------------------------------------------------------------------------------------
def Generacja(czestotliwosc,przebieg):
    """
    Przebieg -> indeks w tablicy sinus - 0, multisin - 1, sinc - 2
    """
    global PER_INT

    if (przebieg != 0 ) : # jezeli NIE generujemy sinusa
        if czestotliwosc > F_MAX[0] : czestotliwosc = F_MAX[0] # zabezpieczenie, sinc i multisin do 2kHz -> 500 probek
    
    PER_INT,liczba_probek = DobierzPER(czestotliwosc)
    PER_string = uint16NaStringa(PER_INT)
    przebieg_string = KSZTALTY[przebieg] + KONCOWKA_LICZBA_PROBEK[liczba_probek]
    przebieg = PRZEBIEGI[przebieg_string]
    #ramka =  "G" + zamienNaZnaki(przebieg,PER,liczba_probek)
    ramka = 'G' + ' ' + str(przebieg) + ' ' + PER_string + ' ' + str(liczba_probek) + ' ' + TERMINATOR # pola sa ROZDZIELONE SPACJAMI!
    #print(ramka)
    NadajCOM(ramka)
#-------------------------------------------------------------------------------------------
def PomiarOkres(delay):
    #delay = int(delay)
    #ramka =  "P" + chr(POMIAR_FLAGI["POMIAR_OKRESOWY"]) + chr(delay)
    delay_string = uint16NaStringa(delay)
    ramka = 'P' + ' ' + str(POMIAR_FLAGI["POMIAR_OKRESOWY"]) + ' ' + delay_string + ' ' + TERMINATOR #pola rozdzielone spacjami
    #print(ramka)
    NadajCOM(ramka)
    dane = OdczytajPomiar()
    napiecie = daneADCnaNapiecie(dane)
    return napiecie
#-------------------------------------------------------------------------------------------

def PomiarImp(delay):
    #delay = int(delay)
    #ramka =  "P" + chr(POMIAR_FLAGI["POMIAR_IMPULSOWY"]) + chr(delay)
    delay_string = uint16NaStringa(delay)
    ramka = 'P' + ' ' + str(POMIAR_FLAGI["POMIAR_IMPULSOWY"]) + ' ' + delay_string + ' ' + TERMINATOR #pola rozdzielone spacjami
    #print(ramka)
    NadajCOM(ramka)
    dane = OdczytajPomiar()
    napiecie = daneADCnaNapiecie(dane)
    return napiecie
#-------------------------------------------------------------------------------------------
def daneADCnaNapiecie(dane):
    """
    dane - dane pomiarowe odebrane z XMEGI
    są rozdzielone spacjami i na koncu wystepuje znak terminacji
    """
    dane = dane.strip(TERMINATOR) # usuwamy znak terminacji
    dane = dane.split() # dzielimy dane po bialych znakach
    dane = np.asarray(dane).astype('float64')
    napiecie = ( (dane - ADC_OFFSET )/ ADC_MAX ) * ADC_VREF
    return napiecie
#-------------------------------------------------------------------------------------------
def WidmoMultiSin(czestotliwosc):
    indeksy = np.linspace(1,10,10)
    indeksy = indeksy.astype('uint16')
    widmo_tablica = np.array([])
    
    for k in indeksy:
        k_string = uint16NaStringa(k)
        ramka = 'F'+' '+ k_string + ' ' + TERMINATOR
        print(ramka)
        NadajCOM(ramka)
        dane = OdczytajPomiar()
        dane = dane.strip(TERMINATOR)
        dane = dane.split()
        widmo = funkcje.listUint2Float(dane)
        print(k * czestotliwosc," Hz widmo : ",widmo , " widmo [dB] :" , 20*np.log10(widmo) )
        widmo_tablica = np.concatenate( ( widmo_tablica, np.array([widmo]) ) )

    return widmo_tablica
#-------------------------------------------------------------------------------------------
def WidmoSinus(czestotliwosc_podstawowa):
    f = np.array([czestotliwosc_podstawowa])
    widmo = WidmoMultiSin(f)

    return widmo
#-------------------------------------------------------------------------------------------
def WidmoSinc(tablica_czestotliwosci):
    #frq = tablica_czestotliwosci // czestotliwosc_podstawowa
    frq = tablica_czestotliwosci
    frq = frq.astype('uint16')
    widmo_tablica = np.array([])

    for f in frq:
        f_string = uint16NaStringa(f)
        ramka = 'T'+' '+ f_string + ' ' + TERMINATOR
        print(ramka)
        NadajCOM(ramka)
        dane = OdczytajPomiar()
        dane = dane.strip(TERMINATOR)
        dane = dane.split()
        widmo = funkcje.listUint2Float(dane)
        print(f,". widmo : ",widmo , " widmo [dB] :" , 20*np.log10(widmo) )
        widmo_tablica = np.concatenate( ( widmo_tablica, np.array([widmo]) ) )

    return widmo_tablica
#-------------------------------------------------------------------------------------------
def DobierzPER(frq):
    if frq > max(F_MAX) : frq = max(F_MAX) # blad!!!!
    for f_max in F_MAX:
        delta_f = f_max - frq
        indeks = F_MAX.index(f_max)
        if delta_f >=0 : break
    PER = ( F_CPU //( LICZBY_PROBEK[indeks] * frq ) ) - 1
    if PER < PER_MIN : PER = PER_MIN
    if PER > PER_MAX : PER = PER_MAX
    return PER,indeks
#-------------------------------------------------------------------------------------------

def NadajCOM(ramka):
    port_szeregowy.write(ramka.encode()) # nadajemy dane
    dane = port_szeregowy.read(len(ramka)) # uklad odpowiada ta sama sekwencja
    print(dane.decode())
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
    """
    Odbiera dane az do znaku terminacji
    """
    dane = []
    dane_string = ''
    while(True): # odbieramy dane
        znak = port_szeregowy.read(1)   # odczyt 1 bajtu
        dane.append( znak )
        if znak.decode() == TERMINATOR :
            for bajt in dane:
                dane_string += bajt.decode() # dekoduje dane z binarnych na stringa
            return dane_string
#-------------------------------------------------------------------------------------------

def WczytajSlownikiUszkodzen(nazwa_ukladu,typ_slownika):

    slownik_PCA2 = {}
    slownik_PCA3 = {}
    
    #sprawdzenie lokalziacji:
    if os.getcwd() != SCIEZKA_DO_SLOWNIKOW :
        os.chdir(SCIEZKA_DO_SLOWNIKOW)
    # wejscie do katalogu ze slownikami
    if typ_slownika == 'Sinc' : os.chdir(nazwa_ukladu+'/Slowniki_Sinc')
    else : os.chdir(nazwa_ukladu+'/Slowniki_Multisin')
    os.chdir('Slownik_PCA_2')
    lista_plikow = os.listdir() # nazwy plikow oznaczaja sygnatury w slowniku
    for nazwa_pliku in lista_plikow:
        indeks_kropki = nazwa_pliku.find('.')
        sygnatura = nazwa_pliku[:indeks_kropki]
        slownik_PCA2[sygnatura] = np.load(nazwa_pliku) # do slownika mozna dodawac nowe elementy w ten sposob

    os.chdir('../Slownik_PCA_3')

    lista_plikow = os.listdir() # nazwy plikow oznaczaja sygnatury w slowniku
    for nazwa_pliku in lista_plikow:
        indeks_kropki = nazwa_pliku.find('.')
        sygnatura = nazwa_pliku[:indeks_kropki]
        slownik_PCA3[sygnatura] = np.load(nazwa_pliku) # do slownika mozna dodawac nowe elementy w ten sposob
    
    # powrot do lokalizacji pierwotnej
    os.chdir(SCIEZKA_DO_SLOWNIKOW)
    
    return slownik_PCA2, slownik_PCA3
#-------------------------------------------------------------------------------------------
def wczytajMacierzPCA(nazwa_ukladu, typ_slownika):
    #sprawdzenie lokalziacji:
    if os.getcwd() != SCIEZKA_DO_SLOWNIKOW :
        os.chdir(SCIEZKA_DO_SLOWNIKOW)

    if typ_slownika == 'Sinc' : os.chdir(nazwa_ukladu+'/Slowniki_Sinc')
    else : os.chdir(nazwa_ukladu+'/Slowniki_Multisin')
##    os.chdir(nazwa_ukladu+'/Slowniki_Multisin')

    fi2 = np.load('PCA_2_SKL.npy')
    fi3 = np.load('PCA_3_SKL.npy')

    os.chdir(SCIEZKA_DO_SLOWNIKOW)
    
    return fi2, fi3
    
#-------------------------------------------------------------------------------------------

def ObliczWidmo(typ_widma,dane,PER, czestotliwosci = np.array([0])):
    fs = F_CPU/(PER + 1) # czestotliwosc probkowania
    n = len(dane) # length of the signal
    if typ_widma == 'TF':
        Ts = 1/fs
        T = n * Ts
        t = np.linspace(0,1,n) * T
        if czestotliwosci[0] ==0  : frq = np.linspace( (1/T), 100 * (1/T), 1000 )
        else : frq = czestotliwosci
        (ReU,ImU) = funkcje.TransformataFourieraSinc(dane, t, frq)
        widmo = np.sqrt( ReU*ReU + ImU*ImU )
    else : # domyslnie FFT
        k = np.arange(n)
        frq = k * (fs/n) # czestotliwosc - widmo sie powiela!
        frq = frq[range(int(n/2))] # bierzemy tylko polowe, zeby nie powielac widma
        widmo = np.fft.fft(dane)/n # fft computing and normalization
        widmo = widmo[range(int(n/2))]
        widmo = abs(widmo)

    return widmo,frq
#-------------------------------------------------------------------------------------------

def zapisDanych(dane,etykieta_pliku,nazwa_ukladu, typ_pomiaru_string):
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
    nazwa_katalogu_z_pomiarem = nazwa_ukladu + '_' + str(data.year) + '-' + str(data.month) + '-' + str(data.day)
    if not(os.path.exists(nazwa_katalogu_z_pomiarem)):
        # jezeli folder nie istnieje tworzymy go
        os.mkdir(nazwa_katalogu_z_pomiarem)
    os.chdir(nazwa_katalogu_z_pomiarem)

    katalog = 'Multisin'
    if typ_pomiaru_string == 'Sinc' : katalog = 'Sinc'

    if not(os.path.exists(katalog)):
        # jezeli folder nie istnieje tworzymy go
        os.mkdir(katalog)
    os.chdir(katalog)
    
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
def SprawdzCzyStanNominalnyOdleglosc(nazwa_ukladu,punkt, liczba_skladowych_glownych, typ_slownika):
    """
    Sprawdzenie czy odleglosc Mahalanobisa miedzy punktem pomiarowym, a
    wyznaczonym w symulajci centrum jest mniejsza od wartosci granicznej
    """


    wartosc_srednia, C1, s_graniczna = WczytajParametryElipsy(nazwa_ukladu, liczba_skladowych_glownych, typ_slownika)
    s = odlegloscMahalanobisa(punkt, wartosc_srednia, C1)

    os.chdir(SCIEZKA_DO_SLOWNIKOW) # powrot do pierwotnej lokalizacji
    
    if ( s < s_graniczna ) : return True
    else : return False

#-------------------------------------------------------------------------------------------
def WczytajParametryElipsy(nazwa_ukladu, liczba_skladowych_glownych, typ_slownika):
    #sprawdzenie lokalziacji:
    if os.getcwd() != SCIEZKA_DO_SLOWNIKOW :
        os.chdir(SCIEZKA_DO_SLOWNIKOW)

    
    if typ_slownika == 'Sinc' : os.chdir(nazwa_ukladu+'/Slowniki_Sinc')
    else : os.chdir(nazwa_ukladu+'/Slowniki_Multisin')

    wartosc_srednia, C1, s_graniczna = 0,0,0 # inicjalizacja zmiennych
    
    if liczba_skladowych_glownych == 3 :
        wartosc_srednia = np.load('srodek_PCA_3_skladowe.npy')
        C1 = np.load('macierz_skalujaca_PCA_3_skladowe.npy')
        s_graniczna = np.load('graniczna_odleglosc_PCA_3_skladowe.npy')
    else : # domyslnie 2 skladowe
        wartosc_srednia = np.load('srodek_PCA_2_skladowe.npy')
        C1 = np.load('macierz_skalujaca_PCA_2_skladowe.npy')
        s_graniczna = np.load('graniczna_odleglosc_PCA_2_skladowe.npy')


    os.chdir(SCIEZKA_DO_SLOWNIKOW) # powrot do lokalizacji
    
    return wartosc_srednia, C1, s_graniczna
    
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
#-------------------------------------------------------------------------------------------
def odlegloscMahalanobisa(x,y,C):
    """
    Odleglosc Mahalanobisa miedzy punktami x i y
    z zastosowaniem macierzy skalujacej C
    """
    x = x.reshape((x.shape[0],1)) # wektor kolumnowy
    y = y.reshape((y.shape[0],1)) # wektor kolumnowy
    d = x - y
    s = np.matmul(np.transpose(d), C)
    s = np.matmul( s , d)
    return np.sqrt(s)


#-------------------------------------------------------------------------------------------
def g(x,c1,c2):
    a = c2 - c1
    r = x - c1
    return (np.dot(a,r) / np.dot(a,a))
#-------------------------------------------------------------------------------------------
def h(g_od_x):
    if g_od_x <= 0 : return 0
    if g_od_x >= 1 : return 1
    return g_od_x
#-------------------------------------------------------------------------------------------
def DRB(x,c1,c2,s1,s2):
    g_od_x = g(x,c1,c2)
    w = c1 + (c2-c1) * h(g_od_x) # (c2 - c1) = a (5.11)
    s = s1
    if s2 > s : s = s2 # wybieramy wieksze std
    r = x - w # pomocniczy wektor
    exp_arg = ( (-1) / (2*s*s) ) * np.dot(r,r)
    return np.exp(exp_arg)

#-------------------------------------------------------------------------------------------
def wczytaj_slownik_std(nazwa_ukladu, liczba_skladowych_glownych, typ_sygnalu):

    koncowka = ''
    if typ_sygnalu == 'Sinc' : koncowka = 'Sinc'
    else : koncowka = 'Multisin'
    
    nazwa_katalogu = nazwa_ukladu + '/Slowniki_' + koncowka + '/std_PCA' + str(liczba_skladowych_glownych)
    
    os.chdir(SCIEZKA_DO_SLOWNIKOW + '/' + nazwa_katalogu)

##    print(os.getcwd())
    
    slownik_std = {}
    lista_plikow = os.listdir()
    for nazwa_pliku in lista_plikow:
        indeks_kropki = nazwa_pliku.find('.')
        sygnatura = nazwa_pliku[:indeks_kropki]
        slownik_std[sygnatura] = np.load(nazwa_pliku) # do slownika mozna dodawac nowe elementy w ten sposob

    os.chdir(SCIEZKA_DO_SLOWNIKOW)
    return slownik_std
#-------------------------------------------------------------------------------------------
def KlasyfikacjaDRB(slownik_uszkodzen, pomiar, slownik_odchylen_std):
    slownik_wynikow = {}
    klucze = list(slownik_uszkodzen.keys())
    liczba_punktow = 0
    for klucz in klucze :
        if klucz != 'Nominalne':
            liczba_punktow = slownik_uszkodzen[klucz].shape[0]
            break
    
    for uszkodzenie in slownik_uszkodzen:
        if uszkodzenie == 'Nominalne' : continue # klasyfikacja uszkodzenia -> stwierdzono juz ze uklad jest uszkodzony
        slownik_wynikow[uszkodzenie] = 0
        for i in range(liczba_punktow - 1):
            c1 = slownik_uszkodzen[uszkodzenie][i]
            c2 = slownik_uszkodzen[uszkodzenie][i+1]
            s1 = slownik_odchylen_std[uszkodzenie][i]
            s2 = slownik_odchylen_std[uszkodzenie][i+1]
            wynik = DRB(pomiar,c1,c2,s1,s1)
            if wynik > slownik_wynikow[uszkodzenie] : slownik_wynikow[uszkodzenie] = wynik
    return slownik_wynikow
###############################################################################################################################
#-------------------------------------------------------------------------------------------
def WczytanieCzestotliwosci(nazwa_ukladu, typ_slownika):
    #sprawdzenie lokalziacji:
    if os.getcwd() != SCIEZKA_DO_SLOWNIKOW :
        os.chdir(SCIEZKA_DO_SLOWNIKOW)

    if typ_slownika == 'Sinc' : os.chdir(nazwa_ukladu+'/Slowniki_Sinc')
    else : os.chdir(nazwa_ukladu+'/Slowniki_Multisin')

    f = np.load("f.npy")

    os.chdir(SCIEZKA_DO_SLOWNIKOW)
    
    return f
