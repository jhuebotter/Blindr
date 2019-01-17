#!/usr/bin/python

# this script contains the visual interaction with the user and starts the blindr.py script

from tkinter import *
from tkinter import simpledialog, ttk, messagebox
from tkinter import filedialog as fd
import threading
import pandas as pd
import os

root = Tk()
root.title('Blindr')
root.geometry("380x290")
ttk.Style().configure('TMenubutton', foreground='black', background='white',font=("Arial", 11),relief="rigid")
ttk.Style().configure('green/black.TButton', foreground='black', background='white',font=("Arial", 11))
ttk.Style().configure('TLabel',font=("Arial", 11))
busy = False

class App():

    # this is the main gui window for user interaction with a few buttons

    def __init__(self):
        super(App, self).__init__()

        self.filename = None
        self.no_of_groups = StringVar(root)
        self.no_of_groups.set(' ')
        self.choices = [' ']
        self.feats = []
        self.animal_id = StringVar(root)
        self.animal_id.set(' ')

        ttk.Label(root, text="Select your input file").grid(row=0, padx=20, sticky=W)
        ttk.Button(root, text='open explorer', command=self.extract_me, style='green/black.TButton').grid(row=0, column=1, pady=10, sticky="ew")
        ttk.Label(root, text="Number of groups to create ",style='TLabel').grid(row=1,padx=20,pady=10,sticky=W)
        ttk.OptionMenu(root, self.no_of_groups, " ", "2", "3", "4", "5", "6", "7", "8", "9", "10",style = 'TMenubutton').grid(row=1, column=1, pady=10, sticky="ew")

        ttk.Label(root, text="Select the animal ID indicator").grid(row=2,padx=20,pady=10,sticky=W)
        self.id_menu = ttk.OptionMenu(root, self.animal_id, *self.choices, style='TMenubutton')
        self.id_menu.grid(row=2, column=1, pady=10, sticky="ew")
        self.id_menu.config(state="disabled")

        ttk.Label(root, text="Select all relevant features").grid(row=3,padx=20,pady=10,sticky="nw")
        self.featmenu = Listbox(root, selectmode='multiple', height=5, exportselection=0)
        self.featmenu.grid(row=3, column=1, pady=10, sticky="ew")
        self.featmenu.config(state="disabled")

        ttk.Button(root, text='Quit', command=self.exit, width=14, style='green/black.TButton').grid(row=4, sticky=W, pady=10, padx=20)
        ttk.Button(root, text='Run', command=self.run, style='green/black.TButton').grid(row=4, column=1, sticky="ew", pady=10)
        
        root.protocol("WM_DELETE_WINDOW", self.exit)
        mainloop()


    def readfile(self):

        # this function reads in parameters from the input file

        if self.filename:
            file = self.filename.rsplit('.',1)
            file_type = file[1]
            if file_type == 'csv':
                f = open(self.filename,"r")
                split = f.read().split('\n')[0][-1]
                df = pd.read_csv(self.filename, sep=split)
                df.dropna(axis='columns', how='all',inplace=True)
                print(df.head())
            elif file_type in ['xlsx','xls']:
                df = pd.read_excel(self.filename)
            self.choices = [' '] + list(df.columns)
            ttk.OptionMenu(root, self.animal_id, *self.choices , style='TMenubutton').grid(row=2, column=1, pady=10, sticky="ew")
            self.featmenu = Listbox(root, selectmode='multiple', height=5, exportselection=0)
            self.featmenu.grid(row=3, column=1, pady=10, sticky="ew")
            for choice in self.choices[1:]:
                self.featmenu.insert(END, choice)
            self.scrollbar = ttk.Scrollbar(root, orient="vertical")
            self.scrollbar.grid(row=3, column=1, sticky="nse",pady=10)
            self.scrollbar.config(command=self.featmenu.yview)
            self.featmenu.config(yscrollcommand=self.scrollbar.set)
  

    def run(self):
        
        # this function will initialize the blinder.py script to process the data in the input file, if given
        
        if busy:
            messagebox.showwarning("Blindr running", "The process is already started. Please wait until it has finished.")
            return

        self.feats = [self.featmenu.get(i) for i in self.featmenu.curselection()]

        if self.filename == None:
            messagebox.showwarning("No file selected", "Please select a file and try again.")

        elif self.no_of_groups.get() == ' ':
            messagebox.showwarning("No of groups not selected", "Please select the needed number of groups and try again.")

        elif self.animal_id.get() == ' ':
            messagebox.showwarning("No animal ID selected", "Please select an animal ID and try again.")

        elif len(self.feats) < 1:
            messagebox.showwarning("No features selected", "Please select at least one animal feature and try again.")

        elif self.animal_id.get() in self.feats:
            messagebox.showwarning("ID selected as feature", "The animal ID cannot be used as a feature. Please select a different ID or deselect it as a feature and try again.")

        else:
            f = open("args.txt","w+")
            f.write(self.no_of_groups.get()+"\n")
            f.write(self.filename +"\n")
            file = self.filename.rsplit('.',1)
            file_type = file[1]
            file_name = file[0].rsplit('/',1)[1]
            output = file[0]+"_blinded/"
            f.write(output +"\n")
            f.write(file_type +"\n")
            f.write(file_name +"\n")
            f.write(self.animal_id.get() + "\n")
            for feat in self.feats:
                f.write(feat + "\n")
            f.close()
            Threader(name='Run-blindr')
            messagebox.showwarning("Script running", "Please wait a moment. The results will open automatically.")


    def extract_me(self):

        # this function reads in the input file 

        self.filename = fd.askopenfilename(filetypes=[("EXCEL/CSV Files","*.xls *.xlsx *.csv")])
        self.readfile()


    def exit(self):

        # this function closes the application

        leave = False
        if busy:     
            if messagebox.askokcancel("Quit", "The script is currently running. Do you want to abort quit?"):
                leave = True
        else:
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                leave = True
        if leave:
            if os.path.isfile('args.txt'):
                os.remove('args.txt')
            root.destroy()



class Threader(threading.Thread):

    # this class is used to start the blindr script in a seperate thread

    def __init__(self, *args, **kwargs):

        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        self.start()

    def run(self):

        global busy
        import blindr
        busy = True
        blindr.activate()
        busy = False


if __name__ == '__main__':
    app = App()