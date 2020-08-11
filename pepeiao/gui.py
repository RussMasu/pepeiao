import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import tkinter.font as font
import subprocess
from os import getcwd
import re

# TODO write predictions to csv file
# TODO clean up output
# TODO output stderr instead of "Error Occurred"
# TODO convert program to run on multiple threads
# TODO write WINDOWS starting code

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
    # generate args
    if arg is "predict":
        args = ["pepeiao", arg, savename]
        for item in file:
            args.append(item)
        print(args)
    elif arg is "train":
        args = ["pepeiao", arg, model]
        for item in file:
            args.append(item)
        args.append(savename)
    else:
        args = ["pepeiao", arg]
        for item in file:
            args.append(item)

    # run subprocess
    process = subprocess.Popen(args, stdout=subprocess.PIPE)

    while True:
        output = process.stdout.readline()
        if output is not None:
            self.text.insert(tk.END, output)
            self.text.see("end")
            self.update()
        # break out of loop if exit code is returned
        if process.poll() is not None:
            rc = process.poll()
            break
    # if subprocess succeeds
    if rc is 0:
        self.text.insert(tk.END, "\n\nFinished writing files")
        self.button1.config(state='normal')
    else:
        self.text.insert(tk.END, "Error Occurred.")


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

        # frames dict to hold pages
        self.frames = {}

        for F in (homePage, inputPage, featurePage, featurePage2, trainPage, trainPage2, predictPage, predictPage2):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(homePage)

    def show_frame(self, page):
        p = self.frames.get(page)
        p.tkraise()
        p.update()
        p.event_generate("<<onDisplay>>")


class homePage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Create a neural network or make predictions from neural network?",
                         font=font.Font(size=12, family='Helvetica'))
        label.pack(pady=100)

        # buttons with quit, create, and predict options

        button = ttk.Button(self, text="Quit", command=self.closeWindow)
        button.pack(side='left')
        frame = tk.Frame(self)
        frame.pack(side='right')
        button = ttk.Button(frame, text="Create", command=lambda: controller.show_frame(inputPage))
        button.grid(row=0, column=0)
        button1 = ttk.Button(frame, text="Predict", command=lambda: controller.show_frame(predictPage))
        button1.grid(row=0, column=1)

    def closeWindow(self):
        self.controller.destroy()


class inputPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Pretrained feat files are required to train the nerual network. \n"
                                    "Create feat files or load feat files to train network?",
                         font=font.Font(size=12, family='Helvetica'))
        label.pack(pady=100)

        # buttons with quit, create, and predict options
        button = ttk.Button(self, text="<<Back", command=lambda: controller.show_frame(homePage))
        button.pack(side='left')
        frame = tk.Frame(self)
        frame.pack(side='right')
        button = ttk.Button(frame, text="Create", command=lambda: controller.show_frame(featurePage))
        button.grid(row=0, column=0)
        button1 = ttk.Button(frame, text="Load", command=lambda: controller.show_frame(trainPage))
        button1.grid(row=0, column=1)


class featurePage(tk.Frame):
    def __init__(self, parent, controller):
        # need to reference controller in function
        self.controller = controller
        tk.Frame.__init__(self, parent)
        self.label = ttk.Label(self, text="Enter training .wav files")
        self.label.pack()

        self.files = []
        self.text = tk.scrolledtext.ScrolledText(self, state='disabled', width=60, height=10)
        self.text.see(tk.END)
        self.text.pack()

        # create frame holding add and clear buttons
        frame = tk.Frame(self)
        frame.pack()
        button = ttk.Button(frame, text="Add Files", command=self.openDialogbox)
        button.grid(row=0, column=0)
        button1 = ttk.Button(frame, text="Clear Files", command=self.clearDialogbox)
        button1.grid(row=0, column=1)

        button2 = ttk.Button(self, text="<<Back", command=lambda: controller.show_frame(inputPage))
        button2.pack(side='left')
        button3 = ttk.Button(self, text="Submit", command=self.submitText)
        button3.pack(side='right')


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

        self.text = tk.scrolledtext.ScrolledText(self, width=60, height=10)
        self.text.insert(tk.END, "Creating Feat Files. . .")
        self.text.config(state='disabled', background="light grey")
        self.text.see(tk.END)
        self.text.pack()

        button = ttk.Button(self, text="<<Back", command=self.resBack)
        button.pack(side='left')

        self.button1 = ttk.Button(self, text="Next>>", command=self.resForward)
        self.button1.config(state='disabled')
        self.button1.pack(side='right')

        # when page is displayed create file
        self.bind("<<onDisplay>>", self.createFile)

    def createFile(self, event):
        self.button1.config(state='disabled')
        file = self.controller.var
        self.controller.var = None
        self.text.config(state='normal')
        pepeiaoSubprocess(self, file, "feature", None, None)
        self.text.config(state='disabled')

    def resBack(self):
        resetPage(self, "Feat", featurePage)

    def resForward(self):
        resetPage(self, "Feat", trainPage)


class trainPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)

        self.files = []
        # label and text box to enter feat files
        frame = tk.Frame(self)
        frame.pack()
        self.label = ttk.Label(frame, text="Enter .feat files")
        self.label.grid(row=0, column=0, padx=10, pady=10)
        self.text = tk.scrolledtext.ScrolledText(frame, state='disabled', width=60, height=10)
        self.text.see(tk.END)
        self.text.grid(row=0, column=1)

        # create frame holding add and clear buttons
        frame1 = tk.Frame(self)
        frame1.pack()
        button = ttk.Button(frame1, text="Add Files", command=self.openDialogbox)
        button.grid(row=0, column=0)
        button1 = ttk.Button(frame1, text="Clear Files", command=self.clearDialogbox)
        button1.grid(row=0, column=1)

        # empty space
        blank = tk.Label(self)
        blank.pack()

        # label and drop down menu holding model choices
        frame2 = tk.Frame(self)
        frame2.pack()
        self.label1 = ttk.Label(frame2, text="Select model")
        self.label1.grid(row=0, column=0, sticky='E')
        choices = {'bulbul', 'conv', 'gru', 'transfer'}
        self.option = tk.StringVar(self)
        self.option.set('bulbul')
        menu = tk.OptionMenu(frame2, self.option, *choices)
        menu.grid(row=0, column=1, sticky='W')

        # label and entry box to enter saved name
        frame3 = tk.Frame(self)
        frame3.pack()
        self.label2 = ttk.Label(frame3, text="Save as:")
        self.label2.grid(row=0, column=0)
        self.entry = ttk.Entry(frame3)
        self.entry.grid(row=0, column=1, sticky='W')

        # back and submit buttons
        button2 = ttk.Button(self, text="<<Back", command=lambda: controller.show_frame(inputPage))
        button2.pack(side='left')

        button3 = ttk.Button(self, text="Submit", command=self.submitText)
        button3.pack(side='right')

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

        self.text = tk.scrolledtext.ScrolledText(self, width=60, height=10)
        self.text.insert(tk.END, "Creating Model File. . .")
        self.text.config(state='disabled', background="light grey")
        self.text.see(tk.END)
        self.text.pack()

        button = ttk.Button(self, text="<<Back", command=self.resBack)
        button.pack(side='left')

        self.button1 = ttk.Button(self, text="Next>>", command=self.resForward)
        self.button1.config(state='disabled')
        self.button1.pack(side='right')
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
        self.text.config(state='disabled')

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
        self.text = tk.scrolledtext.ScrolledText(self, state='disabled', width=60, height=10)
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
        self.label2 = ttk.Label(self, text="Load NN:")
        self.label2.grid(row=3, column=0)

        # create frame holding add and clear buttons
        frame = tk.Frame(self)
        frame.grid(row=3, column=1, sticky='W')
        button = ttk.Button(frame, text="Select Model", command=self.addModel)
        button.grid(row=0, column=0, sticky='W')
        self.entry = ttk.Entry(frame, state='disabled', width=80)
        #self.entry = ttk.Entry(frame, width=80)
        self.entry.grid(row=0, column=1)

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

    def addModel(self):
        self.entry.config(state='normal')
        if not self.entry.get():  # if entry is empty
            self.entry.delete(0, tk.END)
        filename = tk.filedialog.askopenfilenames(initialdir=getcwd(), title="Select Model",
                                                  filetypes=[("h5 files", "*.h5")])
        self.entry.insert(tk.END, filename[0])
        self.entry.config(state='disabled')


class predictPage2(tk.Frame):
    def __init__(self, parent, controller):
        # need to reference controller in function
        self.controller = controller
        tk.Frame.__init__(self, parent)

        self.text = tk.scrolledtext.ScrolledText(self, width=95, height=10)
        self.text.insert(tk.END, "Creating Prediction Files. . .")
        self.text.config(state='disabled', background="light grey")
        self.text.see(tk.END)
        self.text.pack()

        button = ttk.Button(self, text="<<Back", command=self.resBack)
        button.pack(side='left')

        self.button1 = ttk.Button(self, text="Next>>", command=self.resForward)
        self.button1.config(state='disabled')
        self.button1.pack(side='right')

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
        self.text.config(state='disabled')

    def resBack(self):
        resetPage(self, "Prediction", predictPage)

    def resForward(self):
        resetPage(self, "Prediction", homePage)


app = GraphicalUserInterface()
app.title('Pepeiao Neural Network')
app.mainloop()
