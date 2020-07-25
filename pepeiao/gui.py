import tkinter as tk
from tkinter import ttk
import subprocess
import sys
from io import StringIO


class GraphicalUserInterface(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.var = None

        # create container object
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # frames dict to hold pages
        self.frames = {}

        for F in (inputPage, featurePage, featurePage2):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(inputPage)

    def show_frame(self, page):
        # remove all frames from grid
        for frame in self.frames:
            self.frames.get(frame).grid_remove()
        # display page to grid
        p = self.frames.get(page)
        p.grid()
        # allow grid to finishing loading before generating event
        p.update()
        p.event_generate("<<onDisplay>>")





class inputPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text=".feat files are required to train the neural network.\n"
                                    "  Do you wish to load existing .feat "
                                    "files or create new .feat files from .wav files?")
        #label.grid(row=0, column=0, padx=10, pady=10)
        label.pack(padx=10, pady=20)

        button = tk.Button(self, text="Create",
                            command=lambda: controller.show_frame(featurePage))
        #button.grid(row=2, column=0)
        button.pack(side='right')


class featurePage(tk.Frame):
    def __init__(self, parent, controller):
        # need to reference controller in function
        self.controller = controller
        tk.Frame.__init__(self, parent)
        self.label = ttk.Label(self, text="Enter Feat Files")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.text = tk.Text(self)
        self.text.bind("<Return>", self.processText)
        self.text.grid(row=1, column=0)

        button = ttk.Button(self, text="<<Back",
                            command=lambda: controller.show_frame(inputPage))
        button.grid(row=2, column=0)

        button1 = ttk.Button(self, text="Submit",
                             command=self.processText)
        button1.grid(row=2, column=1)


    def processText(self, *event):
        str = self.text.get("1.0", tk.END)
        # remove last char from var
        str = str[:-1]
        self.controller.var = str
        self.controller.show_frame(featurePage2)


class featurePage2(tk.Frame):
    def __init__(self, parent, controller):
        # need to reference controller in function
        self.controller = controller
        tk.Frame.__init__(self, parent)
        self.label = ttk.Label(self, text="Creating Feat Files. . .")
        self.label.grid(row=0, column=0, padx=100, pady=20)

        button = ttk.Button(self, text="<<Back",
                            command=lambda: controller.show_frame(featurePage))
        button.grid(row=1, column=0)
        # when page is displayed create file
        self.bind("<<onDisplay>>", self.createFile)

    def createFile(self, event):
        file = self.controller.var
        # create temp stream
        temp_out = StringIO()
        # replace stdout with temp stream
        sys.stdout = temp_out
        subprocess.run(['pepeiao', 'feature', file])
        self.controller.var = None
        # create temp stream
        self.label.configure(text=temp_out.read())
        #TODO redirec stdout/stderr to label


app = GraphicalUserInterface()
app.title('Pepeiao Neural Network')
app.mainloop()
#file = "C:/Users/Russ Masuda/PycharmProjects/birdNN/data/S4A01450_20170507_180200.wav"
