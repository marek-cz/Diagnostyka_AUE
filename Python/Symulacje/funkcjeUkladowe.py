"""

MODUL Z FUNKCJAMI UKLADOWYMI -> UNIWERSALNY DO BADANIA DOWOLNEGO UKLADU

"""
#------------------------------------------------------------------------------
import copy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy import linalg
import os
import sygnaly

os.chdir('uklady')
lista_ukladow = os.listdir()
print("Wybierz układ: \n")

i = 0
for uklad in lista_ukladow:
    indeks_kropki = uklad.find('.')
    nazwa_ukladu = uklad[:indeks_kropki]
    i = i + 1
    print(i,". ",nazwa_ukladu)

indeks = int( input("Podaj numer ukladu : ") )
nazwa = lista_ukladow[indeks-1]

os.system('copy ' + nazwa + " uklad.py")

os.chdir('..')
sciezka_dest = os.getcwd() + '\\uklad.py'
os.chdir('uklady')
sciezka_src = os.getcwd()  + '\\uklad.py'
os.replace(sciezka_src,sciezka_dest)

import uklad

plt.rc('axes', labelsize = 14)
plt.rc('xtick', labelsize=12)
plt.rc('ytick', labelsize=12)


PROG_GORNY_PROCENTY = 150
PROG_DOLNY_PROCENTY = 50
ODSTEP_OD_WAR_NOMINALNEJ_PROCENTY = 5
WARTOSC_NOMINALNA_PROCENTY = 100

F_CPU = 32e6
LICZBA_PROBEK = 500

PER = (F_CPU//(LICZBA_PROBEK*uklad.BADANE_CZESTOTLIWOSCI[0])) - 1 # wartosc rejestru PER
F_ZNORMALIZOWANE = uklad.BADANE_CZESTOTLIWOSCI / uklad.BADANE_CZESTOTLIWOSCI[0]
uklad.BADANE_CZESTOTLIWOSCI[0] = F_CPU / (LICZBA_PROBEK * (PER+1)) # dopasowanie do faktycznie generowanej przez DAC czesttoliwosci
uklad.BADANE_CZESTOTLIWOSCI = F_ZNORMALIZOWANE * uklad.BADANE_CZESTOTLIWOSCI[0]

#------------------------------------------------------------------------------
def charCzestotliwosciowaModul(licznik_transmitancji,mianownik_transmitancji,f):
    f = np.asarray(f)
    w = 2*np.pi*f
    potegi_w_liczniku = np.arange(len(licznik_transmitancji)-1,-1,-1)
    #print(potegi_w_liczniku)
    potegi_w_mianowniku = np.arange(len(mianownik_transmitancji)-1,-1,-1)
    char_czest_licznik = 0
    char_czest_mianownik = 0
    for i in range(len(licznik_transmitancji)):
        char_czest_licznik += np.power((w*(1j)), potegi_w_liczniku[i] ) * licznik_transmitancji[i]
        #print(char_czest_licznik)
    for i in range(len(mianownik_transmitancji)):
        char_czest_mianownik += np.power((w*(1j)), potegi_w_mianowniku[i] ) * mianownik_transmitancji[i]
        #print(char_czest_mianownik)

    modul = abs(char_czest_licznik/char_czest_mianownik)
    # NORMALIZACJA!
    #modul /= modul.max()
    return modul

#------------------------------------------------------------------------------
def monteCarlo(elementy_wykluczone_z_losowania = [],elementy = uklad.elementy,czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI,tolerancja = uklad.TOLERANCJA,liczba_losowanMC = uklad.LICZBA_LOSOWAN_MC):
    """
    DLA ZADANYCH WARTOSCI ELEMENTOW GENERUJEMY MACIERZ DANYCH
    WOKOL PUNKTU NOMINALNEGO - KLASTER/OBSZAR TOLERANCJI
    ZWRACA MACIERZ W KTOREJ KAZDY WIERSZ JEST PUNKTEM POMIAROWYM,
    WIERSZ 0 TO PUNKT NMOMINALNY
    """
    elementy_modyfikacje = copy.deepcopy( elementy )
    czestotliwosci = np.asarray(czestotliwosci)
    liczba_czestotliwosci = czestotliwosci.shape[0]
    #L = 1 - tolerancja
    #H = 1 + tolerancja
    
    liczba_wierszy = liczba_losowanMC + 1 # tyle punktow pomiarowych ile jest losowan. +1 bo wiersz 0 to punkt nominalny
    liczba_kolumn = liczba_czestotliwosci
    
    klaster = np.zeros( ( liczba_wierszy , liczba_kolumn ) )
    l, m = uklad.transmitancja(elementy)
    klaster[0] = charCzestotliwosciowaModul(l, m,czestotliwosci)
    #################################################################################
    #           LOSOWANIE MONTECARLO
    #################################################################################
    licznik = 1
    for i in range(liczba_losowanMC): # MonteCarlo
        for element in elementy_modyfikacje: # tolerancje
            if element in elementy_wykluczone_z_losowania :
                #print("\n\nTen element nie jest losowany: ",element,"\n\n")
                elementy_modyfikacje[element] = elementy[element]
            else :
                if element.find('R') != -1 :
                    # gdy element jest rezystorem
                    L = 1 - tolerancja['R']
                    H = 1 + tolerancja['R']
                    elementy_modyfikacje[element] = elementy[element] * (np.random.uniform(L,H))
                elif element.find('C') != -1 :
                    # gdy element jets kondensatorem :
                    L = 1 - tolerancja['C']
                    H = 1 + tolerancja['C']
                    elementy_modyfikacje[element] = elementy[element] * (np.random.uniform(L,H))
                else :
                    print("Czegoś nie uwzględniłeś! : ",element)
                #print(element," : ",elementy_modyfikacje[element])
        #print(elementy_modyfikacje)
        l, m = uklad.transmitancja(elementy_modyfikacje)
        klaster[licznik] = charCzestotliwosciowaModul(l, m,czestotliwosci)
        licznik = licznik +  1
    return klaster
#------------------------------------------------------------------------------
def tolerancjaElementu(element,tolerancja):
    if element.find('R') != -1 :
        # gdy element jest rezystorem
        L = 1 - tolerancja['R']
        H = 1 + tolerancja['R']
    elif element.find('C') != -1 :
        L = 1 - tolerancja['C']
        H = 1 + tolerancja['C']
    else :
        print("Czegoś nie uwzględniłeś! : ",element)
    return L,H   
#------------------------------------------------------------------------------
def analizaWorstCase(sygnal,elementy = uklad.elementy,czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI,tolerancja = uklad.TOLERANCJA):
    widmo_sygnalu = sygnaly.widmo(sygnal,czestotliwosci)
    elementy_modyfikacje = copy.deepcopy( elementy )
    wynik = np.array([])
    lista_elementow = list(elementy.keys())
    liczba_elementow_slownika = len( lista_elementow )
    licznik = 0
    liczba_przypadkow = np.power(2,liczba_elementow_slownika)
    
    for element in elementy_modyfikacje : # ustawienie wszystkich elementow na minimalna wartosc
        if element.find('R') != -1 :
            # gdy element jest rezystorem
            L = 1 - tolerancja['R']
            elementy_modyfikacje[element] = elementy[element] * L
        elif element.find('C') != -1 :
            # gdy element jets kondensatorem :
            L = 1 - tolerancja['C']
            elementy_modyfikacje[element] = elementy[element] * L
        else :
            print("Czegoś nie uwzględniłeś! : ",element)
    # mamy 2^n przypadkow - idziemy przez nie binarnie ;)
    while (licznik < liczba_przypadkow):
        licznik_string = "{0:b}".format(licznik)
        pad = '' # uzupelniamy zerami z przodu
        for i in range(liczba_elementow_slownika - len(licznik_string)):
            pad += '0'
        licznik_string = pad + licznik_string
        
        licznik_elementow = 0
        for element in lista_elementow:
            L,H = tolerancjaElementu(element,tolerancja)
            if licznik_string[licznik_elementow] == '1' :
                elementy_modyfikacje[element] = elementy[element] * H
            else :
                elementy_modyfikacje[element] = elementy[element] * L
            licznik_elementow += 1

        # symulacja:
        l,m = uklad.transmitancja(elementy_modyfikacje)
        symulacja = charCzestotliwosciowaModul(l,m,czestotliwosci) * widmo_sygnalu
        wynik = np.concatenate((wynik, symulacja))
        licznik += 1

    wynik = wynik.reshape((liczba_przypadkow, wynik.shape[0]//liczba_przypadkow ))
    
    return wynik
    
        
#------------------------------------------------------------------------------
def generujWartosciElementowZnormalizowane(liczba_punktow_na_element):

    liczba_punktow_plus = liczba_punktow_minus = (liczba_punktow_na_element//2) + 1
    #tolerancja = tolerancja * 100 # procenty!
    delta_minus = (WARTOSC_NOMINALNA_PROCENTY - ODSTEP_OD_WAR_NOMINALNEJ_PROCENTY - PROG_DOLNY_PROCENTY) / liczba_punktow_minus
    delta_plus = (PROG_GORNY_PROCENTY - (WARTOSC_NOMINALNA_PROCENTY + ODSTEP_OD_WAR_NOMINALNEJ_PROCENTY)) / liczba_punktow_plus
    
    wartosci_elementu_znormalizowane_minus = np.arange(PROG_DOLNY_PROCENTY,WARTOSC_NOMINALNA_PROCENTY - ODSTEP_OD_WAR_NOMINALNEJ_PROCENTY + delta_minus ,delta_minus)
    indeks_ostatniego_elementu = int(wartosci_elementu_znormalizowane_minus.shape[0]-1)
    if wartosci_elementu_znormalizowane_minus[indeks_ostatniego_elementu] > (WARTOSC_NOMINALNA_PROCENTY - ODSTEP_OD_WAR_NOMINALNEJ_PROCENTY) :
        wartosci_elementu_znormalizowane_minus = np.delete(wartosci_elementu_znormalizowane_minus,indeks_ostatniego_elementu)
    indeks_ostatniego_elementu = int(wartosci_elementu_znormalizowane_minus.shape[0]-1)
    if ((WARTOSC_NOMINALNA_PROCENTY - ODSTEP_OD_WAR_NOMINALNEJ_PROCENTY) - wartosci_elementu_znormalizowane_minus[indeks_ostatniego_elementu]) > 1 : # arbitralnie przyjeta wartosc
        wartosci_elementu_znormalizowane_minus = np.concatenate( (wartosci_elementu_znormalizowane_minus,np.array([WARTOSC_NOMINALNA_PROCENTY - ODSTEP_OD_WAR_NOMINALNEJ_PROCENTY])) )
##################################################################################################################################################################
    wartosci_elementu_znormalizowane_plus = np.arange(WARTOSC_NOMINALNA_PROCENTY + ODSTEP_OD_WAR_NOMINALNEJ_PROCENTY, PROG_GORNY_PROCENTY + delta_plus ,delta_plus)
    indeks_ostatniego_elementu = int(wartosci_elementu_znormalizowane_plus.shape[0]-1)
    
    if wartosci_elementu_znormalizowane_plus[indeks_ostatniego_elementu] > (PROG_GORNY_PROCENTY) :
        wartosci_elementu_znormalizowane_plus = np.delete(wartosci_elementu_znormalizowane_plus, indeks_ostatniego_elementu)
    indeks_ostatniego_elementu = int(wartosci_elementu_znormalizowane_plus.shape[0]-1)
    if (PROG_GORNY_PROCENTY - wartosci_elementu_znormalizowane_plus[indeks_ostatniego_elementu]) > 1 : # arbitralnie przyjeta wartosc
        wartosci_elementu_znormalizowane_plus = np.concatenate( (wartosci_elementu_znormalizowane_plus,np.array([PROG_GORNY_PROCENTY])) )

    return (wartosci_elementu_znormalizowane_minus, wartosci_elementu_znormalizowane_plus)

#------------------------------------------------------------------------------
def slownikUszkodzen(sygnal,elementy = uklad.elementy, badane_czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI,liczba_punktow_na_element = uklad.LICZBA_PUNKTOW,tolerancja = uklad.TOLERANCJA): # elementy slownika sa macierzami numPy
    elementy_modyfikacje = copy.deepcopy( elementy )
    słownikUszkodzen = {}

    wartosci_minus, wartosci_plus = generujWartosciElementowZnormalizowane(liczba_punktow_na_element)
    
    for uszkodzony_element in elementy: # wartosci mniejsze od nominalnej
        i = 0
        
        lista = np.zeros((wartosci_minus.shape[0],len(badane_czestotliwosci)))
        for wartosc in wartosci_minus:
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            #print(elementy_modyfikacje)
            (licznik, mianownik) = uklad.transmitancja(elementy_modyfikacje)
            charAmpl = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci)
            wartosci = charAmpl * sygnaly.widmo(sygnal,badane_czestotliwosci)
            lista[i] = wartosci
            i = i + 1
        słownikUszkodzen.setdefault(uszkodzony_element + '-',lista)
        elementy_modyfikacje = copy.deepcopy( elementy )

    for uszkodzony_element in elementy: # wartosci wieksze od nominalnej
        i = 0
        lista = np.zeros((wartosci_plus.shape[0],len(badane_czestotliwosci)))
        for wartosc in wartosci_plus:
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            #print(elementy_modyfikacje)
            (licznik, mianownik) = uklad.transmitancja(elementy_modyfikacje)
            charAmpl = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci)
            wartosci = charAmpl * sygnaly.widmo(sygnal,badane_czestotliwosci)
            lista[i] = wartosci
            i = i + 1
        słownikUszkodzen.setdefault(uszkodzony_element + '+',lista)
        elementy_modyfikacje = copy.deepcopy( elementy )

    (licznik, mianownik) = uklad.transmitancja(elementy)
    charAmpl = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci)
    wartosci = charAmpl * sygnaly.widmo(sygnal,badane_czestotliwosci)
    słownikUszkodzen.setdefault('Nominalne',wartosci)

    #s = LaczenieSygnatur(słownikUszkodzen)

    return słownikUszkodzen

#------------------------------------------------------------------------------
def slownikUszkodzenMonteCarlo(sygnal,elementy = uklad.elementy, badane_czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI,liczba_punktow_na_element = uklad.LICZBA_PUNKTOW,tolerancja = uklad.TOLERANCJA,liczba_losowanMC = uklad.LICZBA_LOSOWAN_MC): # elementy slownika sa macierzami numPy

    elementy_modyfikacje = copy.deepcopy( elementy )
    słownikUszkodzen = {}
    widmo_sygnalu = sygnaly.widmo(sygnal,badane_czestotliwosci)

    wartosci_minus, wartosci_plus = generujWartosciElementowZnormalizowane(liczba_punktow_na_element)
    
    for uszkodzony_element in elementy: # wartosci mniejsze od nominalnej
        klaster = []
        for wartosc in wartosci_minus:
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            char_apl_MC = monteCarlo(elementy_wykluczone_z_losowania = [uszkodzony_element], elementy = elementy_modyfikacje, czestotliwosci = badane_czestotliwosci ) 
            klaster.append( char_apl_MC * widmo_sygnalu )
        słownikUszkodzen.setdefault(uszkodzony_element + '-',klaster)
        elementy_modyfikacje = copy.deepcopy( elementy )

    for uszkodzony_element in elementy: # wartosci wieksze od nominalnej
        klaster = []
        for wartosc in wartosci_plus:
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            char_apl_MC = monteCarlo(elementy_wykluczone_z_losowania = [uszkodzony_element], elementy = elementy_modyfikacje, czestotliwosci = badane_czestotliwosci ) 
            klaster.append( char_apl_MC * widmo_sygnalu )
        słownikUszkodzen.setdefault(uszkodzony_element + '+',klaster)
        elementy_modyfikacje = copy.deepcopy( elementy )
        

    klaster = widmo_sygnalu * monteCarlo(czestotliwosci = badane_czestotliwosci) # punkt nominalny -> obszar tolerancji
    słownikUszkodzen.setdefault('Nominalne',klaster)

    #s = LaczenieSygnatur(słownikUszkodzen)

    return słownikUszkodzen
    
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def LaczenieWyrazenWSlowniku(slownik):
    nowy_slownik = {}
    polaczone_sygnatury = []
    for element1 in slownik:
        for element2 in slownik:
            if (element1 == element2) : continue # ten sam wyraz
            if (element1 == 'Nominalne') or (element2 == 'Nominalne') : continue
            # na wypadek nominalnego punktu w danych
            #####################################################
            a = slownik[element1] - slownik['Nominalne']
            if (a.all() == 0): continue
            a = slownik[element2] - slownik['Nominalne']
            if (a.all() == 0): continue
            ######################################################
            a = slownik[element1] - slownik[element2]
            if (a.all() == 0): # kiedy elementy sa takie same
                if not((element1 in polaczone_sygnatury) or (element2 in polaczone_sygnatury) ):
                    nowy_slownik.setdefault(element1+element2,slownik[element1])
                    polaczone_sygnatury.append(element1)
                    polaczone_sygnatury.append(element2)
        lista_kluczy = list(nowy_slownik.keys())
        dodaj = True
        for klucz in lista_kluczy:
            if(klucz.find(element1) != -1): dodaj = False
        if (dodaj) : nowy_slownik.setdefault(element1,slownik[element1])
    return nowy_slownik
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def LaczenieSygnatur(slownik):
    s1 = copy.deepcopy(slownik)
    for i in range (20):
        s1 = LaczenieWyrazenWSlowniku(s1)

    sygnatury_do_polaczenia = []
    
    for e1 in s1:
        for e2 in s1:
            #print(e1," | ",e2)
            if (e1 == 'Nominalne') or (e2 == 'Nominalne') : continue
            if (e1 == e2) : continue
            #if (e1[:1] == e2[:1]) : continue # sprawdzanie tego samego elementu "w druga strone"
            #print(e1,' | ',e2)
            for w1 in s1[e1]:
                for w2 in s1[e2]:
                    delta = abs(w1 - w2)
                    a = np.sqrt(np.dot(delta,delta))
                    #print(e1,' | ',e2,'delta : ',a)
                    if (a < uklad.epsilon):
                        if not( ( (e1,e2) in sygnatury_do_polaczenia ) or ((e2,e1) in sygnatury_do_polaczenia ) ) :
                            sygnatury_do_polaczenia.append((e1,e2))

    print(sygnatury_do_polaczenia)

    for sygnatura in sygnatury_do_polaczenia:
        s1.setdefault(sygnatura[0]+sygnatura[1],s1[sygnatura[0]])
        del(s1[sygnatura[0]])
        del(s1[sygnatura[1]])
                      
    return s1
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def PolaczDwieSygnatury(slownik):

    s1 = copy.deepcopy(slownik)
    
    sygnatura = list(slownik.keys())
    for i in range(len(sygnatura)):
        if (sygnatura == 'Nominalne') : continue
        print(i+1, ". ",sygnatura[i])

    indeks_1 = int(input('Podaj pierwsza sygnature: '))
    indeks_2 = int(input('Podaj druga sygnature: '))
    
    s1.setdefault(sygnatura[indeks_1]+sygnatura[indeks_2],s1[sygnatura[indeks_1]])
    del(s1[sygnatura[indeks_1]])
    del(s1[sygnatura[indeks_2]])
                      
    return s1
#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne2D(slownik_uszkodzen,badane_czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI):
    #plt.clf()
    i = 0
    for uszkodzenie in slownik_uszkodzen:
        if uszkodzenie == 'Nominalne' :
            continue
        A = slownik_uszkodzen[uszkodzenie]
        A = np.transpose(A)
        plt.plot(A[0],A[1],'o-', label = uszkodzenie)
    plt.xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    plt.ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    plt.legend()
    plt.show()
#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne2D_tolerancje(slownik_uszkodzen,elementy = uklad.elementy,badane_czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI,tolerancja = uklad.TOLERANCJA,liczba_losowan =uklad.LICZBA_LOSOWAN_MC):
    KOLORY_OBSZAR_TOL = {'R1' : 'b','R2' : 'g', 'R3' : 'r', 'C1' : 'c','C2':'y','C3' : 'k'}
    KOLORY_OBSZAR_TOL_KLUCZE = KOLORY_OBSZAR_TOL.keys()

    KOLORY_KRZYWE = {'R1' : 'k','R2' : 'y', 'R3' : 'c', 'C1' : 'r','C2':'g','C3' : 'b'}
    KOLORY_KRZYWE_KLUCZE = KOLORY_KRZYWE.keys()
    
    i = 0
    # obszary tolerancji
    for uszkodzenie in slownik_uszkodzen:
        A = slownik_uszkodzen[uszkodzenie]
        if uszkodzenie == 'Nominalne' :
            continue
            A = np.transpose(A)
            plt.plot(A[0],A[1],'o', label = 'Obszar tolerancji')
        else :
            for klaster in A :
                X = np.transpose(klaster)
                kolor = 'b'
                for klucz in KOLORY_OBSZAR_TOL_KLUCZE :
                    if uszkodzenie.find(klucz) != -1 :
                        kolor = KOLORY_OBSZAR_TOL[klucz]
                        break
                plt.plot(X[0],X[1],kolor+'o')

    #tolerancja obszaru nominalnego:
    A = slownik_uszkodzen['Nominalne']
    A = np.transpose(A)
    plt.plot(A[0],A[1],'o', label = 'Obszar tolerancji')
    
    # Krzywe nominalne
    for uszkodzenie in slownik_uszkodzen:
        A = slownik_uszkodzen[uszkodzenie]
        if uszkodzenie == 'Nominalne' :
            A = np.transpose(A)
            plt.plot(A[0][:1],A[1][:1],'o', label = uszkodzenie)
        else :
            krzywa_nominalna = []
            for klaster in A :
                krzywa_nominalna.append(klaster[0])
            krzywa_nominalna = np.transpose(krzywa_nominalna)
            kolor = 'b'
            for klucz in KOLORY_KRZYWE_KLUCZE :
                if uszkodzenie.find(klucz) != -1 :
                    kolor = KOLORY_KRZYWE[klucz]
                    break
            plt.plot(krzywa_nominalna[0],krzywa_nominalna[1],kolor+'o-', label = uszkodzenie)
    plt.axis('equal')
    plt.xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    plt.ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    
    plt.legend()
    plt.show()
#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne2D_tolerancje_pomiar(slownik_uszkodzen,pomiar,elementy = uklad.elementy,badane_czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI,tolerancja = uklad.TOLERANCJA,liczba_losowan =uklad.LICZBA_LOSOWAN_MC):
    KOLORY_OBSZAR_TOL = {'R1' : 'b','R2' : 'g', 'R3' : 'r', 'C1' : 'c','C2':'y','C3' : 'k'}
    KOLORY_OBSZAR_TOL_KLUCZE = KOLORY_OBSZAR_TOL.keys()

    KOLORY_KRZYWE = {'R1' : 'k','R2' : 'y', 'R3' : 'c', 'C1' : 'r','C2':'g','C3' : 'b'}
    KOLORY_KRZYWE_KLUCZE = KOLORY_KRZYWE.keys()
    
    i = 0
    # obszary tolerancji
    for uszkodzenie in slownik_uszkodzen:
        A = slownik_uszkodzen[uszkodzenie]
        if uszkodzenie == 'Nominalne' :
            continue
            A = np.transpose(A)
            plt.plot(A[0],A[1],'o', label = 'Obszar tolerancji')
        else :
            for klaster in A :
                X = np.transpose(klaster)
                kolor = 'b'
                for klucz in KOLORY_OBSZAR_TOL_KLUCZE :
                    if uszkodzenie.find(klucz) != -1 :
                        kolor = KOLORY_OBSZAR_TOL[klucz]
                        break
                plt.plot(X[0],X[1],kolor+'o')

    #tolerancja obszaru nominalnego:
    A = slownik_uszkodzen['Nominalne']
    A = np.transpose(A)
    plt.plot(A[0],A[1],'o', label = 'Obszar tolerancji')


    # Krzywe nominalne
    for uszkodzenie in slownik_uszkodzen:
        A = slownik_uszkodzen[uszkodzenie]
        if uszkodzenie == 'Nominalne' :
            A = np.transpose(A)
            plt.plot(A[0][:1],A[1][:1],'o', label = uszkodzenie)
        else :
            krzywa_nominalna = []
            for klaster in A :
                krzywa_nominalna.append(klaster[0])
            krzywa_nominalna = np.transpose(krzywa_nominalna)
            kolor = 'b'
            for klucz in KOLORY_KRZYWE_KLUCZE :
                if uszkodzenie.find(klucz) != -1 :
                    kolor = KOLORY_KRZYWE[klucz]
                    break
            plt.plot(krzywa_nominalna[0],krzywa_nominalna[1],kolor+'o-', label = uszkodzenie)
    A = pomiar
    A = np.transpose(A)
    plt.plot(A[0][:],A[1][:],'ko', label = "pomiar")
    plt.axis('equal')
    plt.xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    plt.ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    
    plt.legend()
    plt.show()
#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne2D_i_pomiar(slownik_uszkodzen,pomiar,worst_case = np.array([[0,0]]),badane_czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI):
    #plt.clf()
    i = 0
    for uszkodzenie in slownik_uszkodzen:
        A = slownik_uszkodzen[uszkodzenie]
        A = np.transpose(A)
        if uszkodzenie == 'Nominalne' :
            A = A.reshape((2,1))
            plt.plot(A[0][:1],A[1][:1],'o-', label = uszkodzenie)
            #continue
        else :
            plt.plot(A[0],A[1],'o-', label = uszkodzenie)
    A = pomiar
    A = np.transpose(A)
    plt.plot(A[0][:],A[1][:],'ko', label = "pomiar")
    A = worst_case
    A = np.transpose(A)
    plt.plot(A[0][:],A[1][:],'o', label = "Worst Case")
    plt.xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    plt.ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    plt.axis('equal')
    plt.legend()
    plt.show()
 
#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne3D_oszarNominalny(slownik_uszkodzen,badane_czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI):
    #plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    i = 0
    for uszkodzenie in slownik_uszkodzen:
        if uszkodzenie == 'Nominalne' :
            #continue
            A = monteCarlo([],uklad.elementy,badane_czestotliwosci,uklad.TOLERANCJA,uklad.LICZBA_LOSOWAN_MC)
            A = np.transpose(A)
            ax.plot(A[0],A[1],A[2],'o', label = 'Obszar tolerancji')
            ax.plot(A[0][:1],A[1][:1],A[2][:1],'ko-', label = uszkodzenie)
        else :
            A = slownik_uszkodzen[uszkodzenie]
            A = np.transpose(A)
            ax.plot(A[0],A[1],A[2],'o-', label = uszkodzenie)
    ax.set_xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    ax.set_ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    ax.set_zlabel('|H('+str(badane_czestotliwosci[2])+' Hz)|')
    ax.legend()
    plt.show()
#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne3D(slownik_uszkodzen,badane_czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI):
    #plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    i = 0
    for uszkodzenie in slownik_uszkodzen:
        if uszkodzenie == 'Nominalne' :
            continue
        A = slownik_uszkodzen[uszkodzenie]
        A = np.transpose(A)
        ax.plot(A[0],A[1],A[2],'o-', label = uszkodzenie)
    ax.set_xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    ax.set_ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    ax.set_zlabel('|H('+str(badane_czestotliwosci[2])+' Hz)|')
    ax.legend()
    plt.show()

#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne3D_i_pomiar(slownik_uszkodzen,pomiar,badane_czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI):
    #plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    i = 0
    for uszkodzenie in slownik_uszkodzen:
        if uszkodzenie == 'Nominalne' :
            continue
        A = slownik_uszkodzen[uszkodzenie]
        A = np.transpose(A)
        ax.plot(A[0],A[1],A[2],'o-', label = uszkodzenie)
    A = pomiar
    A = np.transpose(A)
    ax.plot(A[0][:],A[1][:],A[2][:],'ko', label = "pomiar")
    ax.set_xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    ax.set_ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    ax.set_zlabel('|H('+str(badane_czestotliwosci[2])+' Hz)|')
    ax.legend()
    plt.show()

#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne3D_tolerancje(slownik_uszkodzen,elementy = uklad.elementy,badane_czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI,tolerancja = uklad.TOLERANCJA,liczba_losowan =uklad.LICZBA_LOSOWAN_MC ):
    #plt.clf()

    KOLORY_OBSZAR_TOL = {'R1' : 'b','R2' : 'g', 'R3' : 'r', 'C1' : 'c','C2':'y','C3' : 'k'}
    KOLORY_OBSZAR_TOL_KLUCZE = KOLORY_OBSZAR_TOL.keys()

    KOLORY_KRZYWE = {'R1' : 'k','R2' : 'y', 'R3' : 'c', 'C1' : 'r','C2':'g','C3' : 'b'}
    KOLORY_KRZYWE_KLUCZE = KOLORY_KRZYWE.keys()
    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    i = 0
    # obszary tolerancji
    for uszkodzenie in slownik_uszkodzen:
        A = slownik_uszkodzen[uszkodzenie]
        if uszkodzenie == 'Nominalne' :
            A = np.transpose(A)
            ax.plot(A[0],A[1],A[2],'o', label = 'Obszar tolerancji')
        else :
            for klaster in A :
                X = np.transpose(klaster)
                kolor = 'b'
                for klucz in KOLORY_OBSZAR_TOL_KLUCZE :
                    if uszkodzenie.find(klucz) != -1 :
                        kolor = KOLORY_OBSZAR_TOL[klucz]
                        break
                ax.plot(X[0],X[1],X[2],kolor+'o')

    # Krzywe nominalne
    for uszkodzenie in slownik_uszkodzen:
        A = slownik_uszkodzen[uszkodzenie]
        if uszkodzenie == 'Nominalne' :
            A = np.transpose(A)
            ax.plot(A[0][:1],A[1][:1],A[2][:1],'o-', label = uszkodzenie)
        else :
            krzywa_nominalna = []
            for klaster in A :
                krzywa_nominalna.append(klaster[0])
            krzywa_nominalna = np.transpose(krzywa_nominalna)
            kolor = 'b'
            for klucz in KOLORY_KRZYWE_KLUCZE :
                if uszkodzenie.find(klucz) != -1 :
                    kolor = KOLORY_KRZYWE[klucz]
                    break
            ax.plot(krzywa_nominalna[0],krzywa_nominalna[1],krzywa_nominalna[2],kolor+'o-', label = uszkodzenie)
    ax.set_xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    ax.set_ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    ax.set_zlabel('|H('+str(badane_czestotliwosci[2])+' Hz)|')
    ax.legend()
    plt.show()
#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne3D_tolerancje_i_pomiar(slownik_uszkodzen,pomiar,elementy = uklad.elementy,badane_czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI,tolerancja = uklad.TOLERANCJA,liczba_losowan =uklad.LICZBA_LOSOWAN_MC ):
    #plt.clf()

    KOLORY_OBSZAR_TOL = {'R1' : 'b','R2' : 'g', 'R3' : 'r', 'C1' : 'c','C2':'y','C3' : 'k'}
    KOLORY_OBSZAR_TOL_KLUCZE = KOLORY_OBSZAR_TOL.keys()

    KOLORY_KRZYWE = {'R1' : 'k','R2' : 'y', 'R3' : 'c', 'C1' : 'r','C2':'g','C3' : 'b'}
    KOLORY_KRZYWE_KLUCZE = KOLORY_KRZYWE.keys()
    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    i = 0
    # obszary tolerancji
    for uszkodzenie in slownik_uszkodzen:
        A = slownik_uszkodzen[uszkodzenie]
        if uszkodzenie == 'Nominalne' :
            A = np.transpose(A)
            ax.plot(A[0],A[1],A[2],'o', label = 'Obszar tolerancji')
        else :
            for klaster in A :
                X = np.transpose(klaster)
                kolor = 'b'
                for klucz in KOLORY_OBSZAR_TOL_KLUCZE :
                    if uszkodzenie.find(klucz) != -1 :
                        kolor = KOLORY_OBSZAR_TOL[klucz]
                        break
                ax.plot(X[0],X[1],X[2],kolor+'o')

    # Krzywe nominalne
    for uszkodzenie in slownik_uszkodzen:
        A = slownik_uszkodzen[uszkodzenie]
        if uszkodzenie == 'Nominalne' :
            A = np.transpose(A)
            ax.plot(A[0][:1],A[1][:1],A[2][:1],'o-', label = uszkodzenie)
        else :
            krzywa_nominalna = []
            for klaster in A :
                krzywa_nominalna.append(klaster[0])
            krzywa_nominalna = np.transpose(krzywa_nominalna)
            kolor = 'b'
            for klucz in KOLORY_KRZYWE_KLUCZE :
                if uszkodzenie.find(klucz) != -1 :
                    kolor = KOLORY_KRZYWE[klucz]
                    break
            ax.plot(krzywa_nominalna[0],krzywa_nominalna[1],krzywa_nominalna[2],kolor+'o-', label = uszkodzenie)
    A = pomiar
    A = np.transpose(A)
    ax.plot(A[0][:1],A[1][:1],A[2][:1],'o', label = "pomiar")
    ax.set_xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    ax.set_ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    ax.set_zlabel('|H('+str(badane_czestotliwosci[2])+' Hz)|')
    ax.axis('equal')
    ax.legend()
    plt.show()
#------------------------------------------------------------------------------
#                         PCA
#------------------------------------------------------------------------------
def wygenerujMacierzDanychPCA(sygnal,elementy = uklad.elementy,czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI,liczba_losowanMC = uklad.LICZBA_LOSOWAN_MC,tolerancja = uklad.TOLERANCJA,liczba_punktow = uklad.LICZBA_PUNKTOW):
    """
    GENERUJEMY MACIERZ DANYCH DO ANALIZY PCA
    KAZDA KOLUMNA MACIERZY ODPOWIADA JEDNEMU WEKTOROWI POMIAROWEMU
    """
    elementy_modyfikacje = copy.deepcopy( elementy )
    czestotliwosci = np.asarray(czestotliwosci)
    liczba_czestotliwosci = czestotliwosci.shape[0]
    delta = (150 - 50) / liczba_punktow
    liczba_elementow = len(list(elementy.keys()))

    widmo_sygnalu = sygnaly.widmo(sygnal,czestotliwosci)
    wartosci_uszkodzenia = np.arange(50,150+delta,delta) # uszkodzenia
    
    liczba_wierszy = liczba_losowanMC * liczba_elementow * (wartosci_uszkodzenia.shape[0])
    licznik = 0
    
    X_t = np.zeros( ( liczba_wierszy , liczba_czestotliwosci ) )
    for uszkodzony_element in elementy:     # wybor elementu do uszkodzenia
        for uszkodzenie in wartosci_uszkodzenia: # wszystkie mozliwe uszkodzenia DANEGO ELEMENTU
            #if uszkodzenie == 10 : continue
            for i in range(liczba_losowanMC): # MonteCarlo
                for element in elementy_modyfikacje: # tolerancje
                    if element.find('R') != -1 :
                        # gdy element jest rezystorem
                        L = 1 - tolerancja['R']
                        H = 1 + tolerancja['R']
                        elementy_modyfikacje[element] = elementy[element] * (np.random.uniform(L,H))
                    elif element.find('C') != -1 :
                        # gdy element jets kondensatorem :
                        L = 1 - tolerancja['C']
                        H = 1 + tolerancja['C']
                        elementy_modyfikacje[element] = elementy[element] * (np.random.uniform(L,H))
                    else :
                        print("Czegoś nie uwzględniłeś! : ",element)
                    #elementy_modyfikacje[element] = elementy[element] * (np.random.uniform(L,H))
                elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * uszkodzenie / 100
                l, m = uklad.transmitancja(elementy_modyfikacje)
                X_t[licznik] = charCzestotliwosciowaModul(l, m,czestotliwosci) * widmo_sygnalu
                licznik = licznik +  1
    return np.transpose(X_t)    
#------------------------------------------------------------------------------
def PCA(X,prog_wariancji):
    """
    GENARUJE MACIERZ TRANSFORMACJI LINIOWEJ
    """
    C = np.cov(X) # macierz kowariancji macierzy X
    P,S,Q_t = linalg.svd(C,full_matrices=True)
    Pm = 0
    licznik = 1
    for wartosc_wlasna in S:
        Pm +=  100 * (wartosc_wlasna/ (np.sum(S)))
        print(licznik,". P = ", Pm)
        if Pm > prog_wariancji :
            break
        licznik += 1
    P_t = np.transpose(P) # transpozycja macierzy P
    macierz_przeksztalcenia = P_t[:licznik]
    return macierz_przeksztalcenia
#------------------------------------------------------------------------------
def slownikUszkodzenPCA(slownikUszkodzen, fi):
    s = copy.deepcopy(slownikUszkodzen)
    for element in s:
        y = np.matmul(fi,np.transpose(s[element]))
        s[element] = np.transpose(y)
    return s

#------------------------------------------------------------------------------
def slownikUszkodzenPCA_MC(slownikUszkodzen, fi):
    s = copy.deepcopy(slownikUszkodzen)
    for element in s:
        if element == 'Nominalne':
            y = np.matmul(fi,np.transpose(s[element]))
            s[element] = np.transpose(y)
            continue
        for i in range(len(s[element])) :
            z = np.matmul(fi,np.transpose(s[element][i]))
            s[element][i] = np.transpose(z)
    return s
#------------------------------------------------------------------------------------------------------------------------------------------------------------
def macierzKowariancjiEstymata(macierz_danych):
    """
    Zakladamy ze kazdy wiersz macierzy danych to jeden pomiar
    """

    # estymata wartosci sredniej:
    mx = np.zeros(macierz_danych[:1].shape)
    licznik = 0
    for pomiar in macierz_danych:
        mx += pomiar
        licznik += 1
    mx /= licznik

    # estymata macierzy korelacji:
    a = np.matmul( np.transpose(mx), mx) # macierz pomocniacza do wyznaczenia wymiarow macierzy kowariancji
    Cx = np.zeros(a.shape)
    for pomiar in macierz_danych:
        x = np.transpose(pomiar - mx)
        x_t = pomiar - mx
        Cx += np.matmul(x,x_t)
    Cx /= licznik

    return Cx, mx
#------------------------------------------------------------------------------------------------------------------------------------------------------------
def wyrysujKlasterDanych3D(dane,badane_czestotliwosci = uklad.BADANE_CZESTOTLIWOSCI):
    #plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    #A = monteCarlo([],uklad.elementy,badane_czestotliwosci,uklad.TOLERANCJA,uklad.LICZBA_LOSOWAN_MC)
    A = np.transpose(dane)
    ax.plot(A[0],A[1],A[2],'o', label = 'Obszar tolerancji')
    ax.plot(A[0][:1],A[1][:1],A[2][:1],'ko-', label = 'Punkt nominalny')
    ax.set_xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    ax.set_ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    ax.set_zlabel('|H('+str(badane_czestotliwosci[2])+' Hz)|')
    ax.legend()
    plt.show()
#------------------------------------------------------------------------------------------------------------------------------------------------------------
def EB(macierz_kowariancji,srodek,punkt):
    """
    Obliczanie elipsoidalnej funkcji bazowej EB
    srodek i punkt to wektory wierszowe (1,n)
    """
    C = np.linalg.inv(macierz_kowariancji) # macierz skalujaca
    x = np.transpose(punkt)
    c = np.transpose(srodek)
    d = x - c
    d_t = np.transpose(d)
    a = np.matmul(d_t,C) # pomocnicza macierz
    a = np.matmul(a,d)

    y = np.exp(-0.5 * a)

    return y,a
#------------------------------------------------------------------------------------------------------------------------------------------------------------
def analizaEB(klaster_danych,macierz_kowariancji,srodek):
    """
    Analiza parametro klastra danych pod wzgledem funkcji EB:
    """
    licznik = 1
    d_max = 0
    d_min = 200000
    eb_min = 2
    eb_max = 0
    indeks_min = 0
    indeks_max = 0
    for i in range(1,klaster_danych.shape[0]-1):
        eb,d = EB(macierz_kowariancji,srodek,klaster_danych[i:i+1])
        if d > d_max : d_max = d
        if d < d_min : d_min = d
        if eb > eb_max :
            eb_max = eb
            indeks_max = licznik
        if eb < eb_min :
            eb_min = eb
            indeks_min = licznik
        licznik += 1
    
    print(licznik)
    return d_max,d_min,eb_min,eb_max,indeks_min,indeks_max

#------------------------------------------------------------------------------------------------------------------------------------------------------------

def odleglosci(slownikUszkodzen,pomiar):
    d_min_lista = []
    for uszkodzenie in slownikUszkodzen:
        if uszkodzenie == "Nominalne":
            r = slownikUszkodzen["Nominalne"] - pomiar
            d2 = np.dot(r,r)
            d = np.sqrt(d2)
            print (uszkodzenie," : ",d)
            d_min_lista.append(d)
        else :
            d_min = 10000
            for i in range(slownikUszkodzen[uszkodzenie].shape[0]):
                r = slownikUszkodzen[uszkodzenie][i] - pomiar
                d2 = np.dot(r,r)
                d = np.sqrt(d2)
                if d < d_min : d_min = d
            print (uszkodzenie," : ",d_min)
            d_min_lista.append(d_min)

    return d_min_lista
