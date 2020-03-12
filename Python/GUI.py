#------------------------------------------

#------------------------------------------
import tkinter as tk
import GUI_backend as backend
#------------------------------------------
##### utworzenie instancji okna
okno = tk.Tk()
#### tytul okna
okno.title( "Diagnostyka AUE" )
#okno.geometry("250x250")
okno.resizable(False, False)
#------------------------------------------
#           ZMIENNE GLOBALNE
portyCOM = [] # LISTA ZAWIERAJACA PORTY COM
wyborPortuCOM = tk.StringVar() #   zmienna zawierajaca indeks wybranego potru COM
wyborTypuPomiaru = tk.StringVar()
typyPomiaru = ["Sinus","Wieloharmoniczny","Impulsowy"]
czestotliwosc = 1000
opoznienie_ms = 10
opcje = ["Generacja","Pomiar","Wyrysuj dane","Widmo na MCU","Diagnozuj"]
zmienneOpcji = {} # slownik zawierajacy zmienne przypisane poszczegolnym opcjom
for opcja in opcje:
    zmienneOpcji.setdefault(opcja, tk.IntVar())


#------------------------------------------
#           FUNKCJE
def funkcjaPrzycisku1():
    global czestotliwosc
    global opoznienie_ms
    opcje = {} # slownik na opcje do wyslania do analizy-> bez koniecznosci tk
    #print("Czestotliwosc [Hz]: ",entry_field_czestotliwosc.get())
    czestotliwosc = int(entry_field_czestotliwosc.get() )# pobranie wartosci czestotliwosci
    #print("Opoznienie [ms]: ",entry_field_opoznienie.get())
    opoznienie_ms = entry_field_opoznienie.get() # pobranie wartosci czestotliwosci
    #print("Opcje pomiaru: ")
    for opcja in zmienneOpcji:
        #print(opcja, ": " ,zmienneOpcji[opcja].get(), " \n")
        opcje.setdefault(opcja, zmienneOpcji[opcja].get() )
    #print("Typ pomiaru: ", wyborTypuPomiaru.get() )
    #print("Port szeregowy: ", wyborPortuCOM.get() )

    
    backend.Analiza(czestotliwosc,opoznienie_ms,opcje,typyPomiaru.index(wyborTypuPomiaru.get()),wyborPortuCOM.get())
    
def zmianaCOM(*args): # function called when var changes
    #print(wyborPortuCOM.get())  # this is where you'd set another variable to var.get()
    xyz = 0 # nic

def zmianaMetodyPomiaru(*args): # function called when var changes
    #print(wyborTypuPomiaru.get())  # this is where you'd set another variable to var.get()
    xyz = 0 # nic
    
def WypiszPortyCOM():
    global portyCOM
    global wyborPortuCOM
    # usuniecie z listy starych portow :
    for port in portyCOM:
        COM_menu.delete(port)
    # odswiezenie listy portow
    #portyCOM = ["COM 1","COM 2","COM 3","COM 4","COM 5","COM 6"] # DO TESTOW :)
    portyCOM = backend.ListaPortowCOM()
    # wstawienie do menu nowych portow
    for port in portyCOM :
        COM_menu.add_radiobutton(label = port, value = port, variable = wyborPortuCOM )

def ZamknijProgram():
    okno.destroy()
 
#------------------------------------------------------------------------------------------------------
# top menu:
menu1 = tk.Menu(okno)
# nizsze warstwy menu:
program_menu = tk.Menu(menu1, tearoff = 0) # tearoff = 0 -> menu sie nie "odrywa"
program_menu.add_separator()
program_menu.add_command(label = "Zamknij", command = ZamknijProgram) # zamyka aplikacje

menu1.add_cascade(label = "Program", menu = program_menu)

wyborPortuCOM.trace('w', zmianaCOM) # funkcja callback wywolywana za kazdym razem gdy wyborPortuCOM sie zmieni
COM_menu = tk.Menu(menu1, tearoff=0, postcommand=WypiszPortyCOM)
menu1.add_cascade(label="Port Szeregowy", menu=COM_menu)

wyborTypuPomiaru.trace('w',zmianaMetodyPomiaru) # funkcja callback wywolywana za kazdym razem gdy wyborPortuCOM sie zmieni
Pomiar_menu = tk.Menu(menu1, tearoff=0)
for typ_pomiaru in typyPomiaru:
    #print(typ_pomiaru)
    Pomiar_menu.add_radiobutton(label = typ_pomiaru, value = typ_pomiaru, variable = wyborTypuPomiaru)
wyborTypuPomiaru.set(typyPomiaru[0]) # domyslna wartosc
menu1.add_cascade(label="Sygnał", menu=Pomiar_menu)

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
#------------------------------------------------------------------------------------------------------
# Entry fields
entry_field_czestotliwosc = tk.Entry(ramka_czestotliwosc, width = 5)
entry_field_czestotliwosc.insert(0,"1000")
entry_field_czestotliwosc.grid(column = 1, row = 0)

entry_field_opoznienie = tk.Entry(ramka_czestotliwosc, width = 5)
entry_field_opoznienie.insert(0,"10")
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
button1 = tk.Button(ramka_body,text = "Testuj", bg = "orange", command = funkcjaPrzycisku1,padx = 5,pady = 5,font =('Arial', 12))
button1.grid(column = 0, row = 3)
#------------------------------------------------------------------------------------------------------

#### petla komunikatow - start GUI !
okno.mainloop()