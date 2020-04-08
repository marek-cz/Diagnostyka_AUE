"""MODUL Z FUNKCJAMI"""
import numpy as np
import matplotlib.pyplot as plt
import struct

def wyrysuj_okres(dane,widmo,frq):
    

    widmo_dB = 20 * np.log10(widmo)

    fig, ax = plt.subplots(2,1)
    ax[0].plot(dane,'bo-')
    ax[0].set_xlabel('Probka n')
    ax[0].set_ylabel('U(t) [V]')
    ax[0].set_title('Probki z ADC')
    ax[1].plot( frq,widmo_dB,'bo') # plotting the spectrum
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
    
#-------------------------------------------------------------------------------------------

def listUint2Float(lista_uint):
    y = []
    for wartosc in lista_uint :
        y.append( int(wartosc) )
    return struct.unpack('<f', struct.pack('4b', *y))[0]


