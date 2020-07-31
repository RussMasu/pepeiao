import tkinter as tk
from tkinter import ttk, filedialog
import subprocess
from os import getcwd


def processDialog(self, filename):
    for file in filename:
        self.files.append(file)
    self.text.config(state='normal')
    self.text.insert(tk.END, filename)
    self.text.config(state='disabled')


def clearDialog(self):
    self.files.clear()
    self.text.config(state='normal')
    self.text.delete('1.0', tk.END)
    self.text.config(state='disabled')


def pepeiaoSubprocess(self, file, arg, model, savename):
    # run pepeiao predict
    if arg is "predict":
        args = ["pepeiao", arg, savename]
        for item in file:
            args.append(item)
    # run pepeiao train
    elif arg is "train":
        args = ["pepeiao", arg, savename]
        for item in file:
            args.append(item)
        args.append(savename)
    # default case
    else:
        args = ["pepeiao", arg]
        for item in file:
            args.append(item)

    process = subprocess.Popen(args, stdout=subprocess.PIPE)

    while True:
        output = process.stdout.readline()
        # break out of loop if exit code is returned
        if process.poll() is not None:
            rc = process.poll()
            break
        if output:
            self.text.insert(tk.END, output.strip())
            self.update()
    # if subprocess succeeds
    if rc is 0:
        self.text.insert(tk.END, "\n\nFinished writing files")
        # enable link to next screen
        self.button1.config(state='normal')
    # else
    else:
        self.text.delete('1.0', tk.END)
        self.text.insert(tk.END, "Invalid file name received")

    self.text.config(state='disabled')


def resetPage(self, string, page):
    self.text.config(state='normal')
    self.text.delete('1.0', tk.END)
    self.text.insert(tk.END, "Creating " + string + " Files. . .")
    self.text.config(state='disabled')
    self.controller.show_frame(page)


class GraphicalUserInterface(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.var = None
        self.model = None
        self.saveName = None

        # create container object
        container = tk.Frame(self)
        container.grid(row=0, column=0)
        #container.pack(side="top", fill="both", expand=True)

        #container.grid_rowconfigure(0, weight=1)
        #container.grid_columnconfigure(0, weight=1)

        # frames dict to hold pages
        self.frames = {}

        for F in (homePage, inputPage, featurePage, featurePage2, trainPage, trainPage2, predictPage, predictPage2):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(homePage)

    def show_frame(self, page):
        #"""
        # remove all frames from grid
        for frame in self.frames:
            self.frames.get(frame).grid_remove()
        # display page to grid
        p = self.frames.get(page)
        p.grid()
        """
        # allow grid to finishing loading before generating event
        p = self.frames.get(page)
        p.tkraise()
        """
        p.update()
        p.event_generate("<<onDisplay>>")


class homePage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Make predictions from model file or Create a model file?")
        label.grid(row=0, column=0, padx=10, pady=10)

        # buttons with quit, create, and predict options
        button = ttk.Button(self, text="Quit", command=self.closeWindow)
        button.grid(row=1, column=0, sticky='W')

        button = ttk.Button(self, text="Create", command=lambda: controller.show_frame(inputPage))
        button.grid(row=1, column=1, sticky='E')

        button1 = ttk.Button(self, text="Predict", command=lambda: controller.show_frame(predictPage))
        button1.grid(row=1, column=2)

    def closeWindow(self):
        self.controller.destroy()


class inputPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text=".feat files are required to train the neural network.\n"
                                    "  Do you wish to load existing .feat "
                                    "files or create new .feat files from .wav files?")
        label.grid(row=0, column=0, padx=10, pady=10)

        button1 = tk.Button(self, text="<<Back", command=lambda: controller.show_frame(homePage))
        button1.grid(row=1, column=0, sticky='W')

        button = tk.Button(self, text="Create", command=lambda: controller.show_frame(featurePage))
        button.grid(row=1, column=1, sticky='E')

        button1 = tk.Button(self, text="Load", command=lambda: controller.show_frame(trainPage))
        button1.grid(row=1, column=2)


class featurePage(tk.Frame):
    def __init__(self, parent, controller):
        # need to reference controller in function
        self.controller = controller
        tk.Frame.__init__(self, parent)
        self.label = ttk.Label(self, text="Enter training .wav files")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.files = []
        self.text = tk.Text(self, state='disabled')
        self.text.see(tk.END)
        self.text.grid(row=1, column=0)

        # create frame holding add and clear buttons
        frame = tk.Frame(self)
        frame.grid(row=2, column=0)
        button = ttk.Button(frame, text="Add Files", command=self.openDialogbox)
        button.grid(row=0, column=0)
        button1 = ttk.Button(frame, text="Clear Files", command=self.clearDialogbox)
        button1.grid(row=0, column=1)

        button2 = ttk.Button(self, text="<<Back", command=lambda: controller.show_frame(inputPage))
        button2.grid(row=3, column=0, sticky="W")

        button3 = ttk.Button(self, text="Submit", command=self.submitText)
        button3.grid(row=3, column=1)


    def submitText(self, *event):
        self.controller.var = self.files
        self.controller.show_frame(featurePage2)

    def openDialogbox(self):
        filename = tk.filedialog.askopenfilenames(initialdir=getcwd(), title="Select training .wav files",
                                                  filetypes=[("wav files", "*.wav")])
        processDialog(self, filename)

    def clearDialogbox(self):
        clearDialog(self)


class featurePage2(tk.Frame):
    def __init__(self, parent, controller):
        # need to reference controller in function
        self.controller = controller
        tk.Frame.__init__(self, parent)

        self.text = tk.Text(self)
        self.text.insert(tk.END, "Creating Feat Files. . .")
        self.text.config(state='disabled', background="light grey")
        self.text.see(tk.END)
        self.text.grid(row=0, column=0)

        button = ttk.Button(self, text="<<Back", command=self.resBack)
        button.grid(row=1, column=0)

        self.button1 = ttk.Button(self, text="Next>>", command=self.resForward)
        self.button1.config(state='disabled')
        self.button1.grid(row=1, column=1)

        # when page is displayed create file
        self.bind("<<onDisplay>>", self.createFile)

    def createFile(self, event):
        self.button1.config(state='disabled')
        file = self.controller.var
        self.controller.var = None
        self.text.config(state='normal')
        pepeiaoSubprocess(self, file, "feature", None, None)

    def resBack(self):
        resetPage(self, "Feat", featurePage)

    def resForward(self):
        resetPage(self, "Feat", trainPage)

    #TODO make window output scrollable
    #TODO write predictions to csv file
    #TODO add load file dialog box to predict
    #TODO fix error where only part of window is shown
    #TODO surpress not responding message on executing command
    #TODO write WINDOWS starting code


class trainPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)

        # label and text box to enter feat files
        self.label = ttk.Label(self, text="Enter .feat files")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.files = []
        self.text = tk.Text(self, state='disabled')
        self.text.see(tk.END)
        self.text.grid(row=0, column=1)

        # create frame holding add and clear buttons
        frame = tk.Frame(self)
        frame.grid(row=1, column=1)
        button = ttk.Button(frame, text="Add Files", command=self.openDialogbox)
        button.grid(row=0, column=0)
        button1 = ttk.Button(frame, text="Clear Files", command=self.clearDialogbox)
        button1.grid(row=0, column=1)

        # empty space
        blank = tk.Label(self)
        blank.grid(row=2, column=0)

        # label and drop down menu holding model choices
        self.label1 = ttk.Label(self, text="Select model")
        self.label1.grid(row=3, column=0, sticky='E')

        choices = {'bulbul', 'conv', 'gru', 'transfer'}
        self.option = tk.StringVar(self)
        self.option.set('bulbul')
        menu = tk.OptionMenu(self, self.option, *choices)
        menu.grid(row=3, column=1, sticky='W')

        # label and entry box to enter saved name
        self.label2 = ttk.Label(self, text="Save as:")
        self.label2.grid(row=4, column=0)
        self.entry = ttk.Entry(self)
        self.entry.grid(row=4, column=1, sticky='W')

        # back and submit buttons
        button2 = ttk.Button(self, text="<<Back", command=lambda: controller.show_frame(inputPage))
        button2.grid(row=5, column=0)

        button3 = ttk.Button(self, text="Submit", command=self.submitText)
        button3.grid(row=5, column=2)

    def submitText(self, *event):
        self.controller.var = self.files
        self.controller.model = self.option.get()
        self.controller.saveName = self.entry.get()
        self.controller.show_frame(trainPage2)

    def openDialogbox(self):
        filename = tk.filedialog.askopenfilenames(initialdir=getcwd(), title="Select feat files",
                                                  filetypes=[("feat files", "*.feat")])
        processDialog(self, filename)

    def clearDialogbox(self):
        clearDialog(self)


class trainPage2(tk.Frame):
    def __init__(self, parent, controller):
        # need to reference controller in function
        self.controller = controller
        tk.Frame.__init__(self, parent)

        self.text = tk.Text(self)
        self.text.insert(tk.END, "Creating Model File. . .")
        self.text.config(state='disabled', background="light grey")
        self.text.see(tk.END)
        self.text.grid(row=0, column=0)

        button = ttk.Button(self, text="<<Back", command=self.resBack)
        button.grid(row=1, column=0)

        self.button1 = ttk.Button(self, text="Next>>", command=self.resForward)
        self.button1.config(state='disabled')
        self.button1.grid(row=1, column=1)
        # when page is displayed create file
        self.bind("<<onDisplay>>", self.createFile)

    def createFile(self, event):
        self.button1.config(state='disabled')
        file = self.controller.var
        model = self.controller.model
        saveName = self.controller.saveName
        self.controller.var = None
        self.controller.model = None
        self.controller.saveName = None

        self.text.config(state='normal')
        pepeiaoSubprocess(self, file, "train", model, saveName)

    def resBack(self):
        resetPage(self, "Model", trainPage)

    def resForward(self):
        resetPage(self, "Model", homePage)


class predictPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)

        # label and text box to enter feat files
        self.label = ttk.Label(self, text="Enter testing .wav files")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.files = []
        self.text = tk.Text(self, state='disabled')
        self.text.see(tk.END)
        self.text.grid(row=0, column=1)

        # create frame holding add and clear buttons
        frame = tk.Frame(self)
        frame.grid(row=1, column=1)
        button = ttk.Button(frame, text="Add Files", command=self.openDialogbox)
        button.grid(row=0, column=0)
        button1 = ttk.Button(frame, text="Clear Files", command=self.clearDialogbox)
        button1.grid(row=0, column=1)

        # empty space
        blank = tk.Label(self)
        blank.grid(row=2, column=0)

        # label and entry box to enter saved name
        self.label2 = ttk.Label(self, text="Load model:")
        self.label2.grid(row=3, column=0)
        self.entry = ttk.Entry(self)
        self.entry.grid(row=3, column=1, sticky='W')

        # back and submit buttons
        button2 = ttk.Button(self, text="<<Back", command=lambda: controller.show_frame(homePage))
        button2.grid(row=4, column=0)

        button3 = ttk.Button(self, text="Submit", command=self.submitText)
        button3.grid(row=4, column=2)

    def submitText(self, *event):
        self.controller.var = self.files
        self.controller.saveName = self.entry.get()
        self.controller.show_frame(predictPage2)

    def openDialogbox(self):
        filename = tk.filedialog.askopenfilenames(initialdir=getcwd(), title="Select testing .wav files",
                                                  filetypes=[("wav files", "*.wav")])
        processDialog(self, filename)

    def clearDialogbox(self):
        clearDialog(self)


class predictPage2(tk.Frame):
    def __init__(self, parent, controller):
        # need to reference controller in function
        self.controller = controller
        tk.Frame.__init__(self, parent)

        self.text = tk.Text(self)
        self.text.insert(tk.END, "Creating Prediction Files. . .")
        self.text.config(state='disabled', background="light grey")
        self.text.see(tk.END)
        self.text.grid(row=0, column=0)

        button = ttk.Button(self, text="<<Back", command=self.resBack)
        button.grid(row=1, column=0)

        self.button1 = ttk.Button(self, text="Next>>", command=self.resForward)
        self.button1.config(state='disabled')
        self.button1.grid(row=1, column=1)

        # when page is displayed create file
        self.bind("<<onDisplay>>", self.createFile)

    def createFile(self, event):
        self.button1.config(state='disabled')
        file = self.controller.var
        saveName = self.controller.saveName
        self.controller.var = None
        self.controller.saveName = None

        self.text.config(state='normal')
        pepeiaoSubprocess(self, file, "predict", None, saveName)

    def resBack(self):
        resetPage(self, "Prediction", predictPage)

    def resForward(self):
        resetPage(self, "Prediction", homePage)


app = GraphicalUserInterface()
app.title('Pepeiao Neural Network')
app.mainloop()
# data\S4A01450_20170507_180200.wav data\S4A01450_20170507_190200.wav
