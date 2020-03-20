"""

MODUL Z FUNKCJAMI UKLADOWYMI -> UNIWERSALNY DO BADANIA DOWOLNEGO UKLADU

"""
#------------------------------------------------------------------------------
import copy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import random
from scipy import linalg
import os

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
#------------------------------------------------------------------------------
def charCzestotliwosciowaModul(licznik_transmitancji,mianownik_transmitancji,f):
    f = np.asarray(f)
    w = 2*np.pi*f
    potegi_w_liczniku = np.arange(len(licznik_transmitancji)-1,-1,-1)
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
    return modul

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def slownikUszkodzen(elementy, badane_czestotliwosci,liczba_punktow_na_element):
    elementy_modyfikacje = copy.deepcopy( elementy )
    słownikUszkodzen = {}
    liczba_punktow_plus = liczba_punktow_minus = liczba_punktow_na_element//2
    delta_minus = (100-50) / liczba_punktow_minus
    delta_plus = (100-150) / liczba_punktow_plus

    for uszkodzony_element in elementy: # wartosci mniejsze od nominalnej
        lista = []
        wartosci_elementu_znormalizowane = np.arange(50,100,delta_minus)
        for wartosc in wartosci_elementu_znormalizowane:
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            #print(uszkodzony_element,": ",elementy_modyfikacje[uszkodzony_element])
            (licznik, mianownik) = uklad.transmitancja(elementy_modyfikacje)
            wartosci = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci)
            lista.append(wartosci)
        słownikUszkodzen.setdefault(uszkodzony_element + '-',lista)
        elementy_modyfikacje = copy.deepcopy( elementy )

    for uszkodzony_element in elementy: # wartosci wieksze od nominalnej
        lista = []
        wartosci_elementu_znormalizowane = np.arange(150,100,delta_plus)
        for wartosc in wartosci_elementu_znormalizowane:
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            #print(uszkodzony_element,": ",elementy_modyfikacje[uszkodzony_element])
            (licznik, mianownik) = uklad.transmitancja(elementy_modyfikacje)
            wartosci = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci)
            lista.append(wartosci)
        słownikUszkodzen.setdefault(uszkodzony_element + '+',lista)
        elementy_modyfikacje = copy.deepcopy( elementy )

    (licznik, mianownik) = uklad.transmitancja(elementy)
    wartosci = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci)
    słownikUszkodzen.setdefault('Nominalne',wartosci)
    

    return słownikUszkodzen
    
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def slownikUszkodzen2(elementy, badane_czestotliwosci,liczba_punktow_na_element,tolerancja): # elementy slownika sa macierzami numPy
    elementy_modyfikacje = copy.deepcopy( elementy )
    słownikUszkodzen = {}
    liczba_punktow_plus = liczba_punktow_minus = (liczba_punktow_na_element//2) + 1
    tolerancja = tolerancja * 100 # procenty!
    delta_minus = (100 - tolerancja -50) / liczba_punktow_minus
    delta_plus = (150 - (100 + tolerancja)) / liczba_punktow_plus

    for uszkodzony_element in elementy: # wartosci mniejsze od nominalnej
        #lista = np.zeros((liczba_punktow_minus,len(badane_czestotliwosci)))
        i = 0
        wartosci_elementu_znormalizowane = np.arange(50,100 - tolerancja + delta_minus ,delta_minus)
        indeks_ostatniego_elementu = int(wartosci_elementu_znormalizowane.shape[0]-1)
        if wartosci_elementu_znormalizowane[indeks_ostatniego_elementu] > (100 - tolerancja) :
            wartosci_elementu_znormalizowane = np.delete(wartosci_elementu_znormalizowane,indeks_ostatniego_elementu)
        indeks_ostatniego_elementu = int(wartosci_elementu_znormalizowane.shape[0]-1)
        #print((100 - tolerancja) - wartosci_elementu_znormalizowane[indeks_ostatniego_elementu])
        if ((100 - tolerancja) - wartosci_elementu_znormalizowane[indeks_ostatniego_elementu]) > 1 : # arbitralnie przyjeta wartosc
            wartosci_elementu_znormalizowane = np.concatenate( (wartosci_elementu_znormalizowane,np.array([100 - tolerancja])) )
        #print(wartosci_elementu_znormalizowane,'\n')
        lista = np.zeros((wartosci_elementu_znormalizowane.shape[0],len(badane_czestotliwosci)))
        for wartosc in wartosci_elementu_znormalizowane:
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            #print(elementy_modyfikacje)
            #print(uszkodzony_element,": ",elementy_modyfikacje[uszkodzony_element])
            (licznik, mianownik) = uklad.transmitancja(elementy_modyfikacje)
            wartosci = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci)
            lista[i] = wartosci
            i = i + 1
        słownikUszkodzen.setdefault(uszkodzony_element + '-',lista)
        elementy_modyfikacje = copy.deepcopy( elementy )

    for uszkodzony_element in elementy: # wartosci wieksze od nominalnej
        #lista = np.zeros((liczba_punktow_minus,len(badane_czestotliwosci)))
        i = 0
        wartosci_elementu_znormalizowane = np.arange(100 + tolerancja, 150 + delta_plus ,delta_plus)
        if wartosci_elementu_znormalizowane[wartosci_elementu_znormalizowane.shape[0]-1] > (150) :
            wartosci_elementu_znormalizowane = np.delete(wartosci_elementu_znormalizowane,wartosci_elementu_znormalizowane.shape[0] - 1)
        indeks_ostatniego_elementu = int(wartosci_elementu_znormalizowane.shape[0]-1)
        if (150 - wartosci_elementu_znormalizowane[indeks_ostatniego_elementu]) > 1 : # arbitralnie przyjeta wartosc
            wartosci_elementu_znormalizowane = np.concatenate( (wartosci_elementu_znormalizowane,np.array([150])) )
        #print(wartosci_elementu_znormalizowane,'\n')
        lista = np.zeros((wartosci_elementu_znormalizowane.shape[0],len(badane_czestotliwosci)))
        for wartosc in wartosci_elementu_znormalizowane:
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            #print(elementy_modyfikacje)
            #print(uszkodzony_element,": ",elementy_modyfikacje[uszkodzony_element])
            (licznik, mianownik) = uklad.transmitancja(elementy_modyfikacje)
            wartosci = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci)
            lista[i] = wartosci
            i = i + 1
        słownikUszkodzen.setdefault(uszkodzony_element + '+',lista)
        elementy_modyfikacje = copy.deepcopy( elementy )

    (licznik, mianownik) = uklad.transmitancja(elementy)
    wartosci = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci)
    słownikUszkodzen.setdefault('Nominalne',wartosci)
    

    return słownikUszkodzen
    
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
            print(e1,' | ',e2)
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

def wyrysujKrzyweIdentyfikacyjne2D(slownik_uszkodzen,badane_czestotliwosci):
    plt.clf()
    i = 0
    for uszkodzenie in slownik_uszkodzen:
        if uszkodzenie == 'Nominalne' :
            plt.plot(slownik_uszkodzen[uszkodzenie][0],slownik_uszkodzen[uszkodzenie][1],'o-', label = uszkodzenie)
        else :
            liczba_punktow = len( slownik_uszkodzen[uszkodzenie] )
            liczba_czestotliwosci = len( badane_czestotliwosci )
            lista = []
            for j in range( liczba_czestotliwosci ):
                lista.append([])
                for i in range( liczba_punktow ):
                    lista[j].append(slownik_uszkodzen[uszkodzenie][i][j])
            plt.plot(lista[0],lista[1],'o-', label = uszkodzenie)
    plt.title('ROZSTRAJANIE ELEMENTOW')
    plt.xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    plt.ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    plt.legend()
    plt.show()

#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne2DdB(slownik_uszkodzen,badane_czestotliwosci):
    plt.clf()
    i = 0
    for uszkodzenie in slownik_uszkodzen:
        if uszkodzenie == 'Nominalne' :
            plt.plot(20*np.log10(slownik_uszkodzen[uszkodzenie][0]),20*np.log10(slownik_uszkodzen[uszkodzenie][1]),'o-', label = uszkodzenie)
        else :
            liczba_punktow = len( slownik_uszkodzen[uszkodzenie] )
            liczba_czestotliwosci = len( badane_czestotliwosci )
            lista = []
            for j in range( liczba_czestotliwosci ):
                lista.append([])
                for i in range( liczba_punktow ):
                    lista[j].append(slownik_uszkodzen[uszkodzenie][i][j])
            plt.plot(20*np.log10(lista[0]),20*np.log10(lista[1]),'o-', label = uszkodzenie)
    plt.title('ROZSTRAJANIE ELEMENTOW')
    plt.xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    plt.ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    plt.legend()
    plt.show()

#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne2D_i_Pomiar(slownik_uszkodzen,badane_czestotliwosci,pomiar):
    plt.clf()
    i = 0
    for uszkodzenie in slownik_uszkodzen:
        if uszkodzenie == 'Nominalne' :
            plt.plot(slownik_uszkodzen[uszkodzenie][0],slownik_uszkodzen[uszkodzenie][1],'o-', label = uszkodzenie)
        else :
            liczba_punktow = len( slownik_uszkodzen[uszkodzenie] )
            liczba_czestotliwosci = len( badane_czestotliwosci )
            lista = []
            for j in range( liczba_czestotliwosci ):
                lista.append([])
                for i in range( liczba_punktow ):
                    lista[j].append(slownik_uszkodzen[uszkodzenie][i][j])
            plt.plot(lista[0],lista[1],'o-', label = uszkodzenie)
    plt.plot(pomiar[0],pomiar[1],'o-', label = 'Pomiar')
    plt.title('ROZSTRAJANIE ELEMENTOW')
    plt.xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    plt.ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    plt.legend()
    plt.show()

#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne3D(slownik_uszkodzen,badane_czestotliwosci):
    #plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    i = 0
    for uszkodzenie in slownik_uszkodzen:
        if uszkodzenie == 'Nominalne' :
            continue
            #ax.plot(slownik_uszkodzen[uszkodzenie][0],slownik_uszkodzen[uszkodzenie][1],slownik_uszkodzen[uszkodzenie][2],'o-', label = uszkodzenie)
        else :
            liczba_punktow = len( slownik_uszkodzen[uszkodzenie] )
            liczba_czestotliwosci = len( badane_czestotliwosci )
            lista = []
            for j in range( liczba_czestotliwosci ):
                lista.append([])
                for i in range( liczba_punktow ):
                    lista[j].append(slownik_uszkodzen[uszkodzenie][i][j])
            ax.plot(lista[0],lista[1],lista[2],'o-', label = uszkodzenie)
            #print(lista)
    ax.set_xlabel('|H('+str(badane_czestotliwosci[0])+' Hz)|')
    ax.set_ylabel('|H('+str(badane_czestotliwosci[1])+' Hz)|')
    ax.set_zlabel('|H('+str(badane_czestotliwosci[2])+' Hz)|')
    ax.legend()
    plt.show()

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def slownikUszkodzen_z_nominalnym(elementy, badane_czestotliwosci,liczba_punktow_na_element):
    elementy_modyfikacje = copy.deepcopy( elementy )
    słownikUszkodzen = {}
    liczba_punktow_plus = liczba_punktow_minus = liczba_punktow_na_element//2
    delta_minus = (100-50) / liczba_punktow_minus
    delta_plus = (100-150) / liczba_punktow_plus

    for uszkodzony_element in elementy: # wartosci mniejsze od nominalnej
        lista = []
        wartosci_elementu_znormalizowane = np.arange(50,100+delta_minus,delta_minus)
        for wartosc in wartosci_elementu_znormalizowane:
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            #print(uszkodzony_element,": ",elementy_modyfikacje[uszkodzony_element])
            (licznik, mianownik) = uklad.transmitancja(elementy_modyfikacje)
            wartosci = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci)
            lista.append(wartosci)
        słownikUszkodzen.setdefault(uszkodzony_element + '-',lista)
        elementy_modyfikacje = copy.deepcopy( elementy )

    for uszkodzony_element in elementy: # wartosci wieksze od nominalnej
        lista = []
        wartosci_elementu_znormalizowane = np.arange(150,100 + delta_plus,delta_plus)
        for wartosc in wartosci_elementu_znormalizowane:
            elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * wartosc/100
            #print(uszkodzony_element,": ",elementy_modyfikacje[uszkodzony_element])
            (licznik, mianownik) = uklad.transmitancja(elementy_modyfikacje)
            wartosci = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci)
            lista.append(wartosci)
        słownikUszkodzen.setdefault(uszkodzony_element + '+',lista)
        elementy_modyfikacje = copy.deepcopy( elementy )

    (licznik, mianownik) = uklad.transmitancja(elementy)
    wartosci = charCzestotliwosciowaModul(licznik, mianownik,badane_czestotliwosci)
    słownikUszkodzen.setdefault('Nominalne',wartosci)
    

    return słownikUszkodzen
    
#------------------------------------------------------------------------------
#                         PCA
#------------------------------------------------------------------------------
def wygenerujMacierzDanychPCA(elementy,czestotliwosci,liczba_losowanMC,tolerancja_elementow,liczba_punktow):
    """
    GENERUJEMY MACIERZ DANYCH DO ANALIZY PCA
    KAZDA KOLUMNA MACIERZY ODPOWIADA JEDNEMU WEKTOROWI POMIAROWEMU
    """
    elementy_modyfikacje = copy.deepcopy( elementy )
    czestotliwosci = np.asarray(czestotliwosci)
    liczba_czestotliwosci = czestotliwosci.shape[0]
    L = 1 - tolerancja_elementow
    H = 1 + tolerancja_elementow
    delta = (150 - 50) / liczba_punktow
    liczba_elementow = len(list(elementy.keys()))
    
    wartosci_uszkodzenia = np.arange(50,150+delta,delta) # uszkodzenia
    
    liczba_wierszy = liczba_losowanMC * liczba_elementow * (wartosci_uszkodzenia.shape[0])
    licznik = 0
    
    X_t = np.zeros( ( liczba_wierszy , liczba_czestotliwosci ) )
    for uszkodzony_element in elementy:     # wybor elementu do uszkodzenia
        for uszkodzenie in wartosci_uszkodzenia: # wszystkie mozliwe uszkodzenia DANEGO ELEMENTU
            #if uszkodzenie == 10 : continue
            for i in range(liczba_losowanMC): # MonteCarlo
                for element in elementy_modyfikacje: # tolerancje
                    elementy_modyfikacje[element] = elementy[element] * (np.random.uniform(L,H))
                elementy_modyfikacje[uszkodzony_element] = elementy[uszkodzony_element] * uszkodzenie / 100
                l, m = uklad.transmitancja(elementy_modyfikacje)
                X_t[licznik] = charCzestotliwosciowaModul(l, m,czestotliwosci)
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
