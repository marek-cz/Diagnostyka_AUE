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

C1 =  45.37 * n
C2 =  49.77 * n
C3 =  45.47 * n


elementy = {'R1' : R1,'R2' : R2,'C1' : C1,'C2' : C2,'C3' : C3}

TOLERANCJA = {'R' : 0.01, 'C' : 0.04}

#------------------------------------------------------------------------------------
# 2. BADANE CZESTOTLIWOSCI
CZESTOTLIWOSC_PODSTAWOWA_MULTISIN = 20 # czestotliwosc podstawowa sygnalu wieloharmonicznego
BADANE_CZESTOTLIWOSCI_SINC = np.array([5,6,7,8,9,10,11,12,13,14]) * 10  # czestotliwosci dla pobudzenia SINC
#------------------------------------------------------------------------------------
# 3. LICZBA LOSOWAN W ANALIZE MONTE CARLO -> PCA
LICZBA_LOSOWAN_MC = 10000
# 6. Liczba losowan do badania obszaru nominalnego
LICZBA_LOSOWAN_PUNKT_NOMINALNY = 100000
