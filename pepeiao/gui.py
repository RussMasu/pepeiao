import tkinter as tk
import subprocess

class GraphicalUserInterface(tk.Tk):
    def __init__(self, *args, **kwargs):
        # self.current = None
        self.frames = {}
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.grid()
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # add all pages to self.frames
        for f in (inputPage, featurePage):
            frame = f(container, self)
            self.frames[f] = frame

        # show starting page on init
        self.show_frame(inputPage)

    def show_frame(self, page):
        # remove all frames from grid
        for frame in self.frames:
            self.frames.get(frame).grid_remove()
        # display page to grid
        self.frames.get(page).grid()
        # self.current = page


class inputPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text=".feat files are required to train the neural network.\n"
                                    "  Do you wish to load existing .feat "
                                    "files or create new .feat files from .wav files?")
        label.grid(row=0, column=0)

        button = tk.Button(self, text="Create",
                            command=lambda: controller.show_frame(featurePage))
        button.grid(row=1, column=1)
        #self.window.mainloop()


class featurePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Enter Feat Files")
        label.grid(row=0, column=0)

        #text = tk.Text()
        text = tk.Entry()
        text.grid(row=0, column=1)

        button = tk.Button(self, text="<<Back",
                            command=lambda: controller.show_frame(inputPage))
        button.grid(row=1, column=1)
"""
    def onReturn(self, event):
        #When Return key is run pepeiao.feature with args taken from text box
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
"""
app = GraphicalUserInterface()
app.mainloop()
#file = "C:/Users/Russ Masuda/PycharmProjects/birdNN/data/S4A01450_20170507_180200.wav"
