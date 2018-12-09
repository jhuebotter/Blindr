import platform
import sys
import os
import tkinter
from tkinter import *
from tkinter import simpledialog, ttk
from tkinter import filedialog as fd
from tkinter import messagebox


class App():
   def __init__(self):
       self.filename = None
       self.root = Tk()
       self.root.title('Blindr')
       self.root.geometry("540x230")
       #background_image = PhotoImage('mouse.jpeg')

       # background="..." doesn't work...
       ttk.Style().configure('TMenubutton', foreground='black', background='white',font=("Arial", 18),relief="rigid")
       ttk.Style().configure('green/black.TButton', foreground='black', background='white',font=("Arial", 18))
       ttk.Style().configure('TLabel',font=("Arial", 18))


       l1 = ttk.Label(self.root, text="Select your input file").grid(row=0,padx=20,sticky=tkinter.W)
       # l1.pack()

       button1 = ttk.Button(self.root, text='open explorer', command=self.extract_me,style='green/black.TButton').grid(row=0, column=1, pady=20)
       # button1.pack()

       l2 = ttk.Label(self.root, text="Number of groups to create ",style='TLabel').grid(row=1,padx=20,pady=20,sticky=tkinter.W)
       # l2.pack()

       self.variable = StringVar(self.root)
       self.variable.set("2")  # default value

       w = ttk.OptionMenu(self.root, self.variable, "2", "3", "4", "5", "6", "7", "8", "9", "10",style = 'TMenubutton').grid(row=1, column=1, pady=20, sticky=tkinter.E)
       # w.pack()

       #print(self.variable.get())

       #l3 = ttk.Label(self.root, text="End of Selection ").grid(row=2)
       # l3.pack()

       button2 = ttk.Button(self.root, text='Run Blindr', command=self.quit,style='green/black.TButton').grid(row=2, column=0, pady=20)
       
       button2 = ttk.Button(self.root, text='Close', command=self.close_app,style='green/black.TButton').grid(row=2, column=1, pady=20)
       # button2.pack()


       self.root.mainloop()

   def extract_me(self):

       self.filename = fd.askopenfilename(filetypes=[("EXCEL/CSV Files","*.xls *.xlsx *.csv")])
       #print(self.filename)

   def close_app(self):
       
       if os.path.isfile('args.txt'):
            os.remove('args.txt')
       sys.exit()


   def quit(self):

       if self.filename:
             f = open("args.txt","w+")
             f.write(self.variable.get()+"\n")
             f.write(self.filename +"\n")
             file = self.filename.rsplit('.',1)#[0]+"_Blinded/"
             file_type = file[1]
             file_name = file[0].rsplit('/',1)[1]
             output = file[0]+"_blinded/"
             f.write(output +"\n")
             f.write(file_type +"\n")
             f.write(file_name +"\n")
             f.close()
             self.root.destroy()
       else:
            messagebox.showwarning("No file selected", "Please select a file and try again.")

app = App()







