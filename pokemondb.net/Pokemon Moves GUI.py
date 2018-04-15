'''This application is a basic GUI to display move data from pokemon
Different search filters can be applied to sort the moves

Created by: Patrick Touchette
Date: 2018-03-04

Thanks to https://pokemondb.net/ , the data was scraped from that website

'''

import tkinter as tk
from tkinter import ttk
import pandas as pd
from PIL import Image, ImageTk

#GOBAL SETTINGS
TITLE_FONT = ('Droid, 20')
LABEL_FONT = ('Droid, 10')
MOVES_HEADINGS_FONT = ('Droid', 10, 'bold')
MOVES_FONT = ('Droid', 10)
FRAME_PADDING = (20, 10)  #padx, pady
WIDGET_PADDING = (8, 4)  #padx, pady
COLORS = {'Normal': '#8a8a59','Fire': '#f08030' ,'Water': '#6890f0','Electric': '#f8d030','Grass': '#78c850','Ice': '#98d8d8',
                    'Fighting': '#c03028','Poison': '#a040a0','Ground': '#e0c068','Flying': '#a890f0','Psychic': '#f85888','Bug': '#a8b820',
                    'Rock': '#b8a038','Ghost': '#705898','Dragon': '#7038f8','Dark': '#705848','Steel': '#b8b8d0','Fairy': '#e898e8'}

class Main_Application(tk.Frame):
    def __init__(self, root, dataframe):
        tk.Frame.__init__(self, root)
        self.root = root
        self.root.title('Moves')
        self.root.iconphoto(self.root, tk.PhotoImage(file='img/pokeball.png'))
        self.root.geometry('+50+15') #('1050x600+50+50')
        self.df = dataframe
        self.types = list(set(df['Type']))

        self.create_frames()
        self.add_padding(self.grid_slaves())
        self.populate_rows(self.df[0:50])

    def create_frames(self):
        self.title_frame = Title_Frame(self, 'Pokemon Move List')
        self.search_frame = Search_Filters(self)
        self.sort_buttons_frame = Sort_Buttons(self)
        self.moves_frame = Moves_Frame(self)

        self.title_frame.grid(row=0, column=0, sticky=tk.W)
        self.search_frame.grid(row=1, column=0, sticky=tk.W)
        self.sort_buttons_frame.grid(row=2, column=0, sticky=tk.W)
        self.moves_frame.grid(row=3, column=0, sticky=tk.W)


    def add_padding(self, slaves):
        '''recursive funtion to loop through all the layers of frames and widgets'''
        for slave in slaves:
            print(slave.widgetName + '    ' + str(slave) + '    SLAVES' + str(slave.grid_slaves()))
            if slave.widgetName == 'frame':
                #slave.configure(highlightbackground="black", highlightcolor="black", highlightthickness=1) #For testing
                slave.grid_configure(padx=FRAME_PADDING[0], pady=FRAME_PADDING[1])
            else:
                slave.grid_configure(padx=WIDGET_PADDING[0], pady=WIDGET_PADDING[1])

            if len(slave.grid_slaves()) > 0:
                self.add_padding(slave.grid_slaves())

    def populate_rows(self, data):
        '''Displays the data contained in the dataframe that is passed to it'''
        for i in range(len(data)):
            self.row = Moves_Row(self.moves_frame.frame, data.iloc[i], MOVES_FONT)
            self.row.grid(row=i+1, column=0, sticky=tk.W, pady=2)
            self.row.configure(highlightbackground="grey", highlightcolor="grey", highlightthickness=1)

            #Bind all widgets inside row to scrollbar to enable scrolling
            self.row.bind("<MouseWheel>", self.moves_frame.mouse_wheel)
            for widget in self.row.winfo_children():
                widget.bind("<MouseWheel>", self.moves_frame.mouse_wheel)

    def clear_rows(self):
        '''Deletes all rows and widgets in the moves_frame'''
        slaves = self.moves_frame.frame.grid_slaves()
        for slave in slaves:
            slave.destroy()

    def clear_button(self):
        '''button that clears all user selections'''
        self.clear_rows()
        self.search_frame.type_combobox.current(0)
        self.search_frame.category_combobox.current(0)
        self.search_frame.search.set('')
        self.sort_buttons_frame.reset_buttons()

    def populate_rows_by_selection(self, event=''):
        '''Displays moves according to combobox selections,type & cat...'''
        self.clear_rows()

        self.search = self.search_frame.search.get()
        self.typ = []
        self.typ.append(self.search_frame.chosen_type.get())
        self.cat = []
        self.cat.append(self.search_frame.chosen_category.get())
        if self.typ[0] == 'All':
            self.typ = self.types
        if self.cat[0] == 'All':
            self.cat = ['Z-Move', 'Physical', 'Status', 'Special']

        self.df2 = self.df[self.df['Type'].isin(self.typ)]
        self.df2 = self.df2[self.df2['Cat.'].isin(self.cat)]
        self.df2 = self.df2[(self.df2['Name'].str.lower().str.contains(self.search)) | (self.df2['Effect'].str.lower().str.contains(self.search))]

        self.apply_button_sort()
        self.populate_rows(self.df2)

    def apply_button_sort(self):
        '''Apply in ascending or descending order, as per button press'''
        sort_direction = self.sort_buttons_frame.sort_direction
        column = self.sort_buttons_frame.sort_column

        if sort_direction == '-':
            pass
        if sort_direction == '▲':
            self.df2 = self.df2.sort_values(by=column, ascending=True)
        if sort_direction == '▼':
            self.df2 = self.df2.sort_values(by=column, ascending=False)


class Title_Frame(tk.Frame):
    def __init__(self, master, title):
        tk.Frame.__init__(self, master)
        self.img = tk.PhotoImage(file='img/65.png')
        self.img_label = ttk.Label(self, image=self.img)
        self.title = ttk.Label(self, text=title, font=TITLE_FONT)
        self.img_label.grid(row=0, column=0, sticky=tk.W)
        self.title.grid(row=0, column=1, sticky=tk.W)

class Search_Filters(tk.Frame):
    '''Creates the search box, type filter and category filter'''
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.search_label = ttk.Label(self, text='Name/Effect', font = LABEL_FONT)
        self.type_label = ttk.Label(self, text='Type', font = LABEL_FONT)
        self.category_label = ttk.Label(self, text='Category', font = LABEL_FONT)
        self.search = tk.StringVar()
        self.search_entry = ttk.Entry(self, width=12, text=self.search, font = LABEL_FONT)
        self.search_entry.bind("<Return>", master.populate_rows_by_selection)

        self.chosen_type = tk.StringVar()
        self.type_combobox = ttk.Combobox(self, width=12, textvariable=self.chosen_type, state='readonly', font = LABEL_FONT)
        self.type_combobox['values'] = [ 'All','Normal','Fire','Water','Electric','Grass','Ice',
                                    'Fighting','Poison','Ground','Flying','Psychic','Bug',
                                    'Rock','Ghost','Dragon','Dark','Steel','Fairy',]
        self.type_combobox.configure(height=len(self.type_combobox['values']))
        self.type_combobox.bind("<<ComboboxSelected>>", master.populate_rows_by_selection)
        self.type_combobox.current(0)

        self.chosen_category = tk.StringVar()
        self.category_combobox = ttk.Combobox(self, width=12, textvariable=self.chosen_category, state='readonly')
        self.category_combobox['values'] = ['All', 'Physical', 'Special', 'Status', 'Z-Move']
        self.category_combobox.bind("<<ComboboxSelected>>", master.populate_rows_by_selection)
        self.category_combobox.current(0)

        self.button_clear = ttk.Button(self, text='Clear', command=master.clear_button)

        self.search_label.grid(row=0, column=0, sticky=tk.W)
        self.search_entry.grid(row=0, column=1, sticky=tk.W)
        self.type_label.grid(row=0, column=2, sticky=tk.W)
        self.type_combobox.grid(row=0, column=3, sticky=tk.W)
        self.category_label.grid(row=0, column=4, sticky=tk.W)
        self.category_combobox.grid(row=0, column=5, sticky=tk.W)
        self.button_clear.grid(row=0, column=6, sticky=tk.W)

class Sort_Buttons(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.font = MOVES_HEADINGS_FONT
        self.names = list(master.df)
        self.sort_column = 'Name'
        self.sort_direction = '▲' #▲ = ascending, ▼ = desencding

        self.b0 = tk.Button(self, text='Name', width=20, font=self.font)
        self.b1 = tk.Button(self, text='Type', width=8, font=self.font)
        self.b2 = tk.Button(self, text='Cat.', width=8, font=self.font)
        self.b3 = tk.Button(self, text='Power', width=8, font=self.font)
        self.b4 = tk.Button(self, text='Acc.', width=7, font=self.font)
        self.b5 = tk.Button(self, text='PP', width=7, font=self.font)
        #self.label6 = ttk.Label(self, text=self.data[6], width=8, font=font).grid(row=0, column=6)
        self.b7 = tk.Button(self, text='Effect', width=49, font=self.font)
        self.b8 = tk.Button(self, text='Prob. (%)', width=8, font=self.font)

        self.configure_buttons()

    def configure_buttons(self):
        buttons = []
        for button in self.winfo_children():
            button.pack(side=tk.LEFT)
            button['text'] = button['text']  + ' -'

        self.b0.config(command=lambda: self.button_press(self.b0))
        self.b1.config(command=lambda: self.button_press(self.b1))
        self.b2.config(command=lambda: self.button_press(self.b2))
        self.b3.config(command=lambda: self.button_press(self.b3))
        self.b4.config(command=lambda: self.button_press(self.b4))
        self.b5.config(command=lambda: self.button_press(self.b5))
        self.b7.config(command=lambda: self.button_press(self.b7))
        self.b8.config(command=lambda: self.button_press(self.b8))

    def button_press(self, button):
        text = button['text'].split()[0]
        sort = button['text'].split()[1]

        for b in self.winfo_children():
            b['text'] = b['text'].split()[0]  + ' -'

        if sort == '-':
            button['text'] = text + ' ▲'
        if sort == '▲':
            button['text'] = text + ' ▼'
        if sort == '▼':
            button['text'] = text + ' -'

        self.sort_column = text
        self.sort_direction = button['text'].split()[1]

        self.master.populate_rows_by_selection()

    def reset_buttons(self):
        for b in self.winfo_children():
            b['text'] = b['text'].split()[0]  + ' -'
        self.sort_column = 'Name'
        self.sort_direction = '▲'

class Moves_Frame(tk.Frame):
    '''Creates a scrollable region to display all the moves data
    # https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter/3092341#3092341'''
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.canvas = tk.Canvas(self, borderwidth=0, background="#e6e6e6") #ffffff
        self.canvas.configure(width=1000, height=500)
        self.frame = tk.Frame(self.canvas, background="#e6e6e6")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.grid(row=0, column=1, sticky=tk.NS)
        self.canvas.grid(row=0, column=0, sticky=tk.W)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        # Add mousewheel scrolling with Windows OS
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)
        self.frame.bind("<MouseWheel>", self.mouse_wheel)
        self.canvas.bind("<Up>",    lambda event: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Down>",  lambda event: self.canvas.yview_scroll( 1, "units"))
        # with Linux OS
        self.canvas.bind("<Button-4>", self.mouse_wheel)
        self.canvas.bind("<Button-5>", self.mouse_wheel)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def mouse_wheel(self, event):
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units")

class Moves_Row(tk.Frame):
    def __init__(self,master, data, font):
        tk.Frame.__init__(self, master)
        self.data = data
        self.label0 = tk.Label(self, text=self.data['Name'], width=20, font=MOVES_HEADINGS_FONT)
        self.label1 = tk.Label(self, text=self.data['Type'], width=8, font=font)
        self.label2 = tk.Label(self, text=self.data['Cat.'], width=8, font=font)
        self.label3 = tk.Label(self, text=self.data['Power'], width=8, font=font)
        self.label4 = tk.Label(self, text=self.data['Acc.'], width=8, font=font)
        self.label5 = tk.Label(self, text=self.data['PP'], width=8, font=font)
        #self.label6 = ttk.Label(self, text=self.data[6], width=8, font=font).grid(row=0, column=6)
        self.label7 = tk.Label(self, text=self.data['Effect'], width=50, font=font)
        self.label8 = tk.Label(self, text=self.data['Prob. (%)'], width=8, font=font)

        self.label0.grid(row=0, column=0)
        self.label1.grid(row=0, column=1)
        self.label2.grid(row=0, column=2)
        self.label3.grid(row=0, column=3)
        self.label4.grid(row=0, column=4)
        self.label5.grid(row=0, column=5)
        self.label7.grid(row=0, column=7)
        self.label8.grid(row=0, column=8)

        self.label1.config(background=COLORS[self.data['Type']])
        #self.label1.config(highlightbackground="black", highlightcolor="black", highlightthickness=10)
        self.label0.config(wraplength=120)
        self.label7.config(wraplength=350)

        self.justify_labels()

    def justify_labels(self):
        for label in self.grid_slaves():
            label.config(anchor=tk.W, justify=tk.LEFT)
            label.grid_configure(pady=WIDGET_PADDING[1])

    def delete_rows(self):
        '''Deletes all move labels'''
        for slave in self.grid_slaves():
            slave.destroy()

def to_int(string):
    '''Converts strings to integers. Used to clean the dataframe'''
    try:
        integer = int(string)
    except ValueError:
        integer = int()
    return integer

if __name__ == '__main__':
    df = pd.read_csv('scraped data/moves.csv', encoding='latin1')
    df['Power'] = df['Power'].apply(to_int)
    df = df.fillna('-')

    root = tk.Tk()
    app = Main_Application(root, df)
    app.grid(row=0, column=0, sticky=tk.W)

    root.mainloop()
