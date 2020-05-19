"""MODUL Z FUNKCJAMI"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import struct

plt.rc('axes', labelsize = 18)
plt.rc('xtick', labelsize = 16)
plt.rc('ytick', labelsize = 16)

def wyrysuj_okres(dane, pobudzenie, widmo,frq,typ_pomiaru):
    
    typ_rysowania = 'bo'
    sygnal = np.asarray(dane).astype('float64')
    if typ_pomiaru == 'TF' :
        typ_rysowania = 'b-'
        sygnal -= dane[0]
    else :
        sygnal -= sygnal.mean()
        

    
    widmo_dB = 20 * np.log10(widmo)

    fig, ax = plt.subplots(2,1)
    ax[0].plot(sygnal,'b-', label = 'Pomiar', linewidth = 4)
    ax[0].plot(pobudzenie,'r-', label = 'Sygnał generowany', linewidth = 4)
    ax[0].set_xlabel('Próbka n', fontsize=18)
    ax[0].set_ylabel('U(t) [V]', fontsize=18)
    ax[0].set_title('Przebiegi czasowe', fontsize=20)
    ax[1].plot( frq,widmo_dB,typ_rysowania, label = 'Pomiar', linewidth = 4) # plotting the spectrum
    ax[1].set_xscale('log')
    ax[1].set_xlabel('Częstotliwość [Hz]', fontsize=18)
    ax[1].set_ylabel('|Y(f)| [dB]', fontsize=18)
    ax[1].set_title('Widmo aplitudowe pomiaru', fontsize=20)

    ax[0].legend(loc="upper right", prop={'size': 16})
    ax[0].grid()
    ax[1].legend(loc="upper right", prop={'size': 16})
    ax[1].grid()
    plt.subplots_adjust(top = 0.92, bottom = 0.15 , hspace = 0.6)
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
#-------------------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne2D(slownik_uszkodzen):
    #plt.clf()
    for uszkodzenie in slownik_uszkodzen:
        #if uszkodzenie == 'Nominalne' :
            #continue
        A = slownik_uszkodzen[uszkodzenie]
        A = np.transpose(A)
        plt.plot(A[0],A[1],'o-', label = uszkodzenie)
    plt.xlabel('PCA 1', fontsize=20)
    plt.ylabel('PCA 2', fontsize=20)
    plt.axis('equal')
    plt.grid()
    plt.legend(prop={'size': 22})
    plt.show()

#-------------------------------------------------------------------------------------------
def wyrysujKrzyweIdentyfikacyjne3D(slownik_uszkodzen, tablica_pomiarow = 0):
    #plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    for uszkodzenie in slownik_uszkodzen:
        #if uszkodzenie == 'Nominalne' : ax.plot(A[0][:1],A[1][:1],A[2][:1],'ko-', label = uszkodzenie)
        A = slownik_uszkodzen[uszkodzenie]
        A = np.transpose(A)
        if uszkodzenie == 'Nominalne' :
            A = A.reshape( (3,1) )
            ax.plot(A[0][:],A[1][:],A[2][:],'o', label = uszkodzenie)
        else : ax.plot(A[0],A[1],A[2],'o-', label = uszkodzenie)

    if (type(tablica_pomiarow) is np.ndarray ):  # sprawdzenie czy sa pomiary
        ax.plot(tablica_pomiarow[0],tablica_pomiarow[1],tablica_pomiarow[2],'ko', label = "Pomiar")
    ax.set_xlabel('PCA 1', fontsize=20)
    ax.set_ylabel('PCA 2', fontsize=20)
    ax.set_zlabel('PCA 3', fontsize=20)
    ax.legend(prop={'size': 22})
    plt.grid()
    plt.show()

#-------------------------------------------------------------------------------------------
    
def wyznaczElipse(macierz_skalujaca, odleglosc_Mahalanobisa, srodek):
    """
    Na podstawie macierzy skalujacej i zadanej granicznej odleglosci
    Mahalanobisa generuje tablice x i y opisujace elipse o dlugosci
    polosi wielkiej rownej granicznej odleglosci Mahalanobisa
    """
    A = macierz_skalujaca[0][0]
    B = macierz_skalujaca[1][0] # moze byc rowniez [0][1]
    C = macierz_skalujaca[1][1]

    # wyznaczenie parametrow elipsy na podstawie macierzy :
    alfa = 0.5 * np.arctan( 2*B / (A-C)) # kat pocylenia elipsy
    s = np.sin(alfa) * np.cos(alfa) # pomocnicza zmienna skalujaca
    a2 = (A+C - (B/s))/2
    b2 = (A+C + B/s) / 2
    a = np.sqrt(a2) # dlugosc jednej  z polosi
    b = np.sqrt(b2) # dlugosc drugiej z polosi

    k = a/b # stosunek dlugosci polosi

    # przeskalowanie polosi do wartosci odleglosci Mahalanobisa

    a = odleglosc_Mahalanobisa
    b = odleglosc_Mahalanobisa / k

    # wyznaczenie tablic x i y
    t = np.linspace(0, 2 * np.pi,628) # parametr - kat
    x = srodek[0]+a*np.cos(t)*np.cos(alfa) - b*np.sin(t)*np.sin(alfa)
    y = srodek[1]+a*np.cos(t)*np.sin(alfa) + b*np.sin(t)*np.cos(alfa)

    x = x.reshape((x.shape[1],))
    y = y.reshape((y.shape[1],))
    
    return x,y
#-------------------------------------------------------------------------------------------

def TransformataFourieraSinc(sygnal,tn,frq):
    i = 0
    ReU = np.zeros(len(frq))
    ImU = np.zeros(len(frq))
    #un = un/4095 # wyniki sa juz w postaci napiecia!
    un = sygnal - sygnal[0]
    #print(un.shape)
    #print(tn.shape)
    for f in frq:
        w = 2 * np.pi * f
        sin_w_tn = np.sin(w*tn)
        cos_w_tn = np.cos(w*tn)
        du_dt = ( ( un[1:] - un[:-1] ) / ( tn[1:] - tn[:-1] ) )
        
        ReU[i] = sum( ( 1/w)*( un[1:] * sin_w_tn[1:] - un[:-1] * sin_w_tn[:-1] ) + du_dt * ((cos_w_tn[1:] - cos_w_tn[:-1]) / (w*w) ) )
        ImU[i] = sum( (-1/w)*( un[1:] * cos_w_tn[1:] - un[:-1] * cos_w_tn[:-1] ) + du_dt * ((sin_w_tn[1:] - sin_w_tn[:-1]) / (w*w) ) )
        
        i = i + 1
    
    return (ReU,ImU)
