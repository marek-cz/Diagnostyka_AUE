#------------------------------------------

#------------------------------------------
import tkinter as tk
import GUI_backend as backend
#------------------------------------------
##### utworzenie instancji okna
okno = tk.Tk()
#### tytul okna
okno.title( "Diagnostyka AUE" )
okno.geometry("370x410")
okno.resizable(False, False)
#------------------------------------------
#           ZMIENNE GLOBALNE
portyCOM = [] # LISTA ZAWIERAJACA PORTY COM
wyborPortuCOM = tk.StringVar() #   zmienna zawierajaca indeks wybranego potru COM
wyborTypuPomiaru = tk.StringVar()
wyborUkladu = tk.StringVar()
ileSkladowychPCA = tk.IntVar()
MetodaKlasyfikacji = tk.StringVar()
typyPomiaru = ["Sinus","Wieloharmoniczny","Sinc"]
czestotliwosc = 100
opoznienie_ms = 100
opcje = ["Generacja","Pomiar","Zapisz pomiar","Zapisz widmo","Widmo na MCU","Diagnozuj"]
zmienneOpcji = {} # slownik zawierajacy zmienne przypisane poszczegolnym opcjom
for opcja in opcje:
    zmienneOpcji.setdefault(opcja, tk.IntVar())


backend.os.chdir('slowniki_uszkodzen')
uklady = []
UKLAD_DOMYSLNY = 'HPF_MFB'
METODA_DOMYSLNA = 'DRB'
licznik = 1
#------------------------------------------
#           FUNKCJE
def funkcjaPrzycisku1():
    global czestotliwosc
    global opoznienie_ms
    global licznik
    opcje = {} # slownik na opcje do wyslania do analizy-> bez koniecznosci tk
    czestotliwosc = int(entry_field_czestotliwosc.get() )# pobranie wartosci czestotliwosci
    opoznienie_ms = entry_field_opoznienie.get() # pobranie wartosci czestotliwosci
    for opcja in zmienneOpcji:
        opcje.setdefault(opcja, zmienneOpcji[opcja].get() )

    wynik = backend.Analiza(czestotliwosc,opoznienie_ms,opcje,typyPomiaru.index(wyborTypuPomiaru.get()),wyborTypuPomiaru.get() ,wyborPortuCOM.get(), wyborUkladu.get(), ileSkladowychPCA.get(), MetodaKlasyfikacji.get())
    if not (licznik % 15) :
        wynik_klasyfikacji.delete(1.0,tk.END) # miesci sie 15 wpisow
        licznik = 1
    if wynik != '':
        wynik_klasyfikacji.insert(tk.END, str(licznik)+' '+ wynik +"\n") # wstaw rezultat do pola wyniku
        licznik += 1
    
def zmianaCOM(*args): # function called when var changes
    # this is where you'd set another variable to var.get()
    xyz = 0 # nic

def zmianaMetodyPomiaru(*args): # function called when var changes
    # this is where you'd set another variable to var.get()
    xyz = 0 # nic

def zmianaUkladu(*args):
    xyz = 0 # nic :)

def zmianaMetodyKlasyfikacji(*args):
    print(MetodaKlasyfikacji.get())
    return 0

def zmianaPCA(*args):
    print("liczba skladowych glownych = ",ileSkladowychPCA.get())

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
    backend.WyrysujSlownik(wyborUkladu.get(),ileSkladowychPCA.get(), wyborTypuPomiaru.get())

def WyrysujPomiary():
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
 
#------------------------------------------------------------------------------------------------------
# top menu:
menu1 = tk.Menu(okno)
# nizsze warstwy menu:
program_menu = tk.Menu(menu1, tearoff = 0) # tearoff = 0 -> menu sie nie "odrywa"
program_menu.add_command(label = "Wykresy czasowe i widmo pomiaru", command = WyrysujDane) # Rysowanie
program_menu.add_command(label = "Krzywe identyfikacyjne", command = WyrysujSlownik) # Rysowanie
program_menu.add_command(label = "Krzywe identyfikacyjne i punkty pomiarowe", command = WyrysujPomiary ) # Rysowanie
##program_menu.add_separator()
##program_menu.add_command(label = "Zamknij", command = ZamknijProgram) # zamyka aplikacje

menu1.add_cascade(label = "Wykresy", menu = program_menu)

wyborPortuCOM.trace('w', zmianaCOM) # funkcja callback wywolywana za kazdym razem gdy wyborPortuCOM sie zmieni
COM_menu = tk.Menu(menu1, tearoff=0, postcommand=WypiszPortyCOM)
menu1.add_cascade(label="Port Szeregowy", menu=COM_menu)

wyborTypuPomiaru.trace('w',zmianaMetodyPomiaru) # funkcja callback wywolywana za kazdym razem gdy wyborTypuPomiaru sie zmieni
Pomiar_menu = tk.Menu(menu1, tearoff=0)
for typ_pomiaru in typyPomiaru:
    #print(typ_pomiaru)
    Pomiar_menu.add_radiobutton(label = typ_pomiaru, value = typ_pomiaru, variable = wyborTypuPomiaru)
wyborTypuPomiaru.set(typyPomiaru[0]) # domyslna wartosc
menu1.add_cascade(label="Sygnał", menu=Pomiar_menu)

wyborUkladu.set(UKLAD_DOMYSLNY)
wyborUkladu.trace('w',zmianaUkladu) #seldzenie zmiennej wybor ukladu
Uklad_menu = tk.Menu(menu1, tearoff=0, postcommand=WypiszUklady)
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

#------------------------------------------------------------------------------------------------------
# etykiety:
label1 = tk.Label(ramka_head, text = "Diagnostyka AUE", font =('Arial', 20),padx=3,pady = 3)
label1.grid(column = 0, row = 0)

label2 = tk.Label(ramka_czestotliwosc, text = "Częstotliwość [Hz] : ", font =('Arial', 12))
label2.grid(column = 0, row = 0)
label4 = tk.Label(ramka_czestotliwosc, text = "Opoznienie [ms] : ", font =('Arial', 12))
label4.grid(column = 0, row = 1, sticky = 'w')

label3 = tk.Label(ramka_opcje, text = "Opcje pomiaru : ", font =('Arial', 12))
label3.grid(column = 0, row = 0)

label4 = tk.Label(ramka_wynik, text = "Wynik klasyfikacji : ", font =('Arial', 12))
label4.grid(column = 0, row = 0)
#------------------------------------------------------------------------------------------------------
# Entry fields
entry_field_czestotliwosc = tk.Entry(ramka_czestotliwosc, width = 5)
entry_field_czestotliwosc.insert(0,"100")
entry_field_czestotliwosc.grid(column = 1, row = 0)

entry_field_opoznienie = tk.Entry(ramka_czestotliwosc, width = 5)
entry_field_opoznienie.insert(0,"100")
entry_field_opoznienie.grid(column = 1, row = 1)
#------------------------------------------------------------------------------------------------------
# Chechbox'y:
wiersz = 2
for opcja in opcje: # dla kazdej opcji tworzymy przycisk
    c = tk.Checkbutton(ramka_opcje,justify = 'left', text=opcja, variable=zmienneOpcji[opcja])
    c.grid(row = wiersz,sticky = 'w')
    wiersz = wiersz + 1

#------------------------------------------------------------------------------------------------------
# Przyciski
#button1 = tk.Button(ramka_body,text = "Testuj", bg = "orange", command = funkcjaPrzycisku1,padx = 5,pady = 5,font =('Arial', 12))
button1 = tk.Button(ramka_opcje,text = "Wykonaj", bg = "orange", command = funkcjaPrzycisku1,padx = 5,pady = 5,font =('Arial', 12))
button1.grid(column = 0, row = wiersz+1)
#------------------------------------------------------------------------------------------------------
# Pole tekstowe:
wynik_klasyfikacji = tk.Text(master = ramka_wynik,height = 15, width = 20)
wynik_klasyfikacji.grid(column = 0, row = 1)
#------------------------------------------------------------------------------------------------------

#### petla komunikatow - start GUI !
okno.mainloop()
