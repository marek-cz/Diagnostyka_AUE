"""MODUL Z FUNKCJAMI"""
import numpy as np
import matplotlib.pyplot as plt

def wyrysuj_okres(dane):        
    dane = np.asarray(dane).astype('uint16')

    dane = dane / 4095 
        
    Fs = 1000
    n = len(dane) # length of the signal
    k = np.arange(n)
    T = n/Fs
    frq = k/T # two sides frequency range

    frq = frq[range(int(n/2))] # one side frequency range

    #Y = np.fft.fft(dane - dane.mean())/n # usuniecie wartosci sredniej
    Y = np.fft.fft(dane)/n # fft computing and normalization
    Y = Y[range(int(n/2))]

    Y_abs = np.abs(Y)
    Y_abs /= Y_abs[1:].max()
    
    Y_abs_dB = 20 * np.log10(Y_abs)


    fig, ax = plt.subplots(2,1)
    ax[0].plot(dane,'b')
    ax[0].set_xlabel('Probka n')
    ax[0].set_ylabel('Amplituda [V]')
    ax[0].set_title('Probki z ADC')
    #ax[1].plot(frq,np.abs(Y),'bo') # plotting the spectrum
    ax[1].plot( frq ,Y_abs_dB,'bo') # plotting the spectrum
    ax[1].set_xscale('log')
    ax[1].set_xlabel('Czestotliwosc [Hz]')
    ax[1].set_ylabel('|Y(f)| dB')
    ax[1].set_title('Widmo')


    plt.show()

def wyrysuj(dane):        
    dane = np.asarray(dane).astype('uint16')

    dane = dane / 4095
    plt.clf()
    plt.plot(dane)
    plt.show()
    
def DaneStr2Lista(dane_string):
    print("kupa")
