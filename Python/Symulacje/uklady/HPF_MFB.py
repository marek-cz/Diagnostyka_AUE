"""
PLIK ZAWIERAJACY OPIS BADANEGO UKŁADU
"""

import numpy as np




#------------------------------------------------------------------------------
def transmitancja(elementy):
    licznik_wyraz_wolny = 0
    licznik_przy_s = 0
    licznik_przy_s2 = (-1) * elementy['C1']/elementy['C2']
    mianownik_wyraz_wolny = 1/(elementy['R1'] * elementy['R2'] * elementy['C2'] * elementy['C3'])
    mianownik_przy_s = (elementy['C1'] + elementy['C2'] + elementy['C3']) / (elementy['R1'] * elementy['C2'] * elementy['C3'])
    mianownik_przy_s2 = 1
    licznik = [licznik_przy_s2,licznik_przy_s,licznik_wyraz_wolny]
    mianownik = [mianownik_przy_s2 ,mianownik_przy_s, mianownik_wyraz_wolny]
    return (licznik, mianownik)

#------------------------------------------------------------------------------
# 1. ELEMENTY - wartości nominalne
k = 1e3
u = 1e-6
n = 1e-9

R1 = 100 * k
R2 = 10 * k

C1 = 47 * n
C2 = 47 * n
C3 = 47 * n

elementy = {'R1' : R1,'R2' : R2,'C1' : C1,'C2' : C2,'C3' : C3}

TOLERANCJA = {'R' : 0.05, 'C' : 0.05}

#------------------------------------------------------------------------------------
# 2. BADANE CZESTOTLIWOSCI
BADANE_CZESTOTLIWOSCI = np.array([50,100,150])
#BADANE_CZESTOTLIWOSCI = np.array([100,150])
#------------------------------------------------------------------------------------
# 3. LICZBA PUNKTOW NA ELEMENT
LICZBA_PUNKTOW = 12
#------------------------------------------------------------------------------------
# 4. Epsilon
epsilon = 0.01
#------------------------------------------------------------------------------------
# 5. LICZBA LOSOWAN W ANALIZE MONTE CARLO -> PCA
LICZBA_LOSOWAN_MC = 500
# 6. PCA - PROG WARIANCJI - DO OKRESLENIA LICZBY SKLADOWYCH GLOWNYCH -  W PROCENTACH!
PCA_PROG = 99 # [%]
