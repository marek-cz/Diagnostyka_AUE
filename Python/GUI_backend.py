"""
MODUL ZAWIERAJACY BACK-END DO GUI
"""

import serial
import serial.tools.list_ports
import numpy as np
import funkcje
#-------------------------------------------------------------------------------------------
# stale
F_CPU = 32000000# 32 MHz
POMIAR_FLAGI = {"POMIAR_OKRESOWY": 1 ,"POMIAR_IMPULSOWY": 2 }
LICZBY_PROBEK = [500,250,100]
F_MAX = [2000,4000,10000]
LICZBA_PROBEK_f_MAX = [(1000,1000),(250,4000),(100,10000)]
PRZEBIEGI = {"SINUS_500_NR" : 0 , "SINUS_250_NR" : 1, "SINUS_100_NR" : 2,
             "PILA_1000_NR":3,"MULTI_SIN_500_NR" : 4, "MULTI_SIN_250_NR" : 5,
             "MULTI_SIN_100_NR" : 6, "SINC_500_NR" : 7,"SINC_250_NR" : 8,
             "SINC_100_NR" : 9}
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
#-------------------------------------------------------------------------------------------
# zmienne globalne
port_szeregowy = 0
#czestotliwosc = 1000
PER_INT = 31
wyniki_pomiaru = [1]
#-------------------------------------------------------------------------------------------

def Analiza(czestotliwosc,opoznienie, opcje_pomiaru, typ_pomiaru, portCOM):
    global wyniki_pomiaru
    print(typ_pomiaru)

    if (not (OtworzPortCOM(portCOM))) : return False # bledne otwarcie portu
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
    if (opcje_pomiaru["Wyrysuj dane"]) :
        ZamknijCOM(portCOM)
        funkcje.wyrysuj_okres(wyniki_pomiaru,PER_INT)
    ZamknijCOM(portCOM)
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
    print("Ramka generacji ", ramka.encode())
    NadajCOM(ramka)
#-------------------------------------------------------------------------------------------
def PomiarOkres(delay):
    delay = int(delay)
    #delay = delay // 10
    #if delay > 255 : delay = 255
    ramka =  "P" + chr(POMIAR_FLAGI["POMIAR_OKRESOWY"]) + chr(delay)
    NadajCOM(ramka)
    dane = OdczytajPomiar()
    dane = dane.strip('$')
    dane = dane.split()
    return dane
#-------------------------------------------------------------------------------------------

def PomiarImp(delay):
    delay = int(delay)
    #delay = delay // 10
    #if delay > 255 : delay = 255
    ramka =  "P" + chr(POMIAR_FLAGI["POMIAR_IMPULSOWY"]) + chr(delay)
    NadajCOM(ramka)
    dane = OdczytajPomiar()
    dane = dane.strip('$')
    dane = dane.split()
    return dane
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
    #print("Czestotliwosc: ",F_MAX[indeks])
    PER = ( F_CPU //( LICZBY_PROBEK[indeks] * frq ) ) - 1
    if PER < PER_MIN : PER = PER_MIN
    #print("Okres: ",PER)
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
    #port_szeregowy.write(ramka.encode())
    #port_szeregowy.write(ramka)
    #''.join(str(ord(c)) for c in s)
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
                #f = open("../../Pomiary/Pomiary_filtru/pomiary/pomiary.txt","a")
                #f.write(dane_string)
                #f.close()
                return dane_string
        else :
            licznik_znakow_terminacji = 0
