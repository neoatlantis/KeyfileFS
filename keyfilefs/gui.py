#!/usr/bin/env python3

import subprocess
from tkinter import *

class GUI:

    def __init__(self, mountpoint, fs):
        self.fs = fs
        self.mountpoint = mountpoint
        self.root = Tk()

        self.__initWidgets()

    def __initWidgets(self):
        w = Label(self.root, text=self.mountpoint)
        w.pack()

    def __enter__(self, *args, **kvargs):
        self.root.mainloop()

    def __exit__(self, *args, **kvargs):
        subprocess.run(["fusermount", "-u", self.mountpoint])
