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
    (licznik, mianownik) = uklad.transmitancja(uklad.elementy)
    h_nom = funkcjeUkladowe.charCzestotliwosciowaModul(licznik, mianownik,f)
    H = np.asarray(h_nom)
    for i in range (200):
##        for element in elementy :
##            if element.find('R') != -1 :
##                #element jest Rezystorem
##                a = 1 - uklad.TOLERANCJA['R']
##                b = 1 + uklad.TOLERANCJA['R']
##            elif element.find('C') != -1:
##                a = 1 - uklad.TOLERANCJA['C']
##                b = 1 + uklad.TOLERANCJA['C']
##            else :
##                print('kaszana!')
##            elementy_modyfikacje[element] = elementy[element] * (random.uniform(a,b))
        elementy_modyfikacje = funkcjeUkladowe.losowanieRozkladNormalny(elementy, funkcjeUkladowe.uklad.TOLERANCJA)
        (licznik, mianownik) = uklad.transmitancja(elementy_modyfikacje)
        h = funkcjeUkladowe.charCzestotliwosciowaModul(licznik, mianownik,f)
        #if h[150] > maksimum[150] : maksimum = h
        #if h[150] < minimum[150] : minimum = h
        plt.plot(f, 20 * np.log10(abs(h)),'r',linewidth=4)
        H = np.concatenate( (H, h) )
    #plt.plot(f, 20 * np.log10(abs(maksimum)),'r')
    #print(f,len(f))
    plt.plot(f, 20 * np.log10(abs(h)),'r', label = 'Losowania' ,linewidth=4)
    plt.plot(f, 20 * np.log10(abs(h_nom)),'b',label = 'Nominalna',linewidth=4)
    plt.semilogx()
    plt.title('Charakterystyka amplitudowa filtru', fontsize=26)
    plt.xlabel("Częstotliwość [Hz]", fontsize=30)
    plt.ylabel('|H(f)| [dB]', fontsize=30)
    plt.axis('equal')
    plt.grid()
    plt.legend(prop={'size': 30})
    plt.show()
    plt.show()

    return H
    
#------------------------------------------------------------------------------
# 2. TRANSMITANCJA 
(licznik, mianownik) = uklad.transmitancja(uklad.elementy)


##plt.rc('axes', labelsize = 14)
##plt.rc('xtick', labelsize=12)
##plt.rc('ytick', labelsize=12) 

f = np.logspace(1,3,1000)

# na podstawie dokumentacji scipy
H = wyrysujCharakterystyki(uklad.elementy,f)

H = H.reshape ( ( H.shape[0] // f.shape[0], f.shape[0] ) )
var = H.var(axis = 0)

plt.semilogx(f, var,'b',linewidth=4)
plt.title('Wariancja charakterystyki amplitudowej', fontsize=26)
plt.xlabel("Częstotliwość [Hz]", fontsize=30)
plt.ylabel('Wariancja |H(f)| [V/V]', fontsize=30)
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
plt.grid()
plt.show()
plt.show()
