"""
PLIK ZAWIERAJACY OPIS BADANEGO UKŁADU
"""

import numpy as np




#------------------------------------------------------------------------------
def transmitancja(elementy):
    licznik_wyraz_wolny = (-elementy['R3']) / (elementy['R1'])
    mianownik_wyraz_wolny = 1
    mianownik_przy_s = elementy['C2'] * (elementy['R2'] + elementy['R3'] + ( (elementy['R2']*elementy['R3'])/(elementy['R1']) ) )
    mianownik_przy_s2 = elementy['R2']*elementy['R3']*elementy['C1']*elementy['C2']
    licznik = [licznik_wyraz_wolny]
    mianownik = [mianownik_przy_s2 ,mianownik_przy_s, mianownik_wyraz_wolny]
    return (licznik, mianownik)

#------------------------------------------------------------------------------
# 1. ELEMENTY - wartości nominalne
k = 1e3
u = 1e-6
n = 1e-9

R1 = 10 * k
R2 = 10 * k
R3 = 10 * k

C1 = 470 * n
C2 = 47 * n

elementy = {'R1' : R1,'R2' : R2,'R3' : R3,'C1' : C1,'C2' : C2}

TOLERANCJA = 0.05

#------------------------------------------------------------------------------------
# 2. BADANE CZESTOTLIWOSCI
BADANE_CZESTOTLIWOSCI = np.array([50,100,150])
#BADANE_CZESTOTLIWOSCI = np.array([40,80,120])
#------------------------------------------------------------------------------------
# 3. LICZBA PUNKTOW NA ELEMENT
LICZBA_PUNKTOW = 12
#------------------------------------------------------------------------------------
# 4. Epsilon
epsilon = 0.001
#------------------------------------------------------------------------------------
# 5. LICZBA LOSOWAN W ANALIZE MONTE CARLO -> PCA
LICZBA_LOSOWAN_MC = 500
# 6. PCA - PROG WARIANCJI - DO OKRESLENIA LICZBY SKLADOWYCH GLOWNYCH -  W PROCENTACH!
PCA_PROG = 99 # [%]
