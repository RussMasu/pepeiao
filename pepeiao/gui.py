import tkinter as tk
import subprocess
import pepeiao.feature

class GraphicalUserInterface:
    def __init__(self):
        """input window gui"""
        self.var = None
        self.window = tk.Tk()

        self.greeting = tk.Label(text=".feat files are required to train the neural network.\n"
                                      " Do you wish to load existing .feat files or create new .feat"
                                      " files from .wav files? ", width=75, height=10)  # .grid(row=0, column=0
        self.greeting.pack()

        self.button = tk.Button(text="Create", width=10, height=2, command=self.linkWindow)  # .grid(row=2, column=1)
        self.button.pack(side="right")
        self.window.mainloop()

    def feature(self):
        """feature window gui"""
        # create window
        self.window = tk.Tk()
        # create widget
        self.greeting = tk.Label(text="Input .wav files", width=20, height=2)#.grid(row=0, column=0)
        # add widget to window
        self.greeting.pack()
        # create text box for user input
        self.text = tk.Text()#.grid(row=1, column=0)
        self.text.bind('<Return>', self.onReturn)
        self.text.pack()
        # create submit button
        self.button = tk.Button(text="Submit", width=10, height=2, command=self.onClick)#.grid(row=2, column=1)
        self.button.pack(side="right")
        # required for window to be shown
        self.window.mainloop()

    def onReturn(self, event):
        """When Return key is run pepeiao.feature with args taken from text box"""
        self.var = self.text.get("1.0", tk.END)  # passing return
        # parse user input
        self.var = self.var[:-1]
        #TODO load in different window
        self.greeting.configure(text="Loading wav files. . .")
        subprocess.run(["pepeiao", "feature", self.var])
        self.var = None

    def onClick(self):
        self.var = self.text.get("1.0", tk.END)
        # parse user input
        self.var = self.var[:-1]
        subprocess.run(["pepeiao", "feature", self.var])
        self.var = None

    def linkWindow(self):
        pass

app = GraphicalUserInterface()
#file = "C:/Users/Russ Masuda/PycharmProjects/birdNN/data/S4A01450_20170507_180200.wav"
