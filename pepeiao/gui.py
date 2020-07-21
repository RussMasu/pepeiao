import tkinter as tk
import subprocess
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
file = "C:/Users/Russ Masuda/PycharmProjects/birdNN/data/S4A01450_20170506_063300.wav"
subprocess.run(["pepeiao", "feature", file])
