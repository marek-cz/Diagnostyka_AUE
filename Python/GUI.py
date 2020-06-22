import tkinter as tk
import OknoModalne
import GUI_backend as backend
#------------------------------------------
##### utworzenie instancji okna
okno = tk.Tk()
#### tytul okna
okno.title( "Diagnostyka AUE" )
okno.geometry("380x420")
okno.resizable(False, False)
#------------------------------------------
#           ZMIENNE GLOBALNE
folder_z_pomiarami = ''
portyCOM = [] # LISTA ZAWIERAJACA PORTY COM
wyborPortuCOM = tk.StringVar() #   zmienna zawierajaca indeks wybranego potru COM
wyborTypuPomiaru = tk.StringVar()
wyborUkladu = tk.StringVar()
ileSkladowychPCA = tk.IntVar()
pokazPomiarVar = tk.IntVar()
MetodaKlasyfikacji = tk.StringVar()
TrybPracy = tk.StringVar()
typyPomiaru = ["Sinus","Wieloharmoniczny","Sinc"]
czestotliwosc = 100
opoznienie_ms = 100
opcje = ["Generacja","Pomiar","Zapisz pomiar","Zapisz widmo","Widmo na MCU","Diagnozuj"]
zmienneOpcji = {} # slownik zawierajacy zmienne przypisane poszczegolnym opcjom
for opcja in opcje:
    zmienneOpcji.setdefault(opcja, tk.IntVar())


backend.os.chdir('slowniki_uszkodzen')

uklady = []
UKLAD_DOMYSLNY = 'Brak'
METODA_DOMYSLNA = 'DRB'
SCIEZKA_DOMYSLNA = backend.os.getcwd()

##licznik = 1
#------------------------------------------
#           FUNKCJE
def funkcjaPrzycisku1():
    global czestotliwosc
    global opoznienie_ms
    global licznik
    backend.funkcje.plt.close('all')
    opcje = {} # slownik na opcje do wyslania do analizy-> bez koniecznosci tk
    czestotliwosc = int(entry_field_czestotliwosc.get() )# pobranie wartosci czestotliwosci
    opoznienie_ms = entry_field_opoznienie.get() # pobranie wartosci czestotliwosci
    for opcja in zmienneOpcji:
        opcje.setdefault(opcja, zmienneOpcji[opcja].get() )
        
    if ( TrybPracy.get() == 'Online' ):
        """
        Praca online - to co program robil przed implementacja pracy w trybie offline
        """

        wynik = backend.Analiza(czestotliwosc,opoznienie_ms,opcje,typyPomiaru.index(wyborTypuPomiaru.get()),wyborTypuPomiaru.get() ,wyborPortuCOM.get(), wyborUkladu.get(), ileSkladowychPCA.get(), MetodaKlasyfikacji.get())
        wynik_klasyfikacji.delete('1.0',tk.END) # wyczyszczenie pola tekstowego
        wynik_klasyfikacji.insert(tk.END,  wynik +"\n") # wstaw rezultat do pola wyniku
        if ( (opcje["Pomiar"] or opcje["Diagnozuj"]) and (pokazPomiarVar.get()) ) :
            backend.funkcje.plt.close('all')
            backend.WyrysujDane(wyborTypuPomiaru.get())

    else:
        """
        Praca w trybie offline - wczytanie pomiarow z katalogu, iteracyjne wyznaczanie widma i klasyfikacja
        """
        backend.os.chdir(folder_z_pomiarami)
        lista_plikow = backend.os.listdir()
        backend.os.chdir(SCIEZKA_DOMYSLNA)
        wynik_klasyfikacji.delete('1.0',tk.END) # wyczyszczenie pola tekstowego
        licznik = 1
        liczba_plikow_str = str(len(lista_plikow))
        for plik in lista_plikow:
            if not(weryfikacjaPliku( plik )) : continue # jezeli plik NIE przejdzie walidacji
            pomiar = backend.np.load(folder_z_pomiarami + '/'+plik)
            wynik = str(licznik) + '/' + liczba_plikow_str + '\n' + plik + '\n'
            wynik += backend.AnalizaOffline(wyborUkladu.get(), typyPomiaru.index(wyborTypuPomiaru.get()),wyborTypuPomiaru.get(), ileSkladowychPCA.get(), MetodaKlasyfikacji.get(), pomiar)
            wynik_klasyfikacji.insert(tk.END,  wynik +"\n") # wstaw rezultat do pola wyniku
            licznik += 1
        scrollbar.config( command = wynik_klasyfikacji.yview ) # dopasowanie scrollbara do dlugosci rezultatu
        backend.funkcje.plt.close('all')
        backend.WyrysujSlownikOffline( wyborUkladu.get(), ileSkladowychPCA.get(), wyborTypuPomiaru.get() )

    
def zmianaCOM(*args): # function called when var changes
    # this is where you'd set another variable to var.get()
    xyz = 0 # nic

def zmianaMetodyPomiaru(*args): # function called when var changes
    # this is where you'd set another variable to var.get()
    xyz = 0 # nic

def zmianaUkladu(*args):
    xyz = 0 # nic :)

def zmianaMetodyKlasyfikacji(*args):
    return 0

def zmianaPCA(*args):
    return 0

def WypiszPortyCOM():
    global portyCOM
    global wyborPortuCOM
    # usuniecie z listy starych portow :
    for port in portyCOM:
        COM_menu.delete(port)
    # odswiezenie listy portow
    portyCOM = backend.ListaPortowCOM()
    # wstawienie do menu nowych portow
    for port in portyCOM :
        COM_menu.add_radiobutton(label = port, value = port, variable = wyborPortuCOM )

def ZamknijProgram():
    okno.destroy()

def WyrysujDane():
    backend.WyrysujDane(wyborTypuPomiaru.get())

def WyrysujSlownik():
    if wyborUkladu.get() == 'Brak' : return -1
    backend.funkcje.plt.close('all')
    backend.WyrysujSlownik(wyborUkladu.get(),ileSkladowychPCA.get(), wyborTypuPomiaru.get())

def WyrysujPomiary():
    if wyborUkladu.get() == 'Brak' : return -1
    backend.funkcje.plt.close('all')
    backend.WyrysujSlownik(wyborUkladu.get(), ileSkladowychPCA.get(), wyborTypuPomiaru.get(), True)

def WypiszUklady():
    global uklady
    for uklad in uklady:
        Uklad_menu.delete(uklad)
    # odswierzenie listy ukladow
    uklady = backend.os.listdir()
    # dodanie ukladow do menu
    for uklad in uklady:
        Uklad_menu.add_radiobutton(label = uklad, value = uklad, variable = wyborUkladu)

def grupujUszkodzenia():
    ##uszkodzenia = ['C1-','C2-','R1-','R2-','R3-','C1+','C2+','R1+','R2+','R3+']
    uszkodzenia = backend.uszkodzenia_GET( wyborUkladu.get(), wyborTypuPomiaru.get(), ileSkladowychPCA.get() )
    grupy_niejednoznacznosci_lokalne = backend.grupy_niejednoznacznosci_GET()
    okno_modalne = OknoModalne.OknoModalne(okno,uszkodzenia, grupy_niejednoznacznosci_lokalne )
    okno.wait_window(okno_modalne.top)
    
    backend.grupy_niejednoznacznosci_SET( grupy_niejednoznacznosci_lokalne )



def wyborFolderu():
    global folder_z_pomiarami
    folder_z_pomiarami = tk.filedialog.askdirectory( parent=okno, initialdir = backend.os.getcwd(), title="Wybierz folder z pomiarami:")
    

def weryfikacjaPliku(nazwa_pliku):
    if (nazwa_pliku.find('pomiar') == -1) : return False
    if (nazwa_pliku.find('.npy') == -1) : return False
    return True
#------------------------------------------------------------------------------------------------------
# top menu:
menu1 = tk.Menu(okno)
# nizsze warstwy menu:
program_menu = tk.Menu(menu1, tearoff = 0) # tearoff = 0 -> menu sie nie "odrywa"
program_menu.add_command(label = "Wykresy czasowe i widmo pomiaru", command = WyrysujDane) # Rysowanie
program_menu.add_command(label = "Krzywe identyfikacyjne", command = WyrysujSlownik) # Rysowanie
program_menu.add_command(label = "Krzywe identyfikacyjne i punkty pomiarowe", command = WyrysujPomiary ) # Rysowanie


menu1.add_cascade(label = "Wykresy", menu = program_menu)

wyborPortuCOM.trace('w', zmianaCOM) # funkcja callback wywolywana za kazdym razem gdy wyborPortuCOM sie zmieni
COM_menu = tk.Menu(menu1, tearoff=0, postcommand=WypiszPortyCOM)
menu1.add_cascade(label="Port Szeregowy", menu=COM_menu)

wyborTypuPomiaru.trace('w',zmianaMetodyPomiaru) # funkcja callback wywolywana za kazdym razem gdy wyborTypuPomiaru sie zmieni
Pomiar_menu = tk.Menu(menu1, tearoff=0)
for typ_pomiaru in typyPomiaru:
    
    Pomiar_menu.add_radiobutton(label = typ_pomiaru, value = typ_pomiaru, variable = wyborTypuPomiaru)
wyborTypuPomiaru.set(typyPomiaru[1]) # domyslna wartosc
menu1.add_cascade(label="Sygnał", menu=Pomiar_menu)

wyborUkladu.set(UKLAD_DOMYSLNY)
wyborUkladu.trace('w',zmianaUkladu) #seldzenie zmiennej wybor ukladu
Uklad_menu = tk.Menu(menu1, tearoff=0, postcommand=WypiszUklady)
## dodanie mozliwosci grupowania uszkodzen
Uklad_menu.add_command( label = "Grupuj", command = grupujUszkodzenia ) # grupowanie uszkodzen w obszary niejednoznaczności
Uklad_menu.add_separator()
Uklad_menu.add_radiobutton(label = 'Brak', value = 'Brak', variable = wyborUkladu)
menu1.add_cascade(label = 'Układ',menu = Uklad_menu)

ileSkladowychPCA.set(2) # domyslnie 2 skladowe glowne
ileSkladowychPCA.trace('w',zmianaPCA) # funkcja callback wywolywana za kazdym razem gdy uzytkownik zmieni liczbe skaldowych PCA
PCA_menu = tk.Menu(menu1, tearoff=0)#, postcommand=WypiszUklady)
PCA_menu.add_radiobutton(label = "2 składowe główne", value = 2, variable = ileSkladowychPCA)
PCA_menu.add_radiobutton(label = "3 składowe główne", value = 3, variable = ileSkladowychPCA)
menu1.add_cascade(label = 'PCA',menu = PCA_menu)


MetodaKlasyfikacji.set(METODA_DOMYSLNA)
MetodaKlasyfikacji.trace('w',zmianaMetodyKlasyfikacji) # funkcja callback wywolywana za kazdym razem gdy uzytkownik zmieni metode klasyfikacji
Klasyfikacja_menu = tk.Menu(menu1, tearoff=0)
Klasyfikacja_menu.add_radiobutton(label = "Klasyczna", value = 'Klasyczna', variable = MetodaKlasyfikacji)
Klasyfikacja_menu.add_radiobutton(label = "DRB", value = 'DRB', variable = MetodaKlasyfikacji)
menu1.add_cascade(label = 'Klasyfikacja',menu = Klasyfikacja_menu)

okno.config(menu = menu1)
#------------------------------------------------------------------------------------------------------
# ramki glowne:
ramka_head = tk.Frame(okno, borderwidth = 1)
ramka_head.grid(column = 0, row = 0)
ramka_body = tk.Frame(okno, borderwidth = 1)
ramka_body.grid(column = 0, row = 1)
#------------------------------------------------------------------------------------------------------
# ramki pomocnicze:
ramka_czestotliwosc = tk.Frame(ramka_body, borderwidth = 1)
ramka_czestotliwosc.grid(column = 0, row = 0, sticky = 'w')

ramka_opcje = tk.Frame(ramka_body, borderwidth = 1)
ramka_opcje.grid(column = 0, row = 1, sticky = 'w')

ramka_wynik = tk.Frame(ramka_body, borderwidth = 1)
ramka_wynik.grid(column = 1, row = 1, sticky = 'w')

ramka_wyrysuj = tk.Frame(ramka_body, borderwidth = 1)
ramka_wyrysuj.grid(column = 1, row = 0)#, sticky = 'w')

##ramka_folder = tk.Frame(ramka_body, borderwidth = 1)
##ramka_folder.grid(column = 0, row = 2, sticky = 'w')
#------------------------------------------------------------------------------------------------------
# etykiety:
label1 = tk.Label(ramka_head, text = "Diagnostyka AUE", font =('Arial', 20),padx=3,pady = 3)
label1.grid(column = 0, row = 0)

label2 = tk.Label(ramka_czestotliwosc, text = "Częstotliwość [Hz] : ", font =('Arial', 12))
label2.grid(column = 0, row = 0)
label4 = tk.Label(ramka_czestotliwosc, text = "Opóznienie [ms] : ", font =('Arial', 12))
label4.grid(column = 0, row = 1, sticky = 'w')

label3 = tk.Label(ramka_opcje, text = "Opcje pomiaru : ", font =('Arial', 12))
label3.grid(column = 0, row = 4)

label4 = tk.Label(ramka_wynik, text = "Wynik klasyfikacji : ", font =('Arial', 12))
label4.grid(column = 0, row = 0)

label5 = tk.Label(ramka_opcje, text = "Tryb pracy : ", font =('Arial', 12))
label5.grid(column = 0, row = 0,sticky = 'w')

##label6 = tk.Label(ramka_folder, text = "Folder z pomiarami : ", font =('Arial', 12))
##label6.grid(column = 0, row = 0,sticky = 'w')

label7 = tk.Label(ramka_body, text = "", font =('Arial', 12))
label7.grid(column = 0, row = 3, sticky = 'w')
#------------------------------------------------------------------------------------------------------
# Entry fields
entry_field_czestotliwosc = tk.Entry(ramka_czestotliwosc, width = 5)
entry_field_czestotliwosc.insert(0,"100")
entry_field_czestotliwosc.grid(column = 1, row = 0)

entry_field_opoznienie = tk.Entry(ramka_czestotliwosc, width = 5)
entry_field_opoznienie.insert(0,"100")
entry_field_opoznienie.grid(column = 1, row = 1)

##entry_field_folder = tk.Entry(ramka_folder, width = 30)
##entry_field_folder.grid(column = 0, row = 1, sticky = 'w')
#------------------------------------------------------------------------------------------------------
# Radiobutton:
TrybPracy.set('Online')
radio_button_1 = tk.Radiobutton(ramka_opcje, text = 'Online', variable=TrybPracy, value = 'Online')#,command = funkcjaTrybPracy)
radio_button_1.grid(row = 1,sticky = 'w')
radio_button_2 = tk.Radiobutton(ramka_opcje, text = 'Offline', variable=TrybPracy, value = 'Offline' ,command = wyborFolderu)
radio_button_2.grid(row = 2,sticky = 'w')
#------------------------------------------------------------------------------------------------------
# Chechbox'y:
wiersz = 5
for opcja in opcje: # dla kazdej opcji tworzymy przycisk
    c = tk.Checkbutton(ramka_opcje,justify = 'left', text=opcja, variable=zmienneOpcji[opcja])
    c.grid(row = wiersz,sticky = 'w')
    wiersz = wiersz + 1

pokazPomiarVar.set(0)
Checkbutton_wyrysuj = tk.Checkbutton(ramka_wyrysuj,justify = 'left', text='Pokaż pomiar', variable = pokazPomiarVar )
Checkbutton_wyrysuj.grid(column = 0, row = 0,sticky = tk.E)
#------------------------------------------------------------------------------------------------------
# Przyciski
#button1 = tk.Button(ramka_body,text = "Testuj", bg = "orange", command = funkcjaPrzycisku1,padx = 5,pady = 5,font =('Arial', 12))
button1 = tk.Button(ramka_opcje,text = "Wykonaj", bg = "orange", command = funkcjaPrzycisku1,padx = 5,pady = 5,font =('Arial', 12))
button1.grid(column = 0, row = wiersz+1)

##button2 = tk.Button(ramka_folder,text = "Wybierz folder", bg = "orange", command = funkcjaPrzycisku2,padx = 5,pady = 5,font =('Arial', 12))
##button2.grid(column = 0, row = 2)
#------------------------------------------------------------------------------------------------------
# suwaki:
scrollbar = tk.Scrollbar(ramka_wynik)
scrollbar.grid( row = 1, column = 1,sticky=tk.N+tk.S )
#------------------------------------------------------------------------------------------------------
# Pole tekstowe:
wynik_klasyfikacji = tk.Text(master = ramka_wynik,height = 15, width = 20, wrap = tk.WORD, yscrollcommand = scrollbar.set )
wynik_klasyfikacji.grid(column = 0, row = 1)
#------------------------------------------------------------------------------------------------------

#### petla komunikatow - start GUI !
okno.mainloop()
