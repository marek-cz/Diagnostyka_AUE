"""
Modul do generacji sygnalow
"""

import numpy as np

sinus = np.load('sygnaly/sinus_uint16.npy')
multisin = np.load('sygnaly/multisin_probki_uint16.npy')
sinc = np.load('sygnaly/sinc_uint16.npy')

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


def TransformataFouriera(sygnal, frq):
    """
    Funckja wyznaczająca transformate Fouriera dla liniowej aproksymacji sygnalu
    na częstotliwości (częstotliwościach) zawartych w frq - wektor w ktorym rosnaco
    sa zapsiane czestotliwosci od f_min do f_max
    """
    i = 0
    ReU = np.zeros(len(frq))
    ImU = np.zeros(len(frq))
    T_ack = 1/frq[0]    # czas akwizycji
    N = len(sygnal)     # liczba probek

    tn = np.arange(0, T_ack, (T_ack / N) )    # wektor czasow
    un = sygnal.astype('float32')     # dla uproszczenia zapisu
    un -= un[0]         # usuniecie skladowej stalej interpretowanej przez TF jako impuls prostokatny
    un = un/4095
    for f in frq:
        w = 2 * np.pi * f
        sin_w_tn = np.sin(w*tn)
        cos_w_tn = np.cos(w*tn)
        du_dt = ( ( un[1:] - un[:-1] ) / ( tn[1:] - tn[:-1] ) )
        
        ReU[i] = sum( ( 1/w)*( un[1:] * sin_w_tn[1:] - un[:-1] * sin_w_tn[:-1] ) + du_dt * ((cos_w_tn[1:] - cos_w_tn[:-1]) / (w*w) ) )
        ImU[i] = sum( (-1/w)*( un[1:] * cos_w_tn[1:] - un[:-1] * cos_w_tn[:-1] ) + du_dt * ((sin_w_tn[1:] - sin_w_tn[:-1]) / (w*w) ) )
        
        i = i + 1
    
    modul = np.sqrt( ReU*ReU + ImU * ImU )
    #return (ReU,ImU)
    return modul

    
