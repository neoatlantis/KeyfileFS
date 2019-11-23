#!/usr/bin/env python3

DESCRIPTION = """
CLI for starting a KeyfileFS
============================

Usage:
    python3 -m keyfilefs                    \\
        <mount point>                       \\
        --map/-m <instructions directory>   \\
        --keyfile/-k <main key file>

This command mounts a KeyfileFS at given <mount point>.

Sub-keyfiles are derived based on files contained in <instructions directory>.
Any filename in this directory is treated as a "salt", and will be mapped onto
<mount point>/keyfiles/ under the same name.

For example, if we have a file at location `/home/user/passwords.kdbx`, then
using `--map /home/user` we will have

    /...(path to mount point).../keyfiles/passwords.kdbx

as the corresponding keyfile. The users may use KeepassX and choose above file
to enhance their security. Content of this keyfile is derived using one-way
cryptography from

    1. content of the main keyfile given by `--keyfile/-k`, and
    2. its corresponding filename "passwords.kdbx";

So long as these 2 factors stay unchanged, the 1024-bytes content within
keyfile `<mount point>/keyfiles/passwords.kdbx` remains the same.



...
"""


import os
import re
import threading
import argparse
import subprocess

from .fs import KeyfileFSOperations, mountKeyfileFS
from .constants import *
from .gui import GUI
from .sectools import *


parser = argparse.ArgumentParser(
    description=DESCRIPTION,
    formatter_class=argparse.RawDescriptionHelpFormatter
)

parser.add_argument("mountpoint", help="""
The (empty) directory for mounting this filesystem.
""")

parser.add_argument("--map", "-m", help="""
The directory being mapped to keyfiles.
""")

parser.add_argument("--keyfile", "-k", help="""
The master keyfile. All keyfiles will be derived from this.
""")


args = parser.parse_args()

if args.keyfile:
    args.keyfile = os.path.realpath(args.keyfile)

##############################################################################




keyfileFS = KeyfileFSOperations()

fst = threading.Thread(
    target=mountKeyfileFS,
    args=(keyfileFS, args.mountpoint)
)
fst.start()



gui = GUI(mountpoint=args.mountpoint, fs=keyfileFS)

if not disallow_swap():
    print("Failed securing memory. Exit.")
    exit(1)

if args.keyfile:
    gui.onChooseKeyfile(args.keyfile)
if args.map:
    gui.onChooseMapDirectory(args.map)

with gui:
    pass

print("Bye.")
