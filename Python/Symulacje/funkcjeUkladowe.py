"""

MODUL Z FUNKCJAMI UKLADOWYMI -> UNIWERSALNY DO BADANIA DOWOLNEGO UKLADU

"""
#------------------------------------------------------------------------------
import copy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy import linalg
from scipy import signal
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

plt.rc('axes', labelsize = 16)
plt.rc('xtick', labelsize=14)
plt.rc('ytick', labelsize=14)


PROG_GORNY_PROCENTY = 150
PROG_DOLNY_PROCENTY = 50
ODSTEP_OD_WAR_NOMINALNEJ_PROCENTY = 5
WARTOSC_NOMINALNA_PROCENTY = 100

LICZBA_PUNKTOW = 6 # liczba punktow na element

F_CPU = 32e6
LICZBA_PROBEK = 500

##PER = (F_CPU//(LICZBA_PROBEK*uklad.BADANE_CZESTOTLIWOSCI_MULTISIN[0])) - 1 # wartosc rejestru PER
##F_ZNORMALIZOWANE = uklad.BADANE_CZESTOTLIWOSCI_MULTISIN / uklad.BADANE_CZESTOTLIWOSCI_MULTISIN[0]
##uklad.BADANE_CZESTOTLIWOSCI_MULTISIN[0] = F_CPU / (LICZBA_PROBEK * (PER+1)) # dopasowanie do faktycznie generowanej przez DAC czesttoliwosci
##uklad.BADANE_CZESTOTLIWOSCI_MULTISIN = F_ZNORMALIZOWANE * uklad.BADANE_CZESTOTLIWOSCI_MULTISIN[0]

PER = (F_CPU//(LICZBA_PROBEK*uklad.CZESTOTLIWOSC_PODSTAWOWA_MULTISIN)) - 1 # wartosc rejestru PER
uklad.CZESTOTLIWOSC_PODSTAWOWA_MULTISIN = F_CPU / (LICZBA_PROBEK * (PER+1)) # dopasowanie do faktycznie generowanej przez DAC czesttoliwosci

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
def monteCarloUniform(czestotliwosci, elementy_wykluczone_z_losowania = [],elementy = uklad.elementy  ,tolerancja = uklad.TOLERANCJA,liczba_losowanMC = uklad.LICZBA_LOSOWAN_MC):
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
def monteCarloNormal(czestotliwosci, elementy_wykluczone_z_losowania = [],elementy = uklad.elementy  ,tolerancja = uklad.TOLERANCJA,liczba_losowanMC = uklad.LICZBA_LOSOWAN_MC, na_podstawie_odp_czasowej = False, sygnal = np.array([]) ):
    """
    DLA ZADANYCH WARTOSCI ELEMENTOW GENERUJEMY MACIERZ DANYCH
    WOKOL PUNKTU NOMINALNEGO - KLASTER/OBSZAR TOLERANCJI
    ZWRACA MACIERZ W KTOREJ KAZDY WIERSZ JEST PUNKTEM POMIAROWYM,
    WIERSZ 0 TO PUNKT NMOMINALNY
    """
    czestotliwosci = np.asarray(czestotliwosci)
    liczba_czestotliwosci = czestotliwosci.shape[0]
    
    liczba_wierszy = liczba_losowanMC + 1 # tyle punktow pomiarowych ile jest losowan. +1 bo wiersz 0 to punkt nominalny
    liczba_kolumn = liczba_czestotliwosci
    
    klaster = np.zeros( ( liczba_wierszy , liczba_kolumn ) )
    if na_podstawie_odp_czasowej : # jezeli flaga jest ustawiona zwraca WIDMO ODPOWIEDZI UKLADU!!!!!!
        normowanie_w_odp_czasowej = True
        y,t = odpowiedzCzasowaUkladu( elementy, sygnal, czestotliwosci[0], normowanie_w_odp_czasowej) # odpowiedz CZASOWA ukladu w stanie nominalnym
        klaster[0] = sygnaly.TransformataFouriera( y, czestotliwosci, not(normowanie_w_odp_czasowej) )  # negacja zeby normowac TYLKO RAZ!
    else : # domyslnie - zwraca CHARAKTERYSTYKE AMPLITUDOWA
        l, m = uklad.transmitancja(elementy_modyfikacje)
        klaster[0] = charCzestotliwosciowaModul(l, m,czestotliwosci)
##    l, m = uklad.transmitancja(elementy)
##    klaster[0] = charCzestotliwosciowaModul(l, m,czestotliwosci)
    #################################################################################
    #           LOSOWANIE MONTECARLO
    #################################################################################
    licznik = 1
    for i in range(liczba_losowanMC): # MonteCarlo
        elementy_modyfikacje = losowanieRozkladNormalny( elementy, tolerancja, elementy_wykluczone_z_losowania)
        if na_podstawie_odp_czasowej : # jezeli flaga jest ustawiona zwraca WIDMO ODPOWIEDZI UKLADU!!!!!!
            normowanie_w_odp_czasowej = True
            y,t = odpowiedzCzasowaUkladu( elementy_modyfikacje, sygnal, czestotliwosci[0], normowanie_w_odp_czasowej) # odpowiedz CZASOWA uszkodzonego ukladu!
            klaster[licznik] = sygnaly.TransformataFouriera( y, czestotliwosci, not(normowanie_w_odp_czasowej) )  # negacja zeby normowac TYLKO RAZ!
        else : # domyslnie - zwraca CHARAKTERYSTYKE AMPLITUDOWA
            l, m = uklad.transmitancja(elementy_modyfikacje)
            klaster[licznik] = charCzestotliwosciowaModul(l, m,czestotliwosci)
        licznik = licznik +  1
    return klaster

#------------------------------------------------------------------------------
def losowanieRozkladNormalny( elementy, tolerancja , elementy_wykluczone_z_losowania = []):
    elementy_modyfikacje = copy.deepcopy( elementy )
    for element in elementy_modyfikacje: # dla kazdego elementu ukladu
        if element in elementy_wykluczone_z_losowania : # jezeli wartosc elementu ma byc niezmienna
            elementy_modyfikacje[element] = elementy[element]
        else : # modyfikacja wartosci elementu w zakresie jego tolerancji
            if element.find('R') != -1 : # gdy element jest rezystorem
                tol = tolerancja['R']
            elif element.find('C') != -1 : # gdy element jest kondensatorem :
                tol = tolerancja['C']
            else :
                print("Czegoś nie uwzględniłeś! : ",element)
            sigma = (elementy[element] * tol )/3
            elementy_modyfikacje[element] = np.random.normal(elementy[element], sigma)

    return elementy_modyfikacje   
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
def analizaWorstCase(czestotliwosci, sygnal,elementy = uklad.elementy  ,tolerancja = uklad.TOLERANCJA):
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
    """
    Zwraca wartosci w procentach, potem nalezy przemnozyc wartosc elementu, przez otrzymane wartosci
    """

    wartosci_elementu_znormalizowane_minus = np.linspace(PROG_DOLNY_PROCENTY, WARTOSC_NOMINALNA_PROCENTY-ODSTEP_OD_WAR_NOMINALNEJ_PROCENTY, liczba_punktow_na_element)
    wartosci_elementu_znormalizowane_plus  = np.linspace(WARTOSC_NOMINALNA_PROCENTY + ODSTEP_OD_WAR_NOMINALNEJ_PROCENTY, PROG_GORNY_PROCENTY, liczba_punktow_na_element)

    return (wartosci_elementu_znormalizowane_minus, wartosci_elementu_znormalizowane_plus)

#------------------------------------------------------------------------------
def slownikUszkodzen(badane_czestotliwosci, sygnal, typ_widma, elementy = uklad.elementy, liczba_punktow_na_element = LICZBA_PUNKTOW, na_podstawie_odp_czasowej = False): # elementy slownika sa macierzami numPy
    elementy_modyfikacje = copy.deepcopy( elementy )
    słownikUszkodzen = {}

    widmo_sygnalu = 0 # inicjalizacja zmiennej
    
    if typ_widma == 'TF' :
        widmo_sygnalu = sygnaly.TransformataFouriera(sygnal,badane_czestotliwosci)      # TF -> Transformata Fouriera -> sinc
        print("Licze TF")
    else : widmo_sygnalu = sygnaly.widmo(sygnal, badane_czestotliwosci)                 # domyslnie metoda wieloharmoniczna - FFT

    
    wartosci_minus, wartosci_plus = generujWartosciElementowZnormalizowane(liczba_punktow_na_element)
    
    for uszkodzony_element in elementy: # wartosci mniejsze od nominalnej
        i = 0
        
        lista = np.zeros((wartosci_minus.shape[0],len(badane_czestotliwosci)))
        for wartosc in wartosci_minus:
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            if na_podstawie_odp_czasowej :
                normowanie_w_odp_czasowej = True
                y,t = odpowiedzCzasowaUkladu( elementy_modyfikacje, sygnal, badane_czestotliwosci[0], normowanie_w_odp_czasowej) # odpowiedz CZASOWA uszkodzonego ukladu!
                wartosci = sygnaly.TransformataFouriera( y, badane_czestotliwosci, not(normowanie_w_odp_czasowej) )  # negacja zeby normowac TYLKO RAZ!
            else : # obliczenia na podstawie wzoru : Y(f) = H(f) * X(f)
                (licznik, mianownik) = uklad.transmitancja(elementy_modyfikacje)
                charAmpl = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci) # H(f)
                wartosci = charAmpl * widmo_sygnalu # H(f) * X(f)
            lista[i] = wartosci
            i = i + 1
        słownikUszkodzen.setdefault(uszkodzony_element + '-',lista)
        elementy_modyfikacje = copy.deepcopy( elementy )

    for uszkodzony_element in elementy: # wartosci wieksze od nominalnej
        i = 0
        lista = np.zeros((wartosci_plus.shape[0],len(badane_czestotliwosci)))
        for wartosc in wartosci_plus:
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            if na_podstawie_odp_czasowej :
                normowanie_w_odp_czasowej = True
                y,t = odpowiedzCzasowaUkladu( elementy_modyfikacje, sygnal, badane_czestotliwosci[0], normowanie_w_odp_czasowej) # odpowiedz CZASOWA uszkodzonego ukladu!
                wartosci = sygnaly.TransformataFouriera( y, badane_czestotliwosci, not(normowanie_w_odp_czasowej) )  # negacja zeby normowac TYLKO RAZ!
            else : # obliczenia na podstawie wzoru : Y(f) = H(f) * X(f)
                (licznik, mianownik) = uklad.transmitancja(elementy_modyfikacje)
                charAmpl = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci) # H(f)
                wartosci = charAmpl * widmo_sygnalu # H(f) * X(f)
            lista[i] = wartosci
            i = i + 1
        słownikUszkodzen.setdefault(uszkodzony_element + '+',lista)
        elementy_modyfikacje = copy.deepcopy( elementy )

    if na_podstawie_odp_czasowej :
        normowanie_w_odp_czasowej = True
        y,t = odpowiedzCzasowaUkladu( elementy_modyfikacje, sygnal, badane_czestotliwosci[0], normowanie_w_odp_czasowej) # odpowiedz CZASOWA uszkodzonego ukladu!
        wartosci = sygnaly.TransformataFouriera( y, badane_czestotliwosci, not(normowanie_w_odp_czasowej) )  # negacja zeby normowac TYLKO RAZ!
    else : # obliczenia na podstawie wzoru : Y(f) = H(f) * X(f)
        (licznik, mianownik) = uklad.transmitancja(elementy_modyfikacje)
        charAmpl = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci) # H(f)
        wartosci = charAmpl * widmo_sygnalu # H(f) * X(f)
    słownikUszkodzen.setdefault('Nominalne',wartosci)

    #s = LaczenieSygnatur(słownikUszkodzen)

    return słownikUszkodzen

#------------------------------------------------------------------------------
def slownikUszkodzenMonteCarlo(badane_czestotliwosci, sygnal, typ_widma,elementy = uklad.elementy, liczba_punktow_na_element = LICZBA_PUNKTOW,liczba_losowanMC = uklad.LICZBA_LOSOWAN_MC, na_podstawie_odp_czasowej = False): # elementy slownika sa macierzami numPy

    elementy_modyfikacje = copy.deepcopy( elementy )
    słownikUszkodzen = {}
    widmo_sygnalu = 0 # inicjalizacja zmiennej

    if na_podstawie_odp_czasowej :
        N = len(badane_czestotliwosci)
        widmo_sygnalu = np.ones(N) # element neutralny mnozenia
    else :
        if typ_widma == 'TF' :
            widmo_sygnalu = sygnaly.TransformataFouriera(sygnal,badane_czestotliwosci)      # TF -> Transformata Fouriera -> sinc
            print("Licze TF")
        else : widmo_sygnalu = sygnaly.widmo(sygnal, badane_czestotliwosci)                 # domyslnie metoda wieloharmoniczna - FFT

    wartosci_minus, wartosci_plus = generujWartosciElementowZnormalizowane(liczba_punktow_na_element)

    print('widmo_sygnalu = ', widmo_sygnalu)
    
    for uszkodzony_element in elementy: # wartosci mniejsze od nominalnej
        klaster = []
        for wartosc in wartosci_minus:
            print("Uszkodzony element : ", uszkodzony_element,' = ', wartosc,'%')
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            char_amp_MC = monteCarloNormal(elementy_wykluczone_z_losowania = [uszkodzony_element], elementy = elementy_modyfikacje, czestotliwosci = badane_czestotliwosci , liczba_losowanMC = liczba_losowanMC, na_podstawie_odp_czasowej = na_podstawie_odp_czasowej, sygnal = sygnal ) 
            klaster.append( char_amp_MC * widmo_sygnalu )
        słownikUszkodzen.setdefault(uszkodzony_element + '-',klaster)
        elementy_modyfikacje = copy.deepcopy( elementy )

    for uszkodzony_element in elementy: # wartosci wieksze od nominalnej
        klaster = []
        for wartosc in wartosci_plus:
            print("Uszkodzony element : ", uszkodzony_element,' = ', wartosc,'%')
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            char_amp_MC = monteCarloNormal(elementy_wykluczone_z_losowania = [uszkodzony_element], elementy = elementy_modyfikacje, czestotliwosci = badane_czestotliwosci , liczba_losowanMC = liczba_losowanMC, na_podstawie_odp_czasowej = na_podstawie_odp_czasowej, sygnal = sygnal )
            klaster.append( char_amp_MC * widmo_sygnalu )
        słownikUszkodzen.setdefault(uszkodzony_element + '+',klaster)
        elementy_modyfikacje = copy.deepcopy( elementy )
        
    print("Obszar nominalny")
    klaster = widmo_sygnalu * monteCarloNormal(czestotliwosci = badane_czestotliwosci, liczba_losowanMC = liczba_losowanMC, na_podstawie_odp_czasowej = na_podstawie_odp_czasowej, sygnal = sygnal) # punkt nominalny -> obszar tolerancji
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
def wyrysujKrzyweIdentyfikacyjne2D(slownik_uszkodzen):
    #plt.clf()
    i = 0
    for uszkodzenie in slownik_uszkodzen:
        if uszkodzenie == 'Nominalne' :
            continue
        A = slownik_uszkodzen[uszkodzenie]
        A = np.transpose(A)
        plt.plot(A[0],A[1],'o-', label = uszkodzenie)
    plt.xlabel('PCA 1', fontsize=20)
    plt.ylabel('PCA 2', fontsize=20)
    plt.axis('equal')
    plt.grid()
    plt.legend(prop={'size': 22})
    plt.show()
#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne2D_tolerancje(slownik_uszkodzen):
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
    plt.xlabel('PCA1')
    plt.ylabel('PCA2')
    
    plt.legend()
    plt.show()
#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne2D_tolerancje_pomiar(badane_czestotliwosci, slownik_uszkodzen,pomiar,elementy = uklad.elementy,tolerancja = uklad.TOLERANCJA,liczba_losowan =uklad.LICZBA_LOSOWAN_MC):
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
def wyrysujKrzyweIdentyfikacyjne2D_i_pomiar(badane_czestotliwosci, slownik_uszkodzen,pomiar,worst_case = np.array([[0,0]])  ):
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
def wyrysujKrzyweIdentyfikacyjne3D_oszarNominalny(slownik_uszkodzen,badane_czestotliwosci  ):
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
def wyrysujKrzyweIdentyfikacyjne3D(slownik_uszkodzen  ):
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
    ax.set_xlabel('PCA 1', fontsize=20)
    ax.set_ylabel('PCA 2', fontsize=20)
    ax.set_zlabel('PCA 3', fontsize=20)
    ax.legend(prop={'size': 22})
    plt.grid()
    plt.show()

#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne3D_i_pomiar(slownik_uszkodzen,pomiar,badane_czestotliwosci  ):
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
def wyrysujKrzyweIdentyfikacyjne3D_tolerancje(badane_czestotliwosci, slownik_uszkodzen,elementy = uklad.elementy, tolerancja = uklad.TOLERANCJA,liczba_losowan =uklad.LICZBA_LOSOWAN_MC ):
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
def wyrysujKrzyweIdentyfikacyjne3D_tolerancje_i_pomiar(badane_czestotliwosci, slownik_uszkodzen,pomiar,elementy = uklad.elementy, tolerancja = uklad.TOLERANCJA,liczba_losowan =uklad.LICZBA_LOSOWAN_MC ):
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
def wygenerujMacierzDanychPCA(slownik_uszkodzen_MC): #(badane_czestotliwosci, sygnal, typ_widma ,liczba_losowan, elementy = uklad.elementy, liczba_punktow_na_element = LICZBA_PUNKTOW,tolerancja = uklad.TOLERANCJA):
    """
    GENERUJEMY MACIERZ DANYCH DO ANALIZY PCA
    KAZDA KOLUMNA MACIERZY ODPOWIADA JEDNEMU WEKTOROWI POMIAROWEMU
    """
##    slownik_uszkodzen_MC = slownikUszkodzenMonteCarlo( badane_czestotliwosci, sygnal, typ_widma ,elementy, liczba_punktow_na_element ,tolerancja ,liczba_losowanMC = liczba_losowan)
##    Liczba_wymiarow  =  badane_czestotliwosci.shape[0] # liczba wymiarow w przestrzeni pomiarowej
    Liczba_wymiarow = slownik_uszkodzen_MC['Nominalne'][0].shape[0]
    X = np.array([])
    for uszkodzenie in slownik_uszkodzen_MC:
        if uszkodzenie == 'Nominalne':
            
            A = slownik_uszkodzen_MC[uszkodzenie]
            A = A.reshape( (A.shape[0] * Liczba_wymiarow, ) )
            X = np.concatenate( ( X, A ) )
        else :
            for punkt in slownik_uszkodzen_MC[uszkodzenie]:
                
                A = punkt
                A = A.reshape( (A.shape[0] * Liczba_wymiarow, ) )
                X = np.concatenate( ( X, A ) )

    dlugosc_rekordu = X.shape[0]
    X = X.reshape( ( dlugosc_rekordu // Liczba_wymiarow, Liczba_wymiarow ) )
    X = np.transpose(X)
    
    return X # zwracamy macierz w ktorej kazda kolumna jest wektorem pomiarowym
#------------------------------------------------------------------------------
def PCA_var(X,prog_wariancji):
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
def PCA(X,liczba_skladowych):
    """
    GENARUJE MACIERZ TRANSFORMACJI LINIOWEJ
    """
    C = np.cov(X) # macierz kowariancji macierzy X
    P,S,Q_t = linalg.svd(C,full_matrices=True)
    P_t = np.transpose(P) # transpozycja macierzy P
    macierz_przeksztalcenia = P_t[:liczba_skladowych]
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
def wyrysujKlasterDanych3D(dane,badane_czestotliwosci  ):
    #plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    #A = monteCarlo([],uklad.elementy,badane_czestotliwosci,uklad.TOLERANCJA,uklad.LICZBA_LOSOWAN_MC)
    A = np.transpose(dane)
    ax.plot(A[0],A[1],A[2],'o', label = 'Obszar tolerancji')
    #ax.plot(A[0][:1],A[1][:1],A[2][:1],'ko-', label = 'Punkt nominalny')
    ax.set_xlabel('PCA 1')
    ax.set_ylabel('PCA 2')
    ax.set_zlabel('PCA 3')
    ax.legend()
    #plt.axis('equal')
    #plt.show()
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
#------------------------------------------------------------------------------------------------------------------------------------------------------------
def okrag(srodek, promien):
    kat = np.linspace(0, 2 * np.pi, 628)
    x1 = srodek[0] + promien * np.cos(kat)
    x2 = srodek[1] + promien * np.sin(kat)

    return x1, x2
    
#------------------------------------------------------------------------------------------------------------------------------------------------------------
def odchylenia_std(uszkodzenie_symulacja_MC):
    """
    Funkcja zwracajaca wektor odchylen std dla danego uszkodzenia
    """
    x = np.asarray(uszkodzenie_symulacja_MC)
    odchylenia = []
    for e in x :
        acc = 0
        mx = e.mean(axis = 0)
        for i in range(e.shape[0]):
            r = e[i] - mx
            acc += np.dot(r,r)
        sigma = np.sqrt( acc/ (e.shape[0] - 1) )
        odchylenia.append(sigma)

    return np.asarray(odchylenia)

#------------------------------------------------------------------------------------------------------------------------------------------------------------
def slownik_odchylen_std(slownik_uszkodzen_MC):
    slownik = {}

    for uszkodzenie in slownik_uszkodzen_MC:
        if uszkodzenie == 'Nominalne' : continue
        slownik[uszkodzenie] = odchylenia_std( slownik_uszkodzen_MC[uszkodzenie] )

    return slownik
#------------------------------------------------------------------------------------------------------------------------------------------------------------

def odpowiedzCzasowaUkladu(elementy, tablica_napiec_pobudzenia_uint16, czestotliwosc_podstawowa, zamiana_z_probek_na_napiecie = True):
    pobudzenie = tablica_napiec_pobudzenia_uint16.astype('float32')
    
    if zamiana_z_probek_na_napiecie :
        pobudzenie /= 4095
        pobudzenie -= pobudzenie[0]
    
    n = len(pobudzenie)
    T = 1/czestotliwosc_podstawowa # czas trwania sygnalu
    t = np.linspace(0,1,n) * T # wektor czasow

    l,m = uklad.transmitancja(elementy)
    lti = signal.lti(l, m) # obiekt opisujacy system o zadanej transmitancji
    t, y, x = signal.lsim2(lti, pobudzenie, t)
    
    return y, t
    
