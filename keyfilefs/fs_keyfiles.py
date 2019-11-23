#!/usr/bin/env python3

import re
import hashlib
import errno

from fuse import FuseOSError

from .constants import *



class KeyfileFSKeyfiles:

    def __init__(self, parent):
        self.parent = parent
        def pbkdfGen(salt, length=512):
            return hashlib.pbkdf2_hmac(
                "sha512", parent.secret, salt, 100, length)
        self.PBKDF = pbkdfGen
        self.updateSalts()
        
    def updateSalts(self):
        self.salts = self.parent.saltsFromDirectory

    def readdir(self):
        for each in self.salts:
            if re.match(REGEX_FILENAME_RULE, each): yield each + ".keyfile"

    def getattr(self, basename):
        return {
            "st_size": KEYFILE_LENGTH,
        }

    def read(self, basename, length, offset):
        if basename[:-8] not in self.salts:
            raise FuseOSError(errno.ENOENT)
        fulldata = self.PBKDF(basename.encode("ascii"))
        return fulldata[offset:offset+length]
