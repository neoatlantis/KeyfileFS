#!/usr/bin/env python3

import os
import subprocess
from tkinter import *
import tkinter.filedialog as filedialog


class GUI:

    def __init__(self, mountpoint, fs):
        self.fs = fs
        self.mountpoint = mountpoint
        self.root = Tk()
        self.accessReleased = True # after initialization will be set to False

        self.keyfileVar = StringVar()
        self.directoryVar = StringVar()

        self.__initWidgets()

    def __initWidgets(self):
        self.root.title("KeyfileFS")
        self.root.resizable(False, False)

        lbl1 = Label(self.root, text="Mount path:")
        lbl1.grid(row=0, column=0, sticky=E)

        lbl2 = Label(self.root, text="Master key file:")
        lbl2.grid(row=1, column=0, sticky=E)

        lbl3 = Label(self.root, text="Directory being mapped:")
        lbl3.grid(row=2, column=0, sticky=E)

        lblPath = Label(self.root, text=self.mountpoint, anchor=W)
        lblPath.grid(row=0, column=1, columnspan=3, sticky=W)

        txtKeyfile = Entry(
            self.root,
            state="readonly",
            textvariable=self.keyfileVar,
            width=50
        )
        txtKeyfile.grid(row=1, column=1, columnspan=2)

        txtDirectory = Entry(
            self.root,
            state="readonly",
            textvariable=self.directoryVar,
            width=50
        )
        txtDirectory.grid(row=2, column=1, columnspan=2)

        btnKeyfile = Button(
            self.root,
            text="Browse...",
            command=self.onChooseKeyfile,
        )
        btnKeyfile.grid(row=1, column=3)

        btnDirectory = Button(
            self.root,
            text="Browse...",
            command=self.onChooseMapDirectory
        )
        btnDirectory.grid(row=2, column=3)

        self.accessStatusVar = StringVar()

        self.txtAccess = Entry(
            self.root,
            state="disabled",
            textvariable=self.accessStatusVar,
            justify=CENTER,
        )
        self.txtAccess.grid(row=3, column=0, columnspan=4, sticky=W+E)

        self.btnRelease = Button(
            self.root,
            text="Allow Access",
            command=self.toggleAccess
        )
        self.btnRelease.grid(row=4, column=0, columnspan=2, sticky=W+E)

        self.toggleAccess()

        btnExit = Button(self.root, text="Exit", command=self.onExit)
        btnExit.grid(row=4, column=2, columnspan=2, sticky=W+E)


    def toggleAccess(self):
        self.accessReleased = not self.accessReleased
        self.fs.setRelease(self.accessReleased)
        if self.accessReleased:
            self.btnRelease.config(text="Click to deny access")
            self.accessStatusVar.set(
                "Allowing keyfile access. Keyfiles now readable by any program."
            )
            self.txtAccess.config(
                disabledbackground="green",
                disabledforeground="white",
            )
        else:
            self.btnRelease.config(text="Click to allow access")
            self.accessStatusVar.set(
                "Denying keyfile access. " + 
                "Click button below to grant permission."
            )
            self.txtAccess.config(
                disabledbackground="red",
                disabledforeground="white",
            )


    def __enter__(self, *args, **kvargs):
        self.root.mainloop()

    def __exit__(self, *args, **kvargs):
        subprocess.run(["fusermount", "-u", self.mountpoint])

    def onChooseKeyfile(self, filename=None):
        if not filename:
            filename = filedialog.askopenfilename()
            if not filename: return
        self.keyfileVar.set(filename)
        self.fs.setKeyfile(filename)

    def onChooseMapDirectory(self, directory=None):
        if not directory:
            directory = filedialog.askdirectory(
                initialdir=os.path.expanduser("~"))
            if not directory: return
        self.directoryVar.set(directory)
        self.fs.setSaltsFromDirectory(directory)

    def onExit(self):
        self.root.destroy()
