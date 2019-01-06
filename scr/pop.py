#!/usr/bin/python

# this script contains the visual interaction with the user and starts the blindr.py script

import platform
import sys
import os
import threading
import time
import tkinter
from tkinter import *
from tkinter import simpledialog, ttk
from tkinter import filedialog as fd
from tkinter import messagebox


class App():

    # this is the main gui window for user interaction with a few buttons

    def __init__(self):
        super(App, self).__init__()
        self.filename = None
        self.root = Tk()
        self.root.title('Blindr')
        self.root.geometry("540x230")

        ttk.Style().configure('TMenubutton', foreground='black', background='white',font=("Arial", 18),relief="rigid")
        ttk.Style().configure('green/black.TButton', foreground='black', background='white',font=("Arial", 18))
        ttk.Style().configure('TLabel',font=("Arial", 18))

        l1 = ttk.Label(self.root, text="Select your input file").grid(row=0,padx=20,sticky=tkinter.W)

        button1 = ttk.Button(self.root, text='open explorer', command=self.extract_me,style='green/black.TButton').grid(row=0, column=1, pady=20)

        l2 = ttk.Label(self.root, text="Number of groups to create ",style='TLabel').grid(row=1,padx=20,pady=20,sticky=tkinter.W)

        self.variable = StringVar(self.root)
        self.variable.set("2")

        w = ttk.OptionMenu(self.root, self.variable, "2", "2", "3", "4", "5", "6", "7", "8", "9", "10",style = 'TMenubutton').grid(row=1, column=1, pady=20, sticky=tkinter.E)

        button2 = ttk.Button(self.root, text='Run Blindr', command=self.run,style='green/black.TButton').grid(row=2, column=0, pady=20)
       
        button3 = ttk.Button(self.root, text='Close', command=self.close_app,style='green/black.TButton').grid(row=2, column=1, pady=20)

        self.root.mainloop()


    def extract_me(self):

        # this function reads in the input file 

        self.filename = fd.askopenfilename(filetypes=[("EXCEL/CSV Files","*.xls *.xlsx *.csv")])


    def close_app(self):

        # this function closes the application
       
        if os.path.isfile('args.txt'):
            os.remove('args.txt')
        sys.exit()
        self.root.destroy()


    def run(self):

        # this function will initialize the blinder.py script to process the data in the input file, if given

        if self.filename:
            f = open("args.txt","w+")
            f.write(self.variable.get()+"\n")
            f.write(self.filename +"\n")
            file = self.filename.rsplit('.',1)
            file_type = file[1]
            file_name = file[0].rsplit('/',1)[1]
            output = file[0]+"_blinded/"
            f.write(output +"\n")
            f.write(file_type +"\n")
            f.write(file_name +"\n")
            f.close()
            try:
                import blindr
                blindr.activate()                             
            except:
                pass
        else:
            messagebox.showwarning("No file selected", "Please select a file and try again.")


        def on_closing(self):

            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                close_app()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

       
if __name__ == '__main__':
    app = App()







