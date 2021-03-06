import funkcjeUkladowe

PROG = 0.9973 # 3 sigma
DELTA_S_CONST = funkcjeUkladowe.np.array([[5e-5]])

#---------------------------------------------------------------
def odlegloscMahalanobisa(x,y,C):
    """
    Odleglosc Mahalanobisa miedzy punktami x i y
    z zastosowaniem macierzy skalujacej C
    """
    x = x.reshape((x.shape[0],1)) # wektor kolumnowy
    y = y.reshape((y.shape[0],1)) # wektor kolumnowy
    d = x - y
    s = funkcjeUkladowe.np.matmul(funkcjeUkladowe.np.transpose(d), C)
    s = funkcjeUkladowe.np.matmul( s , d)
    return funkcjeUkladowe.np.sqrt(s)

#---------------------------------------------------------------
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
    alfa = 0.5 * funkcjeUkladowe.np.arctan( 2*B / (A-C)) # kat pocylenia elipsy
    s = funkcjeUkladowe.np.sin(alfa) * funkcjeUkladowe.np.cos(alfa) # pomocnicza zmienna skalujaca
    a2 = (A+C - (B/s))/2
    b2 = (A+C + B/s) / 2
    a = funkcjeUkladowe.np.sqrt(a2) # dlugosc jednej  z polosi
    b = funkcjeUkladowe.np.sqrt(b2) # dlugosc drugiej z polosi

    k = a/b # stosunek dlugosci polosi

    # przeskalowanie polosi do wartosci odleglosci Mahalanobisa

    a = odleglosc_Mahalanobisa
    b = odleglosc_Mahalanobisa / k

    # wyznaczenie tablic x i y
    t = funkcjeUkladowe.np.linspace(0, 2 * funkcjeUkladowe.np.pi,628) # parametr - kat
    x = srodek[0]+a*funkcjeUkladowe.np.cos(t)*funkcjeUkladowe.np.cos(alfa) - b*funkcjeUkladowe.np.sin(t)*funkcjeUkladowe.np.sin(alfa)
    y = srodek[1]+a*funkcjeUkladowe.np.cos(t)*funkcjeUkladowe.np.sin(alfa) + b*funkcjeUkladowe.np.sin(t)*funkcjeUkladowe.np.cos(alfa)

    x = x.reshape((x.shape[1],))
    y = y.reshape((y.shape[1],))
    
    return x,y
###########################################################################################################
def wyznaczMacierzSkalujaca(Klaster_danych):
    liczba_pomiarow = Klaster_danych.shape[1] # liczba pomiarow
    C = funkcjeUkladowe.np.cov( Klaster_danych ) # wyznaczanie macierzy kowariancji
    C_inv = funkcjeUkladowe.np.linalg.inv(C) # odwrocenie macierzy kowariancji
    wartosci_wlasne, wektory_wlasne = funkcjeUkladowe.np.linalg.eig( C_inv ) # wyznaczenie wektorow i wartosci wlasnych macierzy odwrotnej do macierzy kowariancji

    lambda_min = wartosci_wlasne.min()
    LAMBDA_diag = funkcjeUkladowe.np.diag( wartosci_wlasne / lambda_min ) # normowanie wartosci wlasnych
    U = wektory_wlasne

    C1 = funkcjeUkladowe.np.matmul( funkcjeUkladowe.np.matmul( U, LAMBDA_diag ), funkcjeUkladowe.np.transpose(U) ) # wyznaczenie unormowanej macierzy skalujacej

    return C1
###########################################################################################################
def wyznaczGranicznaOdlegloscMahalanobisa(Klaster_danych, srodek, macierz_skalujaca ):
    s_graniczna = 0.0
    liczba_pomiarow = Klaster_danych.shape[1] # liczba pomiarow
    delta_s = odlegloscMahalanobisa( Klaster_danych[:,0], srodek, macierz_skalujaca) # pierwszy pomiar - stan nominalny
    if (delta_s == 0) : delta_s = DELTA_S_CONST # zabezpieczenie
    # iteracyjne wyznaczanie odleglosci granicznej
    while (True): 
        licznik = 0
        for i in range(liczba_pomiarow):
                x = Klaster_danych[:,i]
                d = odlegloscMahalanobisa(x, srodek, macierz_skalujaca)
                if (d < s_graniczna) : licznik += 1
        if licznik / liczba_pomiarow > PROG : break
        s_graniczna += delta_s

    return s_graniczna
###########################################################################################################
def PCA_2_skladowe(PCA_FI_2_SKLADOWE,ObszarTolerancji, slownik_uszkodzen):
    Klaster_danych = funkcjeUkladowe.np.matmul( PCA_FI_2_SKLADOWE, funkcjeUkladowe.np.transpose( ObszarTolerancji ) ) # transpozycja, bo w PCA mamy miec pomiary w kolumnach, a w ObszatTolerancji sa w wierszach

    C1 = wyznaczMacierzSkalujaca(Klaster_danych) # macierz skalujaca do odleglosci Mahalanobisa
    srodek = Klaster_danych.mean(axis=1)# wektor wartosci sredniej 
    s_graniczna_PCA_2 = wyznaczGranicznaOdlegloscMahalanobisa(Klaster_danych,srodek,C1) # graniczna odleglosc Mahalanobisa - jezeli punkt jets dalej, jest poza obszarem nominalnym

    slownik_uszkodzen_PCA_2 = funkcjeUkladowe.slownikUszkodzenPCA(slownik_uszkodzen, PCA_FI_2_SKLADOWE)

    funkcjeUkladowe.np.save('srodek_PCA_2_skladowe', srodek)
    funkcjeUkladowe.np.save('macierz_skalujaca_PCA_2_skladowe', C1)
    funkcjeUkladowe.np.save('graniczna_odleglosc_PCA_2_skladowe', s_graniczna_PCA_2)

    if not(funkcjeUkladowe.os.path.exists('Slownik_PCA_2')):
        # jezeli folder nie istnieje tworzymy go
        funkcjeUkladowe.os.mkdir('Slownik_PCA_2')
    funkcjeUkladowe.os.chdir('Slownik_PCA_2')
    # zapis slownika do plikow numpy:
    for sygnatura in slownik_uszkodzen_PCA_2:
        funkcjeUkladowe.np.save(sygnatura, slownik_uszkodzen_PCA_2[sygnatura])


    print("Analiza PCA dla dwoch skladowych glownych zostala zakonczona")
    print("Srodek: ", srodek)
    print("Macierz skalujaca: \n", C1)
    print("\nOdleglsoc graniczna : ", s_graniczna_PCA_2)
    #decyzja = input("Czy wyrysowac krzywe identyfikacyjne dla dwoch skladowych glownych? T/N ")
    #if decyzja == 'T' : funkcjeUkladowe.wyrysujKrzyweIdentyfikacyjne2D(slownik_uszkodzen_PCA_2)
    ############################################
    #   EWENTUALNE LACZENIE SYGNATUR
    ###########################################
    funkcjeUkladowe.os.chdir('../')  # <- powrot do katalogu
###########################################################################################################

def PCA_3_skladowe(PCA_FI_3_SKLADOWE,ObszarTolerancji, slownik_uszkodzen):
    Klaster_danych = funkcjeUkladowe.np.matmul( PCA_FI_3_SKLADOWE, funkcjeUkladowe.np.transpose( ObszarTolerancji ) ) # transpozycja, bo w PCA mamy miec pomiary w kolumnach, a w ObszatTolerancji sa w wierszach

    C1 = wyznaczMacierzSkalujaca(Klaster_danych) # macierz skalujaca do odleglosci Mahalanobisa
    srodek = Klaster_danych.mean(axis=1)# wektor wartosci sredniej 
    s_graniczna_PCA_3 = wyznaczGranicznaOdlegloscMahalanobisa(Klaster_danych,srodek,C1) # graniczna odleglosc Mahalanobisa - jezeli punkt jets dalej, jest poza obszarem nominalnym

    slownik_uszkodzen_PCA_3 = funkcjeUkladowe.slownikUszkodzenPCA(slownik_uszkodzen, PCA_FI_3_SKLADOWE)

    funkcjeUkladowe.np.save('srodek_PCA_3_skladowe', srodek)
    funkcjeUkladowe.np.save('macierz_skalujaca_PCA_3_skladowe', C1)
    funkcjeUkladowe.np.save('graniczna_odleglosc_PCA_3_skladowe', s_graniczna_PCA_3)

    if not(funkcjeUkladowe.os.path.exists('Slownik_PCA_3')):
        # jezeli folder nie istnieje tworzymy go
        funkcjeUkladowe.os.mkdir('Slownik_PCA_3')
    funkcjeUkladowe.os.chdir('Slownik_PCA_3')
    # zapis slownika do plikow numpy:
    for sygnatura in slownik_uszkodzen_PCA_3:
        funkcjeUkladowe.np.save(sygnatura, slownik_uszkodzen_PCA_3[sygnatura])


    print("Analiza PCA dla trzech skladowych glownych zostala zakonczona")
    print("Srodek: ", srodek)
    print("Macierz skalujaca: \n", C1)
    print("\nOdleglsoc graniczna : ", s_graniczna_PCA_3)
    #decyzja = input("Czy wyrysowac krzywe identyfikacyjne dla trzech skladowych glownych? T/N ")
    #if decyzja == 'T' : funkcjeUkladowe.wyrysujKrzyweIdentyfikacyjne3D(slownik_uszkodzen_PCA_3)
    ############################################
    #   EWENTUALNE LACZENIE SYGNATUR
    ###########################################
    funkcjeUkladowe.os.chdir('../')  # <- powrot do katalogu Slowniki_Multisin
###########################################################################################################
def Symulacja(ObszarTolerancji, f, sygnal, typ_widma, slownik_uszkodzen, na_podstawie_odp_czasowej = False):
    ObszarTolerancji *= funkcjeUkladowe.uklad.WZMOCNIENIE_TORU_POMIAROWEGO # dostosowanie do wzmocnienia toru pomiarowego
    decyzja = 'T'#input("Czy symulowac macierz danych? T/N ")
    slownik_MC = {} # inicjalizacja -> zmienna widoczna poza if'em
    if decyzja == 'T' :
        slownik_MC = funkcjeUkladowe.slownikUszkodzenMonteCarlo(f, sygnal, typ_widma, na_podstawie_odp_czasowej = na_podstawie_odp_czasowej)
##        X = funkcjeUkladowe.wygenerujMacierzDanychPCA(f, sygnal, typ_widma ,funkcjeUkladowe.uklad.LICZBA_LOSOWAN_MC)
        X = funkcjeUkladowe.wygenerujMacierzDanychPCA( slownik_MC )
        funkcjeUkladowe.np.save("macierz_danych_"+nazwa_ukladu, X)

    X = funkcjeUkladowe.np.load("macierz_danych_"+nazwa_ukladu+".npy")

    PCA_FI_2_SKLADOWE = funkcjeUkladowe.PCA(X, 2)
    PCA_FI_3_SKLADOWE = funkcjeUkladowe.PCA(X, 3)

    funkcjeUkladowe.np.save('PCA_2_SKL', PCA_FI_2_SKLADOWE)
    funkcjeUkladowe.np.save('PCA_3_SKL', PCA_FI_3_SKLADOWE)
    PCA_2_skladowe(PCA_FI_2_SKLADOWE,ObszarTolerancji, slownik_uszkodzen)
    odchylenia_std(slownik_MC, PCA_FI_2_SKLADOWE, 2)
    PCA_3_skladowe(PCA_FI_3_SKLADOWE,ObszarTolerancji, slownik_uszkodzen)
    odchylenia_std(slownik_MC, PCA_FI_3_SKLADOWE, 3)
###########################################################################################################

def odchylenia_std(slownik_uszkodzen_MC, fi, liczba_skladowych_glownych):
    slownik_uszkodzen_MC_po_PCA = funkcjeUkladowe.slownikUszkodzenPCA_MC(slownik_uszkodzen_MC, fi) # wyznaczamy slownik uszkodzen dla danej przestrzeni

    slownik_std = funkcjeUkladowe.slownik_odchylen_std( slownik_uszkodzen_MC_po_PCA )
    nazwa_katalogu = "std_PCA" + str(liczba_skladowych_glownych)

    if not(funkcjeUkladowe.os.path.exists(nazwa_katalogu)):
        # jezeli folder nie istnieje tworzymy go
        funkcjeUkladowe.os.mkdir(nazwa_katalogu)
    funkcjeUkladowe.os.chdir(nazwa_katalogu)
    # zapis slownika do plikow numpy:
    for sygnatura in slownik_std:
        funkcjeUkladowe.np.save(sygnatura, slownik_std[sygnatura])

    funkcjeUkladowe.os.chdir('../')  # <- powrot do katalogu wyzej
#------------------------------------------------------------------------------------------------------------------

print("Symulacje w toku...\n")

RASTER_MULTISIN = funkcjeUkladowe.np.array([ 1,2,3,4,5,6,7,8,9,10 ])

sygnal_MULTISIN = funkcjeUkladowe.sygnaly.multisin
sygnal_SINC = funkcjeUkladowe.sygnaly.sinc
f_multisin = funkcjeUkladowe.uklad.CZESTOTLIWOSC_PODSTAWOWA_MULTISIN
f_multisin = RASTER_MULTISIN * f_multisin
f_sinc = funkcjeUkladowe.uklad.BADANE_CZESTOTLIWOSCI_SINC

slownikUszkodzenMultisin = funkcjeUkladowe.slownikUszkodzen( f_multisin ,sygnal_MULTISIN, 'FFT')
##slownikUszkodzenSinc = funkcjeUkladowe.slownikUszkodzen( f_sinc ,sygnal_SINC, 'TF')
#   Na podstawie odpowiedzi czasowej :
slownikUszkodzenSinc = funkcjeUkladowe.slownikUszkodzen( f_sinc ,sygnal_SINC, 'TF', na_podstawie_odp_czasowej = True)
#
widmo_MULTISIN  =  funkcjeUkladowe.sygnaly.widmo(sygnal_MULTISIN, f_multisin)
widmo_SINC      =  funkcjeUkladowe.sygnaly.TransformataFouriera(sygnal_SINC, f_sinc)


# wydobycie nazwy badanego układu:
nazwa_pliku_z_ukladem = funkcjeUkladowe.nazwa
indeks_kropki = nazwa_pliku_z_ukladem.find('.')
nazwa_ukladu = nazwa_pliku_z_ukladem[:indeks_kropki]

# przejscie do katalogu slowniki uszkodzen :
# po wyborze układu jestesmy w folderze uklady
funkcjeUkladowe.os.chdir('../..')
if not(funkcjeUkladowe.os.path.exists('slowniki_uszkodzen')):
    # jezeli folder nie istnieje tworzymy go
    funkcjeUkladowe.os.mkdir('slowniki_uszkodzen')
funkcjeUkladowe.os.chdir('slowniki_uszkodzen')
if not(funkcjeUkladowe.os.path.exists(nazwa_ukladu)):
    # jezeli folder nie istnieje tworzymy go
    funkcjeUkladowe.os.mkdir(nazwa_ukladu)
funkcjeUkladowe.os.chdir(nazwa_ukladu)


#######################################################################################################################################
#       WIELOHARMONICZNY
##########################################
print("\n\n\tWIELOHARMONICZNY\n\n")
if not(funkcjeUkladowe.os.path.exists('Slowniki_Multisin')):
    # jezeli folder nie istnieje tworzymy go
    funkcjeUkladowe.os.mkdir('Slowniki_Multisin')
funkcjeUkladowe.os.chdir('Slowniki_Multisin')


funkcjeUkladowe.np.save('f',f_multisin)
ObszarTolerancji = widmo_MULTISIN * funkcjeUkladowe.monteCarloNormal( f_multisin ,liczba_losowanMC = funkcjeUkladowe.uklad.LICZBA_LOSOWAN_PUNKT_NOMINALNY)
Symulacja( ObszarTolerancji, f_multisin, sygnal_MULTISIN, 'FFT' , slownikUszkodzenMultisin )


print("Symulacje dla sygnalu wieloharmonicznego zakonczone")
print("Slowniki uszkodzen w folderze : \n",funkcjeUkladowe.os.getcwd())

########################################################################################################################################
#       SINC
##############################
print("\n\n\tSINC\n\n")
funkcjeUkladowe.os.chdir('..')
if not(funkcjeUkladowe.os.path.exists('Slowniki_Sinc')):
    # jezeli folder nie istnieje tworzymy go
    funkcjeUkladowe.os.mkdir('Slowniki_Sinc')
funkcjeUkladowe.os.chdir('Slowniki_Sinc')


funkcjeUkladowe.np.save('f',f_sinc)
##ObszarTolerancji = widmo_SINC * funkcjeUkladowe.monteCarloNormal( f_sinc ,liczba_losowanMC = funkcjeUkladowe.uklad.LICZBA_LOSOWAN_PUNKT_NOMINALNY)
# na podstawie odpowiedzi czasowej ukladu
ObszarTolerancji = funkcjeUkladowe.monteCarloNormal(f_sinc, liczba_losowanMC = funkcjeUkladowe.uklad.LICZBA_LOSOWAN_PUNKT_NOMINALNY, na_podstawie_odp_czasowej = True, sygnal = sygnal_SINC)
Symulacja( ObszarTolerancji, f_sinc, sygnal_SINC, 'TF' , slownikUszkodzenSinc )


print("Symulacje dla sygnalu SINC zakonczone")
print("Slowniki uszkodzen w folderze : \n",funkcjeUkladowe.os.getcwd())
