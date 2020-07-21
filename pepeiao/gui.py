import tkinter as tk
import pepeiao.feature

class GraphicalUserInterface:
    def __init__(self):
        self.var = None
        # create window
        self.window = tk.Tk()
        # create widget
        self.greeting = tk.Label(text="Input .wav files")
        # add widget to window
        self.greeting.pack()
        # create entry widget for user input
        self.entry = tk.Entry()
        self.entry.bind('<Return>', self.onReturn)
        self.entry.pack()
        # required for window to be shown
        self.window.mainloop()

    def onReturn(self, event):
        """When Return key is pressed in entry widget"""
        self.var = self.entry.get()
        print(self.var)


# app = GraphicalUserInterface()
pepeiao.feature.main("")
