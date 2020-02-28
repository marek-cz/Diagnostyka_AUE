"""MODUL DO OBSLUGI PORTU SZEREGOWEGO - WYSYLANIE POLECEN DO XMEGA"""


import serial
import time
import serial.tools.list_ports
import funkcje


####################################################################
# stale
F_CPU = 32000000# 32 MHz
POMIAR_FLAGI = {"POMIAR_OKRESOWY": 1 ,"POMIAR_IMPULSOWY": 2 }
LICZBY_PROBEK = [1000,250,100]
F_MAX = [1000,4000,10000]
LICZBA_PROBEK_f_MAX = [(1000,1000),(250,4000),(100,10000)]
PRZEBIEGI = {"SINUS_1000_NR" : 0 , "SINUS_250_NR" : 1, "SINUS_100_NR" : 2,
             "PILA_1000_NR":3,"MULTI_SIN_1000_NR" : 4, "MULTI_SIN_250_NR" : 5,
             "MULTI_SIN_100_NR" : 6, "SINC_1000_NR" : 7,"SINC_250_NR" : 8,
             "SINC_100_NR" : 9}
KSZTALTY = ["SINUS","PILA","MULTI_SIN","SINC"]
KONCOWKA_LICZBA_PROBEK = ["_1000_NR","_250_NR","_100_NR"]
TERMINATOR = b'\x24'
TERMINATOR_STRING = '$$$$'
LICZBA_ZNAKOW_TERMINACJI = 4
####################################################################
# zmienne globalne
czestotliwosc = 1000
PER_INT = 31
####################################################################
def PER_na_2_znaki(PER):
    T1 = PER // 256 # STARSZY BAJT
    T1 = chr(T1)
    T2 = PER % 256  # MLODSZY BAJT
    T2 = chr(T2)
    PER_2_znaki = T1 + T2
    return PER_2_znaki
####################################################################
def zamienNaZnaki(przebieg,PER,liczba_probek):
    przebieg = chr(przebieg)
    PER = PER_na_2_znaki(PER)
    liczba_probek = chr(liczba_probek)

    ciag_znakow = przebieg + PER + liczba_probek
    
    return ciag_znakow
####################################################################
def DopasowanieCzest(frq):
    delta_f = []

    for N in LICZBY_PROBEK:
        PER = (F_CPU//(N * frq)) - 1
        if PER < 31 : f = -100000
        else : f = F_CPU/(N * ( PER + 1 ) )
        delta_f.append(f)
    for i in range(len(delta_f)):
        delta_f[i] = abs(delta_f[i])
    indeks_min = delta_f.index( min( delta_f ) )
    PER = ( F_CPU //( LICZBY_PROBEK[indeks_min] * frq ) ) - 1
    
    return (PER, indeks_min )
####################################################################
def DobierzPER(frq):
    if frq > max(F_MAX) : return -1 # blad!!!!
    for f_max in F_MAX:
        delta_f = f_max - frq
        indeks = F_MAX.index(f_max)
        if delta_f >=0 : break

    PER = ( F_CPU //( LICZBY_PROBEK[indeks] * frq ) ) - 1

    return PER,indeks
        
####################################################################
def GeneracjaDopCzest():
    print("GeneracjaDopCzest")
    przebieg = int(input("\nWybierz przebieg\n"))
    czestotliwosc = int(input("\nPodaj czestotliwosc [Hz]\n"))
    PER,liczba_probek = DopasowanieCzest(czestotliwosc)
    
    ramka =  "G" + zamienNaZnaki(przebieg,PER,liczba_probek)
    NadajCOM(ramka)
    return True
####################################################################
def GeneracjaMaxProb():
    global czestotliwosc
    global PER_INT
    print("GeneracjaMaxProb")
    for i in range( len( KSZTALTY ) ):
        print(i,". ",KSZTALTY[i])
    przebieg = int(input("\nWybierz przebieg\n"))
    czestotliwosc = int(input("\nPodaj czestotliwosc [Hz]\n"))

    PER_INT,liczba_probek = DobierzPER(czestotliwosc)
    PER = PER_INT
    przebieg_string = KSZTALTY[przebieg] + KONCOWKA_LICZBA_PROBEK[liczba_probek]
    przebieg = PRZEBIEGI[przebieg_string]

    print(przebieg,PER,liczba_probek)

    ramka =  "G" + zamienNaZnaki(przebieg,PER,liczba_probek)
    NadajCOM(ramka)
    return True

####################################################################
def PomiarOkres():
    print("Pomiar Okresowy")
    delay = int(input("\nPodaj opóźnienie (x10ms)\n"))
    if delay > 255 : delay = 255
    ramka =  "P" + chr(POMIAR_FLAGI["POMIAR_OKRESOWY"]) + chr(delay)
    NadajCOM(ramka)
    dane = OdczytajPomiar()
    dane = dane.strip('$')
    dane = dane.split()
    #dane.remove(TERMINATOR_STRING)
    print(dane)
    funkcje.wyrysuj_okres(dane,PER_INT)
    return True
####################################################################
def PomiarImp():
    print("Pomiar Impulsowy")
    delay = int(input("\nPodaj opóźnienie (x10ms)\n"))
    if delay > 255 : delay = 255
    ramka =  "P" + chr(POMIAR_FLAGI["POMIAR_IMPULSOWY"]) + chr(delay)
    NadajCOM(ramka)
    dane = OdczytajPomiar()
    dane = dane.strip('$')
    dane = dane.split()
    #dane.remove(TERMINATOR_STRING)
    print(dane)
    funkcje.wyrysuj_okres(dane,PER_INT)
    return True
####################################################################
def Widmo():
    print("Widmo")
    return True
####################################################################
def Wyjscie():
    print("Wyjscie")
    return False
####################################################################
def NadajCOM(ramka):
    ramka = ramka + "$$$$"
    print("długosc ramki ", len(ramka))
    print("\n",ramka,"\n",ramka.encode(),"\n")
    port_szeregowy.write(ramka.encode())
    dane = port_szeregowy.read(len(ramka))
    print('\n\n\n')
    print(dane)
    print('\n\n\n')
####################################################################
def WyborPortuCOM():
    ports = list(serial.tools.list_ports.comports())
    if len(ports) != 0 :
        print("Wybierz port COM: \n")
        # wypisanie portow COM
        for i in range( len( ports ) ):
            print(i,". ",ports[i])
        port = int( input( "\n" ) )
        return ports[port][0]
    else:
        print("Nie ma dostepnych portow!\n")
        return 0
####################################################################
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
                print("Liczba odebranych Bajtow: ",len(dane))
                for bajt in dane:
                    dane_string += bajt.decode()
                return dane_string
        else :
            licznik_znakow_terminacji = 0
        
####################################################################
menu1 = """Co chcesz zrobic?
1. Generacja - dopasowane czestotliwosc
2. Generacja - maksymalna liczba probek
3. Pomiar Okresowy
4. Pomiar Impulsowy
5. Widmo
6. Wyjsc
"""

slownik_funkcji = {'1':GeneracjaDopCzest,'2':GeneracjaMaxProb,'3':PomiarOkres, '4':PomiarImp ,'5': Widmo,'6' : Wyjscie}
#input()        # BREAKPOINT
iteracje = True
portCOM = WyborPortuCOM()
if ( portCOM != 0) :

    port_szeregowy = serial.Serial(port = portCOM,baudrate=9600,parity=serial.PARITY_NONE,
                               stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=None)
    if port_szeregowy.isOpen():
         print(port_szeregowy.name + ' is open...')

else :
    iteracje = False
    print("Podlacz urzadzenie!")

while(iteracje):
    decyzja = input(menu1)
    iteracje = slownik_funkcji[decyzja]() # funkcje zwracaja warunek kontynuacji petli
    

if ( portCOM != 0) :
    port_szeregowy.close() # zamkniecie portu
    print("Zamkniecie portu ",portCOM)
