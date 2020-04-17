import funkcjeUkladowe

PROG = 0.99

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


#---------------------------------------------------------------

print("Symulacje w toku...\n")

#def slownikUszkodzenMultisin():
sygnal = funkcjeUkladowe.sygnaly.multisin
slownikUszkodzenMultisin = funkcjeUkladowe.slownikUszkodzen(sygnal)



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
if not(funkcjeUkladowe.os.path.exists('Slownik_Multisin')):
    # jezeli folder nie istnieje tworzymy go
    funkcjeUkladowe.os.mkdir('Slownik_Multisin')
funkcjeUkladowe.os.chdir('Slownik_Multisin')
# zapis slownika do plikow numpy:
for sygnatura in slownikUszkodzenMultisin:
    funkcjeUkladowe.np.save(sygnatura, slownikUszkodzenMultisin[sygnatura])

ObszarTolerancji = funkcjeUkladowe.sygnaly.widmo(sygnal, funkcjeUkladowe.uklad.BADANE_CZESTOTLIWOSCI) * funkcjeUkladowe.monteCarloNormal(liczba_losowanMC = funkcjeUkladowe.uklad.LICZBA_LOSOWAN_PUNKT_NOMINALNY)
wartosc_srednia = ObszarTolerancji.mean(axis=0) # wektor!
sigma = ObszarTolerancji.std(axis=0)            # wektor!

#zapsianie wartosci sredniej i odchylenia std do plikow
funkcjeUkladowe.np.save("../wartosc_srednia", wartosc_srednia)
funkcjeUkladowe.np.save("../odchylenie_std", sigma)


decyzja = input("Czy symulowac macierz danych? T/N ")

if decyzja == 'T' :
    X = funkcjeUkladowe.wygenerujMacierzDanychPCA(sygnal , funkcjeUkladowe.uklad.LICZBA_LOSOWAN_MC)
    funkcjeUkladowe.np.save("../macierz_danych_"+nazwa_ukladu, X)

X = funkcjeUkladowe.np.load("../macierz_danych_"+nazwa_ukladu+".npy")

PCA_FI_2_SKLADOWE = funkcjeUkladowe.PCA(X, 2)
PCA_FI_3_SKLADOWE = funkcjeUkladowe.PCA(X, 3)

funkcjeUkladowe.np.save('../PCA_2_SKL', PCA_FI_2_SKLADOWE)
funkcjeUkladowe.np.save('../PCA_3_SKL', PCA_FI_3_SKLADOWE)

# wyznaczenie granicznej odległości Mahalanobisa dla PCA - 2 składowe główne

Klaster_danych = funkcjeUkladowe.np.matmul( PCA_FI_2_SKLADOWE, funkcjeUkladowe.np.transpose( ObszarTolerancji ) ) # transpozycja, bo w PCA mamy miec pomiary w kolumnach, a w ObszatTolerancji sa w wierszach
liczba_pomiarow = Klaster_danych.shape[1] # liczba pomiarow
C = funkcjeUkladowe.np.cov( Klaster_danych ) # wyznaczanie macierzy kowariancji
C_inv = funkcjeUkladowe.np.linalg.inv(C) # odwrocenie macierzy kowariancji
wartosci_wlasne, wektory_wlasne = funkcjeUkladowe.np.linalg.eig( C_inv ) # wyznaczenie wektorow i wartosci wlasnych macierzy odwrotnej do macierzy kowariancji

lambda_min = wartosci_wlasne.min()
LAMBDA_diag = funkcjeUkladowe.np.diag( wartosci_wlasne / lambda_min ) # normowanie wartosci wlasnych
U = wektory_wlasne

C1 = funkcjeUkladowe.np.matmul( funkcjeUkladowe.np.matmul( U, LAMBDA_diag ), funkcjeUkladowe.np.transpose(U) ) # wyznaczenie unormowanej macierzy skalujacej

srodek = funkcjeUkladowe.np.matmul( PCA_FI_2_SKLADOWE, wartosc_srednia )
s_graniczna = 0.0
delta_s = odlegloscMahalanobisa( Klaster_danych[:,0], srodek, C1) # pierwszy pomiar - stan nominalny
# iteracyjne wyznaczanie odleglosci granicznej
while (True): 
    licznik = 0
    for i in range(liczba_pomiarow):
	    x = Klaster_danych[:,i]
	    d = odlegloscMahalanobisa(x,srodek,C1)
	    if (d < s_graniczna) : licznik += 1
    if licznik / liczba_pomiarow > PROG : break
    s_graniczna += delta_s


print("Slownik uszkodzen w folderze : \n",funkcjeUkladowe.os.getcwd())
