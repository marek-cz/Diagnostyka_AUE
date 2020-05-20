import tkinter as tk


class OknoModalne:
    def __init__(self, parent, uszkodzenia, grupy_niejednoznacznosci):


        self.grupy_niejednoznacznosci = grupy_niejednoznacznosci
        
        self.top = tk.Toplevel(parent)
        self.top.transient(parent)
        self.top.grab_set()
        self.top.geometry("400x500")
        self.top.resizable(False, False)
        self.top.title('Grupy niejednoznacznosci')
##        self.top.bind("<Return>", self.ok)

        self.Komunikat = tk.StringVar()
        self.Komunikat_usun = tk.StringVar()
        
        ####################################################
        #   ramki
        ramka_head = tk.Frame(self.top, borderwidth = 1)
        ramka_head.grid(column = 0, row = 0)
        ramka_body = tk.Frame(self.top, borderwidth = 1)
        ramka_body.grid(column = 0, row = 1)

        ramka_uszkodzenia = tk.Frame(ramka_body, borderwidth = 1)
        ramka_uszkodzenia.grid(column = 0, row = 0)

        ramka_grupy_niejedn = tk.Frame(ramka_body, borderwidth = 1)
        ramka_grupy_niejedn.grid(column = 1, row = 0)
        ####################################################

        ####################################################
        #   napisy
        label1 = tk.Label(ramka_head, text = "Grupy niejednoznaczności", font =('Arial', 20),padx=3,pady = 3)
        label1.grid(column = 0, row = 0)

        label2 = tk.Label(ramka_uszkodzenia, text = "Uszkodzenia:", font =('Arial', 16),padx=3,pady = 3)
        label2.grid(column = 0, row = 0)

        label3 = tk.Label(ramka_grupy_niejedn, text = "Grupy niejednoznaczności:", font =('Arial', 16),padx=3,pady = 3)
        label3.grid(column = 0, row = 0)

        label4 = tk.Message(ramka_uszkodzenia, textvariable = self.Komunikat, font =('Arial', 10),padx=3,pady = 3, width = 400 )
        label4.grid(column = 0, row = 3)

        label4 = tk.Message(ramka_grupy_niejedn, textvariable = self.Komunikat_usun, font =('Arial', 10),padx=3,pady = 3, width = 400 )
        label4.grid(column = 0, row = 3)

        ####################################################
        #   listy

        self.lista_uszkodzen = tk.Listbox( ramka_uszkodzenia, height = len(uszkodzenia) + 1 ,selectmode = tk.MULTIPLE  ) #, yscrollcommand = scrollbar.set )
        self.lista_uszkodzen.grid(column = 0, row = 1)
        for uszkodzenie in uszkodzenia:
            self.lista_uszkodzen.insert(tk.END, uszkodzenie )

        self.lista_grup_niejedn = tk.Listbox( ramka_grupy_niejedn, height = len(uszkodzenia) + 1 , selectmode = tk.SINGLE  ) #, yscrollcommand = scrollbar.set )
        self.lista_grup_niejedn.grid(column = 0, row = 1)
        for grupa in grupy_niejednoznacznosci:
            self.lista_grup_niejedn.insert(tk.END, grupa )
        ####################################################

        ####################################################
        #   przyciski
        button_dodaj = tk.Button(ramka_uszkodzenia,text = "Dodaj", bg = "orange",padx = 5,pady = 5,font =('Arial', 12), command = self.dodajDoListy )
        button_dodaj.grid(column = 0, row = 2 )

        button_usun = tk.Button(ramka_grupy_niejedn,text = "Usuń", bg = "orange",padx = 5,pady = 5,font =('Arial', 12), command = self.usunZListy )
        button_usun.grid(column = 0, row = 2 )

        button_zapisz = tk.Button(ramka_body,text = "Zapisz i zakończ", bg = "red",padx = 5,pady = 5,font =('Arial', 14), command = self.zapiszZakoncz )
        button_zapisz.grid(column = 1, row = 3 )

        ####################################################

    def dodajDoListy(self):
        zaznaczone_elementy_indeksy = self.lista_uszkodzen.curselection()
        if len(zaznaczone_elementy_indeksy) == 0 :
            self.Komunikat.set("")
            return -1
        zaznaczone_uszkodzenia = ''
        for indeks in zaznaczone_elementy_indeksy :
            if (self.CzyUszkodzenieJestNaLiscie(self.lista_uszkodzen.get(indeks))) :
                self.Komunikat.set("Błąd!")
                return -2
            zaznaczone_uszkodzenia += self.lista_uszkodzen.get(indeks)
            self.lista_uszkodzen.select_clear(indeks)
        grupa = '{' + zaznaczone_uszkodzenia + '}'
        self.grupy_niejednoznacznosci.append(grupa)
        self.lista_grup_niejedn.insert(tk.END, grupa )

        self.Komunikat.set("Dodano " + grupa)

        print(self.grupy_niejednoznacznosci)

    def usunZListy(self):
        zaznaczone_elementy_indeksy = self.lista_grup_niejedn.curselection()
        if len(zaznaczone_elementy_indeksy) == 0 :
            self.Komunikat_usun.set("")
            return -1
        for indeks in zaznaczone_elementy_indeksy :
            self.grupy_niejednoznacznosci.remove( self.lista_grup_niejedn.get(indeks) )
            self.Komunikat_usun.set("Usunieto " + self.lista_grup_niejedn.get(indeks))
            self.lista_grup_niejedn.delete(indeks)


        print(self.grupy_niejednoznacznosci)

    def zapiszZakoncz(self):
        self.top.destroy()


    def CzyUszkodzenieJestNaLiscie(self, uszkodzenie):
        for element in self.grupy_niejednoznacznosci:
            if (element.find(uszkodzenie) != -1) : return True
