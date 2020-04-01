"""
Modul do generacji sygnalow
"""

import numpy as np

def multisin(f,fazy = np.array([]),LICZBA_PROBEK = 500,OFFSET = 250):
    f = np.asarray(f)
    liczba_harmonicznych = f.shape[0]
    t = np.arange(0,1, (1/LICZBA_PROBEK))
    sygnal = 0
    DAC_MAX = 4095
    if fazy.shape[0] == 0 :
        fazy = np.load("../../../Symulacje/fazy_optymalne.npy")
    for i in range(liczba_harmonicznych) :
        sygnal += np.sin( 2*np.pi*f[i]*t + fazy[i] )
    
    if np.min(sygnal) < 0 :
        sygnal -= np.min(sygnal) # odejmujemy ujemna -> dodajemy
    
    sygnal /= sygnal.max()
    sygnal *= (DAC_MAX-OFFSET) / DAC_MAX
    return sygnal

def widmoMultisin(sygnal,f,Fs = 500):
    n = len(sygnal) # length of the signal
    k = np.arange(n)
    T = n/Fs
    frq = k/T # two sides frequency range
    frq = frq[range(int(n/2))] # one side frequency range

    Y = np.fft.fft(sygnal)/n # fft computing and normalization
    Y = Y[range(int(n/2))]

    modul = abs(Y)
    szukane_widmo = []
    for F in f :
        szukane_widmo.append(modul[F])
    szukane_widmo = np.asarray(szukane_widmo)       
    return szukane_widmo
