"""
PLIK ZAWIERAJACY OPIS BADANEGO UKŁADU
"""

import numpy as np




#------------------------------------------------------------------------------
def transmitancja(elementy):
    licznik_wyraz_wolny = (-elementy['R6']) / (elementy['R1']*elementy['R4']*elementy['R5']*elementy['C1']*elementy['C2'])
    mianownik_wyraz_wolny = (elementy['R6']) / (elementy['R3']*elementy['R4']*elementy['R5']*elementy['C1']*elementy['C2'])
    mianownik_przy_s = (1) / (elementy['R2'] * elementy['C1'])
    mianownik_przy_s2 = 1
    licznik = [licznik_wyraz_wolny]
    mianownik = [mianownik_przy_s2 ,mianownik_przy_s, mianownik_wyraz_wolny]
    return (licznik, mianownik)

#------------------------------------------------------------------------------
# 1. ELEMENTY - wartości nominalne
k = 1e3;
n = 1e-9;

R1 = 10 * k
R2 = 10 * k
R3 = 10 * k
R4 = 10 * k
R5 = 10 * k
R6 = 10 * k

C1 = 100 * n
C2 = 100 * n

elementy = {'R1' : R1,'R2' : R2,'R3' : R3,'R4' : R4,'R5' : R5,'R6' : R6,'C1' : C1,'C2' : C2}

TOLERANCJA = {'R' : 0.05, 'C' : 0.05}

#------------------------------------------------------------------------------------
# 2. BADANE CZESTOTLIWOSCI
#BADANE_CZESTOTLIWOSCI_MULTISIN = np.array([1,2,3,4,5,6,7,8,9,10]) * 20 # czestotliwosci dla pobudzenia wieloharmonicznego
CZESTOTLIWOSC_PODSTAWOWA_MULTISIN = 20 # czestotliwosc podstawowa sygnalu wieloharmonicznego
BADANE_CZESTOTLIWOSCI_SINC = np.array([5,6,7,8,9,10,11,12,13,14]) * 10  # czestotliwosci dla pobudzenia SINC
#------------------------------------------------------------------------------------
# 3. LICZBA LOSOWAN W ANALIZE MONTE CARLO -> PCA
LICZBA_LOSOWAN_MC = 10000
# 6. Liczba losowan do badania obszaru nominalnego
LICZBA_LOSOWAN_PUNKT_NOMINALNY = 100000