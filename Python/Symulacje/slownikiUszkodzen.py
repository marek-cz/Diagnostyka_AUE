import funkcjeUkladowe

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


print("Slownik uszkodzen w folderze : \n",funkcjeUkladowe.os.getcwd())

