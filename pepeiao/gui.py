import tkinter as tk
from tkinter import ttk, filedialog
import subprocess
import shlex
import sys
from os import getcwd, path


def parse(string):
    """Given a string adds current dir to string"""
    newstring = []
    word = []
    record = False
    for i in range(0, len(string)):
        if string[i] == '{':
            record = True
        elif string[i] == '}':
            # join char array to form string
            temp = ""
            temp = temp.join(word)
            word.clear()
            # write string to newstring arr
            newstring.append(temp)
            record = False
        elif record is True:
            word.append(string[i])

    return newstring


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

        self.text = tk.Text(self)
        self.text.see(tk.END)
        # self.text.bind("<Return>", self.processText)
        self.text.grid(row=1, column=0)

        button = ttk.Button(self, text="Open Files", command=self.openDialogbox)
        button.grid(row=2, column=0)

        button1 = ttk.Button(self, text="<<Back", command=lambda: controller.show_frame(inputPage))
        button1.grid(row=3, column=0, sticky="W")

        button2 = ttk.Button(self, text="Submit", command=self.processText)
        button2.grid(row=3, column=1)


    def processText(self, *event):
        s = self.text.get("1.0", tk.END)
        # remove last char from var
        s = s[:-1]
        s = parse(s)
        self.controller.var = s
        self.controller.show_frame(featurePage2)

    def openDialogbox(self):
        filename = tk.filedialog.askopenfilenames(initialdir=getcwd(), title="Select training .wav files",
                                                  filetypes=[("wav files", "*.wav")])
        self.text.insert(tk.END, filename)


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

        button = ttk.Button(self, text="<<Back",
                            command=self.resetBack)
        button.grid(row=1, column=0)
        # when page is displayed create file
        self.bind("<<onDisplay>>", self.createFile)

    def createFile(self, event):
        file = self.controller.var
        self.controller.var = None
        self.text.config(state='normal')
        try:
            # return command output as byte string
            args = ["pepeiao", "feature"]
            for item in file:
                args.append(item)
            #temp = check_output(args)

            process = subprocess.Popen(args, stdout=subprocess.PIPE)
            while True:
                output = process.stdout.readline()
                # break out of loop if exit code is returned
                if process.poll() is not None:
                    break
                if output:
                    self.text.insert(tk.END, output.strip())
                    self.update()
            self.text.insert(tk.END, "\n\nFinished writing files")

            #self.text.insert(tk.END, temp)
        except subprocess.CalledProcessError:
            # handle non zero exit status
            self.text.delete('1.0', tk.END)
            self.text.insert(tk.END, "Invalid file name received")
        self.text.config(state='disabled')

    def resetBack(self):
        # change label to initial state and go to page
        self.text.config(state='normal')
        self.text.delete('1.0', tk.END)
        self.text.insert(tk.END, "Creating Feat Files. . .")
        self.text.config(state='disabled')
        self.controller.show_frame(featurePage)

    #TODO make window output scrollable, write to output as created, update message when finished
    #TODO write predictions to csv file
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
        self.text = tk.Text(self)
        self.text.grid(row=0, column=1)
        button = ttk.Button(self, text="Open Files", command=self.openDialogbox)
        button.grid(row=1, column=1)

        # label and drop down menu holding model choices
        self.label1 = ttk.Label(self, text="Select model")
        self.label1.grid(row=2, column=0, sticky='E')

        choices = {'bulbul', 'conv', 'gru', 'transfer'}
        self.option = tk.StringVar(self)
        self.option.set('bulbul')
        menu = tk.OptionMenu(self, self.option, *choices)
        menu.grid(row=2, column=1, sticky='W')

        # label and entry box to enter saved name
        self.label2 = ttk.Label(self, text="Save as:")
        self.label2.grid(row=3, column=0)
        self.entry = ttk.Entry(self)
        self.entry.grid(row=3, column=1, sticky='W')


        # back and submit buttons
        button1 = ttk.Button(self, text="<<Back", command=lambda: controller.show_frame(inputPage))
        button1.grid(row=4, column=0)

        button2 = ttk.Button(self, text="Submit", command=self.processText)
        button2.grid(row=4, column=2)

    def processText(self, *event):
        s = self.text.get("1.0", tk.END)
        # remove last char from var
        s = s[:-1]
        s = parse(s)
        self.controller.var = s
        self.controller.model = self.option.get()
        self.controller.saveName = self.entry.get()
        self.controller.show_frame(trainPage2)

    def openDialogbox(self):
        filename = tk.filedialog.askopenfilenames(initialdir=getcwd(), title="Select feat files",
                                                  filetypes=[("feat files", "*.feat")])
        self.text.insert(tk.END, filename)


class trainPage2(tk.Frame):
    def __init__(self, parent, controller):
        # need to reference controller in function
        self.controller = controller
        tk.Frame.__init__(self, parent)
        self.label = ttk.Label(self, text="Creating Model File. . .")
        self.label.grid(row=0, column=0, padx=100, pady=20)

        button = ttk.Button(self, text="<<Back", command=self.resetBack)
        button.grid(row=1, column=0)
        # when page is displayed create file
        self.bind("<<onDisplay>>", self.createFile)

    def createFile(self, event):
        file = self.controller.var
        model = self.controller.model
        saveName = self.controller.saveName
        self.controller.var = None
        self.controller.model = None
        self.controller.saveName = None
        # check for correct extension
        if saveName[-3:] != '.h5':
            self.label.configure(text='saved name must end with .h5')
        else:
            try:
                # return command output as byte string
                args = ["pepeiao", "train", model]
                for item in file:
                    args.append(item)
                args.append(saveName)
                temp = check_output(args)
                self.label.configure(text=temp)
            except CalledProcessError:
                # handle non zero exit status
                self.label.configure(text="Invalid argument received")

    def resetBack(self):
        # change label to initial state and go to page
        self.label.configure(text="Creating Model File. . .")
        self.controller.show_frame(trainPage)


class predictPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)

        # label and text box to enter feat files
        self.label = ttk.Label(self, text="Enter testing .wav files")
        self.label.grid(row=0, column=0, padx=10, pady=10)
        self.text = tk.Text(self)
        self.text.grid(row=0, column=1)
        button = ttk.Button(self, text="Open Files", command=self.openDialogbox)
        button.grid(row=1, column=1)

        # label and entry box to enter saved name
        self.label2 = ttk.Label(self, text="Load model:")
        self.label2.grid(row=2, column=0)
        self.entry = ttk.Entry(self)
        self.entry.grid(row=2, column=1, sticky='W')

        # back and submit buttons
        button = ttk.Button(self, text="<<Back", command=lambda: controller.show_frame(homePage))
        button.grid(row=3, column=0)

        button1 = ttk.Button(self, text="Submit", command=self.processText)
        button1.grid(row=3, column=2)

    def processText(self, *event):
        s = self.text.get("1.0", tk.END)
        # remove last char from var
        s = s[:-1]
        s = parse(s)
        self.controller.var = s
        self.controller.saveName = self.entry.get()
        self.controller.show_frame(predictPage2)

    def openDialogbox(self):
        filename = tk.filedialog.askopenfilenames(initialdir=getcwd(), title="Select testing .wav files",
                                                  filetypes=[("wav files", "*.wav")])
        self.text.insert(tk.END, filename)


class predictPage2(tk.Frame):
    def __init__(self, parent, controller):
        # need to reference controller in function
        self.controller = controller
        tk.Frame.__init__(self, parent)
        self.label = ttk.Label(self, text="Creating Prediction File. . .")
        self.label.grid(row=0, column=0, padx=100, pady=20)

        button = ttk.Button(self, text="<<Back", command=self.resetBack)
        button.grid(row=1, column=0)
        # when page is displayed create file
        self.bind("<<onDisplay>>", self.createFile)

    def createFile(self, event):
        file = self.controller.var
        saveName = self.controller.saveName
        self.controller.var = None
        self.controller.saveName = None
        # check for correct extension
        if saveName[-3:] != '.h5':
            self.label.configure(text='Model name must end with .h5')
        else:
            try:
                # return command output as byte string
                args = ["pepeiao", "predict", saveName]
                for item in file:
                    args.append(item)
                temp = check_output(args)
                self.label.configure(text=temp)
            except CalledProcessError:
                # handle non zero exit status
                self.label.configure(text="Invalid argument received")

    def resetBack(self):
        # change label to initial state and go to page
        self.label.configure(text="Creating Prediction File. . .")
        self.controller.show_frame(predictPage)


app = GraphicalUserInterface()
app.title('Pepeiao Neural Network')
app.mainloop()
# data\S4A01450_20170507_180200.wav data\S4A01450_20170507_190200.wav
