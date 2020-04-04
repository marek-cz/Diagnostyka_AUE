""" CHARAKTERYSTYKA FILTRU TOW - THOMSONA
    NA WYKRESACH RÓWNIEZ ANALIZA TOLERANCJI
    MONTE CARLO"""

# Biblioteki

import matplotlib.pyplot as plt
import numpy as np
import random
import copy
import funkcjeUkladowe


import uklad

#------------------------------------------------------------------------------
def wyrysujCharakterystyki(elementy,f):
    """Wyrysowanie charakterystyk uwzgledniajacych tolerancje elementow"""

    elementy_modyfikacje = copy.deepcopy( elementy  ) 
    minimum = 10000* np.ones(f.shape[0])
    maksimum = np.zeros(f.shape[0])
    plt.clf()
    for i in range (10):
        for element in elementy :
            if element.find('R') != -1 :
                #element jest Rezystorem
                a = 1 - uklad.TOLERANCJA['R']
                b = 1 + uklad.TOLERANCJA['R']
            elif element.find('C') != -1:
                a = 1 - uklad.TOLERANCJA['C']
                b = 1 + uklad.TOLERANCJA['C']
            else :
                print('kaszana!')
            elementy_modyfikacje[element] = elementy[element] * (random.uniform(a,b))
            (licznik, mianownik) = uklad.transmitancja(elementy_modyfikacje)
            h = funkcjeUkladowe.charCzestotliwosciowaModul(licznik, mianownik,f)
            #if h[150] > maksimum[150] : maksimum = h
            #if h[150] < minimum[150] : minimum = h
            plt.plot(f, 20 * np.log10(abs(h)),'r')
    #plt.plot(f, 20 * np.log10(abs(maksimum)),'r')
    #print(f,len(f))
    (licznik, mianownik) = uklad.transmitancja(uklad.elementy)
    h = funkcjeUkladowe.charCzestotliwosciowaModul(licznik, mianownik,f)
    plt.plot(f, 20 * np.log10(abs(h)),'b',label = 'Nominalna')
    plt.semilogx()
    plt.title('Charakterystyka amplitudowa filtru')
    plt.xlabel('Częstotliwość [Hz]')
    plt.ylabel('|H| [dB]')
    plt.margins(0, 0.1)
    plt.grid(which='both', axis='both')
    plt.legend()
    plt.show()
    
#------------------------------------------------------------------------------
# 2. TRANSMITANCJA 
(licznik, mianownik) = uklad.transmitancja(uklad.elementy)


plt.rc('axes', labelsize = 14)
plt.rc('xtick', labelsize=12)
plt.rc('ytick', labelsize=12) 

f = np.arange(1,5000,1)

# na podstawie dokumentacji scipy
wyrysujCharakterystyki(uklad.elementy,f)
