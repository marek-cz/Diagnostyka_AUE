"""
Modul do generacji sygnalow
"""

import numpy as np

sinus = np.load('sygnaly/sinus_uint16.npy')
multisin = np.load('sygnaly/multisin_probki_uint16.npy')

def widmo(sygnal,f,Fs = 500):
    DAC_MAX = 4096
    DAC_VREF = 1.0
    sygnal = DAC_VREF * (sygnal / DAC_MAX)
    n = len(sygnal) # length of the signal
    k = np.arange(n)
    T = n/Fs
    frq = k * T # two sides frequency range
    frq = frq[range(int(n/2))] # one side frequency range

    Y = np.fft.fft(sygnal)/n # fft computing and normalization
    Y = Y[range(int(n/2))]

    modul = abs(Y)
    szukane_widmo = []
    f = f // f[0]
    f = f.astype('uint16')
    #print(f)
    for F in f :
        szukane_widmo.append(modul[F])
    szukane_widmo = np.asarray(szukane_widmo)       
    return  szukane_widmo
